# Colors — contrato de cobertura e evolução

Aplicável a `foundations`, `create`, `tokens`, `document` e `audit`. Reutilize
Colors para os cálculos e os mecanismos existentes de cada operação para propor,
aprovar e persistir. Não crie outra operação ou fonte de verdade.

## Preparar e validar uma proposta nova

Aplique este fluxo ao propor adição/alteração de escala, papel, estado, mapeamento
ou exceção de cor em qualquer operação. Consulta legada e contraste pontual sem
proposta nova não exigem matriz. Ler este guia ou executar cálculos isolados não
substitui validar o plano.

1. Leia seletivamente as decisões pertinentes (paths, naming, Colors e componentes
   afetados). Preserve o histórico; não carregue relatórios completos sem necessidade.
2. Monte `coverage` **somente para os usos afetados**, por tema e horizonte. Não
   reconstrua a matriz inteira nem copie passos antigos para recalculá-los. Inclua
   pares/dependentes relevantes ao impacto; lacunas ficam explícitas. Use IDs
   existentes quando houver. `palettes` e `themes` contêm apenas candidatos/mapeamentos
   necessários; `palettes: {}` e papéis vazios permitem reuso sem novos aliases.
3. Consulte `python3 scripts/colors.py palette --help` para argumentos e contrato
   JSON; adapte o [template](../assets/templates/colors-coverage-plan.json).
   Não invente valores de `usage`: `normal_text`, `large_text`, `non_text`.
4. Execute o preview **antes de apresentar a proposta**:

   ```sh
   python3 scripts/colors.py palette --plan /tmp/colors-plan.json --existing /projeto/tokens.json --require-coverage
   # Sem arquivo temporário: envie o mesmo JSON por stdin com --plan -.
   ```

   Os caminhos dos scripts são relativos à skill instalada. Não chame o executor
   persistente de `foundations` apenas para validar uma proposta. `--require-coverage`
   exige matriz válida e não vazia; não migra registros legados nem grava tokens.
   Para exploração sem pares definidos, use `partial`/`not_evaluated` conforme a
   evidência e `pairs: []` com `coverage` válido; não invente contraste ou inspeção.
5. Confira código de retorno **e stderr antes de interpretar stdout**. Em Python:

   ```python
   result = subprocess.run(command, input=json.dumps(plan), text=True, capture_output=True)
   if result.returncode != 0:
       raise ValueError(result.stderr.strip() or "Preview falhou sem diagnóstico")
   if result.stderr.strip():
       raise ValueError("Revisar diagnóstico antes de consumir JSON: " + result.stderr)
   preview = json.loads(result.stdout)
   ```

   No exemplo, `command` contém `palette --plan - --existing ... --require-coverage`.
   Corrija o campo diagnosticado e revalide o mesmo escopo; não retire temas,
   pares ou cobertura para contornar erros. Funções de baixo nível servem para
   diagnóstico, não comprovam validação do plano. Se bloqueado, apresente pendências
   e não declare a proposta validada.
6. Apresente uma **matriz explícita resumida**: uso/tema, horizonte, situação,
   reuso/extensão/exceção, cálculo, visual e pendências. Informe comando e resultado
   do preview e diff material de tokens/decisões. Não exponha todo JSON nem use
   `--full` por padrão. Antes de entregar, confira que matriz e proposta correspondem
   ao plano efetivamente validado; se o plano mudar, revalide os usos afetados.

Este fluxo prepara a aprovação da operação atual, não a substitui. Em `create` e
`tokens`, aguarde a aprovação explícita dos diffs antes de persistir. Em `foundations`,
preserve a autorização aditiva e as restrições existentes; pedido só de proposta
não autoriza escrita. Matriz incremental de preview não substitui registros ou
checklists completos: apresente integração/merge no diff da operação, preserve usos
não afetados e nunca sobrescreva o histórico pela saída parcial do helper. Migrar
plano legado concluído exige aprovação; journal, lock e retomada permanecem iguais.

## Planejar granularidade

Distinga cobertura `functional` (usos existentes/entrega aprovada) de `evolution`
(roadmap, padrões recorrentes ou decisões explícitas). Cada passo deve ter uso,
motivo e benefício concretos. Necessidades futuras podem ser apenas registradas;
não preencha intervalos, gere estados, aliases ou famílias por especulação. Não
há quantidade fixa de passos; famílias podem ter granularidades diferentes.

Leia `decisions.naming`, convenção e direção existentes. Proponha identificador
livre compatível com a posição do passo, sem renumerar, renomear ou modificar
tokens aprovados. Número não é luminosidade nem garantia de contraste. Se faltar
intervalo/regra compatível, exponha o conflito e proponha extensão da convenção
para aprovação; não invente decimais, sufixos ou namespaces silenciosamente.
`naming_evidence` registra essa revisão contextual: o helper não interpreta a
semântica de toda convenção nem escolhe nomes automaticamente.

## Contrato opcional no plano de Colors

O plano mantém `palettes`, `themes`, `pairs` e aceita `coverage` com exatamente:

- `version`: inteiro `1` (versão do contrato, não da release).
- `uses`: lista de linhas da matriz; não exige produto cartesiano de estados.
- `steps`: justificativas dos passos explicitamente presentes em `palettes`.

Consulte o [exemplo completo](../assets/templates/colors-coverage-plan.json).
Seus valores são ilustrativos, não defaults nem autorização para gerar tokens.

Cada linha de `uses` exige:

| Campo | Contrato |
| --- | --- |
| `id`, `use` | Identificador único e descrição do uso/parte/estado concreto. |
| `theme` | Tema presente em `themes`; não inventar outro tema. |
| `horizon` | `functional` ou `evolution`. |
| `status` | `covered`, `partial`, `deferred` ou `not_evaluated`. |
| `evidence` | Fonte concreta do uso/roadmap/decisão e contexto. |
| `pending` | Lista de pendências relevantes; vazia somente quando apropriado. |
| `tokens` | Caminhos reais relacionados ao uso; aliases são resolvidos até o valor final. |
| `pairs` | Pares `{foreground, background, usage}` presentes em `pairs` do plano e nos tokens desta linha. |
| `visual` | `{status, evidence}`: status `passed`, `failed`, `pending` ou `not_applicable`; evidência contextual obrigatória. |
| `decision` | `reuse`, `extension`, `exception` ou `undecided`. |
| `alternatives` | Busca por equivalentes e justificativa da escolha, inclusive por que reuso/extensão não servem a uma exceção. |
| `review_when` | Condição de retomada/revisão, inclusive para adiamentos e exceções. |

`covered` exige tokens resolvíveis, pares calculados aprovados, decisão definida,
nenhuma pendência relevante e visual aprovado ou não aplicável com justificativa.
`partial` representa investigação/validação incompleta, inclusive cálculo aprovado
com inspeção pendente. `deferred` é adiamento consciente, com motivo e retomada;
`not_evaluated` é ausência de avaliação, incompatível com resultados já calculados
ou inspeção concluída. Usos sem cálculo suportado ficam parciais, com cálculo
externo/limitação descritos; nunca simule aprovação para satisfazer o helper.

Cada item de `steps` exige `token`, `uses` (IDs), `reason` (necessidade/benefício) e
`naming_evidence` (convenção e inserção revisadas). Justifique todos os passos
explicitamente propostos, inclusive os reutilizados numa retomada. O uso vinculado
deve rastrear o passo, ter decisão `extension` e não estar adiado/não avaliado.
Um plano só de reuso usa `palettes: {}` e `steps: []`. Com `coverage`, `pairs: []`
permite registrar planejamento ainda sem pares, sem declarar cobertura concluída;
não provoca geração de passos ou aliases implícitos. Planos legados continuam
aceitos e recebem `unknown_legacy`, sem migração ou defeito automático.

## Evidências separadas e percepção

`calculation` é calculado pelo helper: `passed`, `failed` ou `not_evaluated`.
`visual` é evidência declarada: o helper não abre navegador nem confirma capturas.
`conformance` permanece `not_assessed`: nem cálculo nem relato de inspeção
comprovam conformidade WCAG completa. O agente deve relatar o que inspecionou de
fato; não atribua inspeção ao helper ou declare uso integralmente validado com
pendências relevantes.

`perceptual_review` detalha OKLCH dos valores sRGB finais, deltas de L/C/H,
distância OKLab e igualdade após quantização entre vizinhos na ordem explícita
do plano. Matiz acromático não tem delta significativo (`null`). Reveja a família
existente e a posição de uma inserção, não só os candidatos gerados. Medidas e
ordenação não garantem harmonia nem distinção perceptual; não há limiar universal
de aprovação. Gamut mapping e quantização podem alterar a trajetória pretendida.

Contraste é separado: pares reais, valores finais, temas e estados relevantes.
Não exigir 3:1 entre hover e default. Considerar adjacência do foco e exceções
WCAG. Transparência/composição/gradientes fora da cobertura exigem cálculo externo
apropriado ou pendência. Preserve identidade e seeds oficiais.

## Reuso, extensão e exceção

Reuso → extensão → exceção justificada é uma avaliação de alternativas, não
obrigação de estender inadequadamente. Cores específicas de componente são
permitidas. Igualdade de valor não equivale a igualdade de intenção; novo alias
exige contrato útil. Segundo consumidor motiva revisão, sem promoção automática;
uma extensão necessária não exige dois consumidores. Migrações exigem aprovação
explícita e impacto por arquivos, bindings, temas e dependentes.

## Persistência, consumo e apresentação

A matriz vive em `plan.coverage`, preservada com origens, decisões e validação no
checklist/registro existentes. Em `foundations`, use a mesma transação, lock e
retomada de [foundations.md](foundations.md), sem gravação paralela da matriz.
Concluir o helper é conclusão técnica, não inspeção visual integral. A verificação
final confere cobertura calculada contra o registro persistido. Edição conflitante
ou mudança de plano concluído continua bloqueada: não apague journal/checklist
nem reinicialize para contornar. Evoluções exigem proposta de diff compatível e
aprovação; não torne uma retomada em migração silenciosa.

Em `create`, apresente decisão por uso e novos tokens com a cobertura pertinente
na proposta; aprovação do componente não autoriza tokens omitidos. Em `tokens`,
mostre alterações da matriz/decisões separadas do diff de tokens, impactos e
compatibilidade; não recalcule escalas para renomear. Após mudanças aprovadas,
revalide cobertura e mantenha decisões/checklist coerentes no fluxo da operação.

Em `document`, publique resumo da matriz e exceções com links para evidências;
não regenere escalas. Em `audit`, confronte decisões e usos reais. O helper
recalcula pares registrados sobre fontes fornecidas sem gerar paletas nem escrever;
evidência visual continua declarada, não reinspecionada. Contrato/fontes incompatíveis
geram revisão, não violação automática de interface. Fontes divididas e temas
alternativos exigem contextos explícitos, conforme os limites existentes.

Apresente resumos por padrão, preservando falhas, pendências e impactos materiais.
`colors.py palette --full` expõe matriz completa, cadeias e valores resolvidos,
relações perceptuais e documento candidato. O relatório completo de `foundations`
permanece no checklist/decisões como evidência de retomada. Não copie esse volume
inteiro para a conversa; resuma e ofereça os detalhes quando necessários.
