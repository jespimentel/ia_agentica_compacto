---
marp: true
style: |
  section.columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }
  section.columns h2 {
    grid-column: 1 / -1;
  }

---

# Prompts, Skills e Agentes de IA para a Promotoria de Justiça

## José Eduardo de Souza Pimentel

[GitHub](https://github.com/jespimentel) | [Blog](https://jespimentel.blogspot.com/) | [YouTube](https://www.youtube.com/@jespimentel)

v. 2.0

---

![bg right](img/qrcode.png) 

# Agenda

- Introdução à IA Agêntica
- Engenharia de Prompt
- Agentes Declarativos do Copilot
- Skills e MCP (conectores e plugins)
- Agentes de Execução e Harness
- **Prática de IA Agêntica**
- Dicas e Conclusões

---

# Introdução à IA Agêntica

---

![bg right](img/attention.jpg)

## Evolução dos LLM

- **2017** -> Transformer + _self-attention_ (paralelização massiva)
- **2018 a 2021** -> Escala + modelos de fundação (GPT e Bert) -> Capacidades emergentes
- **2022 a 2023** -> Multimodalidade + expansão da tecnologia
- **2024 ~** -> Raciocínio + Agentes (+ Eficiência)

---

![bg fit](img/agentes.jpg)

---

## Pós-treinamento (Execução de ordens X Planejamento)

**Possibilidades:**
- _Reinforcement Learning_ com instruções humanas para garantir obediência a regras e formatos
- _Reinforcement Learning_ com autonomia e planejamento, para exploração de cenários e tomada de decisão independente (violação do Hugging Face e benchmark _ExploitGym_)

**Abordagem dos modelos de fronteira:**
- **Equilíbrio:** obediência + capacidades avançadas de raciocínio em múltiplos passos

---

<style>
table, th, td { 
  border: none !important; 
  background: transparent !important; 
}
table {
  margin-left: auto !important;
  margin-right: auto !important;
}
</style>

## Probabilístico X Determinístico

| | |
|---|---|
| ![w:450px](img/probabilistico.jpg) | ![w:450px](img/deterministico.jpg) |

---

## O problema do OCR

- len(texto) 
- len (p.images)
- análise de miniaturas
- cruzamento de informações

![bg right fit](img/ocr.jpg)


---

## A janela de contexto

- **Limite em tokens**: cuidado com processos muito longos / recursão
- **Excedente é descartado**: o modelo "esquece" sem avisar
- **Perdido no meio** (_lost in the middle_): o início e o fim recebem mais atenção
- **Degradação** (_context rot_): quanto mais contexto irrelevante, pior a resposta

**Mitigação:** OCR e extração prévios, recorte das peças relevantes, conversa nova por tarefa, síntese em arquivo e skills sob demanda

---

## A petição destinada à IA do juiz

- Síntese na abertura: pedido, fatos e provas (se possível)
- Seções e parágrafos numerados, curtos e monotemáticos (RAG)
- Prova com remissão exata (fls./ID)
- Pedidos numerados e específicos no fecho (repetição)
- Enxuta (talvez seja lida por um humano)
- Sem comandos ocultos (_prompt injection_)
- Conferida pelo Promotor de Justiça (risco de alucinação)

---

## Aviso nº 009/2025-CGMP

- Visão geral sobre a regulamentação do uso da IA no MPSP
- O que devemos **realmente** restringir?

---

![bg right fit](img/trafico-gpt.png)

> **Curiosidade:** em processo sob nossa análise, a ré usou o ChatGPT para gerar o "cardápio" com os tipos de drogas que comercializava

---

# Engenharia de Prompt

---

<!-- _class: columns -->

## Elementos estruturais do prompt

<div>

### Engenharia "tradicional"
- Papel + contexto
- Restrições + tom
- Exemplos (few-shots)
- Insumo factual
- Instrução unívoca
- Formato de saída

</div>

<div>

### Engenharia "agêntica"
- Instruções claras
- Objetivo explícito
- Exemplos (quando necessários)
- Delimitação de seções
- Critérios de sucesso

**(instrução <> dado)**

</div>

---

## Delimitação das seções

**Markdown**

| Marcação | Descrição no Prompt | Exemplo no Prompt |
|----------|--------------------|--------------------|
| `#` | Título | `# Analisador de Inquérito Policial` |
| `##` | Subtítulo (bom para dividir por seções lógicas) | `## Instruções` |
| `**Negrito**` | Destaca termos-chave para o LLM | `**Não inclua opiniões**` |
| `- Item` | Lista não ordenada para enumerar instruções ou requisitos | `- Analise os fatos` |
| `---` | Linha horizontal para separar seções | `---` |

---

**XML**

- Delimita blocos de maneira inequívoca (`<instrucao></instrucao>`; `<contexto></contexto>`), para que o modelo não confunda dados com instruções
- Mitiga a ambiguidade semântica do Markdown em prompts longos
- Previne **prompt injection** 

**Exemplo:**

```xml
<contexto>
Réu preso em flagrante por tráfico de drogas com 500g de cocaína, conforme fls. 12.
Condenado em 1ª instância; defesa apelou (fls. 123).
Razões da apelação a fls. 210/215, com o seguinte conteúdo:
"Pela r. Sentença de fls. 123, o apelante FULANO DE TAL foi condenado ..."
</contexto>
<instrucao>
Liste os pedidos contidos na apelação defensiva fornecida no contexto.
</instrucao>
```
---

**Placeholders**
- Transformam o prompt em template reutilizável (`{{nome_do_réu}}`, `[dia da semana seguinte]`)
- Facilitam a automação com scripts.
- Podem/devem ser usados nos modelos do SAJ-MP

**Exemplo:**

```text
Elabore uma certidão de tempestividade para o recurso interposto por {{NOME_RECORRENTE}},
protocolado em {{DATA_PROTOCOLO}}, considerando o prazo final em {{DATA_LIMITE}}.
```

---

## Técnicas de prompting

| Cenário | Técnica recomendada |
|---|---|
| Tarefa genérica e direta | Zero-shot |
| Saída com formato rígido (petição, ofício, denúncia) | Few-shot |
| Análise jurídica com múltiplos critérios | Critérios claros + exemplos + raciocínio do modelo |
| Cálculo de pena ou prescrição | Ferramenta/código determinístico |

**Chain-of-Thought (CoT)**: se o mecanismo nativo de raciocínio estiver desabilitado

---

# Agentes Declarativos do Copilot

---

## Visão geral do "agente"

**Conhecimento**

> Recuperação probabilística por RAG / RAG Agêntico

- **No prompt**: o que se aplica sempre (regras, template, restrições)
- **No conhecimento**: referência estável, consultada conforme o caso (ex.: catálogo de modelos, manual de regras)
- **Atenção**: RAG recupera contexto; não é memória e não garante a veracidade da resposta

---

## Compartilhamento

**Padronização do trabalho da equipe**

![bg fit right](img/compartilhamento.png)

---

**Copilot Premium**

![Análise de crime tributário](img/copilot-premium.png)

---

# Skills e MCP (conectores e plugins)

---

## Context engineering

> A tendência conceitual mais importante atualmente é a passagem de prompt engineering para context engineering. Em sistemas agênticos, a qualidade não depende apenas da instrução, mas também de quais documentos, exemplos, resultados de busca, ferramentas, memórias, skills e estados devem entrar na janela de contexto. 

- **Skills**: mecanismos de descoberta e carregamento sob demanda, que evitam o contexto excessivo.

---

**Skills**

- Quando usar?
- Tecnologia agnóstica (Padrão aberto)
- O que é?
    - No mínimo: uma pasta com o arquivo SKILL.md
    - _Frontamatter_ (`YAML`) pré-carregado:
        - `name`: nome da Skill
        - `description`: o que faz + gatilho
    - Corpo: instruções de execução
- Regra prática: < 500 linhas

---

**MCP (Model Context Protocol)**

- Quando usar?
    - Para conectar IAs a dados, ferramentas e APIs externas de forma padronizada
- Tecnologia agnóstica (Padrão aberto)
- O que é?
    - Arquitetura Cliente-Servidor via JSON-RPC 2.0 
    - 3 Primitivas principais expostas pelo servidor:
        - `Tools`: Funções executáveis pela IA
        - `Resources`: Dados e arquivos para contexto
        - `Prompts`: Templates de interação reutilizáveis
- Regra prática (não obrigatória): 1 Servidor MCP = 1 Responsabilidade

---

**Exemplo:** ***Progressive Disclosure***

```markdown
elaborar-denuncia/            # sobe como .zip (ou botão "salvar") em Customize > Skills
├── SKILL.md                  # frontmatter (name + description/gatilho) + método
└── references/               # descoberta progressiva (lido sob demanda)
    ├── template.md           # estrutura da peça — lido só ao redigir
    └── exemplos.md           # exemplos de saída — só sem modelo do índice/colado

# Fora da skill (não é empacotado):
Conector Google Drive .......... ligado na UI de conectores (sem arquivo)
Google Drive (externo, via MCP)
└── modelos_denuncias/
    ├── indice.md
    └── *.md                   # modelos de peças
```

---

## Copilot e Skills

![bg fit](img/copilot-skills.jpg)

---

# Agentes de Execução e Harness

---

**Agente de Execução e Harness**

- Quando usar?
    - Para tarefas autônomas que exigem execução de código e controle de estado
- O que é?
    - **Agente**: O modelo (LLM) responsável pelo raciocínio, planejamento e tomada de decisão
    - **Harness**: O ambiente/runtime que envolve o agente para gerenciar a execução
- Regra prática: A IA decide o *quê* fazer; o Harness possibilita a execução do plano

---

## VS Code + Claude Code/Codex/Continue

![VS Code](img/vs-code.jpg)

---

# Prática de IA Agêntica
>[Exemplos](https://github.com/jespimentel/ia_agentica_compacto/tree/main/pratica)


---

# Dicas e Conclusões

---

- Estrutura de prompt com Markdown ou XML não é estética, é semântica
- Em agentes, pense em **Context Engineering**: passe a [arquivar/indexar](https://github.com/jespimentel/ia_agentica_compacto/tree/main/scripts) o trabalho produzido na Promotoria
- Divida tarefas complexas em subtarefas (use outro agente apenas quando a vantagem for evidente)
- Modelo importa, mas harness, ferramentas, contexto, estado e dados determinam a eficiência
- Teste o VS Code com as extensões do Claude, Codex ou Continue
- [Conheça o Python e tenha mais poder](https://jespimentel.github.io/curso_rapido_python/)

---

![bg fit](img/economia-tempo.jpg)

---

**Referências:**

- [ANTHROPIC. Agent Skills (docs)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

- [____. Claude Suport. Como criar habilidades personalizadas](https://support.claude.com/pt/articles/12512198-como-criar-habilidades-personalizadas)

- [____. Repositório público de skills](https://github.com/anthropics/skills)

- [____. The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

- [PIMENTEL, José Eduardo de Souza. A IA Generativa na Promotoria (apostila)](https://github.com/jespimentel/ia_gen_na_promotoria/blob/main/apostila/IA_Gen_Promotoria_Pimentel.pdf)

- [____. Minicurso de Bauru (site)](https://github.com/jespimentel/minicurso_bauru/blob/main/docs/index.md)
