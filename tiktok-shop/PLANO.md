# Projeto TikTok Shop

Projeto separado do plano de GTA 6 (que fica no `PLANO.md` da raiz). **Início:** 24/11/2026

## Objetivo
Vender como afiliado no TikTok Shop com vídeos de apresentação curtos (18s), sem voz: imagem, texto chamativo e trilha.

## O que já foi feito (24/11)
6 produtos analisados a partir dos links do usuário. O 4º link veio repetido. A página completa do produto pede captcha, então nome, preço e foto vieram do próprio link de compartilhamento. Não deu pra ver se já existia vídeo de apresentação, então foi feito vídeo pra todos.

| # | Produto | Preço no link | Vídeo | Formato |
|---|---|---|---|---|
| 01 | Escova Modeladora WAKESHOW 38mm | R$ 159 (-53%) | `videos/01_escova_modeladora_wakeshow.mp4` | modelo IA |
| 02 | Sandália Infantil Kidstep | R$ 20,94 (-79%) | `videos/02_sandalia_infantil_kidstep.mp4` | foco no produto |
| 03 | Escova Secadora GOKOCO 5 em 1 | R$ 439 (-4%, sem selo) | `videos/03_escova_secadora_gokoco_5em1.mp4` | modelo IA |
| 04 | Kit Panelas Munique 11 pçs | a partir de R$ 260,90 (-47%) | `videos/04_kit_panelas_munique_11pcs.mp4` | modelo IA |
| 05 | Suporte Controles tema GTA VI | a partir de R$ 43,90 (-31%) | `videos/05_suporte_controles_gta6.mp4` | foco no produto |
| 06 | Relógio Inteligente T900 | R$ 33 (-87%) | `videos/06_smartwatch_t900.mp4` | foco no produto |

- Legendas, título do link, comentário fixado e guia de postagem: `roteiros/legendas.md`
- Decisão do usuário: só usar pessoa quando ajudar a vender (beleza e casa). O resto fica com foco no produto.

## Como os vídeos são montados (técnico)
- `tools/produtos.py`: roteiro de cada vídeo (textos, cores, preço, imagens). `tools/build.py <chave>` gera o mp4 (1080x1920, 18s, trilha sintetizada sem direitos autorais, loudnorm -14 LUFS). Com `python3 build.py <chave> 1.0,5,10` só salva quadros de prévia em `/tmp/tts_<chave>/`.
- Cenas: gancho (0–3,2s) → produto + selo de desconto → 4 benefícios → desejo → preço + "TOCA NO CARRINHO" com seta pro canto inferior esquerdo (onde fica o link do produto).
- Fotos dos produtos: `assets/prod/` (CDN `p16-oec-sg.ibyteimg.com`, a URL vem no `og_info` do redirect do link `vt.tiktok.com`).
- Modelos/cenários de IA: `assets/ia/`. Gerados no CPU com **Realistic Vision 5.1 + LCM LoRA** (licença creativeml-openrail-m, uso comercial ok), ~1 min por imagem, 512x896. **Sempre conferir as imagens:** a IA às vezes gera nudez. Usar roupa fechada no prompt (gola alta, suéter) e descartar o que sair impróprio.
- Fontes em `fonts/` (Anton + Montserrat).
- Pexels: a chave salva no ambiente dá 401. O Pexels exige a chave **sem** "Bearer", e o formulário coloca "Bearer". Para usar, editar o segredo nas configurações do ambiente sem prefixo.

## ⚠️ Lição aprendida (24/11): esse formato NÃO serve pro TikTok Shop
O vídeo do smartwatch levou violação com **-4 pontos**, redução de visibilidade e remoção do produto do vídeo. Motivo: "imagens estáticas / slides / texto animado com pouco movimento". Os outros dois que sumiram provavelmente caíram no mesmo motivo.
- **Nunca mais** fazer vídeo de TikTok Shop com foto do produto + texto animado + zoom (o formato do `tools/build.py`).
- O TikTok Shop exige **vídeo real e dinâmico**: produto na mão, em uso, sendo mostrado de verdade.
- Caminho certo: pedir **amostra grátis** no Centro de Afiliados e gravar com o celular, ou usar os **vídeos oficiais do vendedor** liberados no Centro de Afiliados. Claude ajuda com roteiro, gancho, cortes, legenda e edição do vídeo gravado.
- Os vídeos em `videos/` só servem fora do TikTok Shop (Stories, status, Reels sem link de produto).

## Próximos passos
1. Apagar os vídeos desse formato que ainda estão no ar com link de produto, pra não juntar mais pontos.
2. Ver no Centro de Afiliados quais produtos têm amostra grátis ou vídeo do vendedor, e montar roteiros de gravação.
3. Saber como foram os primeiros posts (views, cliques no produto, vendas) e fazer mais vídeos dos que venderem (mesmo produto, gancho diferente).
4. Antes de cada post, conferir se preço e desconto ainda batem com a loja. Se mudar, atualizar em `produtos.py` e renderizar de novo.
5. Novos produtos: o usuário manda os links e o processo se repete.
