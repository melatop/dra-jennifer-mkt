#!/usr/bin/env python3
"""Carrossel no estilo do perfil antigo da Dra. Jennifer (fundo rosado, título serifado centralizado
com destaque em pílula teal, rabisco teal, traço rosa, foto real na capa, figurinhas da Dra. e card branco).
Uso: python3 build2.py spec.json  ->  <saida>/NN-nome.png + previa.png"""
import json, sys, os, asyncio, base64, html as H
from playwright.async_api import async_playwright
from PIL import Image

W, HG = 1080, 1350
AQUI = os.path.dirname(os.path.abspath(__file__))


def uri(p):
    ext = "jpeg" if p.lower().endswith((".jpg", ".jpeg")) else "png"
    return f"data:image/{ext};base64," + base64.b64encode(open(p, "rb").read()).decode()


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:'Carlito',sans-serif;color:#2D2D2D;position:relative;
  background:linear-gradient(170deg,#FDF4F7 0%,#F8E6EC 55%,#F3DCE5 100%);-webkit-font-smoothing:antialiased}
h1,h2{font-family:'Caladea',serif;font-weight:700;color:#6D2E46;text-align:center;letter-spacing:-.5px}
mark{background:#CFE8EA;color:#6D2E46;padding:0 18px;border-radius:22px;-webkit-box-decoration-break:clone;box-decoration-break:clone}
.rab{position:absolute;width:58px;height:44px}
.traco{display:block;margin:26px auto 0;width:300px;height:26px}
.foot{position:absolute;left:60px;right:60px;bottom:34px;display:flex;justify-content:space-between;align-items:center;font-size:24px;color:#87495E}
.foot .h{display:flex;align-items:center;gap:10px}.foot svg{width:24px;height:24px}
.foot .sw{font-weight:700;letter-spacing:2px;font-size:22px;display:flex;align-items:center;gap:10px}
.chip{display:inline-block;background:#87495E;color:#fff;font-weight:700;font-size:24px;letter-spacing:3px;text-transform:uppercase;padding:9px 22px;border-radius:999px}
.card{position:absolute;left:70px;right:70px;background:#fff;border-radius:30px;padding:34px 40px 34px 40px;display:flex;gap:28px;align-items:center;box-shadow:0 10px 30px rgba(109,46,70,.10)}
.card .pata{flex:none;width:86px;height:86px;border-radius:50%;background:#87495E;display:flex;align-items:center;justify-content:center}
.card .pata svg{width:46px;height:46px}
.card p{font-size:33px;line-height:1.38}
.ref{position:absolute;left:50%;transform:translateX(-50%);background:rgba(255,255,255,.94);color:#6D2E46;font-weight:700;font-size:22px;letter-spacing:2px;padding:10px 22px;border-radius:999px;text-transform:uppercase;white-space:nowrap}
"""
PAW = '<svg viewBox="0 0 40 40" fill="currentColor"><ellipse cx="9" cy="16" rx="3.8" ry="4.8"/><ellipse cx="16" cy="8.5" rx="3.8" ry="5"/><ellipse cx="24" cy="8.5" rx="3.8" ry="5"/><ellipse cx="31" cy="16" rx="3.8" ry="4.8"/><path d="M20 19c-5 0-10 6-10 11 0 4 3 5 6 4.4 2-.4 2.7-1 4-1s2 .6 4 1c3 .6 6-.4 6-4.4 0-5-5-11-10-11z"/></svg>'
PAW_B = PAW.replace('currentColor', '#FFFFFF')
ARROW = '<svg viewBox="0 0 44 20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="width:40px;height:18px"><path d="M2 10h38M31 2l9 8-9 8"/></svg>'
RAB = '<svg class="rab" viewBox="0 0 58 44" fill="none" stroke="#5897A0" stroke-width="5" stroke-linecap="round"><path d="M6 8l40 6M6 24h46M6 40l40-6"/></svg>'
TRACO = '<svg class="traco" viewBox="0 0 300 26" fill="none" stroke-linecap="round"><path d="M6 16C80 6 200 4 294 10" stroke="#D1899D" stroke-width="7"/><path d="M30 22C110 14 200 14 270 18" stroke="#D1899D" stroke-width="3" opacity=".6"/></svg>'


def foot(i, n, handle="@jenniferaragao.vet", claro=False):
    cor = ' style="color:#FFFFFF"' if claro else ''
    return (f'<div class="foot"{cor}><span class="h">{PAW}{H.escape(handle)}</span>'
            + (f'<span class="sw">ARRASTE {ARROW}</span>' if n > 1 and i <= 2 else '') + '</div>')


def page(body, css=""):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{CSS}{css}</style></head><body>{body}</body></html>'


def slide(s, i, n, base):
    t = s["tipo"]
    if t == "capa":
        foto = uri(os.path.join(base, s["foto"]))
        css = f""".foto{{position:absolute;left:0;right:0;bottom:0;height:{s.get('altura_foto', 820)}px;background:url('{foto}') {s.get('foco','center')}/cover;
          -webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 16%);mask-image:linear-gradient(to bottom,transparent 0,#000 16%)}}
          .topo{{position:absolute;left:60px;right:60px;top:84px;text-align:center}}
          h1{{font-size:{s.get('tamanho', 80)}px;line-height:1.16}}
          .sub{{margin-top:22px;font-size:36px;color:#87495E;text-align:center}}
          .rab{{right:70px;top:{s.get('rab_y', 120)}px}}
          .foot{{background:rgba(255,255,255,.88);left:0;right:0;bottom:0;padding:16px 60px}}"""
        ref = f'<div class="ref" style="bottom:110px">Foto a tirar · referência</div>' if s.get("referencia") else ''
        body = (f'<div class="foto"></div>{ref}<div class="topo"><h1>{s["titulo"]}</h1>'
                + (f'<p class="sub">{s["subtitulo"]}</p>' if s.get("subtitulo") else '') + TRACO + '</div>' + RAB + foot(i, n))
        return page(body, css)
    if t == "topico":
        fig = uri(os.path.join(base, s["figurinha"]))
        css = f""".topo{{position:absolute;left:70px;right:70px;top:96px;text-align:center}}
          h2{{margin-top:30px;font-size:{s.get('tamanho', 70)}px;line-height:1.2}}
          .fig{{position:absolute;left:50%;transform:translateX(-50%) rotate({s.get('giro', -3)}deg);bottom:{s.get('fig_y', 420)}px;height:{s.get('fig_h', 420)}px;filter:drop-shadow(0 8px 14px rgba(109,46,70,.18))}}
          .card{{bottom:120px}}
          .rab{{left:70px;top:110px;transform:scaleX(-1)}}"""
        body = (f'<div class="topo">' + (f'<span class="chip">{s["rotulo"]}</span>' if s.get("rotulo") else '')
                + f'<h2>{s["titulo"]}</h2>{TRACO}</div>{RAB}<img class="fig" src="{fig}" alt="">'
                + f'<div class="card"><span class="pata">{PAW_B}</span><p>{s["corpo"]}</p></div>' + foot(i, n))
        return page(body, css)
    if t == "cta":
        logo = uri(os.path.join(base, "logo.png"))
        fig = uri(os.path.join(base, s["figurinha"])) if s.get("figurinha") else None
        css = f""".logo{{position:absolute;left:50%;transform:translateX(-50%);top:110px;width:560px}}
          .meio{{position:absolute;left:70px;right:70px;top:540px;text-align:center}}
          h2{{font-size:{s.get('tamanho', 70)}px;line-height:1.2}}
          .sub{{margin-top:20px;font-size:38px;color:#5897A0;font-family:'Caladea',serif;font-style:italic}}
          .bt{{margin:36px auto 0;display:inline-flex;align-items:center;gap:16px;background:#87495E;color:#fff;font-weight:700;font-size:34px;padding:24px 50px;border-radius:999px}}
          .fig{{position:absolute;right:60px;bottom:96px;height:{s.get('fig_h', 300)}px;transform:rotate(4deg);filter:drop-shadow(0 8px 14px rgba(109,46,70,.18))}}"""
        body = (f'<img class="logo" src="{logo}" alt=""><div class="meio"><h2>{s["titulo"]}</h2>'
                + (f'<p class="sub">{s["subtitulo"]}</p>' if s.get("subtitulo") else '')
                + (f'<div class="bt">{H.escape(s["botao"])} {ARROW}</div>' if s.get("botao") else '') + '</div>'
                + (f'<img class="fig" src="{fig}" alt="">' if fig else '') + foot(i, n))
        return page(body, css)
    raise ValueError(t)


CHECK = """() => { const av=[]; const R=e=>e.getBoundingClientRect();
  if(!document.fonts.check('700 60px Caladea')) av.push('fonte');
  document.querySelectorAll('h1,h2,.sub,.card,.chip,.bt').forEach(el=>{const r=R(el); if(r.left<40||r.right>1040) av.push(el.className||el.tagName+': sai da margem');});
  const t=document.querySelector('h1,h2'), c=document.querySelector('.card'), f=document.querySelector('.fig'), tr=document.querySelector('.traco');
  if(c&&tr&&f){ if(R(f).top<R(tr).bottom+10) av.push('figurinha encosta no título ('+Math.round(R(f).top-R(tr).bottom)+'px)'); if(R(f).bottom>R(c).top+60) av.push('figurinha cobre o card'); }
  if(c&&R(c).bottom>1300) av.push('card invade rodapé');
  const m=document.querySelector('.meio'); if(m&&R(m).bottom>1240) av.push('texto do CTA desce demais');
  if(f&&document.querySelector('.meio')&&R(f).top<R(m).bottom-20&&R(f).left<R(m).right) av.push('figurinha do CTA sobre o texto');
  return av; }"""


async def render(spec, base):
    out = spec["saida"]; os.makedirs(out, exist_ok=True)
    n = len(spec["slides"]); pngs = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": W, "height": HG})
        for i, s in enumerate(spec["slides"], 1):
            if spec.get("somente") and i not in spec["somente"]: continue
            f = os.path.join(out, f"_{i:02d}.html"); open(f, "w").write(slide(s, i, n, base))
            await pg.goto("file://" + f); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(200)
            av = await pg.evaluate(CHECK)
            png = os.path.join(out, f"{i:02d}-{s.get('nome','slide')}.png"); await pg.screenshot(path=png); pngs.append(png)
            print(os.path.basename(png), "OK" if not av else av)
        await b.close()
    ims = [Image.open(x).resize((360, 450)) for x in pngs]
    cols = min(len(ims), 6); rows = (len(ims) + cols - 1) // cols
    g = Image.new("RGB", (cols * 372 - 12, rows * 462 - 12), "white")
    for k, im in enumerate(ims): g.paste(im, ((k % cols) * 372, (k // cols) * 462))
    g.save(os.path.join(out, "previa.png"))


if __name__ == "__main__":
    sp = sys.argv[1]; spec = json.load(open(sp)); asyncio.run(render(spec, os.path.dirname(os.path.abspath(sp))))
