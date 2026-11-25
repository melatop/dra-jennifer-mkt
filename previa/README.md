# Prévia do feed (branch `previa`)

Página de aprovação dos posts do Instagram da Dra. Jennifer Aragão.
Publicada só neste branch: https://previa--jenniferaragao-vet.netlify.app/previa/

- `posts.json`: posts do mês (id, versão, data, tipo, legenda, imagens, briefing, roteiro).
- `img/<post-id>/`: artes prontas (JPG 1080×1350).
- `config.js`: URL e chave publicável do Supabase.
- Respostas (aprovar/reprovar + comentário): tabela `previa_respostas`, via RPC `previa_listar` / `previa_registrar`, com senha.
- Fotos enviadas pela Dra.: Edge Function `previa-fotos` → Storage privado `previa-fotos` + cópia no repo privado `melatop/dra-jennifer-fotos`.

Este branch não deve ser mesclado no `main`.
