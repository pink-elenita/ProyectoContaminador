from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.units import inch
from datetime import date
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import io
import os

# ── Paleta acorde al programa ────────────────────────────────
MORADO_OSC  = "#1A0A2E"
MORADO_CARD = "#2D1B4E"
MORADO_MED  = "#3D2460"
VERDE       = "#4ADE80"
VERDE_TEXT  = "#064E3B"
BORDE       = "#5B3A8A"
TEXTO_MUTED = "#A78CC0"

PIE_COLORS  = ["#4ADE80", "#7C3AED", "#E040A0"]   # verde, morado, rosa

def _ruta_base():
    return os.path.join(os.path.expanduser("~"), "Downloads")

def _grafica_pastel(transporte_co2, energia_co2, alimentacion_co2):
    """Genera la gráfica de pastel y la devuelve como imagen en memoria."""
    datos   = []
    labels  = []
    colores = []
    nombres = ["Transporte", "Energía", "Alimentación"]
    valores = [transporte_co2, energia_co2, alimentacion_co2]
    cols    = PIE_COLORS

    for i, v in enumerate(valores):
        if v > 0:
            datos.append(v)
            labels.append(f"{nombres[i]}\n{v:.2f} kg CO₂")
            colores.append(cols[i])

    if not datos:
        return None

    fig, ax = plt.subplots(figsize=(5, 3.5),
                           facecolor="#1A0A2E")
    ax.set_facecolor("#1A0A2E")

    wedges, texts, autotexts = ax.pie(
        datos,
        labels=None,
        colors=colores,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops=dict(edgecolor="#2D1B4E", linewidth=2),
        pctdistance=0.75
    )

    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(9)
        at.set_fontweight("bold")

    # Leyenda
    parches = [mpatches.Patch(color=colores[i], label=labels[i])
               for i in range(len(datos))]
    legend = ax.legend(handles=parches,
                       loc="center left",
                       bbox_to_anchor=(1.0, 0.5),
                       frameon=False,
                       labelcolor="white",
                       fontsize=8)

    ax.set_title("Distribución de Huella de Carbono",
                 color="white", fontsize=11, fontweight="bold", pad=12)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150,
                bbox_inches="tight", facecolor="#1A0A2E")
    plt.close(fig)
    buf.seek(0)
    return buf

def exportar_pdf(usuario, actividades):
    carpeta       = _ruta_base()
    nombre_archivo = os.path.join(
        carpeta, f"huella_{usuario}_{date.today().strftime('%Y%m%d')}.pdf"
    )

    doc = SimpleDocTemplate(nombre_archivo, pagesize=letter,
                            rightMargin=48, leftMargin=48,
                            topMargin=48, bottomMargin=48)
    elementos = []

    # ── Estilos ──────────────────────────────────────────────
    def estilo(nombre, **kw):
        base = dict(fontName="Helvetica", fontSize=11,
                    textColor=colors.HexColor(MORADO_OSC))
        base.update(kw)
        return ParagraphStyle(nombre, **base)

    s_titulo   = estilo("titulo", fontSize=15, fontName="Helvetica-Bold",
                         textColor=colors.HexColor(MORADO_CARD), spaceAfter=2)
    s_sub      = estilo("sub", fontSize=11,
                         textColor=colors.HexColor(BORDE), spaceAfter=16)
    s_seccion  = estilo("seccion", fontSize=13, fontName="Helvetica-Bold",
                         textColor=colors.HexColor(MORADO_CARD),
                         spaceBefore=16, spaceAfter=6)
    s_footer   = estilo("footer", fontSize=9,
                         textColor=colors.HexColor(TEXTO_MUTED),
                         alignment=1)

    # ── Encabezado ───────────────────────────────────────────
    header_data = [[
        Paragraph("🌿 Calculadora Huella de Carbono", s_titulo),
        Paragraph(
            f"<b>Usuario:</b> {usuario}<br/>"
            f"<b>Fecha:</b> {date.today().strftime('%d/%m/%Y')}",
            estilo("hdr_right", fontSize=10,
                   textColor=colors.HexColor(BORDE), alignment=2)
        )
    ]]
    header_table = Table(header_data, colWidths=[4*inch, 2.5*inch])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F3F0FF")),
        ("ROUNDEDCORNERS", [10,10,10,10]),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (0,-1), 16),
        ("RIGHTPADDING",  (-1,0), (-1,-1), 16),
    ]))
    elementos.append(header_table)
    elementos.append(Spacer(1, 14))
    elementos.append(HRFlowable(width="100%", thickness=2,
                                color=colors.HexColor(VERDE), spaceAfter=14))

    # ── Tarjetas de totales ──────────────────────────────────
    hoy       = date.today().strftime("%d/%m/%Y")
    total_hoy = sum(a.calcular_co2() for a in actividades if a.fecha == hoy)
    total_all = sum(a.calcular_co2() for a in actividades)

    totales_data = [
        [
            Paragraph("Huella de Hoy",
                      estilo("lbl_hoy", fontSize=10,
                             textColor=colors.HexColor(TEXTO_MUTED))),
            Paragraph("Huella Total",
                      estilo("lbl_tot", fontSize=10,
                             textColor=colors.HexColor(TEXTO_MUTED)))
        ],
        [
            Paragraph(f"<b>{total_hoy:.2f} kg CO₂</b>",
                      estilo("val_hoy", fontSize=18, fontName="Helvetica-Bold",
                             textColor=colors.HexColor(VERDE_TEXT))),
            Paragraph(f"<b>{total_all:.2f} kg CO₂</b>",
                      estilo("val_tot", fontSize=18, fontName="Helvetica-Bold",
                             textColor=colors.HexColor(MORADO_CARD)))
        ]
    ]
    totales_table = Table(totales_data, colWidths=[3.2*inch, 3.2*inch])
    totales_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor(VERDE)),
        ("BACKGROUND", (1,0), (1,-1), colors.HexColor("#EDE9FE")),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ROUNDEDCORNERS", [10,10,10,10]),
        ("BOX", (0,0), (0,-1), 1, colors.HexColor(VERDE)),
        ("BOX", (1,0), (1,-1), 1, colors.HexColor(BORDE)),
    ]))
    elementos.append(totales_table)
    elementos.append(Spacer(1, 18))

    # ── Gráfica de pastel ────────────────────────────────────
    t_co2 = sum(a.calcular_co2() for a in actividades if a.tipo() == "transporte")
    e_co2 = sum(a.calcular_co2() for a in actividades if a.tipo() == "energia")
    a_co2 = sum(a.calcular_co2() for a in actividades if a.tipo() == "alimentacion")

    buf = _grafica_pastel(t_co2, e_co2, a_co2)
    if buf:
        img = Image(buf, width=5.5*inch, height=3.2*inch)
        img.hAlign = "CENTER"
        elementos.append(img)
        elementos.append(Spacer(1, 14))

    # ── Tabla por categoría ──────────────────────────────────
    categorias = [
        ("🚗  Transporte",   "transporte",   VERDE),
        ("⚡  Energía",      "energia",      "#7C3AED"),
        ("🌱  Alimentación", "alimentacion", "#E040A0"),
    ]

    for nombre_cat, tipo, color_cat in categorias:
        acts = [a for a in actividades if a.tipo() == tipo]
        if not acts:
            continue

        elementos.append(Paragraph(nombre_cat, s_seccion))

        data = [["Actividad", "Cantidad", "Fecha", "CO₂ (kg)"]]
        for a in acts:
            data.append([a.nombre, str(a.cantidad), a.fecha,
                         f"{a.calcular_co2():.2f}"])

        tabla = Table(data, colWidths=[2.8*inch, 1.1*inch, 1.1*inch, 1.1*inch])
        tabla.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor(color_cat)),
            ("TEXTCOLOR",     (0,0), (-1,0), colors.white),
            ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0), (-1,0), 10),
            ("ROWBACKGROUNDS",(0,1), (-1,-1),
             [colors.white, colors.HexColor("#F3F0FF")]),
            ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
            ("FONTSIZE",      (0,1), (-1,-1), 9),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ROWHEIGHT",     (0,0), (-1,-1), 22),
            ("BOX",           (0,0), (-1,-1), 1, colors.HexColor(BORDE)),
            ("INNERGRID",     (0,0), (-1,-1), 0.4, colors.HexColor("#D8C8F0")),
            ("ROUNDEDCORNERS",[6,6,6,6]),
        ]))
        elementos.append(tabla)
        elementos.append(Spacer(1, 10))

    # ── Footer ───────────────────────────────────────────────
    elementos.append(Spacer(1, 20))
    elementos.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor(BORDE), spaceAfter=8))
    elementos.append(Paragraph(
        f"Generado por Calculadora Huella de Carbono  ·  {date.today().strftime('%d/%m/%Y')}",
        s_footer
    ))

    doc.build(elementos)
    return nombre_archivo