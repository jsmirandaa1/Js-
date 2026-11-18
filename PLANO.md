# Plano – Crescimento nas redes com GTA 6 (memória do projeto)

Última atualização: 18/11/2026 (véspera do lançamento do GTA 6, que libera 19/11 às 00:00 de Brasília, PS5/Xbox Series, sem PC).

## Quem é o criador
- TikTok @jhonlivesx com ~34k seguidores **não gamers** (público aleatório). Também tem canal no YouTube. Está começando agora no nicho de games.
- Conteúdo em **português BR**, estilo **zoeira**.
- Tempo disponível: **só à noite, das 19h em diante** (trabalha de madrugada e durante o dia).
- Tem **PS5 + GTA 6 (pré-download)**, placa de captura e OBS (ainda se enrolando com o OBS). Quer fazer live na **Twitch**.
- Desconfortável em mostrar o rosto → formato escolhido: **Shorts de curiosidades narrados com voz de IA** (ElevenLabs). Ele grava a voz e manda; o Claude monta o vídeo.

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
