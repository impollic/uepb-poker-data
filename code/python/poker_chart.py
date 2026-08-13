import glob
import json
import os
import re

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

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

COR_MEDIA = "#000000"
COR_AMPLITUDE = "#000000"

if not ARQUIVOS_JOGOS:
    raise FileNotFoundError(f"Nenhum arquivo de jogo encontrado em {PADRAO_ARQUIVOS_JOGOS}")

# Lendo os jogos

jogos = []
for caminho in ARQUIVOS_JOGOS:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        jogos.append(json.load(arquivo))

# Juntando os saldos em série continua

saldos_combinados = {nome: [] for nome in ORDEM_JOGADORES}
media_combinada = []
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

    serie_media = jogo["media"]
    if indice_jogo == 0:
        media_combinada.extend(serie_media)
    else:
        media_combinada.extend(serie_media[1:])

    cursor += tamanho_jogo if indice_jogo == 0 else tamanho_jogo - 1
    fronteiras_rodadas.append(cursor - 1)

num_pontos = len(saldos_combinados[ORDEM_JOGADORES[0]])
x = np.arange(num_pontos)

# Amplitude por rodada

maximo_rodada = [
    max(saldos_combinados[nome][i] for nome in ORDEM_JOGADORES)
    for i in range(num_pontos)
]
minimo_rodada = [
    min(saldos_combinados[nome][i] for nome in ORDEM_JOGADORES)
    for i in range(num_pontos)
]

# Estatísticas descritivas por jogador

todos_valores_combinados = [v for serie in saldos_combinados.values() for v in serie]

estatisticas_jogadores = {}
for nome in ORDEM_JOGADORES:
    serie = saldos_combinados[nome]
    estatisticas_jogadores[nome] = {
        "n": len(serie),
        "media": float(np.mean(serie)),
        "mediana": float(np.median(serie)),
        "minimo": min(serie),
        "maximo": max(serie),
        "amplitude": max(serie) - min(serie),
        "desvio_padrao": float(np.std(serie)),
        "saldo_final": serie[-1],
    }

# Estatísticas descritivas globais (rodapé)

amplitude_total_grupo = max(todos_valores_combinados) - min(todos_valores_combinados)
desvio_padrao_grupo = float(np.std(todos_valores_combinados))
media_geral_grupo = float(np.mean(todos_valores_combinados))
coeficiente_variacao_grupo = (
    desvio_padrao_grupo / media_geral_grupo if media_geral_grupo != 0 else float("nan")
)

# Plot

figura = plt.figure(figsize=(16, 9), dpi=110)
figura.patch.set_facecolor("white")

grade = GridSpec(
    nrows=4,
    ncols=2,
    figure=figura,
    width_ratios=[3.1, 1],
    height_ratios=[0.9, 0.55, 6.5, 1.1],
    hspace=0.18,
    wspace=0.15,
)

eixo_titulo = figura.add_subplot(grade[0, :])
eixo_legenda = figura.add_subplot(grade[1, :])
eixo = figura.add_subplot(grade[2, 0])
eixo_estatisticas = figura.add_subplot(grade[2, 1])
eixo_rodape = figura.add_subplot(grade[3, :])

eixo_titulo.axis("off")
eixo_legenda.axis("off")
eixo_estatisticas.axis("off")
eixo_estatisticas.set_facecolor("#555")
eixo_rodape.axis("off")
eixo.set_facecolor("white")

# --- Título ---

eixo_titulo.text(
    0.04,
    0.3,
    "Poker-Data",
    fontsize=24,
    fontweight="bold",
    color="#1A1A1A",
    ha="center",
    va="center",
)

# --- Gráfico principal ---

eixo.fill_between(
    x,
    minimo_rodada,
    maximo_rodada,
    color=COR_AMPLITUDE,
    alpha=0.05,
    linewidth=0,
    zorder=1,
)
# opacidade da amplitude

for nome in ORDEM_JOGADORES:
    serie = saldos_combinados[nome]
    eh_lider = nome == "Apollo"
    eixo.plot(
        x,
        serie,
        color=CORES[nome],
        linewidth= 2.25 if eh_lider else 2,
        alpha=1.0 if eh_lider else 0.9,
        zorder=5 if eh_lider else 3,
        solid_capstyle="butt",
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

eixo.plot(
    x,
    media_combinada,
    color=COR_MEDIA,
    linewidth=1,
    linestyle=(0, (6, 4)),
    alpha=0.5,
    zorder=4,
    dash_capstyle="round",
)
eixo.annotate(
    "  Média",
    (x[-1], media_combinada[-1]),
    xytext=(6, 0),
    textcoords="offset points",
    va="center",
    ha="left",
    fontsize=10,
    fontweight="bold",
    color=COR_MEDIA,
    alpha=0.65,
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

todos_valores = todos_valores_combinados + media_combinada
eixo.set_ylim(min(todos_valores) - 200, max(todos_valores) + 200)
eixo.set_xlim(-0.5, num_pontos - 0.5)

eixo.set_ylabel("Saldo acumulado (R$)", fontsize=9.5, color="#444444", labelpad=10)
eixo.set_xlabel("Rodadas", fontsize=9.5, color="#444444", labelpad=10)

# Legenda

itens_legenda = ORDEM_JOGADORES + ["Média", "Amplitude"]
n_itens_legenda = len(itens_legenda)

for i, nome in enumerate(itens_legenda):
    x0 = i / n_itens_legenda * 0.75 - 0.025
    eh_media = nome == "Média"
    eh_amplitude = nome == "Amplitude"
    cor_item = COR_MEDIA if (eh_media or eh_amplitude) else CORES[nome]

    if eh_amplitude:
        eixo_legenda.add_patch(
            plt.Rectangle(
                (x0, 0.3),
                0.028,
                0.4,
                transform=eixo_legenda.transAxes,
                facecolor=COR_AMPLITUDE,
                alpha=0.12,
                linewidth=0,
                clip_on=False,
            )
        )
    else:
        eixo_legenda.add_patch(
            plt.Rectangle(
                (x0, 0.3),
                0.028,
                0.4,
                transform=eixo_legenda.transAxes,
                facecolor=cor_item,
                alpha=0.55 if eh_media else 1.0,
                linewidth=0,
                clip_on=False,
            )
        )

    eixo_legenda.text(
        x0 + 0.042,
        0.5,
        nome,
        transform=eixo_legenda.transAxes,
        fontsize=9.5,
        va="center",
        ha="left",
        color=cor_item,
        alpha=0.65 if (eh_media or eh_amplitude) else 1.0,
    )

eixo_legenda.set_xlim(0, 1)
eixo_legenda.set_ylim(0, 1)

# Sidebar

eixo_estatisticas.set_xlim(0, 1)
eixo_estatisticas.set_ylim(0, 1)

eixo_estatisticas.annotate(
    "Estatísticas por jogador",
    xy=(0.0, 0.935),
    xytext=(0, 0),
    textcoords="offset points",
    xycoords="axes fraction",
    fontsize=10.5,
    fontweight="bold",
    color="#1A1A1A",
    ha="left",
    va="top",
    linespacing=1.4,
)

# Tabela

linhas_estatistica = [
    ("x̄", "media", "{:,.0f}"),
    ("Md", "mediana", "{:,.0f}"),
    ("Xmin", "minimo", "{:,.0f}"),
    ("Xmax", "maximo", "{:,.0f}"),
    ("At", "amplitude", "{:,.0f}"),
    ("Dp", "desvio_padrao", "{:,.0f}"),
    ("Saldo Atual", "saldo_final", "{:,.0f}"),
]

ALTURA_LINHA_PONTOS = 15.5
ALTURA_CABECALHO_PONTOS = 46
LARGURA_COLUNA_ROTULO = 0.40

largura_coluna_jogador = (1.0 - LARGURA_COLUNA_ROTULO) / len(ORDEM_JOGADORES)
posicoes_coluna_jogador = [
    LARGURA_COLUNA_ROTULO + largura_coluna_jogador * (i + 0.5)
    for i in range(len(ORDEM_JOGADORES))
]

# Cabeçalho das colunas

for nome, x_coluna in zip(ORDEM_JOGADORES, posicoes_coluna_jogador):
    eixo_estatisticas.annotate(
        nome[:3],
        xy=(x_coluna, 1.0),
        xytext=(0, -ALTURA_CABECALHO_PONTOS),
        textcoords="offset points",
        xycoords="axes fraction",
        fontsize=8.5,
        fontweight="semibold",
        color=CORES[nome],
        ha="center",
        va="top",
    )

eixo_estatisticas.annotate(
    "",
    xy=(0.0, 1.0),
    xytext=(0, -(ALTURA_CABECALHO_PONTOS + 13)),
    textcoords="offset points",
    xycoords="axes fraction",
)

deslocamento_pontos = ALTURA_CABECALHO_PONTOS + 15

for rotulo, chave, formato in linhas_estatistica:
    eixo_estatisticas.annotate(
        rotulo,
        xy=(0.0, 1.0),
        xytext=(0, -deslocamento_pontos),
        textcoords="offset points",
        xycoords="axes fraction",
        fontsize=7.6,
        color="#777777",
        ha="left",
        va="top",
    )

    for nome, x_coluna in zip(ORDEM_JOGADORES, posicoes_coluna_jogador):
        valor = estatisticas_jogadores[nome][chave]
        texto_valor = formato.format(valor)

        eixo_estatisticas.annotate(
            texto_valor,
            xy=(x_coluna, 1.0),
            xytext=(0, -deslocamento_pontos),
            textcoords="offset points",
            xycoords="axes fraction",
            fontsize=7.6,
            color="#333333",
            ha="center",
            va="top",
            family="monospace",
        )

    deslocamento_pontos += ALTURA_LINHA_PONTOS

# Rodapé

eixo_rodape.set_xlim(0, 1)
eixo_rodape.set_ylim(0, 1)

blocos_rodape = [
    (
        "Amplitude total",
        f"R$ {amplitude_total_grupo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    ),
    ("Valor máximo", f"R$ {max(todos_valores_combinados):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
    ("Valor mínimo", f"R$ {min(todos_valores_combinados):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")),
    (
        "Desvio padrão",
        f"R$ {desvio_padrao_grupo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    ),
    (
        "Média atual",
        f"R$ {media_geral_grupo:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
    ),
]

n_blocos_rodape = len(blocos_rodape)
for indice_bloco, (rotulo, valor) in enumerate(blocos_rodape):
    x0 = indice_bloco / n_blocos_rodape * 0.78

    eixo_rodape.text(
        x0,
        0.55,
        rotulo,
        fontsize=8,
        color="#888888",
        ha="left",
        va="top",
    )
    eixo_rodape.text(
        x0,
        0.20,
        valor,
        fontsize=11,
        fontweight="bold",
        color="#333333",
        ha="left",
        va="top",
    )

eixo_rodape.text(
    1.0,
    0.15,
    "Fonte: histórico de partidas registrado manualmente",
    fontsize=10,
    color="#AAAAAA",
    ha="right",
    va="center",
    style="italic",
)

figura.text(
    0.5,
    0.965,
    "Saldo acumulado das movimentações registradas no histórico, incluindo empréstimos como entradas positivas.",
    fontsize=8.5,
    color="#888888",
    ha="center",
)

plt.subplots_adjust(top=0.94, bottom=0.05, left=0.070, right=0.97)

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