# Create — resultados de validação

> Registro histórico da etapa: contagens, bloqueios e pendências abaixo descrevem
> aquela execução. Para o estado de preparação atual, consulte o
> [checklist da release experimental](../docs/experimental-release-checklist.md).

## Entrega

- SKILL.md passa a rotear create para uma referência comum pequena.
- create.md conduz investigação, perguntas essenciais, contrato, aprovação,
  implementação e verificação. Guias Web/Flutter são carregados conforme o alvo.
- O helper create.py revisa propostas em leitura, sem gerar código, instalar
  ferramentas, executar comandos ou representar aprovação do usuário.
- O modelo de plano é instalado dentro da skill, sem defaults de framework/API.
- Não foram alteradas as outras operações, helpers ou visualizações existentes.

A anatomia, API, variantes, tamanhos e justificativas são definidos na proposta
legível ao usuário. O helper verifica somente o subconjunto determinístico:
evidências da plataforma, classificação declarada, caminhos, referências/aliases,
uso de novos tokens, cobertura declarada de estados e entregáveis previstos.

## Testes executados

**175 testes aprovados, sem ignorados:**

| Suíte | Quantidade |
| --- | ---: |
| Python existente | 115 |
| Novos fluxos de revisão create | 21 |
| Modelos DTCG do catálogo | 13 |
| Renderer DOM compartilhado | 24 |
| Adaptadores HTML/React | 2 |

Também executados: quick_validate.py (skill válida) e node --check do renderer.
Dependências opcionais dos testes de catálogo vieram do ambiente já disponível,
sem instalação ou alteração de projetos consumidores.

## Fluxos create verificados

| Fluxo | Resultado observado |
| --- | --- |
| Web com React/Storybook identificados | Proposta pronta para revisão, com aprovação ainda exigida |
| Flutter com pubspec e Widgetbook encontrados | Plataforma inferida quando única; ferramenta compatível |
| Web + Flutter sem alvo | Solicitação de escolha, sem duas implementações automáticas |
| Só Web declarado, sem tecnologia | Informação essencial pendente; framework não escolhido |
| Plataforma divergente do registro | Escopo precisa ser esclarecido |
| Catálogo ausente ou incorreto | Setup requer aprovação ou correção; nenhuma instalação |
| Decisões/tokens ausentes | Proposta não considerada pronta |
| Componente/arquivo existente | Criação recusada; alteração exige diff/aprovação específica |
| Tokens/aliases ausentes, cíclicos ou incompatíveis | Pendência explícita, sem correção automática |
| Novo token | Justificativa, binding/uso, arquivo de tokens e aprovação exigidos |
| Token novo sem uso ou em colisão | Revisão exigida, fonte original preservada |
| Estado sem caso, checks a11y ausentes ou artefato não planejado | Proposta pendente |
| Pergunta não respondida/Atomic não definido | Proposta pendente |
| Caminho com traversal, symlink de escrita ou sobreposição | Recusa ou revisão antes de implementação |
| Modelo vazio | Não é tratado como proposta pronta |
| Comando listado no JSON | Não executado pelo helper |

O teste de preservação produziu tokens pelas CLIs reais de Colors, Typography,
Spacing, Borders e Elevation em diretório temporário. A revisão create manteve
os bytes de todos os arquivos, inclusive decisões, e não criou arquivos no projeto.
Saídas da CLI create verificadas: 0 (proposal_ready), 2 (needs_input), 1 (entrada inválida).

## Reprodução

```bash
python3 -m unittest discover -s tests -q
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
```

Os últimos dois testes são opcionais sem dependências disponíveis; nesse ambiente
eles executaram e passaram, não foram contabilizados como ignorados.

## Limites e próximos testes

Não foi solicitado um componente concreto no consumidor. Os testes novos não
executam React/Flutter de um componente gerado, Storybook/Widgetbook novos, auditoria
WCAG ou uma sessão independente do agente. O fluxo de linguagem está documentado
em create-scenarios.md para avaliação manual; os cenários não foram contados como
execuções aprovadas. Os testes dos adaptadores são regressão do catálogo existente.

O helper não comprova que um binding CSS/Dart funciona, que uma asserção descrita
é correta ou que valores DTCG completos são válidos. `proposal_ready` não é
aprovação nem conformidade de componente. O próximo teste ponta a ponta deve usar
um componente e projeto definidos, com proposta/diff aceitos, implementação real,
catálogo, testes funcionais/acessíveis executados e registro dos resultados.

Nenhum arquivo do POC foi alterado nesta entrega.

## Evolução visual — 2026-11-03

- Referência interna visual-design.md carregada condicionalmente por create.md;
  fluxo explícito Investigar → Projetar → Aprovar → Implementar → Inspecionar → Validar.
- SKILL.md permanece com 40 linhas. Scripts, templates, schemas e seis operações
  preservados; nenhum componente criado no POC ou projeto consumidor alterado.
- `npm test`: 213 testes Python aprovados; catálogo JS aprovado. A suíte completa
  retornou 1: 24 testes de renderização Storybook, 2 de adapters e 14 de documentação
  ignorados por dependências de desenvolvimento ausentes. Não são aprovações.
- Tentativa de instalar dependências isoladamente em /tmp: cache incompleto
  (ENOTCACHED) e registro npm inacessível (EAI_AGAIN). Reexecutar `npm test` após
  disponibilizar as dependências de desenvolvimento já declaradas em package.json.
- `quick_validate.py skills/prismo`: Skill is valid!
- Testes novos cobrem contrato documental, carregamento condicional, links locais,
  limite da evidência visual e distribuição da referência pelo instalador.
  Cenários de julgamento visual foram adicionados a create-scenarios.md; continuam
  pendentes de avaliação comportamental em componente aprovado, fora desta etapa.
