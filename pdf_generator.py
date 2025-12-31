"""
Módulo de generación de PDF para Topoguías de Senderismo
Genera documentos profesionales de 2 páginas en formato A4 Landscape
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from PIL import Image
import io
import qrcode
from datetime import datetime


class TopoGuidePDFGenerator:
    """Generador de topoguías de senderismo en formato PDF profesional"""
    
    # Constantes de diseño
    PAGE_WIDTH, PAGE_HEIGHT = A4
    LANDSCAPE_WIDTH, LANDSCAPE_HEIGHT = A4[1], A4[0]  # Landscape
    
    # Colores corporativos
    GREEN_PRIMARY = colors.HexColor("#007A33")
    GREEN_LIGHT = colors.HexColor("#E8F5E9")
    OCHRE = colors.HexColor("#E8AF2E")
    TEXT_DARK = colors.HexColor("#333333")
    TEXT_LIGHT = colors.HexColor("#FFFFFF")
    GRAY_LIGHT = colors.HexColor("#F5F5F5")
    GRAY_BORDER = colors.HexColor("#DDDDDD")
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.c = canvas.Canvas(output_path, pagesize=(self.LANDSCAPE_WIDTH, self.LANDSCAPE_HEIGHT))
        
        # Estilos de texto
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self):
        """Crea estilos de texto personalizados"""
        
        # Título principal PR-GU XX
        self.styles.add(ParagraphStyle(
            name='RouteTitle',
            parent=self.styles['Heading1'],
            fontSize=32,
            fontName='Helvetica-Bold',
            textColor=self.GREEN_PRIMARY,
            alignment=TA_CENTER,
            spaceAfter=5 * mm
        ))
        
        # Subtítulo de ruta
        self.styles.add(ParagraphStyle(
            name='RouteSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            fontName='Helvetica',
            textColor=self.TEXT_DARK,
            alignment=TA_CENTER,
            spaceAfter=10 * mm
        ))
        
        # Títulos de sección
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading3'],
            fontSize=12,
            fontName='Helvetica-Bold',
            textColor=self.GREEN_PRIMARY,
            alignment=TA_LEFT,
            spaceAfter=3 * mm
        ))
        
        # Texto de párrafo justificado
        self.styles.add(ParagraphStyle(
            name='BodyTextCustom',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Helvetica',
            textColor=self.TEXT_DARK,
            alignment=TA_JUSTIFY,
            leading=12,
            spaceAfter=3 * mm
        ))
        
        # Texto de recomendaciones
        self.styles.add(ParagraphStyle(
            name='RecommendationText',
            parent=self.styles['Normal'],
            fontSize=8,
            fontName='Helvetica',
            textColor=self.TEXT_DARK,
            alignment=TA_JUSTIFY,
            leading=10
        ))
        
        # Texto para panel de información
        self.styles.add(ParagraphStyle(
            name='InfoPanelText',
            parent=self.styles['Normal'],
            fontSize=7,
            fontName='Helvetica',
            textColor=self.TEXT_DARK,
            alignment=TA_LEFT,
            leading=9
        ))
    
    def _draw_header(self, route_code, route_name, logo_left=None, logo_right=None):
        """Dibuja la cabecera con logos y título"""
        # Fondo verde de cabecera
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.rect(0, self.LANDSCAPE_HEIGHT - 20 * mm, self.LANDSCAPE_WIDTH, 20 * mm, fill=1, stroke=0)
        
        # Logo izquierdo (si existe)
        if logo_left:
            try:
                img = Image.open(logo_left)
                img.thumbnail((25 * mm, 15 * mm))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                self.c.drawImage(
                    self._pil_to_reportlab(img_bytes),
                    10 * mm, self.LANDSCAPE_HEIGHT - 18 * mm,
                    width=img.width / 2.83,
                    height=img.height / 2.83,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando logo izquierdo: {e}")
        
        # Logo derecho (si existe)
        if logo_right:
            try:
                img = Image.open(logo_right)
                img.thumbnail((25 * mm, 15 * mm))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                self.c.drawImage(
                    self._pil_to_reportlab(img_bytes),
                    self.LANDSCAPE_WIDTH - 35 * mm, self.LANDSCAPE_HEIGHT - 18 * mm,
                    width=img.width / 2.83,
                    height=img.height / 2.83,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando logo derecho: {e}")
        
        # Título de ruta (PR-GU XX)
        self.c.setFillColor(self.TEXT_LIGHT)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, self.LANDSCAPE_HEIGHT - 12 * mm, route_code)
        
        # Subtítulo
        self.c.setFillColor(self.TEXT_LIGHT)
        self.c.setFont("Helvetica", 11)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, self.LANDSCAPE_HEIGHT - 18 * mm, route_name)
    
    def _draw_panoramic(self, panoramic_path, landmarks=None):
        """Dibuja la imagen panorámica con etiquetas"""
        img_y_start = self.LANDSCAPE_HEIGHT - 20 * mm - 55 * mm
        img_height = 55 * mm
        
        if panoramic_path:
            try:
                img = Image.open(panoramic_path)
                aspect_ratio = img.width / img.height
                img_width = min(self.LANDSCAPE_WIDTH - 20 * mm, img_height * aspect_ratio)
                img_display_height = img_width / aspect_ratio
                
                x_pos = (self.LANDSCAPE_WIDTH - img_width) / 2
                
                self.c.drawImage(
                    panoramic_path,
                    x_pos, self.LANDSCAPE_HEIGHT - 20 * mm - img_display_height - 2 * mm,
                    width=img_width,
                    height=img_display_height,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando imagen panorámica: {e}")
        
        # Etiqueta "MIRADOR" vertical
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 10)
        
        self.c.saveState()
        self.c.translate(8 * mm, self.LANDSCAPE_HEIGHT - 20 * mm - img_height / 2)
        self.c.rotate(90)
        self.c.drawCentredString(0, 0, "MIRADOR")
        self.c.restoreState()
        
        # Etiquetas de paisajes
        if landmarks:
            for landmark in landmarks:
                try:
                    x = landmark.get('x', 0) * mm
                    y = (self.LANDSCAPE_HEIGHT - 20 * mm - img_height + landmark.get('y', 0)) * mm
                    text = landmark.get('text', '')
                    
                    # Fondo semitransparente
                    text_width = len(text) * 3 * mm
                    self.c.setFillColorRGB(0, 0, 0, 0.5)
                    self.c.roundRect(
                        x - text_width/2, y,
                        text_width, 8 * mm, 2, fill=1, stroke=0
                    )
                    self.c.setFillColor(self.TEXT_LIGHT)
                    self.c.drawCentredString(x, y + 2 * mm, text)
                except Exception as e:
                    print(f"Error dibujando landmark: {e}")
    
    def _draw_descriptions(self, paragraphs):
        """Dibuja los párrafos descriptivos"""
        col_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.60
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 9)
        
        y_position = self.LANDSCAPE_HEIGHT - 80 * mm
        
        for i, paragraph in enumerate(paragraphs[:4]):
            lines = self._wrap_text(paragraph, col_width, 9, "Helvetica")
            for line in lines[:3]:
                if y_position > 20 * mm:
                    self.c.drawString(15 * mm, y_position, line)
                    y_position -= 4 * mm
            y_position -= 3 * mm
    
    def _draw_recommendations(self, recommendations):
        """Dibuja el bloque de recomendaciones"""
        box_x = self.LANDSCAPE_WIDTH - 75 * mm
        box_width = 65 * mm
        box_height = 100 * mm
        box_y = self.LANDSCAPE_HEIGHT - 30 * mm
        
        # Fondo gris claro
        self.c.setFillColor(self.GRAY_LIGHT)
        self.c.rect(box_x, box_y - box_height, box_width, box_height, fill=1, stroke=0)
        
        # Borde verde
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(2)
        self.c.rect(box_x, box_y - box_height, box_width, box_height, fill=0, stroke=1)
        
        # Título
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(box_x + 5 * mm, box_y - 8 * mm, "RECOMENDACIONES")
        
        # Lista
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 7)
        
        y_recomm = box_y - 15 * mm
        for rec in recommendations[:6]:
            # Viñeta
            self.c.setFillColor(self.OCHRE)
            self.c.circle(box_x + 4 * mm, y_recomm, 1 * mm, fill=1, stroke=0)
            
            self.c.setFillColor(self.TEXT_DARK)
            lines = self._wrap_text(rec, box_width - 15 * mm, 7, "Helvetica")
            for line in lines[:2]:
                self.c.drawString(box_x + 8 * mm, y_recomm - 2 * mm, line)
                y_recomm -= 3.5 * mm
            y_recomm -= 2 * mm
    
    def _draw_page1(self, data, logo_left=None, logo_right=None):
        """Genera la página 1 completa"""
        # Cabecera
        self._draw_header(
            data.get('route_code', 'PR-GU 00'),
            data.get('route_name', 'Nombre del Sendero'),
            logo_left,
            logo_right
        )
        
        # Imagen panorámica
        self._draw_panoramic(
            data.get('panoramic_image'),
            data.get('landmarks', [])
        )
        
        # Descripciones
        self._draw_descriptions(data.get('paragraphs', []))
        
        # Recomendaciones
        self._draw_recommendations(data.get('recommendations', []))
        
        # Pie de página
        self._draw_footer(page_num=1, date_str=data.get('date'))
    
    def _draw_footer(self, page_num=1, date_str=None):
        """Dibuja el pie de página"""
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(1)
        self.c.line(10 * mm, 10 * mm, self.LANDSCAPE_WIDTH - 10 * mm, 10 * mm)
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 7)
        self.c.drawString(10 * mm, 5 * mm, f"Topoguía de Senderismo - {page_num}/2")
        
        self.c.setFont("Helvetica-Bold", 7)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, 5 * mm, "Castilla-La Mancha")
        
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        self.c.drawRightString(self.LANDSCAPE_WIDTH - 10 * mm, 5 * mm, date_str)
    
    def _draw_map(self, map_path, waypoints=None):
        """Dibuja el mapa topográfico"""
        map_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.55
        map_height = 85 * mm
        map_x = 15 * mm
        map_y = self.LANDSCAPE_HEIGHT - 30 * mm - map_height
        
        if map_path:
            try:
                self.c.drawImage(
                    map_path,
                    map_x, map_y,
                    width=map_width,
                    height=map_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando mapa: {e}")
        
        # Borde
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(2)
        self.c.rect(map_x, map_y, map_width, map_height, fill=0, stroke=1)
    
    def _draw_elevation_profile(self, profile_path):
        """Dibuja el perfil de elevación"""
        profile_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.55
        profile_height = 45 * mm
        profile_x = 15 * mm
        profile_y = 20 * mm
        
        if profile_path:
            try:
                self.c.drawImage(
                    profile_path,
                    profile_x, profile_y,
                    width=profile_width,
                    height=profile_height,
                    preserveAspectRatio=True,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando perfil: {e}")
        
        # Borde
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(2)
        self.c.rect(profile_x, profile_y, profile_width, profile_height, fill=0, stroke=1)
    
    def _draw_mide_panel(self, mide_data, technical_data):
        """Dibuja el panel MIDE e información técnica"""
        panel_x = self.LANDSCAPE_WIDTH - 110 * mm
        panel_width = 95 * mm
        panel_y = self.LANDSCAPE_HEIGHT - 30 * mm
        panel_height = self.LANDSCAPE_HEIGHT - 40 * mm
        
        # Fondo
        self.c.setFillColor(self.GRAY_LIGHT)
        self.c.rect(panel_x, 15 * mm, panel_width, panel_height, fill=1, stroke=0)
        
        # Borde
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(2)
        self.c.rect(panel_x, 15 * mm, panel_width, panel_height, fill=0, stroke=1)
        
        # Contenido
        y_pos = panel_y - 10 * mm
        
        # Tabla técnica
        self._draw_technical_table(panel_x + 5 * mm, y_pos, technical_data, panel_width - 10 * mm)
        
        # MIDE grid
        self._draw_mide_grid(panel_x + 5 * mm, y_pos - 50 * mm, mide_data, panel_width - 10 * mm)
        
        # Info adicional
        self._draw_info_bottom(panel_x + 5 * mm, 20 * mm, technical_data)
    
    def _draw_technical_table(self, x, y, data, width):
        """Tabla de datos técnicos"""
        # Cabecera
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.rect(x, y, width, 8 * mm, fill=1, stroke=0)
        
        self.c.setFillColor(self.TEXT_LIGHT)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawCentredString(x + width / 2, y + 2 * mm, "FICHA TÉCNICA")
        
        # Datos
        row_height = 6 * mm
        y_row = y - row_height
        
        data_rows = [
            ("Horario:", data.get('time', '2h 30m')),
            ("Distancia:", data.get('distance', '11,0 km')),
            ("Subida:", data.get('elevation_up', '167 m')),
            ("Bajada:", data.get('elevation_down', '167 m')),
            ("Tipo:", data.get('route_type', 'Circular'))
        ]
        
        self.c.setFont("Helvetica", 7)
        for label, value in data_rows:
            self.c.setFillColor(self.TEXT_DARK)
            self.c.drawString(x + 2 * mm, y_row + 1 * mm, label)
            self.c.setFont("Helvetica-Bold", 7)
            self.c.drawString(x + width / 2, y_row + 1 * mm, value)
            self.c.setFont("Helvetica", 7)
            y_row -= row_height
    
    def _draw_mide_grid(self, x, y, mide_data, width):
        """Cuadrícula MIDE"""
        cell_width = width / 2
        cell_height = 22 * mm
        
        mide_items = [
            ('SEVERIDAD', mide_data.get('severity', 1)),
            ('ORIENTACIÓN', mide_data.get('orientation', 2)),
            ('DIFICULTAD', mide_data.get('difficulty', 2)),
            ('ESFUERZO', mide_data.get('effort', 2))
        ]
        
        for i, (title, value) in enumerate(mide_items):
            cell_x = x + (i % 2) * cell_width
            cell_y = y - (i // 2) * cell_height
            
            # Color
            if value <= 2:
                color = self.GREEN_PRIMARY
            elif value == 3:
                color = self.OCHRE
            else:
                color = colors.HexColor("#E74C3C")
            
            # Celda
            self.c.setStrokeColor(color)
            self.c.setLineWidth(2)
            self.c.rect(cell_x, cell_y, cell_width, cell_height, fill=0, stroke=1)
            
            # Valor
            self.c.setFillColor(color)
            self.c.setFont("Helvetica-Bold", 18)
            self.c.drawCentredString(cell_x + cell_width / 2, cell_y + cell_height / 2 - 2 * mm, str(value))
            
            # Título
            self.c.setFillColor(self.TEXT_DARK)
            self.c.setFont("Helvetica-Bold", 6)
            self.c.drawCentredString(cell_x + cell_width / 2, cell_y + cell_height - 5 * mm, title)
    
    def _draw_info_bottom(self, x, y, data):
        """Información adicional"""
        # Teléfonos
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x, y + 35 * mm, "CONTACTO")
        
        self.c.setFillColor(colors.red)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x, y + 30 * mm, f"Emergencias: {data.get('emergency', '112')}")
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 7)
        self.c.drawString(x, y + 25 * mm, f"Parque: {data.get('phone', '949 88 53 00')}")
        self.c.drawString(x, y + 20 * mm, data.get('web', 'info@parque.es')[:40])
        
        # QR
        try:
            qr = qrcode.QRCode(box_size=3, border=1)
            qr.add_data(data.get('web', 'http://example.com'))
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color=self.GREEN_PRIMARY, back_color="white")
            
            qr_bytes = io.BytesIO()
            qr_img.save(qr_bytes, format='PNG')
            qr_bytes.seek(0)
            
            self.c.drawImage(
                self._pil_to_reportlab(qr_bytes),
                x + 50 * mm, y + 15 * mm,
                width=25 * mm,
                height=25 * mm,
                mask='auto'
            )
        except Exception as e:
            print(f"Error generando QR: {e}")
    
    def _draw_page2(self, data):
        """Página 2"""
        # Cabecera simple
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.rect(0, self.LANDSCAPE_HEIGHT - 15 * mm, self.LANDSCAPE_WIDTH, 15 * mm, fill=1, stroke=0)
        
        self.c.setFillColor(self.TEXT_LIGHT)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, self.LANDSCAPE_HEIGHT - 10 * mm, "MAPA Y PERFIL")
        
        # Mapa
        self._draw_map(data.get('map_image'), data.get('waypoints', []))
        
        # Perfil
        self._draw_elevation_profile(data.get('profile_image'))
        
        # Panel MIDE
        self._draw_mide_panel(data.get('mide', {}), data.get('technical', {}))
        
        # Footer
        self._draw_footer(page_num=2, date_str=data.get('date'))
    
    def _wrap_text(self, text, max_width, font_size, font_name):
        """Ajusta texto al ancho"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        char_width = font_size * 0.5
        max_chars = int(max_width / char_width)
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _pil_to_reportlab(self, img_bytes):
        """Convierte imagen a formato ReportLab"""
        from reportlab.lib.utils import ImageReader
        return ImageReader(img_bytes)
    
    def generate(self, page1_data, page2_data, logo_left=None, logo_right=None):
        """Genera PDF completo"""
        # Página 1
        self._draw_page1(page1_data, logo_left, logo_right)
        self.c.showPage()
        
        # Página 2
        self._draw_page2(page2_data)
        self.c.showPage()
        
        # Guardar
        self.c.save()
        return self.output_path


def create_topoguide_pdf(output_path, data, logo_left=None, logo_right=None):
    """
    Crea topoguía PDF
    
    Args:
        output_path: Ruta de salida
        data: Datos de la ruta
        logo_left: Logo izquierdo (opcional)
        logo_right: Logo derecho (opcional)
    """
    generator = TopoGuidePDFGenerator(output_path)
    
    # Página 1
    page1_data = {
        'route_code': data.get('route_code', 'PR-GU 00'),
        'route_name': data.get('route_name', 'Sendero'),
        'panoramic_image': data.get('panoramic_image'),
        'landmarks': data.get('landmarks', []),
        'paragraphs': data.get('paragraphs', []),
        'recommendations': data.get('recommendations', []),
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    # Página 2
    page2_data = {
        'map_image': data.get('map_image'),
        'profile_image': data.get('profile_image'),
        'waypoints': data.get('waypoints', []),
        'mide': data.get('mide', {
            'severity': 1,
            'orientation': 2,
            'difficulty': 2,
            'effort': 2
        }),
        'technical': {
            'time': data.get('time', '2h 30m'),
            'distance': data.get('distance', '11,0 km'),
            'elevation_up': data.get('elevation_up', '167 m'),
            'elevation_down': data.get('elevation_down', '167 m'),
            'route_type': data.get('route_type', 'Circular'),
            'emergency': data.get('emergency', '112'),
            'phone': data.get('phone', '949 88 53 00'),
            'web': data.get('web', 'http://example.com')
        },
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    generator.generate(page1_data, page2_data, logo_left, logo_right)
    return output_path
