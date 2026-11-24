# Canal Dark de Quiz – Plano

Projeto separado do canal de GTA 6. Canal "dark" (sem rosto): narração + visual gerado + timer + revelação da resposta.

## Estrutura
- `quiz/roteiros/` – roteiros e legendas dos posts
- `quiz/videos/` – vídeos prontos
- `quiz/tools/` – scripts de montagem

## Pipeline (reaproveita o do canal de GTA)
narração mp3 (ElevenLabs) → Whisper (`tools/asr.py`) → legenda palavra por palavra → telas de pergunta/opções/timer/resposta geradas em PIL → trilha + SFX (tic-tac, acerto) gerados no script → ffmpeg 9:16.

## O que já foi feito
- 24/11: estrutura criada, ambiente preparado (Whisper, fontes Anton/Bebas Neue/Montserrat). Aguardando roteiro do 1º vídeo (postar hoje).

## Próximos passos
1. Receber roteiro do 1º vídeo e montar.
