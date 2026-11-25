"""Ilustrações provisórias das fotos de capa (1080x820), até a Dra. mandar as fotos reais."""
import asyncio, os, sys
sys.path.insert(0, "/home/claude/previa/ilustra")
from cenas import img, arvore, INK  # reaproveita gatos e árvore
from playwright.async_api import async_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 820
os.chdir("/home/claude/previa/ilustra")


def parede(cor="#D3D6DB", chao="#CDB49A", y=640):
    return f'<rect width="{W}" height="{H}" fill="{cor}"/><rect y="{y}" width="{W}" height="{H-y}" fill="{chao}"/>'


def natal():
    return (parede() + arvore(330, 70, 0.9)
            + img("gato-zack.png", 560, 400, 300) + img("gato-fred.png", 800, 450, 230))


def mala(x, y):
    return (f'<g transform="translate({x} {y})">'
            f'<rect x="0" y="60" width="520" height="300" rx="34" fill="#5897A0" stroke="{INK}" stroke-width="12"/>'
            f'<path d="M0 0 h520 l-30 70 h-460 z" fill="#4A8790" stroke="{INK}" stroke-width="12" stroke-linejoin="round" transform="translate(0 -30) skewX(-8)"/>'
            f'<path d="M40 140 h440 M40 220 h440" stroke="#4A8790" stroke-width="10"/>'
            f'<rect x="210" y="300" width="100" height="30" rx="10" fill="#F2C14E" stroke="{INK}" stroke-width="8"/>'
            f'<path d="M60 80 c40 -30 120 -30 160 0 M300 80 c40 -30 120 -30 160 0" stroke="#F2B8C6" stroke-width="16" fill="none" stroke-linecap="round"/></g>')


def viagem():
    return (parede() + mala(280, 360)
            + img("cabeca-raul.png", 400, 230, 280)
            + f'<path d="M420 400 h240" stroke="{INK}" stroke-width="12"/>')


def reveillon():
    janela = (f'<rect x="90" y="90" width="300" height="360" rx="10" fill="#26304A" stroke="{INK}" stroke-width="12"/>'
              + "".join(f'<g stroke="{c}" stroke-width="5" stroke-linecap="round">' + "".join(
                  f'<path d="M{cx} {cy} l{dx} {dy}"/>' for dx, dy in [(0, -34), (24, -24), (34, 0), (24, 24), (0, 34), (-24, 24), (-34, 0), (-24, -24)]) + '</g>'
                  for cx, cy, c in [(180, 180, "#F2C14E"), (300, 260, "#F0B9C8"), (200, 350, "#A9D3D9")])
              + f'<path d="M240 90 v360 M90 270 h300" stroke="{INK}" stroke-width="10"/>')
    cama = (f'<rect x="440" y="420" width="600" height="150" rx="20" fill="#FFFFFF" stroke="{INK}" stroke-width="12"/>'
            f'<path d="M440 470 C600 430 800 520 1040 460 L1040 560 L440 560 Z" fill="#B9D6F0" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>'
            f'<rect x="460" y="570" width="30" height="70" fill="#8A5A3B" stroke="{INK}" stroke-width="10"/><rect x="990" y="570" width="30" height="70" fill="#8A5A3B" stroke="{INK}" stroke-width="10"/>')
    return (parede() + janela + cama
            + f'<rect x="440" y="570" width="600" height="70" fill="#3B3F4A"/>'
            + img("cabeca-zack.png", 640, 560, 190)
            + f'<rect x="440" y="636" width="600" height="20" fill="#CDB49A"/>')


CENAS = {"capa-natal": natal, "capa-viagem": viagem, "capa-reveillon": reveillon}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H})
        for nome, f in CENAS.items():
            html = (f'<!doctype html><html><body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                    f'viewBox="0 0 {W} {H}">{f()}</svg></body></html>')
            path = os.path.join(AQUI, nome + ".html"); open(path, "w").write(html)
            await pg.goto("file://" + path); await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(AQUI, nome + ".png"))
        await b.close()

if __name__ == "__main__":
    asyncio.run(main())
