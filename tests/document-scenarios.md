# document — cenários de avaliação do agente

Roteiros manuais, não contabilizados como testes automatizados. Usar cópia temporária
do consumidor, nunca simular aprovação para modificar o projeto real.

| Pedido/contexto | Resultado a observar |
| --- | --- |
| Documentar Colors, portal e tokens existentes | Consulta fontes e temas; propõe página/diff e reutiliza catálogo sem recalcular ou copiar valores como outra fonte |
| Documentar Button com README/API gerada/stories | Orientação/anatomia/uso no portal, links para API/casos reais; não duplica tabelas geradas |
| Flutter com Widgetbook local sem publicação | Referência ao use-case/caminho/comando conhecidos; não inventa URL nem importa Dart em MDX |
| Sem Docusaurus | Proposta de setup com dependências/arquivos; nenhuma instalação/escrita antes da aprovação |
| Setup recusado/adiado | Informa pendência e aguarda decisão sobre destino alternativo; não instala outro portal |
| Dois portais/idiomas/versões | Identifica destino e preserva rotas, sidebars, versões congeladas e traduções fora do escopo |
| Identidade sem regra de logo/marca | Perguntas objetivas; não deduz regra a partir de um asset ou gera marca |
| API diverge de decisões | Apresenta conflito; não corrige componente/tokens para combinar com o texto |
| Informações já disponíveis | Não pergunta novamente; cita fontes, diferencia fatos e lacunas |
| Proposta não aprovada ou só create aprovado | Nenhum arquivo do consumidor alterado |
| Proposta aprovada | Executa somente diffs aprovados, com cobertura aplicável e fontes rastreáveis |
| Build/links/MDX falham ou runtime indisponível | Corrige regressão no escopo ou reporta bloqueio; não relaxa checks nem declara aprovado |

Próximo ensaio ponta a ponta: selecionar portal real e tópico, registrar proposta e
aprovação, comparar conteúdo com fontes, executar build/links/exemplos e inspecionar
páginas no browser. Registrar diff e evidências, incluindo preservação das fundações.
