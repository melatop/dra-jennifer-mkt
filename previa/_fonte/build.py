#!/usr/bin/env python3
"""Gera e renderiza um carrossel da Dra. Jennifer Aragão a partir de um spec JSON.
Uso: python3 build.py spec.json
Saída: <out>/NN-<slug>.png (1080x1350), <out>/previa.png, <out>/revisao-layout.json e os .html em <out>/_html/.
"""
import json, sys, os, re, shutil, asyncio, html as H
from playwright.async_api import async_playwright
from PIL import Image

W, HGT = 1080, 1350
C = dict(mauve="#87495E", mauve_dark="#6D2E46", teal="#5897A0", pink="#D1899D", ink="#2D2D2D",
         bg_rosa="#FAEEF3", bg_teal="#F0F8F9", bg_cta="#FCF8F9",
         on_dark="#FBF5F7", pink_light="#F0B9C8", teal_light="#A9D3D9", body_dark="#EBD9E0")

BASE_CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{HGT}px;overflow:hidden}}
body{{font-family:'Carlito','Calibri',sans-serif;color:{C['ink']};position:relative;-webkit-font-smoothing:antialiased}}
h1,h2{{font-family:'Caladea','Cambria',serif;font-weight:700}}
.kw{{background-image:linear-gradient({C['pink']},{C['pink']});background-repeat:no-repeat;background-size:100% 6px;background-position:0 92%;padding-bottom:4px}}
.foot{{position:absolute;left:80px;right:80px;top:1168px;height:52px;border-top:1.5px solid {C['pink']};display:flex;align-items:flex-end;justify-content:space-between}}
.handle{{font-size:26px;letter-spacing:.5px;color:{C['teal']};display:flex;align-items:center;gap:12px}}
.handle svg{{width:28px;height:28px}}
.swipe{{font-size:26px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:{C['mauve']};display:flex;align-items:center;gap:12px}}
.swipe svg{{width:44px;height:20px}}
.content{{position:absolute;left:80px;width:920px;bottom:252px}}
h2{{font-size:80px;line-height:1.08;color:{C['mauve']};letter-spacing:-.5px}}
.rule{{margin-top:44px;width:96px;height:2px;background:{C['pink']}}}
.body{{margin-top:40px;width:860px;font-size:36px;line-height:1.42;color:{C['ink']}}}
.label{{font-size:26px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:{C['teal']}}}
.head{{position:absolute;left:80px;right:80px;top:176px;display:flex;align-items:flex-end;justify-content:space-between}}
"""
PAW = '<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.4"><ellipse cx="9" cy="16" rx="3.6" ry="4.6"/><ellipse cx="16" cy="8.5" rx="3.6" ry="4.8"/><ellipse cx="24" cy="8.5" rx="3.6" ry="4.8"/><ellipse cx="31" cy="16" rx="3.6" ry="4.6"/><path d="M20 19c-5 0-10 6-10 11 0 4 3 5 6 4.4 2-.4 2.7-1 4-1s2 .6 4 1c3 .6 6-.4 6-4.4 0-5-5-11-10-11z"/></svg>'
ARROW = '<svg viewBox="0 0 44 20" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M2 10h38M31 2l9 8-9 8"/></svg>'

def foot(handle, swipe):
    return (f'<div class="foot"><div class="handle">{PAW}{H.escape(handle)}</div>'
            + (f'<div class="swipe">Arraste {ARROW}</div>' if swipe else '') + '</div>')

def page(bg, css, body):
    return f'<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><style>{BASE_CSS}body{{background:{bg}}}{css}</style></head><body>{body}</body></html>'

def text_block(s, dark=False):
    out = f'<h2>{s["titulo"]}</h2><div class="rule"></div>'
    if s.get("corpo"): out += f'<p class="body">{s["corpo"]}</p>'
    if s.get("destaque"):
        out += f'<p class="callout">{s["destaque"]}</p>'
    return f'<div class="content">{out}</div>'

DARK_CSS = f"""h2{{color:{C['on_dark']}}}.body{{color:{C['body_dark']}}}
.foot{{border-top-color:rgba(209,137,157,.7)}}.foot .handle{{color:{C['teal_light']}}}.foot .swipe{{color:{C['on_dark']}}}
.callout{{margin-top:44px;padding:26px 0 26px 34px;border-left:5px solid {C['pink']};font-family:'Caladea',serif;font-style:italic;font-size:44px;line-height:1.2;color:{C['on_dark']}}}
.callout b{{font-style:normal;color:{C['pink_light']}}}.label{{color:{C['teal_light']}}}"""
LIGHT_CALLOUT = f".callout{{margin-top:44px;padding:22px 0 22px 34px;border-left:5px solid {C['pink']};font-family:'Caladea',serif;font-style:italic;font-size:42px;line-height:1.2;color:{C['mauve_dark']}}}"

def build_slide(s, i, n, spec, bg_light):
    handle = spec.get("handle", "@jenniferaragao.vet")
    swipe = i <= 2 and n > 1
    t = s["tipo"]
    if t == "capa":
        css = f""".photo{{position:absolute;inset:0;width:{W}px;height:{HGT}px;object-fit:cover;object-position:{s.get('foco','center top')}}}
.scrim{{position:absolute;inset:0;background:linear-gradient(to bottom,rgba(109,46,70,0) 0%,rgba(109,46,70,0) 42%,rgba(109,46,70,.72) 56%,rgba(109,46,70,.94) 66%,{C['mauve_dark']} 76%)}}
.content{{bottom:214px}}h1{{font-size:{s.get('tamanho_titulo',80)}px;line-height:1.06;color:{C['on_dark']};letter-spacing:-.5px}}h1 em{{font-style:normal;color:{C['pink_light']}}}
.sub{{margin-top:30px;font-size:38px;line-height:1.3;color:{C['on_dark']}}}.sub i{{color:{C['pink_light']}}}
.foot{{border-top-color:rgba(209,137,157,.7)}}.foot .handle{{color:{C['teal_light']}}}.foot .swipe{{color:{C['on_dark']}}}"""
        body = (f'<img class="photo" src="{s["foto"]}" alt=""><div class="scrim"></div>'
                f'<div class="content"><h1>{s["titulo"]}</h1>' + (f'<p class="sub">{s["subtitulo"]}</p>' if s.get("subtitulo") else '') + '</div>'
                + foot(handle, swipe))
        return page(C['mauve_dark'], css, body)
    if t == "texto":
        css = LIGHT_CALLOUT + f""".topo{{position:absolute;left:80px;right:80px;top:186px;height:150px;display:flex;align-items:center;gap:26px}}
.topo svg{{height:118px;width:auto}}.topo .op{{font-family:'Caladea',serif;font-size:84px;line-height:1;color:{C['pink']}}}"""
        topo = f'<div class="topo">{s["topo"]}</div>' if s.get("topo") else ''
        return page(bg_light, css, topo + text_block(s) + foot(handle, swipe))
    if t == "enfase":
        css = DARK_CSS + ".topo{position:absolute;left:80px;right:80px;top:186px}.topo svg{display:block;margin-top:30px;width:920px;height:110px}"
        topo = '<div class="topo">' + (f'<div class="label">{s["kicker"]}</div>' if s.get("kicker") else '') + s.get("topo", "") + '</div>'
        return page(C['mauve_dark'], css, topo + text_block(s, True) + foot(handle, swipe))
    if t == "dica":
        css = LIGHT_CALLOUT + f""".num{{display:flex;align-items:baseline;gap:22px}}
.num b{{font-family:'Caladea',serif;font-size:230px;line-height:.8;font-weight:400;color:{C['teal']};letter-spacing:-6px}}
.icon{{width:176px;height:150px}}"""
        head = (f'<div class="head"><div class="num"><b id="numero">{s["numero"]}</b><span class="label">{s.get("rotulo","Dica")}</span></div>'
                f'<div class="icon" id="icone">{s["icone"]}</div></div>')
        return page(bg_light, css, head + text_block(s) + foot(handle, swipe))
    if t == "trio":
        css = LIGHT_CALLOUT + f""".trio{{position:absolute;left:80px;right:80px;top:160px;display:grid;grid-template-columns:1fr 1fr 1fr}}
.trio::before{{content:"";position:absolute;left:16.66%;right:16.66%;top:80px;border-top:2px dashed {C['pink']}}}
.trio div{{position:relative;display:flex;flex-direction:column;align-items:center;gap:22px}}
.trio i{{width:160px;height:160px;border-radius:50%;border:2px solid {C['teal']};background:{bg_light};display:flex;align-items:center;justify-content:center}}
.trio svg{{width:92px;height:92px}}.trio span{{font-size:26px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:{C['teal']};text-align:center}}"""
        items = ''.join(f'<div><i>{it["icone"]}</i><span>{H.escape(it["rotulo"])}</span></div>' for it in s["itens"])
        return page(bg_light, css, f'<div class="trio">{items}</div>' + text_block(s) + foot(handle, swipe))
    if t == "cta":
        css = f""".logo{{position:absolute;left:50%;top:150px;transform:translateX(-50%);width:720px}}
.content{{left:80px;right:80px;width:auto;bottom:auto;top:676px;text-align:center}}h2{{font-size:72px;line-height:1.1}}
.sub{{margin-top:18px;font-family:'Caladea',serif;font-style:italic;font-size:46px;color:{C['teal']}}}
.cta{{margin:44px auto 0;display:inline-flex;align-items:center;gap:18px;background:{C['mauve']};color:{C['on_dark']};font-size:36px;font-weight:700;letter-spacing:.5px;padding:26px 52px;border-radius:999px}}.cta svg{{width:40px;height:20px}}"""
        body = (f'<img class="logo" src="{spec["logo"]}" alt="Dra. Jennifer Aragão – Medicina Felina">'
                f'<div class="content"><h2>{s["titulo"]}</h2>' + (f'<p class="sub">{s["subtitulo"]}</p>' if s.get("subtitulo") else '')
                + f'<div class="cta">{H.escape(s.get("botao","Agende pelo link da bio"))} {ARROW}</div></div>' + foot(handle, swipe))
        return page(C['bg_cta'], css, body)
    raise ValueError(f"tipo desconhecido: {t}")

ALIGN_JS = """() => {
  const n = document.getElementById('numero'), ic = document.getElementById('icone');
  if (!n || !ic) return null;
  const cs = getComputedStyle(n), ctx = document.createElement('canvas').getContext('2d');
  ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
  const m = ctx.measureText(n.textContent);
  const probe = document.createElement('span'); probe.style.cssText = 'display:inline-block;width:0;height:0;vertical-align:baseline';
  n.appendChild(probe); const base = probe.getBoundingClientRect().bottom; probe.remove();
  const glyphC = base - (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2;
  const svg = ic.querySelector('svg'); const bb = svg.getBBox(); const ctm = svg.getScreenCTM();
  const iconC = ctm.f + ctm.d * (bb.y + bb.height / 2);
  ic.style.transform = `translateY(${glyphC - iconC}px)`;
  return glyphC - iconC;
}"""

CHECK_JS = """(tipo) => {
  const av = [], R = e => e.getBoundingClientRect(), q = s => document.querySelector(s);
  const lines = el => { const ys = new Set(), w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) { const r = document.createRange(); r.selectNodeContents(n);
      for (const b of r.getClientRects()) if (b.width > 1) ys.add(Math.round(b.top / 10)); } return ys.size; };
  const lastLineWords = el => { const ws = []; const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT); let n;
    while ((n = w.nextNode())) { const re = /\\S+/g; let m; while ((m = re.exec(n.data))) { const r = document.createRange();
      r.setStart(n, m.index); r.setEnd(n, m.index + m[0].length); ws.push(Math.round(r.getBoundingClientRect().top)); } }
    if (!ws.length) return 0; const last = Math.max(...ws); return ws.filter(t => Math.abs(t - last) < 8).length; };
  if (!document.fonts.check("700 80px Caladea") || !document.fonts.check("36px Carlito")) av.push("fonte Caladea/Carlito não carregou");
  const c = q('.content'), t = q('.head') || q('.topo') || q('.trio') || q('.logo');
  if (c && t) { const gap = R(c).top - R(t).bottom; if (gap < 48) av.push(`respiro de ${Math.round(gap)}px entre o elemento do topo e o texto (mín. 48): enxugue o texto`); }
  document.querySelectorAll('h1,h2,.body,.callout,.sub,.cta,.topo,.trio span').forEach(el => {
    const r = R(el), nm = el.className || el.tagName.toLowerCase();
    if (el.scrollWidth > el.clientWidth + 2) av.push(`${nm}: conteúdo vaza na horizontal (palavra ou SVG largo demais)`);
    if (r.left < 79 || r.right > 1001) av.push(`${nm}: sai da margem de 80px`);
    if (r.bottom > 1168 && !el.closest('.foot')) av.push(`${nm}: invade o rodapé (termina em ${Math.round(r.bottom)}px)`);
  });
  const h = q('h1') || q('h2');
  if (h) { const n = lines(h), max = tipo === 'capa' ? 4 : 3; if (n > max) av.push(`título com ${n} linhas (máx. ${max})`);
    if (tipo !== 'capa' && h.querySelectorAll('.kw').length !== 1) av.push(`título com ${h.querySelectorAll('.kw').length} palavras-chave sublinhadas (deve ser 1)`);
    if (tipo === 'capa' && R(h).top < 720) av.push(`título da capa começa em ${Math.round(R(h).top)}px, acima do degradê (perde contraste e pode cobrir rostos)`); }
  const b = q('.body');
  if (b) { const nw = b.innerText.trim().split(/\\s+/).length; if (nw > 25) av.push(`corpo com ${nw} palavras (máx. ~25)`);
    if (lines(b) > 1 && lastLineWords(b) === 1) av.push('corpo termina com uma palavra sozinha na última linha (viúva)'); }
  return av;
}"""

async def render(files, outdir):
    rel = {}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': W, 'height': HGT})
        for f, png, tipo in files:
            await pg.goto('file://' + os.path.abspath(f)); await pg.evaluate('document.fonts.ready'); await pg.wait_for_timeout(250)
            await pg.evaluate(ALIGN_JS)
            rel[os.path.basename(png)] = await pg.evaluate(CHECK_JS, tipo)
            await pg.screenshot(path=png)
        await b.close()
    json.dump(rel, open(os.path.join(outdir, "revisao-layout.json"), "w"), ensure_ascii=False, indent=2)
    tot = sum(len(v) for v in rel.values())
    print(f"\nREVISÃO DE LAYOUT: {tot} aviso(s)")
    for k, v in rel.items():
        for a in v: print(f"  {k}: {a}")

def slug(t):
    t = re.sub(r'<[^>]+>', '', t).lower()
    for a, b_ in zip('áàâãéêíóôõúç', 'aaaaeeiooouc'): t = t.replace(a, b_)
    return re.sub(r'[^a-z0-9]+', '-', t).strip('-')[:28]

def main(spec_path):
    spec = json.load(open(spec_path)); base = os.path.dirname(os.path.abspath(spec_path))
    out = spec["saida"]; hd = os.path.join(out, "_html"); os.makedirs(hd, exist_ok=True)
    for k in ("logo",):
        if spec.get(k): shutil.copy(os.path.join(base, spec[k]), hd); spec[k] = os.path.basename(spec[k])
    slides = spec["slides"]; n = len(slides); files = []; light = 0
    for i, s in enumerate(slides, 1):
        if s.get("foto"): shutil.copy(os.path.join(base, s["foto"]), hd); s["foto"] = os.path.basename(s["foto"])
        bg = s.get("fundo")
        if not bg and s["tipo"] in ("texto", "dica", "trio"):
            bg = C['bg_rosa'] if light % 2 == 0 else C['bg_teal']; light += 1
        if s.get("foto"):
            w_, h_ = Image.open(os.path.join(hd, s["foto"])).size
            if w_ < 1080 or h_ < 1350: print(f"AVISO: foto do slide {i} tem {w_}x{h_}px (ideal >= 1080x1350); vai ampliar e perder nitidez.")
        if spec.get("somente") and i not in spec["somente"]: continue
        f = os.path.join(hd, f"{i:02d}.html"); open(f, 'w').write(build_slide(s, i, n, spec, bg))
        files.append((f, os.path.join(out, f"{i:02d}-{s.get('nome') or slug(s['titulo'])}.png"), s["tipo"]))
    asyncio.run(render(files, out))
    ims = [Image.open(p).resize((360, 450)) for _, p, _ in files]; cols = min(4, len(files)); rows = (len(files) + cols - 1) // cols
    grid = Image.new('RGB', (cols * 360 + (cols - 1) * 12, rows * 450 + (rows - 1) * 12), 'white')
    for k, im in enumerate(ims): grid.paste(im, ((k % cols) * 372, (k // cols) * 462))
    grid.save(os.path.join(out, "previa.png" if not spec.get("somente") else "previa-aprovacao.png"))
    print("\n".join(p for _, p, _ in files))

if __name__ == "__main__":
    main(sys.argv[1])
