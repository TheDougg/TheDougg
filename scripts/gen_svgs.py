"""Gera os SVGs animados do perfil (assets/). Rode: python scripts/gen_svgs.py"""
from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"
VIOLETA, CIANO = "#8b5cf6", "#22d3ee"
FONT_MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
FONT_SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

TEMAS = {
    "dark": dict(bg="#0d1117", card="#161b22", borda="#30363d", texto="#e6edf3",
                 suave="#8b949e", token=CIANO, acento=VIOLETA),
    "light": dict(bg="#ffffff", card="#f6f8fa", borda="#d0d7de", texto="#1f2328",
                  suave="#57606a", token="#7c3aed", acento="#7c3aed"),
}


def salvar(nome, conteudo):
    ASSETS.joinpath(nome).parent.mkdir(parents=True, exist_ok=True)
    ASSETS.joinpath(nome).write_text(conteudo, encoding="utf-8")


def gradiente_girando(gid, cores, dur=6):
    stops = "".join(f'<stop offset="{i / (len(cores) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(cores))
    return (f'<linearGradient id="{gid}" gradientUnits="objectBoundingBox">{stops}'
            f'<animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" '
            f'dur="{dur}s" repeatCount="indefinite"/></linearGradient>')


# ---------------------------------------------------------------- terminal

def terminal():
    T = 20.0          # ciclo completo (s)
    cw = 9.0          # largura aproximada de um caractere (px) a 15px
    dt = 0.055        # tempo por caractere digitado
    x0, y0, lh = 28, 78, 25
    prompt = "doug@github:~$ "
    roteiro = [
        ("cmd", "whoami"),
        ("out", [("Douglas Henrique", "#e6edf3", True), (" (Doug) · dev full stack · Brasil", "#8b949e", False)]),
        ("cmd", "cat stack.txt"),
        ("out", [("TypeScript · React · Node.js · Prisma · Python · Java · Camunda", "#67e8f9", False)]),
        ("cmd", "ls ~/projetos"),
        ("out", [("simulai-academy/   datalock/   dividiu/   camunda-plugins/", "#a78bfa", True)]),
        ("cmd", "cat foco.txt"),
        ("out", [("IA aplicada à educação · automação de processos · produto que vira negócio", "#e6edf3", False)]),
        ("end", None),
    ]

    defs, corpo, t = [], [], 0.6
    for i, (tipo, dado) in enumerate(roteiro):
        y = y0 + i * lh
        cid = f"c{i}"
        if tipo == "cmd":
            pts = [(0, 0), (t, len(prompt) * cw)]
            t += 0.35
            for k in range(1, len(dado) + 1):
                pts.append((t, (len(prompt) + k) * cw))
                t += dt
            pts.append((t, 900))
            t += 0.35
        elif tipo == "out":
            pts = [(0, 0), (t, 900)]
            t += 0.9
        else:
            pts = [(0, 0), (t, 900)]
        kt = ";".join(f"{p / T:.4f}" for p, _ in pts) + ";1"
        vals = ";".join(f"{w:.0f}" for _, w in pts) + f";{pts[-1][1]:.0f}"
        defs.append(f'<clipPath id="{cid}"><rect x="{x0 - 4}" y="{y - 18}" height="{lh}" width="0">'
                    f'<animate attributeName="width" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
                    f'keyTimes="{kt}" values="{vals}"/></rect></clipPath>')
        if tipo in ("cmd", "end"):
            cmd = escape(dado or "")
            cursor = (f'<tspan fill="{CIANO}">▋<animate attributeName="fill-opacity" values="1;1;0;0" '
                      f'keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></tspan>') if tipo == "end" else ""
            corpo.append(
                f'<text x="{x0}" y="{y}" clip-path="url(#{cid})"><tspan fill="#3fb950" font-weight="700">doug@github</tspan>'
                f'<tspan fill="#8b949e">:</tspan><tspan fill="#58a6ff" font-weight="700">~</tspan>'
                f'<tspan fill="#8b949e">$ </tspan><tspan fill="#e6edf3">{cmd}</tspan>{cursor}</text>')
        else:
            spans = "".join(f'<tspan fill="{c}"{" font-weight=\"700\"" if b else ""}>{escape(s)}</tspan>' for s, c, b in dado)
            corpo.append(f'<text x="{x0}" y="{y}" clip-path="url(#{cid})">{spans}</text>')

    h = y0 + len(roteiro) * lh + 10
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {h}" width="900" height="{h}" role="img" aria-label="Terminal: Douglas Henrique (Doug), dev full stack">
<defs>{gradiente_girando("borda", [VIOLETA, CIANO, "#3fb950", VIOLETA], 8)}{"".join(defs)}</defs>
<rect x="2" y="2" width="896" height="{h - 4}" rx="14" fill="#0d1117" stroke="url(#borda)" stroke-width="2"/>
<rect x="3" y="3" width="894" height="36" rx="13" fill="#161b22"/>
<rect x="3" y="26" width="894" height="13" fill="#161b22"/>
<circle cx="26" cy="21" r="6" fill="#ff5f56"/><circle cx="46" cy="21" r="6" fill="#ffbd2e"/><circle cx="66" cy="21" r="6" fill="#27c93f"/>
<text x="450" y="25" text-anchor="middle" font-family="{FONT_MONO}" font-size="13" fill="#8b949e">doug@github: ~ — zsh</text>
<g font-family="{FONT_MONO}" font-size="15" xml:space="preserve">{"".join(corpo)}</g>
</svg>'''
    salvar("terminal.svg", svg)


# ---------------------------------------------------------------- fluxo BPMN

def fluxo(tema):
    c = TEMAS[tema]

    def tarefa(x, y, w, h, linhas, tag=None):
        meio = y + h / 2 - (len(linhas) - 1) * 8 + 5
        txt = "".join(f'<text x="{x + w / 2}" y="{meio + i * 16}" text-anchor="middle">{escape(l)}</text>'
                      for i, l in enumerate(linhas))
        marca = f'<text x="{x + 8}" y="{y + 15}" font-size="10" fill="{c["acento"]}">{tag}</text>' if tag else ""
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{c["card"]}" '
                f'stroke="{c["suave"]}" stroke-width="1.6"/>{marca}{txt}')

    def gateway(cx, cy, simbolo):
        return (f'<path d="M{cx} {cy - 25} L{cx + 25} {cy} L{cx} {cy + 25} L{cx - 25} {cy} Z" fill="{c["card"]}" '
                f'stroke="{c["suave"]}" stroke-width="1.6"/>'
                f'<text x="{cx}" y="{cy + 7}" text-anchor="middle" font-size="20" font-weight="700" fill="{c["suave"]}">{simbolo}</text>')

    seta = f'stroke="{c["suave"]}" stroke-width="1.6" fill="none" marker-end="url(#seta)"'
    fluxos = ["M58 130 H78", "M200 130 H233", "M355 130 H383", "M410 105 V68 H458", "M410 155 V192 H458",
              "M600 68 H650 V103", "M600 192 H650 V157", "M675 130 H698", "M820 130 H840"]
    caminho_a = "M40 130 H410 V68 H650 V130 H858"
    caminho_b = "M40 130 H410 V192 H650 V130 H858"

    def token(caminho, ativo_em_cima):
        kp = "0;1;1" if ativo_em_cima else "0;0;1"
        op = "1;0" if ativo_em_cima else "0;1"
        return (f'<g><animate attributeName="opacity" dur="12s" repeatCount="indefinite" calcMode="discrete" '
                f'keyTimes="0;.5" values="{op}"/>'
                f'<circle r="13" fill="{c["token"]}" opacity=".25"><animate attributeName="r" values="9;15;9" dur="1.2s" repeatCount="indefinite"/></circle>'
                f'<circle r="7" fill="{c["token"]}"/>'
                f'<animateMotion dur="12s" repeatCount="indefinite" path="{caminho}" keyPoints="{kp}" keyTimes="0;.5;1" calcMode="linear"/></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260" width="900" height="260" role="img" aria-label="Fluxo BPMN de como eu trabalho">
<defs><marker id="seta" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{c["suave"]}"/></marker></defs>
<g font-family="{FONT_SANS}" font-size="13" fill="{c["texto"]}">
<circle cx="40" cy="130" r="18" fill="{c["card"]}" stroke="{c["suave"]}" stroke-width="1.6"/>
<text x="40" y="172" text-anchor="middle" font-size="12" fill="{c["suave"]}">problema real</text>
{tarefa(80, 100, 120, 60, ["Entender", "o processo"])}
{tarefa(235, 100, 120, 60, ["Desenhar", "a solução"])}
<text x="295" y="178" text-anchor="middle" font-size="11" font-weight="600" fill="{c["acento"]}" letter-spacing=".6">BPMN · DMN</text>
{gateway(410, 130, "×")}
<text x="444" y="127" font-size="12" fill="{c["suave"]}">dá pra</text>
<text x="444" y="142" font-size="12" fill="{c["suave"]}">automatizar?</text>
<text x="420" y="60" font-size="11" fill="{c["acento"]}">sim</text>
<text x="420" y="210" font-size="11" fill="{c["acento"]}">não</text>
{tarefa(460, 40, 140, 56, ["Automatizar", "com Camunda"])}
{tarefa(460, 164, 140, 56, ["Construir produto", "React + Node"])}
{gateway(650, 130, "×")}
{tarefa(700, 100, 120, 60, ["Entregar", "e medir"])}
<circle cx="858" cy="130" r="18" fill="{c["card"]}" stroke="{c["texto"]}" stroke-width="4"/>
<text x="858" y="172" text-anchor="middle" font-size="12" fill="{c["suave"]}">usuário feliz</text>
{"".join(f'<path d="{d}" {seta}/>' for d in fluxos)}
{token(caminho_a, True)}{token(caminho_b, False)}
</g></svg>'''
    salvar(f"fluxo-{tema}.svg", svg)


# ---------------------------------------------------------------- cards

def quebrar(texto, largura):
    linhas, atual = [], ""
    for p in texto.split():
        if len(atual) + len(p) + 1 > largura and atual:
            linhas.append(atual)
            atual = p
        else:
            atual = f"{atual} {p}".strip()
    return linhas + [atual]


def card(nome, tema, titulo, tag, descricao, rodape, cores):
    c = TEMAS[tema]
    linhas = quebrar(descricao, 36)
    desc = "".join(f'<text x="22" y="{92 + i * 18}" font-size="13" fill="{c["suave"]}">{escape(l)}</text>'
                   for i, l in enumerate(linhas[:3]))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 170" width="300" height="170" role="img" aria-label="{escape(titulo)}">
<defs>{gradiente_girando("b", cores + [cores[0]], 5)}
<linearGradient id="ic" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{cores[0]}"/><stop offset="1" stop-color="{cores[1]}"/></linearGradient></defs>
<rect x="1.5" y="1.5" width="297" height="167" rx="16" fill="{c["bg"]}" stroke="url(#b)" stroke-width="2"/>
<g font-family="{FONT_SANS}">
<rect x="22" y="22" width="38" height="38" rx="10" fill="url(#ic)"/>
<text x="41" y="48" text-anchor="middle" font-size="19" font-weight="800" fill="#fff">{escape(titulo[0])}</text>
<text x="72" y="40" font-size="17" font-weight="700" fill="{c["texto"]}">{escape(titulo)}</text>
<text x="72" y="58" font-size="11" font-weight="600" fill="{cores[0] if tema == "light" else cores[1]}" letter-spacing=".6">{escape(tag.upper())}</text>
{desc}
<text x="22" y="152" font-size="12" font-weight="600" fill="{c["texto"]}">{escape(rodape)} ↗</text>
<circle cx="276" cy="148" r="4" fill="#3fb950"><animate attributeName="opacity" values="1;.25;1" dur="2s" repeatCount="indefinite"/></circle>
</g></svg>'''
    salvar(f"cards/{nome}-{tema}.svg", svg)


CARDS = [
    ("simulai", "SimulAI Academy", "Edtech · IA",
     "Estude com IA, não contra ela. Seu PDF vira simulado, mapa mental e redação corrigida no padrão ENEM.",
     "simulaiacademy.com", ["#8b5cf6", "#ec4899"]),
    ("datalock", "DataLock", "Cibersegurança · LGPD",
     "Proteção avançada de dados e adequação à LGPD para empresas.",
     "datalock.com.br", ["#0ea5e9", "#22c55e"]),
    ("dividiu", "Dividiu", "App · Pix",
     "Juntou a galera, dividiu a conta. Rateio automático, comprovante e cobrança no Pix.",
     "dividiu.app", ["#f59e0b", "#ef4444"]),
    ("re-xlsx", "re-xlsx", "Plugin Camunda Modeler",
     "Excel ⇄ tabelas de decisão DMN, com tipos FEEL e hit policy configurável.",
     "github.com/TheDougg", ["#22d3ee", "#8b5cf6"]),
    ("re-lint", "re-lint", "Plugin Camunda Modeler",
     "Valida convenções do BPMN e marca os problemas direto no diagrama.",
     "github.com/TheDougg", ["#22d3ee", "#8b5cf6"]),
    ("re-docs", "re-docs", "Plugin Camunda Modeler",
     "Documentação do processo com busca e exportação em HTML, Markdown, PNG e SVG.",
     "github.com/TheDougg", ["#22d3ee", "#8b5cf6"]),
]


# ---------------------------------------------------------------- jogo da velha

def pecas():
    base = '<rect x="3" y="3" width="74" height="74" rx="14" fill="#161b22" stroke="#30363d" stroke-width="2"/>'
    defs = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{VIOLETA}"/>'
            f'<stop offset="1" stop-color="#ec4899"/></linearGradient></defs>')
    abre = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80">'
    salvar("velha/x.svg", f'{abre}{defs}{base}<path d="M26 26 L54 54 M54 26 L26 54" stroke="url(#g)" stroke-width="8" stroke-linecap="round"/></svg>')
    salvar("velha/o.svg", f'{abre}{base}<circle cx="40" cy="40" r="15" fill="none" stroke="{CIANO}" stroke-width="8"/></svg>')
    salvar("velha/vazio.svg", f'{abre}{base}<path d="M40 33 V47 M33 40 H47" stroke="#30363d" stroke-width="3" stroke-linecap="round">'
                              f'<animate attributeName="stroke" values="#30363d;#8b5cf6;#30363d" dur="2.4s" repeatCount="indefinite"/></path></svg>')


# ---------------------------------------------------------------- rodapé

def rodape():
    a = "M0 40 C150 10 300 70 450 40 C600 10 750 70 900 40 V90 H0 Z"
    b = "M0 40 C150 70 300 10 450 40 C600 70 750 10 900 40 V90 H0 Z"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 90" width="900" height="90" preserveAspectRatio="none">
<defs><linearGradient id="w" x1="0" x2="1"><stop offset="0" stop-color="{VIOLETA}"/><stop offset=".5" stop-color="{CIANO}"/><stop offset="1" stop-color="#ec4899"/></linearGradient></defs>
<path d="{a}" fill="url(#w)" opacity=".35"><animate attributeName="d" values="{a};{b};{a}" dur="7s" repeatCount="indefinite"/></path>
<path d="{b}" fill="url(#w)" opacity=".6" transform="translate(0 14)"><animate attributeName="d" values="{b};{a};{b}" dur="9s" repeatCount="indefinite"/></path>
</svg>'''
    salvar("rodape.svg", svg)


if __name__ == "__main__":
    terminal()
    for tema in TEMAS:
        fluxo(tema)
        for args in CARDS:
            card(args[0], tema, *args[1:])
    pecas()
    rodape()
    print("SVGs gerados em", ASSETS)
