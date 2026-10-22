"""Gera os SVGs animados do perfil (assets/). Rode: python scripts/gen_svgs.py"""
import re
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


# ---------------------------------------------------------------- cabeçalho

def cabecalho(tema):
    c = TEMAS[tema]
    g1, g2 = (VIOLETA, CIANO) if tema == "dark" else ("#7c3aed", "#0891b2")

    def entra(atraso, conteudo):
        # Sem animação o texto já aparece (opacidade base 1); com animação, entra subindo.
        dur, k = atraso + .7, atraso / (atraso + .7)
        return (f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{dur:.2f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 12;0 12;0 0" '
                f'keyTimes="0;{k:.3f};1" dur="{dur:.2f}s" fill="freeze" calcMode="spline" '
                f'keySplines="0 0 1 1;.2 .8 .2 1"/>{conteudo}</g>')

    numeros = [("3", "produtos no ar"), ("3", "plugins open source"), ("TS · Py · Java", "no dia a dia")]
    stats, x = "", 48
    for i, (n, rotulo) in enumerate(numeros):
        stats += entra(.9 + i * .15, f'<text x="{x}" y="212" font-size="26" font-weight="800" fill="{c["texto"]}">{n}</text>'
                                     f'<text x="{x}" y="232" font-size="12" fill="{c["suave"]}">{rotulo}</text>')
        x += 54 + max(len(n) * 15, len(rotulo) * 6.6)
        if i < len(numeros) - 1:
            stats += entra(.9 + i * .15, f'<rect x="{x - 26}" y="192" width="1" height="42" fill="{c["borda"]}"/>')

    # produtos no lado direito, ligados por um fluxo com token (o mesmo do diagrama BPMN)
    pos = {"simulai": (650, 34, "SimulAI Academy"), "datalock": (780, 88, "DataLock"), "dividiu": (668, 150, "Dividiu")}
    centro = {k: (x + 35, y + 35) for k, (x, y, _) in pos.items()}
    (ax, ay), (bx, by), (cx, cy) = centro["simulai"], centro["datalock"], centro["dividiu"]
    trilho = f"M{ax} {ay} L{bx} {by} L{cx} {cy} Z"
    tiles = ""
    for i, (nome, (x, y, rotulo)) in enumerate(pos.items()):
        tiles += (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" '
                  f'dur="4.5s" begin="-{i * 1.5}s" repeatCount="indefinite" calcMode="spline" '
                  f'keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                  f'<rect x="{x}" y="{y}" width="70" height="70" rx="18" fill="{c["card"]}" stroke="{c["borda"]}"/>'
                  f'{logo(nome, x + 7, y + 7, 56)}'
                  f'<text x="{x + 35}" y="{y + 88}" text-anchor="middle" font-size="11" font-weight="600" fill="{c["suave"]}">{rotulo}</text></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260" width="900" height="260" role="img" aria-label="Douglas Henrique, dev full stack">
<defs>
<radialGradient id="luz1" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(140 30) scale(420 260)"><stop offset="0" stop-color="{g1}" stop-opacity="{.28 if tema == "dark" else .14}"/><stop offset="1" stop-color="{g1}" stop-opacity="0"/></radialGradient>
<radialGradient id="luz2" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(780 250) scale(380 240)"><stop offset="0" stop-color="{g2}" stop-opacity="{.22 if tema == "dark" else .12}"/><stop offset="1" stop-color="{g2}" stop-opacity="0"/></radialGradient>
<pattern id="pontos" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1" fill="{c["suave"]}" opacity=".22"/></pattern>
<linearGradient id="nome" gradientUnits="userSpaceOnUse" x1="40" y1="0" x2="520" y2="0" spreadMethod="reflect">
<stop offset="0" stop-color="{c["texto"]}"/><stop offset=".45" stop-color="{g1}"/><stop offset="1" stop-color="{g2}"/>
<animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="960 0" dur="9s" repeatCount="indefinite"/></linearGradient>
<clipPath id="moldura"><rect x="1" y="1" width="898" height="258" rx="20"/></clipPath>
</defs>
<g clip-path="url(#moldura)">
<rect width="900" height="260" fill="{c["bg"]}"/>
<rect width="900" height="260" fill="url(#pontos)"/>
<rect width="900" height="260" fill="url(#luz1)"><animate attributeName="opacity" values="1;.6;1" dur="8s" repeatCount="indefinite"/></rect>
<rect width="900" height="260" fill="url(#luz2)"><animate attributeName="opacity" values=".6;1;.6" dur="8s" repeatCount="indefinite"/></rect>
</g>
<rect x="1" y="1" width="898" height="258" rx="20" fill="none" stroke="{c["borda"]}"/>
<g font-family="{FONT_SANS}">
{entra(.1, f'<text x="48" y="68" font-size="12" font-weight="700" letter-spacing="3" fill="{g1}">DEV FULL STACK · BRASIL</text>')}
{entra(.3, '<text x="46" y="124" font-size="50" font-weight="800" fill="url(#nome)" letter-spacing="-1">Douglas Henrique</text>')}
{entra(.55, f'<text x="48" y="160" font-size="18" fill="{c["suave"]}">Crio produtos com IA e automatizo processos de negócio.</text>')}
{stats}
<path d="{trilho}" fill="none" stroke="{g1}" stroke-opacity=".45" stroke-width="1.5" stroke-dasharray="4 6">
<animate attributeName="stroke-dashoffset" from="0" to="-40" dur="2s" repeatCount="indefinite"/></path>
<circle r="5" fill="{g2}"><animateMotion dur="7s" repeatCount="indefinite" path="{trilho}"/></circle>
{tiles}
</g></svg>'''
    salvar(f"cabecalho-{tema}.svg", svg)


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


def logo(nome, x, y, tam):
    """Logo vetorial embutido (o GitHub bloqueia imagem em data: dentro de SVG)."""
    svg = (ASSETS / "logos" / f"{nome}.svg").read_text(encoding="utf-8")
    viewbox = re.search(r'viewBox="([^"]+)"', svg).group(1)
    miolo = svg[svg.index(">") + 1:svg.rindex("</svg>")]
    return f'<svg x="{x}" y="{y}" width="{tam}" height="{tam}" viewBox="{viewbox}">{miolo}</svg>'


def icone(nome, titulo):
    if (ASSETS / "logos" / f"{nome}.svg").exists():
        return logo(nome, 22, 22, 38)
    return (f'<rect x="22" y="22" width="38" height="38" rx="10" fill="url(#ic)"/>'
            f'<text x="41" y="48" text-anchor="middle" font-size="19" font-weight="800" fill="#fff">{escape(titulo[0])}</text>')


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
{icone(nome, titulo)}
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
    for tema in TEMAS:
        cabecalho(tema)
        fluxo(tema)
        for args in CARDS:
            card(args[0], tema, *args[1:])
    pecas()
    rodape()
    print("SVGs gerados em", ASSETS)
