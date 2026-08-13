import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec


CAMINHO_TEMPORADA = Path("./data/processed/temporada.json")

CORES = {
    "Apollo": "#E53935",
    "Felipe": "#2E7D32",
    "Lucas": "#FB8C00",
    "Luiz": "#8E24AA",
    "Cassiano": "#1E88E5",
    "Wanderson": "#6D4C41",
}

CORES_FALLBACK = [
    "#E53935",
    "#2E7D32",
    "#FB8C00",
    "#8E24AA",
    "#1E88E5",
    "#6D4C41",
    "#00897B",
    "#3949AB",
    "#F4511E",
    "#8E24AA",
]

COR_MEDIA = "#000000"
COR_AMPLITUDE = "#000000"


def carregar_temporada():
    if not CAMINHO_TEMPORADA.exists():
        raise FileNotFoundError(
            f"Arquivo da temporada não encontrado: {CAMINHO_TEMPORADA}"
        )

    with CAMINHO_TEMPORADA.open("r", encoding="utf-8") as arquivo:
        temporada = json.load(arquivo)

    campos_obrigatorios = {
        "jogadores",
        "valoresIniciais",
        "jogos",
        "saldos",
        "media",
        "estatisticas",
        "emprestimos",
        "avisos",
    }

    campos_ausentes = campos_obrigatorios - temporada.keys()
    if campos_ausentes:
        raise ValueError(
            "O arquivo temporada.json não possui os campos obrigatórios: "
            + ", ".join(sorted(campos_ausentes))
        )

    return temporada


def obter_cores(jogadores):
    cores = {}

    for indice, nome in enumerate(jogadores):
        cores[nome] = CORES.get(
            nome,
            CORES_FALLBACK[indice % len(CORES_FALLBACK)],
        )

    return cores


def formatar_reais(valor, casas=0):
    texto = f"R$ {valor:,.{casas}f}"
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


temporada = carregar_temporada()

ORDEM_JOGADORES = temporada["jogadores"]
CORES_JOGADORES = obter_cores(ORDEM_JOGADORES)

valores_iniciais = temporada["valoresIniciais"]
jogos = temporada["jogos"]
saldos = temporada["saldos"]
media = temporada["media"]

estatisticas_jogadores = temporada["estatisticas"]["porJogador"]
estatisticas_gerais = temporada["estatisticas"]["geral"]

emprestimos_jogadores = temporada["emprestimos"]["porJogador"]
emprestimos_gerais = temporada["emprestimos"]["geral"]
avisos = temporada["avisos"]


# Validação estrutural dos dados recebidos.
num_pontos = len(media)

for nome in ORDEM_JOGADORES:
    if nome not in saldos:
        raise ValueError(f"Não existem saldos para o jogador '{nome}'.")

    if len(saldos[nome]) != num_pontos:
        raise ValueError(
            f"A série de saldos de '{nome}' possui {len(saldos[nome])} pontos, "
            f"mas a média possui {num_pontos} pontos."
        )

    if nome not in estatisticas_jogadores:
        raise ValueError(
            f"Não existem estatísticas calculadas para o jogador '{nome}'."
        )

    if nome not in emprestimos_jogadores:
        raise ValueError(
            f"Não existem dados de empréstimos para o jogador '{nome}'."
        )


x = np.arange(num_pontos)

maximo_rodada = [
    max(saldos[nome][i] for nome in ORDEM_JOGADORES)
    for i in range(num_pontos)
]

minimo_rodada = [
    min(saldos[nome][i] for nome in ORDEM_JOGADORES)
    for i in range(num_pontos)
]


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

figura.text(
    0.5,
    0.965,
    (
        f"{len(jogos)} jogo{'s' if len(jogos) != 1 else ''} • "
        f"{num_pontos} rodadas registradas"
    ),
    fontsize=8.5,
    color="#888888",
    ha="center",
)


# --- Gráfico principal ---

eixo.fill_between(
    x,
    minimo_rodada,
    maximo_rodada,
    color=COR_AMPLITUDE,
    alpha=0.01,
    linewidth=0,
    zorder=1,
)
# alpha da amplitude

for nome in ORDEM_JOGADORES:
    serie = saldos[nome]
    eh_lider = nome == "Apollo"

    eixo.plot(
        x,
        serie,
        color=CORES_JOGADORES[nome],
        linewidth=1.8 if eh_lider else 1.8, #todo alterar dps
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
        color=CORES_JOGADORES[nome],
    )


eixo.plot(
    x,
    media,
    color=COR_MEDIA,
    linewidth=1,
    linestyle=(0, (6, 4)),
    alpha=0.5,
    zorder=4,
    dash_capstyle="round",
)

eixo.annotate(
    "  Média",
    (x[-1], media[-1]),
    xytext=(6, 0),
    textcoords="offset points",
    va="center",
    ha="left",
    fontsize=10,
    fontweight="bold",
    color=COR_MEDIA,
    alpha=0.65,
)


# Fronteiras dos jogos vêm prontas do JSON.
for indice, jogo in enumerate(jogos[:-1]):
    x_fronteira = jogo["indiceFinal"]

    if not 0 <= x_fronteira < num_pontos:
        continue

    eixo.axvline(
        x_fronteira,
        color="#AAAAAA",
        linewidth=1.3,
        linestyle="--",
        zorder=2,
    )

    proximo_jogo = jogos[indice + 1]["numero"]

    eixo.annotate(
        (
            f"Fim do jogo {jogo['numero']} / "
            f"Início do jogo {proximo_jogo}"
        ),
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

todos_valores = [
    valor
    for nome in ORDEM_JOGADORES
    for valor in saldos[nome]
]

eixo.set_ylim(min(todos_valores + media) - 200, max(todos_valores + media) + 200)
eixo.set_xlim(-0.5, num_pontos - 0.5)

eixo.set_ylabel(
    "Saldo acumulado (R$)",
    fontsize=9.5,
    color="#444444",
    labelpad=10,
)

eixo.set_xlabel(
    "Rodadas",
    fontsize=9.5,
    color="#444444",
    labelpad=10,
)


# --- Legenda ---

itens_legenda = ORDEM_JOGADORES + ["Média", "Amplitude"]
n_itens_legenda = len(itens_legenda)

for indice, nome in enumerate(itens_legenda):
    x0 = indice / n_itens_legenda * 0.8 - 0.025

    eh_media = nome == "Média"
    eh_amplitude = nome == "Amplitude"

    cor_item = (
        COR_MEDIA
        if (eh_media or eh_amplitude)
        else CORES_JOGADORES[nome]
    )

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


# --- Sidebar ---

eixo_estatisticas.set_xlim(0, 1)
eixo_estatisticas.set_ylim(0, 1)

eixo_estatisticas.annotate(
    "Estatísticas por jogador",
    xy=(0.0, 0.955),
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

linhas_estatistica = [
    ("Saldo inicial", "saldo_inicial", "{:,.0f}"),
    ("x̄", "media", "{:,.0f}"),
    ("Md", "mediana", "{:,.0f}"),
    ("Xmin", "minimo", "{:,.0f}"),
    ("Xmax", "maximo", "{:,.0f}"),
    ("At", "amplitude", "{:,.0f}"),
    ("Dp", "desvioPadrao", "{:,.0f}"),
    ("Saldo Atual", "saldoFinal", "{:,.0f}"),
]

linhas_emprestimos = [
    ("Tomados", "totalTomados", "{:,.0f}"),
    ("Pagos", "totalPagos", "{:,.0f}"),
    ("Em aberto", "totalEmAberto", "{:,.0f}"),
]

ALTURA_LINHA_PONTOS = 14
ALTURA_CABECALHO_PONTOS = 40
LARGURA_COLUNA_ROTULO = 0.39

largura_coluna_jogador = (
    1.0 - LARGURA_COLUNA_ROTULO
) / len(ORDEM_JOGADORES)

posicoes_coluna_jogador = [
    LARGURA_COLUNA_ROTULO + largura_coluna_jogador * (i + 0.5)
    for i in range(len(ORDEM_JOGADORES))
]

# Cabeçalho das colunas.

for nome, x_coluna in zip(ORDEM_JOGADORES, posicoes_coluna_jogador):
    eixo_estatisticas.annotate(
        nome[:3],
        xy=(x_coluna, 1.0),
        xytext=(0, -ALTURA_CABECALHO_PONTOS),
        textcoords="offset points",
        xycoords="axes fraction",
        fontsize=8,
        fontweight="semibold",
        color=CORES_JOGADORES[nome],
        ha="center",
        va="top",
    )


def desenhar_linhas_sidebar(
    linhas,
    dados_por_jogador,
    deslocamento_inicial,
    *,
    cor_rotulo="#777777",
):
    deslocamento = deslocamento_inicial

    for rotulo, chave, formato in linhas:
        eixo_estatisticas.annotate(
            rotulo,
            xy=(0.0, 1.0),
            xytext=(0, -deslocamento),
            textcoords="offset points",
            xycoords="axes fraction",
            fontsize=7.1,
            color=cor_rotulo,
            ha="left",
            va="top",
        )

        for nome, x_coluna in zip(
            ORDEM_JOGADORES,
            posicoes_coluna_jogador,
        ):
            if chave == "saldo_inicial":
                valor = valores_iniciais[nome]
            else:
                valor = dados_por_jogador[nome][chave]

            eixo_estatisticas.annotate(
                formato.format(valor),
                xy=(x_coluna, 1.0),
                xytext=(0, -deslocamento),
                textcoords="offset points",
                xycoords="axes fraction",
                fontsize=7.1,
                color="#333333",
                ha="center",
                va="top",
                family="monospace",
            )

        deslocamento += ALTURA_LINHA_PONTOS

    return deslocamento


deslocamento_pontos = ALTURA_CABECALHO_PONTOS + 13

deslocamento_pontos = desenhar_linhas_sidebar(
    linhas_estatistica,
    estatisticas_jogadores,
    deslocamento_pontos,
)

# Título da seção de empréstimos.

deslocamento_pontos += 10

eixo_estatisticas.annotate(
    "Empréstimos por jogador",
    xy=(0.0, 1.0),
    xytext=(0, -deslocamento_pontos),
    textcoords="offset points",
    xycoords="axes fraction",
    fontsize=8.8,
    fontweight="bold",
    color="#1A1A1A",
    ha="left",
    va="top",
)

deslocamento_pontos += 19

desenhar_linhas_sidebar(
    linhas_emprestimos,
    emprestimos_jogadores,
    deslocamento_pontos,
)


# --- Rodapé ---

eixo_rodape.set_xlim(0, 1)
eixo_rodape.set_ylim(0, 1)

blocos_rodape = [
    (
        "Amplitude total",
        formatar_reais(estatisticas_gerais["amplitudeTotal"], 2),
    ),
    (
        "Valor máximo",
        formatar_reais(estatisticas_gerais["valorMaximo"], 2),
    ),
    (
        "Valor mínimo",
        formatar_reais(estatisticas_gerais["valorMinimo"], 2),
    ),
    (
        "Desvio padrão",
        formatar_reais(estatisticas_gerais["desvioPadrao"], 2),
    ),
    (
        "Média atual",
        formatar_reais(estatisticas_gerais["mediaAtual"], 2),
    ),
    (
        "Média histórica",
        formatar_reais(estatisticas_gerais["mediaHistorica"], 2),
    ),
]

n_blocos_rodape = len(blocos_rodape)

for indice_bloco, (rotulo, valor) in enumerate(blocos_rodape):
    x0 = indice_bloco / n_blocos_rodape * 0.84

    eixo_rodape.text(
        x0,
        0.55,
        rotulo,
        fontsize=7.8,
        color="#888888",
        ha="left",
        va="top",
    )

    eixo_rodape.text(
        x0,
        0.20,
        valor,
        fontsize=10.5,
        fontweight="bold",
        color="#333333",
        ha="left",
        va="top",
    )

eixo_rodape.text(
    1.0,
    0.15,
    (
        f"Empréstimos gerais: "
        f"{emprestimos_gerais['totalTomados']} tomados • "
        f"{emprestimos_gerais['totalPagos']} pagos • "
        f"{emprestimos_gerais['totalEmAberto']} em aberto"
    ),
    fontsize=8.5,
    color="#AAAAAA",
    ha="right",
    va="center",
)

if avisos:
    eixo_rodape.text(
        0.0,
        -0.03,
        "Avisos: " + " • ".join(str(aviso) for aviso in avisos),
        fontsize=8,
        color="#B26A00",
        ha="left",
        va="top",
        clip_on=False,
    )


plt.subplots_adjust(
    top=0.94,
    bottom=0.05,
    left=0.070,
    right=0.97,
)

gerenciador = figura.canvas.manager

if hasattr(gerenciador, "set_window_title"):
    gerenciador.set_window_title("Poker: Temporada")

try:
    gerenciador.window.state("zoomed")
except Exception:
    try:
        gerenciador.resize(*gerenciador.window.maxsize())
    except Exception:
        pass


plt.show()
