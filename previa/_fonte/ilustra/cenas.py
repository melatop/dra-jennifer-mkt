"""Monta as ilustrações de referência das fotos a tirar (1080x1350) com a Dra. vetorial
e os gatos do canal @dicasmiau. Uso: python3 cenas.py  -> cena-*.png"""
import asyncio, base64, os
from playwright.async_api import async_playwright
from dra import dra_svg, INK

AQUI = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350


def png(nome):
    with open(os.path.join(AQUI, nome), "rb") as f:
        return "data:image/png;base64," + base64.b64encode(f.read()).decode()


def img(nome, x, y, w, flip=False):
    from PIL import Image
    iw, ih = Image.open(os.path.join(AQUI, nome)).size
    h = w * ih / iw
    t = f' transform="translate({2*x+w} 0) scale(-1 1)"' if flip else ""
    return f'<image href="{png(nome)}" x="{x}" y="{y}" width="{w}" height="{h:.0f}"{t}/>'


def dra(x, y, s, bracos, roupa="jaleco"):
    return f'<g transform="translate({x} {y}) scale({s})">{dra_svg(bracos, standalone=False, roupa=roupa)}</g>'


def selo():
    return ('<g><rect x="40" y="40" width="300" height="52" rx="26" fill="#FFFFFF" opacity=".92"/>'
            '<text x="190" y="74" text-anchor="middle" font-family="Carlito, sans-serif" font-weight="700" '
            'font-size="22" letter-spacing="3" fill="#6D2E46">REFERÊNCIA DA FOTO</text></g>')


def janela(x, y, w, h):
    return (f'<polygon points="{x+w},{y} {x+w+380},{y+h+420} {x+w+120},{y+h+420} {x+w},{y+h}" fill="#FFF6D8" opacity=".55"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="#DDF0F4" stroke="{INK}" stroke-width="12"/>'
            f'<path d="M{x+w/2} {y}v{h}M{x} {y+h/2}h{w}" stroke="{INK}" stroke-width="10"/>'
            f'<path d="M{x+30} {y+40} l60 -30 M{x+30} {y+90} l100 -50" stroke="#FFFFFF" stroke-width="10" stroke-linecap="round"/>')


def arvore(x, y, s):
    t = f'transform="translate({x} {y}) scale({s})"'
    camadas = "".join(
        f'<path d="M0 {y0} L{-w} {y0+h} Q0 {y0+h+30} {w} {y0+h} Z" fill="{c}" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>'
        for y0, h, w, c in [(240, 230, 250, "#3E8E6A"), (120, 210, 200, "#47A077"), (20, 180, 150, "#52B184")])
    bolas = "".join(f'<circle cx="{cx}" cy="{cy}" r="20" fill="{c}" stroke="{INK}" stroke-width="8"/>'
                    for cx, cy, c in [(-60, 170, "#D1899D"), (70, 230, "#F2C14E"), (-110, 330, "#F2C14E"), (40, 360, "#D1899D"), (150, 420, "#87495E"), (-30, 440, "#5897A0")])
    return (f'<g {t}><rect x="-40" y="470" width="80" height="90" fill="#8A5A3B" stroke="{INK}" stroke-width="12"/>'
            f'<path d="M-90 550 h180 l-20 90 h-140 z" fill="#87495E" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>'
            f'{camadas}{bolas}<path d="M0 -40 l14 30 32 4 -24 22 7 32 -29 -16 -29 16 7 -32 -24 -22 32 -4 z" fill="#F2C14E" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/></g>')


def mesa(y):
    return (f'<rect x="60" y="{y}" width="960" height="70" rx="14" fill="#C9CED6" stroke="{INK}" stroke-width="12"/>'
            f'<rect x="100" y="{y+70}" width="880" height="400" fill="#DDE1E7" stroke="{INK}" stroke-width="12"/>'
            f'<path d="M300 {y-6} h480 l20 40 h-520 z" fill="#F2B8C6" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>')


def guitarra(x, y, s, rot=-12):
    """guitarra (superstrat preta, estilo Ibanez GIO) pendurada na parede"""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="M-6 -40 v-10" stroke="{INK}" stroke-width="8"/><path d="M-30 -40 h48 l-8 -26 h-32 z" fill="#5A5F6A" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
            f'<rect x="-18" y="-40" width="36" height="300" rx="6" fill="#B8814E" stroke="{INK}" stroke-width="10"/>'
            + "".join(f'<path d="M-18 {y0}h36" stroke="#E8D8BE" stroke-width="4"/>' for y0 in range(-10, 250, 32))
            + f'<path d="M-24 250 C-70 230 -96 260 -84 300 C-76 330 -110 360 -96 410 C-80 470 -20 480 0 470 C40 486 104 470 112 400 C118 350 84 330 92 296 C100 260 74 226 30 250 C20 236 6 230 -10 238 Z" fill="#1E1F24" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>'
            f'<rect x="-30" y="300" width="60" height="22" rx="4" fill="#E9E9EE" stroke="{INK}" stroke-width="6"/><rect x="-30" y="380" width="60" height="22" rx="4" fill="#E9E9EE" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-30 424 h60" stroke="#C9CCD3" stroke-width="10" stroke-linecap="round"/>'
            f'<circle cx="64" cy="420" r="10" fill="#C9CCD3" stroke="{INK}" stroke-width="5"/><circle cx="80" cy="392" r="10" fill="#C9CCD3" stroke="{INK}" stroke-width="5"/>'
            f'<path d="M-4 -40 V440 M4 -40 V440" stroke="#EDEDED" stroke-width="2"/></g>')


def violao(x, y, s, rot=10):
    """violão de madeira clara pendurado na parede"""
    return (f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">'
            f'<path d="M-6 -40 v-10" stroke="{INK}" stroke-width="8"/><path d="M-28 -40 h56 l-6 -34 h-44 z" fill="#8A5A3B" stroke="{INK}" stroke-width="8" stroke-linejoin="round"/>'
            f'<rect x="-20" y="-40" width="40" height="260" rx="6" fill="#6B4430" stroke="{INK}" stroke-width="10"/>'
            + "".join(f'<path d="M-20 {y0}h40" stroke="#D8C3A0" stroke-width="4"/>' for y0 in range(-10, 220, 30))
            + f'<path d="M0 214 C-70 214 -96 260 -84 310 C-76 340 -116 370 -110 430 C-102 510 -40 530 0 530 C40 530 102 510 110 430 C116 370 76 340 84 310 C96 260 70 214 0 214 Z" fill="#E2B27A" stroke="{INK}" stroke-width="12" stroke-linejoin="round"/>'
            f'<circle cx="0" cy="340" r="38" fill="#3A2418" stroke="{INK}" stroke-width="8"/><circle cx="0" cy="340" r="50" fill="none" stroke="#B98552" stroke-width="6"/>'
            f'<rect x="-46" y="440" width="92" height="18" rx="6" fill="#6B4430" stroke="{INK}" stroke-width="6"/>'
            f'<path d="M-4 -40 V448 M4 -40 V448" stroke="#F4EBDD" stroke-width="2"/></g>')


def cena_apresentacao():
    return (f'<rect width="{W}" height="{H}" fill="#D3D6DB"/>'
            f'<rect y="1050" width="{W}" height="300" fill="#CDB49A"/>'
            + janela(60, 200, 200, 280)
            + guitarra(760, 165, 0.6, -8) + violao(965, 170, 0.56, 10)
            + img("sofa-capuccino.png", -110, 170, 1300)
            + dra(215, 150, 0.65, "frente", "casa")
            + img("gato-zack.png", 390, 620, 300)
            + selo())


def cena_consulta():
    return (f'<rect width="{W}" height="{H}" fill="#E8F3F4"/>'
            f'<rect x="700" y="150" width="300" height="200" rx="12" fill="#FFFFFF" stroke="{INK}" stroke-width="10"/>'
            f'<path d="M740 200 h220 M740 240 h160 M740 280 h190" stroke="#B9D7DB" stroke-width="12" stroke-linecap="round"/>'
            + dra(230, 120, 0.62, "frente")
            + mesa(860)
            + img("caixa-transporte.png", 70, 600, 330)
            + img("gato-raul.png", 520, 610, 270)
            + selo())


def cena_natal():
    return (f'<rect width="{W}" height="{H}" fill="#D3D6DB"/>'
            f'<rect y="1000" width="{W}" height="350" fill="#CDB49A"/>'
            f'<path d="M0 120 Q180 190 360 120 T720 120 T1080 120" fill="none" stroke="{INK}" stroke-width="6"/>'
            + "".join(f'<circle cx="{x}" cy="{y}" r="12" fill="{c}" stroke="{INK}" stroke-width="6"/>' for x, y, c in [(90, 150, "#F2C14E"), (270, 150, "#D1899D"), (450, 150, "#5897A0"), (630, 150, "#F2C14E"), (810, 150, "#D1899D"), (990, 150, "#5897A0")])
            + arvore(240, 300, 0.95)
            + guitarra(680, 240, 0.5, -8) + violao(890, 245, 0.48, 10)
            + img("sofa-capuccino.png", 300, 380, 900)
            + dra(400, 540, 0.68, "frente", "casa")
            + img("gato-zack.png", 590, 1010, 270)
            + img("gato-fred.png", 50, 1030, 240)
            + img("gato-raul.png", 290, 1070, 200, flip=True)
            + selo())


CENAS = {"cena-apresentacao": cena_apresentacao, "cena-consulta": cena_consulta, "cena-natal": cena_natal}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H})
        for nome, f in CENAS.items():
            html = (f'<!doctype html><html><head><meta charset="utf-8"><style>html,body{{margin:0}}</style></head><body>'
                    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{f()}</svg></body></html>')
            open(os.path.join(AQUI, nome + ".html"), "w").write(html)
            await pg.goto("file://" + os.path.join(AQUI, nome + ".html"))
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=os.path.join(AQUI, nome + ".png"))
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
