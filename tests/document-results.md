# document — resultados de validação

> Registro histórico da etapa: contagens, bloqueios e pendências abaixo descrevem
> aquela execução. Para o estado de preparação atual, consulte o
> [checklist da release experimental](../docs/experimental-release-checklist.md).

## Implementação

O roteador disponibiliza document; document.md conduz investigação, proposta,
aprovação, redação e validação. A referência Docusaurus é carregada apenas para o
portal. Cobertura: fundações, componentes e identidade; referências aos catálogos,
reutilização de fontes técnicas, lacunas explícitas e setup somente aprovado.

O helper document.py realiza inventário em leitura com biblioteca padrão Python.
Localiza candidatos, versões declaradas, decisões/fonte de tokens, docs existentes,
componentes, catálogos e assets; explicita limites e não interpreta configuração JS,
instala dependências, gera documentação ou representa aprovação.

As referências/scripts/assets das operações anteriores não foram alteradas.
Nenhum arquivo do POC ou outro consumidor foi modificado; nenhum pacote instalado.

## Testes executados

**189 testes aprovados; nenhum ignorado:**

| Suíte | Quantidade | Resultado |
| --- | ---: | --- |
| Python, incluindo 14 novos testes document | 150 | OK |
| Modelos do catálogo DTCG | 13 | OK |
| Renderer DOM | 24 | OK |
| Adaptadores HTML/React | 2 | OK |

Também executados: quick_validate.py (Skill is valid!) e a CLI de inventário no
próprio repositório. Essa CLI identificou corretamente que este repositório contém
a Skill e seus templates, sem portal/decisões de um consumidor; não criou arquivos.

## Fluxos automatizados novos

- Portal com manifest/config é evidência para investigação, nunca aprovação.
- Portal ausente e evidências incompletas (só dependência ou só configuração)
  sinalizam investigação/setup; não executam instalação.
- Múltiplos portais no monorepo sinalizam escolha; seleção por pacote é possível.
- Caminhos customizados de decisões/tokens e docs existentes são inventariados.
- Decisões/tokens ausentes são lacunas explícitas; candidatos não viram fonte aprovada.
- Componentes Web/Flutter, stories/use-cases e assets de marca são candidatos,
  sem inferir URLs publicadas, APIs ou regras de identidade.
- Dependências/build e symlinks são excluídos; busca e apresentação têm limites
  explícitos, sem declarar ausência a partir de inventário parcial.
- Traversal/fontes externas e JSON inválido são recusados.
- CLI preserva todos os bytes dos arquivos temporários, inclusive tokens, decisões
  e documentos das cinco fundações. Configuração JS e scripts de package.json
  contendo comandos de escrita não são executados.
- Erro de entrada retorna 1; inventário retorna 0, sem campo de aprovação concedida.

## Reprodução

```bash
python3 -m unittest discover -s tests -q
python3 /caminho/skill-creator/scripts/quick_validate.py skills/prismo
python3 skills/prismo/scripts/document.py .
node tests/storybook/catalog.test.mjs
PRISMO_JSDOM_PATH=/ambiente/node_modules/jsdom node tests/storybook/render.test.mjs
PRISMO_STORYBOOK_TEST_PACKAGE=/ambiente/package.json node tests/storybook/adapters.test.mjs
```

Nesta execução, os dois testes Node opcionais usaram dependências já disponíveis
em site-easyprocess/frontend (somente leitura), sem instalação. São regressões dos
visualizadores existentes, não teste de um portal Docusaurus novo.

## Limites e pendências

Os novos testes verificam o inventário determinístico e sua ausência de mutações.
Não provam o comportamento conversacional do agente nem qualidade editorial.
Os cenários em document-scenarios.md são roteiros manuais, não execuções aprovadas.

Não foi solicitado documentar um tópico de um consumidor concreto. Não foram
criados portal/páginas nesse consumidor, nem executados build Docusaurus,
verificação de links publicados ou inspeção de páginas no browser. O próximo teste
ponta a ponta depende de selecionar consumidor/tópico, aprovar proposta/diffs e
então produzir e validar a documentação real. O inventário não resolve aliases,
valida DTCG ou interpreta configurações dinâmicas/paths do plugin; esses itens
continuam na investigação orientada pelas referências.
