#!/usr/bin/env python3
"""Carrossel no estilo do post aprovado "Por que o gato faz xixi fora da caixa?" (@jenniferaragao.vet):
fundo rosado, título Caladea centralizado com destaque em pílula teal clara, subtítulo, traço rosa duplo,
setas teal desenhadas à mão, foto real ocupando a parte de baixo (fundindo no rosa), card branco opcional
com patinha mauve e rodapé branco com @ e "Arraste".
Uso: python3 build3.py spec.json  ->  <saida>/NN-nome.png + previa.png"""
import json, sys, os, asyncio, base64, html as H
from playwright.async_api import async_playwright
from PIL import Image

W, HG = 1080, 1350


def uri(p):
    ext = "jpeg" if p.lower().endswith((".jpg", ".jpeg")) else "png"
    return f"data:image/{ext};base64," + base64.b64encode(open(p, "rb").read()).decode()


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Carlito',sans-serif;color:#2D2D2D;position:relative;background:linear-gradient(180deg,#FBEEF3 0%,#F7E3EA 100%);-webkit-font-smoothing:antialiased}
.foto{position:absolute;left:0;right:0;bottom:0;background-size:cover;background-repeat:no-repeat}
.veu{position:absolute;left:0;right:0}
.topo{position:absolute;left:70px;right:70px;text-align:center}
h1{font-family:'Caladea',serif;font-weight:700;color:#6D2E46;letter-spacing:-.6px;line-height:1.2}
mark{background:#C9E5E6;color:#6D2E46;padding:2px 22px 4px;border-radius:26px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.sub{margin-top:26px;font-size:36px;color:#87495E}
.traco{display:block;margin:18px auto 0;width:330px;height:30px}
.seta{position:absolute;width:62px;height:50px}
.card{position:absolute;left:64px;right:64px;bottom:108px;background:rgba(255,255,255,.96);border-radius:32px;padding:30px 38px;display:flex;gap:28px;align-items:center;box-shadow:0 10px 30px rgba(80,30,50,.16)}
.card .pata{flex:none;width:92px;height:92px;border-radius:50%;background:#87495E;display:flex;align-items:center;justify-content:center}
.card .pata svg{width:48px;height:48px}
.card p{font-size:32px;line-height:1.36;color:#2D2D2D}
.foot{position:absolute;left:0;right:0;bottom:0;height:64px;background:rgba(255,255,255,.9);display:flex;align-items:center;justify-content:space-between;padding:0 54px;font-size:23px;color:#87495E}
.foot .h{display:flex;align-items:center;gap:10px}.foot svg{width:22px;height:22px}
.foot .sw{font-weight:700;letter-spacing:2px;font-size:21px;display:flex;align-items:center;gap:10px}
.logo{display:block;margin:0 auto 34px;width:470px}
"""
PAW = '<svg viewBox="0 0 40 40" fill="currentColor"><ellipse cx="9" cy="16" rx="3.8" ry="4.8"/><ellipse cx="16" cy="8.5" rx="3.8" ry="5"/><ellipse cx="24" cy="8.5" rx="3.8" ry="5"/><ellipse cx="31" cy="16" rx="3.8" ry="4.8"/><path d="M20 19c-5 0-10 6-10 11 0 4 3 5 6 4.4 2-.4 2.7-1 4-1s2 .6 4 1c3 .6 6-.4 6-4.4 0-5-5-11-10-11z"/></svg>'
ARROW = '<svg viewBox="0 0 44 20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:38px;height:17px"><path d="M2 10h38M31 2l9 8-9 8"/></svg>'
TRACO = ('<svg class="traco" viewBox="0 0 330 30" fill="none" stroke-linecap="round">'
         '<path d="M8 18C90 8 220 6 322 11" stroke="#C9839A" stroke-width="7"/>'
         '<path d="M40 25C120 17 220 16 296 20" stroke="#C9839A" stroke-width="3.5" opacity=".75"/></svg>')


def seta(x, y, girar=False):
    t = 'transform:scaleX(-1);' if girar else ''
    return (f'<svg class="seta" style="left:{x}px;top:{y}px;{t}" viewBox="0 0 62 50" fill="none" stroke="#5897A0" '
            'stroke-width="5.5" stroke-linecap="round"><path d="M6 9L50 17M6 26H56M6 43L50 35"/></svg>')


def slide(s, i, n, base):
    foto = uri(os.path.join(base, s["foto"]))
    alt = s.get("altura_foto", 860)
    fade = s.get("fade", 230)
    css = (f".foto{{height:{alt}px;background-image:url('{foto}');background-position:{s.get('foco','center')}}}"
           f".veu{{bottom:{alt - fade}px;height:{fade + 2}px;background:linear-gradient(180deg,#F9E8EE 0%,rgba(249,232,238,.0) 100%)}}"
           f".veu2{{position:absolute;left:0;right:0;bottom:0;height:{alt}px;background:rgba(246,214,226,{s.get('tinta', .10)});mix-blend-mode:multiply}}"
           f".topo{{top:{s.get('topo', 78)}px}}h1{{font-size:{s.get('tamanho', 76)}px}}")
    logo = f'<img class="logo" src="{uri(os.path.join(base, "logo.png"))}" alt="">' if s.get("logo") else ''
    corpo = (f'<div class="foto"></div><div class="veu2"></div><div class="veu"></div>'
             f'<div class="topo">{logo}<h1>{s["titulo"]}</h1>'
             + (f'<p class="sub">{s["subtitulo"]}</p>' if s.get("subtitulo") else '')
             + (TRACO if s.get("traco", True) else '') + '</div>'
             + "".join(seta(*xy) for xy in s.get("setas", [[935, 96], [60, 1100, True]]))
             + (f'<div class="card"><span class="pata" style="color:#fff">{PAW}</span><p>{s["card"]}</p></div>' if s.get("card") else '')
             + f'<div class="foot"><span class="h">{PAW}@jenniferaragao.vet</span>'
             + (f'<span class="sw">ARRASTE {ARROW}</span>' if n > 1 and i < n else '') + '</div>')
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}{css}</style></head><body>{corpo}</body></html>'


CHECK = """() => { const av=[]; const R=e=>e.getBoundingClientRect();
  if(!document.fonts.check('700 60px Caladea')) av.push('fonte');
  document.querySelectorAll('h1,.sub,.card').forEach(el=>{const r=R(el); if(r.left<40||r.right>1040) av.push(el.className||el.tagName+': margem');});
  const t=document.querySelector('.topo'); const c=document.querySelector('.card');
  if(c && R(t).bottom > R(c).top-200) av.push('título muito perto do card');
  return av; }"""


async def render(spec, base):
    out = spec["saida"]; os.makedirs(out, exist_ok=True)
    n = len(spec["slides"]); pngs = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": W, "height": HG})
        for i, s in enumerate(spec["slides"], 1):
            f = os.path.join(out, f"_{i:02d}.html"); open(f, "w").write(slide(s, i, n, base))
            await pg.goto("file://" + f); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
            av = await pg.evaluate(CHECK)
            png = os.path.join(out, f"{i:02d}-{s.get('nome','slide')}.png"); await pg.screenshot(path=png); pngs.append(png)
            print(os.path.basename(png), "OK" if not av else av)
        await b.close()
    ims = [Image.open(x).resize((360, 450)) for x in pngs]
    g = Image.new("RGB", (len(ims) * 372 - 12, 450), "white")
    for k, im in enumerate(ims): g.paste(im, (k * 372, 0))
    g.save(os.path.join(out, "previa.png"))


if __name__ == "__main__":
    sp = sys.argv[1]; spec = json.load(open(sp)); asyncio.run(render(spec, os.path.dirname(os.path.abspath(sp))))
