create extension if not exists pgcrypto with schema extensions;

-- Prévia do feed: configuração (senha), respostas de aprovação e fotos enviadas.
-- Nada aqui é acessível diretamente pela chave pública: tudo passa por funções que conferem a senha.

create table if not exists public.previa_config (
  id int primary key default 1 check (id = 1),
  senha_hash text not null,
  updated_at timestamptz not null default now()
);
alter table public.previa_config enable row level security;

create table if not exists public.previa_respostas (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  mes text not null check (mes ~ '^\d{4}-\d{2}$'),
  post_id text not null check (post_id ~ '^[a-z0-9-]{3,80}$'),
  versao int not null check (versao between 1 and 50),
  status text not null check (status in ('aprovado', 'reprovado')),
  comentario text check (char_length(comentario) <= 4000)
);
create index if not exists previa_respostas_busca on public.previa_respostas (mes, post_id, versao, created_at desc);
alter table public.previa_respostas enable row level security;

create table if not exists public.previa_fotos (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  mes text not null check (mes ~ '^\d{4}-\d{2}$'),
  post_id text not null check (post_id ~ '^[a-z0-9-]{3,80}$'),
  storage_path text not null,
  github_path text not null,
  github_sha text,
  tipo text,
  bytes int,
  removida boolean not null default false
);
create index if not exists previa_fotos_busca on public.previa_fotos (mes, post_id) where not removida;
alter table public.previa_fotos enable row level security;

-- confere a senha (uso interno e pela Edge Function com service_role)
create or replace function public.previa_senha_ok(p_senha text)
returns boolean
language sql stable security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.previa_config c
    where c.id = 1 and c.senha_hash = extensions.crypt(coalesce(p_senha, ''), c.senha_hash)
  );
$$;

create or replace function public.previa_listar(p_senha text, p_mes text)
returns table (post_id text, versao int, status text, comentario text, created_at timestamptz)
language plpgsql stable security definer
set search_path = ''
as $$
begin
  if not public.previa_senha_ok(p_senha) then
    perform pg_sleep(1);
    raise exception 'senha incorreta' using errcode = '28P01';
  end if;
  return query
    select distinct on (r.post_id, r.versao) r.post_id, r.versao, r.status, r.comentario, r.created_at
    from public.previa_respostas r
    where r.mes = p_mes
    order by r.post_id, r.versao desc, r.created_at desc;
end;
$$;

create or replace function public.previa_registrar(
  p_senha text, p_mes text, p_post_id text, p_versao int, p_status text, p_comentario text
)
returns table (created_at timestamptz)
language plpgsql volatile security definer
set search_path = ''
as $$
begin
  if not public.previa_senha_ok(p_senha) then
    perform pg_sleep(1);
    raise exception 'senha incorreta' using errcode = '28P01';
  end if;
  return query
    insert into public.previa_respostas (mes, post_id, versao, status, comentario)
    values (p_mes, p_post_id, p_versao, p_status, nullif(btrim(p_comentario), ''))
    returning previa_respostas.created_at;
end;
$$;

revoke all on function public.previa_senha_ok(text) from public, anon, authenticated;
revoke all on function public.previa_listar(text, text) from public;
revoke all on function public.previa_registrar(text, text, text, int, text, text) from public;
grant execute on function public.previa_senha_ok(text) to service_role;
grant execute on function public.previa_listar(text, text) to anon, authenticated, service_role;
grant execute on function public.previa_registrar(text, text, text, int, text, text) to anon, authenticated, service_role;

-- bucket privado para as miniaturas das fotos enviadas (só a Edge Function acessa)
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('previa-fotos', 'previa-fotos', false, 20971520,
        array['image/jpeg', 'image/png', 'image/webp', 'image/heic', 'image/heif'])
on conflict (id) do nothing;
