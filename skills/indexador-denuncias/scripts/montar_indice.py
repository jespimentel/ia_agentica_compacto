#!/usr/bin/env python3
"""Monta/atualiza references/indice.md a partir das entradas redigidas.
Uso: python3 montar_indice.py <pasta_destino> <pasta_entradas>
<pasta_destino> e a pasta que contem references/. O indice fica em
<pasta_destino>/references/indice.md, com cabecalhos '### <nome>.md'.
Cada entrada: <pasta_entradas>/<nome do arquivo sem extensao>.txt com o resumo.
Se existir um indice.md antigo na raiz de <pasta_destino> (formato v1, com
cabecalhos '.docx'), suas entradas sao aproveitadas; o arquivo antigo nao e apagado.
"""
import re, sys
from pathlib import Path

CAB = ('# Índice das denúncias\n\n'
       'Cada entrada traz o nome exato do arquivo em `references/` e um resumo padronizado: '
       'sujeitos; conduta nuclear com dados objetivos; contexto da descoberta e situação prisional; '
       'enquadramento. Leia aqui os resumos e abra apenas a peça escolhida.\n')

RESERVADO = 'indice.md'

def chave(nome):
    nome = nome.strip()
    return nome[:-5] + '.md' if nome.lower().endswith('.docx') else nome

def ler_blocos(path):
    blocos = {}
    texto = path.read_text(encoding='utf-8')
    for m in re.finditer(r'^### (.+?)\n(.*?)(?=^### |\Z)', texto, re.M | re.S):
        blocos[chave(m.group(1))] = m.group(2).strip()
    return blocos

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    dest, ent = Path(sys.argv[1]), Path(sys.argv[2])
    refdir = dest / 'references'
    idx = refdir / RESERVADO
    antigo = dest / RESERVADO
    blocos = {}
    if idx.exists():
        blocos = ler_blocos(idx)
    elif antigo.exists():
        blocos = ler_blocos(antigo)
        print('MIGRACAO: entradas lidas de', antigo, '(arquivo antigo mantido; pode ser apagado)')
    for f in ent.glob('*.txt'):
        blocos[f.stem + '.md'] = f.read_text(encoding='utf-8').strip()
    refs = {p.name for p in refdir.glob('*.md') if p.name != RESERVADO}
    faltando = sorted(refs - blocos.keys())
    orfaos = sorted(blocos.keys() - refs)
    corpo = '\n\n'.join(f'### {k}\n{v}' for k, v in sorted(blocos.items()) if k in refs)
    idx.write_text(CAB + '\n' + corpo + '\n', encoding='utf-8')
    print(f'references/indice.md com {len([k for k in blocos if k in refs])} entradas')
    for k in faltando:
        print('SEM RESUMO:', k)
    for k in orfaos:
        print('RESUMO SEM PECA (descartado):', k)

if __name__ == '__main__':
    main()
