# Estabilização do Prismo

Reproduções anteriores à implementação: `init` registra `paths.tokens: null` para fonte reutilizada; alteração em alias de `dashArray` omite o dependente dos valores resolvidos; JSON duplicado é aceito por `json.loads`; instalador aceita dois projetos separados por `--`; audit classifica tipo `colro` como pendência; suíte documental ignora 14 testes sem dependências e retorna sucesso.

- [x] P0 — Integração dos caminhos de tokens: `init.py`, referências de init, consumidores e testes de integração; validar init/create/tokens/audit e registros anteriores.
- [x] P0 — Aliases compostos: `tokens.py` e testes de tokens; validar valores anteriores/posteriores e dependentes.
- [x] P1 — JSON estrito: helpers consumidores e testes de leitura; validar entradas duplicadas e formatos válidos.
- [x] P1 — Instalador: `scripts/install.sh` e `test_install.py`; validar argumentos ambíguos, copy/symlink e atualização.
- [x] P1 — Classificação do audit: `tokens.py`, `audit.py` e testes; validar erros inválidos, limitações e códigos de saída.
- [x] P1 — Suíte obrigatória: configuração de desenvolvimento, runner e testes de integração; validar ausência e presença das dependências sem skips silenciosos.
- [x] Validação final: suíte completa, estrutura da Skill, instalador e testes de integração; registrar limitações.


Validação executada: 205 testes Python e 53 testes JavaScript aprovados, sem ignorados; regressões do instalador (14) e integração init (12) aprovadas separadamente; `bash -n` e validador estrutural da Skill aprovados. A execução sem dependências de teste retornou falha, conforme esperado. Os testes JavaScript usaram instalações já existentes em leitura; a instalação das dependências declaradas não foi exercitada nesta execução. Registros legados com mais de uma fonte candidata exigem escolha explícita.
