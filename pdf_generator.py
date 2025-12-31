"""
Módulo de generación de PDF para Topoguías de Senderismo - Diseño Moderno
Reescritura completa para mejorar la estética y legibilidad.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics import renderPDF
import io
import qrcode
from datetime import datetime

class ModernTopoGuideGenerator:
    """
    Generador de topoguías con diseño moderno, limpio y estético.
    Utiliza principios de diseño editorial (grid, jerarquía, espacio en blanco).
    """
    
    # Configuración de página
    PAGE_WIDTH, PAGE_HEIGHT = landscape(A4)
    MARGIN = 15 * mm
    
    # Paleta de Colores Moderna (Nature Theme)
    C_PRIMARY = colors.HexColor("#1B4D3E")    # Verde Bosque Profundo
    C_ACCENT = colors.HexColor("#D4A017")     # Oro Viejo / Ocre
    C_TEXT_MAIN = colors.HexColor("#2C3E50")  # Gris Azulado Oscuro
    C_TEXT_LIGHT = colors.HexColor("#7F8C8D") # Gris Medio
    C_BG_LIGHT = colors.HexColor("#F8F9FA")   # Blanco Roto
    C_WHITE = colors.white
    
    # Fuentes (Standard Type 1 para asegurar compatibilidad)
    FONT_HEAD = "Helvetica-Bold"
    FONT_BODY = "Helvetica"
    FONT_LIGHT = "Helvetica-Oblique"

    def __init__(self, output_path):
        self.output_path = output_path
        self.c = canvas.Canvas(output_path, pagesize=landscape(A4))
        self.c.setTitle("Topoguía de Senderismo")

    def _draw_rounded_rect(self, x, y, width, height, radius, color, fill=True, stroke=False):
        """Dibuja un rectángulo con esquinas redondeadas"""
        self.c.saveState()
        if fill:
            self.c.setFillColor(color)
        if stroke:
            self.c.setStrokeColor(color)
        self.c.roundRect(x, y, width, height, radius, fill=1 if fill else 0, stroke=1 if stroke else 0)
        self.c.restoreState()

    def _draw_shadow_card(self, x, y, width, height, radius=3*mm):
        """Dibuja una sombra suave para simular elevación (efecto tarjeta)"""
        self.c.saveState()
        self.c.setFillColor(colors.Color(0, 0, 0, alpha=0.05))
        # Sombra desplazada
        self.c.roundRect(x + 1*mm, y - 1*mm, width, height, radius, fill=1, stroke=0)
        self.c.restoreState()
        # Tarjeta blanca encima
        self._draw_rounded_rect(x, y, width, height, radius, self.C_WHITE)

    def _draw_badge(self, x, y, text, bg_color, text_color=colors.white):
        """Dibuja una pequeña etiqueta/badge"""
        self.c.saveState()
        w = 20 * mm  # Ancho estimado
        h = 6 * mm
        self._draw_rounded_rect(x, y, w, h, 2*mm, bg_color)
        self.c.setFillColor(text_color)
        self.c.setFont(self.FONT_HEAD, 7)
        self.c.drawCentredString(x + w/2, y + 1.5*mm, text)
        self.c.restoreState()

    def _draw_image_rounded(self, path, x, y, w, h, radius=3*mm):
        """Dibuja una imagen recortada con esquinas redondeadas"""
        if not path:
            # Placeholder si no hay imagen
            self._draw_rounded_rect(x, y, w, h, radius, self.C_BG_LIGHT)
            self.c.setFillColor(self.C_TEXT_LIGHT)
            self.c.drawCentredString(x + w/2, y + h/2, "Sin Imagen Disponible")
            return

        try:
            # Crear un path de recorte
            self.c.saveState()
            p = self.c.beginPath()
            p.roundRect(x, y, w, h, radius)
            self.c.clipPath(p, stroke=0)
            
            # Dibujar imagen
            self.c.drawImage(path, x, y, width=w, height=h, preserveAspectRatio=True, anchor='c', mask='auto')
            self.c.restoreState()
            
            # Borde sutil interno para definir límites si la imagen es clara
            self.c.saveState()
            self.c.setStrokeColor(colors.Color(0,0,0,0.1))
            self.c.setLineWidth(0.5)
            self.c.roundRect(x, y, w, h, radius, fill=0, stroke=1)
            self.c.restoreState()
        except Exception as e:
            print(f"Error drawing image: {e}")

    # --- ELEMENTOS DE PÁGINA 1 ---

    def _page1_hero(self, data):
        """Sección superior con Título y Panorámica"""
        # Fondo decorativo superior
        top_bar_h = 35 * mm
        self.c.setFillColor(self.C_PRIMARY)
        self.c.rect(0, self.PAGE_HEIGHT - top_bar_h, self.PAGE_WIDTH, top_bar_h, fill=1, stroke=0)
        
        # Título Ruta (Blanco sobre verde)
        self.c.setFillColor(self.C_WHITE)
        self.c.setFont(self.FONT_HEAD, 24)
        self.c.drawString(self.MARGIN, self.PAGE_HEIGHT - 18 * mm, data.get('route_name', 'Nombre de la Ruta'))
        
        # Código Ruta y Tipo (Subtítulo)
        subtitle = f"{data.get('route_code', '')}  |  {data.get('route_type', '')}"
        self.c.setFont(self.FONT_BODY, 12)
        self.c.setFillColor(colors.Color(1, 1, 1, 0.8)) # Blanco con transparencia
        self.c.drawString(self.MARGIN, self.PAGE_HEIGHT - 26 * mm, subtitle)
        
        # Imagen Panorámica (Tarjeta grande flotante)
        img_y = self.PAGE_HEIGHT - top_bar_h - 90 * mm + 10 * mm # superpuesta un poco
        img_h = 90 * mm
        img_w = self.PAGE_WIDTH - (2 * self.MARGIN)
        img_x = self.MARGIN
        
        self._draw_shadow_card(img_x, img_y, img_w, img_h)
        self._draw_image_rounded(data.get('panoramic_image'), img_x, img_y, img_w, img_h)
        
        # Etiquetas de paisaje (Landmarks)
        landmarks = data.get('landmarks', [])
        if landmarks:
            self.c.saveState()
            self.c.setFont(self.FONT_HEAD, 8)
            self.c.setFillColor(self.C_WHITE)
            # Dibujamos las etiquetas en la parte inferior de la imagen
            # Esto es una aproximación visual ya que no tenemos coordenadas reales en la imagen
            base_y = img_y + 5 * mm
            for i, mark in enumerate(landmarks):
                # Distribuir etiquetas
                lx = img_x + 10*mm + (i * 40*mm) 
                if lx < img_x + img_w:
                    # Fondo semitransparente para el texto
                    txt = mark.get('text', '')
                    tw = self.c.stringWidth(txt, self.FONT_HEAD, 8) + 4*mm
                    self._draw_rounded_rect(lx, base_y, tw, 5*mm, 1*mm, colors.Color(0,0,0,0.6))
                    self.c.drawString(lx + 2*mm, base_y + 1.5*mm, txt)
            self.c.restoreState()

    def _page1_content(self, data):
        """Contenido descriptivo en columnas"""
        start_y = self.PAGE_HEIGHT - 130 * mm
        col_gap = 10 * mm
        col_width = (self.PAGE_WIDTH - (2 * self.MARGIN) - col_gap) / 2
        
        # -- Columna Izquierda: Descripción --
        self.c.setFillColor(self.C_TEXT_MAIN)
        
        # Título sección
        self.c.setFont(self.FONT_HEAD, 14)
        self.c.drawString(self.MARGIN, start_y, "Sobre el Recorrido")
        
        # Línea decorativa
        self.c.setStrokeColor(self.C_ACCENT)
        self.c.setLineWidth(2)
        self.c.line(self.MARGIN, start_y - 2*mm, self.MARGIN + 15*mm, start_y - 2*mm)
        
        # Texto párrafos
        text_y = start_y - 10 * mm
        paragraphs = data.get('paragraphs', [])
        self.c.setFont(self.FONT_BODY, 9.5)
        self.c.setFillColor(colors.Color(0.2, 0.2, 0.2))
        
        # Unir párrafos 1 y 2 para la izquierda
        full_text_left = "\n\n".join([p for p in paragraphs[:2] if p])
        lines_left = self._wrap_text(full_text_left, col_width, 9.5)
        
        for line in lines_left:
            if text_y < 20 * mm: break # Margen inferior
            self.c.drawString(self.MARGIN, text_y, line)
            text_y -= 4.5 * mm
            
        # Unir párrafos 3 y 4 para continuar si hay espacio, o ponerlos si es breve
        # Para simplificar el diseño moderno, usamos la columna derecha para recomendaciones e info extra
        
        # -- Columna Derecha: Naturaleza y Consejos --
        x_right = self.MARGIN + col_width + col_gap
        y_right = start_y
        
        # Título sección derecha
        self.c.setFont(self.FONT_HEAD, 14)
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.drawString(x_right, y_right, "Naturaleza y Recomendaciones")
        self.c.setStrokeColor(self.C_ACCENT)
        self.c.line(x_right, y_right - 2*mm, x_right + 15*mm, y_right - 2*mm)
        
        y_right -= 10 * mm
        
        # Texto de naturaleza (Párrafos 3 y 4)
        full_text_right = "\n\n".join([p for p in paragraphs[2:] if p])
        lines_right = self._wrap_text(full_text_right, col_width, 9.5)
        
        self.c.setFont(self.FONT_BODY, 9.5)
        for line in lines_right:
            if y_right < 65 * mm: break 
            self.c.drawString(x_right, y_right, line)
            y_right -= 4.5 * mm
            
        # Bloque de Recomendaciones (Estilo caja destacada)
        rec_box_y = y_right - 5 * mm
        recs = data.get('recommendations', [])
        
        if recs:
            box_h = 45 * mm # Altura fija para la caja
            box_y_start = 20 * mm # Margen inferior página
            
            # Fondo suave
            self._draw_rounded_rect(x_right, box_y_start, col_width, y_right - box_y_start - 5*mm, 3*mm, self.C_BG_LIGHT)
            
            curr_y = y_right - 10 * mm
            self.c.setFillColor(self.C_PRIMARY)
            self.c.setFont(self.FONT_HEAD, 10)
            self.c.drawString(x_right + 5*mm, curr_y, "⚠️ A TENER EN CUENTA")
            
            curr_y -= 6 * mm
            self.c.setFont(self.FONT_BODY, 8.5)
            self.c.setFillColor(self.C_TEXT_MAIN)
            
            for rec in recs[:5]: # Max 5 recomendaciones
                # Bullet point personalizado
                self.c.setFillColor(self.C_ACCENT)
                self.c.circle(x_right + 6*mm, curr_y + 1*mm, 1*mm, fill=1, stroke=0)
                
                # Texto
                self.c.setFillColor(self.C_TEXT_MAIN)
                rec_lines = self._wrap_text(rec, col_width - 15*mm, 8.5)
                for l in rec_lines:
                    self.c.drawString(x_right + 10*mm, curr_y, l)
                    curr_y -= 4 * mm
                curr_y -= 1 * mm # Extra espacio entre items

    # --- ELEMENTOS DE PÁGINA 2 ---

    def _page2_layout(self, data):
        """Layout de la página técnica"""
        # Cabecera Simple Página 2
        self.c.setFillColor(self.C_PRIMARY)
        self.c.rect(0, self.PAGE_HEIGHT - 15*mm, self.PAGE_WIDTH, 15*mm, fill=1, stroke=0)
        self.c.setFillColor(self.C_WHITE)
        self.c.setFont(self.FONT_HEAD, 10)
        self.c.drawRightString(self.PAGE_WIDTH - self.MARGIN, self.PAGE_HEIGHT - 10*mm, f"{data.get('route_code')} - Información Técnica")

        # Grid principal: 2/3 Mapa y Perfil (Izq), 1/3 Datos (Der)
        col_split = (self.PAGE_WIDTH * 0.66)
        
        # --- COLUMNA IZQUIERDA: VISUALES ---
        
        # 1. Mapa Topográfico
        map_h = 110 * mm
        map_w = col_split - self.MARGIN - 5*mm
        map_x = self.MARGIN
        map_y = self.PAGE_HEIGHT - 20*mm - map_h
        
        self._draw_shadow_card(map_x, map_y, map_w, map_h)
        self._draw_image_rounded(data.get('map_image'), map_x, map_y, map_w, map_h)
        # Etiqueta sobre el mapa
        self._draw_badge(map_x + 5*mm, map_y + map_h - 10*mm, "MAPA TOPOGRÁFICO", self.C_PRIMARY)

        # 2. Perfil de Elevación
        prof_h = 50 * mm
        prof_w = map_w
        prof_x = map_x
        prof_y = map_y - 10*mm - prof_h
        
        self._draw_shadow_card(prof_x, prof_y, prof_w, prof_h)
        self._draw_image_rounded(data.get('profile_image'), prof_x, prof_y, prof_w, prof_h)
        self._draw_badge(prof_x + 5*mm, prof_y + prof_h - 10*mm, "PERFIL DE ELEVACIÓN", self.C_ACCENT, self.C_TEXT_MAIN)

        # --- COLUMNA DERECHA: DATOS ---
        
        data_x = col_split + 5*mm
        data_w = self.PAGE_WIDTH - data_x - self.MARGIN
        top_y = self.PAGE_HEIGHT - 20*mm
        
        # 1. Panel de Ficha Técnica (Resumen Métrico)
        self._draw_metric_panel(data_x, top_y, data_w, data.get('technical', {}))
        
        # 2. Panel MIDE
        mide_y = top_y - 75*mm
        self._draw_mide_modern(data_x, mide_y, data_w, data.get('mide', {}))
        
        # 3. Panel Contacto y QR
        contact_y = mide_y - 65*mm
        self._draw_contact_footer(data_x, contact_y, data_w, data.get('technical', {}))

    def _draw_metric_panel(self, x, y, w, data):
        """Dibuja el panel de métricas con iconos simulados"""
        h = 70 * mm
        y_start = y - h
        
        self._draw_shadow_card(x, y_start, w, h)
        
        # Título
        self.c.setFillColor(self.C_PRIMARY)
        self.c.setFont(self.FONT_HEAD, 12)
        self.c.drawString(x + 5*mm, y - 10*mm, "FICHA TÉCNICA")
        self.c.setLineWidth(1)
        self.c.line(x + 5*mm, y - 12*mm, x + w - 5*mm, y - 12*mm)
        
        # Items
        items = [
            ("🕒", "Tiempo Estimado", data.get('time', '-')),
            ("📏", "Distancia Total", data.get('distance', '-')),
            ("↗️", "Desnivel Subida", data.get('elevation_up', '-')),
            ("↘️", "Desnivel Bajada", data.get('elevation_down', '-')),
            ("🔄", "Tipo de Ruta", data.get('route_type', '-'))
        ]
        
        curr_y = y - 22*mm
        for icon, label, val in items:
            # Icono (simulado con texto emoji o carácter)
            self.c.setFont("Helvetica", 14)
            self.c.setFillColor(self.C_TEXT_MAIN)
            self.c.drawString(x + 5*mm, curr_y, icon)
            
            # Label
            self.c.setFont(self.FONT_LIGHT, 8)
            self.c.setFillColor(self.C_TEXT_LIGHT)
            self.c.drawString(x + 18*mm, curr_y + 3*mm, label)
            
            # Valor
            self.c.setFont(self.FONT_HEAD, 11)
            self.c.setFillColor(self.C_TEXT_MAIN)
            self.c.drawString(x + 18*mm, curr_y - 1*mm, str(val))
            
            # Separador fino
            self.c.setStrokeColor(colors.Color(0.9, 0.9, 0.9))
            self.c.line(x + 5*mm, curr_y - 4*mm, x + w - 5*mm, curr_y - 4*mm)
            
            curr_y -= 11*mm

    def _draw_mide_modern(self, x, y, w, mide_data):
        """Visualización moderna del MIDE con barras de colores"""
        h = 60 * mm
        y_start = y - h
        
        self._draw_shadow_card(x, y_start, w, h)
        
        # Cabecera MIDE
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_HEAD, 12)
        self.c.drawString(x + 5*mm, y - 10*mm, "VALORACIÓN MIDE")
        self.c.setFont(self.FONT_BODY, 7)
        self.c.setFillColor(self.C_TEXT_LIGHT)
        self.c.drawRightString(x + w - 5*mm, y - 10*mm, "Escala 1 (Bajo) a 5 (Alto)")
        
        # Grid 2x2 de indicadores
        mide_items = [
            ('Severidad del Medio', mide_data.get('severity', 1)),
            ('Orientación', mide_data.get('orientation', 1)),
            ('Dificultad Desplaz.', mide_data.get('difficulty', 1)),
            ('Esfuerzo Físico', mide_data.get('effort', 1))
        ]
        
        box_w = (w - 15*mm) / 2
        box_h = 18 * mm
        
        # Posiciones relativas para 2x2
        positions = [
            (x + 5*mm, y - 25*mm),           # Top Left
            (x + 5*mm + box_w + 5*mm, y - 25*mm), # Top Right
            (x + 5*mm, y - 25*mm - 20*mm),   # Bot Left
            (x + 5*mm + box_w + 5*mm, y - 25*mm - 20*mm) # Bot Right
        ]
        
        for i, (label, val) in enumerate(mide_items):
            px, py = positions[i]
            
            # Color lógico (1-2 Verde, 3 Amarillo, 4-5 Rojo)
            if val <= 2: 
                badge_color = self.C_PRIMARY
            elif val == 3: 
                badge_color = self.C_ACCENT
            else: 
                badge_color = colors.HexColor("#C0392B") # Rojo alerta
                
            # Caja de fondo del item
            self._draw_rounded_rect(px, py - box_h, box_w, box_h, 2*mm, colors.Color(0.97, 0.97, 0.97))
            
            # Círculo con el valor
            circle_r = 6*mm
            self.c.setFillColor(badge_color)
            self.c.circle(px + circle_r + 2*mm, py - box_h/2, circle_r, fill=1, stroke=0)
            
            self.c.setFillColor(self.C_WHITE)
            self.c.setFont(self.FONT_HEAD, 12)
            self.c.drawCentredString(px + circle_r + 2*mm, py - box_h/2 - 1.5*mm, str(val))
            
            # Label
            self.c.setFillColor(self.C_TEXT_MAIN)
            self.c.setFont(self.FONT_BODY, 8)
            lines = self._wrap_text(label, box_w - (circle_r*2) - 6*mm, 8)
            ly = py - box_h/2 + 2*mm
            if len(lines) > 1: ly += 2*mm
            
            for line in lines:
                self.c.drawString(px + (circle_r*2) + 5*mm, ly, line)
                ly -= 3.5*mm

    def _draw_contact_footer(self, x, y, w, data):
        """Pie de página técnico con QR y teléfonos"""
        h = 40 * mm # Altura restante aproximada
        y_start = y - h
        
        # No dibujamos tarjeta completa, solo elementos limpios
        
        # QR Code
        qr_size = 28 * mm
        web_url = data.get('web', '')
        if web_url:
            try:
                qr = qrcode.QRCode(box_size=2, border=1)
                qr.add_data(web_url)
                qr.make(fit=True)
                qr_img = qr.make_image(fill_color="black", back_color="white")
                
                qr_bytes = io.BytesIO()
                qr_img.save(qr_bytes, format='PNG')
                qr_bytes.seek(0)
                
                # Dibujar fondo blanco para QR
                self._draw_rounded_rect(x + w - qr_size - 5*mm, y_start + 5*mm, qr_size, qr_size, 2*mm, self.C_WHITE)
                self.c.drawImage(ImageReader(qr_bytes), x + w - qr_size - 5*mm, y_start + 5*mm, width=qr_size, height=qr_size)
                
                # Texto "Escanear"
                self.c.setFont(self.FONT_BODY, 6)
                self.c.drawCentredString(x + w - qr_size/2 - 5*mm, y_start + 2*mm, "Info Digital")
                
            except Exception:
                pass
        
        # Textos de contacto
        text_w = w - qr_size - 10*mm
        curr_y = y - 10*mm
        
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_HEAD, 10)
        self.c.drawString(x + 5*mm, curr_y, "CONTACTO Y EMERGENCIAS")
        
        curr_y -= 8*mm
        
        # Emergencias
        self.c.setFillColor(colors.HexColor("#C0392B")) # Rojo
        self.c.setFont(self.FONT_HEAD, 14)
        self.c.drawString(x + 5*mm, curr_y, f"SOS 112")
        if data.get('emergency') and data.get('emergency') != '112':
             self.c.drawString(x + 35*mm, curr_y, f"/ {data.get('emergency')}")
             
        curr_y -= 8*mm
        # Parque
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_BODY, 9)
        self.c.drawString(x + 5*mm, curr_y, "Info Parque / Espacio Natural:")
        self.c.setFont(self.FONT_HEAD, 10)
        self.c.drawString(x + 5*mm, curr_y - 5*mm, data.get('phone', '-'))


    def _wrap_text(self, text, max_width_mm, font_size):
        """Utilidad simple para ajustar texto"""
        if not text: return []
        c = self.c
        lines = []
        words = text.split()
        curr_line = []
        
        # Conversión mm a puntos aprox (1mm = 2.83pt)
        max_pts = max_width_mm * 2.83
        
        for word in words:
            curr_line.append(word)
            w = c.stringWidth(' '.join(curr_line), self.FONT_BODY, font_size)
            if w > max_pts:
                curr_line.pop()
                if curr_line:
                    lines.append(' '.join(curr_line))
                curr_line = [word]
        
        if curr_line:
            lines.append(' '.join(curr_line))
        return lines

    def generate(self, page1_data, page2_data):
        # --- PÁGINA 1 ---
        self._page1_hero(page1_data)
        self._page1_content(page1_data)
        
        # Pie de página 1
        self.c.setFont(self.FONT_LIGHT, 8)
        self.c.setFillColor(self.C_TEXT_LIGHT)
        self.c.drawCentredString(self.PAGE_WIDTH/2, 10*mm, f"Generado el {datetime.now().strftime('%d/%m/%Y')} | Pág. 1")
        self.c.showPage()
        
        # --- PÁGINA 2 ---
        self._page2_layout(page2_data)
        
        # Pie de página 2
        self.c.setFont(self.FONT_LIGHT, 8)
        self.c.setFillColor(self.C_TEXT_LIGHT)
        self.c.drawCentredString(self.PAGE_WIDTH/2, 10*mm, f"Topoguía Generada Automáticamente | Pág. 2")
        self.c.save()


# --- FUNCIÓN INTERFAZ COMPATIBLE CON APP.PY ---

def create_topoguide_pdf(output_path, data, logo_left=None, logo_right=None):
    """
    Interfaz compatible con la llamada existente en app.py.
    Mapea los datos del diccionario plano a la estructura moderna.
    """
    generator = ModernTopoGuideGenerator(output_path)
    
    # Preparamos los datos tal cual vienen de app.py
    # app.py pasa un diccionario 'flat' (plano) en algunos casos y anidado en otros.
    # Aquí unificamos la estructura para el generador.
    
    # Datos combinados para Página 1 (Inspiracional)
    page1_data = {
        'route_code': data.get('route_code', ''),
        'route_name': data.get('route_name', ''),
        'route_type': data.get('route_type', ''),
        'panoramic_image': data.get('panoramic_image'),
        'landmarks': data.get('landmarks', []),
        'paragraphs': data.get('paragraphs', []),
        'recommendations': data.get('recommendations', [])
    }
    
    # Datos combinados para Página 2 (Técnica)
    # Extraemos MIDE con seguridad
    mide_raw = data.get('mide', {})
    
    page2_data = {
        'route_code': data.get('route_code', ''),
        'map_image': data.get('map_image'),
        'profile_image': data.get('profile_image'),
        'technical': {
            'time': data.get('time', ''),
            'distance': data.get('distance', ''),
            'elevation_up': data.get('elevation_up', ''),
            'elevation_down': data.get('elevation_down', ''),
            'route_type': data.get('route_type', ''),
            'emergency': data.get('emergency', '112'),
            'phone': data.get('phone', ''),
            'web': data.get('web', '')
        },
        'mide': {
            'severity': mide_raw.get('severity', 1),
            'orientation': mide_raw.get('orientation', 1),
            'difficulty': mide_raw.get('difficulty', 1),
            'effort': mide_raw.get('effort', 1)
        }
    }
    
    generator.generate(page1_data, page2_data)
    return output_path
