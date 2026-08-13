import { readFile, writeFile } from "node:fs/promises";

// Constantes da última rodada, rodada 2

const constants = {
    currentValues: {
        Apollo: 1490,
        Felipe: 255,
        Lucas: 155,
        Luiz: -600,
        Cassiano: 380,
    },

    dataPath: "./data/raw/game_2.txt",
    outputPath: "./data/processed/game_2.json",
};

const jsonData = {
    Apollo: [constants.currentValues.Apollo],
    Felipe: [constants.currentValues.Felipe],
    Lucas: [constants.currentValues.Lucas],
    Luiz: [constants.currentValues.Luiz],
    Cassiano: [constants.currentValues.Cassiano],
    media: [],
};

const names = Object.keys(constants.currentValues);

const content = await readFile(constants.dataPath, "utf-8");

const lines = content.trim().split(/\r?\n/);

function getLastValue(name) {
    const values = jsonData[name];

    return values[values.length - 1];
}

function insertNewValue(name, value) {
    jsonData[name].push(value + getLastValue(name));
}

function calculateMedia() {
    const sum = names.reduce((acc, name) => acc + getLastValue(name), 0);

    return Math.round((sum / names.length) * 100) / 100;
}

function insertMedia() {
    jsonData.media.push(calculateMedia());
}

function parseLine(line) {
    const values = line
        .trim()
        .split(/\s+/)
        .filter(Boolean)
        .map(Number);

    const parsedValues = values.slice(0, 5);

    while (parsedValues.length < 5) {
        parsedValues.push(0);
    }

    return parsedValues;
}

insertMedia();

for (const line of lines) {
    if (!line.trim()) {
        continue;
    }

    const processedLine = parseLine(line);

    for (const [index, name] of names.entries()) {
        insertNewValue(name, processedLine[index]);
    }

    insertMedia();
}

await writeFile(
    constants.outputPath,
    JSON.stringify(jsonData, null, 2),
    "utf-8"
);