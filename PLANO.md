# Plano – Crescimento nas redes com GTA 6 (memória do projeto)

Última atualização: 24/11/2026.

> Conversa com o Claude: sempre em **português BR**. O idioma do conteúdo depende do canal (ver abaixo).

## Quem é o criador
- TikTok @jhonlivesx com ~34k seguidores **não gamers** (público aleatório). Também tem canal no YouTube. Está começando agora no nicho de games.
- Conteúdo em **português BR**, estilo **zoeira**.
- Tempo disponível: **só à noite, das 19h em diante** (trabalha de madrugada e durante o dia).
- Tem **PS5 + GTA 6 (pré-download)**, placa de captura e OBS (ainda se enrolando com o OBS). Quer fazer live na **Twitch**.
- Desconfortável em mostrar o rosto → formato escolhido: **Shorts de curiosidades narrados com voz de IA** (ElevenLabs). Ele grava a voz e manda; o Claude monta o vídeo.

> Existe também um **canal dark em inglês sobre dinheiro**, que é um projeto separado: ver `CANAL_DARK.md`.

## Estratégia decidida
- Mesmo vídeo vertical em **TikTok, YouTube Shorts e Instagram Reels**.
- Duração **65–75s** (TikTok só monetiza vídeo com mais de 1 min).
- Referências analisadas: **Hazard** (@HazardousHDTV, 727k – formatos repetíveis: X vs Y, "fases de", "faça isso agora", "ninguém usa", dinheiro; capas com texto grande em 2 cores; volume altíssimo) e **TGG** (@TGG_, 2,37M – humor/esquetes, legenda palavra por palavra). Fórmula: formato do Hazard + zoeira do TGG + jeitinho brasileiro.
- Meta: **2 vídeos por dia**.
- Futuro: usar o **gameplay dele** (mais seguro que trailer e exclusivo); considerar TikTok LIVE além da Twitch.

## O que já foi feito
| Vídeo | Status | Arquivo |
|---|---|---|
| "7 coisas que você precisa saber antes de jogar GTA 6" | **Postado em 18/11** | `videos/7coisas_gta6.mp4` |
| "As 5 fases de quem esperou o GTA 6" | Pronto, ainda não postado (sugestão: 18/11 à noite) | `videos/5fases_gta6.mp4` |

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

## Como os vídeos são montados (técnico)
- Scripts em `tools/`: `build_7coisas.py`, `build_5fases.py`, `capw.py` (legenda por palavra), `asr.py` (transcrição).
- Pipeline: narração mp3 → `asr.py` (faster-whisper "small", pt, `word_timestamps`) gera `voz_words.json` → legenda ASS palavra por palavra (fonte Anton) → cortes 9:16 do trailer/screenshots → overlays PNG (títulos, carimbos, barra de download, relógio) → trilha synthwave **gerada no próprio script** (sem direitos autorais) com ducking → ffmpeg.
- **Atenção:** a voz do ElevenLabs costuma ler o **título** no começo. Sempre transcrever com Whisper antes de sincronizar (nunca estimar por pausas).
- Material oficial: kit de imprensa da Rockstar (`https://www.rockstargames.com/VI/media`): `GTAVI_Launch_Trailer.mp4`, `GTAVI_Pre-Load_Now.mp4`, `GTAVI_Screenshots.zip`. Não está no repositório (pesado): baixar de novo para uma pasta de trabalho com a estrutura `rs/tr/...` esperada pelos scripts. Fonte Anton: pacote npm `@fontsource/anton` (converter .woff → .ttf com fontTools).
- Ambiente de nuvem "**Js-**" libera: rockstargames.com, media-rockstargames-com.akamaized.net, huggingface.co e CDNs do HF (necessário pro Whisper; usar `HF_HUB_DISABLE_XET=1`). YouTube é bloqueado.
- Sempre conferir quadros do vídeo final antes de entregar (sincronia legenda × fala × cena).
