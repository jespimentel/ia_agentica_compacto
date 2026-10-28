---
name: "indexador-denuncias"
description: "Indexa uma pasta de denúncias em .docx, convertendo cada peça para .md em references/ e gerando references/indice.md com resumo padronizado de cada uma, para disclosure progressivo."
---

# Indexador de denúncias

Transforma uma pasta com peças de denúncia (.docx) em um acervo de consulta progressiva:

```
<pasta>/
├── references/
│   ├── indice.md      ← resumos curtos de todas as peças (lido primeiro)
│   ├── <nome da peça 1>.md
│   └── <nome da peça 2>.md
└── (os .docx originais, intactos)
```

Quem consultar o acervo (o próprio Claude, outra skill, um projeto) lê só o `references/indice.md`, escolhe as peças pertinentes e abre apenas os `.md` correspondentes, na mesma pasta. A pasta `references/` é autocontida e pode ser copiada inteira para outra skill (por exemplo, a skill `denuncia`).

## Regras gerais

- Nunca alterar, mover ou apagar os .docx originais.
- Cada `.md` tem exatamente o mesmo nome do `.docx` (só troca a extensão), inclusive espaços duplos e acentos. Não "limpar" nomes.
- O `indice.md` usa cabeçalhos `### <nome exato do arquivo>.md`, idênticos aos nomes em `references/`. O nome `indice.md` é reservado: um `.docx` chamado "indice" deve ser renomeado.
- Trabalhar na própria máquina do usuário (Cowork): usar `device_bash` sobre a pasta montada em `$HOME/mnt/<pasta>`. Não fazer stage dos .docx para a nuvem. Só se `device_bash` não existir, fazer stage e rodar na nuvem, devolvendo os resultados com `device_commit_files`.
- Scripts e arquivos temporários ficam em `$HOME/.indexador/` (fora de `mnt/`, invisível ao usuário), nunca na pasta do usuário. Os scripts são mantidos em `scripts/` nesta skill; o Passo 2 os instala.

## Passo 1. Localizar a pasta

1. O usuário indica a pasta. Se ela não estiver conectada, pedir acesso com `device_request_folder_access` (caminho absoluto, motivo curto).
2. Listar o conteúdo e confirmar: quantidade de .docx, existência prévia de `references/` e de `references/indice.md`. Se houver um `indice.md` antigo na raiz da pasta (versão anterior da skill), ele não é apagado: o Passo 5 aproveita suas entradas e as converte para o novo formato. Ao final, perguntar ao usuário se quer remover o arquivo antigo.
3. Se `references/indice.md` (ou o `indice.md` antigo da raiz) já existir, operar em **modo incremental** (só peças novas ou alteradas), salvo pedido expresso de refazer tudo (usar `--force` na conversão e apagar as entradas antigas do índice se o usuário autorizar).

## Passo 2. Instalar os scripts

Verificar `which python3`. A skill traz dois scripts em `scripts/` (biblioteca padrão do Python, sem dependências):

- `scripts/docx2md.py`: converte os .docx em .md dentro de `references/`.
- `scripts/montar_indice.py`: monta ou atualiza `references/indice.md` a partir dos resumos.

Como a conversão roda na máquina do usuário, instalar os dois em `$HOME/.indexador/`: se a pasta da skill estiver acessível na máquina, copiar com `cp`; caso contrário, ler cada arquivo de `scripts/` e gravá-lo em `$HOME/.indexador/` por heredoc com delimitador entre aspas simples (`cat > ... <<'EOF'`), sem alterar uma linha. Depois, validar:

```bash
python3 -m py_compile "$HOME/.indexador/docx2md.py" "$HOME/.indexador/montar_indice.py" && echo ok
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

O script grava `references/indice.md` e preserva as entradas já existentes (do índice em `references/` ou, na primeira rodada após a atualização da skill, do `indice.md` antigo da raiz, convertendo os cabeçalhos `.docx` para `.md`), substitui as das peças reconvertidas, acrescenta as novas, ordena por nome de arquivo e descarta resumos sem peça correspondente. O próprio `indice.md` nunca é tratado como peça. Formato de cada entrada (idêntico ao modelo):

```
### <nome original>.md
<parágrafo do resumo>
```

Se o relatório apontar **SEM RESUMO**, voltar ao Passo 4 para esses arquivos e rodar de novo.

## Passo 6. Verificar e reportar

1. Conferir por amostragem 2 ou 3 entradas contra as peças (capitulação e quantidades).
2. Confirmar que o número de `.md` em `references/` (sem contar `indice.md`) bate com o de entradas no índice.
3. Limpar `$HOME/.indexador/entradas/` (fora da pasta do usuário).
4. Responder em poucas linhas: quantas peças indexadas, novas nesta rodada, problemas (erros, peças sem texto, formatos ignorados) e que o índice está em `references/indice.md`. Se o `indice.md` antigo da raiz existir, perguntar se deve ser removido.