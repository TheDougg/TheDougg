"""Publica um cartão de atividade com horário de atualização, sem cache de 24h no perfil."""

from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo
import os
import xml.etree.ElementTree as ET


def main():
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    parametros = {
        "user": os.environ.get("GITHUB_REPOSITORY_OWNER", "TheDougg"),
        "hide_border": "true",
        "background": "00000000",
        "ring": "00ff41",
        "fire": "00ff41",
        "currStreakLabel": "00ff41",
        "sideLabels": "8b949e",
        "currStreakNum": "8b949e",
        "sideNums": "8b949e",
        "dates": "8b949e",
        "stroke": "30363d",
        "locale": "pt_BR",
        # Uma URL nova em cada execução evita reutilizar uma resposta antiga.
        "v": str(int(agora.timestamp())),
    }
    pedido = Request(
        "https://streak-stats.demolab.com?" + urlencode(parametros),
        headers={"User-Agent": "github-profile-activity", "Cache-Control": "no-cache"},
    )
    with urlopen(pedido, timeout=45) as resposta:
        svg = ET.fromstring(resposta.read())

    ns = "http://www.w3.org/2000/svg"
    textos = {" ".join(elemento.itertext()).strip() for elemento in svg.iter(f"{{{ns}}}text")}
    if svg.tag != f"{{{ns}}}svg" or not {
        "Total de Contribuições", "Sequência Atual", "Maior Sequência"
    }.issubset(textos):
        raise ValueError("O serviço não retornou um cartão de atividade válido; mantendo a versão publicada.")

    ET.register_namespace("", ns)
    ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    svg.set("viewBox", "0 0 495 220")
    svg.set("height", "220px")
    rodape = ET.SubElement(svg, f"{{{ns}}}text", {
        "x": "247.5", "y": "211", "text-anchor": "middle", "fill": "#8b949e",
        "font-family": "Segoe UI, Ubuntu, sans-serif", "font-size": "11",
    })
    rodape.text = "Atualizado em " + agora.strftime("%d/%m/%Y às %H:%M") + " · Brasília"
    destino = Path("dist/atividade.svg")
    destino.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(svg).write(destino, encoding="utf-8", xml_declaration=True)
    print(rodape.text)


if __name__ == "__main__":
    main()
