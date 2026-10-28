#!/usr/bin/env python3
"""Converte .docx em .md usando apenas a biblioteca padrao.
Uso: python3 docx2md.py <pasta_origem> <pasta_references> [--force]
"""
import re, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def run_text(r):
    out = []
    for el in r:
        if el.tag == W + 't':
            out.append(el.text or '')
        elif el.tag == W + 'tab':
            out.append(' ')
        elif el.tag in (W + 'br', W + 'cr'):
            out.append('\n')
    return ''.join(out)

def is_bold(r):
    rpr = r.find(W + 'rPr')
    b = rpr.find(W + 'b') if rpr is not None else None
    return b is not None and b.get(W + 'val') not in ('0', 'false', 'none')

def para_md(p):
    segs = []
    for r in p.iter(W + 'r'):
        t = run_text(r)
        if not t:
            continue
        b = is_bold(r)
        if segs and segs[-1][1] == b:
            segs[-1][0] += t
        else:
            segs.append([t, b])
    out = ''
    for t, b in segs:
        if b and t.strip():
            lead = t[:len(t) - len(t.lstrip())]
            trail = t[len(t.rstrip()):]
            out += f'{lead}**{t.strip()}**{trail}'
        else:
            out += t
    out = re.sub(r'[  ]{2,}', ' ', out).strip()
    st = p.find(f'{W}pPr/{W}pStyle')
    if out and st is not None:
        m = re.match(r'(?:heading|t[ií]tulo)\s*(\d)', st.get(W + 'val', ''), re.I)
        if m:
            out = '#' * min(int(m.group(1)), 6) + ' ' + out.replace('**', '')
    return out

def table_md(tbl):
    rows = []
    for tr in tbl.findall(W + 'tr'):
        cells = [' '.join(filter(None, (para_md(p) for p in tc.iter(W + 'p')))).replace('|', '/')
                 for tc in tr.findall(W + 'tc')]
        rows.append('| ' + ' | '.join(cells) + ' |')
    if rows:
        n = rows[0].count('|') - 1
        rows.insert(1, '|' + ' --- |' * n)
    return '\n'.join(rows)

def convert(src, dst):
    with zipfile.ZipFile(src) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    blocks = []
    for el in root.find(W + 'body'):
        if el.tag == W + 'p':
            t = para_md(el)
        elif el.tag == W + 'tbl':
            t = table_md(el)
        else:
            continue
        if t:
            blocks.append(t)
    text = '\n\n'.join(blocks) + '\n'
    dst.write_text(text, encoding='utf-8')
    return len(text)

def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    force = '--force' in sys.argv
    if len(args) != 2:
        sys.exit(__doc__)
    src_dir, ref_dir = Path(args[0]), Path(args[1])
    ref_dir.mkdir(parents=True, exist_ok=True)
    ok, skip, err, curtos = [], [], [], []
    for f in sorted(src_dir.iterdir(), key=lambda p: p.name):
        if f.suffix.lower() != '.docx' or f.name.startswith('~$'):
            continue
        dst = ref_dir / (f.stem + '.md')
        if dst.name.lower() == 'indice.md':
            err.append(f'{f.name}: nome reservado ao indice (renomear o .docx)')
            continue
        if dst.exists() and not force and dst.stat().st_mtime >= f.stat().st_mtime:
            skip.append(f.name)
            continue
        try:
            n = convert(f, dst)
            ok.append(f.name)
            if n < 500:
                curtos.append(f.name)
        except Exception as e:
            err.append(f'{f.name}: {e}')
    outros = sorted(p.name for p in src_dir.iterdir()
                    if p.is_file() and p.suffix.lower() in ('.doc', '.odt', '.rtf', '.pdf'))
    print(f'Convertidos: {len(ok)} | Ja existentes (pulados): {len(skip)} | Erros: {len(err)}')
    for o in ok:
        print('CONVERTIDO (resumir):', o)
    for e in err:
        print('ERRO', e)
    for c in curtos:
        print('ATENCAO texto muito curto (verificar):', c)
    for o in outros:
        print('IGNORADO (formato nao .docx):', o)

if __name__ == '__main__':
    main()
