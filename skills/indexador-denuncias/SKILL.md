---
name: "indexador-denuncias"
description: "Indexa uma pasta de denúncias em .docx, convertendo cada peça para .md em references/ e gerando indice.md com resumo padronizado de cada uma, para disclosure progressivo."
---

# Indexador de denúncias

Transforma uma pasta com peças de denúncia (.docx) em um acervo de consulta progressiva:

```
<pasta>/
├── indice.md          ← resumos curtos de todas as peças (lido primeiro)
├── references/
│   ├── <nome da peça 1>.md
│   └── <nome da peça 2>.md
└── (os .docx originais, intactos)
```

Quem consultar o acervo (o próprio Claude, outra skill, um projeto) lê só o `indice.md`, escolhe as peças pertinentes e abre apenas os `.md` correspondentes em `references/`.

## Regras gerais

- Nunca alterar, mover ou apagar os .docx originais.
- Cada `.md` tem exatamente o mesmo nome do `.docx` (só troca a extensão), inclusive espaços duplos e acentos. Não "limpar" nomes.
- Trabalhar na própria máquina do usuário (Cowork): usar `device_bash` sobre a pasta montada em `$HOME/mnt/<pasta>`. Não fazer stage dos .docx para a nuvem. Só se `device_bash` não existir, fazer stage e rodar na nuvem, devolvendo os resultados com `device_commit_files`.
- Scripts e arquivos temporários ficam em `$HOME/.indexador/` (fora de `mnt/`, invisível ao usuário), nunca na pasta do usuário.

## Passo 1. Localizar a pasta

1. O usuário indica a pasta. Se ela não estiver conectada, pedir acesso com `device_request_folder_access` (caminho absoluto, motivo curto).
2. Listar o conteúdo e confirmar: quantidade de .docx, existência prévia de `indice.md` e `references/`.
3. Se `indice.md` já existir, operar em **modo incremental** (só peças novas ou alteradas), salvo pedido expresso de refazer tudo (usar `--force` na conversão e apagar as entradas antigas do índice se o usuário autorizar).

## Passo 2. Instalar os scripts

Verificar `which python3`. Gravar os dois scripts abaixo em `$HOME/.indexador/` via heredoc (`cat > ... <<'EOF'`). Só usam a biblioteca padrão do Python.

### docx2md.py

```python
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
```

### montar_indice.py

```python
#!/usr/bin/env python3
"""Monta/atualiza indice.md a partir das entradas redigidas.
Uso: python3 montar_indice.py <pasta_destino> <pasta_entradas>
Cada entrada: <pasta_entradas>/<nome do arquivo sem extensao>.txt com o resumo.
"""
import re, sys
from pathlib import Path

CAB = ('# Índice das denúncias\n\n'
       'Cada peça está integralmente em `references/<mesmo nome do arquivo>.md`. '
       'Leia aqui os resumos e abra apenas as peças pertinentes.\n')

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    dest, ent = Path(sys.argv[1]), Path(sys.argv[2])
    idx = dest / 'indice.md'
    blocos = {}
    if idx.exists():
        for m in re.finditer(r'^### (.+?)\n(.*?)(?=^### |\Z)', idx.read_text(encoding='utf-8'), re.M | re.S):
            blocos[m.group(1).strip()] = m.group(2).strip()
    for f in ent.glob('*.txt'):
        blocos[f.stem + '.docx'] = f.read_text(encoding='utf-8').strip()
    refs = {p.stem + '.docx' for p in (dest / 'references').glob('*.md')}
    faltando = sorted(refs - blocos.keys())
    orfaos = sorted(blocos.keys() - refs)
    corpo = '\n\n'.join(f'### {k}\n{v}' for k, v in sorted(blocos.items()) if k in refs)
    idx.write_text(CAB + '\n' + corpo + '\n', encoding='utf-8')
    print(f'indice.md com {len([k for k in blocos if k in refs])} entradas')
    for k in faltando:
        print('SEM RESUMO:', k)
    for k in orfaos:
        print('RESUMO SEM PECA (descartado):', k)

if __name__ == '__main__':
    main()
```

## Passo 3. Converter

```bash
python3 "$HOME/.indexador/docx2md.py" "$HOME/mnt/<pasta>" "$HOME/mnt/<pasta>/references"
```

Ler o relatório:

- **CONVERTIDO (resumir)**: peças novas ou alteradas; são as que irão para o Passo 4.
- **ERRO**: arquivo corrompido ou não é docx de verdade. Registrar e informar no final.
- **ATENCAO texto muito curto**: provável peça digitalizada como imagem ou vazia. Abrir o .md e conferir; se não houver texto útil, não resumir e informar o usuário.
- **IGNORADO**: .doc/.odt/.rtf/.pdf. Se houver `soffice`/`libreoffice` na máquina, oferecer converter para .docx antes (`soffice --headless --convert-to docx --outdir <tmp> <arquivo>`); senão, apenas listar no relatório final.
- Se o script falhar por ausência de Python, usar `pandoc "<arq>.docx" -t gfm -o "references/<arq>.md"` em laço.

## Passo 4. Redigir os resumos

Para cada arquivo marcado **CONVERTIDO (resumir)** no relatório do Passo 3 (novos ou alterados desde a última rodada), em ordem alfabética, ler a peça (`cat`) e redigir **um parágrafo de 3 a 4 frases**, com esta sequência fixa:

1. **Sujeitos**: "Réu único." / "Ré única." / "Dois indiciados em concurso." / "Casal de indiciados...". Acrescentar a qualificação relevante ao fato, se houver (ex.: "empregada diarista", "mãe da vítima", "comerciante de veículos", indiciado falecido ou foragido).
2. **Conduta nuclear com dados objetivos**: verbo do tipo, objeto, quantidades e pesos de droga, calibre e numeração de arma, valores, número de vítimas, idade da vítima quando relevante, motivação (ciúme, razões da condição do sexo feminino etc.).
3. **Contexto da descoberta e situação prisional**: como o fato veio à tona (patrulhamento, mandado de busca, investigação posterior) e "Prisão em flagrante." ou "Não consta prisão em flagrante." (com o detalhe entre parênteses se a peça indicar, ex.: "notificado para defesa prévia").
4. **Enquadramento final**, sempre começando por uma destas fórmulas:
   - "Crime único: art. X, ..."
   - "Crime único, por duas vezes: ..." / "Crime único, em continuidade delitiva: ..."
   - "Concurso material: art. X e art. Y, na forma do art. 69 do CP."
   - Citar parágrafos, incisos, causas de aumento e o diploma (CP, Lei 11.343/06, Lei 10.826/03, Lei 11.340/06, CTB), exatamente como capitulado na peça.

Estilo: objetivo, factual, sem adjetivação, sem nomes de réus, vítimas ou testemunhas, sem travessões. Não inventar dados ausentes na peça; se algo não constar, omitir ou usar "não consta".

Modelo de entrada:

> Réu único. Transportava, mediante contratação remunerada em drogas, 1040 porções de crack (139,8g) e revólver calibre .32 com numeração suprimida e munição. Abordado em via pública por PM em patrulhamento; não consta prisão em flagrante (notificado para defesa prévia). Concurso material: art. 33, caput, Lei 11.343/06 e art. 16, § 1º, IV, Lei 10.826/03, na forma do art. 69 do CP.

Gravar cada resumo, assim que redigido, em `$HOME/.indexador/entradas/<nome sem extensão>.txt` (heredoc com aspas simples no delimitador). Trabalhar em lotes de cerca de 10 peças, para que nada se perca em coleções grandes. Em coleções acima de 40 peças, é possível distribuir os lotes entre subagentes, passando a eles as regras deste Passo 4 integralmente.

## Passo 5. Montar o índice

```bash
python3 "$HOME/.indexador/montar_indice.py" "$HOME/mnt/<pasta>" "$HOME/.indexador/entradas"
```

O script preserva as entradas já existentes no `indice.md`, substitui as das peças reconvertidas, acrescenta as novas, ordena por nome de arquivo e descarta resumos sem peça correspondente. Formato de cada entrada (idêntico ao modelo):

```
### <nome original>.docx
<parágrafo do resumo>
```

Se o relatório apontar **SEM RESUMO**, voltar ao Passo 4 para esses arquivos e rodar de novo.

## Passo 6. Verificar e reportar

1. Conferir por amostragem 2 ou 3 entradas contra as peças (capitulação e quantidades).
2. Confirmar que o número de `.md` em `references/` bate com o de entradas no índice.
3. Limpar `$HOME/.indexador/entradas/` (fora da pasta do usuário).
4. Responder em poucas linhas: quantas peças indexadas, novas nesta rodada, problemas (erros, peças sem texto, formatos ignorados) e onde estão `indice.md` e `references/`.