---
name: prismo
description: Cria e evolui Design Systems Web, Flutter e Marketing com fundações DTCG, componentes Web/Flutter e visualização no Storybook. Use para init, foundations, tokens, create, document ou audit do Prismo.
metadata:
  version: "0.1.0-alpha.1"
---

# Prismo

Preserve a arquitetura, as convenções e as decisões do projeto consumidor.
Trabalhe com uma única skill, sem múltiplos agentes ou orquestradores.
Carregue somente a referência da operação solicitada e os recursos indicados por ela.
Separe decisões de design de cálculos determinísticos; só declare validações
aprovadas após executá-las. Ao retomar um Design System, consulte primeiro seu
registro de decisões aprovado, no caminho informado pelo projeto ou usuário.
Antes de alterar um consumidor, apresente o diff e aguarde aprovação explícita;
reapresente mudanças materiais. `audit` permanece somente leitura.

## Operações

- `init`: leia [references/init.md](references/init.md). Investigue, esclareça
  lacunas e apresente uma proposta; aguarde aprovação antes de criar arquivos.
- `foundations colors`: leia [references/colors.md](references/colors.md).
- `foundations typography`: leia [references/typography.md](references/typography.md).
- `foundations spacing`: leia [references/spacing.md](references/spacing.md).
- `foundations borders`: leia [references/borders.md](references/borders.md).
- `foundations elevation`: leia [references/elevation.md](references/elevation.md).
  Para `foundations` sem assunto, esclareça qual fundação executar antes de carregar
  referências. Outras fundações ainda estão indisponíveis.
- Visualização de fundações no Storybook: leia [references/storybook.md](references/storybook.md).
- `create`: leia [references/create.md](references/create.md). Investigue e apresente
  o fluxo Investigar → Projetar → Aprovar → Implementar → Inspecionar → Validar;
  a referência orienta o carregamento visual e do guia Web ou Flutter.
- `document`: leia [references/document.md](references/document.md). Investigue fontes
  e proponha páginas/diffs antes de modificar; setup do portal exige aprovação.
- `tokens`: leia [references/tokens.md](references/tokens.md). Investigue fontes,
  apresente diff/impactos e aguarde aprovação; valide novamente após persistir.
- `audit`: leia [references/audit.md](references/audit.md). Somente leitura;
  classifique evidências, riscos e verificações manuais sem corrigir o consumidor.

Para consultar as decisões técnicas compartilhadas, leia
[references/standards.md](references/standards.md) quando necessário.
