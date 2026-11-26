# Prévia do feed (branch `previa`)

Página de aprovação dos posts do Instagram da Dra. Jennifer Aragão.
Publicada só neste branch: https://previa--jenniferaragao-vet.netlify.app/previa/

- `posts.json`: posts do mês (id, versão, data, tipo, legenda, imagens, briefing, roteiro).
- `img/<post-id>/`: artes prontas (JPG 1080×1350).
- `config.js`: URL e chave publicável do Supabase.
- Respostas (aprovar/reprovar + comentário): tabela `previa_respostas`, via RPC `previa_listar` / `previa_registrar`, com senha.
- Fotos enviadas pela Dra.: Edge Function `previa-fotos` → Storage privado `previa-fotos` + cópia no repo privado `melatop/dra-jennifer-fotos`.

Este branch não deve ser mesclado no `main`.

## Postar (copiar legenda e baixar)
- Cada post tem "Copiar legenda" e, quando aprovado, "Baixar para postar" (também copia a legenda).
- Arquivos baixados: `postar` (lista explícita, se existir) → senão `video` nos Reels → senão `imagens`. Se `capa_a_tirar` for true, o download fica bloqueado até a capa real entrar.
- Celular: menu de compartilhar do sistema (iPhone: "Salvar imagens"). Computador: baixa os arquivos em ordem.
- Reels: colocar o MP4 final em `img/<post-id>/reels.mp4` e preencher `"video"` no `posts.json`.

## Vídeos dos Reels (Google Drive do Pedro)
- `Dra. Jennifer – Marketing/Vídeos dos Reels (envio)/AAAA-MM/AAAA-MM-DD · Tema/`: brutos que ela envia. A pasta "envio" está aberta para qualquer pessoa com o link enviar arquivos.
- `Dra. Jennifer – Marketing/Reels editados (final)/`: MP4 final após a edição (privada).
- No `posts.json`, `pasta_videos` = link da pasta do post; a página mostra o botão "Enviar vídeos" no bloco "O que gravar".
- Para um mês novo: criar a pasta `AAAA-MM` e uma subpasta por Reels dentro de "envio" e preencher `pasta_videos`.

## Foto provisória
- `foto_provisoria: true` + `briefing`: o post mostra a foto atual (ex.: ensaio profissional 2025, pasta "Fotos profissionais" do Drive FitzLab) e a "Sugestão de foto nova". Quando ela enviar a foto, trocar `imagens`, remover `foto_provisoria` e subir `versao`.
- O gato cinza do ensaio de 2025 é o Zack (gato da casa; não precisa de termo de imagem).
