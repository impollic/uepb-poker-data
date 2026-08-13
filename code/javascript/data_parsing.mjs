import { readFile, writeFile } from "node:fs/promises";
import { mean, median, min, max, sampleStandardDeviation } from "simple-statistics";

// CONFIG

const CONFIG = {
  valoresIniciais: {
    Apollo: 400,
    Felipe: 400,
    Lucas: 400,
    Luiz: 400,
    Cassiano: 400,
    Wanderson: 400,
  },
  caminhoEntrada: "./data/raw/temporada.txt",
  caminhoSaida: "./data/processed/temporada.json",
};

const JOGADORES = Object.keys(CONFIG.valoresIniciais);
const TOTAL_JOGADORES = JOGADORES.length;

class ErroProcessamento extends Error {
  constructor(mensagem, contexto = {}) {
    super(mensagem);
    this.name = "ErroProcessamento";
    this.contexto = contexto;
  }
}

function arredondar(valor, casas = 2) {
  if (typeof valor !== "number" || Number.isNaN(valor)) {
    throw new ErroProcessamento(`arredondar() recebeu valor não numérico: ${valor}`);
  }
  const fator = 10 ** casas;
  return Math.round(valor * fator) / fator;
}

function desvioPadraoAmostral(valores) {
  if (!Array.isArray(valores) || valores.length < 2) return 0;
  return sampleStandardDeviation(valores);
}

// ESTATÍSTICAS DESCRITIVAS DE UMA SÉRIE (tipo, saldo de um jogador ao longo do tempo)

function calcularEstatisticasDaSerie(valores) {
  if (!Array.isArray(valores) || valores.length === 0) {
    throw new ErroProcessamento("calcularEstatisticasDaSerie() recebeu uma série vazia.");
  }

  const minimo = min(valores);
  const maximo = max(valores);

  return {
    media: arredondar(mean(valores)),
    mediana: arredondar(median(valores)),
    minimo,
    maximo,
    amplitude: maximo - minimo,
    desvioPadrao: arredondar(desvioPadraoAmostral(valores)),
    saldoFinal: valores[valores.length - 1],
    totalRodadas: valores.length,
  };
}

// DIVISÃO DO ARQUIVO BRUTO EM JOGOS
// linhas compostas por "------" são consideradas separadores de jogos, linhas em branco são ignoradas

function dividirEmJogos(conteudo) {
  if (typeof conteudo !== "string" || !conteudo.trim()) {
    throw new ErroProcessamento("Arquivo de entrada está vazio.");
  }

  const EH_LINHA_DE_SEPARACAO = (linha) => /^-+$/.test(linha.trim());
  const linhas = conteudo.trim().split(/\r?\n/);
  const jogos = [[]];

  for (const linhaBruta of linhas) {
    const linha = linhaBruta.trim();
    if (!linha) continue;

    if (EH_LINHA_DE_SEPARACAO(linha)) {
      jogos.push([]);
      continue;
    }

    jogos[jogos.length - 1].push(linha);
  }

  return jogos.filter((jogo) => jogo.length > 0);
}

// PARSING

function parsearLinha(linha, jogo, rodada) {
  try {
    const brutos = linha
      .split(/\s+/)
      .filter(Boolean)
      .map((token) => {
        const numero = Number(token);
        if (Number.isNaN(numero)) {
          console.warn(
            `Jogo ${jogo}, rodada ${rodada}: token inválido "${token}" tratado como 0.`
          );
          return 0;
        }
        return numero;
      });

    if (brutos.length > TOTAL_JOGADORES) {
      console.warn(
        `Jogo ${jogo}, rodada ${rodada}: ${brutos.length} valores para ${TOTAL_JOGADORES} jogadores. Excedente ignorado.`
      );
    }

    const valores = brutos.slice(0, TOTAL_JOGADORES);
    while (valores.length < TOTAL_JOGADORES) valores.push(0);

    return valores;
  } catch (erro) {
    console.error(`Erro em parsearLinha() [jogo ${jogo}, rodada ${rodada}]: ${erro.message}`);
    // linha ilegível vira rodada neutra (todos 0) em vez de derrubar a temporada inteira
    return new Array(TOTAL_JOGADORES).fill(0);
  }
}

// VALIDAÇÃO DE SOMA DA LINHA

// Regras:
//   - soma === 0                              → rodada NORMAL.
//   - soma !== 0 e exatamente 1 valor não-zero → EMPRÉSTIMO/PAGAMENTO válido
//     (o dinheiro extra tem origem clara: um único jogador tomou ou pagou).
//   - soma !== 0 e 2+ valores não-zero         → SUSPEITO. Isso não é um
//     padrão de empréstimo válido, é muito provavelmente erro de digitação
//     (ex: alguém digitou 130 em vez de -130 numa coluna). Não é silenciado:
//     entra no relatório de avisos para revisão manual.

function validarLinha(deltas, jogo, rodada, linhaOriginal) {
  const soma = deltas.reduce((acc, v) => acc + v, 0);
  const naoZerados = deltas.filter((v) => v !== 0);

  if (soma === 0) {
    return { tipo: "normal", soma };
  }

  if (naoZerados.length === 1) {
    return { tipo: "emprestimo", soma };
  }

  return {
    tipo: "suspeita",
    soma,
    detalhe: {
      jogo,
      rodada,
      linhaOriginal,
      somaObtida: soma,
      somaEsperada: 0,
      valoresNaoZerados: naoZerados.length,
    },
  };
}

function criarRastreadorDeEmprestimos() {
  const porJogador = Object.fromEntries(
    JOGADORES.map((nome) => [nome, { tomados: [], pagos: [], emAberto: [] }])
  );

  function registrarTomada(nome, valor, jogo, rodada) {
    const emprestimo = { valor: Math.abs(valor), jogo, rodada };
    porJogador[nome].tomados.push(emprestimo);
    porJogador[nome].emAberto.push(emprestimo);
  }

  function registrarPagamento(nome, valor, jogo, rodada) {
    const registro = porJogador[nome];

    if (registro.emAberto.length === 0) {
      console.warn(
        `${nome} pagou ${valor} no jogo ${jogo}, rodada ${rodada}, mas não há empréstimo em aberto registrado.`
      );
    }

    // tenta casar por valor exato; se não achar, usa o mais antigo (FIFO)
    const indiceCorrespondente = registro.emAberto.findIndex((e) => e.valor === valor);
    const indice = indiceCorrespondente !== -1 ? indiceCorrespondente : 0;
    const [emprestimoQuitado] = registro.emAberto.splice(indice, 1);

    registro.pagos.push({
      valor,
      jogo,
      rodada,
      tomadoNoJogo: emprestimoQuitado?.jogo ?? null,
      tomadoNaRodada: emprestimoQuitado?.rodada ?? null,
    });
  }

  function processarLinha(deltas, jogo, rodada) {
    deltas.forEach((valor, indice) => {
      if (valor === 0) return;

      const nome = JOGADORES[indice];
      valor < 0
        ? registrarTomada(nome, valor, jogo, rodada)
        : registrarPagamento(nome, valor, jogo, rodada);
    });
  }

  function gerarResumo() {
    const porJogadorResumo = {};
    const totais = { totalTomados: 0, totalPagos: 0, totalEmAberto: 0 };

    for (const nome of JOGADORES) {
      const { tomados, pagos, emAberto } = porJogador[nome];

      porJogadorResumo[nome] = {
        totalTomados: tomados.length,
        totalPagos: pagos.length,
        totalEmAberto: emAberto.length,
        historico: { tomados, pagos },
      };

      totais.totalTomados += tomados.length;
      totais.totalPagos += pagos.length;
      totais.totalEmAberto += emAberto.length;
    }

    return { porJogador: porJogadorResumo, geral: totais };
  }

  return { processarLinha, gerarResumo };
}

function processarTemporada(conteudo) {
  const blocos = dividirEmJogos(conteudo);
  const emprestimos = criarRastreadorDeEmprestimos();
  const avisos = [];

  const saldoAtual = { ...CONFIG.valoresIniciais };
  const saldos = Object.fromEntries(JOGADORES.map((nome) => [nome, [saldoAtual[nome]]]));

  // média DO MOMENTO, rodada a rodada — é essa série que alimenta o gráfico
  // e cujo último ponto representa o estado atual da temporada.
  const mediaPorRodada = [arredondar(mean(Object.values(saldoAtual)))];

  const jogos = [];
  let rodadaGlobal = 0;

  blocos.forEach((linhasDoJogo, indiceJogo) => {
    const numeroJogo = indiceJogo + 1;
    const indiceInicial = rodadaGlobal;

    linhasDoJogo.forEach((linha, indiceRodada) => {
      try {
        const numeroRodada = indiceRodada + 1;
        const deltas = parsearLinha(linha, numeroJogo, numeroRodada);
        const validacao = validarLinha(deltas, numeroJogo, numeroRodada, linha);

        if (validacao.tipo === "emprestimo") {
          emprestimos.processarLinha(deltas, numeroJogo, numeroRodada);
        }

        if (validacao.tipo === "suspeita") {
          console.warn(
            `Jogo ${numeroJogo}, rodada ${numeroRodada}: soma = ${validacao.soma} (esperado 0). ` +
              `Provável erro de digitação — linha: "${linha}"`
          );
          avisos.push(validacao.detalhe);
        }

        JOGADORES.forEach((nome, indice) => {
          saldoAtual[nome] += deltas[indice];
          saldos[nome].push(saldoAtual[nome]);
        });

        mediaPorRodada.push(arredondar(mean(Object.values(saldoAtual))));
        rodadaGlobal += 1;
      } catch (erro) {
        // erro numa rodada específica não deve derrubar a temporada inteira
        console.error(
          `Falha ao processar jogo ${numeroJogo}, linha "${linha}": ${erro.message}`
        );
      }
    });

    jogos.push({
      numero: numeroJogo,
      totalRodadas: linhasDoJogo.length,
      indiceInicial,
      indiceFinal: rodadaGlobal,
    });
  });

  return { saldos, mediaPorRodada, jogos, emprestimos, avisos };
}

function calcularEstatisticasGlobais(saldos, mediaPorRodada) {
  const porJogador = Object.fromEntries(
    JOGADORES.map((nome) => [nome, calcularEstatisticasDaSerie(saldos[nome])])
  );

  const todosOsValores = Object.values(saldos).flat();
  const minimoGeral = min(todosOsValores);
  const maximoGeral = max(todosOsValores);

  const geral = {
    mediaAtual: mediaPorRodada[mediaPorRodada.length - 1],
    mediaHistorica: arredondar(mean(todosOsValores)),
    valorMinimo: minimoGeral,
    valorMaximo: maximoGeral,
    amplitudeTotal: maximoGeral - minimoGeral,
    desvioPadrao: arredondar(desvioPadraoAmostral(todosOsValores)),
  };

  return { porJogador, geral };
}

async function executar() {
  let conteudo;
  try {
    conteudo = await readFile(CONFIG.caminhoEntrada, "utf-8");
  } catch (erro) {
    console.error(`Não foi possível ler o arquivo de entrada "${CONFIG.caminhoEntrada}": ${erro.message}`);
    throw erro;
  }

  const { saldos, mediaPorRodada, jogos, emprestimos, avisos } = processarTemporada(conteudo);

  const jsonFinal = {
    jogadores: JOGADORES,
    valoresIniciais: CONFIG.valoresIniciais,
    jogos,
    saldos,
    media: mediaPorRodada,
    estatisticas: calcularEstatisticasGlobais(saldos, mediaPorRodada),
    emprestimos: emprestimos.gerarResumo(),
    avisos,
  };

  try {
    await writeFile(CONFIG.caminhoSaida, JSON.stringify(jsonFinal, null, 2), "utf-8");
  } catch (erro) {
    console.error(`Não foi possível escrever o arquivo de saída "${CONFIG.caminhoSaida}": ${erro.message}`);
    throw erro;
  }

  console.log(
    `Temporada processada: ${jogos.length} jogo(s), ${mediaPorRodada.length - 1} rodada(s) no total.`
  );

  if (avisos.length > 0) {
    console.warn(`${avisos.length} linha(s) suspeita(s) — revise o campo "avisos" no JSON gerado.`);
  }
}

executar();
