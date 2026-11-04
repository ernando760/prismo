# Nomenclatura de design tokens

A política opcional `decisions.naming` pertence ao registro de decisões aprovado,
sem criar outra fonte de verdade. Sua ausência preserva os caminhos e o comportamento
anteriores. Não infira a política pela aparência dos nomes e não renomeie tokens.

O vocabulário é uma orientação compartilhada, não uma exigência de todos os
segmentos. Primitive descreve valores fundamentais e escalas; Semantic descreve
intenção reutilizável; Component descreve decisão restrita a um componente quando
um papel existente não basta. Um alias pode ligar níveis, mas igualdade de valor ou
alvo não demonstra que dois papéis sejam redundantes.

| Nível | Ordem orientativa | Exemplo com prefixos padrão |
| --- | --- | --- |
| Primitive | categoria/família → escala | `primitive.color.brand.500` |
| Semantic | categoria → propriedade → intenção → estado opcional | `semantic.color.text.primary` |
| Component | componente → variante opcional → propriedade → estado opcional | `component.button.primary.background.hover` |

Categorias sugeridas: `color`, `typography`, `spacing`, `borders`, `elevation`;
propriedades: `text`, `background`, `border`, `radius`, `shadow`; intenções:
`primary`, `secondary`, `action`, `success`, `warning`, `danger`; variantes:
`primary`, `secondary`, `quiet`; estados: `hover`, `pressed`, `focus`, `disabled`.
Nomes de marca, componentes e escalas pertencem ao projeto. Acrescente ou adapte o
vocabulário conforme decisões aprovadas; estrutura e segmentos variam por categoria.
Os caminhos históricos produzidos por cada fundação continuam sendo os padrões de
implementação no modo recomendado; os exemplos acima não exigem migração deles.

Exemplo opcional no plano de init ou em decisões já aprovadas:

```json
{"version": 1, "mode": "custom", "levels": {
  "primitive": {"prefix": "base"},
  "semantic": {"prefix": "role"},
  "component": {"prefix": "widget"}
}, "vocabulary": {"states": ["hover", "pressed", "disabled"]}}
```

`mode` aceita `recommended` ou `custom`; `version` é 1. `levels` e `vocabulary`
são opcionais. Um nível omitido usa seu nome inglês como prefixo; `prefix` pode
ser vazio ou ter segmentos separados por ponto. Prefixos repetidos ou sobrepostos
são ambíguos e recusados. `vocabulary` aceita listas não vazias e sem repetições
em `categories`, `properties`, `intentions`, `variants` e `states`. O vocabulário
é orientação, pois a posição e a intenção não podem ser inferidas universalmente.
Um prefixo vazio não permite classificar automaticamente nomes sem outro prefixo.

Na geração de foundations, o agente prepara aliases e referências dos planos com
os caminhos reais da convenção selecionada. O helper gera novos caminhos com os
prefixos configurados; não reescreve aliases informados nem migra caminhos antigos.
Uma alteração de política durante a retomada, ambiguidade, colisão ou conflito
interrompe a etapa e exige esclarecimento. O checklist registra a política usada.
Conflitos de nomes legados não autorizam sobrescrita. Antes de aprovar mudança de
política ou propor migração, apresente impactos e peça aprovação específica.

Diagnósticos são independentes da validação DTCG: classificação indeterminada é
revisão manual, não erro DTCG. Vocabulário e intenção exigem contexto. Aliases com
mesmo alvo são candidatos para revisão, não redundâncias comprovadas. `document`
usa nomes e significados das fontes e decisões aprovadas; não invente descrições.
