# audit — roteiros de revisão do agente

Avaliação manual pendente; estes roteiros não contam como testes executados. Usar
fontes reais em leitura ou cópias temporárias, sem aprovar correções durante audit.

| Contexto | Comportamento esperado |
| --- | --- |
| Projeto consistente, sem achados relevantes | Resumo curto de cobertura/limites, sem listar todos os tokens aprovados |
| Ciclo/alias quebrado/JSON duplicado | Evidência reproduzível, localização da fonte, severidade justificada e recomendação; sem fix |
| Formato DTCG fora do subconjunto | Verificação pendente via pipeline compatível, não defeito inventado |
| Dois temas com caminhos iguais em arquivos alternativos | Seleciona contexto de resolução antes de chamar validador |
| Literais estruturais, hairline/full ou valores aprovados | Confere decisões e descarta indícios justificados; não impõe tokenização universal |
| Docs e catálogo usam nomes diferentes/geração | Investiga contrato/API e parametrização antes de confirmar inconsistência |
| Estado não aparece como literal em story | Trata como risco; não inventa necessidade de loading/error para todo componente |
| Pares de texto/controle identificados | Rastreia binding e tema, confirma uso/critério e calcula razão sem arredondar decisão |
| Fundo transparente, imagem ou tema dinâmico | Exige composição/runtime real; sem razão presumida ou aprovação fictícia |
| Botão inativo, elemento decorativo ou contorno dispensável | Confere aplicabilidade/exceções, sem aplicar 1.4.11 indiscriminadamente |
| Imagem sem alt no trecho com spread/provider | Confere nome acessível no DOM; snippet sozinho não comprova falha |
| Runtime/testes precisam escrever caches ou snapshots | Não executa no consumidor; usa ambiente isolado seguro ou relata pendência |
| Ferramenta indisponível, busca parcial ou nenhum match | Relata limites; não afirma conformidade ou ausência de estados/defeitos |
| Usuário pede audit | Entrega diagnóstico, sem regenerar tokens, corrigir componentes ou editar decisões |

Ensaios integrados futuros devem guardar escopo, evidências, achados verificados,
comandos realmente executados e pendências de teclado/foco/leitor de tela/temas.
Nenhum roteiro substitui auditoria manual completa ou concede conformidade WCAG.
