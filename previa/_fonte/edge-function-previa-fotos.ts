// Edge Function: fotos da prévia do feed da Dra. Jennifer.
// Ações: enviar (multipart), listar e remover (JSON). Toda chamada confere a senha.
// Cada foto fica no Storage privado (miniatura para a página) e é copiada para o
// repositório privado melatop/dra-jennifer-fotos, de onde o Claude puxa para montar o post.
import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
import { encodeBase64 } from "jsr:@std/encoding@1/base64";

const BUCKET = "previa-fotos";
const REPO = "melatop/dra-jennifer-fotos";
const MAX_BYTES = 20 * 1024 * 1024;
const TIPOS: Record<string, string> = {
  "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "image/heic": "heic", "image/heif": "heif",
};
const RE_MES = /^\d{4}-\d{2}$/;
const RE_POST = /^[a-z0-9-]{3,80}$/;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, apikey, content-type, x-client-info",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
};
const json = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { ...CORS, "Content-Type": "application/json" } });

const sb = createClient(Deno.env.get("SUPABASE_URL")!, Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!, {
  auth: { persistSession: false },
});
const GH = Deno.env.get("GITHUB_TOKEN") ?? "";

async function senhaOk(senha: unknown): Promise<boolean> {
  if (typeof senha !== "string" || !senha) return false;
  const { data, error } = await sb.rpc("previa_senha_ok", { p_senha: senha });
  return !error && data === true;
}

async function github(method: string, path: string, body: unknown) {
  for (let tentativa = 0; tentativa < 3; tentativa++) {
    const r = await fetch(`https://api.github.com/repos/${REPO}/contents/${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${GH}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "previa-feed-dra-jennifer",
      },
      body: JSON.stringify(body),
    });
    if (r.status === 409 && tentativa < 2) {
      await new Promise((res) => setTimeout(res, 600 * (tentativa + 1)));
      continue;
    }
    return r;
  }
  throw new Error("conflito no GitHub");
}

async function assinar(paths: string[]) {
  if (!paths.length) return {};
  const { data } = await sb.storage.from(BUCKET).createSignedUrls(paths, 60 * 60 * 6);
  const m: Record<string, string> = {};
  (data ?? []).forEach((d) => { if (d.path && d.signedUrl) m[d.path] = d.signedUrl; });
  return m;
}

async function enviar(req: Request) {
  const form = await req.formData();
  const senha = form.get("senha"), mes = String(form.get("mes") ?? ""), post = String(form.get("post_id") ?? "");
  const arq = form.get("arquivo");
  if (!(await senhaOk(senha))) return json({ erro: "senha" }, 401);
  if (!RE_MES.test(mes) || !RE_POST.test(post)) return json({ erro: "post inválido" }, 400);
  if (!(arq instanceof File)) return json({ erro: "arquivo ausente" }, 400);
  const ext = TIPOS[arq.type];
  if (!ext) return json({ erro: "tipo de arquivo não aceito" }, 415);
  if (arq.size > MAX_BYTES) return json({ erro: "arquivo grande demais" }, 413);

  const bytes = new Uint8Array(await arq.arrayBuffer());
  const nome = `${new Date().toISOString().replace(/[-:]/g, "").replace(/\..+/, "")}-${crypto.randomUUID().slice(0, 6)}.${ext}`;
  const caminho = `${mes}/${post}/${nome}`;

  const up = await sb.storage.from(BUCKET).upload(caminho, bytes, { contentType: arq.type, upsert: false });
  if (up.error) return json({ erro: "falha ao salvar a foto" }, 500);

  const gh = await github("PUT", caminho, {
    message: `Foto para ${post} (${mes})`,
    content: encodeBase64(bytes),
    branch: "main",
  });
  if (!gh.ok) {
    await sb.storage.from(BUCKET).remove([caminho]);
    console.error("github", gh.status, await gh.text());
    return json({ erro: "falha ao guardar a cópia da foto" }, 502);
  }
  const sha = (await gh.json())?.content?.sha ?? null;

  const ins = await sb.from("previa_fotos").insert({
    mes, post_id: post, storage_path: caminho, github_path: caminho, github_sha: sha, tipo: arq.type, bytes: arq.size,
  }).select("id, created_at, post_id, storage_path").single();
  if (ins.error) return json({ erro: "falha ao registrar a foto" }, 500);
  const urls = await assinar([caminho]);
  return json({ id: ins.data.id, post_id: post, created_at: ins.data.created_at, url: urls[caminho] ?? null });
}

async function listar(b: Record<string, unknown>) {
  if (!(await senhaOk(b.senha))) return json({ erro: "senha" }, 401);
  const mes = String(b.mes ?? "");
  if (!RE_MES.test(mes)) return json({ erro: "mês inválido" }, 400);
  const { data, error } = await sb.from("previa_fotos")
    .select("id, created_at, post_id, storage_path").eq("mes", mes).eq("removida", false).order("created_at");
  if (error) return json({ erro: "falha ao listar" }, 500);
  const urls = await assinar((data ?? []).map((d) => d.storage_path));
  return json((data ?? []).map((d) => ({ id: d.id, post_id: d.post_id, created_at: d.created_at, url: urls[d.storage_path] ?? null })));
}

async function remover(b: Record<string, unknown>) {
  if (!(await senhaOk(b.senha))) return json({ erro: "senha" }, 401);
  const id = Number(b.id);
  if (!Number.isInteger(id)) return json({ erro: "id inválido" }, 400);
  const { data: f } = await sb.from("previa_fotos").select("*").eq("id", id).eq("removida", false).maybeSingle();
  if (!f) return json({ ok: true });
  await sb.from("previa_fotos").update({ removida: true }).eq("id", id);
  await sb.storage.from(BUCKET).remove([f.storage_path]);
  if (f.github_sha) {
    const r = await github("DELETE", f.github_path, { message: `Remove foto de ${f.post_id}`, sha: f.github_sha, branch: "main" });
    if (!r.ok) console.error("github delete", r.status, await r.text());
  }
  return json({ ok: true });
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: CORS });
  if (req.method !== "POST") return json({ erro: "método" }, 405);
  try {
    const ct = req.headers.get("content-type") ?? "";
    if (ct.startsWith("multipart/form-data")) return await enviar(req);
    const b = await req.json().catch(() => ({}));
    if (b.acao === "listar") return await listar(b);
    if (b.acao === "remover") return await remover(b);
    return json({ erro: "ação desconhecida" }, 400);
  } catch (e) {
    console.error(e);
    return json({ erro: "erro interno" }, 500);
  }
});
