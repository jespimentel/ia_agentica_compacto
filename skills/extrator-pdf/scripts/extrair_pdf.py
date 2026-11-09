#!/usr/bin/env python3
"""
Extrator de PDF para Markdown, com economia de tokens.

Para cada página de cada PDF, decide de forma independente entre texto nativo
(PyMuPDF) e OCR (Tesseract), gravando o resultado direto em disco. Nada do
conteúdo do PDF passa pelo contexto do Claude durante a extração — só o
relatório final (contagens por página) é reportado na conversa.

Uso:
    python3 extrair_pdf.py --check-deps
    python3 extrair_pdf.py <arquivo1.pdf> [<arquivo2.pdf> ...] [--saida DIR] [--force] [--lang por+eng]
    python3 extrair_pdf.py --entrada DIR [--saida DIR] [--force]

Sem nenhum PDF explícito e sem --entrada, processa todos os *.pdf de
/mnt/user-data/uploads que ainda não têm .md correspondente em --saida.
"""

import argparse
import shutil
import sys
from pathlib import Path

LIMIAR_CARACTERES = 400
ENTRADA_PADRAO = Path("/mnt/user-data/uploads")
SAIDA_PADRAO = Path("/mnt/user-data/outputs/md")
DPI_OCR = 250


def checar_dependencias(idioma: str) -> bool:
    ok = True

    try:
        import pymupdf  # noqa: F401
        print(f"[ok] pymupdf {pymupdf.__version__}")
    except ImportError:
        print("[FALTA] pymupdf — instale com: pip install pymupdf --break-system-packages")
        ok = False

    try:
        import pytesseract
    except ImportError:
        print("[FALTA] pytesseract — instale com: pip install pytesseract --break-system-packages")
        ok = False
        pytesseract = None

    if shutil.which("tesseract") is None:
        print("[FALTA] binário tesseract — instale com: apt-get install -y tesseract-ocr")
        ok = False
    else:
        print("[ok] binário tesseract encontrado")

    if pytesseract is not None and shutil.which("tesseract") is not None:
        try:
            disponiveis = set(pytesseract.get_languages(config=""))
        except Exception as e:
            print(f"[FALTA] não consegui listar idiomas do tesseract: {e}")
            disponiveis = set()

        for lang in idioma.split("+"):
            if lang in disponiveis:
                print(f"[ok] idioma '{lang}' disponível")
            else:
                print(
                    f"[FALTA] idioma '{lang}' não instalado — instale com: "
                    f"apt-get install -y tesseract-ocr-{lang}"
                )
                ok = False

    return ok


def extrair_pagina(pagina, idioma: str) -> tuple[str, str]:
    """Retorna (texto, fonte) para uma página, aplicando a regra dos 400 caracteres."""
    texto_nativo = pagina.get_text().strip()

    if len(texto_nativo) >= LIMIAR_CARACTERES:
        return texto_nativo, "texto nativo"

    # Abaixo do limiar: tenta OCR apenas nesta página.
    try:
        import pytesseract

        zoom = DPI_OCR / 72
        matriz = __import__("pymupdf").Matrix(zoom, zoom)
        pix = pagina.get_pixmap(matrix=matriz)
        imagem = pix.pil_image() if hasattr(pix, "pil_image") else None
        if imagem is None:
            from PIL import Image
            import io

            imagem = Image.open(io.BytesIO(pix.tobytes("png")))

        texto_ocr = pytesseract.image_to_string(imagem, lang=idioma).strip()
    except Exception:
        texto_ocr = ""

    if texto_ocr:
        return texto_ocr, "Tesseract"

    # OCR falhou ou não produziu nada: preserva o texto nativo curto, se houver.
    return texto_nativo, "pendente"


def extrair_pdf(caminho_pdf: Path, caminho_md: Path, idioma: str) -> dict:
    import pymupdf

    doc = pymupdf.open(caminho_pdf)
    contagem = {"texto nativo": 0, "Tesseract": 0, "pendente": 0}
    partes = []

    for i, pagina in enumerate(doc, start=1):
        texto, fonte = extrair_pagina(pagina, idioma)
        contagem[fonte] += 1
        cabecalho = f"<!-- página {i} | fonte: {fonte} -->"
        if fonte == "pendente":
            corpo = (texto + "\n\n" if texto else "") + "**OCR PENDENTE**"
        else:
            corpo = texto
        partes.append(f"{cabecalho}\n\n{corpo}")

    doc.close()

    caminho_md.parent.mkdir(parents=True, exist_ok=True)
    caminho_md.write_text("\n\n---\n\n".join(partes), encoding="utf-8")

    return contagem


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdfs", nargs="*", help="Caminhos de PDFs específicos a processar (reprocessa mesmo se já existir .md)")
    ap.add_argument("--entrada", type=Path, default=None, help=f"Diretório de entrada (padrão: {ENTRADA_PADRAO})")
    ap.add_argument("--saida", type=Path, default=SAIDA_PADRAO, help=f"Diretório de saída dos .md (padrão: {SAIDA_PADRAO})")
    ap.add_argument("--lang", default="por+eng", help="Idiomas do Tesseract, ex.: por+eng (padrão) ou eng")
    ap.add_argument("--force", action="store_true", help="Reprocessa todo o lote de --entrada, mesmo com .md existente")
    ap.add_argument("--check-deps", action="store_true", help="Só verifica as dependências e sai")
    args = ap.parse_args()

    if args.check_deps:
        ok = checar_dependencias(args.lang)
        sys.exit(0 if ok else 1)

    if not checar_dependencias(args.lang):
        print("\nDependências ausentes. Resolva os itens acima antes de continuar.")
        sys.exit(1)

    args.saida.mkdir(parents=True, exist_ok=True)

    if args.pdfs:
        pdfs = [Path(p) for p in args.pdfs]
        explicitos = True
    else:
        entrada = args.entrada or ENTRADA_PADRAO
        pdfs = sorted(entrada.glob("*.pdf"))
        explicitos = False

    if not pdfs:
        print("Nenhum PDF encontrado para processar.")
        sys.exit(0)

    processados = []
    ignorados = []
    com_erro = []

    for pdf in pdfs:
        if not pdf.exists():
            print(f"[erro] arquivo não encontrado: {pdf}")
            com_erro.append((pdf.name, "arquivo não encontrado"))
            continue

        md = args.saida / f"{pdf.stem}.md"
        if md.exists() and not explicitos and not args.force:
            ignorados.append(pdf.name)
            continue

        print(f"Processando {pdf.name} ...")
        try:
            contagem = extrair_pdf(pdf, md, args.lang)
        except Exception as e:
            print(f"[erro] falha ao processar {pdf.name}: {e}")
            com_erro.append((pdf.name, str(e)))
            continue
        processados.append((pdf.name, md, contagem))

    print("\n=== Relatório ===")
    print(f"PDFs processados: {len(processados)}")
    print(f"PDFs ignorados (já tinham .md): {len(ignorados)}")
    print(f"PDFs com erro: {len(com_erro)}")
    for nome, md, contagem in processados:
        total = sum(contagem.values())
        print(
            f"- {nome} -> {md} "
            f"({total} páginas: {contagem['texto nativo']} texto nativo, "
            f"{contagem['Tesseract']} Tesseract, {contagem['pendente']} pendente)"
        )
    if ignorados:
        print(f"Ignorados: {', '.join(ignorados)}")
    for nome, erro in com_erro:
        print(f"[erro] {nome}: {erro}")


if __name__ == "__main__":
    main()
