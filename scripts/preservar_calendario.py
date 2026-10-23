"""Mantém os dias reais visíveis enquanto a cobrinha percorre o calendário."""

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import xml.etree.ElementTree as ET


def preservar(caminho):
    arvore = ET.parse(caminho)
    raiz = arvore.getroot()
    ns = "http://www.w3.org/2000/svg"
    celulas = [
        elemento for elemento in raiz.iter(f"{{{ns}}}rect")
        if "c" in elemento.get("class", "").split()
    ]
    if not celulas:
        raise ValueError(f"{caminho}: o SVG não contém um calendário válido")

    # As classes originais mantêm as cores recebidas do GitHub. Desativamos
    # somente a animação que apaga os dias, preservando o movimento da cobra.
    for celula in celulas:
        celula.set("style", "animation: none !important")

    ativos = sum(len(celula.get("class").split()) > 1 for celula in celulas)
    agora = datetime.now(ZoneInfo("America/Sao_Paulo"))
    titulo = ET.Element(f"{{{ns}}}title")
    titulo.text = (
        f"Calendário do GitHub: {ativos} dias com contribuições nos últimos 12 meses. "
        + agora.strftime("Atualizado em %d/%m/%Y às %H:%M (Brasília).")
    )
    raiz.insert(0, titulo)
    ET.register_namespace("", ns)
    # O gerador roda em Docker e cria arquivos de outro usuário. A pasta dist
    # pertence ao runner: substituímos o arquivo sem alterar suas permissões.
    temporario = caminho.with_suffix(".tmp")
    arvore.write(temporario, encoding="utf-8", xml_declaration=True)
    temporario.replace(caminho)
    print(f"{caminho}: {ativos} dias ativos; cores originais preservadas")


if __name__ == "__main__":
    for caminho in (Path("dist/snake-light.svg"), Path("dist/snake-dark.svg")):
        preservar(caminho)
