// Jogada vinda de issue (GitHub Action). Env: TITULO ("velha|5"), JOGADOR (login).
// Sem TITULO, só redesenha o bloco do README a partir do estado atual.
import { existsSync, readFileSync, writeFileSync } from "node:fs";
import { atualizarReadme, jogar, novoEstado, REPO } from "../velha/jogo.mjs";

const ESTADO = "data/velha.json";
const estado = existsSync(ESTADO) ? JSON.parse(readFileSync(ESTADO, "utf8")) : novoEstado();
let resultado = { mudou: true, msg: "" };

if (process.env.TITULO) {
  const m = process.env.TITULO.trim().match(/^velha\|([1-9])$/);
  resultado = m ? jogar(estado, Number(m[1]), process.env.JOGADOR || null)
    : { mudou: false, msg: "Não entendi a jogada. Use os links do tabuleiro no README 🙂" };
}
if (resultado.mudou) {
  writeFileSync(ESTADO, JSON.stringify(estado, null, 2) + "\n");
  writeFileSync("README.md", atualizarReadme(readFileSync("README.md", "utf8"), estado));
}
writeFileSync("resposta.md", `${resultado.msg}\n\n[← Voltar pro perfil](https://github.com/${REPO.split("/")[0]})\n`);
