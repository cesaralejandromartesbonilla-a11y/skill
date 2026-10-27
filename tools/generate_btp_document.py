#!/usr/bin/env python3
"""generate_btp_document.py - Generador de documento técnico PDF formal

Tema: "El perfil del egresado del BTP en Electricidad y Construcciones Metálicas"
Requisitos:
- Mínimo 15 páginas (exactamente 16 páginas en vector A4).
- Distribución de área por página:
  * >15% en imágenes/ilustraciones técnicas (distribuidas en DOS figuras dedicadas por capítulo: X.1 y X.2).
  * ~40% en texto técnico estructurado con rigor curricular, normativo e industrial.
  * ~42% restante en márgenes, interlineado, encabezados y pies de página profesionales.
- Cada subsección (ej. 1.1 y 1.2, 2.1 y 2.2, etc.) cuenta con su propia figura/diagrama técnico.
- Generación con ReportLab 5.1 y Matplotlib 3.10 a 300 DPI.
"""

import os
import sys
from pathlib import Path

# Configuración de codificación UTF-8 para consola Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

PAGE_WIDTH, PAGE_HEIGHT = A4
FIGURES_DIR = Path("export/pdf_figures")
OUTPUT_PDF = Path("export/El_Perfil_del_Egresado_BTP_Electricidad_y_Construcciones_Metalicas.pdf")


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numerar páginas dinámicamente y agregar encabezado/pie."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        page_num = self._pageNumber
        
        # Omitir decoraciones en la portada (página 1)
        if page_num > 1:
            # Encabezado formal
            self.setStrokeColor(colors.HexColor("#1E3A8A"))
            self.setLineWidth(1)
            self.line(36, PAGE_HEIGHT - 32, PAGE_WIDTH - 36, PAGE_HEIGHT - 32)
            
            self.setFont("Helvetica-Bold", 7.5)
            self.setFillColor(colors.HexColor("#1E3A8A"))
            self.drawString(36, PAGE_HEIGHT - 27, "PERFIL DEL EGRESADO — BTP EN ELECTRICIDAD Y CONSTRUCCIONES METÁLICAS")
            
            self.setFont("Helvetica-Oblique", 7.5)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawRightString(PAGE_WIDTH - 36, PAGE_HEIGHT - 27, "Marco Curricular y Estándares Ocupacionales")
            
            # Pie de página formal
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(36, 34, PAGE_WIDTH - 36, 34)
            
            self.setFont("Helvetica", 7.5)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(36, 23, "Bachillerato Técnico Profesional • Educación y Competencias para la Industria 4.0")
            self.drawRightString(PAGE_WIDTH - 36, 23, f"Página {page_num} de {total_pages}")
            
        self.restoreState()


def setup_matplotlib():
    plt.rcParams.update({
        'font.sans-serif': 'DejaVu Sans',
        'font.family': 'sans-serif',
        'axes.edgecolor': '#CBD5E1',
        'axes.linewidth': 0.8,
        'grid.color': '#E2E8F0',
        'grid.linestyle': '--',
        'grid.alpha': 0.6
    })


def create_banner_figure(filepath, title, subtitle, items_left, items_right, color_left='#1E3A8A', color_right='#831843'):
    """Genera una figura tipo banner dual con bloques de interconexión."""
    fig, ax = plt.subplots(figsize=(6.4, 1.35), dpi=300)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')
    
    rect1 = plt.Rectangle((0.03, 0.12), 0.44, 0.76, facecolor=color_left, edgecolor='#60A5FA', lw=1.5, transform=ax.transAxes)
    rect2 = plt.Rectangle((0.53, 0.12), 0.44, 0.76, facecolor=color_right, edgecolor='#F472B6', lw=1.5, transform=ax.transAxes)
    ax.add_patch(rect1)
    ax.add_patch(rect2)
    
    ax.text(0.25, 0.68, title, color='#FFFFFF', fontsize=9, weight='bold', ha='center', va='center', transform=ax.transAxes)
    ax.text(0.25, 0.38, "\n".join(items_left), color='#BFDBFE', fontsize=6.5, ha='center', va='center', transform=ax.transAxes)
    
    ax.text(0.75, 0.68, subtitle, color='#FFFFFF', fontsize=9, weight='bold', ha='center', va='center', transform=ax.transAxes)
    ax.text(0.75, 0.38, "\n".join(items_right), color='#FBCFE8', fontsize=6.5, ha='center', va='center', transform=ax.transAxes)
    
    ax.annotate("", xy=(0.52, 0.5), xytext=(0.48, 0.5), xycoords='axes fraction', arrowprops=dict(arrowstyle="<->", color="#38BDF8", lw=2))
    ax.text(0.5, 0.90, "SINERGIA TÉCNICA INTERDISCIPLINARIA", color='#38BDF8', fontsize=7.5, weight='bold', ha='center', transform=ax.transAxes)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)


def create_bars_figure(filepath, categories, values, title, xlabel, bar_color='#2563EB', xlim=None):
    """Genera un gráfico horizontal de barras con porcentajes."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    y_pos = np.arange(len(categories))
    bars = ax.barh(y_pos, values, color=bar_color, height=0.55, edgecolor='#1E3A8A', lw=0.6)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(categories, fontsize=7)
    ax.invert_yaxis()
    ax.set_xlabel(xlabel, fontsize=7, weight='bold', color='#1E293B')
    ax.set_title(title, fontsize=7.5, weight='bold', color='#1E3A8A', pad=6)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    
    max_val = max(values)
    if xlim:
        ax.set_xlim(0, xlim)
    else:
        ax.set_xlim(0, max_val * 1.25)
        
    for bar in bars:
        w = bar.get_width()
        ax.text(w + (max_val * 0.02), bar.get_y() + bar.get_height()/2, f'{w}%', ha='left', va='center', fontsize=6.8, weight='bold', color='#0F172A')
        
    ax.tick_params(axis='x', labelsize=6.5)
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_pillars_figure(filepath, title, pillars, colors_list):
    """Genera 3 o 4 pilares/cajas conceptuales horizontales."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    n = len(pillars)
    width = 0.90 / n
    gap = 0.02
    
    for i, (p_title, p_desc) in enumerate(pillars):
        x = 0.05 + i * (width + gap)
        bg = colors_list[i % len(colors_list)]
        rect = plt.Rectangle((x, 0.10), width, 0.72, facecolor=bg[0], edgecolor=bg[1], lw=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + width/2, 0.68, p_title, color=bg[2], fontsize=7.2, weight='bold', ha='center', va='center', transform=ax.transAxes)
        ax.text(x + width/2, 0.38, p_desc, color=bg[3], fontsize=5.8, ha='center', va='center', transform=ax.transAxes)
        
    ax.text(0.5, 0.90, title, color='#1E3A8A', fontsize=7.8, weight='bold', ha='center', transform=ax.transAxes)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_flowchart_figure(filepath, steps, title):
    """Genera un diagrama de flujo horizontal con flechas entre etapas."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    n = len(steps)
    box_w = 0.84 / n
    for i, (step_num, step_name, step_detail) in enumerate(steps):
        x = 0.06 + i * (box_w + 0.035)
        rect = plt.Rectangle((x, 0.12), box_w, 0.68, facecolor='#EFF6FF', edgecolor='#2563EB', lw=1.2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + box_w/2, 0.66, f"Fase {step_num}", color='#1E40AF', fontsize=6.8, weight='bold', ha='center', transform=ax.transAxes)
        ax.text(x + box_w/2, 0.48, step_name, color='#0F172A', fontsize=6.2, weight='bold', ha='center', transform=ax.transAxes)
        ax.text(x + box_w/2, 0.28, step_detail, color='#475569', fontsize=5.4, ha='center', transform=ax.transAxes)
        
        if i < n - 1:
            arr_x = x + box_w + 0.005
            ax.annotate("", xy=(arr_x + 0.025, 0.46), xytext=(arr_x, 0.46), xycoords='axes fraction',
                        arrowprops=dict(arrowstyle="->", color="#2563EB", lw=1.8))
            
    ax.text(0.5, 0.90, title, color='#1E3A8A', fontsize=7.8, weight='bold', ha='center', transform=ax.transAxes)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_schematic_unifilar(filepath):
    """Genera diagrama unifilar eléctrico con protecciones y alimentadores."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Barra principal
    ax.plot([0.1, 0.9], [0.55, 0.55], color='#1E3A8A', lw=3)
    ax.text(0.5, 0.62, "Barra Principal BT: 3F + N + PE (220V/127V, 60 Hz)", color='#1E3A8A', fontsize=7.2, weight='bold', ha='center')
    
    # Acometida arriba
    ax.plot([0.25, 0.25], [0.85, 0.55], color='#DC2626', lw=2)
    ax.text(0.25, 0.88, "Acometida Eléctrica\n(Medidor / Red)", color='#DC2626', fontsize=6.5, weight='bold', ha='center')
    ax.plot([0.22, 0.28], [0.72, 0.72], color='#DC2626', lw=2)
    ax.text(0.33, 0.72, "TM 3x100A", color='#DC2626', fontsize=6, weight='bold', va='center')
    
    # Circuitos derivados abajo
    circs = [
        (0.20, "C1: Alumbrado\n1x15A | THHN #14", '#2563EB'),
        (0.40, "C2: Tomas GFCI\n1x20A | THHN #12", '#059669'),
        (0.60, "C3: Climatización\n2x30A | THHN #10", '#D97706'),
        (0.80, "C4: Motores/Fuerza\n3x50A | THHN #8", '#7C3AED')
    ]
    for cx, label, col in circs:
        ax.plot([cx, cx], [0.55, 0.25], color=col, lw=1.8)
        rect = plt.Rectangle((cx - 0.08, 0.12), 0.16, 0.20, facecolor='#FFFFFF', edgecolor=col, lw=1.2)
        ax.add_patch(rect)
        ax.text(cx, 0.22, label, color=col, fontsize=5.8, weight='bold', ha='center', va='center')
        
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_grounding_figure(filepath):
    """Genera esquema de sistema de puesta a tierra (SPT)."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Suelo
    ax.axhspan(0, 0.45, facecolor='#FEF3C7', alpha=0.6)
    ax.plot([0.05, 0.95], [0.45, 0.45], color='#B45309', lw=1.5, linestyle='--')
    ax.text(0.12, 0.48, "Nivel de Terreno Natural", color='#B45309', fontsize=6.2, weight='bold')
    
    # Tablero arriba
    rect_t = plt.Rectangle((0.15, 0.60), 0.28, 0.32, facecolor='#EFF6FF', edgecolor='#1E3A8A', lw=1.5)
    ax.add_patch(rect_t)
    ax.text(0.29, 0.80, "Tablero de Distribución", color='#1E3A8A', fontsize=6.8, weight='bold', ha='center')
    ax.text(0.29, 0.68, "Barra Equipotencial PE\nNeutro Aislado N", color='#475569', fontsize=5.8, ha='center')
    
    # Jabalina Copperweld
    ax.plot([0.29, 0.29], [0.60, 0.08], color='#059669', lw=3)
    ax.plot([0.65, 0.65], [0.45, 0.08], color='#B45309', lw=4)
    ax.plot([0.29, 0.65], [0.40, 0.40], color='#059669', lw=2)
    ax.text(0.47, 0.43, "Conductor de Cobre Desnudo 2 AWG", color='#059669', fontsize=6, weight='bold', ha='center')
    
    ax.text(0.65, 0.24, "Electrodo Copperweld\n5/8\" x 2.4 m\n(Tratamiento Bentonita)", color='#78350F', fontsize=6, weight='bold', ha='center')
    
    # Cuadro Telurómetro
    rect_m = plt.Rectangle((0.75, 0.58), 0.20, 0.34, facecolor='#DCFCE7', edgecolor='#15803D', lw=1.2)
    ax.add_patch(rect_m)
    ax.text(0.85, 0.80, "Telurómetro", color='#15803D', fontsize=6.8, weight='bold', ha='center')
    ax.text(0.85, 0.68, "Resistencia:\nR < 5 Ω (Ind.)\nR < 25 Ω (Res.)", color='#166534', fontsize=5.8, weight='bold', ha='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_motor_curve_figure(filepath):
    """Genera curva de par versus velocidad de motor de inducción."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    n = np.linspace(0, 1800, 300)
    # Curva característica par-velocidad de inducción
    t = 1.8 * (n / 1500) / (1 + (n / 1500)**2) * 160 + 40 * np.exp(-((n-1450)/400)**2)
    
    ax.plot(n, t, color='#2563EB', lw=2, label='Par Motor')
    ax.axhline(60, color='#DC2626', lw=1.2, linestyle='--', label='Par Resistente Carga')
    ax.axvline(1800, color='#64748B', lw=1, linestyle=':', label='Velocidad Síncrona Ns (1800 RPM)')
    
    ax.scatter([0, 1400, 1720], [t[0], max(t), 60], color=['#D97706', '#2563EB', '#059669'], s=25, zorder=5)
    ax.text(60, t[0] + 5, f'Par Arranque\n({t[0]:.0f} Nm)', fontsize=6, weight='bold', color='#D97706')
    ax.text(1400, max(t) + 6, f'Par Máximo Kloss\n({max(t):.0f} Nm)', fontsize=6, weight='bold', color='#2563EB', ha='center')
    ax.text(1720, 75, 'Punto Nominal\n(1720 RPM)', fontsize=6, weight='bold', color='#059669', ha='center')
    
    ax.set_xlabel('Velocidad del Rotor (RPM)', fontsize=7, weight='bold')
    ax.set_ylabel('Par Electromagnético (Nm)', fontsize=7, weight='bold')
    ax.set_title('Curva Característica Par-Velocidad Motor de Inducción Jaula de Ardilla', fontsize=7.5, weight='bold', color='#1E3A8A', pad=5)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(fontsize=5.8, loc='upper left')
    ax.tick_params(labelsize=6.5)
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_transformer_figure(filepath):
    """Genera esquema de banco trifásico Delta-Estrella."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Bloque Primario Delta
    rect_d = plt.Rectangle((0.08, 0.18), 0.36, 0.64, facecolor='#EFF6FF', edgecolor='#2563EB', lw=1.5)
    ax.add_patch(rect_d)
    ax.text(0.26, 0.70, "Primario en Delta (Δ)", color='#1E40AF', fontsize=7.2, weight='bold', ha='center')
    ax.text(0.26, 0.50, "Tensión: 13,800 V (MT)\n3 Hilos de Fase (H1, H2, H3)\nSin Conductor Neutro", color='#1E293B', fontsize=6, ha='center')
    ax.text(0.26, 0.28, "Conexión en Triángulo Cerrado", color='#64748B', fontsize=5.5, ha='center', style='italic')
    
    # Símbolo Acoplamiento
    ax.annotate("", xy=(0.54, 0.50), xytext=(0.46, 0.50), xycoords='axes fraction',
                arrowprops=dict(arrowstyle="<->", color="#DC2626", lw=2))
    ax.text(0.50, 0.65, "Acoplamiento\nMagnético Dy5", color='#DC2626', fontsize=6.2, weight='bold', ha='center')
    
    # Bloque Secundario Estrella
    rect_y = plt.Rectangle((0.56, 0.18), 0.36, 0.64, facecolor='#FEF2F2', edgecolor='#DC2626', lw=1.5)
    ax.add_patch(rect_y)
    ax.text(0.74, 0.70, "Secundario en Estrella (Y)", color='#991B1B', fontsize=7.2, weight='bold', ha='center')
    ax.text(0.74, 0.50, "Tensión: 480V / 277V (BT)\n3 Fases (X1, X2, X3) + Neutro X0\nNeutro Sólidamente Puesto a Tierra", color='#1E293B', fontsize=6, ha='center')
    ax.text(0.74, 0.28, "Tensión Fase-Fase / Fase-Neutro", color='#64748B', fontsize=5.5, ha='center', style='italic')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_plc_ladder_figure(filepath):
    """Genera diagrama de arquitectura PLC y lógica Ladder."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Rieles de Ladder
    ax.plot([0.08, 0.08], [0.15, 0.85], color='#1E3A8A', lw=3)
    ax.plot([0.92, 0.92], [0.15, 0.85], color='#1E3A8A', lw=3)
    ax.text(0.08, 0.90, "+24V DC", color='#1E3A8A', fontsize=6.5, weight='bold', ha='center')
    ax.text(0.92, 0.90, "0V (COM)", color='#1E3A8A', fontsize=6.5, weight='bold', ha='center')
    
    # Rung 1: Arranque y Paro con Memoria
    ax.plot([0.08, 0.22], [0.65, 0.65], color='#2563EB', lw=1.5)
    # Contacto NA Pulsador Marcha
    ax.plot([0.22, 0.24], [0.60, 0.70], color='#2563EB', lw=1.5)
    ax.plot([0.28, 0.30], [0.60, 0.70], color='#2563EB', lw=1.5)
    ax.plot([0.22, 0.30], [0.65, 0.65], color='#2563EB', lw=0.5, linestyle=':')
    ax.text(0.26, 0.74, "I0.0 (Marcha)", color='#1E40AF', fontsize=5.8, weight='bold', ha='center')
    
    ax.plot([0.30, 0.44], [0.65, 0.65], color='#2563EB', lw=1.5)
    # Contacto NC Paro
    ax.plot([0.44, 0.46], [0.60, 0.70], color='#DC2626', lw=1.5)
    ax.plot([0.50, 0.52], [0.60, 0.70], color='#DC2626', lw=1.5)
    ax.plot([0.43, 0.53], [0.60, 0.70], color='#DC2626', lw=1.5)
    ax.text(0.48, 0.74, "I0.1 (Paro NC)", color='#DC2626', fontsize=5.8, weight='bold', ha='center')
    
    ax.plot([0.52, 0.76], [0.65, 0.65], color='#2563EB', lw=1.5)
    # Bobina de Salida Q0.0
    circle = plt.Circle((0.80, 0.65), 0.04, facecolor='#FFFFFF', edgecolor='#059669', lw=1.8)
    ax.add_patch(circle)
    ax.text(0.80, 0.65, "Q0.0", color='#059669', fontsize=5.8, weight='bold', ha='center', va='center')
    ax.text(0.80, 0.74, "KM1 (Motor)", color='#059669', fontsize=5.8, weight='bold', ha='center')
    ax.plot([0.84, 0.92], [0.65, 0.65], color='#2563EB', lw=1.5)
    
    # Enclavamiento Q0.0 en paralelo
    ax.plot([0.16, 0.16], [0.65, 0.35], color='#2563EB', lw=1.5)
    ax.plot([0.16, 0.22], [0.35, 0.35], color='#2563EB', lw=1.5)
    ax.plot([0.22, 0.24], [0.30, 0.40], color='#2563EB', lw=1.5)
    ax.plot([0.28, 0.30], [0.30, 0.40], color='#2563EB', lw=1.5)
    ax.text(0.26, 0.24, "Q0.0 (Enclavamiento)", color='#1E40AF', fontsize=5.8, weight='bold', ha='center')
    ax.plot([0.30, 0.38], [0.35, 0.35], color='#2563EB', lw=1.5)
    ax.plot([0.38, 0.38], [0.35, 0.65], color='#2563EB', lw=1.5)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_solar_pv_figure(filepath):
    """Genera diagrama de topología de sistema solar fotovoltaico."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    stages = [
        (0.08, "Generador Solar\nPaneles Fotovoltaicos\n(Strings DC)", '#D97706', '#FEF3C7'),
        (0.32, "Caja Combinadora\nProtección Fusibles\nDescargadores SPD", '#B45309', '#FFEDD5'),
        (0.56, "Inversor Central\nConversión DC a AC\nSeguimiento MPPT", '#2563EB', '#EFF6FF'),
        (0.80, "Tablero AC & Red\nMedidor Bidireccional\nCargas y Red Eléctrica", '#059669', '#DCFCE7')
    ]
    for x, txt, col_b, col_f in stages:
        rect = plt.Rectangle((x, 0.15), 0.18, 0.66, facecolor=col_f, edgecolor=col_b, lw=1.2)
        ax.add_patch(rect)
        ax.text(x + 0.09, 0.48, txt, color=col_b, fontsize=5.8, weight='bold', ha='center', va='center')
        
    for i in range(3):
        ax.annotate("", xy=(stages[i+1][0] - 0.01, 0.48), xytext=(stages[i][0] + 0.19, 0.48),
                    arrowprops=dict(arrowstyle="->", color="#1E293B", lw=1.5))
        
    ax.text(0.5, 0.90, "Cadena de Conversión y Flujo Energético Fotovoltaico Interconectado", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_arc_flash_figure(filepath):
    """Genera diagrama de fronteras de aproximación y categorías NFPA 70E."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Límites semicirculares concéntricos
    angles = np.linspace(0, np.pi, 200)
    r_flash = 0.90
    r_lim = 0.65
    r_res = 0.40
    
    ax.plot(0.5 + r_flash * 0.45 * np.cos(angles), 0.10 + r_flash * 0.75 * np.sin(angles), color='#DC2626', lw=1.5, linestyle='--')
    ax.plot(0.5 + r_lim * 0.45 * np.cos(angles), 0.10 + r_lim * 0.75 * np.sin(angles), color='#D97706', lw=1.5, linestyle='-.')
    ax.plot(0.5 + r_res * 0.45 * np.cos(angles), 0.10 + r_res * 0.75 * np.sin(angles), color='#7C3AED', lw=1.5, linestyle=':')
    
    ax.scatter([0.5], [0.10], color='#0F172A', s=40, zorder=5)
    ax.text(0.5, 0.02, "Conductor Energizado Expuesto", color='#0F172A', fontsize=6.2, weight='bold', ha='center')
    
    ax.text(0.5, 0.42, "Límite Restringido\n(Solo Personal Calificado con EPP)", color='#7C3AED', fontsize=5.8, weight='bold', ha='center')
    ax.text(0.5, 0.62, "Límite de Aproximación Limitada", color='#D97706', fontsize=5.8, weight='bold', ha='center')
    ax.text(0.5, 0.80, "Frontera de Arco Eléctrico (Arc Flash Boundary: 1.2 cal/cm²)", color='#DC2626', fontsize=6.5, weight='bold', ha='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.95)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_steel_profiles_figure(filepath):
    """Genera perfiles estructurales laminados en caliente."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # 1. Perfil W (Viga ala ancha)
    ax.fill([0.08, 0.22, 0.22, 0.16, 0.16, 0.22, 0.22, 0.08, 0.08, 0.14, 0.14, 0.08],
            [0.78, 0.78, 0.70, 0.70, 0.30, 0.30, 0.22, 0.22, 0.30, 0.30, 0.70, 0.70],
            color='#1E3A8A')
    ax.text(0.15, 0.12, "Perfil W / IPE\n(Flexión y Vigas)", color='#1E3A8A', fontsize=5.8, weight='bold', ha='center')
    
    # 2. Perfil HSS Tubular
    rect_out = plt.Rectangle((0.30, 0.22), 0.14, 0.56, facecolor='#2563EB', edgecolor='#1E3A8A', lw=1)
    rect_in = plt.Rectangle((0.33, 0.32), 0.08, 0.36, facecolor='#F8FAFC', edgecolor='#1E3A8A', lw=1)
    ax.add_patch(rect_out)
    ax.add_patch(rect_in)
    ax.text(0.37, 0.12, "Tubo HSS\n(Compresión / Columnas)", color='#2563EB', fontsize=5.8, weight='bold', ha='center')
    
    # 3. Perfil UPN (Canal)
    ax.fill([0.52, 0.64, 0.64, 0.58, 0.58, 0.64, 0.64, 0.52],
            [0.78, 0.78, 0.70, 0.70, 0.30, 0.30, 0.22, 0.22],
            color='#059669')
    ax.text(0.58, 0.12, "Canal UPN\n(Arriostres y Correas)", color='#059669', fontsize=5.8, weight='bold', ha='center')
    
    # 4. Perfil L (Ángulo)
    ax.fill([0.74, 0.80, 0.80, 0.88, 0.88, 0.74],
            [0.78, 0.78, 0.28, 0.28, 0.22, 0.22],
            color='#D97706')
    ax.text(0.81, 0.12, "Ángulo L\n(Celosías y Tijerales)", color='#D97706', fontsize=5.8, weight='bold', ha='center')
    
    ax.text(0.5, 0.90, "Taxonomía de Perfiles de Acero Estructural según AISC 360 y ASTM A36/A992", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_cutting_comparison_figure(filepath):
    """Genera comparativa técnica entre Oxicorte y Corte por Plasma CNC."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Lado Izquierdo: Oxicorte
    rect1 = plt.Rectangle((0.05, 0.15), 0.42, 0.70, facecolor='#FFFBEB', edgecolor='#D97706', lw=1.2)
    ax.add_patch(rect1)
    ax.text(0.26, 0.72, "Oxicorte Convencional / CNC", color='#B45309', fontsize=7, weight='bold', ha='center')
    ax.text(0.26, 0.44, "• Gas: O2 + Acetileno/Propano\n• Rango: Espesores gruesos (>25 mm)\n• Metal: Exclusivo acero al carbono\n• ZAT: Amplia distorsión térmica", color='#78350F', fontsize=5.8, ha='center')
    
    # Lado Derecho: Plasma
    rect2 = plt.Rectangle((0.53, 0.15), 0.42, 0.70, facecolor='#EFF6FF', edgecolor='#2563EB', lw=1.2)
    ax.add_patch(rect2)
    ax.text(0.74, 0.72, "Corte por Plasma de Alta Definición", color='#1E40AF', fontsize=7, weight='bold', ha='center')
    ax.text(0.74, 0.44, "• Gas: Aire comprimido / Nitrógeno / O2\n• Rango: Espesores delgados y medios (1-35 mm)\n• Metal: Acero al carbono, inoxidable, aluminio\n• Calidad: Bisel casi nulo y mínima ZAT", color='#1E293B', fontsize=5.8, ha='center')
    
    ax.annotate("", xy=(0.52, 0.50), xytext=(0.48, 0.50), xycoords='axes fraction',
                arrowprops=dict(arrowstyle="<->", color="#64748B", lw=1.5))
    ax.text(0.5, 0.90, "Criterios de Selección Tecnológica para Preparación de Juntas y Biseles", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_weld_morphology_figure(filepath):
    """Genera corte transversal de morfología de unión soldada y ZAT."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Placas base
    ax.fill([0.05, 0.42, 0.42, 0.05], [0.30, 0.30, 0.60, 0.60], color='#CBD5E1', edgecolor='#475569', lw=1)
    ax.fill([0.58, 0.95, 0.95, 0.58], [0.30, 0.30, 0.60, 0.60], color='#CBD5E1', edgecolor='#475569', lw=1)
    ax.text(0.20, 0.45, "Metal Base (BM)\nASTM A36", color='#334155', fontsize=6.2, weight='bold', ha='center')
    ax.text(0.80, 0.45, "Metal Base (BM)\nASTM A36", color='#334155', fontsize=6.2, weight='bold', ha='center')
    
    # ZAT (HAZ)
    ax.fill([0.38, 0.44, 0.44, 0.38], [0.25, 0.25, 0.65, 0.65], color='#FCD34D', alpha=0.8)
    ax.fill([0.56, 0.62, 0.62, 0.56], [0.25, 0.25, 0.65, 0.65], color='#FCD34D', alpha=0.8)
    
    # Cordón de Soldadura (WM)
    ax.fill([0.42, 0.58, 0.54, 0.46], [0.60, 0.60, 0.75, 0.75], color='#DC2626')
    ax.fill([0.42, 0.58, 0.55, 0.45], [0.30, 0.30, 0.18, 0.18], color='#DC2626')
    ax.fill([0.42, 0.58, 0.58, 0.42], [0.30, 0.30, 0.60, 0.60], color='#EA580C')
    
    ax.text(0.50, 0.45, "Metal de\nSoldadura\n(WM)", color='#FFFFFF', fontsize=5.8, weight='bold', ha='center')
    ax.text(0.35, 0.78, "Zona Afectada por\nel Calor (ZAT / HAZ)", color='#B45309', fontsize=6, weight='bold', ha='center')
    ax.annotate("", xy=(0.40, 0.62), xytext=(0.36, 0.74), arrowprops=dict(arrowstyle="->", color="#B45309", lw=1))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.90)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_gmaw_gtaw_figure(filepath):
    """Genera esquema comparativo de procesos semiautomático GMAW y manual GTAW."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # GMAW Box
    rect1 = plt.Rectangle((0.06, 0.12), 0.42, 0.72, facecolor='#F0FDF4', edgecolor='#16A34A', lw=1.2)
    ax.add_patch(rect1)
    ax.text(0.27, 0.70, "GMAW (MIG / MAG) — Semiautomático", color='#15803D', fontsize=6.8, weight='bold', ha='center')
    ax.text(0.27, 0.42, "• Electrodo de microalambre continuo en carrete\n• Gas de protección: Argón + CO2 (MAG) o Ar puro (MIG)\n• Alta tasa de deposición y productividad continua\n• Utilizado en estructuras, tolvas y carrocerías", color='#14532D', fontsize=5.6, ha='center')
    
    # GTAW Box
    rect2 = plt.Rectangle((0.52, 0.12), 0.42, 0.72, facecolor='#FEF2F2', edgecolor='#DC2626', lw=1.2)
    ax.add_patch(rect2)
    ax.text(0.73, 0.70, "GTAW (TIG) — Máxima Calidad", color='#B91C1C', fontsize=6.8, weight='bold', ha='center')
    ax.text(0.73, 0.42, "• Electrodo no consumible de tungsteno (EWTh/EWLa)\n• Gas de protección: 100% Argón de alta pureza\n• Aporte manual de varilla: pase de raíz radiográfico\n• Aplicación: Tuberías a presión, acero inoxidable, aluminio", color='#7F1D1D', fontsize=5.6, ha='center')
    
    ax.text(0.5, 0.90, "Comparativa Técnica Operativa: Rendimiento Volumétrico vs Calidad Metalúrgica", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_aws_symbol_figure(filepath):
    """Genera descomposición de simbología normalizada AWS A2.4."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Línea de referencia
    ax.plot([0.25, 0.75], [0.50, 0.50], color='#1E3A8A', lw=2.5)
    # Flecha
    ax.annotate("", xy=(0.88, 0.20), xytext=(0.75, 0.50),
                arrowprops=dict(arrowstyle="->", color="#1E3A8A", lw=2.5))
    ax.text(0.90, 0.16, "Flecha\n(Apunta a la junta)", color='#1E3A8A', fontsize=5.8, weight='bold')
    
    # Cola
    ax.plot([0.25, 0.18], [0.50, 0.60], color='#1E3A8A', lw=2)
    ax.plot([0.25, 0.18], [0.50, 0.40], color='#1E3A8A', lw=2)
    ax.text(0.14, 0.50, "Cola\n(WPS-01)", color='#DC2626', fontsize=6.2, weight='bold', ha='center', va='center')
    
    # Símbolo de filete abajo (Lado de la flecha)
    ax.plot([0.50, 0.56], [0.50, 0.38], color='#059669', lw=2)
    ax.plot([0.56, 0.56], [0.38, 0.50], color='#059669', lw=2)
    ax.text(0.44, 0.42, "Cateto: 6 mm", color='#059669', fontsize=5.8, weight='bold')
    ax.text(0.60, 0.38, "Longitud: 50-100", color='#059669', fontsize=5.8, weight='bold')
    
    # Bandera de campo
    ax.plot([0.75, 0.75], [0.50, 0.72], color='#D97706', lw=1.8)
    ax.fill([0.75, 0.68, 0.75], [0.72, 0.65, 0.58], color='#D97706')
    ax.text(0.72, 0.76, "Soldadura en Terreno (Campo)", color='#D97706', fontsize=5.8, weight='bold', ha='center')
    
    ax.text(0.5, 0.90, "Estructura de Símbolo de Soldadura según AWS A2.4", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_ndt_volumetric_figure(filepath):
    """Genera esquema de ensayos no destructivos volumétricos: UT y RT."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # UT Side
    rect1 = plt.Rectangle((0.05, 0.12), 0.42, 0.72, facecolor='#EFF6FF', edgecolor='#2563EB', lw=1.2)
    ax.add_patch(rect1)
    ax.text(0.26, 0.70, "Ultrasonido Industrial (UT) A-Scan", color='#1E40AF', fontsize=6.8, weight='bold', ha='center')
    ax.text(0.26, 0.42, "• Haz sónico de alta frecuencia (2 - 5 MHz)\n• Transductor angular de 45°, 60° o 70°\n• Detección precisa de discontinuidades internas\n• Sin emisión de radiación ionizante (In situ)", color='#1E293B', fontsize=5.6, ha='center')
    
    # RT Side
    rect2 = plt.Rectangle((0.53, 0.12), 0.42, 0.72, facecolor='#FEF2F2', edgecolor='#DC2626', lw=1.2)
    ax.add_patch(rect2)
    ax.text(0.74, 0.70, "Radiografía Industrial (RT)", color='#B91C1C', fontsize=6.8, weight='bold', ha='center')
    ax.text(0.74, 0.42, "• Fuente gamma (Iridio 192) o tubo de Rayos X\n• Registro permanente en película radiográfica digital\n• Identificación de porosidad, escoria y falta de fusión\n• Exige protocolo estricto de seguridad radiológica", color='#7F1D1D', fontsize=5.6, ha='center')
    
    ax.text(0.5, 0.90, "Ensayos No Destructivos Volumétricos de Integridad según AWS D1.1 / ASME IX", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_connection_figure(filepath):
    """Genera detalle de conexión viga-columna AISC 360."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Columna W14
    ax.fill([0.15, 0.32, 0.32, 0.15], [0.05, 0.05, 0.95, 0.95], color='#CBD5E1', edgecolor='#334155', lw=1.5)
    ax.text(0.235, 0.85, "Columna de Acero\nW14x90 (ASTM A992)", color='#1E293B', fontsize=6, weight='bold', ha='center')
    
    # Viga W18
    ax.fill([0.32, 0.85, 0.85, 0.32], [0.30, 0.30, 0.70, 0.70], color='#94A3B8', edgecolor='#334155', lw=1.5)
    ax.text(0.60, 0.50, "Viga Principal W18x50\n(Conexión a Momento)", color='#0F172A', fontsize=6.2, weight='bold', ha='center')
    
    # Placa y pernos A325
    ax.fill([0.32, 0.36, 0.36, 0.32], [0.25, 0.25, 0.75, 0.75], color='#DC2626')
    ax.scatter([0.34, 0.34, 0.34, 0.34], [0.35, 0.45, 0.55, 0.65], color='#FFFFFF', s=16, edgecolors='#7F1D1D', lw=1, zorder=5)
    ax.text(0.40, 0.78, "Pernos ASTM A325 (3/4\")\nTorque Calibrado", color='#DC2626', fontsize=5.8, weight='bold')
    
    # Soldadura en patines
    ax.plot([0.32, 0.42], [0.70, 0.70], color='#059669', lw=3)
    ax.plot([0.32, 0.42], [0.30, 0.30], color='#059669', lw=3)
    ax.text(0.44, 0.32, "Soldadura Bisel CJP (E7018)", color='#059669', fontsize=5.8, weight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_rigging_figure(filepath):
    """Genera esquema de maniobras de izaje y montaje con grúa."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Gancho de grúa arriba
    ax.plot([0.50, 0.50], [0.95, 0.80], color='#1E293B', lw=3)
    circle = plt.Circle((0.50, 0.76), 0.04, facecolor='#D97706', edgecolor='#78350F', lw=1.5)
    ax.add_patch(circle)
    ax.text(0.50, 0.84, "Gancho de Grúa Calibrado", color='#78350F', fontsize=6, weight='bold', ha='center')
    
    # Eslingas a 60 grados
    ax.plot([0.50, 0.28], [0.74, 0.38], color='#2563EB', lw=2)
    ax.plot([0.50, 0.72], [0.74, 0.38], color='#2563EB', lw=2)
    ax.text(0.50, 0.60, "Ángulo de Eslinga ≥ 60°\n(Carga Balanceada)", color='#1E40AF', fontsize=5.8, weight='bold', ha='center')
    
    # Viga de acero levantada
    ax.fill([0.20, 0.80, 0.80, 0.20], [0.32, 0.32, 0.38, 0.38], color='#94A3B8', edgecolor='#1E293B', lw=1.5)
    ax.text(0.50, 0.34, "Elemento Estructural de Acero en Suspensión", color='#0F172A', fontsize=6, weight='bold', ha='center', va='center')
    
    # Vientos (taglines)
    ax.plot([0.20, 0.08], [0.32, 0.08], color='#059669', lw=1.5, linestyle='--')
    ax.plot([0.80, 0.92], [0.32, 0.08], color='#059669', lw=1.5, linestyle='--')
    ax.text(0.08, 0.04, "Cuerda Guía (Tagline)", color='#059669', fontsize=5.8, weight='bold', ha='center')
    ax.text(0.92, 0.04, "Control Antigiro", color='#059669', fontsize=5.8, weight='bold', ha='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_substation_modular_figure(filepath):
    """Genera corte esquemático de sala eléctrica modular industrial."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    # Contenedor modular
    rect = plt.Rectangle((0.08, 0.15), 0.84, 0.68, facecolor='#F1F5F9', edgecolor='#1E3A8A', lw=1.8)
    ax.add_patch(rect)
    ax.text(0.50, 0.76, "Sala Eléctrica Modular Prefabricada (E-House / NEMA 4X)", color='#1E3A8A', fontsize=7.2, weight='bold', ha='center')
    
    # Equipos adentro
    eqs = [
        (0.14, "Celda MT\n13.8 kV", '#DC2626'),
        (0.32, "Trafo Seco\n13.8k/480V", '#D97706'),
        (0.50, "Tablero BT\n480/277V", '#2563EB'),
        (0.68, "Bancos CCM\n& Variadores", '#059669'),
        (0.82, "Control PLC\n& SCADA", '#7C3AED')
    ]
    for x, label, col in eqs:
        r = plt.Rectangle((x, 0.22), 0.12, 0.42, facecolor='#FFFFFF', edgecolor=col, lw=1.2)
        ax.add_patch(r)
        ax.text(x + 0.06, 0.42, label, color=col, fontsize=5.5, weight='bold', ha='center', va='center')
        
    ax.plot([0.08, 0.92], [0.18, 0.18], color='#B45309', lw=2)
    ax.text(0.50, 0.11, "Malla de Tierra Equipotencial Subterránea", color='#B45309', fontsize=5.8, weight='bold', ha='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 0.90)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def create_project_lifecycle_figure(filepath):
    """Genera ciclo de vida de proyectos técnicos y costeo."""
    steps = [
        ("1", "Cómputos y Cubicaciones", "Despiece de acero, cables y bandejas"),
        ("2", "Presupuesto y Adquisición", "Análisis de precios unitarios (APU)"),
        ("3", "Fabricación y QA/QC", "Inspección en taller y pruebas en vacío"),
        ("4", "Montaje y Comisionado", "Protocolos de prueba y dossier final")
    ]
    create_flowchart_figure(filepath, steps, "Ciclo Integral de Gestión Técnica de Proyectos Electromecánicos")


def create_certifications_path_figure(filepath):
    """Genera la ruta de certificaciones profesionales."""
    steps = [
        ("1", "Egresado BTP", "Título de Educación Media Técnica"),
        ("2", "Homologación 3G/4G", "Calificación Soldador AWS D1.1 / Carné BT"),
        ("3", "Supervisor Técnico", "Certificación CWI / Técnico de Mantenimiento"),
        ("4", "Ingeniería Superior", "Continuidad Universitaria (Eléctrica / Mecánica)")
    ]
    create_flowchart_figure(filepath, steps, "Ruta de Crecimiento Técnico, Homologaciones y Continuidad Universitaria")


def create_standards_pyramid_figure(filepath):
    """Genera árbol / pirámide de normas rectoras internacionales."""
    fig, ax = plt.subplots(figsize=(6.4, 1.30), dpi=300)
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#F8FAFC')
    
    levels = [
        (0.72, 0.36, "Normas de Seguridad y Vida: NFPA 70E / OSHA 1910", '#DC2626', '#FEF2F2'),
        (0.44, 0.60, "Códigos de Instalación: NFPA 70 (NEC) • AWS D1.1 • AISC 360", '#2563EB', '#EFF6FF'),
        (0.16, 0.84, "Estándares de Fabricación y Componentes: IEEE • IEC • ASME IX • ASTM", '#059669', '#F0FDF4')
    ]
    for y, w, txt, col, bg in levels:
        x = (1.0 - w) / 2
        r = plt.Rectangle((x, y), w, 0.22, facecolor=bg, edgecolor=col, lw=1.2)
        ax.add_patch(r)
        ax.text(0.50, y + 0.11, txt, color=col, fontsize=6.2, weight='bold', ha='center', va='center')
        
    ax.text(0.5, 0.96, "Estructura Jerárquica del Marco Normativo Internacional Obligatorio", color='#1E3A8A', fontsize=7.5, weight='bold', ha='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(filepath, dpi=300, bbox_inches='tight')
    plt.close(fig)


def generate_all_31_figures():
    """Genera el catálogo completo de 31 figuras técnicas en alta definición."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    setup_matplotlib()
    
    # 1. Portada (Banner general)
    create_banner_figure(
        FIGURES_DIR / "fig_01_portada.png",
        "BTP ELECTRICIDAD", "BTP CONST. METÁLICAS",
        ["• Redes de Distribución MT/BT", "• Automatización y PLC", "• Subestaciones y Motores"],
        ["• Soldadura SMAW/GMAW/GTAW", "• Cálculo Estructural AISC", "• Ensayos No Destructivos NDT"]
    )
    
    # Capítulo 1 (Página 2)
    create_bars_figure(
        FIGURES_DIR / "fig_01_1_demanda.png",
        ['Manufactura', 'Construcción Civil', 'Generación Eléctrica', 'Minería / Petróleo', 'Telecomunicaciones', 'Metalmecánica'],
        [32, 26, 18, 12, 8, 4],
        "Demanda Laboral por Subsector Industrial", "Porcentaje de Absorción (%)", bar_color='#2563EB', xlim=38
    )
    create_pillars_figure(
        FIGURES_DIR / "fig_01_2_competencias.png",
        "Tríada Metodológica del Modelo por Competencias Laborales (CBT)",
        [
            ("SABER CONOCER", "• Teoría electromagnética\n• Metalurgia y resistencia\n• Códigos NEC, AWS, AISC"),
            ("SABER HACER", "• Montaje de tableros BT\n• Soldeo calificado 3G/4G\n• Programación PLC y NDT"),
            ("SABER SER", "• Disciplina LOTO y vida\n• Integridad en inspección\n• Trabajo colaborativo")
        ],
        [
            ('#EFF6FF', '#2563EB', '#1E40AF', '#1E293B'),
            ('#F0FDF4', '#16A34A', '#15803D', '#14532D'),
            ('#FEF2F2', '#DC2626', '#B91C1C', '#7F1D1D')
        ]
    )
    
    # Capítulo 2 (Página 3)
    create_flowchart_figure(
        FIGURES_DIR / "fig_02_1_flujograma_electrico.png",
        [
            ("1", "Diagnóstico", "Inspección visual y análisis térmico"),
            ("2", "Aislamiento", "Corte visible y candadeo LOTO"),
            ("3", "Medición", "Megóhmetro, multímetro y pinza"),
            ("4", "Certificación", "Protocolo de prueba y entrega")
        ],
        "Metodología Operativa del Diagnóstico Eléctrico Industrial"
    )
    create_bars_figure(
        FIGURES_DIR / "fig_02_2_ejes_curriculares.png",
        ['Instalaciones BT/MT', 'Máquinas y Motores', 'Automatización PLC', 'Energías Renovables', 'Seguridad y Códigos'],
        [28, 24, 22, 14, 12],
        "Distribución Curricular del Eje Eléctrico por Horas Formativas", "Porcentaje de Carga Horaria (%)", bar_color='#1E40AF', xlim=35
    )
    
    # Capítulo 3 (Página 4)
    create_schematic_unifilar(FIGURES_DIR / "fig_03_1_unifilar.png")
    create_grounding_figure(FIGURES_DIR / "fig_03_2_puesta_a_tierra.png")
    
    # Capítulo 4 (Página 5)
    create_motor_curve_figure(FIGURES_DIR / "fig_04_1_curva_motor.png")
    create_transformer_figure(FIGURES_DIR / "fig_04_2_transformadores.png")
    
    # Capítulo 5 (Página 6)
    create_plc_ladder_figure(FIGURES_DIR / "fig_05_1_plc_control.png")
    create_solar_pv_figure(FIGURES_DIR / "fig_05_2_solar_fv.png")
    
    # Capítulo 6 (Página 7)
    create_flowchart_figure(
        FIGURES_DIR / "fig_06_1_seguridad_loto.png",
        [
            ("1", "Corte Visible", "Apertura de interruptor"),
            ("2", "Enclavamiento", "Candado y tarjeta LOTO"),
            ("3", "Verificación", "Ausencia de tensión (Voltímetro)"),
            ("4", "Puesta a Tierra", "Cortocircuito preventivo")
        ],
        "Las Reglas de Oro de Seguridad y Bloqueo Operativo (LOTO)"
    )
    create_arc_flash_figure(FIGURES_DIR / "fig_06_2_arc_flash.png")
    
    # Capítulo 7 (Página 8)
    create_steel_profiles_figure(FIGURES_DIR / "fig_07_1_taxonomia_metalica.png")
    create_cutting_comparison_figure(FIGURES_DIR / "fig_07_2_corte_termico.png")
    
    # Capítulo 8 (Página 9)
    create_weld_morphology_figure(FIGURES_DIR / "fig_08_1_morfologia_soldadura.png")
    create_gmaw_gtaw_figure(FIGURES_DIR / "fig_08_2_gmaw_gtaw.png")
    
    # Capítulo 9 (Página 10)
    create_bars_figure(
        FIGURES_DIR / "fig_09_1_fcaw_saw.png",
        ['SMAW (Electrodo)', 'GTAW (TIG)', 'GMAW (MIG/MAG)', 'FCAW (Tubular)', 'SAW (Sumergido)'],
        [2.2, 1.2, 4.8, 6.5, 14.0],
        "Tasa de Deposición de Metal por Proceso de Soldeo (kg/h)", "Tasa de Deposición (kg/hora)", bar_color='#EA580C', xlim=16
    )
    create_aws_symbol_figure(FIGURES_DIR / "fig_09_2_simbologia_aws.png")
    
    # Capítulo 10 (Página 11)
    create_pillars_figure(
        FIGURES_DIR / "fig_10_1_ensayos_superficiales.png",
        "Métodos de Inspección Superficial No Destructiva (END)",
        [
            ("INSPECCIÓN VISUAL (VT)", "• Lupa, galgas de filete\n• Detección de socavación\n• Criterio AWS D1.1 Tabla 6.1"),
            ("LÍQUIDOS PENETRANTES (PT)", "• Tinta roja + Revelador\n• Grietas abiertas en superficie\n• Apto para metales no ferrosos"),
            ("PARTÍCULAS MAGNÉTICAS (MT)", "• Yugo electromagnético\n• Campo longitudinal/circular\n• Defectos sub-superficiales")
        ],
        [
            ('#EFF6FF', '#2563EB', '#1E40AF', '#1E293B'),
            ('#FEF2F2', '#DC2626', '#B91C1C', '#7F1D1D'),
            ('#FEF3C7', '#D97706', '#B45309', '#78350F')
        ]
    )
    create_ndt_volumetric_figure(FIGURES_DIR / "fig_10_2_ensayos_volumetricos.png")
    
    # Capítulo 11 (Página 12)
    create_connection_figure(FIGURES_DIR / "fig_11_1_conexion_viga_columna.png")
    create_rigging_figure(FIGURES_DIR / "fig_11_2_montaje_izaje.png")
    
    # Capítulo 12 (Página 13)
    create_bars_figure(
        FIGURES_DIR / "fig_12_1_nave_industrial.png",
        ['Estructura Metálica', 'Canalizaciones Eléctricas', 'Iluminación y Fuerza', 'Control y Climatización', 'Puesta a Tierra Integral'],
        [35, 22, 18, 15, 10],
        "Distribución Presupuestaria de Naves Industriales Modernas", "Participación en Costo Directo (%)", bar_color='#0284C7', xlim=40
    )
    create_substation_modular_figure(FIGURES_DIR / "fig_12_2_subestacion_modular.png")
    
    # Capítulo 13 (Página 14)
    # Radar plot competencias
    fig, ax = plt.subplots(figsize=(6.4, 1.30), subplot_kw=dict(polar=True), dpi=300)
    cats = ['Liderazgo', 'Seguridad LOTO', 'Comunicación', 'Trabajo Equipo', 'Rigor Técnico', 'Resolución']
    vals = [90, 98, 88, 92, 95, 90]
    vals += vals[:1]
    angles = np.linspace(0, 2*np.pi, len(cats)+1)
    ax.plot(angles, vals, color='#2563EB', lw=1.5)
    ax.fill(angles, vals, color='#3B82F6', alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cats, fontsize=6, weight='bold', color='#1E293B')
    ax.set_ylim(0, 100)
    ax.set_yticklabels([])
    ax.set_title("Madurez de Competencias Socio-Conductuales del Graduado", fontsize=7.5, weight='bold', color='#1E3A8A', pad=8)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_13_1_competencias_radar.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    create_project_lifecycle_figure(FIGURES_DIR / "fig_13_2_gestion_proyectos.png")
    
    # Capítulo 14 (Página 15)
    create_bars_figure(
        FIGURES_DIR / "fig_14_1_trayectoria_laboral.png",
        ['Mantenimiento Industrial', 'Montaje Electromecánico', 'Talleres Metalúrgicos', 'Supervisor de Campo', 'Emprendimiento Propio'],
        [34, 28, 18, 12, 8],
        "Sectores de Absorción Laboral para Graduados BTP", "Porcentaje de Egresados (%)", bar_color='#10B981', xlim=40
    )
    create_certifications_path_figure(FIGURES_DIR / "fig_14_2_ruta_certificaciones.png")
    
    # Capítulo 15 (Página 16)
    create_pillars_figure(
        FIGURES_DIR / "fig_15_1_matriz_perfil.png",
        "Matriz Integradora del Perfil de Egreso BTP",
        [
            ("ENERGÍA Y POTENCIA", "• Redes de distribución\n• Motores y transformadores\n• Calidad de energía y SPT"),
            ("ESTRUCTURAS Y METAL", "• Procesos SMAW, GMAW, FCAW\n• Conexiones sismorresistentes\n• Ensayos NDT superficiales"),
            ("AUTOMATIZACIÓN", "• Lógica de control en PLC\n• Instrumentación 4-20 mA\n• Energías renovables solares")
        ],
        [
            ('#EFF6FF', '#2563EB', '#1E40AF', '#1E293B'),
            ('#FFF7ED', '#EA580C', '#C2410C', '#7C2D12'),
            ('#F0FDF4', '#16A34A', '#15803D', '#14532D')
        ]
    )
    create_standards_pyramid_figure(FIGURES_DIR / "fig_15_2_catalogo_normas.png")
    print("[OK] Generadas exitosamente las 31 figuras tecnicas en 'export/pdf_figures'.")


def build_pdf():
    """Compila el documento PDF formal de 16 páginas con exactamente dos figuras por capítulo."""
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Estilos tipográficos calibrados
    title_cover_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor('#0F172A'),
        alignment=1,
        spaceAfter=6
    )

    subtitle_cover_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=10
    )

    page_h1_style = ParagraphStyle(
        'PageH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=2,
        keepWithNext=True
    )

    page_h2_style = ParagraphStyle(
        'PageH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.2,
        leading=10,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=3,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'PageBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.8,
        textColor=colors.HexColor('#1E293B'),
        alignment=4,  # Justificado
        spaceAfter=4
    )

    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=6.5,
        leading=8,
        textColor=colors.HexColor('#475569'),
        alignment=1,  # Centrado
        spaceAfter=4
    )

    story = []

    # =========================================================================
    # PÁGINA 1: Portada Institucional y Ficha Curricular
    # =========================================================================
    story.append(Spacer(1, 10))
    story.append(Paragraph("SECRETARÍA DE EDUCACIÓN TÉCNICA Y VOCACIONAL", ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=9.5, leading=11, alignment=1, textColor=colors.HexColor('#64748B'))))
    story.append(Paragraph("DIRECCIÓN GENERAL DE EDUCACIÓN MEDIA TÉCNICA", ParagraphStyle('InstSub', fontName='Helvetica', fontSize=8, leading=10, alignment=1, textColor=colors.HexColor('#94A3B8'))))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("EL PERFIL DEL EGRESADO DEL BACHILLERATO TÉCNICO PROFESIONAL EN ELECTRICIDAD Y CONSTRUCCIONES METÁLICAS", title_cover_style))
    story.append(HRFlowable(width="60%", thickness=1.5, color=colors.HexColor('#2563EB'), spaceAfter=8, spaceBefore=2))
    story.append(Paragraph("Manual de Competencias Profesionales, Perfiles Ocupacionales, Fundamentación Tecnológica y Sinergia Productiva", subtitle_cover_style))
    
    # Banner de portada
    story.append(Image(str(FIGURES_DIR / "fig_01_portada.png"), width=480, height=100))
    story.append(Paragraph("Figura 1.0: Ecosistema sinérgico e interdisciplinario entre las especialidades de Electricidad y Construcciones Metálicas.", caption_style))
    story.append(Spacer(1, 6))
    
    # Tabla de Ficha Técnica
    ficha_data = [
        [Paragraph("<b>Título Otorgado:</b>", body_style), Paragraph("Bachiller Técnico Profesional en Electricidad y Construcciones Metálicas", body_style)],
        [Paragraph("<b>Nivel Educativo:</b>", body_style), Paragraph("Educación Media Técnico Profesional (Nivel 4 Marco Nacional de Cualificaciones)", body_style)],
        [Paragraph("<b>Duración Curricular:</b>", body_style), Paragraph("3 Años de Formación Especializada (3,600 Horas: 70% Práctica de Taller / 30% Aula)", body_style)],
        [Paragraph("<b>Normas Rectoras:</b>", body_style), Paragraph("NFPA 70 (NEC), NFPA 70E, IEEE 142, AWS D1.1, AISC 360, ASME IX, ISO 9606-1", body_style)],
        [Paragraph("<b>Ámbitos de Salida:</b>", body_style), Paragraph("Redes BT/MT, Centros de Control de Motores (CCM), Estructuras de Acero y Montaje Industrial", body_style)]
    ]
    ficha_table = Table(ficha_data, colWidths=[120, 360])
    ficha_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(ficha_table)
    story.append(Spacer(1, 8))
    
    p1_text = (
        "El presente documento técnico establece con rigurosidad académica el perfil de egreso correspondiente a los programas del Bachillerato Técnico Profesional (BTP). "
        "La formación contemporánea exige un modelo sustentado en competencias demostrables, articuladas directamente con los requerimientos de la industria manufacturera, "
        "minera, energética y constructiva. El graduado domina la sinergia electromecánica que define a las naves industriales y subestaciones eléctricas, uniendo destrezas de "
        "alta precisión en soldadura y estructuras de acero con el montaje, automatización y mantenimiento de sistemas eléctricos seguros bajo normativa internacional."
    )
    story.append(Paragraph(p1_text, body_style))
    story.append(PageBreak())

    # =========================================================================
    # Capítulos 1 al 15 (Páginas 2 a 16)
    # =========================================================================
    chapters = [
        # Cap 1 (Página 2)
        {
            "num": 1,
            "title": "1. CONTEXTO SOCIO-PRODUCTIVO Y JUSTIFICACIÓN DEL BTP",
            "sub1": "1.1. La Demanda de Técnicos Medios en la Matriz Productiva",
            "text1": "El desarrollo económico y la modernización de los sectores secundario y terciario demandan capital humano técnico con capacidad inmediata de resolución en campo. Las estadísticas ocupacionales evidencian que más del 58% de las posiciones técnicas requeridas por la manufactura y la construcción civil corresponden a profesionales con educación técnica de nivel medio superior. La aceleración de proyectos de energía renovable y naves logísticas exige profesionales versátiles con competencias certificadas.",
            "fig1": "fig_01_1_demanda.png",
            "cap1": "Figura 1.1: Distribución porcentual de inserción laboral para egresados técnicos por subsector productivo.",
            "sub2": "1.2. El Modelo Formativo Basado en Competencias Laborales (CBT)",
            "text2": "El currículo del BTP se sustenta en tres dimensiones indisociables: el Saber Conocer (teoría electromagnética, ciencia de materiales y normativas técnicas), el Saber Hacer (destrezas psicomotrices en banco de taller, soldeo homologado y manejo de instrumentación digital) y el Saber Ser (conciencia de seguridad, disciplina LOTO, ética laboral y reporte transparente en inspecciones técnicas).",
            "fig2": "fig_01_2_competencias.png",
            "cap2": "Figura 1.2: Tríada formativa del modelo por competencias laborales aplicadas al sector electromecánico."
        },
        # Cap 2 (Página 3)
        {
            "num": 2,
            "title": "2. BTP ELECTRICIDAD: EJES FORMATIVOS Y COMPETENCIAS GENERALES",
            "sub2_title": "2.1. Definición del Perfil Ocupacional del Técnico Electricista",
            "text1": "El egresado del BTP en Electricidad está facultado para dimensionar, presupuestar, ejecutar, inspeccionar y mantener redes de energía en baja y media tensión residenciales e industriales. Domina la teoría de circuitos en corriente continua y alterna, análisis fasorial, balanceo de potencia activa y reactiva, así como el protocolo de verificación de aislamiento en motores y transformadores de distribución.",
            "fig1": "fig_02_1_flujograma_electrico.png",
            "cap1": "Figura 2.1: Flujograma metodológico de diagnóstico, aislamiento LOTO y certificación de circuitos.",
            "sub2": "2.2. Ejes Curriculares y Módulos de Especialidad",
            "text2": "El plan de estudios articula cuatro módulos técnicos estructurados: Circuitos Eléctricos y Mediciones, Instalaciones Residenciales y Comerciales bajo NEC, Máquinas Eléctricas Rotativas/Estáticas y Automatización Industrial con Controladores Lógicos Programables (PLC). Esta formación equilibra un 70% de talleres vivenciales con un 30% de fundamentación analítica.",
            "fig2": "fig_02_2_ejes_curriculares.png",
            "cap2": "Figura 2.2: Distribución porcentual de carga horaria formativa por eje temático de la especialidad."
        },
        # Cap 3 (Página 4)
        {
            "num": 3,
            "title": "3. INSTALACIONES ELÉCTRICAS RESIDENCIALES Y COMERCIALES",
            "sub1": "3.1. Acometidas, Canalizaciones y Protecciones en Baja Tensión",
            "text1": "El técnico ejecuta acometidas monofásicas y trifásicas respetando las normativas de servicio eléctrico. Selecciona el calibre de conductores de cobre según ampacidad corregida por temperatura y agrupamiento en canalizaciones conduit (EMT, IMC, PVC). Diseña ramales con protección termomagnética y diferencial contra falla a tierra (GFCI) en recintos húmedos, controlando que la caída de tensión no exceda el 3% en alimentadores.",
            "fig1": "fig_03_1_unifilar.png",
            "cap1": "Figura 3.1: Diagrama unifilar de acometida, barraje de distribución y circuitos derivados protegidos.",
            "sub2": "3.2. Cuadros de Cargas y Sistemas de Puesta a Tierra (SPT)",
            "text2": "Elabora cuadros de balanceo entre fases para minimizar la corriente de neutro. Instala electrodos de puesta a tierra (Copperweld de 5/8 pulg x 2.4 m) y mallas con tratamiento mejorador para lograr resistencias menores a 25 ohmios en viviendas y menores a 5 ohmios en subestaciones, asegurando la inmediata apertura de protecciones ante fallas de aislamiento.",
            "fig2": "fig_03_2_puesta_a_tierra.png",
            "cap2": "Figura 3.2: Esquema técnico del sistema de puesta a tierra (SPT), barra equipotencial y verificación con telurómetro."
        },
        # Cap 4 (Página 5)
        {
            "num": 4,
            "title": "4. MÁQUINAS ELÉCTRICAS ROTATIVAS Y ESTÁTICAS",
            "sub1": "4.1. Motores de Inducción Trifásicos y Monofásicos",
            "text1": "El egresado comprende a fondo el motor asíncrono jaula de ardilla: velocidad síncrona, deslizamiento, factor de servicio y clase térmica de aislamiento. Diseña e implementa esquemas electromagnéticos de control: arranque directo, inversión de giro con enclavamiento mutuo, arranque estrella-triángulo para limitar picos de corriente, y control electrónico mediante arrancadores suaves y variadores de frecuencia.",
            "fig1": "fig_04_1_curva_motor.png",
            "cap1": "Figura 4.1: Curva par-velocidad de motor de inducción con par de arranque, par máximo y punto nominal.",
            "sub2": "4.2. Bancos de Transformadores y Relés de Protección",
            "text2": "Realiza la interconexión de transformadores monofásicos para configurar bancos trifásicos en Delta-Estrella (Dy5) y Delta abierta. Calcula y parametriza relés térmicos bimetálicos, guardamotores magnéticos y disyuntores de caja moldeada (MCCB) para blindar los devanados frente a sobrecargas y desequilibrios de fase prolongados.",
            "fig2": "fig_04_2_transformadores.png",
            "cap2": "Figura 4.2: Topología de conexión de transformador trifásico Delta-Estrella y coordinación de protecciones."
        },
        # Cap 5 (Página 6)
        {
            "num": 5,
            "title": "5. AUTOMATIZACIÓN INDUSTRIAL, PLC Y ENERGÍAS RENOVABLES",
            "sub1": "5.1. Controladores Lógicos Programables (PLC) e Instrumentación",
            "text1": "El técnico programa autómatas industriales bajo estándar IEC 61131-3, prioritariamente en lenguaje de contactos (Ladder) y diagramas de bloques funcionales (FBD). Conecta entradas digitales (sensores inductivos, fotoeléctricos) y analógicas (termocuplas, transmisores de presión 4-20 mA), coordinando lazos cerrados con variadores de frecuencia para el mando de bombas y transportadores.",
            "fig1": "fig_05_1_plc_control.png",
            "cap1": "Figura 5.1: Diagrama de contactos (Ladder) para control secuencial y mando de contactores industriales.",
            "sub2": "5.2. Generación Solar Fotovoltaica y Eficiencia Energética",
            "text2": "Posee competencias en transición energética: cálculo de radiación solar, dimensionamiento de generadores fotovoltaicos interconectados a red (Grid-Tie) y autónomos con baterías. Conecta cajas de combinación con protección contra sobretensiones (SPD) e inversores con seguimiento del punto de máxima potencia (MPPT).",
            "fig2": "fig_05_2_solar_fv.png",
            "cap2": "Figura 5.2: Cadena tecnológica de conversión de energía en sistemas solares fotovoltaicos interconectados."
        },
        # Cap 6 (Página 7)
        {
            "num": 6,
            "title": "6. SEGURIDAD ELÉCTRICA Y NORMATIVA NFPA 70E / OSHA",
            "sub1": "6.1. Procedimientos de Bloqueo y Etiquetado (LOTO)",
            "text1": "La seguridad de la vida humana es prioritaria. El graduado aplica rigurosamente las Cinco Reglas de Oro de la electricidad: corte visible de fuentes, enclavamiento mediante candado personal y tarjeta LOTO intransferible, comprobación de ausencia de tensión con detector bipolar probado, puesta a tierra y cortocircuito, y delimitación física del área de trabajo con cinta de advertencia.",
            "fig1": "fig_06_1_seguridad_loto.png",
            "cap1": "Figura 6.1: Secuencia de aplicación de las Cinco Reglas de Oro y candadeo físico bajo estándar OSHA/LOTO.",
            "sub2": "6.2. Riesgo de Relámpago de Arco (Arc Flash) y EPP Específico",
            "text2": "Comprende la física destructiva del relámpago de arco eléctrico (temperaturas superiores a 19,000 °C y onda de presión expansiva). Identifica las fronteras de aproximación limitada y restringida según NFPA 70E, seleccionando ropa ignífuga con clasificación cal/cm2 (Categorías 1 a 4), caretas con protección UV/IR y guantes dieléctricos con protectores de cuero.",
            "fig2": "fig_06_2_arc_flash.png",
            "cap2": "Figura 6.2: Límites de aproximación segura y frontera de energía incidente contra arco eléctrico NFPA 70E."
        },
        # Cap 7 (Página 8)
        {
            "num": 7,
            "title": "7. BTP CONSTRUCCIONES METÁLICAS: EJES Y COMPETENCIAS",
            "sub1": "7.1. Metalurgia de Aceros Estructurales y Clasificación AISC",
            "text1": "El egresado de Construcciones Metálicas domina la ciencia de los materiales ferrosos. Conoce la influencia del carbono, manganeso y silicio en la soldabilidad, así como el carbono equivalente (CE) para prevenir el agrietamiento en frío. Maneja con solvencia perfiles laminados W, IPE, HEB, canales UPN y perfiles tubulares estructurales HSS bajo especificaciones ASTM A36 y ASTM A992.",
            "fig1": "fig_07_1_taxonomia_metalica.png",
            "cap1": "Figura 7.1: Geometría transversal de perfiles estructurales normalizados según el manual de acero AISC.",
            "sub2": "7.2. Operaciones de Taller: Trazado, Corte Térmico y Biselado",
            "text2": "Domina el trazado geométrico en chapa metálica, punzonado y cizallado. Opera equipos de oxicorte manual y pantógrafos CNC para planchas pesadas, así como sistemas de corte por plasma de alta definición para aceros al carbono e inoxidables, preparando biseles en V, X y U según el plano de taller de la unión soldada.",
            "fig2": "fig_07_2_corte_termico.png",
            "cap2": "Figura 7.2: Comparativa operativa entre corte térmico por oxicorte y plasma de alta definición CNC."
        },
        # Cap 8 (Página 9)
        {
            "num": 8,
            "title": "8. METALURGIA Y PROCESOS DE SOLDADURA: SMAW, GMAW Y GTAW",
            "sub1": "8.1. Soldadura por Arco con Electrodo Revestido (SMAW)",
            "text1": "El proceso SMAW es fundamental en montaje en obra por su versatilidad. El egresado selecciona y manipula electrodos celulósicos (AWS E6010) para penetración profunda en pases de raíz, y electrodos de bajo hidrógeno (AWS E7018) almacenados en hornos térmicos para soldaduras estructurales de alta resistencia y tenacidad al impacto, dominando posiciones 1G a 4G.",
            "fig1": "fig_08_1_morfologia_soldadura.png",
            "cap1": "Figura 8.1: Zonificación metalúrgica de la soldadura: Zona fundida (WM), línea de fusión y ZAT (HAZ).",
            "sub2": "8.2. Soldadura Semiautomática GMAW (MIG/MAG) y Proceso GTAW (TIG)",
            "text2": "Opera equipos semiautomáticos GMAW con alambre sólido ER70S-6 y mezclas de gas Argón/CO2 en modo cortocircuito y spray. En proyectos de alta exigencia utiliza GTAW (TIG) con electrodos de tungsteno no consumibles y Argón puro para realizar pases de raíz de calidad radiográfica en recipientes y tuberías de proceso sin dejar escoria.",
            "fig2": "fig_08_2_gmaw_gtaw.png",
            "cap2": "Figura 8.2: Esquema diferencial entre proceso semiautomático GMAW continuo y proceso de precisión GTAW."
        },
        # Cap 9 (Página 10)
        {
            "num": 9,
            "title": "9. PROCESOS DE ALTA PRODUCTIVIDAD: FCAW Y SAW",
            "sub1": "9.1. Soldadura por Arco con Núcleo de Fundente (FCAW) y SAW",
            "text1": "En industrias de fabricación en serie se emplean procesos de alta tasa de deposición. El técnico califica en FCAW con alambre tubular autoprotegido o protegido por gas (E71T-1), alcanzando más de 5 kg/hora. En vigas armadas de gran peralte opera equipos de Arco Sumergido (SAW), donde el arco arde oculto bajo una manta de fundente granular continuo.",
            "fig1": "fig_09_1_fcaw_saw.png",
            "cap1": "Figura 9.1: Tasas de deposición volumétrica comparativas entre los cinco procesos principales de soldeo.",
            "sub2": "9.2. Simbología de Soldadura AWS A2.4 y Calificación WPS/PQR",
            "text2": "Interpreta y dibuja símbolos de soldadura complejos en planos de ingeniería: línea de referencia, flecha, tamaño del cateto, garganta efectiva y soldadura de campo. Conoce la estructura de una Especificación de Procedimiento de Soldadura (WPS) y su respaldo en el Registro de Calificación de Procedimiento (PQR).",
            "fig2": "fig_09_2_simbologia_aws.png",
            "cap2": "Figura 9.2: Desglose analítico de los componentes de un símbolo de soldadura normalizado bajo norma AWS A2.4."
        },
        # Cap 10 (Página 11)
        {
            "num": 10,
            "title": "10. CONTROL DE CALIDAD Y ENSAYOS NO DESTRUCTIVOS (END / NDT)",
            "sub1": "10.1. Inspección Visual (VT), Líquidos Penetrantes (PT) y Partículas (MT)",
            "text1": "El control de calidad previene fallas catastróficas. El técnico aplica Inspección Visual (VT) con galgas de soldadura para medir catetos, convexidad y socavaciones según AWS D1.1 Tabla 6.1. Ejecuta Líquidos Penetrantes (PT) para detectar discontinuidades abiertas a la superficie y Partículas Magnéticas (MT) con yugo electromagnético en materiales ferromagnéticos.",
            "fig1": "fig_10_1_ensayos_superficiales.png",
            "cap1": "Figura 10.1: Métodos superficiales de ensayos no destructivos: Inspección visual, líquidos penetrantes y yugo magnético.",
            "sub2": "10.2. Ensayos Volumétricos: Ultrasonido Industrial (UT) y Radiografía (RT)",
            "text2": "Comprende los principios físicos de los ensayos volumétricos. Interpreta reportes de Ultrasonido Industrial (UT) con barrido angular para evaluar discontinuidades internas en pases de soldadura gruesos, y conoce los criterios de radiografía industrial (RT) para verificar ausencia de porosidades agrupadas y grietas internas.",
            "fig2": "fig_10_2_ensayos_volumetricos.png",
            "cap2": "Figura 10.2: Ensayos volumétricos de inspección interna: Ultrasonido A-Scan y Radiografía industrial."
        },
        # Cap 11 (Página 12)
        {
            "num": 11,
            "title": "11. FABRICACIÓN Y MONTAJE DE ESTRUCTURAS DE ACERO",
            "sub1": "11.1. Planos de Montaje y Conexiones Sismorresistentes",
            "text1": "El egresado interpreta planos de taller y montaje estructural elaborados en software BIM/CAD. Conoce la configuración de conexiones sismorresistentes viga-columna precalificadas bajo norma AISC 358: placas de momento soldadas en patines y placas de cortante empernadas en alma, garantizando la ductilidad estructural ante eventos sísmicos severos.",
            "fig1": "fig_11_1_conexion_viga_columna.png",
            "cap1": "Figura 11.1: Detalle de nodo viga-columna sismorresistente con placa empernada y soldadura de bisel CJP.",
            "sub2": "11.2. Técnicas de Izaje, Nivelación, Aplomado y Pernos de Alta Resistencia",
            "text2": "Coordina maniobras de izaje seguro con grúas móviles: cálculo de centro de gravedad, capacidad de eslingas de cable y uso de vientos para control de giro. Realiza el aplomado y nivelación topográfica con estación total, e instala pernos de alta resistencia ASTM A325/A490 aplicando torque controlado con llave dinamométrica calibrada.",
            "fig2": "fig_11_2_montaje_izaje.png",
            "cap2": "Figura 11.2: Maniobras de izaje con grúa telescópica, eslingas balanceadas a 60° y control antigiro."
        },
        # Cap 12 (Página 13)
        {
            "num": 12,
            "title": "12. SINERGIA ELECTROMECÁNICA: NAVES INDUSTRIALES Y SUBESTACIONES",
            "sub1": "12.1. El Técnico Polivalente en Edificaciones Industriales",
            "text1": "La frontera entre la electricidad y la construcción metálica desaparece en la nave industrial moderna. El técnico del BTP posee la versatilidad de montar pórticos de acero, fijar arriostramientos y cerchas, y de forma inmediata tender canalizaciones de bandejas portacables tipo escalera en altura para distribuir alimentadores de fuerza y control.",
            "fig1": "fig_12_1_nave_industrial.png",
            "cap1": "Figura 12.1: Distribución porcentual presupuestaria de partidas civiles y electromecánicas en naves industriales.",
            "sub2": "12.2. Salas Eléctricas Modulares (E-Houses) y Mallas Equipotenciales",
            "text2": "Participa en la integración de salas eléctricas prefabricadas modulares transportables. Asegura la equipotencialidad soldando platinas de cobre a la estructura de acero mediante soldadura exotérmica (Cadweld), garantizando que toda masa metálica esté al mismo potencial de tierra para eliminar tensiones de paso y de contacto peligrosas.",
            "fig2": "fig_12_2_subestacion_modular.png",
            "cap2": "Figura 12.2: Distribución de equipos en sala eléctrica modular transportable y malla de puesta a tierra integral."
        },
        # Cap 13 (Página 14)
        {
            "num": 13,
            "title": "13. COMPETENCIAS HUMANAS, ÉTICA Y GESTIÓN DE PROYECTOS",
            "sub1": "13.1. Habilidades Socioemocionales y Trabajo Seguro en Altura",
            "text1": "El perfil técnico se complementa con sólidas actitudes personales: liderazgo de cuadrilla, comunicación técnica asertiva y rigurosa disciplina operacional. En tareas de montaje en altura utiliza arnés de cuerpo entero de cuatro anillos, doble línea de vida con absorbedor de impacto y líneas de vida horizontales certificadas bajo norma OSHA 1926.",
            "fig1": "fig_13_1_competencias_radar.png",
            "cap1": "Figura 13.1: Diagrama radial de competencias socio-conductuales y madurez operacional del egresado.",
            "sub2": "13.2. Ética Profesional, Estimación de Costos y Control de Calidad",
            "text2": "Posee principios éticos inquebrantables: rechaza el uso de consumibles deteriorados o falsear reportes de inspección. Elabora listas de materiales (BOM), análisis de precios unitarios (APU) para licitaciones y cronogramas de avance de obra en diagramas de Gantt, coordinando la trazabilidad de aceros y componentes eléctricos.",
            "fig2": "fig_13_2_gestion_proyectos.png",
            "cap2": "Figura 13.2: Fases metodológicas de la gestión de proyectos técnicos electromecánicos y aseguramiento de calidad."
        },
        # Cap 14 (Página 15)
        {
            "num": 14,
            "title": "14. CAMPO LABORAL, SALIDAS OCUPACIONALES Y EMPLEABILIDAD",
            "sub1": "14.1. Inserción en la Industria Energética, Minera y de la Construcción",
            "text1": "El graduado dispone de un abanico ocupacional amplio: electromecánico de mantenimiento en plantas de manufactura continua, soldador estructural calificado en obras de infraestructura civil, armador de estructuras metálicas en maestranzas, instalador electricista certificado en complejos comerciales y técnico de comisionamiento de proyectos renovables.",
            "fig1": "fig_14_1_trayectoria_laboral.png",
            "cap1": "Figura 14.1: Distribución de egresados técnicos en los principales sectores de absorción y demanda del mercado.",
            "sub2": "14.2. Certificaciones Adicionales y Articulación Universitaria",
            "text2": "El egresado cuenta con bases para obtener el carné oficial de instalador electricista y homologaciones de soldador AWS 3G/4G/6G. Su formación le permite emprender servicios contratistas independientes o proseguir estudios de ingeniería eléctrica, electromecánica o metalúrgica con homologación directa de competencias.",
            "fig2": "fig_14_2_ruta_certificaciones.png",
            "cap2": "Figura 14.2: Trayectoria progresiva de desarrollo profesional, certificaciones especializadas y continuidad superior."
        },
        # Cap 15 (Página 16)
        {
            "num": 15,
            "title": "15. CONCLUSIONES Y MARCO NORMATIVO INTERNACIONAL",
            "sub1": "15.1. Síntesis Integradora del Perfil de Egreso BTP",
            "text1": "El Bachillerato Técnico Profesional en Electricidad y Construcciones Metálicas entrega un técnico polivalente de clase mundial. Su dominio integral de la física aplicada, la destreza manual normalizada y la conciencia de seguridad ocupacional lo posicionan como un agente transformador de la productividad industrial con alta demanda laboral.",
            "fig1": "fig_15_1_matriz_perfil.png",
            "cap1": "Figura 15.1: Matriz de consolidación sinérgica de competencias técnicas, humanas y normativas del egresado.",
            "sub2": "15.2. Catálogo de Normas Técnicas de Referencia Obligatoria",
            "text2": "El ejercicio profesional se rige por: NFPA 70 (NEC) y NFPA 70E (Seguridad eléctrica laboral), IEEE 142 (Puesta a tierra), IEC 61131 (PLCs), AWS D1.1 (Soldadura en acero), AISC 360 (Estructuras de acero), ASME Boiler & Pressure Vessel Code Sección IX e ISO 9606-1 (Calificación de soldadores).",
            "fig2": "fig_15_2_catalogo_normas.png",
            "cap2": "Figura 15.2: Jerarquía de normas técnicas rectoras internacionales que certifican el ejercicio del técnico egresado."
        }
    ]

    for chap in chapters:
        story.append(Paragraph(chap["title"], page_h1_style))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=4, spaceBefore=1))
        
        # Subsección X.1
        sub1_name = chap.get("sub1") or chap.get("sub2_title")
        story.append(Paragraph(sub1_name, page_h2_style))
        story.append(Paragraph(chap["text1"], body_style))
        story.append(Image(str(FIGURES_DIR / chap["fig1"]), width=480, height=92))
        story.append(Paragraph(chap["cap1"], caption_style))
        
        # Subsección X.2 con su figura técnica dedicada
        story.append(Paragraph(chap["sub2"], page_h2_style))
        story.append(Paragraph(chap["text2"], body_style))
        story.append(Image(str(FIGURES_DIR / chap["fig2"]), width=480, height=92))
        story.append(Paragraph(chap["cap2"], caption_style))
        
        story.append(PageBreak())

    # Compilación final
    print(f"[*] Compilando documento PDF formal de 16 paginas en: {OUTPUT_PDF}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    
    file_size_mb = OUTPUT_PDF.stat().st_size / (1024 * 1024)
    print(f"[OK] Documento PDF generado exitosamente: {OUTPUT_PDF}")
    print(f"     Tamano: {file_size_mb:.2f} MB")


def main():
    print("=" * 70)
    print("GENERADOR DEL PERFIL DEL EGRESADO BTP (ELECTRICIDAD Y CONSTR. METÁLICAS)")
    print("Versión con Catálogo Completo de 31 Figuras Técnicas (X.1 y X.2)")
    print("=" * 70)
    generate_all_31_figures()
    build_pdf()
    print("=" * 70)


if __name__ == "__main__":
    main()
