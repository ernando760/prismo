---
name: prismo
description: Cria e evolui Design Systems Web, Flutter e Marketing com fundações DTCG, componentes Web/Flutter e visualização no Storybook. Use para init, foundations, tokens, create, document ou audit do Prismo.
metadata:
  version: "0.1.0-alpha.3"
---

# Prismo

Preserve a arquitetura, as convenções e as decisões do projeto consumidor.
Trabalhe com uma única skill, sem múltiplos agentes ou orquestradores.
Carregue somente a referência da operação solicitada e os recursos indicados por ela.
Separe decisões de design de cálculos determinísticos; só declare validações
aprovadas após executá-las. Ao retomar um Design System, consulte primeiro seu
registro de decisões aprovado, no caminho informado pelo projeto ou usuário.
Antes de alterar um consumidor, apresente o diff e aguarde aprovação explícita;
reapresente mudanças materiais. A exceção é `foundations`: o pedido de criação
autoriza a execução automática aditiva conforme seu guia, sem aprovações por
etapa; conflitos e escolhas essenciais ausentes exigem esclarecimento.
`audit` permanece somente leitura.

Se a proposta acrescentar/alterar cores, papéis, estados, mapeamentos ou exceções,
leia [references/colors-coverage.md](references/colors-coverage.md) antes de propor:
valide a matriz incremental dos usos afetados no preview exigido pelo guia.
Consulta legada ou contraste pontual sem nova proposta não exige reconstruir matriz.

## Operações

- `init`: leia [references/init.md](references/init.md). Investigue, esclareça
  lacunas e apresente uma proposta; aguarde aprovação antes de criar arquivos.
- `foundations [nomes]`: leia [references/foundations.md](references/foundations.md).
  Sem nomes, crie as cinco fundações. Com um ou vários nomes, execute somente as
  solicitadas. Interprete também linguagem natural, incluindo exclusões e retomadas;
  esclareça escopo ambíguo sem expandi-lo. A ordem é Colors → Typography →
  Spacing → Borders → Elevation, com recuperação de transação interrompida antes
  das demais etapas. Antes de cada etapa, carregue sua referência
  (`colors.md`, `typography.md`, `spacing.md`, `borders.md` ou `elevation.md`), tokens
  e decisões atuais. Outras fundações ainda estão indisponíveis.
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
