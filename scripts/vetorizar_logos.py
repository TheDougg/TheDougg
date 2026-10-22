"""Converte os PNGs de assets/logos/ em SVG vetorial (pixel a pixel, faixas por cor).

O GitHub serve SVG com CSP default-src 'none', então PNG embutido em data: não aparece.
Rode uma vez quando trocar um logo: python scripts/vetorizar_logos.py  (precisa de Pillow)
"""
from collections import defaultdict
from pathlib import Path

from PIL import Image

LOGOS = Path(__file__).resolve().parent.parent / "assets" / "logos"
GRADE = 72  # resolução do traço: 72x72 células

# O SimulAI já tem marca vetorial oficial (anel + check); só ganhou o fundo do ícone do app.
SIMULAI = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
<rect width="128" height="128" rx="28" fill="#0e1f38"/>
<g transform="translate(10 12) scale(.82)">
<path fill="#ffffff" d="M87.92 20.31 L95.17 17.99 L79.84 34.51 A36.48 37.08 0 1 0 92.98 54.06 L108.13 35.82 L106.47 43.65 A52.62 53.37 0 1 1 87.92 20.31 Z"/>
<path fill="#818cf8" d="M31.95 60.40 L41.62 51.14 L57.37 65.81 L106.85 12.47 A5.53 5.53 0 0 1 110.81 10.70 L122.75 10.51 L62.93 82.62 A7.19 7.19 0 0 1 52.05 82.82 Z"/>
</g></svg>
'''


def tracar(png):
    im = Image.open(png).convert("RGBA").resize((GRADE, GRADE), Image.LANCZOS)
    faixas = defaultdict(list)  # (cor, alfa) -> [(x, y, largura)]
    for y in range(GRADE):
        x = 0
        while x < GRADE:
            r, g, b, a = im.getpixel((x, y))
            if a < 16:
                x += 1
                continue
            chave = (f"#{r // 12 * 12:02x}{g // 12 * 12:02x}{b // 12 * 12:02x}", min(1, round(a / 255 * 4) / 4))
            ini = x
            while x < GRADE:
                r2, g2, b2, a2 = im.getpixel((x, y))
                if a2 < 16 or (f"#{r2 // 12 * 12:02x}{g2 // 12 * 12:02x}{b2 // 12 * 12:02x}",
                               min(1, round(a2 / 255 * 4) / 4)) != chave:
                    break
                x += 1
            faixas[chave].append((ini, y, x - ini))
    paths = []
    for (cor, alfa), runs in faixas.items():
        # sobreposição mínima evita fiapos entre faixas quando o SVG é escalado
        d = "".join(f"M{x} {y}h{w + .08:g}v1.08h-{w + .08:g}z" for x, y, w in runs)
        op = f' fill-opacity="{alfa:g}"' if alfa < 1 else ""
        paths.append(f'<path fill="{cor}"{op} d="{d}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {GRADE} {GRADE}">{"".join(paths)}</svg>\n'


if __name__ == "__main__":
    LOGOS.joinpath("simulai.svg").write_text(SIMULAI, encoding="utf-8")
    for png in sorted(LOGOS.glob("*.png")):
        if png.stem == "simulai":
            continue
        destino = png.with_suffix(".svg")
        destino.write_text(tracar(png), encoding="utf-8")
        print(destino.name, f"{destino.stat().st_size / 1024:.0f} KB")
