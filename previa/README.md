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
