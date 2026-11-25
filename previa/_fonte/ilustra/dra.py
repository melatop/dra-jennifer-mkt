"""Personagem vetorial da Dra. Jennifer no estilo dos bonecos do canal @dicasmiau
(contorno escuro grosso, cores chapadas). Gera SVG de busto (da cintura para cima)
com duas poses de braço: 'cruzados' e 'frente' (mãos à frente, segurando/examinando).
Quadro: 1000 x 1200. Uso: from dra import dra_svg; dra_svg('frente')"""

INK = "#180600"
PELE, PELE_S = "#F7CBAA", "#E9AE8C"
CABELO, CABELO_S, CABELO_L = "#E8C27A", "#C99A4E", "#F6DDA4"
JALECO, JALECO_S = "#FFFFFF", "#E4E1E6"
SCRUB = "#5897A0"
BLUSA, BLUSA_S = "#B9D6F0", "#9DC0E2"
ESTETO = "#3B3F4A"
BOCHECHA = "#F2A3A8"
SW = 12


def _cabelo_tras():
    return (f'<path d="M318 300 C300 170 400 96 500 96 C612 96 708 170 690 310 C684 420 720 500 742 610 '
            f'C760 700 720 760 690 790 C690 700 672 640 640 600 L360 600 C330 640 312 700 312 790 '
            f'C282 760 242 700 260 610 C282 500 324 420 318 300 Z" fill="{CABELO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M290 560 C300 620 300 690 312 760 M712 560 C702 620 700 690 690 760" fill="none" stroke="{CABELO_S}" stroke-width="10" stroke-linecap="round"/>')


def _rosto():
    return (
        # pescoço
        f'<path d="M455 440 L455 540 L545 540 L545 440 Z" fill="{PELE_S}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        # rosto
        f'<path d="M380 300 C380 200 432 160 500 160 C568 160 620 200 620 300 C620 400 566 466 500 466 C434 466 380 400 380 300 Z" fill="{PELE}" stroke="{INK}" stroke-width="{SW}"/>'
        # orelhas
        f'<path d="M384 300 C360 296 356 344 388 350" fill="{PELE}" stroke="{INK}" stroke-width="{SW}" stroke-linecap="round"/>'
        f'<path d="M616 300 C640 296 644 344 612 350" fill="{PELE}" stroke="{INK}" stroke-width="{SW}" stroke-linecap="round"/>'
        # olhos (arcos sorridentes, como os dos gatos), sobrancelhas, bochechas, boca
        f'<path d="M430 312 Q450 290 470 312 M530 312 Q550 290 570 312" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
        f'<path d="M424 270 Q448 256 474 266 M526 266 Q552 256 576 270" fill="none" stroke="{CABELO_S}" stroke-width="9" stroke-linecap="round"/>'
        f'<ellipse cx="428" cy="358" rx="22" ry="13" fill="{BOCHECHA}" opacity=".75"/><ellipse cx="572" cy="358" rx="22" ry="13" fill="{BOCHECHA}" opacity=".75"/>'
        f'<path d="M458 372 Q500 418 542 372 Q500 386 458 372 Z" fill="#FFFFFF" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>'
        f'<path d="M492 338 Q500 346 508 338" fill="none" stroke="{PELE_S}" stroke-width="7" stroke-linecap="round"/>'
    )


def _franja():
    # repartido de lado, mecha grande caindo para a direita da imagem
    return (f'<path d="M372 318 C356 210 420 140 506 136 C590 132 652 190 640 300 C624 250 600 220 560 206 '
            f'C520 240 456 250 420 246 C400 270 384 292 372 318 Z" fill="{CABELO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M470 156 C520 160 580 186 610 236" fill="none" stroke="{CABELO_L}" stroke-width="10" stroke-linecap="round"/>'
            # mechas da frente sobre os ombros
            f'<path d="M640 300 C664 380 672 460 700 540 C716 590 700 640 668 660 C660 600 640 560 618 520 C626 460 628 380 640 300 Z" fill="{CABELO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M372 318 C350 390 344 470 316 540 C300 590 316 640 348 660 C356 600 376 560 392 520 C384 460 380 390 372 318 Z" fill="{CABELO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
            f'<path d="M668 660 C690 676 712 668 716 646 M348 660 C326 676 304 668 300 646" fill="none" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
            f'<path d="M660 420 C668 480 682 540 676 600 M352 420 C344 480 330 540 336 600" fill="none" stroke="{CABELO_S}" stroke-width="8" stroke-linecap="round"/>')


def _tronco():
    return (
        # jaleco
        f'<path d="M500 528 L330 566 C270 582 236 630 232 700 L226 1200 L774 1200 L768 700 C764 630 730 582 670 566 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        # scrub teal (decote em V)
        f'<path d="M430 548 L500 690 L570 548 Z" fill="{SCRUB}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        f'<path d="M455 548 L500 640 L545 548" fill="{PELE_S}" stroke="{INK}" stroke-width="9" stroke-linejoin="round"/>'
        # lapelas
        f'<path d="M430 548 L500 760 L420 700 L380 600 Z" fill="{JALECO}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        f'<path d="M570 548 L500 760 L580 700 L620 600 Z" fill="{JALECO}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        f'<path d="M500 760 L500 1200" stroke="{JALECO_S}" stroke-width="8"/>'
        f'<circle cx="520" cy="900" r="9" fill="{JALECO_S}" stroke="{INK}" stroke-width="5"/><circle cx="520" cy="1020" r="9" fill="{JALECO_S}" stroke="{INK}" stroke-width="5"/>'
        # bolso com caneta
        f'<path d="M598 760 h90 v70 h-90 z" fill="none" stroke="{JALECO_S}" stroke-width="8"/>'
        f'<path d="M620 760 v-34" stroke="{SCRUB}" stroke-width="10" stroke-linecap="round"/>'
    )


def _estetoscopio():
    return (f'<path d="M412 556 C392 640 398 740 430 800 M588 556 C608 640 602 720 584 770" fill="none" stroke="{ESTETO}" stroke-width="14" stroke-linecap="round"/>'
            f'<path d="M430 800 C440 840 452 860 452 880" fill="none" stroke="{ESTETO}" stroke-width="14" stroke-linecap="round"/>'
            f'<circle cx="452" cy="896" r="22" fill="#C7CCD4" stroke="{INK}" stroke-width="9"/>'
            f'<circle cx="584" cy="780" r="13" fill="{ESTETO}" stroke="{INK}" stroke-width="6"/>')


def _bracos_cruzados():
    return (
        # mangas (braços) pelos lados até o cotovelo
        f'<path d="M236 690 C214 780 214 880 236 950 L320 950 C306 870 304 780 306 720 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M764 690 C786 780 786 880 764 950 L680 950 C694 870 696 780 694 720 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        # antebraço de trás (vai da esquerda para a direita, mão aparece à direita)
        f'<path d="M236 900 C330 870 560 870 690 888 C716 892 724 940 698 950 C560 966 330 966 248 958 C222 950 220 910 236 900 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M640 880 C676 862 716 866 726 890 C734 914 712 930 680 928 Z" fill="{PELE}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        # antebraço da frente (da direita para a esquerda)
        f'<path d="M764 930 C670 908 440 908 310 926 C284 930 276 978 302 988 C440 1004 670 1004 752 996 C778 988 780 944 764 930 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M360 918 C324 900 284 904 274 928 C266 952 288 968 320 966 Z" fill="{PELE}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        f'<path d="M420 960 C520 952 620 952 700 962" fill="none" stroke="{JALECO_S}" stroke-width="7" stroke-linecap="round"/>'
    )


def _bracos_frente():
    # mangas descem pelos lados e os antebraços vêm para o centro, mãos abertas embaixo
    return (
        f'<path d="M236 690 C206 820 210 960 250 1060 C280 1110 340 1120 400 1104 L410 1040 C350 1040 316 1010 306 960 C300 880 300 800 300 720 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M764 690 C794 820 790 960 750 1060 C720 1110 660 1120 600 1104 L590 1040 C650 1040 684 1010 694 960 C700 880 700 800 700 720 Z" fill="{JALECO}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M400 1036 C430 1028 468 1034 484 1052 C496 1066 488 1084 470 1086 L404 1108 Z" fill="{PELE}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        f'<path d="M600 1036 C570 1028 532 1034 516 1052 C504 1066 512 1084 530 1086 L596 1108 Z" fill="{PELE}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
    )


def _tronco_casa():
    return (
        f'<path d="M500 530 L340 562 C276 578 238 628 234 700 L228 1200 L772 1200 L766 700 C762 628 724 578 660 562 Z" fill="{BLUSA}" stroke="{INK}" stroke-width="{SW}" stroke-linejoin="round"/>'
        f'<path d="M420 552 C440 620 560 620 580 552 Z" fill="{PELE_S}" stroke="{INK}" stroke-width="10" stroke-linejoin="round"/>'
        f'<path d="M420 552 C440 620 560 620 580 552" fill="none" stroke="{BLUSA_S}" stroke-width="16" stroke-linecap="round" transform="translate(0 10)"/>'
        f'<path d="M330 760 C360 840 360 980 340 1100 M670 760 C640 840 640 980 660 1100" fill="none" stroke="{BLUSA_S}" stroke-width="8" stroke-linecap="round"/>'
    )


def _bracos_frente_casa():
    return _bracos_frente().replace(f'fill="{JALECO}"', f'fill="{BLUSA}"')


def _bracos_cruzados_casa():
    return _bracos_cruzados().replace(f'fill="{JALECO}"', f'fill="{BLUSA}"').replace(f'stroke="{JALECO_S}"', f'stroke="{BLUSA_S}"')


def dra_svg(bracos="cruzados", standalone=True, roupa="jaleco"):
    if roupa == "casa":
        meio = _tronco_casa() + (_bracos_cruzados_casa() if bracos == "cruzados" else _bracos_frente_casa())
    else:
        meio = _tronco() + _estetoscopio() + (_bracos_cruzados() if bracos == "cruzados" else _bracos_frente())
    corpo = _cabelo_tras() + meio + _rosto() + _franja()
    g = f'<g>{corpo}</g>'
    if not standalone:
        return g
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1200" width="1000" height="1200">{g}</svg>'


if __name__ == "__main__":
    for b in ("cruzados", "frente"):
        open(f"dra-{b}.svg", "w").write(dra_svg(b))
        open(f"dra-{b}-casa.svg", "w").write(dra_svg(b, roupa="casa"))
