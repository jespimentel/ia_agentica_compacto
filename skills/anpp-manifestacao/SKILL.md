---
name: anpp-manifestacao
description: Preenche a manifestação processual e as notificações de ANPP (investigado e vítima) depois que o inquérito já foi analisado e o cabimento já foi decidido pelo Promotor.
---

# Manifestação e notificações de ANPP

Use depois que o Promotor já analisou o inquérito (por exemplo, com a skill analise-processual) e já decidiu pelo cabimento do ANPP. A skill preenche `templates/manifestacao-anpp.md`: manifestação processual, requerimento ao juízo, notificação ao investigado e orientações à vítima.

## Premissas

- O cabimento já foi decidido pelo Promotor. Não reavalie, não condicione o preenchimento a isso e não pergunte sobre isso. Consulte `references/cabimento-anpp.md` apenas para: (a) calcular a pena mínima usada no serviço comunitário, (b) conferir as condições do art. 28-A, (c) se o Promotor pedir conferência de cabimento.
- Entregue o resultado no chat. Só gere arquivo (docx, pdf) se o Promotor pedir expressamente.
- Não altere o texto fixo do template (endereço da Promotoria, e-mail, telefones, orientações sobre a Defensoria, fluxo CAOCrim, assinatura). Altere apenas os campos variáveis e os trechos condicionais descritos abaixo.
- Não invente fatos, nomes, valores, datas nem folhas. O que não constar dos autos fica como `[PREENCHER: ...]` e entra na lista de pendências.
- Sem travessões no texto, salvo se indispensáveis.

## Fluxo

1. **Reunir os dados dos autos.** Use o relatório da analise-processual, se estiver no contexto, ou os autos (PDF, TXT ou MD) fornecidos. Se não houver nenhum dos dois, peça. Extraia: número do processo, assunto, classe, vara; fatos, data, hora e local; investigado(s) e folhas da qualificação; vítima(s) e representantes; testemunhas e folhas; tipificação; pena mínima cominada; existência de fiança; endereços, CEPs e celulares dos destinatários.
2. **Perguntar só o essencial.** Data e horário da audiência: se o Promotor não informar, deixe `[PREENCHER: data e horário]` e não trave o trabalho. Não faça outras perguntas que possam virar pendência.
3. **Redigir o preâmbulo** conforme as regras abaixo.
4. **Adequar o template** conforme a seção "Adequação do template".
5. **Entregar** o texto completo no chat e, ao final, uma lista curta de pendências e conferências.

## Regras do preâmbulo

O trecho de "Noticiam os autos que" até "São testemunhas" deve ter a redação das denúncias do Promotor, para ser aproveitado sem alteração na peça acusatória, se houver denúncia. Veja os exemplos em `references/exemplos-preambulo.md` e siga a estrutura, a ordem das informações e o tom, sem copiar conteúdo.

**Estilo geral**
- Terceira pessoa, linguagem impessoal e objetiva, sem adjetivos, sem juízo de valor e sem opinião do Promotor.
- **Tempo verbal: pretérito perfeito do indicativo em toda a narrativa, afirmando a conduta** ("obteve", "portou", "subtraiu", "compareceu", "apresentou"). Não use "teria" nem outras formas do futuro do pretérito, mesmo sem flagrante ou confissão. O texto deve poder ser usado na denúncia sem correção de tempo verbal.
- Narrar só o que os autos mostram, sem especular sobre motivação. Se os autos forem conflitantes ou duvidosos sobre algum fato, escolha a versão mais bem documentada, redija de forma afirmativa e registre a dúvida na lista de pendências, e não no corpo do texto.
- Datas por extenso ("14 de outubro de 2026"). Horário com "por volta das", no formato dos exemplos. Quantidades com numeral e extenso entre parênteses ("6 (seis) peças").
- Folhas sempre no formato "fls. 19/20", "fls. 101 e 212", entre parênteses ou após o nome. Nunca "fls. fls.". Citar apenas folhas que constem dos autos.
- Nome do investigado em CAIXA ALTA na primeira menção e, nas seguintes, pelo prenome em caixa alta.
- Tratar como "indiciado(a)" se houve indiciamento formal nos autos. Caso contrário, "investigado(a)".

**Primeiro parágrafo ("Noticiam os autos que,")**
- Frase única, completando o período iniciado no template, na ordem: data (ou período) e hora; local (logradouro, número, bairro, "nesta cidade e comarca de Piracicaba/SP" ou o município dos autos); NOME DO INVESTIGADO; "qualificado(a) a fls. X" (folha da qualificação); a conduta, com as elementares do tipo; objeto, valor e vítima; folhas das provas materiais (auto de exibição e apreensão, laudo, comprovante fiscal, imagens etc.).
- Descrever objetos com precisão: arma (tipo, calibre, marca, número, munição), mercadorias (itens e valor da avaliação), valores em reais ("aproximadamente R$ 3.500,00" ou o valor apurado).
- Nomear a vítima, inclusive pessoa jurídica, e seus representantes quando houver.

**Segundo parágrafo ("Apurou-se que")**
- Relato cronológico, em parágrafos curtos, uma ideia por parágrafo, em frases diretas. O primeiro parágrafo completa a frase "Apurou-se que"; os seguintes seguem sem repetir a expressão.
- Incluir modus operandi, atos de execução, quem descobriu o fato e como, flagrante ("foi preso em flagrante delito"), declarações do investigado e confissão quando houver, com folhas dos documentos relevantes.
- Não incluir antecedentes, requisitos de cabimento do ANPP nem opinião.

**Enquadramento ("O(s) fato(s) se enquadram no art.")**
- Concordar número: "O fato se enquadra" ou "Os fatos se enquadram".
- Citar artigo, parágrafo, inciso e diploma. Lei especial: "art. 14 da Lei nº 10.826/03". Código Penal: "art. 155, caput, do Código Penal".
- Usar "em tese" quando a tipificação for incerta. Havendo mais de um crime, listar todos, sem concluir sobre concurso.

**Testemunhas ("São testemunhas:")**
- Formato: "Nome Completo (fls. X)". Separar por ponto e vírgula, com "e" antes do último.
- Servidores públicos (policial militar, guarda municipal etc.): indicar a função e "req.", como em "Nome (PM, req., fls. 3)" e "Nome, guarda municipal (req., fls. 2)".
- Representantes da vítima: "representantes da vítima: Nome (fls. X); ...".
- Se os autos não indicarem testemunhas, deixar `[PREENCHER: testemunhas]` e registrar na lista de pendências.

## Adequação do template

- **Cabeçalho:** número, assunto, classe e vara dos autos. Faltando algum, `[PREENCHER]`.
- **Singular e plural, gênero:** adaptar ao caso e remover os parênteses. Um investigado: "o investigado" ou "a investigada", "notificar o investigado", "acompanhado", "advertido", "ciente". Vários: plural. Manter consistência com o preâmbulo. Trocar "averiguado(a)" por "investigado" ou "investigada" (ou "indiciado(a)", se for o termo adotado no preâmbulo).
- **Serviço comunitário:** prazo igual à pena mínima cominada, considerando as causas de aumento e diminuição do caso (art. 28-A, §1º), reduzida de metade. Em concurso de crimes, siga o critério do item A.3 de `references/cabimento-anpp.md`. Expresse o prazo em meses ou anos. Apresente a conta nas pendências, e não no corpo da peça.
- **Reparar o dano:** manter quando houver prejuízo patrimonial. Se não houver dano a reparar (por exemplo, porte de arma sem vítima determinada), omitir a condição.
- **Fiança:** o trecho condicional sobre perda da fiança só entra se os autos indicarem fiança paga.
- **Advertência do art. 28-A, §11:** manter o parágrafo que informa o descumprimento como justificativa para não oferecer suspensão condicional do processo.
- **Vítima:** se houver vítima identificável (pessoa física ou jurídica), manter a seção 5 e o bloco de destinatários da vítima, adaptando singular e plural. Se não houver (crime de perigo, contra a coletividade, sem vítima determinada), omitir a seção 5 e o bloco.
- **Destinatários:** nome, endereço com CEP e celular conforme os autos. Faltando, `[PREENCHER]`.
- **Marcadores:** remover do texto final todo marcador `[CONDICIONAL: ...]` e `[SEÇÃO CONDICIONAL: ...]`. Manter `[PREENCHER: ...]` apenas para pendências reais.
- **Fecho:** manter "Piracicaba, data do protocolo." literalmente, e a assinatura do template.

## Pendências e conferências

Ao final da resposta, em lista curta, informar: campos `[PREENCHER]` que restaram; a conta do prazo de serviço comunitário e a pena mínima usada; testemunhas ausentes; qualquer dado conflitante ou duvidoso nos autos (nome, folhas, data do fato, tipificação). Se não houver pendência, dizer isso em uma linha.
