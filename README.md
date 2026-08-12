# UEPB Poker Data

Repositório de código aberto para análise e visualização da evolução das fichas nos jogos de poker do meu grupo de amigos. Os dados brutos das rodadas são tratados em JavaScript/TypeScript e convertidos em séries acumuladas, que são consumidas por um script Python + Matplotlib para gerar gráficos estatísticos — atualmente, a corrida temporal do saldo acumulado de cada jogador ao longo das rodadas. A ideia é expandir futuramente para outras métricas, como médias e desvio padrão por jogador.

## Estrutura do projeto

```
uepb-poker-data/
├── code/
│   ├── javascript/
│   │   └── data_handling.js   # transforma os dados brutos (raw) em séries acumuladas (processed)
│   └── python/
│       └── poker_chart.py     # lê os dados processados e plota o gráfico com Matplotlib
├── data/
│   ├── raw/
│   │   ├── game_1.txt
│   │   └── game_2.txt
│   └── processed/
│       ├── game_1.json
│       └── game_2.json
├── LICENSE
└── README.md
```

## Como os dados funcionam

### 1. Dados brutos (`data/raw/game_N.txt`)

Cada arquivo `.txt` representa uma partida (game) e contém uma rodada por linha. Cada linha tem 5 números separados por espaço, representando a **variação de fichas** (delta) de cada jogador naquela rodada — não o saldo total, apenas o quanto ele ganhou ou perdeu em relação à rodada anterior.

A ordem das colunas é sempre a mesma:

```
Apollo  Felipe  Lucas  Luiz  Cassiano
```

Exemplo (`game_2.txt`):

```
-25 -25 135 -85 0
-15 65 -25 -25 0
80 -10 -50 -20 0
-25 -25 -25 75 0
0 0 0 200 0
```

Nesse exemplo, na primeira linha (rodada 1 do jogo 2): Apollo perdeu 25, Felipe perdeu 25, Lucas ganhou 135, Luiz perdeu 85 e Cassiano não teve variação. Um valor como o `200` isolado na última linha, por exemplo, normalmente representa um empréstimo registrado como entrada positiva no saldo do jogador.

### 2. Processamento (`code/javascript/data_handling.js`)

O script Node.js lê o `.txt` da partida, parte de um saldo inicial (`currentValues`, definido manualmente com o saldo final da partida anterior — ou o buy-in inicial, no caso da primeira partida) e vai somando cada linha do arquivo ao saldo acumulado do jogador, gerando um array de saldos por rodada para cada jogador.

O resultado é salvo como JSON em `data/processed/game_N.json`, no formato:

```json
{
  "Apollo": [1490, 1465, 1450, ...],
  "Felipe": [255, 230, 295, ...],
  "Lucas": [155, 290, 265, ...],
  "Luiz": [-600, -685, -710, ...],
  "Cassiano": [380, 380, 380, ...]
}
```

Cada array representa o saldo acumulado do jogador rodada a rodada, começando pelo saldo inicial daquela partida.

### 3. Visualização (`code/python/poker_chart.py`)

O script Python descobre automaticamente todos os arquivos `data/processed/game_*.json` (em ordem numérica), concatena as séries de todas as partidas em uma única linha do tempo contínua e plota, com Matplotlib, a evolução do saldo acumulado de cada jogador ao longo de todas as rodadas — com uma linha vertical marcando a fronteira entre o fim de uma partida e o início da próxima.

## Como rodar

1. Adicione o `.txt` da partida em `data/raw/`, seguindo o formato descrito acima.
2. Gere o JSON processado:

   ```bash
   node code/javascript/data_handling.js
   ```

3. Gere e visualize o gráfico:

   ```bash
   python3 code/python/poker_chart.py
   ```

   O gráfico abre em uma janela interativa (Matplotlib), sem gerar arquivo de imagem.

## Adicionando uma nova partida

Basta criar `data/raw/game_N.txt` com o mesmo formato (uma rodada por linha, 5 valores na ordem `Apollo Felipe Lucas Luiz Cassiano`), ajustar o `data_handling.js` para apontar para o novo arquivo e o saldo inicial da partida, e gerar o `game_N.json` correspondente em `data/processed/`. O `poker_chart.py` detecta o novo arquivo automaticamente, sem precisar de nenhuma alteração no código Python.

## Status atual

- [x] Gráfico de saldo acumulado por rodada (corrida temporal)
- [ ] Média de saldo por jogador
- [ ] Desvio padrão por jogador
- [ ] Outras métricas estatísticas

