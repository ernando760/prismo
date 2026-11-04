# foundations — Spacing

## Investigar e esclarecer

Leia `design-system/decisions.json` ou o caminho documentado pelo projeto, e os
tokens indicados nele. Sem registro, informe a ausência e proponha `init`, sem
inicializar silenciosamente. Preserve Colors, Typography e as decisões anteriores;
carregue apenas esta referência para Spacing, sem recalcular outras fundações.

Busque escalas e usos recorrentes de gap, padding e margin em tokens, CSS/temas,
layout Flutter e componentes representativos. Diferencie uma escala intencional
de valores isolados; registre evidências e nomes existentes. Evite ler dependências
ou o projeto inteiro. Reutilize a fonte de verdade existente, sem migrar tokens
legados automaticamente.

Pergunte apenas o que o projeto/conversa não resolver, em grupos objetivos:

- Escala: base/unidade, progressão linear ou personalizada, passos necessários e
  usos observados. A base 4px é uma opção, não decisão automática.
- Arredondamento: incremento e modo; confirme se pequenas diferenças ou redução
  para zero são aceitáveis. Justifique valores propostos com padrões do projeto.
- Usos/plataformas: mapeamento gap/padding/margin, densidade e restrições existentes;
  para rem, raiz explícita de referência para converter em pixels lógicos Flutter.
Não repita respostas dadas nem invente parâmetros para completar um plano.

## Calcular em preview

Use Python 3.9+, biblioteca padrão, `scripts/spacing.py` relativo à pasta da skill.
Todos os campos do plano são explícitos. Exemplo matemático, não proposta aprovada:

```json
{
  "base": {"value": 4, "unit": "px"},
  "progression": {"type": "linear", "start": 0, "increment": 1},
  "rounding": {"mode": "half_up", "increment": 1},
  "root_px": null,
  "steps": {"none": 0, "sm": 2, "md": 3, "lg": 4, "xl": 6},
  "semantics": {
    "gap": {"compact": "{primitive.spacing.sm}"},
    "padding": {"container": "{primitive.spacing.lg}"},
    "margin": {"section": "{primitive.spacing.xl}"}
  }
}
```

Linear: `base × (start + increment × índice)`. Índices são inteiros não negativos;
start é não negativo e increment positivo. Para personalizar, use
`"progression": {"type": "custom"}`: cada passo passa a ser um multiplicador
explícito da base, inclusive fracionário. Exemplo: base 4px com multiplicadores
0, 0.5, 1.5, 2, 5 gera 0, 2, 6, 8, 20px. Não é uma escala geométrica.

Arredondar para múltiplos do incremento na unidade da base: `half_up` escolhe o
mais próximo, com empates para cima; `floor` para baixo; `ceil` para cima. Usa
aritmética Decimal com contexto de 40 dígitos e imprime valores finitos. Zero é
válido; passos que coincidem após arredondar usam aliases, sem repetir literais.
O preview mostra valor bruto e final para revisar perdas de detalhe.

```bash
python3 /caminho/da/skill/scripts/spacing.py --plan /tmp/spacing-plan.json
python3 /caminho/da/skill/scripts/spacing.py --plan /tmp/spacing-plan.json --existing /projeto/tokens.json
```

Guarde o plano fora do consumidor até aprovação. A saída é somente stdout e o
helper não altera arquivos. Exit 0 significa cálculo e validação do subconjunto
suportado; erros retornam 1 sem preview parcial. Não comprova layout ou aprovação.

## Tokens, reuso e plataformas

Novos tokens usam `$type: dimension` e `{value, unit}` em `px` ou `rem`:
`primitive.spacing.<passo>` e aliases em
`semantic.spacing.<gap|padding|margin>.<papel>`. Não há tipo DTCG chamado spacing.
Os nomes existentes prevalecem: os passos também podem ser aliases `{caminho}`
para dimensões existentes; estas são reutilizadas sem arredondar ou converter.
`steps: {}` permite mapear usos diretamente para a escala existente, sem outra escala.
Semânticos exigem aliases, pelo menos um papel explícito e nenhuma dimensão literal.

O helper preserva o documento passado em `--existing`, incluindo metadados e
outras fundações. Nomes existentes com dimensões resolvidas iguais são preservados;
colisões, aliases ausentes/circulares e tipos incompatíveis são recusados.
Reuso automático de dimensões iguais limita-se a `primitive.spacing` e fontes
explicitamente indicadas pelos aliases de passos: um tamanho de fonte igual não
cria uma dependência silenciosa entre Spacing e Typography. Unidades diferentes
não são tratadas como valores iguais. Revise também as dependências dos aliases.

A saída resumida contém `token_changes`, `scale`, `usages` e `reused`;
`--full` inclui também o documento completo em `tokens`. Cada dimensão tem projeção
CSS e Flutter. Em Web, px é unidade de comprimento CSS;
a projeção Flutter usa o mesmo número em pixels lógicos, sem multiplicar por
DPR. Rem exige `root_px` explícito: `valor exportado × raiz` fornece a projeção,
sem impor tamanho de raiz ao navegador. A raiz real pode variar com preferências.
Alias rem existente também exige essa referência. `dp`, `sp`, `%`, `auto` e `calc()`
não são unidades/valores exportados por este helper.

A escala é não negativa para os usos compartilhados Web/Flutter; margem CSS
negativa exige decisão contextual separada e não é gerada aqui. As projeções são
valores numéricos/CSS, não componentes, CSS compilado ou código Dart. Em Flutter,
mapear espaçamento a constraints, gaps e EdgeInsets conforme o layout; considerar
EdgeInsetsDirectional quando houver direção de leitura. Não presumir que números
iguais garantem o mesmo layout ou que espaçamento equivale ao tamanho de alvo.

Resolve aliases `{caminho}` e tipos herdados; não resolve `$extends`/JSON Pointer.
Tokens legados precisam de mapeamento revisado em cópia temporária. Para múltiplos
arquivos, não grave o documento combinado por cima de um arquivo parcial.
Validação limita-se às dimensões/aliases emitidos ou reutilizados; não é um
validador DTCG completo nem teste de acessibilidade/reflow.

## Aprovar, persistir e verificar

Apresente base, unidade, progressão e justificativas, regras de arredondamento,
tabela bruto/final, aliases, mapeamento semântico e projeções Web/Flutter. Destaque
valores colapsados pelo arredondamento e pendências de layout. Mostre caminhos e
diff dos tokens e do registro, preservando integralmente as outras fundações.

Após aprovação, grave somente o aprovado e acrescente `foundations.spacing` ao
registro existente, sem substituir `init`, Colors ou Typography. Registre plano,
evidências, justificativas, caminhos, reuso, conversão, arredondamento, verificações
e pendências. Releia os arquivos, resolva aliases e recalcule com o plano aprovado.
Confira o diff e reporte preview versus persistência e cálculos versus layout real.

Fontes: [DTCG Dimension](https://www.designtokens.org/tr/2025.10/format/#dimension)
e [Flutter EdgeInsets](https://api.flutter.dev/flutter/painting/EdgeInsets-class.html).
