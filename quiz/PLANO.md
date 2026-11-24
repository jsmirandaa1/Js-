# Canal Dark de Quiz – Plano

Projeto separado do canal de GTA 6. Canal "dark" (sem rosto): narração + visual gerado + timer + revelação da resposta.

## Estrutura
- `quiz/roteiros/` – roteiros e legendas dos posts
- `quiz/videos/` – vídeos prontos
- `quiz/tools/` – scripts de montagem

## Identidade
- Nome: **BrainRush Quiz** · slogan "Think fast, know more!"
- Formato principal: **YouTube 16:9 (1920×1080), ~8–10 min**, narração em **inglês americano**.
- Visual: fundo preto, detalhes dourados, textos brancos. Fontes Anton / Montserrat ExtraBold / Bebas Neue.
- Template fixo de pergunta: topo (logo + categoria + 15 bolinhas de progresso), número da questão à esquerda, palco com imagem animada no centro, timer circular dourado de 7s à direita, pergunta + 4 alternativas (2×2), legenda queimada embaixo. Na revelação: flash, alternativa certa em dourado com ✓, erradas apagadas, palco troca pra cena de explicação com destaque dourado.

## Pipeline (`quiz/tools/`)
1. `brainrush01_data.py` – perguntas, alternativas, narração (copiar/adaptar por vídeo).
2. `brainrush01_tts.py` – voz **Kokoro ONNX `am_michael`** (speed 1.08) + Whisper pros tempos de cada palavra. Letras soletradas ("A G") passam por fonemas (senão o "A" vira "uh").
3. `build_brainrush01.py` – linha do tempo automática (opções aparecem quando a voz fala a letra; 7s de contagem; resposta), cenas, legenda, trilha de suspense + SFX gerados no script (sem direitos autorais), ducking, loudnorm −14 LUFS. Render em 4 processos. `--frames t1,t2` e `--qframes` pra conferir quadros.
4. `thumb_brainrush01.py` – thumbnail 1280×720.
- Assets (não versionados, baixar de novo em `/tmp/claude-0/quiz_assets`): texturas de planetas (raw.githubusercontent: `jeromeetienne/threex.planets`, `mrdoob/three.js` textures/planets), emojis 3D **Microsoft Fluent Emoji** (MIT, `microsoft/fluentui-emoji/main/assets/<Nome>/3D/<nome>_3d.png`), mapas `world-atlas@2` (npm). Modelo Kokoro: HF `onnx-community/Kokoro-82M-v1.0-ONNX`.
- Rede: Pexels (fotos reais) está com chave inválida; Wikimedia/NASA/Unsplash bloqueados. Visual hoje = planetas 3D reais + cenas desenhadas + emojis 3D.

## O que já foi feito
- 24/11: estrutura criada, ambiente preparado.
- 24/11: **Vídeo 01 – "15 General Knowledge Questions — Can You Score 15/15?"** montado (8:31). Arquivos: `quiz/videos/brainrush01.mp4`, `brainrush01_thumb.jpg`, `brainrush01.srt`; publicação em `quiz/roteiros/brainrush01_publicacao.md`.
  - **5 shorts verticais** (1080×1920, 93–106s, 3 perguntas cada, gancho + CTA "follow"): `quiz/videos/shorts/brainrush01_short1..5.mp4`, legendas dos posts em `quiz/roteiros/brainrush01_shorts_legendas.md`. Script: `tools/build_brainrush01_shorts.py`.
  - Mudança vs roteiro: na Q15 o palco mostra "x²" em vez de "144" (mostrar 144 entregaria a resposta).

## Próximos passos
1. Postar o vídeo 01 no YouTube (subir o .srt) e os shorts no TikTok/Shorts (2–3 hoje, resto amanhã). Trazer números: CTR da thumb, retenção, views e comentários dos shorts.
2. Decidir se mantém a voz Kokoro ou troca pra ElevenLabs (é só substituir os wav em `voz/` e rodar de novo).
3. Arrumar a chave do Pexels pra ter fotos reais nas perguntas de animais/lugares.
4. Próximos vídeos: reaproveitar o template; ideias – "Only Geniuses Get 15/15 (Hard Mode)", "Guess the Country by Its Shape", "Science Quiz", Shorts verticais com 3 perguntas cortadas do vídeo longo.
