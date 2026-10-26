#!/usr/bin/env python3
"""generate_btp_document.py - Generador de documento técnico PDF formal

Tema: "El perfil del egresado del BTP en Electricidad y Construcciones Metálicas"
Requisitos:
- Mínimo 15 páginas (se generan 16 páginas).
- Formato A4 (210 x 297 mm = 595.27 x 841.89 pt).
- Distribución de área por página:
  * >15% en imagen / diagrama técnico (dimensiones ~480 x 165 pt = 79,200 pt² ≈ 15.8% del área total).
  * ~40% en texto técnico estructurado con rigor académico y formativo.
  * ~44% restante en blancos, márgenes, cabeceras y pies de página profesionales.
- Generación de gráficos técnicos con Matplotlib y compilación vectorial con ReportLab.
"""

import os
import sys
from pathlib import Path

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
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

# Dimensiones A4 en puntos
PAGE_WIDTH, PAGE_HEIGHT = A4
FIGURES_DIR = Path("export/pdf_figures")
OUTPUT_PDF = Path("export/El_Perfil_del_Egresado_BTP_Electricidad_y_Construcciones_Metalicas.pdf")


class NumberedCanvas(canvas.Canvas):
    """Canvas de dos pasadas para numerar páginas de forma 'Página X de Y' y agregar encabezado/pie."""
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
        
        # Omitir decoraciones en portada (página 1)
        if page_num > 1:
            # Encabezado
            self.setStrokeColor(colors.HexColor("#1A365D"))
            self.setLineWidth(1)
            self.line(40, PAGE_HEIGHT - 35, PAGE_WIDTH - 40, PAGE_HEIGHT - 35)
            
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#1A365D"))
            self.drawString(40, PAGE_HEIGHT - 30, "PERFIL DEL EGRESADO — BTP EN ELECTRICIDAD Y CONSTRUCCIONES METÁLICAS")
            
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(colors.HexColor("#4A5568"))
            self.drawRightString(PAGE_WIDTH - 40, PAGE_HEIGHT - 30, "Marco de Competencias Profesionales")
            
            # Pie de página
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.75)
            self.line(40, 40, PAGE_WIDTH - 40, 40)
            
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(40, 28, "Educación Técnico Profesional • Formación Basada en Competencias Laborales")
            self.drawRightString(PAGE_WIDTH - 40, 28, f"Página {page_num} de {total_pages}")
            
        self.restoreState()


def generate_all_figures():
    """Genera las 16 figuras técnicas en alta resolución (DPI 300) con Matplotlib."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    
    plt.rcParams.update({
        'font.sans-serif': 'DejaVu Sans',
        'font.family': 'sans-serif',
        'axes.edgecolor': '#CBD5E1',
        'axes.linewidth': 0.8,
        'grid.color': '#E2E8F0',
        'grid.linestyle': '--',
        'grid.alpha': 0.7
    })
    
    # -------------------------------------------------------------------------
    # Figura 1: Portada - Ecosistema Electromecánico
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    fig.patch.set_facecolor('#0F172A')
    ax.set_facecolor('#0F172A')
    
    # Diagrama de bloques sinérgicos
    rect1 = plt.Rectangle((0.08, 0.2), 0.38, 0.6, facecolor='#1E3A8A', edgecolor='#60A5FA', lw=2, transform=ax.transAxes)
    rect2 = plt.Rectangle((0.54, 0.2), 0.38, 0.6, facecolor='#831843', edgecolor='#F472B6', lw=2, transform=ax.transAxes)
    ax.add_patch(rect1)
    ax.add_patch(rect2)
    
    ax.text(0.27, 0.58, "BTP ELECTRICIDAD", color='#FFFFFF', fontsize=12, weight='bold', ha='center', va='center', transform=ax.transAxes)
    ax.text(0.27, 0.40, "• Redes de Distribución\n• Automatización y PLC\n• Subestaciones y Motores", color='#BFDBFE', fontsize=8, ha='center', va='center', transform=ax.transAxes)
    
    ax.text(0.73, 0.58, "BTP CONST. METÁLICAS", color='#FFFFFF', fontsize=12, weight='bold', ha='center', va='center', transform=ax.transAxes)
    ax.text(0.73, 0.40, "• Soldadura SMAW/GMAW/GTAW\n• Cálculo Estructural AISC\n• Ensayos No Destructivos", color='#FBCFE8', fontsize=8, ha='center', va='center', transform=ax.transAxes)
    
    ax.annotate("", xy=(0.53, 0.5), xytext=(0.47, 0.5), xycoords='axes fraction', arrowprops=dict(arrowstyle="<->", color="#38BDF8", lw=3))
    ax.text(0.5, 0.88, "INTERSECCIÓN ELECTROMECÁNICA INDUSTRIAL", color='#38BDF8', fontsize=9, weight='bold', ha='center', transform=ax.transAxes)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_01_portada.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 2: Demanda Ocupacional Industrial
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    sectores = ['Manufactura', 'Construcción Civil', 'Generación Eléctrica', 'Minería / Petróleo', 'Telecomunicaciones', 'Metalmecánica']
    demanda = [32, 26, 18, 12, 8, 4]
    colores = ['#1E3A8A', '#2563EB', '#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE']
    
    bars = ax.barh(sectores, demanda, color=colores, height=0.6)
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.set_xlabel('Porcentaje de Absorción Laboral (%)', fontsize=8, weight='bold')
    ax.set_title('Distribución de Inserción Laboral para Egresados Técnicos BTP', fontsize=9, weight='bold', pad=8)
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 0.8, bar.get_y() + bar.get_height()/2, f'{w}%', ha='left', va='center', fontsize=7.5, weight='bold')
    ax.set_xlim(0, 38)
    ax.tick_params(labelsize=7.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_02_demanda.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 3: Flujograma de Diagnóstico Eléctrico
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    ax.set_facecolor('#F8FAFC')
    etapas = ["1. Inspección Visual\ny Termografía", "2. Desenergización\ny Bloqueo (LOTO)", "3. Medición de\nAislamiento (Megger)", "4. Diagnóstico y\nReemplazo", "5. Pruebas Funcionales\ny Reenergización"]
    for i, etapa in enumerate(etapas):
        x = 0.05 + i * 0.19
        rect = plt.Rectangle((x, 0.25), 0.15, 0.5, facecolor='#0284C7', edgecolor='#0369A1', lw=1.5, transform=ax.transAxes, zorder=2)
        ax.add_patch(rect)
        ax.text(x + 0.075, 0.5, etapa, color='#FFFFFF', fontsize=6.8, weight='bold', ha='center', va='center', transform=ax.transAxes, zorder=3)
        if i < len(etapas) - 1:
            ax.annotate("", xy=(x + 0.19, 0.5), xytext=(x + 0.15, 0.5), xycoords='axes fraction', arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2), zorder=1)
    ax.set_title('Flujograma de Protocolo Técnico para Mantenimiento Eléctrico Industrial', fontsize=8.5, weight='bold', pad=10)
    ax.axis('off')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_03_flujograma_electrico.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 4: Esquema Unifilar Eléctrico
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    ax.plot([0.1, 0.9], [0.8, 0.8], 'k-', lw=2)  # Línea barra principal
    ax.text(0.5, 0.88, "Barra de Distribución Principal 220/127 V - 3F + N + PE", ha='center', fontsize=8, weight='bold')
    
    breakers = ["C1: Iluminación\n(1x15A / 14 AWG)", "C2: Tomacorrientes\n(1x20A / 12 AWG)", "C3: Fuerza / Clima\n(2x30A / 10 AWG)", "C4: Tablero Maquinaria\n(3x50A / 6 AWG)"]
    for i, b in enumerate(breakers):
        x = 0.2 + i * 0.2
        ax.plot([x, x], [0.8, 0.45], 'k-', lw=1.5)
        rect = plt.Rectangle((x - 0.06, 0.35), 0.12, 0.2, facecolor='#E0F2FE', edgecolor='#0284C7', lw=1.2)
        ax.add_patch(rect)
        ax.text(x, 0.2, b, ha='center', va='top', fontsize=6.8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.1)
    ax.axis('off')
    ax.set_title('Diagrama Unifilar Típico de Cuadro General de Distribución (NEC/NFPA 70)', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_04_unifilar.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 5: Curva Par-Velocidad Motor Eléctrico
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    velocidad = np.linspace(0, 100, 200)
    par = 1.5 + 4.5 * (velocidad / 100) - 5.0 * (velocidad / 100)**2
    par_arranque = 1.5
    par_nominal = 1.0
    
    ax.plot(velocidad, par, color='#DC2626', lw=2, label='Par Motor Asíncrono Trifásico')
    ax.axhline(par_nominal, color='#475569', linestyle='--', label='Par Nominal de Carga')
    ax.scatter([0], [par_arranque], color='#B91C1C', s=50, zorder=5, label='Par de Arranque (150%)')
    ax.scatter([80], [np.max(par)], color='#15803D', s=50, zorder=5, label='Par Máximo de Ruptura (250%)')
    
    ax.set_xlabel('Velocidad de Rotación (% de Velocidad Síncrona)', fontsize=8, weight='bold')
    ax.set_ylabel('Par Motor (p.u.)', fontsize=8, weight='bold')
    ax.set_title('Curva Característica de Operación Mecánica en Motores de Inducción', fontsize=8.5, weight='bold')
    ax.grid(True)
    ax.legend(fontsize=7, loc='lower left')
    ax.tick_params(labelsize=7.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_05_curva_motor.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 6: Arquitectura de Control Automatizado PLC
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    ax.set_facecolor('#F1F5F9')
    
    # Entradas, PLC, Salidas
    ax.add_patch(plt.Rectangle((0.05, 0.2), 0.22, 0.6, facecolor='#FEF3C7', edgecolor='#D97706', lw=1.5))
    ax.text(0.16, 0.7, "SENSORES / ENTRADAS", fontsize=7.5, weight='bold', ha='center')
    ax.text(0.16, 0.45, "• Finales de Carrera\n• Sensores Inductivos\n• Transmisores 4-20mA", fontsize=6.5, ha='center')
    
    ax.add_patch(plt.Rectangle((0.38, 0.15), 0.24, 0.7, facecolor='#DBEAFE', edgecolor='#2563EB', lw=2))
    ax.text(0.50, 0.72, "CONTROLADOR PLC", fontsize=8, weight='bold', color='#1E40AF', ha='center')
    ax.text(0.50, 0.45, "CPU + Módulos I/O\nLógica Ladder / FBD\nComunicaciones Modbus/IP", fontsize=6.5, ha='center')
    
    ax.add_patch(plt.Rectangle((0.73, 0.2), 0.22, 0.6, facecolor='#DCFCE7', edgecolor='#16A34A', lw=1.5))
    ax.text(0.84, 0.7, "ACTUADORES / SALIDAS", fontsize=7.5, weight='bold', ha='center')
    ax.text(0.84, 0.45, "• Contactores de Potencia\n• Variadores de Freq (VFD)\n• Válvulas Neumáticas", fontsize=6.5, ha='center')
    
    ax.annotate("", xy=(0.37, 0.5), xytext=(0.28, 0.5), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    ax.annotate("", xy=(0.72, 0.5), xytext=(0.63, 0.5), arrowprops=dict(arrowstyle="->", color="#0F172A", lw=2))
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Estructura de Automatización Industrial y Lazo de Control Programable', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_06_plc_control.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 7: Fronteras de Seguridad Eléctrica (NFPA 70E)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    
    circles = [
        (0.8, '#FCA5A5', 'Frontera de Arco Eléctrico (Arc Flash Boundary)'),
        (0.55, '#FDE047', 'Límite de Aproximación Restringida (Personal Calificado)'),
        (0.3, '#86EFAC', 'Límite de Aproximación Prohibida (Riesgo Crítico de Choque)')
    ]
    for r, col, label in circles:
        circle = plt.Circle((0.35, 0.5), r*0.45, facecolor=col, edgecolor='#1E293B', lw=1, alpha=0.85)
        ax.add_patch(circle)
        
    ax.scatter([0.35], [0.5], color='red', marker='x', s=80, lw=3, label='Conductor Energizado Expuesto')
    ax.text(0.72, 0.75, "1. Límite de Choque", fontsize=7.5, weight='bold', color='#15803D')
    ax.text(0.72, 0.50, "2. Límite Restringido", fontsize=7.5, weight='bold', color='#B45309')
    ax.text(0.72, 0.25, "3. Frontera Arc Flash", fontsize=7.5, weight='bold', color='#B91C1C')
    
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Zonificación de Seguridad y Aproximación a Partes Energizadas (NFPA 70E)', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_07_seguridad_electrica.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 8: Taxonomía de Procesos de Construcciones Metálicas
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    procesos = ['Corte Térmico\n(Oxi/Plasma)', 'Mecanizado y\nPlegado', 'Soldadura por\nArco Eléctrico', 'Armado y\nPre-ensamble', 'Tratamiento Superficial\ny Pintura']
    complejidad = [65, 75, 95, 85, 60]
    colores = ['#047857', '#059669', '#10B981', '#34D399', '#6EE7B7']
    
    bars = ax.bar(procesos, complejidad, color=colores, width=0.55)
    ax.set_ylabel('Nivel de Destreza Técnica Requerido (%)', fontsize=8, weight='bold')
    ax.set_ylim(0, 110)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    ax.set_title('Competencias del Taller Metalmecánico según Etapa de Transformación', fontsize=8.5, weight='bold')
    for b in bars:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width()/2, h + 2, f'{h}%', ha='center', fontsize=7.5, weight='bold')
    ax.tick_params(labelsize=7)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_08_taxonomia_metalica.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 9: Morfología del Cordón de Soldadura y ZAT
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    ax.set_facecolor('#F8FAFC')
    
    # Placas base
    ax.add_patch(plt.Rectangle((0.1, 0.2), 0.35, 0.4, facecolor='#94A3B8', edgecolor='#334155', lw=1.5))
    ax.add_patch(plt.Rectangle((0.55, 0.2), 0.35, 0.4, facecolor='#94A3B8', edgecolor='#334155', lw=1.5))
    
    # Cordón y ZAT
    ax.add_patch(plt.Polygon([[0.40, 0.2], [0.60, 0.2], [0.65, 0.6], [0.5, 0.75], [0.35, 0.6]], facecolor='#EA580C', edgecolor='#9A3412', lw=1.5))
    ax.add_patch(plt.Polygon([[0.43, 0.2], [0.57, 0.2], [0.60, 0.58], [0.5, 0.7], [0.40, 0.58]], facecolor='#F97316', edgecolor='#C2410C', lw=1))
    
    ax.text(0.5, 0.45, "Zona Fundida\n(ZF)", color='white', weight='bold', fontsize=7, ha='center')
    ax.text(0.38, 0.35, "ZAT", color='#7C2D12', weight='bold', fontsize=6.5, ha='center')
    ax.text(0.62, 0.35, "ZAT", color='#7C2D12', weight='bold', fontsize=6.5, ha='center')
    ax.text(0.25, 0.4, "Metal Base (MB)\nAcero Estructural", color='#0F172A', weight='bold', fontsize=7, ha='center')
    ax.text(0.75, 0.4, "Metal Base (MB)\nAcero Estructural", color='#0F172A', weight='bold', fontsize=7, ha='center')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0.1, 0.85)
    ax.axis('off')
    ax.set_title('Estructura Metalúrgica de la Junta Soldada: Zona Fundida y Afectada Térmicamente (ZAT)', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_09_morfologia_soldadura.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 10: Comparativa de Procesos de Soldadura
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    procesos = ['SMAW (Electrodo)', 'GMAW (MIG/MAG)', 'FCAW (Flux-Cored)', 'GTAW (TIG)']
    tasa_dep = [1.8, 4.2, 5.5, 1.2]
    calidad_est = [80, 85, 88, 98]
    
    x = np.arange(len(procesos))
    w = 0.35
    ax.bar(x - w/2, tasa_dep, width=w, label='Tasa de Deposición (kg/h)', color='#4338CA')
    ax2 = ax.twinx()
    ax2.plot(x + w/2, calidad_est, color='#EA580C', marker='o', lw=2, label='Acabado Estético / Integridad (%)')
    
    ax.set_xticks(x)
    ax.set_xticklabels(procesos, fontsize=7)
    ax.set_ylabel('Rendimiento (kg/h)', fontsize=7.5, color='#4338CA', weight='bold')
    ax2.set_ylabel('Calidad (%)', fontsize=7.5, color='#EA580C', weight='bold')
    ax2.set_ylim(50, 105)
    ax.set_title('Análisis Comparativo de Procesos de Soldadura por Arco', fontsize=8.5, weight='bold')
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_10_comparativa_procesos.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 11: Inspección de Discontinuidades y Ensayos No Destructivos (END)
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    defectos = ['Socavado Marginal', 'Porosidad Interna', 'Falta de Fusión', 'Fisura Longitudinal', 'Inclusión de Escoria']
    metodos = ['Inspección Visual (VT)', 'Radiografía (RT)', 'Ultrasonido (UT)', 'Partículas Magnéticas (MT)', 'Líquidos Penetrantes (PT)']
    efectividad = [
        [95, 20, 30, 40, 10],  # VT
        [40, 98, 70, 85, 90],  # RT
        [30, 75, 98, 95, 80],  # UT
        [90, 10, 85, 98, 20],  # MT
        [95, 0, 10, 90, 15]    # PT
    ]
    cax = ax.imshow(efectividad, cmap='Blues', aspect='auto')
    ax.set_xticks(np.arange(len(defectos)))
    ax.set_yticks(np.arange(len(metodos)))
    ax.set_xticklabels(defectos, fontsize=6.8, rotation=15, ha='right')
    ax.set_yticklabels(metodos, fontsize=6.8)
    for i in range(len(metodos)):
        for j in range(len(defectos)):
            ax.text(j, i, f'{efectividad[i][j]}%', ha='center', va='center', color='black' if efectividad[i][j] < 60 else 'white', fontsize=6.5, weight='bold')
    ax.set_title('Matriz de Sensibilidad de Ensayos No Destructivos según Discontinuidad (AWS D1.1)', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_11_ensayos_ndt.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 12: Detalle Constructivo Conexión Viga-Columna AISC
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    # Columna
    ax.add_patch(plt.Rectangle((0.15, 0.1), 0.12, 0.8, facecolor='#475569', edgecolor='#0F172A', lw=1.5))
    ax.text(0.21, 0.85, "Columna HEB", ha='center', color='white', weight='bold', fontsize=7)
    
    # Viga
    ax.add_patch(plt.Rectangle((0.27, 0.4), 0.55, 0.25, facecolor='#64748B', edgecolor='#0F172A', lw=1.5))
    ax.text(0.55, 0.5, "Viga IPE 300", ha='center', color='white', weight='bold', fontsize=7.5)
    
    # Placa y pernos
    ax.add_patch(plt.Rectangle((0.27, 0.35), 0.04, 0.35, facecolor='#DC2626', edgecolor='#991B1B', lw=1))
    for y_pos in [0.42, 0.52, 0.62]:
        ax.scatter([0.33, 0.37], [y_pos, y_pos], color='#FEF08A', edgecolor='#854D0E', s=35, zorder=5)
    
    ax.text(0.45, 0.25, "Pernos ASTM A325 Pretensados\n+ Cordón de Filete E70XX", fontsize=6.5, weight='bold', color='#B91C1C')
    ax.set_xlim(0, 0.95)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Conexión Estructural a Momento Viga-Columna s/ Normativa AISC 360', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_12_conexion_viga_columna.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 13: Sinergia Electromecánica en Naves Industriales
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    ax.set_facecolor('#F8FAFC')
    
    # Pórtico
    ax.plot([0.15, 0.15, 0.5, 0.85, 0.85], [0.1, 0.7, 0.9, 0.7, 0.1], color='#334155', lw=3)
    ax.text(0.5, 0.92, "Pórtico Reticulado de Acero Estructural", ha='center', fontsize=7.5, weight='bold')
    
    # Bandeja portacables
    ax.add_patch(plt.Rectangle((0.25, 0.55), 0.5, 0.08, facecolor='#38BDF8', edgecolor='#0369A1', lw=1.2))
    ax.text(0.5, 0.59, "Bandeja Portacables Tipo Escalerilla (Puesta a Tierra Solidaria)", ha='center', fontsize=6.8, weight='bold', color='#0C4A6E')
    
    # Conductores y bajante tierra
    ax.plot([0.27, 0.73], [0.57, 0.57], 'r--', lw=1.5)
    ax.plot([0.75, 0.75, 0.85], [0.55, 0.1, 0.1], color='#16A34A', lw=2)
    ax.text(0.77, 0.3, "Malla a Tierra de Estructura\ny Equipos (IEEE 80)", color='#166534', fontsize=6.5, weight='bold')
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Integración de Canalizaciones Eléctricas y Sistema de Protección en Nave Metálica', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_13_sinergia_electromecanica.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 14: Gráfico Radial de Competencias Integrales
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300, subplot_kw=dict(polar=True))
    categories = ['Destreza\nTécnica', 'Seguridad\nIndustrial', 'Interpretación\nPlanos', 'Trabajo en\nEquipo', 'Gestión de\nCostos', 'Resolución de\nProblemas']
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    values_elec = [92, 95, 90, 85, 75, 88]
    values_elec += values_elec[:1]
    values_met = [95, 90, 92, 88, 80, 85]
    values_met += values_met[:1]
    
    ax.plot(angles, values_elec, color='#2563EB', lw=1.5, label='BTP Electricidad')
    ax.fill(angles, values_elec, color='#3B82F6', alpha=0.25)
    
    ax.plot(angles, values_met, color='#DC2626', lw=1.5, label='BTP Const. Metálicas')
    ax.fill(angles, values_met, color='#EF4444', alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=6.5, weight='bold')
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'], fontsize=5.5)
    ax.set_ylim(0, 100)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.1), fontsize=7)
    ax.set_title('Perfil Comparativo de Competencias Técnicas y Habilidades Blandas', fontsize=8, weight='bold', pad=15)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_14_competencias_radar.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 15: Trayectoria de Carrera y Opciones Laborales
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    etapas_carrera = ["Egresado BTP\n(Nivel Operativo)", "Técnico Especialista\n(Supervisor / Inspector)", "Jefe de Taller / Montaje\n(Gestión y Costos)", "Ingeniería / Emprendedor\n(Dirección de Obras)"]
    salarios = [1.0, 1.6, 2.3, 3.5]
    
    x = np.arange(len(etapas_carrera))
    ax.plot(x, salarios, marker='s', color='#0284C7', lw=2.5, markersize=8)
    for i, txt in enumerate(salarios):
        ax.text(x[i], salarios[i] + 0.18, f'{txt}x Base', ha='center', fontsize=7.5, weight='bold', color='#0369A1')
    ax.set_xticks(x)
    ax.set_xticklabels(etapas_carrera, fontsize=7)
    ax.set_ylabel('Proyección Salarial / Responsabilidad', fontsize=7.5, weight='bold')
    ax.set_ylim(0.5, 4.2)
    ax.grid(True)
    ax.set_title('Trayectoria de Crecimiento Profesional y Proyección Salarial del Egresado', fontsize=8.5, weight='bold')
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_15_trayectoria_laboral.png", dpi=300, bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Figura 16: Resumen Ejecutivo y Marco Normativo
    # -------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.4, 2.2), dpi=300)
    ax.set_facecolor('#0F172A')
    
    cajas = [
        (0.05, "ELECTRICIDAD", "• NFPA 70 (NEC)\n• NFPA 70E (Seguridad)\n• IEEE Std 80 / 142\n• NEMA / IEC 60947", '#38BDF8'),
        (0.38, "CONSTRUCCIÓN METÁLICA", "• AWS D1.1 (Soldadura Acero)\n• AISC 360 (Estructuras)\n• ASME Sec. IX (Calderería)\n• ISO 9606 (Cualificación)", '#F472B6'),
        (0.71, "GESTIÓN Y CALIDAD", "• ISO 9001 (Calidad)\n• ISO 45001 (SST)\n• OHSAS 18001\n• Normas OSHA 1910/1926", '#34D399')
    ]
    for x_pos, titulo, cuerpo, col in cajas:
        rect = plt.Rectangle((x_pos, 0.15), 0.25, 0.7, facecolor='#1E293B', edgecolor=col, lw=1.5, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x_pos + 0.125, 0.72, titulo, color=col, weight='bold', fontsize=7.2, ha='center', transform=ax.transAxes)
        ax.text(x_pos + 0.02, 0.42, cuerpo, color='#F8FAFC', fontsize=6.3, ha='left', va='center', transform=ax.transAxes)
        
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title('Compendio de Estándares Internacionales Dominados por el Egresado', color='white', fontsize=8.5, weight='bold', pad=10)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "fig_16_normativa_cierre.png", dpi=300, facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)

    print(f"[OK] Generadas 16 figuras técnicas en '{FIGURES_DIR}'.")


def build_pdf():
    """Compila el documento PDF formal de 16 páginas en formato A4."""
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    
    # Documento A4 con márgenes balanceados (margen = 36 pt = 12.7 mm)
    # Área de página: 595.27 x 841.89 pt
    # Área imprimible: 523.27 x 769.89 pt
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Estilos tipográficos profesionales
    title_cover_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        alignment=1, # Centrado
        spaceAfter=10
    )
    
    subtitle_cover_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#334155'),
        alignment=1,
        spaceAfter=20
    )
    
    page_h1_style = ParagraphStyle(
        'PageH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    
    page_h2_style = ParagraphStyle(
        'PageH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=5,
        spaceAfter=3
    )

    body_style = ParagraphStyle(
        'PageBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.2,
        leading=11.2,
        textColor=colors.HexColor('#1E293B'),
        alignment=4, # Justificado
        spaceAfter=5
    )
    
    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=7.2,
        leading=9,
        textColor=colors.HexColor('#475569'),
        alignment=1, # Centrado
        spaceAfter=6
    )

    story = []

    # =========================================================================
    # PÁGINA 1: Portada Institucional y Marco Teórico
    # =========================================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("SECRETARÍA DE EDUCACIÓN TÉCNICA Y VOCACIONAL", ParagraphStyle('Inst', fontName='Helvetica-Bold', fontSize=10, leading=12, alignment=1, textColor=colors.HexColor('#64748B'))))
    story.append(Paragraph("DIRECCIÓN GENERAL DE EDUCACIÓN MEDIA TÉCNICA", ParagraphStyle('InstSub', fontName='Helvetica', fontSize=8.5, leading=11, alignment=1, textColor=colors.HexColor('#94A3B8'))))
    story.append(Spacer(1, 25))
    
    story.append(Paragraph("EL PERFIL DEL EGRESADO DEL BACHILLERATO TÉCNICO PROFESIONAL EN ELECTRICIDAD Y CONSTRUCCIONES METÁLICAS", title_cover_style))
    story.append(HRFlowable(width="60%", thickness=2, color=colors.HexColor('#2563EB'), spaceAfter=15, spaceBefore=5))
    story.append(Paragraph("Manual de Competencias Profesionales, Perfiles Ocupacionales, Fundamentación Tecnológica y Sinergia Productiva", subtitle_cover_style))
    
    # Imagen de portada (>15% del área de la hoja A4)
    story.append(Image(str(FIGURES_DIR / "fig_01_portada.png"), width=480, height=165))
    story.append(Paragraph("Figura 1.1: Ecosistema sinérgico e interdisciplinario entre las especialidades de Electricidad y Construcciones Metálicas.", caption_style))
    story.append(Spacer(1, 10))
    
    # Texto representativo (~40% del área)
    p1_text = (
        "El presente documento técnico establece con rigurosidad académica y metodológica el perfil de egreso integral correspondiente a los programas "
        "de formación del Bachillerato Técnico Profesional (BTP) en las áreas de <b>Electricidad</b> y <b>Construcciones Metálicas</b>. La educación técnica "
        "contemporánea exige un enfoque basado en competencias laborales demostrables, articuladas directamente con los requerimientos de la industria moderna, "
        "la infraestructura pesada y la transformación tecnológica. El egresado no sólo adquiere destrezas operativas manuales y analíticas en su campo "
        "específico, sino que domina la sinergia electromecánica que define a las naves industriales, plantas de manufactura y subestaciones eléctricas.<br/><br/>"
        "A lo largo de este compendio se estructuran las 16 dimensiones fundamentales que definen el perfil de salida: competencias generales, especificidades "
        "técnicas de baja y media tensión, automatización mediante PLCs, procesos de soldeo normalizados bajo AWS y ASME, cálculo de estructuras metálicas, "
        "seguridad ocupacional NFPA 70E / OSHA y proyección de empleabilidad. Esta guía constituye el marco de referencia definitivo para evaluadores, "
        "docentes técnicos, industrias contratistas y profesionales en formación."
    )
    story.append(Paragraph(p1_text, body_style))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 2: Contexto Socio-Productivo y Demanda Ocupacional
    # =========================================================================
    story.append(Paragraph("1. CONTEXTO SOCIO-PRODUCTIVO Y JUSTIFICACIÓN DEL BTP", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("1.1. La Demanda de Técnicos Medios en la Matriz Productiva", page_h2_style))
    story.append(Paragraph(
        "El desarrollo económico y la modernización de los sectores secundario y terciario demandan un flujo continuo de capital humano calificado con "
        "capacidad de resolución en campo. Los egresados del BTP en Electricidad y Construcciones Metálicas constituyen la columna vertebral de la ejecución "
        "operativa en ingeniería. Las estadísticas del mercado laboral evidencian que más del 58% de las posiciones técnicas requeridas por la industria de "
        "la manufactura y la construcción civil corresponden precisamente a profesionales con formación técnica de nivel medio superior.<br/><br/>"
        "La aceleración de proyectos de energía renovable (parques fotovoltaicos, parques eólicos), el auge del sector logístico mediante naves industriales "
        "de acero y la modernización de redes eléctricas inteligentes (Smart Grids) han generado una brecha de talento técnico calificado. El BTP responde a "
        "este desafío dotando al graduado de destrezas estandarizadas bajo normas internacionales, permitiendo su inserción inmediata en obra.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_02_demanda.png"), width=480, height=165))
    story.append(Paragraph("Figura 2.1: Distribución porcentual de absorción ocupacional para graduados técnicos por subsector industrial.", caption_style))
    
    story.append(Paragraph("1.2. El Modelo Formativo Basado en Competencias Laborales (CBT)", page_h2_style))
    story.append(Paragraph(
        "El currículo del BTP se sustenta en tres dimensiones indisociables: el <b>Saber Conocer</b> (teoría electromagnética, ciencia de materiales, "
        "resistencia de materiales y normativa técnica), el <b>Saber Hacer</b> (destrezas psicomotrices en banco de trabajo, cableado, soldeo en diversas "
        "posiciones, manejo de instrumentación digital y herramientas de potencia) y el <b>Saber Ser</b> (conciencia de seguridad, ética laboral, honestidad "
        "en los reportes de inspección y compromiso con el trabajo colaborativo en ambientes de alta exigencia).",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 3: Ejes Formativos y Competencias Generales en Electricidad
    # =========================================================================
    story.append(Paragraph("2. BTP ELECTRICIDAD: EJES FORMATIVOS Y COMPETENCIAS GENERALES", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("2.1. Definición del Perfil Ocupacional del Técnico Electricista", page_h2_style))
    story.append(Paragraph(
        "El egresado del Bachillerato Técnico Profesional en Electricidad es un profesional capacitado para planificar, presupuestar, ejecutar, inspeccionar "
        "y mantener sistemas de energía eléctrica en baja y media tensión, tanto en entornos residenciales y comerciales como en complejos fabriles. "
        "Posee un conocimiento riguroso de la teoría de circuitos en corriente continua (CC) y alterna (CA), análisis fasorial, potencia activa, reactiva "
        "y aparente, así como técnicas avanzadas de compensación del factor de potencia.<br/><br/>"
        "Su formación le permite actuar de forma preventiva y correctiva ante contingencias en líneas de suministro, cuadros de protección y distribución, "
        "sistemas de puesta a tierra y bancos de condensadores, garantizando la continuidad del servicio eléctrico bajo estándares estrictos de eficiencia "
        "energética y reducción de pérdidas técnicas.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_03_flujograma_electrico.png"), width=480, height=165))
    story.append(Paragraph("Figura 3.1: Protocolo sistemático de diagnóstico y mantenimiento eléctrico bajo principios de confiabilidad operativa.", caption_style))
    
    story.append(Paragraph("2.2. Competencias Metodológicas de Diagnóstico", page_h2_style))
    story.append(Paragraph(
        "El técnico electricista aplica el método científico en la localización de fallas: lectura sistemática de esquemas de cableado, medición "
        "de magnitudes físicas (voltaje, corriente, resistencia de lazo, impedancia de falla a tierra y armónicos) e interpretación de datos térmicos. "
        "Sabe aplicar pruebas de aislamiento con megóhmetro para evaluar la degradación dieléctrica de conductores y bobinados antes de autorizar la energización.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 4: Instalaciones Eléctricas Residenciales y Comerciales
    # =========================================================================
    story.append(Paragraph("3. INSTALACIONES ELÉCTRICAS RESIDENCIALES Y COMERCIALES", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("3.1. Diseño y Montaje de Circuitos Derivados y Alimentadores", page_h2_style))
    story.append(Paragraph(
        "El egresado domina el cálculo y canalización de instalaciones eléctricas interiores bajo el Código Eléctrico Nacional (NEC / NFPA 70). Sabe determinar "
        "la capacidad de corriente de los conductores según la tabla de ampacidad, aplicando factores de corrección por temperatura ambiente y factores de "
        "agrupamiento de conductores en canalizaciones cerradas (tubo conduit EMT, IMC o PVC).<br/><br/>"
        "Diseña circuitos ramales dedicados para cargas de iluminación general, tomas de corriente convencionales, tomas con protección diferencial GFCI "
        "(Ground Fault Circuit Interrupter) para áreas húmedas y circuitos individuales de alta potencia para equipos de climatización y cocinas eléctricas. "
        "Calcula la caída de tensión porcentual para evitar fluctuaciones térmicas superiores al 3% en alimentadores y al 5% en la carga más lejana.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_04_unifilar.png"), width=480, height=165))
    story.append(Paragraph("Figura 4.1: Diagrama unifilar de tablero de distribución con protecciones magnetotérmicas y diferenciales.", caption_style))
    
    story.append(Paragraph("3.2. Cuadros de Cargas y Sistemas de Puesta a Tierra (SPT)", page_h2_style))
    story.append(Paragraph(
        "Elabora cuadros de balanceo de cargas entre fases para minimizar la corriente de retorno por el neutro en sistemas trifásicos tetrapolares. "
        "Instala electrodos de puesta a tierra (jabalinas de acero recubiertas de cobre - Copperweld) y diseña mallas de tierra con tratamiento químico "
        "del terreno para lograr una resistencia de dispersión inferior a 25 ohmios en instalaciones residenciales y menor a 5 ohmios en centros de cómputo.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 5: Máquinas Eléctricas y Redes Industriales
    # =========================================================================
    story.append(Paragraph("4. MÁQUINAS ELÉCTRICAS ROTATIVAS Y ESTÁTICAS", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("4.1. Motores de Inducción Trifásicos y Monofásicos", page_h2_style))
    story.append(Paragraph(
        "El motor asíncrono tipo jaula de ardilla es el elemento motriz por excelencia en la industria. El egresado de Electricidad comprende en profundidad "
        "los principios de conversión electromecánica de energía: velocidad síncrona, deslizamiento, par resistente y rendimiento nominal. Sabe interpretar "
        "la placa de características de motores (NEMA/IEC), identificar el factor de servicio, la clase de aislamiento y el régimen de servicio (S1-S8).<br/><br/>"
        "Diseña e implementa esquemas electromagnéticos de control: arranque directo, arranque estrella-triángulo (Y-Δ) para reducir la corriente de pico "
        "en la red, inversión de giro mediante enclavamientos mecánicos y eléctricos en contactores, y frenado dinámico por inyección de corriente continua.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_05_curva_motor.png"), width=480, height=165))
    story.append(Paragraph("Figura 5.1: Dinámica de par motor versus velocidad de rotación en motores de inducción con puntos críticos de operación.", caption_style))
    
    story.append(Paragraph("4.2. Transformadores y Protección de Máquinas", page_h2_style))
    story.append(Paragraph(
        "Realiza la conexión de bancos de transformadores trifásicos en configuraciones Delta-Estrella (Dy5, Dy11), Estrella-Estrella y Delta abierta. "
        "Calcula y calibra relés térmicos bimetálicos, guardamotores magnéticos y disyuntores de caja moldeada (MCCB) para salvaguardar los devanados "
        "contra sobrecargas sostenidas, desequilibrios de fase y cortocircuitos francos.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 6: Automatización Industrial, Control PLC y Energías Limpias
    # =========================================================================
    story.append(Paragraph("5. AUTOMATIZACIÓN INDUSTRIAL, PLC Y ENERGÍAS RENOVABLES", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("5.1. Controladores Lógicos Programables (PLC) e Instrumentación", page_h2_style))
    story.append(Paragraph(
        "En la era de la Industria 4.0, el técnico en electricidad no se limita al cableado tradicional; programa y comisiona PLCs compactos y modulares. "
        "Domina los lenguajes estándar de la norma IEC 61131-3, prioritariamente el diagrama de contactos (Ladder) y los bloques de funciones (FBD). "
        "Configura entradas digitales (sensores inductivos, capacitivos, ópticos y finales de carrera) y entradas analógicas (termorresistencias PT100, "
        "termocuplas tipo J/K y lazos de corriente 4-20 mA para presión y nivel).<br/><br/>"
        "Asocia el autómata con variadores de frecuencia (VFD) y arrancadores electrónicos suaves para el control fino de velocidad y rampas de aceleración "
        "en bombas, cintas transportadoras y ventiladores industriales.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_06_plc_control.png"), width=480, height=165))
    story.append(Paragraph("Figura 6.1: Arquitectura funcional de control industrial: adquisición de señales, lógica en PLC y excitación de actuadores.", caption_style))
    
    story.append(Paragraph("5.2. Integración de Sistemas Fotovoltaicos y Eficiencia Energética", page_h2_style))
    story.append(Paragraph(
        "El egresado posee competencias en transición energética: dimensionamiento de generadores solares fotovoltaicos conectados a red (Grid-Tie) "
        "y aislados con banco de baterías (Off-Grid). Conoce la conexión de cadenas de módulos (strings), inversores de onda senoidal pura, dispositivos "
        "de protección contra sobretensiones transitorias (DPS) y protocolos de inyección segura a la red eléctrica.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 7: Seguridad Eléctrica y Normativas Internacionales
    # =========================================================================
    story.append(Paragraph("6. SEGURIDAD ELÉCTRICA Y NORMATIVA NFPA 70E / OSHA", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("6.1. Peligros de la Energía Eléctrica: Choque y Arco Eléctrico", page_h2_style))
    story.append(Paragraph(
        "La vida humana es la prioridad absoluta en la práctica del técnico. El programa formativo inculca una cultura de tolerancia cero a prácticas "
        "inseguras, basada en la norma <b>NFPA 70E</b> (Seguridad Eléctrica en Lugares de Trabajo). El egresado diferencia con claridad técnica entre el riesgo "
        "de choque eléctrico por contacto directo/indirecto y el fenómeno devastador del <i>Arc Flash</i> (relámpago y ráfaga de arco), capaz de generar "
        "temperaturas superiores a 19,000 °C y ondas de presión acústica de alto impacto.<br/><br/>"
        "Comprende la delimitación estricta de las fronteras de aproximación: Frontera de Arco Eléctrico, Límite de Aproximación Limitada y Límite de "
        "Aproximación Restringida, respetando las distancias mínimas y los niveles de energía incidente en calorías por centímetro cuadrado (cal/cm²).",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_07_seguridad_electrica.png"), width=480, height=165))
    story.append(Paragraph("Figura 7.1: Delimitación de fronteras de aproximación y zonas de riesgo eléctrico según norma internacional NFPA 70E.", caption_style))
    
    story.append(Paragraph("6.2. Protocolo LOTO (Lockout / Tagout) y EPP Calificado", page_h2_style))
    story.append(Paragraph(
        "Aplica obligatoriamente el procedimiento de <b>Bloqueo y Etiquetado (LOTO)</b> según OSHA 1910.147 antes de intervenir cualquier equipo: desenergización, "
        "bloqueo físico con candado personal, colocación de tarjeta de advertencia, verificación de ausencia total de tensión con multímetro de categoría "
        "apropiada (CAT III / CAT IV) y puesta a tierra temporal para drenar tensiones inducidas residuales.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 8: Ejes Formativos y Competencias en Construcciones Metálicas
    # =========================================================================
    story.append(Paragraph("7. BTP CONSTRUCCIONES METÁLICAS: EJES Y COMPETENCIAS", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("7.1. Definición del Perfil Ocupacional del Técnico Metalmecánico", page_h2_style))
    story.append(Paragraph(
        "El egresado del Bachillerato Técnico Profesional en Construcciones Metálicas es un especialista calificado en la transformación de perfiles, "
        "láminas y tuberías de acero para la construcción de puentes, naves industriales, tanques de almacenamiento, torres de transmisión y carpintería "
        "pesada. Posee una sólida base en geometría descriptiva, trigonometría aplicada al trazado de calderería e interpretación integral de planos "
        "estructurales de taller y montaje bajo normas ANSI/AISC.<br/><br/>"
        "Domina el uso de maquinaria pesada de taller: cizallas mecánicas e hidráulicas, prensas plegadoras CNC, sierras de cinta automáticas, roladoras "
        "de perfiles y mesas de corte térmico por plasma y oxicorte. Su destreza le permite cortar y conformar materiales con tolerancias milimétricas.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_08_taxonomia_metalica.png"), width=480, height=165))
    story.append(Paragraph("Figura 8.1: Nivel de exigencia operativa y destreza en los procesos clave del taller de construcciones metálicas.", caption_style))
    
    story.append(Paragraph("7.2. Trazado y Desarrollo en Calderería Industrial", page_h2_style))
    story.append(Paragraph(
        "Aplica métodos de desarrollo geométrico por paralelas, radiales y triangulación para generar plantillas de conos truncados, tolvas piramidales, "
        "injertos de tubería a diferentes ángulos (boca de pescado) y transiciones de sección circular a rectangular, considerando siempre el espesor de "
        "la chapa y el radio de curvatura en la línea neutra del material.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 9: Procesos de Soldadura: SMAW, GMAW y GTAW
    # =========================================================================
    story.append(Paragraph("8. METALURGIA Y PROCESOS DE SOLDADURA: SMAW, GMAW Y GTAW", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("8.1. Procesos Manuales y Semiautomáticos de Soldeo", page_h2_style))
    story.append(Paragraph(
        "El núcleo técnico del soldador estructural reside en el dominio de la soldadura por arco eléctrico: soldadura manual con electrodo revestido "
        "(<b>SMAW / Shielded Metal Arc Welding</b>), soldadura bajo gas protector con alambre continuo macizo (<b>GMAW / MIG-MAG</b>) y soldadura con electrodo "
        "de tungsteno no consumible (<b>GTAW / TIG</b>). El egresado califica en posiciones 1G/1F a 4G/4F en plancha y 6G en tubería según código AWS D1.1.<br/><br/>"
        "Comprende la metalurgia de la unión: conoce la clasificación de electrodos AWS (ej. E6010 celulósico para pases de raíz de alta penetración y E7018 "
        "básico de bajo hidrógeno para pases de relleno con alta tenacidad al impacto). Regula con precisión la intensidad de corriente, voltaje de arco y "
        "velocidad de avance para evitar la formación de discontinuidades estructurales.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_09_morfologia_soldadura.png"), width=480, height=165))
    story.append(Paragraph("Figura 9.1: Corte transversal metalográfico de unión soldada: metal base, zona afectada térmicamente (ZAT) y zona fundida.", caption_style))
    
    story.append(Paragraph("8.2. Control Térmico y Prevención de Deformaciones", page_h2_style))
    story.append(Paragraph(
        "Controla la temperatura de precalentamiento y la temperatura entre pasadas para evitar la formación de martensita frágil en la ZAT de aceros "
        "de alto límite elástico. Aplica secuencias de soldeo estratégicas (paso de peregrino, soldaduras alternadas y simétricas) para equilibrar los "
        "esfuerzos residuales de contracción térmica y minimizar la distorsión angular en vigas compuestas.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 10: Procesos Avanzados de Unión: FCAW y SAW
    # =========================================================================
    story.append(Paragraph("9. PROCESOS DE ALTA PRODUCTIVIDAD: FCAW Y SAW", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("9.1. Soldadura Tubular FCAW (Flux-Cored Arc Welding)", page_h2_style))
    story.append(Paragraph(
        "Para aplicaciones de alta velocidad de deposición en obra civil y montaje de puentes, el egresado domina el proceso <b>FCAW</b> tanto autoprotegido "
        "(Innershield) como con gas de asistencia (Outershield con mezcla Ar/CO₂). El alambre tubular con fundente interno permite depositar hasta 6 kg/h "
        "de metal de aporte, manteniendo excelentes propiedades mecánicas incluso ante corrientes de aire moderadas en campo.<br/><br/>"
        "Comprende la química del fundente: eliminación de impurezas de azufre y fósforo, desoxidación del baño de fusión y formación de escorias de rápida "
        "solidificación que soportan el charco de soldadura en posiciones verticales ascendentes (3G) y sobre cabeza (4G).",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_10_comparativa_procesos.png"), width=480, height=165))
    story.append(Paragraph("Figura 10.1: Análisis comparativo de tasas de deposición horaria y acabado superficial entre métodos de soldadura.", caption_style))
    
    story.append(Paragraph("9.2. Soldadura por Arco Sumergido (SAW) en Vigas Armadas", page_h2_style))
    story.append(Paragraph(
        "En fábricas de estructuras pesadas, el técnico opera equipos automáticos de soldadura por <b>Arco Sumergido (SAW)</b> para la confección de vigas "
        "armadas de alma llena (vigas de sección variable o vigas carril para puentes grúa). Sabe preparar el lecho de fundente granular, ajustar la tensión "
        "de arco (28-36 V) y corrientes elevadas (400-800 A) con electrodos gruesos de 3.2 mm a 4.0 mm, logrando penetraciones profundas y libres de salpicaduras.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 11: Control de Calidad y Ensayos No Destructivos (END)
    # =========================================================================
    story.append(Paragraph("10. CONTROL DE CALIDAD Y ENSAYOS NO DESTRUCTIVOS (END / NDT)", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("10.1. Criterios de Aceptación según Código Estructural AWS D1.1", page_h2_style))
    story.append(Paragraph(
        "Una estructura soldada no está completa sin una verificación rigurosa de calidad. El egresado actúa como primer inspector de obra conociendo "
        "los criterios de aceptación estipulados en la cláusula 6 de la norma <b>AWS D1.1</b> para cargas estáticas y dinámicas (cíclicas). Sabe utilizar "
        "galgas de soldadura (tipo Cambridge y de puente de leva) para medir con exactitud la garganta teórica y real de filetes, la sobremonta (refuerzo) "
        "y el socavado marginal en bordes.<br/><br/>"
        "Distingue entre imperfecciones admisibles y defectos inaceptables que comprometen la resistencia a fatiga: poros agrupados superiores al límite "
        "porcentual, faltas de fusión inter-pases, penetración incompleta en biseles y cualquier tipo de grieta en cráter o cordón.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_11_ensayos_ndt.png"), width=480, height=165))
    story.append(Paragraph("Figura 11.1: Eficacia y alcance de detección de métodos de ensayos no destructivos frente a discontinuidades típicas.", caption_style))
    
    story.append(Paragraph("10.2. Práctica de Ensayos Superficiales y Volumétricos", page_h2_style))
    story.append(Paragraph(
        "Aplica de forma autónoma ensayos por <b>Líquidos Penetrantes (PT)</b> (limpieza previa, tiempo de penetración de 10-15 min, remoción controlada "
        "y aplicación de revelador blanco) y <b>Partículas Magnéticas (MT)</b> mediante yugo electromagnético para hallar discontinuidades subsuperficiales. "
        "Asimismo, interpreta reportes de Ultrasonido (UT) y placas radiográficas (RT) emitidos por inspectores nivel II / CWI.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 12: Fabricación y Montaje de Estructuras de Acero
    # =========================================================================
    story.append(Paragraph("11. FABRICACIÓN Y MONTAJE DE ESTRUCTURAS DE ACERO", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("11.1. Ensamblaje en Taller y Geometría de Pórticos", page_h2_style))
    story.append(Paragraph(
        "En el taller de estructuras, el egresado dirige el armado de componentes estructurales complejos: cerchas reticuladas triangulares, columnas "
        "compuestas cajón y vigas de celosía con perfiles tubulares estructurales (HSS). Utiliza mesas de armado con topes mecánicos y plantillas de fijación "
        "para garantizar que la diagonalidad y cuadratura del conjunto se mantenga dentro de las tolerancias de fabricación AISC (+/- 2 mm en longitudes "
        "superiores a 12 metros).<br/><br/>"
        "Prepara los biseles de unión mediante corte mecanizado en V o bisel doble en K, limpiando el óxido de laminación y cascarilla mediante amolado "
        "o granallado con aire comprimido (grado SSPC-SP 6 / Sa 2.5) previo al soldeo definitivo.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_12_conexion_viga_columna.png"), width=480, height=165))
    story.append(Paragraph("Figura 12.1: Geometría de nudo viga-columna atornillado con pernos de alta resistencia pretensados según AISC 360.", caption_style))
    
    story.append(Paragraph("11.2. Montaje en Obra y Conexiones Atornilladas de Alta Resistencia", page_h2_style))
    story.append(Paragraph(
        "En faena de montaje en terreno, participa en el izaje seguro de elementos pesados con grúas móviles: cálculo del centro de gravedad, selección de "
        "eslingas sintéticas de poliéster o cadenas de acero grado 80 y comunicación por señas normalizadas de rigger. Ejecuta el apriete de conexiones "
        "con pernos estructurales ASTM A325 y A490 utilizando torquímetros calibrados o el método del giro de la tuerca para alcanzar la tracción mínima de diseño.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 13: Sinergia Electromecánica en Proyectos Industriales
    # =========================================================================
    story.append(Paragraph("12. SINERGIA ELECTROMECÁNICA: NAVES INDUSTRIALES Y SUBESTACIONES", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("12.1. El Punto de Encuentro entre Estructura y Electricidad", page_h2_style))
    story.append(Paragraph(
        "En la práctica industrial real, las disciplinas no operan de forma aislada. La nave industrial metálica actúa simultáneamente como soporte "
        "mecánico estructural y como masa equipotencial del sistema eléctrico. Aquí reside la ventaja competitiva superior del egresado: comprende cómo "
        "la estructura de acero interactúa con las cargas eléctricas dinámicas y los campos electromagnéticos producidos por corrientes elevadas.<br/><br/>"
        "Diseña y monta la soportería para bandejas portacables galvanizadas en caliente, soportes de transformadores en altura, fijación de ductos de barras "
        "(busways) y ménsulas antivibratorias para compresores y generadores diésel de emergencia sin debilitar el ala o alma de los perfiles estructurales.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_13_sinergia_electromecanica.png"), width=480, height=165))
    story.append(Paragraph("Figura 13.1: Coexistencia constructiva de canalizaciones eléctricas de fuerza y malla de tierra sobre perfiles de acero.", caption_style))
    
    story.append(Paragraph("12.2. Continuidad Eléctrica y Protección Atmosférica", page_h2_style))
    story.append(Paragraph(
        "Garantiza la unión equipotencial (bonding) entre todos los tramos de la nave metálica y el sistema de electrodos en tierra, evitando chispas "
        "peligrosas por corrientes de cortocircuito o descargas atmosféricas. Instala pararrayos tipo PDC o puntas Franklin y bajantes de cobre con fijaciones "
        "termofusión (soldadura exotérmica Cadweld) sobre la estructura metálica según lineamientos de la norma IEEE 80 e IEC 62305.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 14: Habilidades Blandas, Ética y Gestión de Proyectos
    # =========================================================================
    story.append(Paragraph("13. COMPETENCIAS HUMANAS, ÉTICA Y GESTIÓN DE PROYECTOS", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("13.1. Habilidades Socioemocionales y Trabajo en Cuadrilla", page_h2_style))
    story.append(Paragraph(
        "El éxito técnico en faena no depende exclusivamente del dominio de la herramienta, sino de la capacidad de comunicarse con precisión y coordinar "
        "actividades en equipos multidisciplinarios. El egresado está formado para trabajar bajo presión de cronograma sin comprometer los estándares de "
        "calidad ni la seguridad de sus compañeros. Desarrolla escucha activa para interpretar instrucciones complejas del ingeniero residente de obra "
        "y transmite directrices claras a los ayudantes de taller.<br/><br/>"
        "Fomenta la resolución colaborativa de problemas en campo ante interferencias no previstas entre instalaciones de aire acondicionado, tuberías de vapor "
        "y bandejas eléctricas, proponiendo ajustes constructivos viables y documentados en planos <i>as-built</i>.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_14_competencias_radar.png"), width=480, height=165))
    story.append(Paragraph("Figura 14.1: Evaluación holística de competencias: equilibrio entre excelencia operativa, seguridad y gestión humana.", caption_style))
    
    story.append(Paragraph("13.2. Ética Ocupacional y Cubicaciones de Materiales", page_h2_style))
    story.append(Paragraph(
        "El egresado actúa con estricta integridad en la certificación de trabajos: no oculta discontinuidades bajo masillas o pinturas, rechaza materiales "
        "que no cuenten con certificado de calidad de colada (Mill Test Report) y respeta las normativas medioambientales para la disposición de escorias, "
        "restos de electrodos y aceites dieléctricos de transformadores en desuso. Realiza metrados y cómputos de materiales con exactitud para optimizar costos.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 15: Campo Laboral, Salidas Ocupacionales y Empleabilidad
    # =========================================================================
    story.append(Paragraph("14. CAMPO LABORAL, SALIDAS OCUPACIONALES Y EMPLEABILIDAD", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("14.1. Nichos Ocupacionales para el BTP en Electricidad", page_h2_style))
    story.append(Paragraph(
        "Los graduados del BTP en Electricidad acceden a un abanico diverso de puestos en la industria energética e industrial: "
        "<b>Técnico de Mantenimiento Eléctrico de Planta</b>, <b>Bobinador de Máquinas Eléctricas</b>, <b>Instalador y Comisionador de Sistemas Fotovoltaicos</b>, "
        "<b>Liniero en Redes de Distribución de Media Tensión</b>, <b>Panelista de Armado de Cuadros de Control</b> y <b>Técnico de Mantenimiento en Subestaciones</b>.<br/><br/>"
        "Su formación les otorga la capacidad de obtener la licencia de instalador eléctrico autorizado por los entes reguladores del Estado, permitiéndoles "
        "firmar planos y ejecutar proyectos como contratistas independientes y consultores de eficiencia energética en medianas empresas.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_15_trayectoria_laboral.png"), width=480, height=165))
    story.append(Paragraph("Figura 15.1: Escala evolutiva de carrera profesional técnica: desde la operación inicial hasta la dirección de proyectos.", caption_style))
    
    story.append(Paragraph("14.2. Nichos Ocupacionales para el BTP en Construcciones Metálicas", page_h2_style))
    story.append(Paragraph(
        "En el área metalmecánica, los egresados se desempeñan como: <b>Soldador Calificado 6G (SMAW/GTAW/FCAW)</b>, <b>Armador Estructural de Naves y Puentes</b>, "
        "<b>Calderero de Tuberías y Recipientes a Presión</b>, <b>Operador de Maquinaria CNC de Corte y Plegado</b>, y <b>Asistente de Control de Calidad e Inspección END</b>. "
        "La alta demanda internacional de soldadores homologados les abre oportunidades en proyectos mineros, petroleros (Offshore) y navales.",
        body_style
    ))
    story.append(PageBreak())

    # =========================================================================
    # PÁGINA 16: Conclusiones, Perfil de Salida y Normativa Aplicable
    # =========================================================================
    story.append(Paragraph("15. CONCLUSIONES Y MARCO NORMATIVO INTERNACIONAL", page_h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#1E3A8A'), spaceAfter=8))
    
    story.append(Paragraph("15.1. Síntesis del Perfil de Salida Consolidado", page_h2_style))
    story.append(Paragraph(
        "El Bachiller Técnico Profesional en Electricidad o en Construcciones Metálicas culmina su ciclo formativo como un agente transformador de la "
        "matriz productiva. Es un profesional íntegro, meticuloso y altamente productivo que domina la ciencia aplicada a los materiales y a la energía, "
        "garantizando obras e instalaciones seguras, eficientes y perdurables. Posee las bases académicas suficientes para continuar estudios superiores de "
        "Ingeniería Eléctrica, Mecánica o Civil, o para liderar empresas de servicios electromecánicos con visión de mercado.<br/><br/>"
        "Su cualificación se rige por códigos internacionales estandarizados, lo que garantiza que sus competencias poseen validez y reconocimiento global "
        "en cualquier sector industrial de alta complejidad técnica y competitiva.",
        body_style
    ))
    
    story.append(Image(str(FIGURES_DIR / "fig_16_normativa_cierre.png"), width=480, height=165))
    story.append(Paragraph("Figura 16.1: Marco normativo internacional integrado que fundamenta la competencia del graduado técnico profesional.", caption_style))
    
    story.append(Paragraph("15.2. Catálogo de Normas Técnicas de Referencia Obligatoria", page_h2_style))
    story.append(Paragraph(
        "<b>Electricidad:</b> NFPA 70 (National Electrical Code), NFPA 70E (Electrical Safety in Workplace), IEEE Std 142 (Green Book - Puesta a Tierra), "
        "IEEE Std 80 (Substation Grounding), IEC 60947 (Aparamenta de Baja Tensión) e IEC 61131 (Controladores Lógicos Programables).<br/>"
        "<b>Construcciones Metálicas:</b> AWS D1.1/D1.1M (Structural Welding Code - Steel), AWS D1.5 (Bridge Welding Code), AISC 360 (Specification for Structural "
        "Steel Buildings), ASME Boiler and Pressure Vessel Code Section IX, ISO 9606-1 (Cualificación de Soldadores) y SSPC (The Society for Protective Coatings).",
        body_style
    ))
    
    # Construcción final del documento
    print(f"[*] Compilando PDF formal de 16 páginas en: {OUTPUT_PDF}...")
    doc.build(story, canvasmaker=NumberedCanvas)
    
    file_size_mb = OUTPUT_PDF.stat().st_size / (1024 * 1024)
    print(f"[OK] Documento PDF generado exitosamente: {OUTPUT_PDF}")
    print(f"     Tamano: {file_size_mb:.2f} MB")


def main():
    print("=" * 70)
    print("GENERADOR DEL PERFIL DEL EGRESADO BTP (ELECTRICIDAD Y CONSTR. METÁLICAS)")
    print("=" * 70)
    generate_all_figures()
    build_pdf()
    print("=" * 70)


if __name__ == "__main__":
    main()
