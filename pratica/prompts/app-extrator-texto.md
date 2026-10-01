Crie, nesta pasta do VS Code, um aplicativo desktop completo em Python e Flet para converter um ou vários arquivos PDF em Markdown. Não se limite a explicar ou apresentar trechos de código: implemente todos os arquivos do projeto, execute os testes possíveis no ambiente e documente o procedimento de uso e empacotamento.

## Objetivo

O aplicativo deve permitir que o usuário:

1. selecione um ou vários arquivos PDF;
2. escolha a pasta de saída;
3. defina o limiar de caracteres utilizado para decidir entre texto nativo e OCR;
4. processe os arquivos localmente;
5. acompanhe o progresso por arquivo e página;
6. consulte um relatório final;
7. cancele o processamento entre páginas.

O aplicativo deverá ser portátil para Windows x64 e poder ser executado a partir de um pendrive. O computador destinatário não poderá depender de Python, uv, Flet ou Tesseract previamente instalados.

Todo o processamento deve ser local. Não utilize LLM, API externa, serviço de OCR remoto, telemetria própria ou envio de documentos pela internet.

## Configuração do limiar

Inclua na interface um campo numérico com o rótulo:

`Limiar de texto nativo (caracteres)`

Requisitos desse campo:

* valor padrão: `600`;
* aceitar somente números inteiros positivos;
* rejeitar valor vazio, zero, número negativo, decimal ou texto;
* exibir uma mensagem clara de validação;
* impedir o início do processamento enquanto o valor for inválido;
* ficar desabilitado durante o processamento;
* utilizar o valor existente no momento em que o usuário iniciar a extração;
* informar no relatório final qual limiar foi utilizado.

A regra exata deve ser:

```python
len(texto_nativo.strip()) >= threshold
```

Não mantenha o antigo valor padrão de 400 caracteres em nenhuma constante, texto da interface, teste ou documentação. O padrão único deverá ser 600.

## Regra de extração por página

A decisão deve ser tomada separadamente para cada página, nunca para o PDF inteiro.

Para cada página:

1. extraia o texto nativo com PyMuPDF;
2. aplique `strip()` para calcular a quantidade de caracteres;
3. se a quantidade for maior ou igual ao limiar selecionado pelo usuário, grave o texto nativo;
4. se a quantidade for inferior ao limiar, renderize somente essa página como imagem RGB, preferencialmente em PNG e 300 DPI;
5. execute o Tesseract local com o idioma português;
6. utilize, salvo justificativa técnica, o modo `--psm 3`;
7. se o Tesseract produzir conteúdo, o texto do OCR deverá substituir o texto nativo curto;
8. se o Tesseract falhar ou retornar vazio, preserve o texto nativo curto que eventualmente exista e acrescente o marcador `OCR PENDENTE`.

Não resuma, corrija, reorganize, complete ou interprete o conteúdo extraído.

## Formato do Markdown

Cada página deverá começar com um marcador de rastreabilidade:

```markdown
<!-- página N | fonte: texto nativo -->
```

ou:

```markdown
<!-- página N | fonte: Tesseract -->
```

ou:

```markdown
<!-- página N | fonte: pendente -->
```

As páginas deverão ser separadas por:

```markdown
---
```

Em caso de falha do OCR, produza:

```markdown
<!-- página N | fonte: pendente -->

Texto nativo curto, se existir.

> **OCR PENDENTE**
```

O Markdown deve preservar a ordem das páginas. Não tente inferir títulos, listas, tabelas ou outras estruturas semânticas que não estejam diretamente presentes no texto extraído.

## Seleção e saída

A interface deve permitir:

* seleção múltipla de PDFs;
* novas seleções sucessivas, sem apagar automaticamente os arquivos anteriores;
* remoção de arquivos da lista, se isso puder ser implementado de forma simples;
* limpeza integral da lista;
* escolha da pasta de saída;
* exibição dos nomes, tamanhos e caminhos dos PDFs selecionados.

Se o usuário não escolher outra pasta, utilize uma subpasta `md` ao lado do primeiro PDF selecionado.

Arquivos apontados pelo usuário podem ser reprocessados. Se já existir um Markdown com o mesmo nome, ele poderá ser substituído, mas a interface deve informar isso claramente.

Se forem selecionados PDFs diferentes com o mesmo nome-base, evite colisões:

```text
processo.md
processo_2.md
processo_3.md
```

## Gravação segura

Grave inicialmente em um arquivo temporário localizado na mesma pasta do arquivo final. Somente depois da conclusão integral do PDF, substitua atomicamente o Markdown definitivo.

Em caso de cancelamento ou erro fatal durante um PDF, não deixe um Markdown parcial com aparência de arquivo completo. PDFs já concluídos anteriormente podem permanecer gravados.

O cancelamento deve ocorrer entre páginas. Se o Tesseract já estiver processando uma página, informe que o cancelamento será efetivado após a página atual.

## Relatório final

Apresente, para cada PDF:

* caminho ou nome do arquivo;
* Markdown gerado;
* limiar utilizado;
* total de páginas;
* quantidade de páginas provenientes de texto nativo;
* quantidade de páginas provenientes do Tesseract;
* números das páginas que permaneceram com `OCR PENDENTE`;
* mensagens técnicas de erro dessas páginas;
* erro fatal do documento, se houver.

Não reproduza conteúdo potencialmente sigiloso no relatório técnico de erros.

## PDFs problemáticos

Trate de modo controlado:

* PDF inexistente;
* arquivo que não seja PDF;
* PDF corrompido;
* PDF protegido por senha;
* página que não possa ser renderizada;
* Tesseract ausente;
* idioma `por` ausente;
* pasta de saída sem permissão de escrita;
* falha de criação ou substituição do Markdown.

Uma falha em um PDF não deve necessariamente interromper os demais arquivos do lote.

## Interface Flet

Crie uma interface clara em português, contendo pelo menos:

* título do aplicativo;
* aviso de que o processamento é integralmente local;
* botão para selecionar PDFs;
* lista dos PDFs selecionados;
* botão para limpar a lista;
* campo da pasta de saída;
* botão para escolher outra pasta;
* campo numérico do limiar, inicializado com `600`;
* explicação breve da regra do limiar;
* botão para iniciar;
* botão para cancelar;
* barra de progresso;
* texto indicando arquivo e página atuais;
* área de relatório;
* botão para abrir a pasta de saída.

Execute o processamento pesado fora da thread da interface, para que a janela não congele.

Durante o processamento, desabilite os controles que não possam ser alterados com segurança, inclusive o campo do limiar.

## Arquitetura sugerida

Separe a interface do motor de extração. Utilize estrutura semelhante a:

```text
extrator_pdf_portatil/
├── main.py
├── pyproject.toml
├── uv.lock
├── README.md
├── extrator_pdf_portatil/
│   ├── __init__.py
│   ├── app.py
│   └── core.py
├── tests/
│   └── test_core.py
├── scripts/
│   ├── preparar_tesseract.ps1
│   ├── build_portable.ps1
│   └── executar_dev.ps1
└── vendor/
    └── tesseract/
```

Você pode melhorar essa estrutura se houver justificativa técnica, mas preserve a separação entre interface, extração e empacotamento.

Utilize dataclasses ou estruturas tipadas para representar:

* progresso;
* resultado de página;
* resultado de documento;
* relatório do lote.

## Dependências

Utilize `uv` para gerenciamento do ambiente e dependências.

Inclua e fixe versões compatíveis de:

* Flet;
* PyMuPDF;
* PyInstaller, quando necessário;
* pytest.

Consulte a documentação oficial correspondente à versão escolhida e não utilize APIs obsoletas do Flet.

Gere e mantenha o `uv.lock`.

## Tesseract portátil

Durante o desenvolvimento, o programa poderá procurar o Tesseract nesta ordem:

1. caminho indicado explicitamente;
2. `runtime\tesseract\tesseract.exe`, quando empacotado;
3. `vendor\tesseract\tesseract.exe`, durante o desenvolvimento;
4. `tesseract.exe` disponível no `PATH`.

Quando utilizar o Tesseract incorporado, configure corretamente o `TESSDATA_PREFIX`.

Antes de processar, execute verificações equivalentes a:

```text
tesseract.exe --version
tesseract.exe --list-langs
```

Não prossiga silenciosamente com outro idioma se `por` estiver ausente.

## Script de preparação do Tesseract

Crie `scripts\preparar_tesseract.ps1` com parâmetro opcional `-Origem`.

O script deve:

* aceitar um caminho fornecido explicitamente;
* procurar automaticamente `tesseract.exe` com `Get-Command`;
* verificar também locais comuns, incluindo:

  * `C:\tesseract-ocr`;
  * `C:\Program Files\Tesseract-OCR`;
  * `%LOCALAPPDATA%\Programs\Tesseract-OCR`;
* validar a existência de `tesseract.exe`;
* validar `tessdata\por.traineddata`;
* copiar o executável, DLLs, configurações e dados necessários para `vendor\tesseract`;
* emitir mensagem clara com a origem encontrada;
* não exigir que o usuário edite manualmente o script.

Evite problemas de caracteres como `nÃ£o` no Windows PowerShell 5.1. Salve scripts PowerShell com codificação compatível, como UTF-8 com BOM, ou utilize mensagens ASCII quando adequado.

## Empacotamento portátil

Crie `scripts\build_portable.ps1`.

O script deve:

1. confirmar que está sendo executado no Windows;
2. verificar a presença de `uv`;
3. verificar `vendor\tesseract\tesseract.exe`;
4. verificar `vendor\tesseract\tessdata\por.traineddata`;
5. sincronizar o ambiente;
6. executar os testes;
7. empacotar o programa em modo `one-folder`;
8. copiar o Tesseract para `runtime\tesseract` dentro do pacote final;
9. criar um arquivo `INICIAR.bat` dentro do pacote compilado;
10. acrescentar instruções de uso;
11. gerar `release\ExtratorPDF-portatil-win64.zip`.

O computador destinatário não deverá precisar de Python, uv, Flet, Tesseract ou privilégios administrativos.

Não deixe um `INICIAR.bat` enganoso na raiz do código-fonte procurando por um executável ainda inexistente. Gere esse arquivo apenas dentro do pacote compilado ou faça com que ele detecte a ausência do executável e mostre instruções de compilação.

## Testes obrigatórios

Crie testes automatizados que não dependam da interface gráfica.

Teste pelo menos:

1. texto com 599 caracteres usando o padrão 600: deve recorrer ao OCR;
2. texto com exatamente 600 caracteres: deve usar texto nativo;
3. texto com 601 caracteres: deve usar texto nativo;
4. limiar personalizado, por exemplo 1000;
5. texto curto substituído por resultado válido do OCR;
6. falha do OCR preservando o texto curto e acrescentando `OCR PENDENTE`;
7. página sem texto e OCR vazio;
8. marcadores e separadores do Markdown;
9. nomes de saída duplicados;
10. gravação atômica;
11. cancelamento entre páginas;
12. validação do limiar;
13. PDF protegido por senha, se for viável criar a amostra no teste.

Use um Tesseract simulado nos testes unitários, para que eles sejam rápidos e independentes da instalação do sistema. Se houver Tesseract disponível, você também poderá executar um teste de integração separado.

## Critérios de aceitação

Considere o projeto concluído apenas quando:

* o valor padrão do limiar for 600 em todo o projeto;
* o usuário puder alterar o limiar pela interface;
* o valor configurado realmente determinar o ramo de extração de cada página;
* o processamento continuar sendo página por página;
* não houver qualquer fallback para LLM;
* o Markdown registrar a fonte de cada página;
* o Tesseract em português puder ser incorporado ao pacote;
* os testes automatizados passarem;
* a interface permanecer responsiva;
* o README explicar desenvolvimento, testes, compilação e execução portátil;
* o pacote final puder ser copiado integralmente para um pendrive.

## Forma de trabalho

Antes de editar:

1. inspecione os arquivos existentes na pasta;
2. apresente um plano curto;
3. preserve alterações úteis que já existirem.

Durante a implementação:

* crie os arquivos diretamente;
* não apenas cole código na conversa;
* execute testes e verificações;
* corrija os erros encontrados;
* não apague arquivos do usuário sem necessidade;
* não instale software do sistema sem autorização.

Ao final, informe:

* arquivos criados ou alterados;
* arquitetura adotada;
* resultado dos testes;
* comando para executar em desenvolvimento;
* comando para preparar o Tesseract;
* comando para gerar o pacote portátil;
* limitações ou verificações que dependam de execução no Windows.