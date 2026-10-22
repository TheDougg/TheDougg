"""Jogo da velha do README: o visitante joga ❌ por issue, o bot responde ⭕ na hora.

Variáveis de ambiente: TITULO (título da issue, ex. "velha|5"), JOGADOR (login).
Grava data/velha.json, reescreve o bloco do README e deixa a resposta em resposta.md.
Sem argumentos, só redesenha o README a partir do estado atual.
"""
import json
import os
import random
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

RAIZ = Path(__file__).resolve().parent.parent
ESTADO = RAIZ / "data" / "velha.json"
README = RAIZ / "README.md"
RESPOSTA = RAIZ / "resposta.md"
REPO = os.environ.get("GITHUB_REPOSITORY", "TheDougg/TheDougg")
CHANCE_DE_ERRO = 1 / 6  # o bot é minimax, mas às vezes se distrai
LINHAS = [(0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6)]
INICIO, FIM = "<!-- VELHA:INICIO -->", "<!-- VELHA:FIM -->"


def vencedor(tab):
    for a, b, c in LINHAS:
        if tab[a] != " " and tab[a] == tab[b] == tab[c]:
            return tab[a]
    return "empate" if " " not in tab else None


def minimax(tab, vez):
    v = vencedor(tab)
    if v == "O":
        return 1, None
    if v == "X":
        return -1, None
    if v == "empate":
        return 0, None
    melhor = (-2, None) if vez == "O" else (2, None)
    for i in [i for i, c in enumerate(tab) if c == " "]:
        tab[i] = vez
        nota, _ = minimax(tab, "X" if vez == "O" else "O")
        tab[i] = " "
        if (vez == "O" and nota > melhor[0]) or (vez == "X" and nota < melhor[0]):
            melhor = (nota, i)
    return melhor


def jogada_do_bot(tab):
    livres = [i for i, c in enumerate(tab) if c == " "]
    if random.random() < CHANCE_DE_ERRO:
        return random.choice(livres)
    return minimax(tab, "O")[1]


def novo_estado():
    return {"tabuleiro": [" "] * 9, "placar": {"humanos": 0, "bot": 0, "empates": 0},
            "jogadas": 0, "jogadores": {}, "historico": [], "ultimo_jogo": None}


def encerrar(estado, resultado, jogador):
    chave = {"X": "humanos", "O": "bot", "empate": "empates"}[resultado]
    estado["placar"][chave] += 1
    estado["ultimo_jogo"] = {"resultado": resultado, "jogador": jogador, "tabuleiro": estado["tabuleiro"]}
    estado["tabuleiro"] = [" "] * 9
    return {"X": f"🏆 **@{jogador} venceu o bot!** Raríssimo. Seu nome entrou pro placar.",
            "O": "🤖 O bot venceu essa. Um novo jogo já começou — tenta de novo?",
            "empate": "🤝 Deu velha! Empate. Um novo jogo já começou."}[resultado]


def jogar(estado, titulo, jogador):
    m = re.fullmatch(r"\s*velha\|([1-9])\s*", titulo or "")
    if not m:
        return False, "Não entendi a jogada. Use os links do tabuleiro no README 🙂"
    casa = int(m.group(1)) - 1
    tab = estado["tabuleiro"]
    if tab[casa] != " ":
        return False, f"A casa {casa + 1} já está ocupada — alguém jogou antes de você. Volta no README e escolhe outra!"

    tab[casa] = "X"
    estado["jogadas"] += 1
    estado["jogadores"][jogador] = estado["jogadores"].get(jogador, 0) + 1
    registro = f"@{jogador} ❌ casa {casa + 1}"
    resultado = vencedor(tab)
    if resultado:
        msg = encerrar(estado, resultado, jogador)
    else:
        bot = jogada_do_bot(tab)
        tab[bot] = "O"
        registro += f" · bot ⭕ casa {bot + 1}"
        resultado = vencedor(tab)
        msg = encerrar(estado, resultado, jogador) if resultado else \
            f"✅ Você jogou na casa {casa + 1} e o bot respondeu na casa {bot + 1}. Sua vez de novo (ou de outra pessoa)!"
    quando = datetime.now(timezone.utc).strftime("%d/%m %H:%M")
    estado["historico"] = [f"{quando} — {registro}"] + estado["historico"][:4]
    return True, msg


def link(casa):
    titulo = quote(f"velha|{casa + 1}")
    corpo = quote("Só clicar em **Create** 👇 — o bot joga em uns 20 segundos e atualiza o README.\n\n"
                  "Just hit **Create** — the bot moves in ~20s and updates the README.")
    return f"https://github.com/{REPO}/issues/new?title={titulo}&body={corpo}"


def tabuleiro_html(tab, clicavel):
    linhas = []
    for r in range(3):
        celulas = []
        for i in range(r * 3, r * 3 + 3):
            if tab[i] == "X":
                celulas.append('<td><img src="assets/velha/x.svg" width="72" alt="X"></td>')
            elif tab[i] == "O":
                celulas.append('<td><img src="assets/velha/o.svg" width="72" alt="O"></td>')
            elif clicavel:
                celulas.append(f'<td><a href="{link(i)}"><img src="assets/velha/vazio.svg" width="72" alt="casa {i + 1}"></a></td>')
            else:
                celulas.append('<td><img src="assets/velha/vazio.svg" width="72" alt="vazia"></td>')
        linhas.append("<tr>" + "".join(celulas) + "</tr>")
    return '<table align="center">' + "".join(linhas) + "</table>"


def bloco(estado):
    p = estado["placar"]
    top = sorted(estado["jogadores"].items(), key=lambda kv: -kv[1])[:5]
    top_md = " · ".join(f"[@{u}](https://github.com/{u}) ({n})" for u, n in top) or "ninguém ainda — seja a primeira pessoa!"
    hist = "\n".join(f"- {h}" for h in estado["historico"]) or "- nenhuma jogada ainda"
    ultimo = ""
    if estado["ultimo_jogo"]:
        u = estado["ultimo_jogo"]
        txt = {"X": f"@{u['jogador']} venceu 🏆", "O": "o bot venceu 🤖", "empate": "deu velha 🤝"}[u["resultado"]]
        ultimo = f"\n<details><summary>Último jogo: {txt}</summary>\n\n{tabuleiro_html(u['tabuleiro'], False)}\n\n</details>\n"
    return f"""{INICIO}
<p align="center"><b>Você é ❌. Clique numa casa vazia</b> → o GitHub abre uma issue → clique em <b>Create</b> → o bot (minimax, que às vezes se distrai) responde ⭕ e o README se atualiza.<br>
<sub>You're ❌. Click an empty square, hit <b>Create</b> on the issue, and the bot replies ⭕ in ~20s.</sub></p>

{tabuleiro_html(estado["tabuleiro"], True)}

<p align="center">
<img src="https://img.shields.io/badge/humanos-{p['humanos']}-8b5cf6?style=for-the-badge" alt="humanos">
<img src="https://img.shields.io/badge/empates-{p['empates']}-30363d?style=for-the-badge" alt="empates">
<img src="https://img.shields.io/badge/bot-{p['bot']}-22d3ee?style=for-the-badge" alt="bot">
</p>
{ultimo}
<details><summary>🏅 Quem mais jogou · últimas jogadas</summary>

**Top jogadores:** {top_md}

{hist}

<sub>{estado["jogadas"]} jogadas no total.</sub>
</details>
{FIM}"""


def main():
    estado = json.loads(ESTADO.read_text(encoding="utf-8")) if ESTADO.exists() else novo_estado()
    mudou, msg = True, ""
    if os.environ.get("TITULO"):
        mudou, msg = jogar(estado, os.environ["TITULO"], os.environ.get("JOGADOR", "anônimo"))
    if mudou:
        ESTADO.write_text(json.dumps(estado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        texto = README.read_text(encoding="utf-8")
        ini, fim = texto.index(INICIO), texto.index(FIM) + len(FIM)
        README.write_text(texto[:ini] + bloco(estado) + texto[fim:], encoding="utf-8")
    RESPOSTA.write_text(msg + f"\n\n[← Voltar pro perfil](https://github.com/{REPO.split('/')[0]})\n", encoding="utf-8")
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write(f"mudou={'true' if mudou else 'false'}\n")


if __name__ == "__main__":
    main()
