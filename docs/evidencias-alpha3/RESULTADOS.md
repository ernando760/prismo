# Validação da candidata v0.1.0-alpha.3

Preparação local em 2026-11-06. Sem commit, tag ou publicação criados nesta
preparação. As [notas da candidata](../experimental-release-notes-0.1.0-alpha.3.md)
descrevem capacidades e limites. Os registros de releases anteriores são históricos.

## Verificações da candidata

- `npm test`: **306 testes Python e 53 JavaScript aprovados**, sem falhas,
  ignorados ou cancelados. JavaScript: catálogo 13, renderização 24, adaptadores 2
  e documentação 14. Inclui smoke sintético de distribuição, testes de instalação,
  compatibilidade legada, journal, lock, conflitos e retomada.
- Validação estrutural da Skill: `Skill is valid!`.
- `bash -n scripts/install.sh`: aprovado.
- Versões coerentes: package.json, package-lock.json (raiz e pacote raiz) e
  metadados da Skill em `0.1.0-alpha.3`. Nenhuma dependência foi atualizada.
- A preparação usa dependências existentes; não comprova nova instalação npm limpa.

O [registro estruturado](../evidence/release-candidate-0.1.0-alpha.3.json) preserva
ambiente, comandos, contagens e hashes dos arquivos de entrada. As verificações
de organização, referências e índice Git complementam esse registro; os arquivos
de evidência não incluem seus próprios hashes, evitando referência circular.

## Integração e avaliação conversacional

A integração anterior, em 2026-11-05, usou uma cópia isolada do Nexa DS: 12 testes
integrados, quatro Web, quatro de catálogo, typecheck e builds Web/Storybook
aprovados. Foram exercitados reuso sem novos aliases, extensão somente em preview,
exceções do Button, temas, recuperação, conflito e bloqueio de migração implícita.
Esse registro antecede a correção final da CLI; a suíte atual e as sessões abaixo
complementam a evidência, sem alegar repetição daquela integração nesta preparação.

Duas sessões novas e independentes do Codex, somente leitura e sem histórico
herdado, receberam pedidos naturais sem explicação do schema. Ambas consultaram
o contrato, apresentaram matriz explícita e executaram `palette --plan -
--require-coverage` com retorno 0 e stderr vazio, conferidos antes de interpretar
stdout. Não houve chamada inválida aos helpers nessas duas sessões.

| Cenário | Cobertura efetivamente validada | Alterações somente em preview |
| --- | --- | --- |
| Link/seleção, claro e escuro, com roadmap | 16 usos: dez parciais e seis adiados | Dois passos brand.300/700; sem modificar o Button |
| Mensagem de sucesso, só claro | Dois usos funcionais parciais | Nenhum token ou alias novo |

Os planos enviados foram reconstruídos dos comandos registrados e reproduzidos;
os resultados coincidiram com os previews observados. Os
[inputs e resultados duráveis](../evidence/alpha3-conversational-validation.json)
preservam os dois planos exatos, pedidos, comandos, saídas essenciais e hashes.
Não dependem da presença local dos POCs ou de transcrições temporárias.
O registro inclui um baseline compartilhado de 42 tokens de cor DTCG, sem outras
fundações. Os dois planos foram reproduzidos com esse baseline portátil e o helper
atual: contrastes, alterações de tokens e resumos de cobertura coincidem exatamente.

A primeira sessão anterior à correção omitiu a matriz e fez quatro chamadas
inválidas. A investigação mostrou `usage` inválido e leitura de stdout antes da
checagem de erro; `/dev/stdin` funcionava e não era a causa. A correção adicionou
ajuda JSON, modo estrito e fluxo incremental antes da proposta. Esses problemas
não reapareceram nas duas sessões corrigidas; isso não prova confiabilidade geral.

## Preservação e limitações

- As quatro cores de hover/pressed do Button foram preservadas e observadas no
  navegador em claro/escuro. Aliases default continuaram ligados a brand.900/100.
- A última avaliação de prontidão confirmou fontes, tokens, decisões e checklist
  do POC 5 iguais ao inventário anterior. Dois arquivos de cache do Storybook em
  node_modules diferiam; a causa não foi estabelecida. Não se afirma identidade
  byte a byte de todo o diretório. Esta preparação não modifica os POCs.
- Contraste aprovado, inspeção visual declarada e conformidade são evidências
  distintas. Link/seleção propostos, combinações de estados e harmonia nos novos
  contextos não receberam aprovação visual. A inspeção anterior do Button teve
  escopo limitado e não comprova WCAG completa.
- Nomenclatura, benefício de evolução, intenção compartilhada e adiamento versus
  ausência de avaliação continuam decisões contextuais revisadas pelo usuário.
- Consumo de contexto permanece parcial: cada sessão corrigida ainda retornou
  cerca de 58 mil caracteres numa leitura e repetiu uma referência.
- DTCG, composição, busca textual, plataformas e validação conversacional ampla
  mantêm os [limites experimentais](../../README.md#limites-de-uso-experimental).

## Organização e próximos passos

`docs/` contém documentação permanente e evidências necessárias às releases.
Planos, investigações, checklists internos de implementação e relatórios de trabalho
foram retirados de docs e do índice quando necessário. Suas cópias estão em pasta
local ignorada; não são requisito para consultar as evidências desta candidata.
Notas oficiais e evidências históricas das releases anteriores foram mantidas.

A candidata está preparada para revisão e consolidação do snapshot. Uma futura
criação de commit/tag ou publicação deve seguir [AGENTS.md](../../AGENTS.md),
incluindo revisão do conteúdo, identidade autorizada, tag anotada inédita e
aprovação do destino público. Esta preparação não executa essas ações.
