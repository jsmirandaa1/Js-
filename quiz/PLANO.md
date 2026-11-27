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

## Regras de texto (25/11)
- **Nada de hashtags.** Títulos, legendas e descrições com **SEO**:
  1. Palavra-chave principal logo no início (ex.: "General Knowledge Quiz", "Science Trivia Quiz", "Hard Trivia Questions").
  2. Termos que as pessoas pesquisam, tirados das perguntas do vídeo ("capital of Australia", "fastest land animal", "chemical symbol for gold").
  3. Frase natural em inglês (sem lista de palavras soltas), 1–3 linhas, + CTA ("Comment your score!").
  4. YouTube Shorts: título ≤ ~70 caracteres com a keyword na frente; descrição repete a keyword + temas.
  5. TikTok: a legenda funciona como busca — escrever como alguém procuraria ("easy general knowledge quiz with answers").

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

## TikTok — formato SPEED QUIZ (decidido em 25/11)
- YouTube Shorts segue no formato atual (está funcionando: 9 inscritos, short com 200 views em 10 min). **Só o TikTok muda.**
- TikTok não entregava (3 shorts ~200 views). Causas prováveis: vídeo lento (7s + leitura das opções), conta nova, (hipótese de região descartada: usuário mora nos EUA).
- **Formato novo (Speed Quiz):** 8 perguntas em ~65s; voz lê só a pergunta; timer 3s (HARD 4s, FINAL BOSS 5s); resposta seca ("Mars!"); flash a cada troca; **5ª = HARD QUESTION** e **8ª = FINAL BOSS** (tag vermelha + impacto); gancho fixo no topo o vídeo todo ("ONLY 2% GET 8/8"); fim "How many did you get? Comment your score /8".
- Script: `tools/build_speed.py <lote>` + `tools/<lote>_data.py` (escolhe perguntas do banco dos vídeos 01–03). Saída `quiz/videos/tiktok/`.
- Se o speed for bem no TikTok, testar também no YouTube Shorts.
- **Para os próximos roteiros:** marcar dificuldade de cada pergunta (fácil/médio/difícil) e escrever a resposta curta falada. Mais perguntas por roteiro (30+), poucas "pegadinhas" difíceis no meio.

## TikTok — diagnóstico e formatos MICRO (26/11)
- Promoção do short "90% fail question 3" (formato antigo, 90s, abre com tela de título): **só 27% passaram de 2s**, **0% assistiram completo**; 10,9% passaram de 6s (acima da média) → o problema é a abertura e a duração.
- Referências que lideram a busca "quiz" no TikTok: pergunta gigante no 1º frame, 1 pergunta por vídeo (10–20s), charadas/pegadinhas, "find the odd one out" (independe de idioma), ícone por opção, barra de tempo, 3 opções.
- **Formatos novos (lote micro01):** `tools/build_micro.py` + `tools/micro01_data.py`
  - **Riddle Micro** (~11s): charada no 1º frame, 3 opções com emoji 3D, barra 6s, resposta + "Did you get it? Comment your answer!".
  - **Odd One Out** (~11–13s): grade de letras/números com 1 diferente, relógio 8–10s, círculo dourado no diferente.
- Speed Quiz agora **sem intro** (pergunta 1 no 1º frame).
- Teste: 3 posts/dia no TikTok (1 de cada formato) por 3 dias → comparar % "assistiu completo" e % "2 segundos" → escalar o vencedor.

## Espionagem YouTube (26/11) — canais de referência
- **Quiz Blitz** (2,51 mi inscritos, 1,1 mil vídeos): "Guess 120 Animals in 3 Seconds | Easy, Medium, Hard, Impossible" (27 mi, 16 min), "Guess all 195 flags" (13 mi), "Guess 52 Fruits", "Guess who's singing" (tema do momento, 15 mi).
- **Fun Quiz Questions** (294 mil, 505 vídeos, apresentadora com rosto): "Would You Rather… food edition" (7,1 mi), "Can You Pass High School Quiz?" (5,4 mi, 14 min), Guess the Song, General Knowledge.
- **Padrões:** (1) "GUESS THE ___" visual — imagem em vez de texto, qualquer idade/idioma; (2) número grande no título (120, 195, 52); (3) níveis Easy→Medium→Hard→Impossible; (4) 3 segundos por item; (5) vídeos LONGOS 12–16 min (público família/TV → tempo de exibição); (6) thumbnail colorida: faixa de título + grade de imagens reconhecíveis; (7) volume altíssimo; (8) surfar tema do momento; (9) "você passaria na escola?" / "would you rather".
- **Nossa versão (sem copiar marca/personagem com direitos):** Guess the Animal by its Shadow (emojis 3D → silhueta → revela), Guess the Country by its Shape (mapas world-atlas), Guess the Emoji Puzzle (combinação de emojis = palavra), Can You Pass 5th Grade/High School, Would You Rather. Todos com níveis Easy→Impossible, 3s por item, longo 10–15 min + shorts cortados por nível.

- 26/11: **guess01 — "Guess 100 Animals by Their Shadow | Easy → Impossible"** (8:48, 100 animais em 4 níveis, 3s cada) + **10 shorts** verticais + thumb COLORIDA (cards nas cores dos níveis) + legendas SEO. Script `tools/build_guess.py` + `tools/guess01_data.py` (reutilizável pra outros "Guess the ___").

- 27/11: TikTok: 74 seguidores, 92 curtidas. Riddle #1 e #2 ≈ 395 views cada (melhor que o formato antigo: 3 vídeos = 200 no total). Speed #1 = 98. Vários vídeos novos com 0–1 view (postados em sequência). Plano: máx. 2–3 posts/dia espaçados, priorizar formatos sem idioma (sombra, odd one out) + riddles; checar países da audiência.
- Os 74 seguidores do TikTok vieram quase todos da PROMOÇÃO paga (orgânico ainda ~0). Decisão: parar de pagar promoção até um vídeo provar retenção orgânica.
- **CORREÇÃO (27/11): o usuário MORA NOS EUA e a conta do TikTok é americana.** Descartar a hipótese de "conta brasileira/região". Público-alvo = EUA; horários de postagem em horário dos EUA.

- 27/11: **Instagram criado** (Brain rush quiz game). 3 reels: "90% fail question 3" (formato antigo) 638 views · Guess the Animal by Shadow 1.243 · Speed Quiz "Only 2% get 8/8" 1.305 — mas só 1 seguidor. Views vêm de não-seguidores; falta motivo pra seguir (perfil com poucos posts, sem série/"parte 2"). Instagram = repost dos mesmos arquivos do YouTube/TikTok.

## Sistema de chamadas (decidido em 27/11) — vale pra TODO vídeo novo
- Vídeos entregam bem (short com 5 curtidas em 5 min), mas pouca conversão em inscrito/seguidor.
- **Em todo short:** série "PART N" no topo; selo na metade "STILL PERFECT? SUBSCRIBE!" (YT) / "FOLLOW!" (TikTok/IG); final "SUBSCRIBE/FOLLOW FOR PART N+1" + voz.
- **2 versões por short:** `_yt` (YouTube, sino vermelho) e `_soc` (TikTok/Instagram, dedinho dourado).
- Link mágico `youtube.com/@brainrushquiz07?sub_confirmation=1` em bios e descrições. Guia completo: `quiz/roteiros/kit_chamadas.md`.
- Implementado em `tools/build_guess.py` (aplicar nos próximos builders também).

- Banco de temas: `quiz/roteiros/banco_de_temas.md` (usuário quer variar MUITO os temas — não só animais).

## Próximos passos
0. **FOCO ÚNICO: YouTube em inglês até monetizar.** Nada em português (decisão do usuário, 25/11 — evitar acúmulo). TikTok = só repost do mesmo arquivo, sem esforço extra.
   - Meta: entrar no Programa de Parcerias do YouTube (regra geral: 1.000 inscritos + 10 mi de views em Shorts em 90 dias, ou 4.000 h de exibição em vídeos longos; conferir no YouTube Studio › Ganhar dinheiro).
   - Rotina simples: usuário manda roteiro → eu entrego 5 shorts + 1 longo → usuário posta 2 shorts/dia + 1 longo/semana. Só isso.
1. Saber qual short teve as 800 views (qual tema/gancho) e dobrar a aposta no que ganhou.
2. Postar os shorts do vídeo 02 (2/dia). Vídeo 02 longo: segurar pro fim de semana.
3. Usuário manda ~3 roteiros/semana; eu entrego 5 shorts por roteiro + longo semanal.
4. Ideias de séries curtas: "Guess the Country by Its Shape", "Only Geniuses (Hard Mode)", "Human Body", "Space", "Guess the Flag/Logo", "Kids vs Adults questions".
5. Pendentes técnicos: voz (Kokoro vs ElevenLabs), chave do Pexels pra fotos reais.
