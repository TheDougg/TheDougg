"""Gera os SVGs animados do perfil (assets/). Rode: python scripts/gen_svgs.py"""
import random
import re
from pathlib import Path
from xml.sax.saxutils import escape

ASSETS = Path(__file__).resolve().parent.parent / "assets"
VIOLETA, CIANO = "#8b5cf6", "#22d3ee"
FONT_MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
FONT_SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

TEMAS = {
    "dark": dict(bg="#0d1117", card="#161b22", borda="#30363d", texto="#e6edf3",
                 suave="#8b949e", token="#00ff41", acento="#3fb950"),
    "light": dict(bg="#ffffff", card="#f6f8fa", borda="#d0d7de", texto="#1f2328",
                  suave="#57606a", token="#16a34a", acento="#15803d"),
}


def salvar(nome, conteudo):
    ASSETS.joinpath(nome).parent.mkdir(parents=True, exist_ok=True)
    ASSETS.joinpath(nome).write_text(conteudo, encoding="utf-8")


def gradiente_girando(gid, cores, dur=6):
    stops = "".join(f'<stop offset="{i / (len(cores) - 1):.2f}" stop-color="{c}"/>' for i, c in enumerate(cores))
    return (f'<linearGradient id="{gid}" gradientUnits="objectBoundingBox">{stops}'
            f'<animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" '
            f'dur="{dur}s" repeatCount="indefinite"/></linearGradient>')


# ---------------------------------------------------------------- estilo hacker (chuva Matrix)

VERDE, VERDE_CLARO, PRETO = "#00ff41", "#d7ffe0", "#020604"
FONT_CHUVA = "'MS Gothic','Hiragino Kaku Gothic ProN','Noto Sans Mono CJK JP',ui-monospace,monospace"
CARACTERES = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789Z:・.=*+<>|"
BRILHO = ('<filter id="brilho" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>'
          '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>')


def chuva(largura, altura, semente, passo=18, opacidade=1.0):
    """Colunas de caracteres caindo, cada uma com velocidade e atraso próprios."""
    rnd = random.Random(semente)
    colunas = []
    for x in range(6, largura, passo):
        n = rnd.randint(7, 20)
        chars = "".join(
            f'<tspan x="{x}" y="{i * 17}" fill="{VERDE_CLARO if i == n - 1 else VERDE}" '
            f'fill-opacity="{1 if i == n - 1 else round((i + 1) / n * .8, 2)}">{escape(rnd.choice(CARACTERES))}</tspan>'
            for i in range(n))
        dur = rnd.uniform(4, 10)
        colunas.append(
            f'<text>{chars}<animateTransform attributeName="transform" type="translate" '
            f'from="0 {-n * 17}" to="0 {altura + 20}" dur="{dur:.1f}s" begin="-{rnd.uniform(0, dur):.1f}s" '
            f'repeatCount="indefinite"/></text>')
    return f'<g font-family="{FONT_CHUVA}" font-size="15" opacity="{opacidade}">{"".join(colunas)}</g>'


def cabecalho():
    def entra(atraso, conteudo):
        # Sem animação o texto já aparece (opacidade base 1); com animação, entra subindo.
        dur, k = atraso + .7, atraso / (atraso + .7)
        return (f'<g><animate attributeName="opacity" values="0;0;1" keyTimes="0;{k:.3f};1" dur="{dur:.2f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" values="0 12;0 12;0 0" '
                f'keyTimes="0;{k:.3f};1" dur="{dur:.2f}s" fill="freeze" calcMode="spline" '
                f'keySplines="0 0 1 1;.2 .8 .2 1"/>{conteudo}</g>')

    nome = '<text x="46" y="126" font-size="50" font-weight="800" letter-spacing="-1"{extra}>Douglas Henrique</text>'
    # glitch: a cada 6s duas cópias deslocadas piscam por um instante
    glitch = "".join(
        f'<g opacity="0" fill="{cor}"><animate attributeName="opacity" values="0;0;.8;0;.6;0" '
        f'keyTimes="0;.9;.91;.93;.95;1" dur="6s" repeatCount="indefinite"/>'
        f'{nome.format(extra=f" transform=\"translate({dx} 0)\"")}</g>'
        for cor, dx in (("#ff2a6d", -3), ("#05d9e8", 3)))

    numeros = [("3", "produtos no ar"), ("2FA · Argon2 · LGPD", "segurança por padrão"), ("TS · Py · Java", "no dia a dia")]
    stats, x = "", 48
    for i, (n, rotulo) in enumerate(numeros):
        stats += entra(.9 + i * .15, f'<text x="{x}" y="212" font-size="22" font-weight="800" fill="{VERDE_CLARO}">{n}</text>'
                                     f'<text x="{x}" y="232" font-size="12" fill="#6fbf7f" font-family="{FONT_MONO}">{rotulo}</text>')
        x += 46 + max(len(n) * 13, len(rotulo) * 7.4)
        if i < len(numeros) - 1:
            stats += entra(.9 + i * .15, f'<rect x="{x - 22}" y="194" width="1" height="40" fill="{VERDE}" opacity=".3"/>')

    pos = {"simulai": (650, 34, "SimulAI Academy"), "datalock": (780, 88, "DataLock"), "dividiu": (668, 150, "Dividiu")}
    centro = {k: (x + 35, y + 35) for k, (x, y, _) in pos.items()}
    (ax, ay), (bx, by), (cx, cy) = centro["simulai"], centro["datalock"], centro["dividiu"]
    trilho = f"M{ax} {ay} L{bx} {by} L{cx} {cy} Z"
    tiles = ""
    for i, (nome_logo, (x, y, rotulo)) in enumerate(pos.items()):
        tiles += (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -6;0 0" '
                  f'dur="4.5s" begin="-{i * 1.5}s" repeatCount="indefinite" calcMode="spline" '
                  f'keyTimes="0;.5;1" keySplines=".45 0 .55 1;.45 0 .55 1"/>'
                  f'<rect x="{x}" y="{y}" width="70" height="70" rx="18" fill="#07130b" stroke="{VERDE}" stroke-opacity=".55"/>'
                  f'{logo(nome_logo, x + 7, y + 7, 56)}'
                  f'<text x="{x + 35}" y="{y + 88}" text-anchor="middle" font-size="11" font-family="{FONT_MONO}" fill="#6fbf7f">{rotulo}</text></g>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 260" width="900" height="260" role="img" aria-label="Douglas Henrique, dev full stack e segurança de dados">
<defs>{BRILHO}
<linearGradient id="veu" x1="0" x2="1"><stop offset="0" stop-color="{PRETO}" stop-opacity=".92"/><stop offset=".55" stop-color="{PRETO}" stop-opacity=".7"/><stop offset="1" stop-color="{PRETO}" stop-opacity=".25"/></linearGradient>
<linearGradient id="varre" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VERDE}" stop-opacity="0"/><stop offset="1" stop-color="{VERDE}" stop-opacity=".12"/></linearGradient>
<clipPath id="moldura"><rect x="1" y="1" width="898" height="258" rx="20"/></clipPath>
</defs>
<g clip-path="url(#moldura)">
<rect width="900" height="260" fill="{PRETO}"/>
{chuva(900, 260, 7)}
<rect width="900" height="260" fill="url(#veu)"/>
<rect width="900" height="40" fill="url(#varre)"><animateTransform attributeName="transform" type="translate" from="0 -40" to="0 260" dur="5s" repeatCount="indefinite"/></rect>
</g>
<rect x="1" y="1" width="898" height="258" rx="20" fill="none" stroke="{VERDE}" stroke-opacity=".35"/>
<g font-family="{FONT_SANS}">
{entra(.1, f'<text x="48" y="68" font-size="13" font-weight="700" letter-spacing="2" fill="{VERDE}" font-family="{FONT_MONO}">[ DEV FULL STACK · SEGURANÇA DE DADOS ]</text>')}
{entra(.3, f'{glitch}<g fill="{VERDE}" filter="url(#brilho)">{nome.format(extra="")}</g>')}
{entra(.55, f'<text x="48" y="162" font-size="16" fill="#b7f5c4" font-family="{FONT_MONO}">Crio produtos com IA, protejo dados e automatizo processos.</text>')}
{stats}
<path d="{trilho}" fill="none" stroke="{VERDE}" stroke-opacity=".5" stroke-width="1.5" stroke-dasharray="4 6">
<animate attributeName="stroke-dashoffset" from="0" to="-40" dur="2s" repeatCount="indefinite"/></path>
<circle r="4" fill="{VERDE}" filter="url(#brilho)"><animateMotion dur="7s" repeatCount="indefinite" path="{trilho}"/></circle>
{tiles}
</g></svg>'''
    salvar("cabecalho.svg", svg)


def seguranca():
    itens = [
        ("senhas com hash Argon2 / bcrypt", "nunca texto puro"),
        ("login com 2FA + JWT", "token assinado"),
        ("monitoramento de vazamentos", "breaches e paste sites"),
        ("cofre de senhas", "com histórico de renovação"),
        ("varredura de arquivos enviados", "antes de entrar no sistema"),
        ("helmet · rate limit · Zod · DOMPurify", "contra injeção e abuso"),
        ("LGPD", "adequação de empresas à lei"),
    ]
    T, x0, y0, lh = 14.0, 290, 74, 22
    linhas = []
    for i, (oque, nota) in enumerate(itens):
        t = .6 + i * .55
        linhas.append(
            f'<g><animate attributeName="opacity" values="0;1;1" keyTimes="0;{t / T:.3f};1" dur="{T}s" '
            f'repeatCount="indefinite" calcMode="discrete"/>'
            f'<text x="{x0}" y="{y0 + i * lh}"><tspan fill="{VERDE}" font-weight="700">[ OK ]</tspan>'
            f'<tspan fill="#d7ffe0" dx="10">{escape(oque)}</tspan><tspan fill="#5f9e6c" dx="10">// {escape(nota)}</tspan></text></g>')
    t_fim = .6 + len(itens) * .55
    status = (f'<g><animate attributeName="opacity" values="0;1;1" keyTimes="0;{t_fim / T:.3f};1" dur="{T}s" '
              f'repeatCount="indefinite" calcMode="discrete"/>'
              f'<text x="{x0}" y="{y0 + len(itens) * lh + 14}" fill="{VERDE}" font-weight="700" filter="url(#brilho)">&gt; status: PROTEGIDO'
              f'<tspan><animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/> █</tspan></text></g>')

    escudo = "M150 40 L222 66 V122 C222 166 192 196 150 214 C108 196 78 166 78 122 V66 Z"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 250" width="900" height="250" role="img" aria-label="Checklist de segurança de dados">
<defs>{BRILHO}<clipPath id="moldura"><rect x="1" y="1" width="898" height="248" rx="18"/></clipPath>
<clipPath id="escudo"><path d="{escudo}"/></clipPath>
<linearGradient id="feixe" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VERDE}" stop-opacity="0"/><stop offset="1" stop-color="{VERDE}" stop-opacity=".55"/></linearGradient></defs>
<g clip-path="url(#moldura)"><rect width="900" height="250" fill="{PRETO}"/>{chuva(900, 250, 21, 22, .16)}</g>
<rect x="1" y="1" width="898" height="248" rx="18" fill="none" stroke="{VERDE}" stroke-opacity=".35"/>
<circle cx="150" cy="127" r="80" fill="none" stroke="{VERDE}" stroke-width="1.5"><animate attributeName="r" values="80;112" dur="2.4s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values=".6;0" dur="2.4s" repeatCount="indefinite"/></circle>
<path d="{escudo}" fill="#07130b" stroke="{VERDE}" stroke-width="2.5" filter="url(#brilho)"/>
<g clip-path="url(#escudo)"><rect x="70" y="0" width="160" height="34" fill="url(#feixe)"><animateTransform attributeName="transform" type="translate" values="0 6;0 190;0 6" dur="3s" repeatCount="indefinite"/></rect></g>
<rect x="126" y="118" width="48" height="40" rx="6" fill="{VERDE}"/>
<path d="M135 118 V106 A15 15 0 0 1 165 106 V118" fill="none" stroke="{VERDE}" stroke-width="6"/>
<circle cx="150" cy="134" r="5" fill="{PRETO}"/><rect x="148" y="136" width="4" height="12" rx="2" fill="{PRETO}"/>
<g font-family="{FONT_MONO}" font-size="14">
<text x="{x0}" y="42" fill="#6fbf7f">$ ./auditoria --produtos simulai,datalock,dividiu</text>
{"".join(linhas)}{status}
</g></svg>'''
    salvar("seguranca.svg", svg)


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
     "github.com/TheDougg", ["#00ff41", "#22d3ee"]),
    ("re-lint", "re-lint", "Plugin Camunda Modeler",
     "Valida convenções do BPMN e marca os problemas direto no diagrama.",
     "github.com/TheDougg", ["#00ff41", "#22d3ee"]),
    ("re-docs", "re-docs", "Plugin Camunda Modeler",
     "Documentação do processo com busca e exportação em HTML, Markdown, PNG e SVG.",
     "github.com/TheDougg", ["#00ff41", "#22d3ee"]),
]


# ---------------------------------------------------------------- jogo da velha

def pecas():
    base = '<rect x="3" y="3" width="74" height="74" rx="14" fill="#161b22" stroke="#30363d" stroke-width="2"/>'
    defs = (f'<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#00ff41"/>'
            f'<stop offset="1" stop-color="#16a34a"/></linearGradient></defs>')
    abre = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80" width="80" height="80">'
    salvar("velha/x.svg", f'{abre}{defs}{base}<path d="M26 26 L54 54 M54 26 L26 54" stroke="url(#g)" stroke-width="8" stroke-linecap="round"/></svg>')
    salvar("velha/o.svg", f'{abre}{base}<circle cx="40" cy="40" r="15" fill="none" stroke="{CIANO}" stroke-width="8"/></svg>')
    salvar("velha/vazio.svg", f'{abre}{base}<path d="M40 33 V47 M33 40 H47" stroke="#30363d" stroke-width="3" stroke-linecap="round">'
                              f'<animate attributeName="stroke" values="#30363d;#00ff41;#30363d" dur="2.4s" repeatCount="indefinite"/></path></svg>')


# ---------------------------------------------------------------- rodapé

def rodape():
    a = "M0 40 C150 10 300 70 450 40 C600 10 750 70 900 40 V90 H0 Z"
    b = "M0 40 C150 70 300 10 450 40 C600 70 750 10 900 40 V90 H0 Z"
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 90" width="900" height="90" preserveAspectRatio="none">
<defs><linearGradient id="w" x1="0" x2="1"><stop offset="0" stop-color="#003b12"/><stop offset=".5" stop-color="#00ff41"/><stop offset="1" stop-color="#003b12"/></linearGradient></defs>
<path d="{a}" fill="url(#w)" opacity=".35"><animate attributeName="d" values="{a};{b};{a}" dur="7s" repeatCount="indefinite"/></path>
<path d="{b}" fill="url(#w)" opacity=".6" transform="translate(0 14)"><animate attributeName="d" values="{b};{a};{b}" dur="9s" repeatCount="indefinite"/></path>
</svg>'''
    salvar("rodape.svg", svg)


if __name__ == "__main__":
    for tema in TEMAS:
        fluxo(tema)
        for args in CARDS:
            card(args[0], tema, *args[1:])
    cabecalho()
    seguranca()
    pecas()
    rodape()
    print("SVGs gerados em", ASSETS)
