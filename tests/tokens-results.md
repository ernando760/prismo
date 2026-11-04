# tokens — resultados e limitações

## Entrega

- SKILL.md passa a rotear tokens; apenas audit permanece indisponível.
- Referência tokens.md: investigação, proposta de diff/impactos, aprovação,
  persistência pelo agente e validação determinística após a mudança.
- tokens.py: validação e prévia em leitura; usa indexação/validadores existentes,
  acrescenta gestão de mudanças e análise de dependências/ocorrências.
- Modelo de plano sem valores de marca, framework ou namespace obrigatório.
- Primitivos, semânticos e tokens de componentes são tratados pelas convenções do
  consumidor. Nenhuma fundação é recalculada para gerir nomes ou referências.

Os modos validate/preview não escrevem, instalam, executam comandos do projeto ou
obtêm aprovação. A Skill orienta o agente a aplicar somente os diffs aprovados e
executar validate sobre os arquivos efetivamente persistidos. Não há apply/force
ou simulação de autorização por JSON.

## Testes executados

**226 testes aprovados; nenhum ignorado:**

| Suíte | Quantidade |
| --- | ---: |
| Python anterior | 150 |
| Novos testes tokens | 23 |
| Modelos do catálogo DTCG | 13 |
| Renderer DOM | 24 |
| Adaptadores HTML/React | 2 |
| Templates document | 14 |

Também executados: validador estrutural da Skill (Skill is valid!) e validate em
leitura nos **116 tokens reais do POC**, com sucesso no subconjunto suportado.
Nesse POC, valores iguais entre tipografia, spacing e borders foram apresentados
como candidatos, sem mescla automática: igualdade de valor não comprova mesmo papel.

## Fluxos automatizados

- Criação nas três categorias, edição parcial preservando descrição/extensões,
  renomeação e reorganização entre fontes, inclusive caminhos iguais em outro arquivo.
- Tipo herdado preservado em move e aliases de $value reescritos entre arquivos,
  incluindo campos compostos; descrições e metadados não são reescritos.
- Dependentes diretos/transitivos e mudanças de valor resolvido; renomear continua
  tendo impacto mesmo sem alterar o valor dos dependentes.
- Remoção recusada quando deixa aliases pendentes; conjunto explícito de remoções
  validado; sem cascade ou mescla implícitos.
- Referências ausentes, ciclos, tipos incompatíveis, colisões com grupos/tokens,
  chave JSON duplicada e caminho duplicado/ancestral entre fontes detectados.
- Treze tipos conhecidos cobertos em fixtures (incluindo aliases compostos), valores
  inválidos/formatos não suportados recusados. Gradient limita posições no valor
  resolvido conforme DTCG, sem reescrever os valores da fonte.
- Bases com erros de alias/ciclo podem receber proposta de reparo; o resultado precisa
  ser integralmente válido. Comparação resolvida indisponível é null, não uma lista
  que aparente comprovar impacto completo.
- Valores equivalentes sinalizados como candidatos; $root explícito e herança testados.
- Busca encontra caminhos e bindings conhecidos em Web, Flutter e documentação;
  escopos, truncamento e arquivos ignorados são explícitos, sem escrita em consumidores.
- Traversal/symlinks, fonte de destino não fornecida e entradas CLI inválidas recusados.
- Preview CLI preserva todos os bytes da fixture. O teste aplica o candidato somente
  em diretório temporário e executa validate contra os arquivos persistidos; decisões
  e componente/CSS permanecem intactos.
- Cadeia das CLIs reais Colors → Typography → Spacing → Borders → Elevation gerou
  tokens em temporário; acrescentar um token de componente preservou integralmente
  todas as seções anteriores. Nenhum cálculo de fundação foi alterado.

## Reprodução

```bash
python3 -m unittest discover -s tests -q
python3 /caminho/skill-creator/scripts/quick_validate.py skills/prismo
python3 skills/prismo/scripts/tokens.py validate /projeto
python3 skills/prismo/scripts/tokens.py preview /projeto --plan /tmp/tokens-plan.json
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
PRISMO_DOCUMENT_TEST_PACKAGE=/ambiente/package.json node tests/document/render.test.mjs
```

Os testes Node opcionais utilizaram dependências já instaladas em site-easyprocess
(adaptadores/DOM) e prismo-poc (templates document), em leitura; nada foi instalado.
Nenhum arquivo de consumidores/POC foi modificado. Não foi necessário repetir build
de portais/catálogos: seus assets não mudaram, e as regressões executadas passaram.

## Limitações

Não é um validador de conformidade DTCG completo. Há suporte ao subconjunto adotado:
cores sRGB, dimensões px/rem e tipos das fundações, além dos tipos adicionais
explicitamente verificados. Exige $type explícito/herdado; não infere tipo de alias.
JSON Pointer, $ref/$extends, aliases de parada inteira de gradient e outros formatos
de cor precisam do pipeline compatível do projeto. Extensões não têm schema próprio
validado. Nomes iguais em arquivos de temas independentes devem ser validados por
conjunto/contexto, não fornecidos juntos como se fossem uma única fonte composta.

A busca de impacto é textual e limitada, não uma análise de AST/runtime ou de
consumidores externos. Bindings desconhecidos/acessos dinâmicos podem ficar fora;
zero ocorrências nunca comprova impacto zero. Uma base inválida também pode limitar
a análise do estado anterior. Valores equivalentes são apenas candidatos, sem
normalização de unidades nem inferência de finalidade.

O helper não aplica transações, backups ou patches: persistência e eventual restauração
são responsabilidade do fluxo aprovado do agente. Os testes exercitam os mecanismos
determinísticos, não comprovam diálogo/aprovação humana nem uma migração real de
consumidor. Os roteiros de tokens-scenarios.md ainda são avaliação manual pendente.
A próxima validação integrada exige escolher uma mudança concreta, aprovar seu diff
e executar também os checks dos bindings/componentes/docs afetados.
