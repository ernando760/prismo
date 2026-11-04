# foundations — execução automática e retomada

Consulte [naming.md](naming.md) quando houver convenção de tokens a registrar ou aplicar; preserve decisões e nomes existentes.

## Interpretar o pedido

`$prismo foundations` significa todas as cinco fundações. Um nome mantém a
execução individual; vários nomes selecionam somente esse conjunto. Interprete a
intenção também fora da sintaxe: “crie cores e espaçamento” → Colors e Spacing;
“todas menos elevação” → as primeiras quatro; “só a tipografia” → Typography.
Respeite negações: “cores já estão prontas, crie bordas” não solicita Colors.
“Continue as fundações” retoma `requested` do checklist, sem ampliar um pedido
parcial para todas. “Melhore a base” é ambíguo: pergunte quais fundações/alterações.
Pedidos de explicação/preview não autorizam persistência; use os helpers individuais.

Normalize os nomes/termos usuais (cores/colors, tipografia/typography,
espaçamento/spacing, bordas/borders, sombras/elevação/elevation). A interpretação
é conversacional; o helper recebe nomes canônicos, não tenta adivinhar intenção
por palavras-chave. Não acrescente dependências implícitas. Execute o subconjunto
sempre na ordem Colors (`colors.md`), Typography (`typography.md`), Spacing
(`spacing.md`), Borders (`borders.md`), Elevation (`elevation.md`).

## Preparar e decidir

Localize `decisions.json` no caminho registrado/informado, padrão
`design-system/decisions.json`. Sem ele ou sem fonte inequívoca de tokens, informe
a lacuna e proponha `init`, sem inicializar silenciosamente. O checklist fica ao
lado desse registro: `foundations-plan.json`, dentro do diretório do Design System.
Leia um checklist existente antes de propor planos. Preserve etapas concluídas,
planos salvos, decisões de `init`, tokens e seções das outras operações.

Antes de **cada** etapa, releia sua referência e os tokens/decisões atuais. Consulte `decisions.naming` quando presente e prepare os aliases do plano nos caminhos reais; o helper não os reescreve. Use
as evidências do projeto e as informações já fornecidas na conversa. Reutilize
um `foundations.<nome>.plan` existente; se ele não estiver registrado, investigue
os tokens e registre um plano de reuso, sem criar escalas redundantes. Registros
legados aprovados sem plano precisam de esclarecimento/mapeamento antes de
executar o helper; não substitua o registro para fazê-lo passar.

Precedência: decisões aprovadas e tokens existentes são restrições; pedidos novos
conflitantes exigem esclarecer a alteração, nunca sobrescrever silenciosamente.
Nas lacunas, use instruções do usuário e depois os padrões seguros da referência.
Registre a origem de cada campo do plano em `sources`: `user` (conversa/brief),
`existing` (arquivo/decisão/token) ou `default` (seção da referência), sempre com
`evidence` concreta. Quando um campo agrupar escolhas de várias origens, explicite
essas escolhas na evidência e preserve os valores individuais; não atribua ao
usuário um padrão adotado pela Skill.

Pergunte somente quando faltarem escolhas essenciais (marca, famílias/pesos,
temas/usos sem evidência), houver ambiguidade ou conflito. Agrupe as lacunas da
etapa. O pedido de criação autoriza persistir adições com decisões já fornecidas,
reuso e padrões seguros; não peça aprovação de cada cálculo, preview ou gravação.
Essa regra substitui a aprovação repetida do fluxo anterior de foundations,
inclusive na execução individual. Mudanças destrutivas em decisões/tokens
existentes continuam fora desse fluxo; apresente o conflito e esclareça-o.

## Executar o checklist

Use `scripts/foundations.py` (Python 3.9+, biblioteca padrão, Linux), que chama os
mesmos `build` dos cinco helpers. Não replique cálculos, regras de aliases ou
validação. Prepare um JSON temporário fora do consumidor com as etapas prontas:

```json
{
  "spacing": {
    "plan": {
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
    },
    "sources": {
      "base": {"origin": "default", "evidence": "references/spacing.md: Padrões seguros"},
      "progression": {"origin": "default", "evidence": "references/spacing.md: Padrões seguros"},
      "rounding": {"origin": "default", "evidence": "references/spacing.md: Padrões seguros"},
      "root_px": {"origin": "default", "evidence": "px não exige conversão rem"},
      "steps": {"origin": "default", "evidence": "references/spacing.md: Padrões seguros"},
      "semantics": {"origin": "default", "evidence": "references/spacing.md: Padrões seguros"}
    },
    "pending": ["Inspecionar densidade e layout nos usos reais."]
  }
}
```

`plan` tem exatamente o contrato do helper individual. Não copie fixtures de teste
como decisões de design. Inclua em `pending` as verificações visuais, de fontes,
plataforma e performance ainda não executadas e os avisos da referência.

```bash
# Todas: omita --only. Envie as especificações já resolvidas.
python3 /caminho/da/skill/scripts/foundations.py /projeto --plans /tmp/foundations-input.json
# Parcial ou individual: não acrescente etapas ao subconjunto.
python3 /caminho/da/skill/scripts/foundations.py /projeto --only spacing borders --plans /tmp/foundations-input.json
# Retomada do mesmo escopo: planos salvos e decisões são reutilizados.
python3 /caminho/da/skill/scripts/foundations.py /projeto --only spacing borders
# Caminho alternativo do registro:
python3 /caminho/da/skill/scripts/foundations.py /projeto --decisions acme-ds/decisions.json --only spacing
```

Para manter leitura e decisões por etapa, é possível enviar só os planos já
resolvidos mantendo `--only` com todo o escopo solicitado. O helper salva todas as
etapas pendentes e para na primeira sem plano essencial. Esclareça essa etapa e
retome o mesmo escopo com as novas especificações; etapas concluídas são apenas
verificadas em memória, sem recriar ou regravar tokens/decisões.

O checklist registra `requested`, `steps`, `status` (`pending`, `running`,
`completed`, `failed`), `checks`, especificação com origens, resultados de
`validation`, `pending` e `error`. Cada etapa lê entradas, calcula, valida, grava
apenas adições, relê e recalcula os arquivos finais antes de concluir. Colors exige
AA em todos os pares declarados; os outros helpers validam seu subconjunto de
tipos/aliases. Falha interrompe a sequência: não execute as seguintes enquanto
a etapa afetada estiver bloqueada. Exit 1 indica falha ou pendência essencial;
exit 0 significa todas as etapas solicitadas concluídas nas validações executadas.

As gravações por arquivo usam substituição atômica e um journal `transaction` no
checklist. Após interrupção, retome com o mesmo comando. A recuperação só aceita
arquivos iguais ao estado anterior ou esperado; edições externas causam conflito.
O helper verifica os journals de todo o checklist, inclusive fora do escopo
solicitado. Uma transação pendente bloqueia pedidos que não incluam sua etapa;
retome-a primeiro. Se o pedido também incluir outras etapas, a recuperação ocorre
antes delas, mesmo que a ordem normal comece por outra fundação. Journals pendentes
em múltiplas etapas exigem investigação.
Não apague o journal nem o checklist para contornar falhas. O lock local
`.foundations-plan.lock` impede helpers simultâneos e é liberado pelo sistema ao
encerrar o processo; não coordena editores externos. Não altere os mesmos arquivos
com outra ferramenta durante a execução.

O helper usa a fonte **única** registrada por `init` e nunca combina múltiplos
arquivos para sobrescrever um parcial. Fontes divididas, legadas ou formatos não
suportados exigem mapeamento explícito e revisão dos arquivos de origem conforme
as referências; registre o bloqueio e não migre para satisfazer o helper.

## Entregar

Resuma fundações criadas e reutilizadas, decisões e suas origens, caminhos do
checklist/tokens/decisões, validações realmente executadas e pendências por etapa.
Em falha, informe a etapa, o motivo, o que já foi preservado e como retomar.
Cálculo/AA de pares não comprova WCAG completa, validação visual ou equivalência
Web/Flutter. Não instale fontes, Storybook ou outras ferramentas automaticamente.
