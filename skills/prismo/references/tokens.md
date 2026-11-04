# tokens — gerenciamento DTCG

Consulte [naming.md](naming.md) quando houver convenção de tokens a registrar ou aplicar; preserve decisões e nomes existentes.

## Investigar e propor

Leia instruções locais e decisões aprovadas (normalmente
`design-system/decisions.json`). Localize as fontes DTCG, divisão por arquivos/temas,
agregação, convenções de primitivos/semânticos/componentes e seus bindings CSS/Dart.
Busque uso em componentes, catálogos, documentação e pipelines. Não trate arquivo
gerado como fonte editável nem carregue todas as referências de fundações: consulte
uma delas só se a mudança realmente exigir seus cálculos/decisões.

Esclareça apenas lacunas essenciais: finalidade, nome/papel, escopo/plataforma,
valor aprovado e política de compatibilidade. Não gere uma escala ou token por
suposição. Reutilize aliases para papéis existentes; valores iguais não comprovam
papéis equivalentes. Tokens específicos de componente seguem o namespace local,
sem impor pastas nem abstrações. Não recalcule fundações para renomear um token.

Antes de editar, apresente:

- Operações e arquivos, caminho/tipo/valor/metadata antes e depois, motivo e origem.
- Aliases diretos/transitivos afetados e diferenças de valores resolvidos, inclusive
  em temas e valores compostos. Renomear/mover é mudança de contrato, mesmo que o
  valor resolvido permaneça igual.
- Ocorrências em código, bindings/exportações e docs, com cobertura/limites da busca;
  proposta de migração/depreciação e riscos de nomes usados fora do repositório.
- Candidatos equivalentes e colisões; remoção exige verificar consumidores e aliases,
  sem cascade implícito ou substituição silenciosa de um papel semântico.
- Diffs previstos em consumidores/decisões, se necessários, separados do diff de
  tokens; comandos de validação e pendências.

Aguarde aprovação explícita da proposta antes de persistir. A aprovação deve abranger
aliases reescritos, arquivos e eventuais migrações apresentados. Pedido genérico,
saída válida do script ou aprovação de outra operação não aprovam estes diffs.
Não altere componentes, documentação ou decisões automaticamente: proponha cada
ajuste necessário e obtenha autorização. Sem aprovação de migração obrigatória,
não declare a mudança pronta para consumo; proponha compatibilidade ou adie o break.

## Script determinístico, sem escrita

Python 3.9+, sem pacotes externos. `scripts/tokens.py` reutiliza indexação e
validadores de Spacing, Typography e Elevation; não modifica essas operações.
Ele emite preview/diff e candidatos de impacto, nunca escreve, instala, executa
comandos do projeto ou representa aprovação. Monte o plano fora do consumidor,
conforme o [modelo](../assets/templates/tokens-plan.json):

```bash
python3 /skill/scripts/tokens.py validate /projeto
python3 /skill/scripts/tokens.py preview /projeto --plan /tmp/tokens-plan.json
# Fontes divididas: fornecer TODAS as fontes interdependentes, nunca saídas geradas.
python3 /skill/scripts/tokens.py preview /projeto --source ds/base.json --source ds/semantic.json --plan /tmp/tokens-plan.json --scan src --scan docs
```

Sem `--source`, usa `paths.tokens` das decisões; `--decisions` aceita caminho relativo
customizado. `--source` é repetível. Não agregue persistentemente para usar o helper.
Cada fonte fornecida precisa existir. Temas alternativos que repetem caminhos
devem ser validados por contexto de resolução, junto às fontes comuns apropriadas;
não os misture como arquivos de uma mesma árvore composta. Para introduzir arquivo novo ou mover grupo
inteiro, proponha os diffs com as ferramentas normais; o helper move tokens
individualmente entre fontes já fornecidas. Não expanda `$ref`/`$extends` na fonte
para satisfazer o script: use o pipeline compatível do projeto quando necessário.

`changes` é sequencial; verifica o estado inicial e exige resultado conjunto válido.
Se houver erros iniciais de valores/aliases/tipos, permite propor seu reparo, informa
`baseline_validation` e deixa `resolved_value_changes` como null: comparação resolvida
indisponível, impacto anterior pode ser incompleto e requer revisão manual. Estruturas
ilegíveis, duplicações de caminhos e formatos estruturais não suportados continuam
bloqueando a prévia. Não ignora erros restantes no resultado. Operações:

| op | Campos adicionais | Efeito |
| --- | --- | --- |
| create | file, path, token | Insere token com `$value`, sem sobrescrever grupo/token |
| edit | path, patch | Altera só propriedades `$...` explícitas; mantém demais metadados |
| move | path, file, to | Renomeia/reorganiza token; preserva tipo herdado e atualiza aliases exatos em `$value` de todas as fontes fornecidas |
| remove | path | Remove só o token; grupos/metadata ficam; referências pendentes invalidam o plano |

`bindings` associa caminhos existentes a nomes de código conhecidos, por exemplo
`{"semantic.text": ["--ds-text", "AppTokens.text"]}`. É inventário de busca, não regra
para renomear código. Informe bindings reais; não os deduza automaticamente do nome
DTCG. Por padrão, `changes` mostra o diff sem documentos completos; acrescente
`--full` ao preview para incluir candidatos por fonte em `files`.
`affected_tokens` inclui dependentes transitivos e `consumer_impact` lista ocorrências
textuais com arquivo/linha. Os candidatos não são persistidos pelo helper.
Exit 0: validação/prévia do subconjunto passou; exit 1: entrada/validação falhou.

## Cobertura e limites

Exige tipo explícito ou herdado (não infere tipo de alias sem `$type` efetivo).
Valida tipos efetivos/herdados, aliases inteiros e em campos compostos, alvos ausentes,
ciclos, colisões, duplicação de chaves JSON e de caminhos entre fontes; sinaliza
valores equivalentes sem mesclá-los. Preserva metadados não alterados. Tipos aceitos:
color, dimension, fontFamily, fontWeight, number, typography, shadow, duration,
cubicBezier, strokeStyle, border, transition e gradient.

Segue o formato DTCG adotado nas fundações, sem alegar conformidade completa com
[todo o módulo DTCG 2025.10](https://www.designtokens.org/tr/2025.10/format/).
Limites herdados: cor sRGB explícita (não HEX no `$value`), dimensões px/rem,
alias `{caminho.exato}` (incluindo `$root` explícito), sem JSON Pointer, `$ref`,
`$extends` ou aliases de parada inteira de gradient. Tipografia e sombra seguem os
validadores existentes. Posições de gradient fora de 0–1 são limitadas no valor
resolvido conforme DTCG, sem reescrever a fonte. Tipos/formatos não suportados bloqueiam o plano em vez de
serem ignorados. Metadados comuns são verificados, não todo schema de extensões.

Busca de impacto: texto UTF-8, até 1 MiB/arquivo, 5.000 arquivos e 200 ocorrências;
ignora symlinks, dependências, builds e lockfiles. Relata limites; inclui falsos
positivos e não rastreia AST, acessos dinâmicos, bindings desconhecidos ou consumidores
externos. Zero ocorrências não prova impacto zero. Inspecione geração de bindings,
mapas de caminhos e usos indiretos; aprovação não elimina esse limite.

## Persistir e verificar após aprovação

Reconfira fontes, diff e buscas imediatamente antes da escrita; se mudaram desde a
proposta, recalcule e reapresente o impacto material. Aplique apenas o diff aprovado
com as ferramentas do agente, preservando ordem/estilo local quando viável. Não
substitua decisões ou componentes pela saída JSON. Para múltiplos arquivos, prepare
as mudanças juntas e restaure os originais se uma aplicação/validação falhar; não
deixe fontes parcialmente migradas. Confira também o diff por arquivo, inclusive
grupos e metadados não mostrados no diff de tokens.

Execute `validate` novamente contra os arquivos realmente persistidos, com todas as
fontes, e o pipeline/checks existentes de bindings, testes de componentes, catálogos
e docs afetados conforme o escopo aprovado. Não declare validado sem executar;
relate comando, resultado, cobertura e bloqueios. Se houver regressão, corrija dentro
do escopo autorizado ou reverta e apresente a pendência. Registre decisões apenas
no formato e diff aprovados, preservando as demais seções/fundações.

Quando houver política de nomenclatura registrada, a saída inclui diagnóstico separado da validação DTCG; recomendações não autorizam migração.
