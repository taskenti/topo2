"""
Módulo de generación de PDF para Topoguías de Senderismo
Replica exactamente el diseño oficial de Castilla-La Mancha
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
import io
import qrcode
from datetime import datetime


class TopoGuidePDFGenerator:
    """Generador de topoguías que replica el diseño oficial"""
    
    # Modo landscape
    PAGE_WIDTH = landscape(A4)[0]
    PAGE_HEIGHT = landscape(A4)[1]
    
    # Colores exactos del diseño original
    GREEN_HEADER = colors.HexColor("#006838")
    GREEN_DARK = colors.HexColor("#004d29")
    YELLOW_ACCENT = colors.HexColor("#FDB913")
    GRAY_BG = colors.HexColor("#F5F5F5")
    TEXT_DARK = colors.HexColor("#333333")
    WHITE = colors.white
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.c = canvas.Canvas(output_path, pagesize=landscape(A4))
    
    def _draw_page1_header(self, route_code, route_name):
        """Cabecera página 1 - Franja verde con código y nombre"""
        # Franja verde superior (más estrecha)
        self.c.setFillColor(self.GREEN_HEADER)
        self.c.rect(0, self.PAGE_HEIGHT - 25*mm, self.PAGE_WIDTH, 25*mm, fill=1, stroke=0)
        
        # Código de ruta (PR-GU 08) - Grande y centrado
        self.c.setFillColor(self.WHITE)
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawCentredString(self.PAGE_WIDTH/2, self.PAGE_HEIGHT - 13*mm, route_code)
        
        # Nombre del sendero - Más pequeño debajo
        self.c.setFont("Helvetica", 13)
        self.c.drawCentredString(self.PAGE_WIDTH/2, self.PAGE_HEIGHT - 20*mm, route_name)
    
    def _draw_page1_panoramic(self, panoramic_path):
        """Imagen panorámica grande ocupando el ancho completo"""
        if not panoramic_path:
            return
        
        try:
            # Área para la imagen: casi todo el ancho, altura generosa
            img_x = 10*mm
            img_y = self.PAGE_HEIGHT - 25*mm - 70*mm  # Justo debajo del header
            img_width = self.PAGE_WIDTH - 20*mm
            img_height = 70*mm
            
            self.c.drawImage(
                panoramic_path,
                img_x, img_y,
                width=img_width,
                height=img_height,
                preserveAspectRatio=True,
                anchor='c',
                mask='auto'
            )
            
            # Etiqueta vertical "MIRADOR" en el borde izquierdo
            self.c.saveState()
            self.c.setFillColor(self.GREEN_DARK)
            self.c.setFont("Helvetica-Bold", 11)
            self.c.translate(3*mm, img_y + img_height/2)
            self.c.rotate(90)
            self.c.drawCentredString(0, 0, "MIRADOR")
            self.c.restoreState()
            
        except Exception as e:
            print(f"Error cargando panorámica: {e}")
    
    def _draw_page1_text_columns(self, paragraphs, recommendations):
        """Dos columnas: texto descriptivo (izq) y recomendaciones (der)"""
        # COLUMNA IZQUIERDA: Texto descriptivo (65% del ancho)
        text_x = 12*mm
        text_y = self.PAGE_HEIGHT - 100*mm
        text_width = (self.PAGE_WIDTH - 30*mm) * 0.63
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 9)
        
        y_pos = text_y
        for para in paragraphs[:4]:  # Máximo 4 párrafos
            lines = self._wrap_text(para, text_width, 9)
            for line in lines[:4]:  # Máximo 4 líneas por párrafo
                if y_pos > 20*mm:
                    self.c.drawString(text_x, y_pos, line)
                    y_pos -= 3.5*mm
            y_pos -= 2*mm  # Espacio entre párrafos
        
        # COLUMNA DERECHA: Recuadro de recomendaciones
        rec_x = self.PAGE_WIDTH - 95*mm
        rec_y = text_y + 10*mm
        rec_width = 85*mm
        rec_height = 95*mm
        
        # Fondo blanco con borde verde
        self.c.setFillColor(self.WHITE)
        self.c.setStrokeColor(self.GREEN_HEADER)
        self.c.setLineWidth(2)
        self.c.rect(rec_x, rec_y - rec_height, rec_width, rec_height, fill=1, stroke=1)
        
        # Título "RECOMENDACIONES"
        self.c.setFillColor(self.GREEN_HEADER)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(rec_x + 5*mm, rec_y - 8*mm, "RECOMENDACIONES")
        
        # Lista de recomendaciones con bullets
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 8)
        y_rec = rec_y - 16*mm
        
        for rec in recommendations[:6]:
            # Bullet amarillo
            self.c.setFillColor(self.YELLOW_ACCENT)
            self.c.circle(rec_x + 5*mm, y_rec + 1*mm, 1.5*mm, fill=1, stroke=0)
            
            # Texto de la recomendación
            self.c.setFillColor(self.TEXT_DARK)
            lines = self._wrap_text(rec, rec_width - 15*mm, 8)
            for line in lines[:3]:
                self.c.drawString(rec_x + 10*mm, y_rec, line)
                y_rec -= 3.5*mm
            y_rec -= 2*mm
    
    def _draw_page1_footer(self, date_str):
        """Pie de página 1"""
        self.c.setStrokeColor(self.GREEN_HEADER)
        self.c.setLineWidth(0.5)
        self.c.line(10*mm, 12*mm, self.PAGE_WIDTH - 10*mm, 12*mm)
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 8)
        self.c.drawString(10*mm, 8*mm, "Topoguía de Senderismo - 1/2")
        
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawCentredString(self.PAGE_WIDTH/2, 8*mm, "Castilla-La Mancha")
        
        self.c.setFont("Helvetica", 8)
        self.c.drawRightString(self.PAGE_WIDTH - 10*mm, 8*mm, date_str)
    
    def _draw_page2_header(self):
        """Cabecera página 2 - Franja verde más delgada"""
        self.c.setFillColor(self.GREEN_HEADER)
        self.c.rect(0, self.PAGE_HEIGHT - 18*mm, self.PAGE_WIDTH, 18*mm, fill=1, stroke=0)
        
        self.c.setFillColor(self.WHITE)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawCentredString(self.PAGE_WIDTH/2, self.PAGE_HEIGHT - 12*mm, "MAPA Y PERFIL")
    
    def _draw_page2_map(self, map_path):
        """Mapa topográfico grande (lado izquierdo)"""
        if not map_path:
            return
        
        try:
            map_x = 12*mm
            map_y = self.PAGE_HEIGHT - 23*mm - 100*mm
            map_width = (self.PAGE_WIDTH - 30*mm) * 0.58
            map_height = 100*mm
            
            self.c.drawImage(
                map_path,
                map_x, map_y,
                width=map_width,
                height=map_height,
                preserveAspectRatio=True,
                anchor='c',
                mask='auto'
            )
            
            # Borde verde fino
            self.c.setStrokeColor(self.GREEN_HEADER)
            self.c.setLineWidth(1)
            self.c.rect(map_x, map_y, map_width, map_height, fill=0, stroke=1)
            
        except Exception as e:
            print(f"Error cargando mapa: {e}")
    
    def _draw_page2_profile(self, profile_path):
        """Perfil de elevación (debajo del mapa)"""
        if not profile_path:
            return
        
        try:
            prof_x = 12*mm
            prof_y = 20*mm
            prof_width = (self.PAGE_WIDTH - 30*mm) * 0.58
            prof_height = 50*mm
            
            self.c.drawImage(
                profile_path,
                prof_x, prof_y,
                width=prof_width,
                height=prof_height,
                preserveAspectRatio=True,
                anchor='c',
                mask='auto'
            )
            
            # Borde verde fino
            self.c.setStrokeColor(self.GREEN_HEADER)
            self.c.setLineWidth(1)
            self.c.rect(prof_x, prof_y, prof_width, prof_height, fill=0, stroke=1)
            
        except Exception as e:
            print(f"Error cargando perfil: {e}")
    
    def _draw_page2_info_panel(self, technical_data, mide_data):
        """Panel derecho con ficha técnica + MIDE + contacto"""
        panel_x = self.PAGE_WIDTH - 115*mm
        panel_y = self.PAGE_HEIGHT - 23*mm
        panel_width = 105*mm
        panel_height = self.PAGE_HEIGHT - 38*mm
        
        # Fondo gris muy claro
        self.c.setFillColor(self.GRAY_BG)
        self.c.rect(panel_x, 18*mm, panel_width, panel_height, fill=1, stroke=0)
        
        # Borde verde
        self.c.setStrokeColor(self.GREEN_HEADER)
        self.c.setLineWidth(2)
        self.c.rect(panel_x, 18*mm, panel_width, panel_height, fill=0, stroke=1)
        
        # FICHA TÉCNICA
        y_current = panel_y - 5*mm
        self._draw_technical_section(panel_x + 5*mm, y_current, panel_width - 10*mm, technical_data)
        
        # MATRIZ MIDE
        y_current -= 60*mm
        self._draw_mide_matrix(panel_x + 5*mm, y_current, panel_width - 10*mm, mide_data)
        
        # CONTACTO Y QR
        y_current -= 65*mm
        self._draw_contact_section(panel_x + 5*mm, y_current, panel_width - 10*mm, technical_data)
    
    def _draw_technical_section(self, x, y, width, data):
        """Ficha técnica con datos de la ruta"""
        # Cabecera verde
        self.c.setFillColor(self.GREEN_HEADER)
        self.c.rect(x, y, width, 8*mm, fill=1, stroke=0)
        
        self.c.setFillColor(self.WHITE)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawCentredString(x + width/2, y + 2.5*mm, "FICHA TÉCNICA")
        
        # Datos en filas
        y_row = y - 8*mm
        row_height = 7*mm
        
        items = [
            ("Horario:", data.get('time', '2h 35m')),
            ("Distancia:", data.get('distance', '11.0 km')),
            ("Subida:", data.get('elevation_up', '167 m')),
            ("Bajada:", data.get('elevation_down', '167 m')),
            ("Tipo:", data.get('route_type', 'Circular'))
        ]
        
        for i, (label, value) in enumerate(items):
            # Fondo alternado blanco
            if i % 2 == 0:
                self.c.setFillColor(self.WHITE)
                self.c.rect(x, y_row, width, row_height, fill=1, stroke=0)
            
            # Etiqueta
            self.c.setFillColor(self.TEXT_DARK)
            self.c.setFont("Helvetica-Bold", 9)
            self.c.drawString(x + 3*mm, y_row + 2*mm, label)
            
            # Valor
            self.c.setFont("Helvetica", 9)
            self.c.drawString(x + width/2, y_row + 2*mm, value)
            
            y_row -= row_height
    
    def _draw_mide_matrix(self, x, y, width, mide_data):
        """Matriz MIDE 2x2"""
        cell_width = width / 2
        cell_height = 26*mm
        
        mide_items = [
            ('SEVERIDAD', mide_data.get('severity', 1)),
            ('ORIENTACIÓN', mide_data.get('orientation', 2)),
            ('DIFICULTAD', mide_data.get('difficulty', 2)),
            ('ESFUERZO', mide_data.get('effort', 2))
        ]
        
        for i, (title, value) in enumerate(mide_items):
            col = i % 2
            row = i // 2
            
            cell_x = x + col * cell_width
            cell_y = y - row * cell_height
            
            # Color según valor
            if value <= 2:
                border_color = self.GREEN_HEADER
            elif value == 3:
                border_color = self.YELLOW_ACCENT
            else:
                border_color = colors.HexColor("#C00000")
            
            # Fondo blanco
            self.c.setFillColor(self.WHITE)
            self.c.rect(cell_x, cell_y - cell_height, cell_width, cell_height, fill=1, stroke=0)
            
            # Borde grueso coloreado
            self.c.setStrokeColor(border_color)
            self.c.setLineWidth(3)
            self.c.rect(cell_x, cell_y - cell_height, cell_width, cell_height, fill=0, stroke=1)
            
            # Valor numérico grande y centrado
            self.c.setFillColor(border_color)
            self.c.setFont("Helvetica-Bold", 28)
            self.c.drawCentredString(
                cell_x + cell_width/2,
                cell_y - cell_height/2 - 3*mm,
                str(value)
            )
            
            # Título encima del número
            self.c.setFillColor(self.TEXT_DARK)
            self.c.setFont("Helvetica-Bold", 7)
            self.c.drawCentredString(
                cell_x + cell_width/2,
                cell_y - 6*mm,
                title
            )
    
    def _draw_contact_section(self, x, y, width, data):
        """Sección de contacto con teléfonos y QR"""
        # Título
        self.c.setFillColor(self.GREEN_HEADER)
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(x, y, "CONTACTO")
        
        y -= 8*mm
        
        # Emergencias en rojo
        self.c.setFillColor(colors.HexColor("#C00000"))
        self.c.setFont("Helvetica-Bold", 10)
        self.c.drawString(x, y, f"Emergencias: {data.get('emergency', '112')}")
        
        y -= 6*mm
        
        # Teléfono del parque
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 9)
        self.c.drawString(x, y, f"Parque: {data.get('phone', '949 88 53 00')}")
        
        y -= 5*mm
        
        # Web
        web_url = data.get('web', 'http://areasprotegidas.castillalamancha.es')
        self.c.setFont("Helvetica", 7)
        
        # Dividir URL si es muy larga
        if len(web_url) > 40:
            parts = web_url.split('/')
            line1 = '/'.join(parts[:3]) + '/'
            line2 = '/'.join(parts[3:]) if len(parts) > 3 else ''
            self.c.drawString(x, y, line1)
            if line2:
                y -= 3*mm
                self.c.drawString(x, y, line2)
        else:
            self.c.drawString(x, y, web_url)
        
        # QR Code en la esquina inferior derecha del panel
        try:
            qr = qrcode.QRCode(version=1, box_size=3, border=1)
            qr.add_data(web_url)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color=self.GREEN_HEADER, back_color="white")
            
            qr_bytes = io.BytesIO()
            qr_img.save(qr_bytes, format='PNG')
            qr_bytes.seek(0)
            
            from reportlab.lib.utils import ImageReader
            self.c.drawImage(
                ImageReader(qr_bytes),
                x + width - 28*mm, y - 25*mm,
                width=25*mm,
                height=25*mm,
                mask='auto'
            )
        except Exception as e:
            print(f"Error generando QR: {e}")
    
    def _draw_page2_footer(self, date_str):
        """Pie de página 2"""
        self.c.setStrokeColor(self.GREEN_HEADER)
        self.c.setLineWidth(0.5)
        self.c.line(10*mm, 12*mm, self.PAGE_WIDTH - 10*mm, 12*mm)
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 8)
        self.c.drawString(10*mm, 8*mm, "Topoguía de Senderismo - 2/2")
        
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawCentredString(self.PAGE_WIDTH/2, 8*mm, "Castilla-La Mancha")
        
        self.c.setFont("Helvetica", 8)
        self.c.drawRightString(self.PAGE_WIDTH - 10*mm, 8*mm, date_str)
    
    def _wrap_text(self, text, max_width_mm, font_size):
        """Divide texto en líneas que caben en el ancho especificado"""
        words = text.split()
        lines = []
        current_line = []
        
        # Aproximación: cada carácter ocupa ~0.5 * font_size puntos
        # Convertir mm a puntos: 1mm = 2.83 puntos
        max_width_pts = max_width_mm * 2.83
        char_width = font_size * 0.5
        max_chars = int(max_width_pts / char_width)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def generate(self, page1_data, page2_data):
        """Genera el PDF completo de 2 páginas"""
        # PÁGINA 1
        self._draw_page1_header(
            page1_data.get('route_code', 'PR-GU 00'),
            page1_data.get('route_name', 'Sendero')
        )
        
        self._draw_page1_panoramic(page1_data.get('panoramic_image'))
        
        self._draw_page1_text_columns(
            page1_data.get('paragraphs', []),
            page1_data.get('recommendations', [])
        )
        
        self._draw_page1_footer(page1_data.get('date', datetime.now().strftime('%Y-%m-%d')))
        
        self.c.showPage()
        
        # PÁGINA 2
        self._draw_page2_header()
        
        self._draw_page2_map(page2_data.get('map_image'))
        
        self._draw_page2_profile(page2_data.get('profile_image'))
        
        self._draw_page2_info_panel(
            page2_data.get('technical', {}),
            page2_data.get('mide', {})
        )
        
        self._draw_page2_footer(page2_data.get('date', datetime.now().strftime('%Y-%m-%d')))
        
        self.c.save()
        return self.output_path


def create_topoguide_pdf(output_path, data, logo_left=None, logo_right=None):
    """
    Crea una topoguía PDF replicando el diseño oficial
    
    Args:
        output_path: Ruta donde guardar el PDF
        data: Diccionario con todos los datos
        logo_left: No usado (reservado para futuras versiones)
        logo_right: No usado (reservado para futuras versiones)
    """
    generator = TopoGuidePDFGenerator(output_path)
    
    # Preparar datos página 1
    page1_data = {
        'route_code': data.get('route_code', 'PR-GU 00'),
        'route_name': data.get('route_name', 'Sendero'),
        'panoramic_image': data.get('panoramic_image'),
        'paragraphs': data.get('paragraphs', []),
        'recommendations': data.get('recommendations', []),
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    # Preparar datos página 2
    page2_data = {
        'map_image': data.get('map_image'),
        'profile_image': data.get('profile_image'),
        'mide': {
            'severity': data.get('mide', {}).get('severity', 1),
            'orientation': data.get('mide', {}).get('orientation', 2),
            'difficulty': data.get('mide', {}).get('difficulty', 2),
            'effort': data.get('mide', {}).get('effort', 2)
        },
        'technical': {
            'time': data.get('time', '2h 35m'),
            'distance': data.get('distance', '11.0 km'),
            'elevation_up': data.get('elevation_up', '167 m'),
            'elevation_down': data.get('elevation_down', '167 m'),
            'route_type': data.get('route_type', 'Circular'),
            'emergency': data.get('emergency', '112'),
            'phone': data.get('phone', '949 88 53 00'),
            'web': data.get('web', 'http://areasprotegidas.castillalamancha.es')
        },
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    generator.generate(page1_data, page2_data)
    return output_path
