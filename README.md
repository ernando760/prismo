# Prismo

Versão experimental: `v0.1.0-alpha.1`.

Agent Skill experimental para criar e evoluir Design Systems Web, Flutter e
Marketing no Codex. Uma única Skill, com referências sob demanda e helpers Python
baseados na biblioteca padrão, sem orquestradores ou múltiplos agentes.

## Operações disponíveis

| Operação | Escopo e referência |
| --- | --- |
| `init` | Investiga e propõe decisões/caminhos; o helper materializa somente o plano aprovado. [Guia](skills/prismo/references/init.md) |
| `foundations` | Colors, Typography, Spacing, Borders e Elevation, com cálculos determinísticos e prévias DTCG. [Colors](skills/prismo/references/colors.md), [Typography](skills/prismo/references/typography.md), [Spacing](skills/prismo/references/spacing.md), [Borders](skills/prismo/references/borders.md), [Elevation](skills/prismo/references/elevation.md) |
| `tokens` | Validação parcial DTCG, prévia de alterações, aliases, dependentes e busca de impacto. [Guia](skills/prismo/references/tokens.md) |
| `create` | Fluxo guiado de componentes Web/Flutter: investigar, projetar, aprovar, implementar, inspecionar e validar. O helper revisa o plano. [Guia](skills/prismo/references/create.md) |
| `document` | Fluxo guiado de documentação no Docusaurus, com inventário, templates e reutilização das fontes existentes. [Guia](skills/prismo/references/document.md) |
| `audit` | Auditoria somente leitura: achados comprovados, riscos e verificações manuais separados. [Guia](skills/prismo/references/audit.md) |

A [visualização de fundações no Storybook](skills/prismo/references/storybook.md)
é um recurso de foundations, sem operação adicional. As
[decisões técnicas](skills/prismo/references/standards.md) orientam a adoção das
ferramentas conforme a plataforma e a necessidade do projeto.

A Skill preserva arquitetura e decisões existentes. Mudanças no consumidor exigem
proposta/diff e aprovação explícita. Ferramentas de documentação e catálogo não são
instaladas automaticamente. `proposal_ready` e previews dos helpers são evidências
de planejamento; validações só podem ser declaradas após execução.

```text
skills/prismo/
├── SKILL.md       # Entrada com as seis operações
├── references/    # Guias carregados conforme a operação
├── scripts/       # Helpers e cálculos determinísticos
└── assets/        # Modelos de plano e templates de apresentação
scripts/install.sh # Instalação local da Skill
scripts/test_suite.py
tests/            # Regressões e registros históricos de validação
```

## Instalação local

Ambiente suportado nesta etapa: Linux, Codex com suporte a Agent Skills, Bash e
utilitários Unix (`cp`, `mv`, `ln`, `mkdir`, `rm`, `rmdir`, `cat`, `dirname`,
`mktemp`, `realpath -m`, como no GNU coreutils). macOS/Windows não foram validados.
Helpers exigem Python 3.9+ e somente a biblioteca padrão; o mínimo declarado não
foi exercitado nesta preparação, que usou Python 3.14.7. Não há pacotes Python
terceiros para instalar no consumidor.

Node, gerenciador de pacotes, SDK Flutter/Dart e ferramentas de catálogo/portal
são necessários conforme a operação e a plataforma. Reutilize versões compatíveis
já adotadas pelo consumidor; não instale todas como requisito da Skill.

O projeto consumidor deve existir. A partir deste repositório:

```bash
# Desenvolvimento: alterações na origem aparecem imediatamente no consumidor.
bash scripts/install.sh --mode symlink /caminho/para/poc

# Alternativa: cópia independente, sem vínculo com a origem.
bash scripts/install.sh --mode copy /caminho/para/outro-projeto
```

O destino é sempre `PROJETO/.agents/skills/prismo/`. Caminhos relativos são
resolvidos a partir do diretório de execução; use aspas se houver espaços.
O script pode ser chamado pelo caminho absoluto de qualquer diretório.
No modo symlink, mantenha o repositório Prismo no mesmo caminho.

Esse local e o formato `SKILL.md` seguem a
[documentação oficial do Codex sobre skills](https://developers.openai.com/codex/skills/)
e o padrão [Agent Skills](https://agentskills.io/specification).

## Atualização e proteção de arquivos

```bash
# Atualizar uma cópia após alterar ou atualizar este repositório.
bash scripts/install.sh --mode copy --update /caminho/para/poc

# Também permite trocar uma cópia reconhecida para symlink (ou o inverso).
bash scripts/install.sh --mode symlink --update /caminho/para/poc
```

Sem `--update`, qualquer destino existente é recusado, inclusive links quebrados.
Com `--update`, apenas cópias com o marcador `.prismo-install` ou symlinks que
apontam para esta origem são substituídos. Arquivos, diretórios desconhecidos e
links para outras origens são preservados. O marcador identifica a instalação;
não é uma assinatura de autenticidade.

A atualização substitui a instalação inteira, sem mesclar alterações locais.
A versão anterior permanece em `PROJETO/.agents/.prismo-backup.XXXXXX/prismo`,
fora da pasta de descoberta de skills; o caminho é impresso ao concluir.
Revise os backups e remova-os manualmente quando não forem mais necessários.
Para restaurar, remova ou mova a instalação atual e mova o item `prismo` do backup
para `.agents/skills/prismo`. Um backup de symlink preserva o link, não uma cópia
do conteúdo histórico da origem.

O instalador recusa pais `.agents` e `skills` que sejam symlinks, evita sobreposição
com a origem e usa staging e lock para impedir duas execuções simultâneas no mesmo
projeto. Se a publicação falhar após mover a instalação antiga, tenta restaurá-la.
Após uma interrupção abrupta, verifique processos ativos antes de remover um lock
residual em `.agents/.prismo-install.lock`. Não execute simultaneamente outras
ferramentas que alterem esses caminhos.

## Uso

Abra o projeto consumidor no Codex e invoque explicitamente a Skill. Se a instalação
não aparecer, reinicie a sessão. Exemplos:

```text
$prismo init
$prismo foundations elevation
$prismo tokens validar as fontes existentes
$prismo create NomeDoComponente
$prismo document as fundações
$prismo audit o pacote Web
```

Os nomes das operações são argumentos textuais, não comandos slash registrados.
A seleção automática não foi comprovada em sessão nova; prefira invocação explícita.
O agente deve consultar as decisões aprovadas e esclarecer somente lacunas reais.

Sem convenções anteriores, `init` sugere `design-system/decisions.json` e
`design-system/tokens.json`. O arquivo novo de tokens começa como `{}`. Raízes de
componentes são registradas sem criar pastas vazias; diretórios surgem quando há
arquivos aprovados. Tokens e organização existentes são reutilizados.

Caminhos de decisões, fontes, pacotes e catálogos são configuráveis, sem mover
projetos. Veja o [contrato de caminhos](skills/prismo/references/project-path-contract.md).
Os helpers aceitam `--help`; use `--decisions` quando o registro não estiver no
caminho padrão e `--package-dir` nos helpers que oferecem seleção de pacote.

As prévias das fundações e de tokens são resumidas por padrão; `--full` inclui o
documento completo. Os helpers de foundations/tokens/create/document/audit não
persistem mudanças de design. `init --apply` cria arquivos somente após aprovação.
O agente persiste os demais diffs aprovados e executa as verificações pertinentes.

## Desenvolvimento e validação

Use Python 3.9+, Node >=22.14.0 e npm >=10; ambiente exercitado: Python 3.14.7,
Node 22.14.0 e npm 10.9.2 em Linux. As seis dependências de desenvolvimento estão
fixadas em `package.json` e suas transitivas em `package-lock.json` (v3).
Use `npm ci` para instalar a árvore do lock sem atualizá-la. A instalação precisa
de acesso ao registro npm ou de cache completo, suporte ao binário esbuild da
plataforma e permissão para subprocessos/lifecycle. Não rode npm na Skill instalada.

A suíte obrigatória inclui testes Python, smoke de distribuição, catálogo DOM,
adaptadores HTML/React e templates MDX/SSR. Retorna falha se testes obrigatórios
forem ignorados ou bloqueados. O smoke usa TypeScript/esbuild declarados, empacota
e instala uma biblioteca sintética em temporário e testa consumo público; não
publica pacotes. Ele cobre ESM, sem prometer distribuição CJS. Não exige dependências
npm no consumidor da Skill. Veja `scripts/test_suite.py` e `tests/test_distribution.py`.

```bash
npm ci
npm test
npm run test:distribution
bash -n scripts/install.sh
python3 -m unittest discover -s tests -p test_install.py -v
```

Para reutilizar instalações existentes, os testes visuais aceitam
`PRISMO_JSDOM_PATH`, `PRISMO_STORYBOOK_TEST_PACKAGE`,
`PRISMO_DOCUMENT_TEST_PACKAGE` e `PRISMO_DISTRIBUTION_TEST_PACKAGE` (manifesto do
ambiente com TypeScript/esbuild). Isso não comprova instalação limpa das dependências.
O smoke não acessa a rede: `npm pack`/instalação do tarball usam `--offline` e cache
temporário; as ferramentas de teste precisam estar previamente instaladas.

O build completo do portal (`tests/document/build-portal.mjs`) é uma verificação
adicional com Docusaurus/preset-classic já disponíveis; não faz parte de `npm test`.
O validador estrutural `quick_validate.py` pertence à skill `skill-creator` do
ambiente de desenvolvimento e requer PyYAML; também não é dependência do consumidor.

A verificação complementar de 2026-11-04 aprovou a instalação limpa padrão,
com lifecycle do esbuild, e a suíte em sandbox Linux com Node 24.22.1/npm 11.19.1.
Os bloqueios locais anteriores (DNS e spawnSync EPERM) foram diagnosticados como
restrições do ambiente. Resultados e logs estão preservados no checklist abaixo.
Os resultados em `tests/*-results.md` e `docs/*-checklist.md` são registros históricos,
com limites da execução original. O
[checklist desta preparação](docs/experimental-release-checklist.md) registra a
validação atual e eventuais bloqueios.

## Limites de uso experimental

- Uso acompanhado: decisões/diffs precisam de aprovação. A execução conversacional
  completa e a descoberta automática em sessão nova ainda não foram comprovadas.
- `create` revisa cobertura declarada; `distribution` é opcional para planos legados.
  O agente deve validar cada pacote real conforme o [guia Web](skills/prismo/references/create-web.md).
  O smoke da suíte é sintético e não certifica pacotes dos POCs ou outros consumidores.
- DTCG parcial: sRGB, px/rem e aliases exatos; sem suporte geral a `$ref`, `$extends`,
  JSON Pointer ou todos os recursos do formato. Consulte [tokens](skills/prismo/references/tokens.md).
  Fontes divididas exigem conjunto/contexto correto; reuso legado ambíguo exige escolha.
- `audit` e busca de impacto são textuais, limitados e sujeitos a falsos positivos/
  negativos. `--exclude` recebe caminhos literais, não globs; formatos não suportados
  e evidências ausentes permanecem pendentes. Consulte [audit](skills/prismo/references/audit.md).
- DOM simulado, cálculos e builds não comprovam inspeção visual, responsividade,
  desempenho ou WCAG completa. Browser, leitor de tela e dispositivo continuam
  necessários conforme a mudança; os testes da suíte não os substituem.
- Flutter/Widgetbook têm fluxo e fixtures de revisão, sem validação integral de
  componentes gerados em SDK/device nesta preparação. Projeções de sombras não
  garantem equivalência CSS/Flutter; inset bloqueia BoxShadow. Elevation aceita
  semânticos simples, pontuados e aninhados, com alvos existentes ou já emitidos.
- Renderers de fundações HTML/React e templates Docusaurus estão disponíveis;
  outros renderers exigem adaptação. Cópias de módulos de apresentação entre
  aplicações podem divergir; não há sincronização ou migração automática.
- Marketing participa do escopo de decisões, fundações e documentação; não possui
  gerador de componentes próprio. `create` implementa Web ou Flutter.

Consulte as [notas preparatórias da primeira release experimental](docs/experimental-release-notes.md)
para capacidades, cenários ainda não comprovados e condições de liberação.
Consulte o [CHANGELOG](CHANGELOG.md) para o histórico das versões.
