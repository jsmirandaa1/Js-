# Plano – Crescimento nas redes com GTA 6 (memória do projeto)

Última atualização: 18/11/2026 (véspera do lançamento do GTA 6, que libera 19/11 às 00:00 de Brasília, PS5/Xbox Series, sem PC).

## Quem é o criador
- TikTok @jhonlivesx com ~34k seguidores **não gamers** (público aleatório). Também tem canal no YouTube. Está começando agora no nicho de games.
- Conteúdo em **português BR**, estilo **zoeira**.
- Tempo disponível: **só à noite, das 19h em diante** (trabalha de madrugada e durante o dia).
- Tem **PS5 + GTA 6 (pré-download)**, placa de captura e OBS (ainda se enrolando com o OBS). Quer fazer live na **Twitch**.
- Desconfortável em mostrar o rosto → formato escolhido: **Shorts de curiosidades narrados com voz de IA** (ElevenLabs). Ele grava a voz e manda; o Claude monta o vídeo.

## Identidade visual (19/11) – EM ABERTO
- 1ª tentativa (recorte da foto real + fundo neon Vice City/GTA 6, logo "JHON LIVES") foi **reprovada** pelo usuário: recorte ruim, não quer GTA 6 nem fundo de GTA na marca.
- O que ele quer: **ilustração/caricatura com o rosto dele**, usando a foto só como referência. Claude não gera imagem por IA → caminho combinado: usuário gera a ilustração numa ferramenta de imagem (prompt fornecido no chat) e Claude monta perfil + capas (YouTube 2560x1440 com área segura 1546x423, Twitch 1200x480) em cima dela.
- @: YouTube/Twitch @jhonlivesx (confirmar Twitch); TikTok @jhonexlives (muda em ~20 dias).
- Repositório é público: não commitar fotos/artes com o rosto.

## Cortes da live (19/11) – VOD Twitch 2933162928 "GTA 6 AO VIVO" (2h14)
- Pipeline: yt-dlp (áudio) + Whisper + picos de volume; vídeo baixado só nos trechos (segmentos .ts do m3u8). Chat bloqueado (não usar client-id interno). Facecam no canto inferior direito → formato vertical facecam em cima + jogo embaixo. Trechos silenciados (direitos autorais): 48:06–51:12 e 69:12–75:18.
- Hosts liberados no ambiente: www.twitch.tv, gql.twitch.tv, usher.ttvnw.net, d1m7jfoe9zdc1j.cloudfront.net.
- Candidatos: (1) 32:20–33:40 "dei um tiro sem querer" + morte; (2) 35:45–39:10 "não sei mais mirar" + 2ª morte; (3) 95:30–96:40 "tem camaleão?"; (4) 22:00–23:20 passeio de barco "meu Deus"; (5) 59:00–60:20 basquete no jogo. Evitar cutscenes da história (spoiler).
- **Cortes entregues (19/11):** "Eu tentando ser discreto no GTA 6" (32:30–33:22 + 35:46–35:56 + 38:20–38:57, 1:39), "O gráfico do GTA 6 é surreal" (barco 21:58–23:18, 1:20), "Dá pra jogar basquete no GTA 6?" (59:00–60:20, 1:20). Corte extra "Caiu um carro da ponte no GTA 6" (queda em 2:04:49; gancho 2s em câmera lenta + 7474–7522 + replay lento, 1:08) – pelas legendas do jogo ("a ponte não conecta") é evento da missão, não bug. Corte "Caiu uma caminhonete da ponte no GTA 6" (o que o usuário queria: esportivo vermelho roubado do pátio da polícia levado pro Brian; 1:25:08–1:26:25 + replay lento 1:25:55–1:26:04; 1:35). O corte da ponte da missão (2:04:49) não era o momento pedido. Todos os cortes refeitos no estilo cru. Camaleão descartado (bicho não aparece na tela). Vídeos NÃO commitados (rosto, repo público). Script: `tools/build_cortes_live.py` (transcrição de clipe com vad_filter=True, senão perde a voz dele).
- Feedback: ele fala pouco na live (transcrição é quase só diálogo do jogo) → incentivar narrar/reagir mais.

## Preferências de edição (19/11)
- Cortes: vídeo cru, só título fixo; sem legendas/textos no meio. Todo vídeo termina com "ME SEGUE" + @jhonexlives (TikTok) e @jhonlivesx (YouTube/Twitch).

## Shorts 6 e 7 (20/11) – adaptação de conteúdo gringo
- Roteiros em `roteiros/shorts-06-07-gringos.md`: "3 segredos que os gringos acharam" (Dexter, ovo na torre, Pé Grande) e "Primeira pessoa (truque)". Aguardando narração; Shorts 7 idealmente com gameplay dele fazendo o truque.
- Sites de notícia (gamingbible, gamerant, gamespot) não abrem no ambiente; pesquisa feita via busca.

## Estratégia decidida
- Variar formatos (o usuário pediu): lista narrada, "fases", linha do tempo em texto na tela. Formato texto na tela + música é útil quando ele não pode gravar voz.
- Mesmo vídeo vertical em **TikTok, YouTube Shorts e Instagram Reels**.
- Duração **65–75s** (TikTok só monetiza vídeo com mais de 1 min). Se a narração ficar curta, estender o final (tela final/piada) até ≥ 61s.
- Referências analisadas: **Hazard** (@HazardousHDTV, 727k – formatos repetíveis: X vs Y, "fases de", "faça isso agora", "ninguém usa", dinheiro; capas com texto grande em 2 cores; volume altíssimo) e **TGG** (@TGG_, 2,37M – humor/esquetes, legenda palavra por palavra). Fórmula: formato do Hazard + zoeira do TGG + jeitinho brasileiro.
- Meta: **2 vídeos por dia**.
- Futuro: usar o **gameplay dele** (mais seguro que trailer e exclusivo); considerar TikTok LIVE além da Twitch.

## O que já foi feito
| Vídeo | Status | Arquivo |
|---|---|---|
| "7 coisas que você precisa saber antes de jogar GTA 6" | **Postado em 18/11** | `videos/7coisas_gta6.mp4` |
| "As 5 fases de quem esperou o GTA 6" | Pronto, ainda não postado (sugestão: 18/11 ~22h) |
| "13 anos em 1 minuto: linha do tempo do GTA 6" (formato texto na tela + música, sem voz) | Pronto em 18/11 (`videos/linha_do_tempo_gta6.mp4`, legendas em `roteiros/shorts-04-linha-do-tempo.md`) |
| "POV: faltam 5 minutos pro GTA 6" (POV narrado) | Pronto (`videos/pov_5min_gta6.mp4`, 1:01,7); postar 18/11 23h–23h40 |
| "O que todo brasileiro vai fazer na primeira hora de GTA 6" | Roteiro pronto (`roteiros/shorts-03-brasileiro-primeira-hora.md`), aguardando narração do usuário | `videos/5fases_gta6.mp4` |

- Roteiros: `roteiros/shorts-gta6-lancamento.md`
- Legendas dos posts (TikTok / Reels / Shorts): `roteiros/legendas-posts.md`
- O "7 coisas" diz "hoje à meia-noite" → só serve pra postar em 18/11.

## Próximos passos (ordem)
1. Confirmar se o "5 fases" foi postado e saber como foram os 2 primeiros posts (views, retenção, comentários) e ajustar.
2. **"Segredos do GTA 6 que ninguém te contou"** (prometido no fim do "7 coisas") – idealmente com gameplay dele gravado após o lançamento.
3. Banco de ideias pendente:
   - "GTA 5 vs GTA 6: o que mudou em 13 anos"
   - "Mude ISSO antes de jogar GTA 6" (configurações)
   - "Primeiro dinheiro FÁCIL no GTA 6"
   - "Jason ou Lúcia: quem é melhor?"
   - "O que acontece se você… no GTA 6" (série)
   - "Preço das coisas: GTA 6 vs Brasil" (carro do jogo vs Tabela Fipe)
   - "Coisas que só brasileiro faria no GTA 6"
   - "As fases de jogar GTA 6 de madrugada"
   - "GTA 6 é mais realista que o Brasil?"
   - Formatos fixos: X vs Y, As fases de…, Ninguém usa isso, Respondendo comentário.
4. Montar calendário das 2 primeiras semanas pós-lançamento.
5. **Vídeo longo #1** – "Guia completo: primeiras horas no GTA 6 (sem spoiler)", 10–12 min, horizontal. Roteiro com capítulos em `roteiros/longo-01-guia-primeiras-horas.md`. Faltam: o usuário jogar e preencher os [PREENCHER] (mecânicas reais), gravar gameplay por capítulo e a narração (um áudio por capítulo).

### Vídeos longos (decisões)
- Base visual = gameplay do usuário (trailer só no gancho) para evitar "conteúdo reutilizado" e repetição.
- Começar com 8–12 min (anúncio no meio a partir de 8 min). Voz própria recomendada; IA aceita, 1 arquivo por capítulo.
- Usuário manda clipes cortados por capítulo ou lista de minutos; Claude não "assiste" horas de vídeo bruto.
- Render de ~20 min leva 1–2 h no container (rodar em segundo plano).

## Como os vídeos são montados (técnico)
- Scripts em `tools/`: `build_7coisas.py`, `build_5fases.py`, `capw.py` (legenda por palavra), `asr.py` (transcrição).
- Pipeline: narração mp3 → `asr.py` (faster-whisper "small", pt, `word_timestamps`) gera `voz_words.json` → legenda ASS palavra por palavra (fonte Anton) → cortes 9:16 do trailer/screenshots → overlays PNG (títulos, carimbos, barra de download, relógio) → trilha synthwave **gerada no próprio script** (sem direitos autorais) com ducking → ffmpeg.
- **Atenção:** a voz do ElevenLabs costuma ler o **título** no começo. Sempre transcrever com Whisper antes de sincronizar (nunca estimar por pausas).
- Material oficial: kit de imprensa da Rockstar (`https://www.rockstargames.com/VI/media`): `GTAVI_Launch_Trailer.mp4`, `GTAVI_Pre-Load_Now.mp4`, `GTAVI_Screenshots.zip`. Não está no repositório (pesado): baixar de novo para uma pasta de trabalho com a estrutura `rs/tr/...` esperada pelos scripts. Fonte Anton: pacote npm `@fontsource/anton` (converter .woff → .ttf com fontTools).
- Ambiente de nuvem "**Js-**" libera: rockstargames.com, media-rockstargames-com.akamaized.net, huggingface.co e CDNs do HF (necessário pro Whisper; usar `HF_HUB_DISABLE_XET=1`). YouTube é bloqueado.
- Sempre conferir quadros do vídeo final antes de entregar (sincronia legenda × fala × cena).
