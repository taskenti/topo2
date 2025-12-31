"""
Módulo de generación de PDF para Topoguías de Senderismo - Diseño Moderno (Corregido)
Soluciona problemas de renderizado de texto, superposiciones y añade soporte para logos.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader, simpleSplit
import io
import qrcode
from datetime import datetime

class ModernTopoGuideGenerator:
    """
    Generador de topoguías con diseño moderno, limpio y estético.
    Versión v2: Corrección de bugs de texto y layout.
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
    
    # Fuentes Estándar
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
        """Dibuja una tarjeta blanca con sombra suave y FONDO OPACO"""
        self.c.saveState()
        # Sombra
        self.c.setFillColor(colors.Color(0, 0, 0, alpha=0.1))
        self.c.roundRect(x + 1*mm, y - 1*mm, width, height, radius, fill=1, stroke=0)
        # Tarjeta blanca (importante fill=1 para tapar lo de atrás)
        self.c.setFillColor(self.C_WHITE)
        self.c.roundRect(x, y, width, height, radius, fill=1, stroke=0)
        self.c.restoreState()

    def _draw_badge(self, x, y, text, bg_color, text_color=colors.white):
        """Dibuja una pequeña etiqueta/badge"""
        self.c.saveState()
        self.c.setFont(self.FONT_HEAD, 7)
        text_w = self.c.stringWidth(text, self.FONT_HEAD, 7) + 6*mm
        h = 6 * mm
        self._draw_rounded_rect(x, y, text_w, h, 2*mm, bg_color)
        self.c.setFillColor(text_color)
        self.c.drawCentredString(x + text_w/2, y + 1.5*mm, text)
        self.c.restoreState()

    def _draw_image_rounded(self, path, x, y, w, h, radius=3*mm):
        """Dibuja una imagen recortada"""
        if not path:
            self._draw_rounded_rect(x, y, w, h, radius, self.C_BG_LIGHT)
            self.c.setFillColor(self.C_TEXT_LIGHT)
            self.c.setFont(self.FONT_BODY, 8)
            self.c.drawCentredString(x + w/2, y + h/2, "Imagen no disponible")
            return

        try:
            self.c.saveState()
            p = self.c.beginPath()
            p.roundRect(x, y, w, h, radius)
            self.c.clipPath(p, stroke=0)
            self.c.drawImage(path, x, y, width=w, height=h, preserveAspectRatio=True, anchor='c', mask='auto')
            self.c.restoreState()
            
            # Borde sutil
            self.c.saveState()
            self.c.setStrokeColor(colors.Color(0,0,0,0.1))
            self.c.setLineWidth(0.5)
            self.c.roundRect(x, y, w, h, radius, fill=0, stroke=1)
            self.c.restoreState()
        except Exception as e:
            print(f"Error cargando imagen: {e}")
            # Fallback visual
            self._draw_rounded_rect(x, y, w, h, radius, self.C_BG_LIGHT)

    # --- PÁGINA 1 ---

    def _page1_hero(self, data, logos):
        """Cabecera con Logos, Título y Panorámica"""
        top_bar_h = 35 * mm
        
        # Fondo verde superior
        self.c.setFillColor(self.C_PRIMARY)
        self.c.rect(0, self.PAGE_HEIGHT - top_bar_h, self.PAGE_WIDTH, top_bar_h, fill=1, stroke=0)
        
        # --- LOGOS ---
        logo_size = 22 * mm
        logo_y = self.PAGE_HEIGHT - top_bar_h + (top_bar_h - logo_size)/2
        
        # Logo Izquierdo
        if logos.get('left'):
            try:
                self.c.drawImage(logos['left'], self.MARGIN, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto', anchor='w')
            except: pass
            
        # Logo Derecho
        if logos.get('right'):
            try:
                self.c.drawImage(logos['right'], self.PAGE_WIDTH - self.MARGIN - logo_size, logo_y, width=logo_size, height=logo_size, preserveAspectRatio=True, mask='auto', anchor='e')
            except: pass

        # --- TEXTOS CABECERA ---
        # Definir área segura para texto (entre logos)
        text_start_x = self.MARGIN + logo_size + 5*mm
        text_end_x = self.PAGE_WIDTH - self.MARGIN - logo_size - 5*mm
        center_x = self.PAGE_WIDTH / 2
        
        # Título Ruta
        self.c.setFillColor(self.C_WHITE)
        self.c.setFont(self.FONT_HEAD, 20)
        # Ajustamos posición vertical para que no quede tan arriba
        self.c.drawCentredString(center_x, self.PAGE_HEIGHT - 16 * mm, data.get('route_name', 'Nombre de la Ruta'))
        
        # Subtítulo (Código | Tipo)
        subtitle = f"{data.get('route_code', '')}  |  {data.get('route_type', '')}"
        self.c.setFont(self.FONT_BODY, 11)
        self.c.setFillColor(colors.Color(1, 1, 1, 0.85))
        self.c.drawCentredString(center_x, self.PAGE_HEIGHT - 24 * mm, subtitle)
        
        # --- IMAGEN PANORÁMICA ---
        img_y = self.PAGE_HEIGHT - top_bar_h - 90 * mm + 10 * mm
        img_h = 90 * mm
        img_w = self.PAGE_WIDTH - (2 * self.MARGIN)
        img_x = self.MARGIN
        
        self._draw_shadow_card(img_x, img_y, img_w, img_h)
        self._draw_image_rounded(data.get('panoramic_image'), img_x, img_y, img_w, img_h)
        
        # Etiquetas (Landmarks)
        landmarks = data.get('landmarks', [])
        if landmarks:
            self.c.saveState()
            self.c.setFont(self.FONT_HEAD, 8)
            base_y = img_y + 5 * mm
            for i, mark in enumerate(landmarks):
                txt = mark.get('text', '')
                if not txt: continue
                # Posición calculada para no solapar
                lx = img_x + 10*mm + (i * 45*mm)
                if lx + 30*mm < img_x + img_w:
                    tw = self.c.stringWidth(txt, self.FONT_HEAD, 8) + 4*mm
                    self._draw_rounded_rect(lx, base_y, tw, 5*mm, 1*mm, colors.Color(0,0,0,0.6))
                    self.c.setFillColor(self.C_WHITE)
                    self.c.drawString(lx + 2*mm, base_y + 1.5*mm, txt)
            self.c.restoreState()

    def _page1_content(self, data):
        """Texto descriptivo arreglado (sin glitch)"""
        start_y = self.PAGE_HEIGHT - 125 * mm # Bajado un poco para dar aire
        col_gap = 10 * mm
        col_width = (self.PAGE_WIDTH - (2 * self.MARGIN) - col_gap) / 2
        
        # -- COLUMNA IZQUIERDA --
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_HEAD, 14)
        self.c.drawString(self.MARGIN, start_y, "Sobre el Recorrido")
        self.c.setStrokeColor(self.C_ACCENT)
        self.c.setLineWidth(2)
        self.c.line(self.MARGIN, start_y - 2*mm, self.MARGIN + 15*mm, start_y - 2*mm)
        
        text_y = start_y - 10 * mm
        paragraphs = data.get('paragraphs', [])
        
        # Usamos simpleSplit para evitar el glitch de caracteres corruptos
        full_text_left = "\n\n".join([p for p in paragraphs[:2] if p])
        lines_left = simpleSplit(full_text_left, self.FONT_BODY, 9.5, col_width)
        
        self.c.setFont(self.FONT_BODY, 9.5)
        self.c.setFillColor(colors.Color(0.2, 0.2, 0.2))
        
        for line in lines_left:
            if text_y < 20 * mm: break
            self.c.drawString(self.MARGIN, text_y, line)
            text_y -= 4.5 * mm
            
        # -- COLUMNA DERECHA --
        x_right = self.MARGIN + col_width + col_gap
        y_right = start_y
        
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_HEAD, 14)
        self.c.drawString(x_right, y_right, "Naturaleza y Recomendaciones")
        self.c.setStrokeColor(self.C_ACCENT)
        self.c.line(x_right, y_right - 2*mm, x_right + 15*mm, y_right - 2*mm)
        
        y_right -= 10 * mm
        
        full_text_right = "\n\n".join([p for p in paragraphs[2:] if p])
        lines_right = simpleSplit(full_text_right, self.FONT_BODY, 9.5, col_width)
        
        self.c.setFont(self.FONT_BODY, 9.5)
        for line in lines_right:
            if y_right < 75 * mm: break # Dejar espacio para la caja de abajo
            self.c.drawString(x_right, y_right, line)
            y_right -= 4.5 * mm
            
        # Caja de Recomendaciones
        recs = data.get('recommendations', [])
        if recs:
            box_y_start = 20 * mm
            box_height = y_right - box_y_start - 5*mm
            
            # Fondo gris claro para diferenciar
            self._draw_rounded_rect(x_right, box_y_start, col_width, box_height, 3*mm, self.C_BG_LIGHT)
            
            curr_y = y_right - 10 * mm
            self.c.setFillColor(self.C_PRIMARY)
            self.c.setFont(self.FONT_HEAD, 10)
            self.c.drawString(x_right + 5*mm, curr_y, "⚠️ A TENER EN CUENTA")
            
            curr_y -= 6 * mm
            self.c.setFont(self.FONT_BODY, 8.5)
            self.c.setFillColor(self.C_TEXT_MAIN)
            
            for rec in recs[:5]:
                # Bullet
                self.c.setFillColor(self.C_ACCENT)
                self.c.circle(x_right + 6*mm, curr_y + 1*mm, 1*mm, fill=1, stroke=0)
                
                # Texto
                self.c.setFillColor(self.C_TEXT_MAIN)
                # Ajuste de texto para bullets
                rec_lines = simpleSplit(rec, self.FONT_BODY, 8.5, col_width - 15*mm)
                for l in rec_lines:
                    self.c.drawString(x_right + 10*mm, curr_y, l)
                    curr_y -= 4 * mm
                curr_y -= 1.5 * mm

    # --- PÁGINA 2 ---

    def _page2_layout(self, data):
        """Layout técnico corregido"""
        # Cabecera fina
        self.c.setFillColor(self.C_PRIMARY)
        self.c.rect(0, self.PAGE_HEIGHT - 12*mm, self.PAGE_WIDTH, 12*mm, fill=1, stroke=0)
        self.c.setFillColor(self.C_WHITE)
        self.c.setFont(self.FONT_HEAD, 9)
        self.c.drawRightString(self.PAGE_WIDTH - self.MARGIN, self.PAGE_HEIGHT - 8*mm, f"{data.get('route_code')} - Información Técnica")

        col_split = (self.PAGE_WIDTH * 0.64)
        
        # --- IZQUIERDA (VISUALES) ---
        map_h = 105 * mm
        map_w = col_split - self.MARGIN - 5*mm
        map_x = self.MARGIN
        map_y = self.PAGE_HEIGHT - 20*mm - map_h
        
        self._draw_shadow_card(map_x, map_y, map_w, map_h)
        self._draw_image_rounded(data.get('map_image'), map_x, map_y, map_w, map_h)
        self._draw_badge(map_x + 3*mm, map_y + map_h - 9*mm, "MAPA TOPOGRÁFICO", self.C_PRIMARY)

        # Perfil
        prof_h = 50 * mm
        prof_w = map_w
        prof_x = map_x
        prof_y = map_y - 8*mm - prof_h
        
        self._draw_shadow_card(prof_x, prof_y, prof_w, prof_h)
        self._draw_image_rounded(data.get('profile_image'), prof_x, prof_y, prof_w, prof_h)
        # Badge fuera de la gráfica para no tapar
        self._draw_badge(prof_x + 3*mm, prof_y + prof_h - 9*mm, "PERFIL DE ELEVACIÓN", self.C_ACCENT, self.C_TEXT_MAIN)

        # --- DERECHA (DATOS) - IMPORTANTE: Fondo blanco opaco ---
        data_x = col_split + 5*mm
        data_w = self.PAGE_WIDTH - data_x - self.MARGIN
        top_y = self.PAGE_HEIGHT - 20*mm
        
        # 1. Ficha Técnica
        self._draw_metric_panel(data_x, top_y, data_w, data.get('technical', {}))
        
        # 2. MIDE
        mide_y = top_y - 72*mm
        self._draw_mide_modern(data_x, mide_y, data_w, data.get('mide', {}))
        
        # 3. Contacto + QR
        contact_y = mide_y - 62*mm
        self._draw_contact_footer(data_x, contact_y, data_w, data.get('technical', {}))

    def _draw_metric_panel(self, x, y, w, data):
        h = 68 * mm
        y_start = y - h
        
        self._draw_shadow_card(x, y_start, w, h)
        
        self.c.setFillColor(self.C_PRIMARY)
        self.c.setFont(self.FONT_HEAD, 11)
        self.c.drawString(x + 5*mm, y - 8*mm, "FICHA TÉCNICA")
        self.c.setLineWidth(1)
        self.c.setStrokeColor(colors.Color(0.9, 0.9, 0.9))
        self.c.line(x + 5*mm, y - 10*mm, x + w - 5*mm, y - 10*mm)
        
        items = [
            ("🕒", "Tiempo", data.get('time', '-')),
            ("📏", "Distancia", data.get('distance', '-')),
            ("↗️", "Subida", data.get('elevation_up', '-')),
            ("↘️", "Bajada", data.get('elevation_down', '-')),
            ("🔄", "Tipo", data.get('route_type', '-'))
        ]
        
        curr_y = y - 18*mm
        for icon, label, val in items:
            # Alineación mejorada
            self.c.setFont("Helvetica", 12) # Emoji font simulación
            self.c.setFillColor(self.C_TEXT_MAIN)
            self.c.drawString(x + 5*mm, curr_y, icon)
            
            self.c.setFont(self.FONT_LIGHT, 8)
            self.c.setFillColor(self.C_TEXT_LIGHT)
            self.c.drawString(x + 16*mm, curr_y + 2*mm, label)
            
            self.c.setFont(self.FONT_HEAD, 10)
            self.c.setFillColor(self.C_TEXT_MAIN)
            # Alinear valores a la derecha para orden
            self.c.drawRightString(x + w - 5*mm, curr_y, str(val))
            
            self.c.line(x + 5*mm, curr_y - 3*mm, x + w - 5*mm, curr_y - 3*mm)
            curr_y -= 10.5*mm

    def _draw_mide_modern(self, x, y, w, mide_data):
        h = 58 * mm
        y_start = y - h
        
        self._draw_shadow_card(x, y_start, w, h)
        
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_HEAD, 11)
        self.c.drawString(x + 5*mm, y - 8*mm, "VALORACIÓN MIDE")
        
        mide_items = [
            ('Severidad Medio', mide_data.get('severity', 1)),
            ('Orientación', mide_data.get('orientation', 1)),
            ('Dificultad Desp.', mide_data.get('difficulty', 1)),
            ('Esfuerzo Físico', mide_data.get('effort', 1))
        ]
        
        box_w = (w - 15*mm) / 2
        box_h = 16 * mm
        
        positions = [
            (x + 5*mm, y - 22*mm),
            (x + 5*mm + box_w + 5*mm, y - 22*mm),
            (x + 5*mm, y - 22*mm - 20*mm),
            (x + 5*mm + box_w + 5*mm, y - 22*mm - 20*mm)
        ]
        
        for i, (label, val) in enumerate(mide_items):
            px, py = positions[i]
            
            if val <= 2: badge_color = self.C_PRIMARY
            elif val == 3: badge_color = self.C_ACCENT
            else: badge_color = colors.HexColor("#C0392B")
            
            # Caja gris de fondo
            self._draw_rounded_rect(px, py - box_h, box_w, box_h, 2*mm, colors.Color(0.96, 0.96, 0.96))
            
            # Círculo valor
            r = 5*mm
            self.c.setFillColor(badge_color)
            self.c.circle(px + r + 2*mm, py - box_h/2, r, fill=1, stroke=0)
            self.c.setFillColor(self.C_WHITE)
            self.c.setFont(self.FONT_HEAD, 10)
            self.c.drawCentredString(px + r + 2*mm, py - box_h/2 - 1.2*mm, str(val))
            
            # Texto
            self.c.setFillColor(self.C_TEXT_MAIN)
            self.c.setFont(self.FONT_BODY, 7) # Fuente más pequeña para que quepa
            
            # Ajuste vertical del texto
            lines = simpleSplit(label, self.FONT_BODY, 7, box_w - (r*2) - 5*mm)
            ly = py - box_h/2 + 1.5*mm
            if len(lines) > 1: ly += 2*mm
            
            for line in lines:
                self.c.drawString(px + (r*2) + 4*mm, ly, line)
                ly -= 3*mm

    def _draw_contact_footer(self, x, y, w, data):
        """Pie de página con QR destacado y sin cortar texto"""
        h = 40 * mm
        y_start = y - h
        
        # --- QR CODE ---
        qr_size = 26 * mm
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
                
                # Fondo blanco QR
                qr_x = x + w - qr_size - 5*mm
                qr_y = y_start + 6*mm
                self._draw_rounded_rect(qr_x, qr_y, qr_size, qr_size, 2*mm, self.C_WHITE, stroke=True)
                self.c.drawImage(ImageReader(qr_bytes), qr_x, qr_y, width=qr_size, height=qr_size)
                
                self.c.setFont(self.FONT_BODY, 6)
                self.c.drawCentredString(qr_x + qr_size/2, qr_y - 2.5*mm, "Escanea para más info")
            except: pass
        
        # --- TEXTOS ---
        text_w = w - qr_size - 10*mm
        curr_y = y - 6*mm
        
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_HEAD, 10)
        # Texto corregido para que no se corte
        self.c.drawString(x + 2*mm, curr_y, "EMERGENCIAS Y CONTACTO")
        
        curr_y -= 8*mm
        
        # 112 Grande
        self.c.setFillColor(colors.HexColor("#C0392B"))
        self.c.setFont(self.FONT_HEAD, 18)
        self.c.drawString(x + 2*mm, curr_y, "SOS 112")
        
        # Teléfono parque
        curr_y -= 10*mm
        self.c.setFillColor(self.C_TEXT_MAIN)
        self.c.setFont(self.FONT_BODY, 8)
        self.c.drawString(x + 2*mm, curr_y, "Info Parque / Natural:")
        self.c.setFont(self.FONT_HEAD, 10)
        self.c.drawString(x + 2*mm, curr_y - 4.5*mm, data.get('phone', '-'))

    def generate(self, page1_data, page2_data, logos=None):
        if logos is None: logos = {}
        
        # PAGINA 1
        self._page1_hero(page1_data, logos)
        self._page1_content(page1_data)
        
        self.c.setFont(self.FONT_LIGHT, 8)
        self.c.setFillColor(self.C_TEXT_LIGHT)
        self.c.drawCentredString(self.PAGE_WIDTH/2, 8*mm, f"Generado el {datetime.now().strftime('%d/%m/%Y')} | Pág. 1")
        self.c.showPage()
        
        # PAGINA 2
        self._page2_layout(page2_data)
        
        self.c.setFont(self.FONT_LIGHT, 8)
        self.c.setFillColor(self.C_TEXT_LIGHT)
        self.c.drawCentredString(self.PAGE_WIDTH/2, 8*mm, f"Topoguía Senderismo | Pág. 2")
        self.c.save()

# --- INTERFAZ COMPATIBLE ---

def create_topoguide_pdf(output_path, data, logo_left=None, logo_right=None):
    generator = ModernTopoGuideGenerator(output_path)
    
    # Preparar logos
    logos = {
        'left': logo_left,
        'right': logo_right
    }
    
    page1_data = {
        'route_code': data.get('route_code', ''),
        'route_name': data.get('route_name', ''),
        'route_type': data.get('route_type', ''),
        'panoramic_image': data.get('panoramic_image'),
        'landmarks': data.get('landmarks', []),
        'paragraphs': data.get('paragraphs', []),
        'recommendations': data.get('recommendations', [])
    }
    
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
    
    generator.generate(page1_data, page2_data, logos)
    return output_path
