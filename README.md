# Projeto Poker Data

Em desenvolvimento por: Apollo borges, Felipe Ferreira, Lucas Barbosa, Luiz Paulo, Cassiano Agra

## Descrição

Repositório de código aberto para registro, tratamento, análise estatística e visualização da evolução das fichas nas partidas de poker do meu grupo de amigos. O projeto recebe os dados brutos das rodadas em um arquivo de texto, organiza as partidas, interpreta os valores de cada rodada como movimentações de fichas e transforma esses registros em séries históricas de saldo para cada jogador.

O processamento é realizado em JavaScript, que também é responsável pela validação das rodadas, identificação de possíveis inconsistências nos dados e controle do histórico de empréstimos e pagamentos. A partir desse processamento, são calculadas estatísticas descritivas individuais e globais, como média, mediana, valores mínimo e máximo, amplitude, desvio padrão e saldo final de cada jogador.

Os resultados são consolidados em temporada.json, que funciona como a fonte estruturada de dados do projeto. Esse arquivo reúne jogadores, saldos acumulados, divisão das partidas e rodadas, médias por rodada, estatísticas descritivas, empréstimos registrados e avisos gerados durante o processamento.

O Python, utilizando Matplotlib, consome os dados processados para gerar as visualizações estatísticas da temporada. Atualmente, o principal gráfico representa a evolução temporal do saldo acumulado de cada jogador ao longo das rodadas, permitindo observar individualmente as variações de desempenho e, simultaneamente, o comportamento geral da mesa.

## Para fazer
* [ ] Integrar com API do Google Spreadsheet (falar com felipe)
* [ ] Análise de distribuição dos saldos
* [ ] Correlação entre jogadores
* [ ] Modelos de regressão (acho bonito mas não sei o que é)

## Status atual

* [x] Gráfico de saldo acumulado por rodada
* [x] Média de saldo por jogador
* [x] Mediana de saldo por jogador
* [x] Saldo mínimo e máximo por jogador
* [x] Amplitude por jogador
* [x] Desvio padrão por jogador
* [x] Saldo final por jogador
* [x] Média atual e média histórica
* [x] Amplitude total dos saldos
* [x] Valor mínimo e máximo global
* [x] Desvio padrão global
* [x] Identificação das fronteiras entre jogos
* [x] Visualização da amplitude dos saldos por rodada
* [x] Registro e visualização de empréstimos
* [x] Histórico de empréstimos tomados e pagos
* [x] Processamento dos dados brutos em JavaScript
* [x] Geração de um único `temporada.json` como fonte de dados processados
* [x] Consumo do `temporada.json` pelo Python/Matplotlib
* [x] Visualização dinâmica conforme os jogadores e jogos registrados no JSON

