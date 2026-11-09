---
name: extrator-pdf
description: Extrai o texto de um PDF para Markdown, página por página, com economia de tokens, decidindo por página entre texto nativo (PyMuPDF) e OCR (Tesseract) sem que o conteúdo passe pelo contexto do Claude durante a extração. Use sempre que o usuário pedir para converter, transcrever, extrair o texto de, ler integralmente ou fazer OCR em um PDF — especialmente PDFs longos (autos processuais, inquéritos, laudos) onde ler página por página via visão consumiria muitos tokens. Não use para simplesmente responder uma pergunta pontual sobre um PDF curto, nem para criar, mesclar, dividir, preencher ou assinar PDFs (use a skill "pdf" para isso).
---

# Extrator de PDF para Markdown (economia de tokens)

Converte um PDF em Markdown fiel, mantendo a ordem e a separação das páginas,
sem gastar tokens de contexto do Claude durante a extração em si — o script
faz o trabalho pesado sozinho no sandbox e só o relatório final (contagem de
páginas por fonte) chega até a conversa.

Fluxo padrão: `/mnt/user-data/uploads/<base>.pdf` → `<saida>/<base>.md`.

## Quando usar

- PDFs de autos processuais, inquéritos, laudos, decisões — qualquer PDF onde
  o objetivo é ter o texto completo em Markdown para análise posterior (por
  exemplo, como insumo da skill `analise-processual`), sem rasterizar cada
  página manualmente.
- PDFs mistos, com páginas de texto nativo e páginas escaneadas/imagem no
  mesmo arquivo.

Não é necessário para perguntas pontuais sobre 1-2 páginas de um PDF curto —
nesse caso, ler o PDF diretamente é mais simples e não pior em tokens.

## Verificação de dependências

Antes da primeira extração na sessão, rode:

```bash
python3 /mnt/skills/user/extrator-pdf/scripts/extrair_pdf.py --check-deps
```

Se algo faltar, o próprio comando imprime como resolver. Em geral, no sandbox
padrão:

```bash
pip install pymupdf pytesseract --break-system-packages
apt-get install -y tesseract-ocr tesseract-ocr-por
```

O Tesseract e o pacote de idioma inglês (`eng`) costumam já vir instalados;
o pacote de português (`tesseract-ocr-por`) normalmente precisa ser instalado
à parte. Isso só é necessário uma vez por sessão/sandbox — não repita a
instalação a cada PDF.

## Execução

```bash
# Processa todos os PDFs de /mnt/user-data/uploads sem .md correspondente ainda
python3 /mnt/skills/user/extrator-pdf/scripts/extrair_pdf.py --saida /mnt/user-data/outputs/md

# Processa arquivo(s) específico(s) — sempre reprocessa, mesmo se já existir .md
python3 /mnt/skills/user/extrator-pdf/scripts/extrair_pdf.py /mnt/user-data/uploads/inquerito.pdf --saida /mnt/user-data/outputs/md
```

Use `--force` apenas se o usuário pedir para reprocessar todo o lote de um
diretório de entrada. Ao apontar arquivos explicitamente, o script já
reprocessa por padrão.

O script aplica a cada página, de forma independente:

1. Extrai o texto nativo com PyMuPDF (`page.get_text()`).
2. Se o texto, após remover espaços nas extremidades, tiver **400 caracteres
   ou mais**, grava esse texto e marca a fonte como `texto nativo`.
3. Se tiver **menos de 400 caracteres**, rasteriza só essa página (via
   PyMuPDF, sem depender de poppler/pdftoppm) e roda o Tesseract nela. O
   texto do Tesseract substitui o texto nativo curto quando o OCR produz
   conteúdo, e a fonte é marcada `Tesseract`.
4. Se o Tesseract falhar ou não produzir texto, preserva o texto nativo que
   existir e marca a página como `pendente`, com `**OCR PENDENTE**` no corpo.

Não classifique o documento inteiro como nativo ou digitalizado: a decisão é
sempre por página. O script não resume, corrige, completa ou interpreta o
conteúdo extraído — é transcrição literal.

Idioma padrão do OCR: `por+eng`. Ajuste com `--lang` se o documento for só em
outro idioma (isso reduz falsas correções do Tesseract).

## Páginas pendentes

Se, ao final, alguma página ficar marcada `pendente`, a extração ficou
incompleta nesses pontos — normalmente PDFs com imagem de qualidade muito
baixa ou corrompida. Informe ao usuário, por arquivo, quais páginas falharam.

Como alternativa, você (Claude) pode ler visualmente só essas páginas
específicas (rasterizando com `pdftoppm` ou PyMuPDF e usando sua própria
visão), mas isso reintroduz o custo de tokens que esta skill existe para
evitar — faça isso só quando o usuário pedir explicitamente e apenas para as
páginas realmente pendentes, nunca para o documento inteiro. Depois, substitua
o marcador `**OCR PENDENTE**` pelo texto transcrito e atualize o comentário de
fonte da página para `leitura visual`.

## Saída e relatório

Cada página do `.md` gerado começa com
`<!-- página N | fonte: texto nativo|Tesseract|pendente -->` e é separada da
seguinte por uma linha horizontal (`---`). Preserve esse marcador — ele é o
que permite rastrear, depois, de onde veio cada trecho.

Ao final da execução, o script já imprime um relatório com: PDFs processados,
ignorados (já tinham `.md`) e com erro, e por PDF processado, quantas páginas
vieram de texto nativo, Tesseract ou ficaram pendentes. Repasse esse
relatório ao usuário de forma direta, sem reabrir os `.md` gerados para
resumir o conteúdo — isso anularia a economia de tokens que é o objetivo da
skill.
