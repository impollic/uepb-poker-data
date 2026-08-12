import glob
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np

DIRETORIO_DADOS = "./data/processed"
PADRAO_ARQUIVOS_JOGOS = os.path.join(DIRETORIO_DADOS, "game_*.json")

def extrair_numero_jogo(caminho):
    correspondencia = re.search(r"game_(\d+)\.json$", os.path.basename(caminho))
    return int(correspondencia.group(1)) if correspondencia else 0


ARQUIVOS_JOGOS = sorted(glob.glob(PADRAO_ARQUIVOS_JOGOS), key=extrair_numero_jogo)

ORDEM_JOGADORES = ["Apollo", "Felipe", "Lucas", "Luiz", "Cassiano"]

CORES = {
    "Apollo": "#E53935",
    "Felipe": "#2E7D32",
    "Lucas": "#FB8C00",
    "Luiz": "#8E24AA",
    "Cassiano": "#1E88E5",
}

if not ARQUIVOS_JOGOS:
    raise FileNotFoundError(f"Nenhum arquivo de jogo encontrado em {PADRAO_ARQUIVOS_JOGOS}")

jogos = []
for caminho in ARQUIVOS_JOGOS:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        jogos.append(json.load(arquivo))

saldos_combinados = {nome: [] for nome in ORDEM_JOGADORES}
fronteiras_rodadas = []
cursor = 0

for indice_jogo, jogo in enumerate(jogos):
    tamanho_jogo = len(jogo[ORDEM_JOGADORES[0]])
    for nome in ORDEM_JOGADORES:
        serie = jogo[nome]
        if indice_jogo == 0:
            saldos_combinados[nome].extend(serie)
        else:
            saldos_combinados[nome].extend(serie[1:])
    cursor += tamanho_jogo if indice_jogo == 0 else tamanho_jogo - 1
    fronteiras_rodadas.append(cursor - 1)

num_pontos = len(saldos_combinados[ORDEM_JOGADORES[0]])
x = np.arange(num_pontos)

figura = plt.figure(figsize=(15, 8), dpi=110)
eixo = figura.add_subplot(111)
figura.patch.set_facecolor("white")
eixo.set_facecolor("white")

for nome in ORDEM_JOGADORES:
    serie = saldos_combinados[nome]
    eh_lider = nome == "Apollo"
    eixo.plot(
        x,
        serie,
        color=CORES[nome],
        linewidth=3.2 if eh_lider else 2.2,
        alpha=1.0 if eh_lider else 0.9,
        zorder=5 if eh_lider else 3,
        solid_capstyle="round",
    )
    eixo.annotate(
        f"  {nome}",
        (x[-1], serie[-1]),
        xytext=(6, 0),
        textcoords="offset points",
        va="center",
        ha="left",
        fontsize=11,
        fontweight="bold",
        color=CORES[nome],
    )

for indice_fronteira, x_fronteira in enumerate(fronteiras_rodadas[:-1]):
    eixo.axvline(x_fronteira, color="#AAAAAA", linewidth=1.3, linestyle="--", zorder=2)
    eixo.annotate(
        f"Fim do jogo {indice_fronteira + 1} / Início do jogo {indice_fronteira + 2}",
        (x_fronteira, eixo.get_ylim()[1]),
        xytext=(4, -4),
        textcoords="offset points",
        va="top",
        ha="left",
        fontsize=8.5,
        color="#888888",
        rotation=90,
    )

eixo.axhline(0, color="#BBBBBB", linewidth=1.2, zorder=1)
eixo.grid(axis="y", color="#ECECEC", linewidth=1, zorder=0)
eixo.set_axisbelow(True)

eixo.spines["top"].set_visible(False)
eixo.spines["right"].set_visible(False)
eixo.spines["left"].set_visible(False)
eixo.spines["bottom"].set_color("#CCCCCC")

eixo.set_xticks(x)
eixo.set_xticklabels([str(i) for i in x], fontsize=8, color="#666666")
eixo.tick_params(axis="y", labelsize=10.5, colors="#444444", length=0)
eixo.tick_params(axis="x", length=0)

todos_valores = [v for serie in saldos_combinados.values() for v in serie]
eixo.set_ylim(min(todos_valores) - 200, max(todos_valores) + 200)
eixo.set_xlim(-0.5, num_pontos - 0.5 + 3.0)

eixo.set_ylabel("Saldo acumulado (R$)", fontsize=11.5, color="#444444", labelpad=10)
eixo.set_xlabel("Rodadas", fontsize=11.5, color="#444444", labelpad=10)

figura.text(0.5, 0.955, "Poker: Temporada 2", fontsize=24, fontweight="bold", color="#1A1A1A", ha="center")

eixo_legenda = figura.add_axes([0.07, 0.865, 0.86, 0.05])
eixo_legenda.axis("off")
n_itens_legenda = len(ORDEM_JOGADORES)
for i, nome in enumerate(ORDEM_JOGADORES):
    x0 = i / n_itens_legenda
    eixo_legenda.plot(
        [x0, x0 + 0.028],
        [0.5, 0.5],
        color=CORES[nome],
        linewidth=3.5,
        solid_capstyle="round",
        transform=eixo_legenda.transAxes,
        clip_on=False,
    )
    eixo_legenda.text(
        x0 + 0.042,
        0.5,
        nome,
        transform=eixo_legenda.transAxes,
        fontsize=10.5,
        va="center",
        ha="left",
        fontweight="semibold",
        color=CORES[nome],
    )
eixo_legenda.set_xlim(0, 1)
eixo_legenda.set_ylim(0, 1)

figura.text(
    0.5,
    0.02,
    "Saldo acumulado das movimentações registradas no histórico, incluindo empréstimos como entradas positivas.",
    fontsize=8.5,
    color="#888888",
    ha="center",
)

plt.subplots_adjust(top=0.83, bottom=0.12, left=0.06, right=0.95)

gerenciador = figura.canvas.manager
if hasattr(gerenciador, "set_window_title"):
    gerenciador.set_window_title("Poker: Temporada 2")
try:
    gerenciador.window.state("zoomed")
except Exception:
    try:
        gerenciador.resize(*gerenciador.window.maxsize())
    except Exception:
        pass

plt.show()