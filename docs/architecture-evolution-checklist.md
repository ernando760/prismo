# Evolução arquitetural do Prismo

- [x] Definir contrato versionado de caminhos e compatibilidade legada.
- [x] Adaptar init para caminhos explícitos e criação sob demanda.
- [x] Reconhecer pacotes e documentação aninhados nos helpers existentes.
- [x] Atualizar orientações, templates e preparação de bibliotecas.
- [x] Cobrir integração e regressões entre operações.
- [x] Executar suíte completa e revisar alterações (concluído na estabilização posterior).

## Integrações concluídas

- [x] Integrar caminhos registrados aos helpers de documentação e catálogo, preservando precedência e comportamento legado.
- [x] Aplicar caminhos registrados e validação de consumo às instruções de instalação e criação aprovadas.
- [x] Validar integração de projetos simples, pacotes aninhados e configurações legadas.
- [x] Executar a suíte completa e registrar bloqueios.

Resultado: 225 testes Python e 13 testes JavaScript passaram. Os testes de renderização Storybook (24), adaptadores (2) e document (14) foram ignorados por falta das dependências npm; a instalação offline falhou por cache incompleto. Esse bloqueio pertencia à execução original; foi superado posteriormente.


Conclusão posterior: a [estabilização após POC 2](poc2-stabilization-checklist.md)
executou 234 testes Python e 53 JavaScript sem ignorados, com dependências
compatíveis existentes. O resultado anterior foi preservado como histórico;
instalação limpa e validação da preparação atual são acompanhadas no
[checklist da release experimental](experimental-release-checklist.md).
