# tokens — roteiros de avaliação do agente

Cenários manuais, não contados como testes executados. Usar cópia temporária do
consumidor e registrar proposta/aprovação; nunca simular aprovação no projeto real.

| Contexto/pedido | Comportamento esperado |
| --- | --- |
| Novo papel de componente | Busca equivalentes e usa alias semântico; pergunta finalidade/valor ausente, sem criar escala |
| Editar primitivo usado em vários temas | Proposta mostra dependentes transitivos, valores resolvidos e consumidores/bindings |
| Renomear sem alterar valor | Expõe quebra de contrato e aliases reescritos; não confunde valor igual com impacto zero |
| Reorganizar fontes divididas | Seleciona fontes verdadeiras, preserva metadados/herança e verifica o resultado conjunto |
| Remover com consumidores | Propõe migração/compatibilidade ou adia; não faz cascade nem modifica componentes automaticamente |
| Valores iguais com papéis distintos | Mostra candidatos e pede decisão, sem mesclar por igualdade numérica |
| Alias/tipo inválido na base | Propõe reparo, explicita comparação resolvida indisponível e valida todo resultado |
| JSON Pointer/cores não sRGB/pipeline especial | Informa limitação do helper e usa pipeline compatível, sem converter/simplificar a fonte por conta própria |
| Só aprovação de foundations ou nenhuma aprovação | Não persiste nem considera o preview uma aprovação |
| Fontes mudam após proposta | Recalcula diff/impacto e reapresenta mudança material antes de escrever |
| Migração exige componente/docs | Mostra diffs separados e obtém autorização; não altera consumidores como efeito colateral |
| Aplicação parcial ou validação pós-escrita falha | Restaura fontes anteriores e relata pendência; não declara sucesso parcial como concluído |
| Busca sem ocorrências | Declara escopo/limites e verifica bindings/dinâmica; não afirma impacto zero |

Próximo ensaio integrado: token e consumidor escolhidos, fontes e usos investigados,
proposta/diffs aprovados, aplicação pelo agente, validação CLI contra arquivos reais,
geração de bindings e testes dos consumidores afetados. Guardar as evidências e
conferir preservação de decisões/fundações fora do escopo.
