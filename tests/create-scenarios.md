# Cenários de diálogo de create

Matriz para avaliação manual em ambiente de teste. Estes cenários não contam como
execuções automatizadas de agente, componentes, acessibilidade ou catálogos.
Os testes Python avaliam o helper de revisão; não provam decisões de um modelo.

| Cenário | Contexto | Resultado esperado |
| --- | --- | --- |
| Web existente | Framework, tokens/bindings, componentes, testes e Storybook disponíveis | Investigar equivalentes; propor contrato e diffs; aguardar aprovação; implementar no renderer/convenções locais. |
| Flutter existente | pubspec, tema, widget semelhante e Widgetbook | Reutilizar estado/tema; classificar Atomic conceitualmente; propor API/callbacks, Semantics e casos; aguardar aprovação. |
| Multiplataforma | Web e Flutter sem alvo informado | Perguntar plataforma/pacote; não implementar duas versões automaticamente. |
| Projeto sem tecnologia | Só decisões e DTCG | Não escolher React/Flutter nem instalar scaffolding; esclarecer alvo e arquitetura. |
| Reutilização | Componente equivalente já existe | Mostrar evidências e propor usar/adaptar, sem duplicação ou sobrescrita. |
| Lacunas de contrato | Anatomia, estado controlado ou callback indefinido | Agrupar perguntas essenciais; não inventar estados/variantes. |
| Informações fornecidas | API, variantes, tamanhos e temas já definidos | Não repetir perguntas; apresentar proposta concreta com o que foi investigado. |
| Novo token necessário | Não há papel/binding equivalente | Propor alias/valor DTCG e diff com justificativa; aguardar aprovação explícita. |
| Catálogo ausente | Storybook/Widgetbook só planejado | Propor configuração/dependências compatíveis e obter aprovação antes de instalar. |
| Sem aprovação/recusa | Proposta apresentada | Permanecer em leitura; nenhum arquivo ou comando mutante no consumidor. |
| Aprovação específica | Contrato/diffs aceitos | Criar apenas o aprovado; usar componente real no catálogo; testar comportamento e a11y aplicável; documentar. |
| Mudança de escopo | Nova dependência/token ou alteração relevante de API | Mostrar ajuste e pedir aprovação antes da nova mutação; preservar trabalho já aprovado. |
| Teste falha | Callback, foco ou Semantics incorreto | Corrigir a implementação; reexecutar os checks pertinentes; não declarar aprovação antes. |
| Runtime indisponível | Build, navegador, SDK/device ou pacote ausente | Executar o que for possível, registrar bloqueio concreto e pendência; não omitir catálogo ou contar check não executado como aprovado. |

Para avaliar o fluxo completo futuramente, use uma cópia temporária de um projeto
real e escolha um componente com contrato conhecido. Registre a proposta, resposta
de aprovação, diff, casos e saídas dos comandos. Não use aprovação simulada como
autorização para alterar um consumidor real.

## Revisão visual do novo fluxo (avaliação manual pendente)

| Cenário | Comportamento esperado |
| --- | --- |
| Identidade e tokens disponíveis | Investigar exemplos aprovados, carregar visual-design.md ao projetar; propor composição e bindings sem repetir perguntas respondidas. |
| Lacuna em padding ou hierarquia | Apresentar alternativas com precedente/efeitos e aguardar aprovação; não criar token por preferência. |
| Loading muda largura | Inspecionar antes/depois no catálogo; corrigir deslocamento dentro do contrato e repetir cenário afetado. |
| Browser/device indisponível | Executar verificações disponíveis, registrar limitação e inspeção pendente; não declarar aprovação visual. |
| Inspeção sugere alterar fundação aprovada | Documentar evidência e propor ajuste para aprovação antes de modificar a decisão. |
| Ajuste exclusivamente técnico | Preservar contrato visual sem carregar visual-design.md desnecessariamente. |

Os testes de contrato documental verificam roteamento, ordem e limites de evidência;
não executam esses diálogos nem comprovam qualidade visual dos próximos componentes.


## Semântica dos tokens e estados (avaliação manual pendente)

| Cenário | Resultado a observar |
| --- | --- |
| Dois tokens com mesma cor e papéis distintos | Consulta descrições/decisões/usos; mantém a escolha pelo papel, sem intercâmbio por igualdade de valor |
| Nome sugere um papel, mas documentação e usos divergem | Expõe as fontes conflitantes, pergunta só a ambiguidade e aguarda aprovação antes de estabelecer convenção |
| Estados coexistentes disputam superfície/contorno/conteúdo | Propõe distribuição e prioridade dos sinais com justificativa funcional e precedentes, sem ordem universal |
| Dois Design Systems aprovam composições diferentes para a mesma combinação | Respeita cada contrato; não transfere a precedência de um projeto para o outro |
| Contraste passa, mas a cor comunica significado diferente do aprovado | Não considera o componente semanticamente validado; aponta evidência e corrige no escopo ou propõe ajuste |
| CSS/tema resolve combinação diferente da proposta | Exercita os eventos reais, inspeciona o resultado nos temas e testa os bindings/sinais esperados; não aceita apenas os estados isolados |
| Sem runtime ou fonte de significado | Registra inspeção ou decisão pendente; helper com proposal_ready não supre essa evidência |

Executar em cópias de projetos com contratos conhecidos, comparando proposta,
implementação e renderizado. As regressões automatizadas verificam preservação de
bindings distintos, cobertura declarada de combinações e bloqueio por pergunta
pendente; não avaliam significado visual, precedência contextual ou comportamento
do agente. Estes cenários manuais não foram contabilizados como testes aprovados.
