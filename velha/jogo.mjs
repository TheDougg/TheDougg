// Jogo da velha do README. Lógica única, usada pelo Worker (clique) e pela Action (issue).
// O visitante é ❌; o bot é ⭕ e joga perfeito (minimax): o melhor resultado possível contra ele é empate.

export const REPO = "TheDougg/TheDougg";
export const WORKER = "https://velha-doug.douglas123.workers.dev";
export const INICIO = "<!-- VELHA:INICIO -->";
export const FIM = "<!-- VELHA:FIM -->";

const LINHAS = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]];

export function vencedor(tab) {
  for (const [a, b, c] of LINHAS) {
    if (tab[a] !== " " && tab[a] === tab[b] && tab[b] === tab[c]) return tab[a];
  }
  return tab.includes(" ") ? null : "empate";
}

// Nota para o bot (O): vitória rápida vale mais, derrota demorada perde menos.
export function minimax(tab, vez, prof = 0) {
  const v = vencedor(tab);
  if (v === "O") return 10 - prof;
  if (v === "X") return prof - 10;
  if (v === "empate") return 0;
  let melhor = vez === "O" ? -Infinity : Infinity;
  for (let i = 0; i < 9; i++) {
    if (tab[i] !== " ") continue;
    tab[i] = vez;
    const nota = minimax(tab, vez === "O" ? "X" : "O", prof + 1);
    tab[i] = " ";
    melhor = vez === "O" ? Math.max(melhor, nota) : Math.min(melhor, nota);
  }
  return melhor;
}

// Entre as jogadas de nota máxima, sorteia uma para o bot não ficar repetitivo.
export function jogadaDoBot(tab) {
  const notas = new Map();
  for (let i = 0; i < 9; i++) {
    if (tab[i] !== " ") continue;
    tab[i] = "O";
    notas.set(i, minimax(tab, "X", 1));
    tab[i] = " ";
  }
  const melhor = Math.max(...notas.values());
  const opcoes = [...notas].filter(([, n]) => n === melhor).map(([i]) => i);
  return opcoes[Math.floor(Math.random() * opcoes.length)];
}

export function novoEstado() {
  return { tabuleiro: Array(9).fill(" "), placar: { humanos: 0, bot: 0, empates: 0 },
           jogadas: 0, jogadores: {}, historico: [], ultimo_jogo: null };
}

function encerrar(estado, resultado, quem) {
  estado.placar[{ X: "humanos", O: "bot", empate: "empates" }[resultado]] += 1;
  estado.ultimo_jogo = { resultado, jogador: quem, tabuleiro: estado.tabuleiro };
  estado.tabuleiro = Array(9).fill(" ");
  return {
    X: `🏆 ${quem} venceu o bot! Isso não devia ser possível.`,
    O: "🤖 O bot venceu essa. Um novo jogo já começou.",
    empate: "🤝 Deu velha! Empate. Um novo jogo já começou.",
  }[resultado];
}

/** Aplica a jogada do visitante (casa 1–9) e a resposta do bot. jogador = login do GitHub ou null (anônimo). */
export function jogar(estado, casa, jogador) {
  const i = casa - 1;
  if (!Number.isInteger(casa) || i < 0 || i > 8) return { mudou: false, msg: "Casa inválida. Use o tabuleiro do README." };
  const tab = estado.tabuleiro;
  if (tab[i] !== " ") return { mudou: false, msg: `A casa ${casa} já está ocupada. Volta no README e escolhe outra!` };

  const quem = jogador ? `@${jogador}` : "alguém";
  tab[i] = "X";
  estado.jogadas += 1;
  if (jogador) estado.jogadores[jogador] = (estado.jogadores[jogador] ?? 0) + 1;
  let registro = `${quem} ❌ casa ${casa}`;
  let resultado = vencedor(tab);
  let msg;
  if (resultado) {
    msg = encerrar(estado, resultado, quem);
  } else {
    const bot = jogadaDoBot(tab);
    tab[bot] = "O";
    registro += ` · bot ⭕ casa ${bot + 1}`;
    resultado = vencedor(tab);
    msg = resultado ? encerrar(estado, resultado, quem)
      : `✅ Você jogou na casa ${casa} e o bot respondeu na casa ${bot + 1}. Sua vez de novo!`;
  }
  const quando = new Date().toLocaleString("pt-BR", { timeZone: "America/Sao_Paulo", day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }).replace(",", "");
  estado.historico = [`${quando} — ${registro}`, ...estado.historico.slice(0, 4)];
  return { mudou: true, msg };
}

function linkIssue(i) {
  const corpo = "Só clicar em **Create** 👇 — o bot joga em uns 20 segundos e atualiza o README.\n\n" +
                "Just hit **Create** — the bot moves in ~20s and updates the README.";
  return `https://github.com/${REPO}/issues/new?title=${encodeURIComponent(`velha|${i + 1}`)}&body=${encodeURIComponent(corpo)}`;
}

function tabuleiroHtml(tab, clicavel) {
  const linhas = [];
  for (let r = 0; r < 3; r++) {
    const celulas = [];
    for (let i = r * 3; i < r * 3 + 3; i++) {
      if (tab[i] === "X") celulas.push('<td><img src="assets/velha/x.svg" width="72" alt="X"></td>');
      else if (tab[i] === "O") celulas.push('<td><img src="assets/velha/o.svg" width="72" alt="O"></td>');
      else if (clicavel) celulas.push(`<td><a href="${WORKER}/jogar?casa=${i + 1}"><img src="assets/velha/vazio.svg" width="72" alt="casa ${i + 1}"></a></td>`);
      else celulas.push('<td><img src="assets/velha/vazio.svg" width="72" alt="vazia"></td>');
    }
    linhas.push(`<tr>${celulas.join("")}</tr>`);
  }
  return `<table align="center">${linhas.join("")}</table>`;
}

export function bloco(estado) {
  const p = estado.placar;
  const top = Object.entries(estado.jogadores).sort((a, b) => b[1] - a[1]).slice(0, 5)
    .map(([u, n]) => `[@${u}](https://github.com/${u}) (${n})`).join(" · ") || "ninguém ainda — seja a primeira pessoa!";
  const hist = estado.historico.map((h) => `- ${h}`).join("\n") || "- nenhuma jogada ainda";
  const livres = estado.tabuleiro.map((c, i) => (c === " " ? `[${i + 1}](${linkIssue(i)})` : null)).filter(Boolean).join(" · ");
  let ultimo = "";
  if (estado.ultimo_jogo) {
    const u = estado.ultimo_jogo;
    const txt = { X: `${u.jogador} venceu 🏆`, O: "o bot venceu 🤖", empate: "deu velha 🤝" }[u.resultado];
    ultimo = `\n<details><summary>Último jogo: ${txt}</summary>\n\n${tabuleiroHtml(u.tabuleiro, false)}\n\n</details>\n`;
  }
  return `${INICIO}
<p align="center"><b>Você é ❌. Clique numa casa vazia</b> e pronto: o bot responde ⭕ e o tabuleiro atualiza na hora.<br>
<sub>O bot joga perfeito (minimax): o melhor que dá pra tirar dele é empate. · <i>You're ❌. Click a square; the bot plays perfectly.</i></sub></p>

${tabuleiroHtml(estado.tabuleiro, true)}

<p align="center">
<img src="https://img.shields.io/badge/humanos-${p.humanos}-00c853?style=for-the-badge" alt="humanos">
<img src="https://img.shields.io/badge/empates-${p.empates}-30363d?style=for-the-badge" alt="empates">
<img src="https://img.shields.io/badge/bot-${p.bot}-22d3ee?style=for-the-badge" alt="bot">
</p>
${ultimo}
<details><summary>🏅 Jogar com meu @ (entra no ranking) · últimas jogadas</summary>

Pelo clique a jogada é anônima. Para aparecer no ranking, jogue por uma issue escolhendo a casa: ${livres}

**Top jogadores:** ${top}

${hist}

<sub>${estado.jogadas} jogadas no total.</sub>
</details>
${FIM}`;
}

export function atualizarReadme(texto, estado) {
  const ini = texto.indexOf(INICIO);
  const fim = texto.indexOf(FIM) + FIM.length;
  return texto.slice(0, ini) + bloco(estado) + texto.slice(fim);
}
