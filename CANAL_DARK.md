# Canal Dark – Dinheiro (em inglês)

Última atualização: 24/11/2026.

> Projeto **separado** do GTA 6 (que está em `PLANO.md`). Conversa com o Claude em português BR; todo o conteúdo do canal sai em **inglês**.

## O que é
- **Canal dark** (sem rosto, sem a voz real dele) sobre **dinheiro**, em inglês, pro público gringo.
- Nome: **The Wealth Blueprint** (slogan: "Understand money. Build wealth.").
- Formato do ep. 001: **vídeo longo de 8–10 min**, narração em inglês americano, voz masculina grave e calma.
- Objetivo: **crescer o canal** primeiro e **monetizar depois**.

## Decisões em aberto
- @ do canal e plataformas (YouTube só, ou também TikTok/Reels).
- Formato: Shorts, vídeo longo, ou os dois.
- Recorte do nicho (renda extra, investimento, histórias de ricos/falências, psicologia do dinheiro, etc.).
- Voz (ElevenLabs em inglês?) e estilo visual.

## Cuidados (monetização no YouTube)
- O YouTube corta monetização de conteúdo "inautêntico": vídeo em massa, repetitivo, só voz de IA lendo texto genérico em cima de imagem de banco. Pra passar: roteiro original com opinião e ângulo próprio, edição caprichada e formatos variados.
- Não prometer ganho fácil e não dar "dica de investimento" garantida. Isso derruba a confiança e pode bater nas regras de golpe/spam.

## Vídeos
| Vídeo | Status | Arquivos |
|---|---|---|
| Ep. 001 – "The First $100,000 Is the Hardest — Here's Why" | **Pronto (24/11/2026)**, aguardando postar | vídeo `videos/dark/ep001_first_100k.mp4` · thumb `videos/dark/ep001_thumbnail.png` · legenda `videos/dark/ep001_first_100k.en.srt` · roteiro `roteiros/dark/ep001-first-100k.md` · título/descrição/tags `roteiros/dark/ep001-publicacao.md` |

## Como o Ep. 001 foi feito (técnico)
- **Voz:** Kokoro TTS (open source, roda local, sem custo), mistura de 60% `am_michael` + 40% `am_onyx` (grave, ~106 Hz), velocidade 0.88, gerada frase a frase. Valores em dólar escritos por extenso no texto da TTS (senão ela lê errado). Modelo: `kokoro-onnx` + `kokoro-v1.0.onnx`/`voices-v1.0.bin` (GitHub releases do thewh1teagle/kokoro-onnx).
- Pausas: 0,65–0,85s entre frases, ~4s entre capítulos, +4s pro título depois do gancho, +9s no final pra tela final do YouTube. Duração: **8m25s**.
- **Visual:** 100% motion graphics em Python/pycairo (`tools/dark/ep001_build.py`), 1080p30, paleta azul-marinho + dourado, fontes Playfair Display (títulos) e Inter (números/textos). Cada animação é sincronizada pelo tempo da frase (timeline do TTS) e pelas palavras (Whisper `small.en`).
- **Trilha:** gerada no script (`tools/dark/ep001_music.py`): ambiente em Ré menor (Dm–Bb–F–C), pad + grave + piano + pulso nos capítulos 3–4 + risers/booms nas trocas de capítulo. Sem direitos autorais.
- **Mix:** ducking da trilha pela voz, master em -14 LUFS.
- **Extras:** `tools/dark/ep001_extras.py` gera thumbnail, `.srt` e capítulos.
- Bancos de vídeo (Pexels etc.) seguem bloqueados nesta nuvem.

## Próximos passos
1. Postar o Ep. 001 no YouTube (seguir `roteiros/dark/ep001-publicacao.md`) e contar como foi (CTR da thumb, retenção nos primeiros 30s, comentários).
2. Se quiser trocar a voz por ElevenLabs: mandar o mp3 que eu ressincronizo tudo (a timeline é recalculada pelo Whisper).
3. Ep. 002: definir tema. Formato "Wealth Blueprint" (documentário 8–10 min) reaproveita o motor de animação.
4. Definir as decisões em aberto acima (@, Shorts de corte do episódio pra divulgar, frequência).

Pastas: roteiros em `roteiros/dark/`, vídeos em `videos/dark/`, scripts em `tools/dark/`.
