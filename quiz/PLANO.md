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

## Fluxo padrão (decidido em 24/11)
O usuário manda o roteiro → eu entrego **1 vídeo longo 16:9 no template + 3 cortes verticais** (TikTok/Shorts, 3 perguntas cada, +1 min) + thumb + .srt + título/descrição/capítulos + legendas dos posts.
Como fazer um vídeo novo NN:
1. `tools/brainrushNN_data.py` (copiar o 02: INTRO, perguntas, PRE "Question number X!" separado, SCORE/SCORE_KEYS, OUTRO, SHORTS).
2. `tools/brainrushNN_scenes.py` (stage_ask/stage_exp/MONT de cada pergunta; o palco não pode entregar a resposta na pergunta).
3. `BR_VID=NN python3 tools/brainrush01_tts.py` → conferir transcrições ruins (Whisper às vezes alucina; refazer sem initial_prompt).
4. `BR_VID=NN python3 tools/build_brainrush01.py --qframes` (conferir) → render completo → `build_brainrush01_shorts.py`.
5. `tools/thumb_brainrushNN.py`.

## O que já foi feito
- 24/11: estrutura criada, ambiente preparado.
- 24/11: **Vídeo 01 – "15 General Knowledge Questions — Can You Score 15/15?"** montado (8:31). Arquivos: `quiz/videos/brainrush01.mp4`, `brainrush01_thumb.jpg`, `brainrush01.srt`; publicação em `quiz/roteiros/brainrush01_publicacao.md`.
  - **5 shorts verticais** (1080×1920, 93–106s, 3 perguntas cada, gancho + CTA "follow"): `quiz/videos/shorts/brainrush01_short1..5.mp4`, legendas dos posts em `quiz/roteiros/brainrush01_shorts_legendas.md`. Script: `tools/build_brainrush01_shorts.py`.
  - Mudança vs roteiro: na Q15 o palco mostra "x²" em vez de "144" (mostrar 144 entregaria a resposta).

- 24/11: **Vídeo 02 – "15 Science & Nature Questions — Can You Beat This Quiz?"** (8:15) + 3 shorts, pra postar em 25/11. Arquivos `quiz/videos/brainrush02*`, `quiz/videos/shorts/brainrush02_short1..3.mp4`, textos em `quiz/roteiros/brainrush02_*`.
  - Padronizei "Question number X!" + leitura das alternativas em todas as perguntas (o roteiro só tinha na 1ª).

- 25/11: **Resultado do 1º dia:** vídeo longo 01 ~0 views; shorts ~800 views, 7 comentários, 7 inscritos (tudo veio dos shorts). → canal vira **shorts-first**.

- 25/11 (detalhe): só 2 shorts postados no **YouTube**: um ~800 views (7 coment.), outro ~350 views / 7 curtidas / 0 coment. **TikTok flopou:** 3 shorts, ~200 views no total, 1 seguidor.
  - Hipótese principal do TikTok: conta brasileira → TikTok mostra pra público do Brasil, que não entende o quiz em inglês. Outras: conta nova em "aquecimento", vídeo de 90s longo demais pra conta nova no TikTok.

- 25/11: **Vídeo 03 – "30 General Knowledge Questions — Can You Score 30/30?"** (roteiro de 30 perguntas em 5 rounds, ~14 min) + **10 shorts** (5 dias de conteúdo a 2/dia). Arquivos `quiz/videos/brainrush03*`, `quiz/videos/shorts/brainrush03_short1..10.mp4`, textos em `quiz/roteiros/brainrush03_*`.
  - Motor agora aceita qualquer nº de perguntas, rounds no chip e roteiro sem tela de pontuação. Perguntas repetidas reaproveitam cenas dos vídeos 01/02.
  - Ferramenta `tools/fix_transcripts.py` (BR_VID=NN) refaz transcrições ruins do Whisper.

## Estratégia de postagem (decidida em 25/11)
- **Shorts são o motor.** Vídeo longo em canal sem inscritos não recebe tráfego; ele só começa a render quando os shorts trazem base (~500–1.000 inscritos).
- **Ritmo:** **2 shorts por dia** (manhã ~11h e noite ~19h, horário de Brasília — público EUA acorda/almoça), mesmo arquivo no TikTok + YouTube Shorts (+ Reels se der).
- **1 vídeo longo por semana** (sábado ou domingo), feito das mesmas 15 perguntas — vira a "playlist" pra quem chega pelos shorts. Quando passar de ~1k inscritos, testar 2 longos/semana.
- **Produção:** cada roteiro de 15 perguntas → **5 shorts** (não 3) + 1 longo. 2 shorts/dia = **~3 roteiros por semana** (1 vira longo; os outros podem ser só shorts).
- **Testes contínuos:** variar o gancho (%, "geniuses", "90% fail") e o tema; anotar views/retenção por short e repetir o que ganhar. Fixar comentário "Comment your score 👇".
- **Métricas que importam:** YouTube Shorts → "% que assistiu vs. deslizou" (meta >70%) e retenção média; TikTok → tempo médio e % que assistiu inteiro; comentários; inscritos por short.

## Próximos passos
0. **FOCO ÚNICO: YouTube em inglês até monetizar.** Nada em português (decisão do usuário, 25/11 — evitar acúmulo). TikTok = só repost do mesmo arquivo, sem esforço extra.
   - Meta: entrar no Programa de Parcerias do YouTube (regra geral: 1.000 inscritos + 10 mi de views em Shorts em 90 dias, ou 4.000 h de exibição em vídeos longos; conferir no YouTube Studio › Ganhar dinheiro).
   - Rotina simples: usuário manda roteiro → eu entrego 5 shorts + 1 longo → usuário posta 2 shorts/dia + 1 longo/semana. Só isso.
1. Saber qual short teve as 800 views (qual tema/gancho) e dobrar a aposta no que ganhou.
2. Postar os shorts do vídeo 02 (2/dia). Vídeo 02 longo: segurar pro fim de semana.
3. Usuário manda ~3 roteiros/semana; eu entrego 5 shorts por roteiro + longo semanal.
4. Ideias de séries curtas: "Guess the Country by Its Shape", "Only Geniuses (Hard Mode)", "Human Body", "Space", "Guess the Flag/Logo", "Kids vs Adults questions".
5. Pendentes técnicos: voz (Kokoro vs ElevenLabs), chave do Pexels pra fotos reais.
