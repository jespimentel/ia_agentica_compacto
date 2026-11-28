# Contexto e Objetivo

Preciso da sua ajuda para criar uma **skill** (habilidade) destinada à redação de **Razões de Apelação Criminal** pelo Ministério Público.

A arquitetura da skill deve seguir exatamente o padrão da skill de *contrarrazões* que estou enviando em anexo como referência, contendo a seguinte estrutura de diretórios e arquivos:

* `SKILL.md`: Instruções principais, gatilhos, fluxo de execução e regras de negócio.
* `assets/`: Contendo o arquivo de template estruturado (ex: `template_apelacao.md`).
* `references/`: Contendo exemplos reais de peças prontas (para calibração de estilo, tom e estrutura) e os arquivos de apoio `teses.md` e `julgados.md` para fundamentação jurídica.

# Fluxo de Trabalho da Skill (Como ela deverá operar)

Quando a skill for acionada em uma tarefa futura, ela deverá seguir estas etapas rigorosas:

1. **Análise dos Documentos de Entrada:** O usuário fornecerá peças processuais. A **Sentença** é obrigatória. Opcionalmente, poderão ser fornecidas a **Denúncia**, as **Alegações Finais** do MP e outras peças relevantes (laudos, termos de depoimento, etc.).
2. **Definição do Objetivo Recursal:**
* O modelo deve cruzar o pedido das *Alegações Finais* (ou da *Denúncia*) com o dispositivo da *Sentença* para identificar a sucumbência (ex: absolvição total/parcial, desclassificação, afastamento de qualificadora/causa de aumento, dosimetria da pena).
* **Regra de Interrupção:** Se o objetivo do recurso não estiver claro a partir dos documentos fornecidos (ou se houver múltiplas possibilidades de impugnação sem alegações finais para balizar), o modelo **deve pausar e perguntar** expressamente ao usuário qual é o objetivo pretendido antes de redigir a peça.


3. **Pesquisa e Fundamentação:** O modelo deve consultar os arquivos `references/teses.md` e `references/julgados.md` (seguindo a mesma lógica de busca e aproveitamento aplicada na skill de contrarrazões) para selecionar precedentes e teses compatíveis com a matéria discutida, sem inventar jurisprudência ou extrapolar o conteúdo dos documentos fornecidos.
4. **Consulta à Jurisprudência (STF, STJ e TJSP):** Além dos arquivos locais de referência, o modelo deve consultar jurisprudência do **STF**, do **STJ** e do **TJSP** utilizando exatamente a mesma estratégia aplicada na skill de *contrarrazões* que está sendo enviada em anexo, integrando apenas entendimentos pertinentes e verificados ao caso concreto.
5. **Preenchimento e Redação:** Preencher o template utilizando o estilo das peças de referência, mantendo linguagem jurídica clara, objetiva e técnica.

# Ajustes no Template

O template base está abaixo. Os placeholders foram padronizados para o formato `{{NOME_DO_CAMPO}}` com instruções claras para o modelo, incluindo regras para adaptação dinâmica (como concordância de gênero/número e ajuste do texto da folha de interposição conforme o objetivo do recurso, caso não seja apenas "condenação nos termos da denúncia").

Autos nº {{NUMERO_PROCESSO}}
{{CLASSE_PROCESSUAL}}
{{ASSUNTO_PROCESSUAL}}

O Promotor de Justiça que esta subscreve, com fundamento no artigo 593, inciso I, do Código de Processo Penal, tendo tomado ciência da r. Sentença de fls. {{FOLHAS_SENTENCA}}, vem perante Vossa Excelência interpor o presente RECURSO DE APELAÇÃO, objetivando {{OBJETIVO_INTERPOSICAO_RESUMIDO — Ex: a condenação do(s) apelado(s) nos exatos termos da denúncia / a reforma parcial da sentença para...}}.

Recebido o presente recurso, requer-se seu regular processamento, com vista aos autos à Defesa, para que o contrarie.

P. Deferimento.

Piracicaba, {{DATA_PROTOCOLO}}.

JOSÉ EDUARDO DE SOUZA PIMENTEL
11° Promotor de Justiça de Piracicaba

---

RAZÕES DE APELAÇÃO

Egrégio Tribunal
Colenda Câmara
Douto Procurador de Justiça

Pela r. Sentença de fls. {{FOLHAS_SENTENCA}}, o(a) apelado(a) **{{NOME_APELADO}}** foi {{DISPOSITIVO_SENTENCA — Ex: absolvido(a) da imputação do art. X, com fundamento no art. 386, inciso Y, do CPP}}.

Em que pesem os bons fundamentos do Juízo, busca-se, por este recurso, **{{OBJETIVO_DETALHADO_RECURSO}}**.

Aos fatos.

O(A) apelado(a) respondeu ao processo como incurso(a) no {{TIPIFICACAO_DENUNCIA}}.

{{CORPO_ARGUMENTATIVO — Narrativa fática concisa extraída da denúncia/sentença, seguida da impugnação específica aos fundamentos da sentença, cotejo probatório e inserção das teses/julgados aplicáveis da pasta references}}

Nesse cenário, {{FECHO_ARGUMENTATIVO — Ex: reiterando nossas alegações finais, a condenação era mesmo de rigor / impõe-se a reforma da r. sentença para...}}.

Pelo exposto, aguarda-se o conhecimento e provimento do presente recurso.

Piracicaba, {{DATA_PROTOCOLO}}.

JOSÉ EDUARDO DE SOUZA PIMENTEL
11° Promotor de Justiça de Piracicaba

# Requisitos de Entrega e Revisão Crítica

1. **Análise Prévia Obrigatória:** Antes de gerar os arquivos finais da skill, analise criticamente a skill de *contrarrazões* que estou enviando em anexo em conjunto com estas instruções. Aponte eventuais falhas de lógica, melhorias possíveis no fluxo de trabalho ou pontos que precisam de esclarecimento para que esta nova skill fique ainda mais precisa.
2. **Formato de Entrega (após alinhamento):** Forneça todos os arquivos necessários para a skill (`SKILL.md`, template e eventuais arquivos auxiliares) de forma separada e prontos para download, organizados para que eu apenas os salve nas respectivas pastas locais (`assets/` e `references/`).