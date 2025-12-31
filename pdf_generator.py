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
        self.c = canvas.Canvas(output_path, pagesize=A4)
        self.c.setPageSize(A4)  # Usamos A4 normal pero rotaremos contenido
        
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
            name='BodyText',
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
                    width=img.width / 2.83,  # Conversión a puntos
                    height=img.height / 2.83,
                    mask='auto'
                )
            except:
                pass
        
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
            except:
                pass
        
        # Título de ruta (PR-GU XX) - muy grande en verde oscuro
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, self.LANDSCAPE_HEIGHT - 14 * mm, route_code)
        
        # Subtítulo
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 12)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, self.LANDSCAPE_HEIGHT - 19 * mm, route_name)
    
    def _draw_panoramic(self, panoramic_path, landmarks=None):
        """Dibuja la imagen panorámica con etiquetas"""
        img_y_start = self.LANDSCAPE_HEIGHT - 20 * mm - 55 * mm  # Debajo de cabecera
        img_height = 55 * mm
        
        if panoramic_path:
            try:
                img = Image.open(panoramic_path)
                # Mantener aspecto ratio
                img.thumbnail((self.LANDSCAPE_WIDTH - 20 * mm, img_height))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # Centrar imagen
                img_width = img.width / 2.83
                x_pos = (self.LANDSCAPE_WIDTH - img_width) / 2
                
                self.c.drawImage(
                    self._pil_to_reportlab(img_bytes),
                    x_pos, self.LANDSCAPE_HEIGHT - 20 * mm - img_height - 2 * mm,
                    width=img_width,
                    height=img_height / 2.83,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando imagen panorámica: {e}")
        
        # Etiqueta "MIRADOR" vertical en el lateral izquierdo
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 10)
        
        # Guardar estado y rotar
        self.c.saveState()
        self.c.translate(8 * mm, self.LANDSCAPE_HEIGHT - 20 * mm - img_height / 2)
        self.c.rotate(90)
        self.c.drawCentredString(0, 0, "MIRADOR DEL PICO")
        self.c.restoreState()
        
        # Etiquetas de paisajes si se proporcionan
        if landmarks:
            self.c.setFillColor(self.TEXT_LIGHT)
            self.c.setFont("Helvetica-Bold", 8)
            for landmark in landmarks:
                x = landmark.get('x', 0)
                y = landmark.get('y', 0)
                text = landmark.get('text', '')
                # Fondo semitransparente para texto
                self.c.setFillColorRGB(0, 0, 0, 0.5)
                self.c.roundRect(
                    (x - 20) * mm, 
                    (self.LANDSCAPE_HEIGHT - 20 * mm - img_height + y) * mm,
                    len(text) * 3 * mm + 5 * mm, 8 * mm, 2, fill=1, stroke=0
                )
                self.c.setFillColor(self.TEXT_LIGHT)
                self.c.drawCentredString(x * mm, (self.LANDSCAPE_HEIGHT - 20 * mm - img_height + y + 2) * mm, text)
    
    def _draw_descriptions(self, paragraphs):
        """Dibuja los párrafos descriptivos"""
        text_y_start = 20 * mm  # Margen inferior
        col_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.65  # 65% del ancho
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 9)
        
        y_position = self.LANDSCAPE_HEIGHT - 20 * mm - 55 * mm - 10 * mm
        
        for i, paragraph in enumerate(paragraphs):
            if i < 4:  # Máximo 4 párrafos
                # Mostrar solo primeras líneas de cada párrafo
                lines = self._wrap_text(paragraph, col_width, 9, "Helvetica")
                for line in lines[:3]:  # Máx 3 líneas por párrafo
                    self.c.drawString(15 * mm, y_position, line)
                    y_position -= 11 * mm
                y_position -= 5 * mm  # Espacio entre párrafos
    
    def _draw_recommendations(self, recommendations):
        """Dibuja el bloque de recomendaciones"""
        # Posición: columna derecha
        box_x = self.LANDSCAPE_WIDTH - (self.LANDSCAPE_WIDTH - 30 * mm) * 0.65 + 5 * mm
        box_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.30
        box_height = 100 * mm
        box_y = self.LANDSCAPE_HEIGHT - 20 * mm - 55 * mm - 10 * mm
        
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
        
        # Lista de recomendaciones
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 8)
        
        y_recomm = box_y - 15 * mm
        for rec in recommendations[:5]:  # Máx 5 recomendaciones
            # Viñeta
            self.c.setFillColor(self.OCHRE)
            self.c.circle(box_x + 7 * mm, y_recomm - 2 * mm, 2 * mm, fill=1, stroke=0)
            
            self.c.setFillColor(self.TEXT_DARK)
            self.c.setFont("Helvetica", 7)
            self.c.drawString(box_x + 12 * mm, y_recomm - 5 * mm, rec[:60] + ("..." if len(rec) > 60 else ""))
            y_recomm -= 12 * mm
    
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
        
        # Pie de página página 1
        self._draw_footer(page_num=1)
    
    def _draw_footer(self, page_num=1):
        """Dibuja el pie de página"""
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(1)
        self.c.line(10 * mm, 10 * mm, self.LANDSCAPE_WIDTH - 10 * mm, 10 * mm)
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 7)
        self.c.drawString(10 * mm, 5 * mm, f"Topoguía de Senderismo - {page_num}/2")
        
        self.c.setFont("Helvetica-Bold", 7)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, 5 * mm, "Castilla-La Mancha")
        
        self.c.drawRightString(self.LANDSCAPE_WIDTH - 10 * mm, 5 * mm, data.get('date', datetime.now().strftime('%Y-%m-%d')))
    
    def _draw_map(self, map_path, waypoints=None):
        """Dibuja el mapa topográfico con traza"""
        map_width = self.LANDSCAPE_WIDTH - 30 * mm
        map_height = 80 * mm
        map_x = 10 * mm
        map_y = self.LANDSCAPE_HEIGHT - 25 * mm - map_height
        
        if map_path:
            try:
                img = Image.open(map_path)
                img.thumbnail((map_width, map_height))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                self.c.drawImage(
                    self._pil_to_reportlab(img_bytes),
                    map_x, map_y,
                    width=img.width / 2.83,
                    height=img.height / 2.83,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando mapa: {e}")
        
        # Borde verde alrededor del mapa
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(2)
        self.c.rect(map_x, map_y, map_width, map_height, fill=0, stroke=1)
        
        # Waypoints y marcadores
        if waypoints:
            self.c.setFont("Helvetica-Bold", 8)
            for wp in waypoints:
                x = wp.get('x', 0) * map_width / 100 + map_x
                y = wp.get('y', 0) * map_height / 100 + map_y
                label = wp.get('label', '')
                
                if wp.get('type') == 'start':
                    self.c.setFillColor(colors.Green)
                    self.c.circle(x, y, 4 * mm, fill=1, stroke=1)
                    self.c.setFillColor(colors.White)
                    self.c.drawCentredString(x, y + 5 * mm, "INICIO")
                elif wp.get('type') == 'end':
                    self.c.setFillColor(colors.Red)
                    self.c.circle(x, y, 4 * mm, fill=1, stroke=1)
                    self.c.setFillColor(colors.White)
                    self.c.drawCentredString(x, y + 5 * mm, "FINAL")
                elif wp.get('type') == 'viewpoint':
                    self.c.setFillColor(self.OCHRE)
                    self.c.circle(x, y, 3 * mm, fill=1, stroke=1)
    
    def _draw_elevation_profile(self, profile_path, data):
        """Dibuja el perfil de elevación"""
        profile_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.55
        profile_height = 50 * mm
        profile_x = 10 * mm
        profile_y = 15 * mm + 55 * mm
        
        if profile_path:
            try:
                img = Image.open(profile_path)
                img.thumbnail((profile_width, profile_height))
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                self.c.drawImage(
                    self._pil_to_reportlab(img_bytes),
                    profile_x, profile_y,
                    width=img.width / 2.83,
                    height=img.height / 2.83,
                    mask='auto'
                )
            except Exception as e:
                print(f"Error cargando perfil: {e}")
        
        # Etiquetas del perfil
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 7)
        
        # Labels
        labels = [
            (profile_x + 5 * mm, profile_y + profile_height + 2 * mm, "INICIO"),
            (profile_x + profile_width * 0.3, profile_y + profile_height + 2 * mm, "MIRABUENO"),
            (profile_x + profile_width * 0.6, profile_y + profile_height + 2 * mm, "ARAGOSA"),
            (profile_x + profile_width - 20 * mm, profile_y + profile_height + 2 * mm, "FINAL")
        ]
        
        for x, y, text in labels:
            self.c.drawCentredString(x, y, text)
    
    def _draw_mide_panel(self, mide_data, technical_data):
        """Dibuja el panel de información MIDE"""
        panel_x = self.LANDSCAPE_WIDTH - (self.LANDSCAPE_WIDTH - 30 * mm) * 0.40 - 5 * mm
        panel_width = (self.LANDSCAPE_WIDTH - 30 * mm) * 0.40
        panel_y = 15 * mm
        panel_height = 130 * mm
        
        # Fondo panel
        self.c.setFillColor(self.GRAY_LIGHT)
        self.c.rect(panel_x, panel_y, panel_width, panel_height, fill=1, stroke=0)
        
        # Borde verde
        self.c.setStrokeColor(self.GREEN_PRIMARY)
        self.c.setLineWidth(2)
        self.c.rect(panel_x, panel_y, panel_width, panel_height, fill=0, stroke=1)
        
        # Tabla de datos técnicos
        self._draw_technical_table(panel_x + 5 * mm, panel_y + panel_height - 25 * mm, technical_data, panel_width - 10 * mm)
        
        # Matriz MIDE
        self._draw_mide_grid(panel_x + 5 * mm, panel_y + panel_height - 75 * mm, mide_data, panel_width - 10 * mm)
        
        # Panel inferior: señalización, consejos, teléfonos
        self._draw_info_bottom(panel_x + 5 * mm, panel_y + 5 * mm, technical_data)
    
    def _draw_technical_table(self, x, y, data, width):
        """Dibuja la tabla de datos técnicos"""
        # Fondo verde para cabecera
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.rect(x, y - 12 * mm, width, 8 * mm, fill=1, stroke=0)
        
        self.c.setFillColor(self.TEXT_LIGHT)
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawCentredString(x + width / 2, y - 8 * mm, "FICHA TÉCNICA")
        
        # Datos
        row_height = 7 * mm
        y_row = y - 12 * mm - row_height
        
        data_rows = [
            ("Horario:", data.get('time', '2h 30m')),
            ("Distancia:", data.get('distance', '11,0 km')),
            ("Desnivel Subida:", data.get('elevation_up', '167 m')),
            ("Desnivel Bajada:", data.get('elevation_down', '167 m')),
            ("Tipo de Ruta:", data.get('route_type', 'Circular'))
        ]
        
        self.c.setFont("Helvetica-Bold", 8)
        for label, value in data_rows:
            # Fondo alternado
            if data_rows.index((label, value)) % 2 == 0:
                self.c.setFillColor(self.GREEN_LIGHT)
                self.c.rect(x, y_row - 2 * mm, width / 2, row_height, fill=1, stroke=0)
                self.c.rect(x + width / 2, y_row - 2 * mm, width / 2, row_height, fill=1, stroke=0)
            
            self.c.setFillColor(self.TEXT_DARK)
            self.c.drawString(x + 3 * mm, y_row, label)
            self.c.setFont("Helvetica", 8)
            self.c.drawString(x + width / 2 + 3 * mm, y_row, value)
            self.c.setFont("Helvetica-Bold", 8)
            y_row -= row_height
    
    def _draw_mide_grid(self, x, y, mide_data, width):
        """Dibuja la cuadrícula MIDE 2x2"""
        cell_width = width / 2
        cell_height = 25 * mm
        
        mide_items = [
            ('SEVERIDAD DEL MEDIO', mide_data.get('severity', 1), 'Medio'),
            ('ORIENTACIÓN', mide_data.get('orientation', 2), 'Itinerario'),
            ('DIFICULTAD', mide_data.get('difficulty', 2), 'Desplazamiento'),
            ('ESFUERZO', mide_data.get('effort', 2), 'Esfuerzo')
        ]
        
        for i, (title, value, subtitle) in enumerate(mide_items):
            cell_x = x + (i % 2) * cell_width
            cell_y = y - (i // 2) * cell_height
            
            # Color según valor
            if value <= 2:
                color = self.GREEN_PRIMARY
            elif value == 3:
                color = self.OCHRE
            else:
                color = colors.HexColor("#E74C3C")
            
            # Borde de celda
            self.c.setStrokeColor(color)
            self.c.setLineWidth(3)
            self.c.rect(cell_x, cell_y, cell_width, cell_height, fill=0, stroke=1)
            
            # Valor grande
            self.c.setFillColor(color)
            self.c.setFont("Helvetica-Bold", 20)
            self.c.drawCentredString(cell_x + cell_width / 2, cell_y + cell_height / 2 - 3 * mm, str(value))
            
            # Título y subtítulo
            self.c.setFillColor(self.TEXT_DARK)
            self.c.setFont("Helvetica-Bold", 7)
            self.c.drawCentredString(cell_x + cell_width / 2, cell_y + cell_height - 8 * mm, title)
            self.c.setFont("Helvetica", 6)
            self.c.drawCentredString(cell_x + cell_width / 2, cell_y + cell_height - 14 * mm, subtitle)
    
    def _draw_info_bottom(self, x, y, data):
        """Dibuja la información inferior del panel"""
        # Señalización
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x, y + 45 * mm, "SEÑALIZACIÓN")
        
        # Marcas de senderismo (rectángulos simulados)
        self.c.setFillColor(colors.White)
        self.c.rect(x + 5 * mm, y + 48 * mm, 30 * mm, 4 * mm, fill=1, stroke=1)
        self.c.rect(x + 38 * mm, y + 48 * mm, 30 * mm, 4 * mm, fill=1, stroke=1)
        self.c.rect(x + 71 * mm, y + 48 * mm, 20 * mm, 4 * mm, fill=1, stroke=1)
        
        # Consejos
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x, y + 30 * mm, "DISFRUTA DEL PARQUE")
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 6)
        consejos = ["· Usa prismáticos", "· Respira el silencio", "· No enciendas fuego", "· Llévate la basura"]
        for i, consejo in enumerate(consejos):
            self.c.drawString(x, y + 25 * mm - i * 4 * mm, consejo)
        
        # Teléfonos y web
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.setFont("Helvetica-Bold", 8)
        self.c.drawString(x, y + 12 * mm, "TELÉFONOS DE INTERÉS")
        
        self.c.setFillColor(colors.HexColor("#E74C3C"))
        self.c.setFont("Helvetica-Bold", 9)
        self.c.drawString(x, y + 7 * mm, f"Emergencias: {data.get('emergency', '112')}")
        
        self.c.setFillColor(self.TEXT_DARK)
        self.c.setFont("Helvetica", 7)
        self.c.drawString(x, y + 2 * mm, f"Parque: {data.get('phone', '949 88 53 00')}")
        self.c.drawString(x, y - 2 * mm, data.get('web', 'http://areasprotegidas.castillalamancha.es'))
        
        # QR Code
        qr = qrcode.QRCode(box_size=10, border=0)
        qr.add_data(data.get('web', 'http://example.com'))
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color=self.GREEN_PRIMARY, back_color="white")
        
        qr_bytes = io.BytesIO()
        qr_img.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)
        
        # Posicionar QR en esquina
        self.c.drawImage(
            self._pil_to_reportlab(qr_bytes),
            x + (x + 20 * mm),  # Ajustar posición
            y,
            width=20 * mm,
            height=20 * mm,
            mask='auto'
        )
    
    def _draw_page2(self, data):
        """Genera la página 2 completa"""
        # Sin cabecera verde completa en página 2, solo barra superior
        self.c.setFillColor(self.GREEN_PRIMARY)
        self.c.rect(0, self.LANDSCAPE_HEIGHT - 15 * mm, self.LANDSCAPE_WIDTH, 15 * mm, fill=1, stroke=0)
        
        # Título en cabecera página 2
        self.c.setFillColor(self.TEXT_LIGHT)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawCentredString(self.LANDSCAPE_WIDTH / 2, self.LANDSCAPE_HEIGHT - 10 * mm, "INFORMACIÓN TÉCNICA")
        
        # Mapa grande
        self._draw_map(data.get('map_image'), data.get('waypoints', []))
        
        # Perfil de elevación
        self._draw_elevation_profile(data.get('profile_image'), data)
        
        # Panel MIDE y datos técnicos
        self._draw_mide_panel(data.get('mide', {}), data.get('technical', {}))
        
        # Pie de página
        self._draw_footer(page_num=2)
    
    def _wrap_text(self, text, max_width, font_size, font_name):
        """Envuelve texto para que quepa en el ancho especificado"""
        lines = []
        words = text.split(' ')
        current_line = ""
        
        # Estimación simple de anchura de caracteres
        char_width = font_size * 0.5
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if len(test_line) * char_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _pil_to_reportlab(self, img_bytes):
        """Convierte imagen PIL a formato compatible con ReportLab"""
        from reportlab.lib.utils import ImageReader
        return ImageReader(img_bytes)
    
    def generate(self, page1_data, page2_data, logo_left=None, logo_right=None):
        """Genera el PDF completo de 2 páginas"""
        # Página 1
        self.c.showPage()
        self.c.setPageSize(A4)  # Mantener A4 pero procesar en landscape
        self.LANDSCAPE_WIDTH, self.LANDSCAPE_HEIGHT = A4[1], A4[0]
        
        self._draw_page1(page1_data, logo_left, logo_right)
        
        # Página 2
        self.c.showPage()
        self._draw_page2(page2_data)
        
        # Guardar PDF
        self.c.save()
        
        return self.output_path


def create_topoguide_pdf(output_path, data, logo_left=None, logo_right=None):
    """
    Función principal para crear una topoguía de senderismo
    
    Args:
        output_path: Ruta donde se guardará el PDF
        data: Diccionario con todos los datos de la ruta
        logo_left: Ruta al logo institucional izquierdo (opcional)
        logo_right: Ruta al logo institucional derecho (opcional)
    
    Returns:
        Ruta del PDF generado
    """
    generator = TopoGuidePDFGenerator(output_path)
    
    # Datos para página 1
    page1_data = {
        'route_code': data.get('route_code', 'PR-GU 00'),
        'route_name': data.get('route_name', 'Nombre del Sendero'),
        'panoramic_image': data.get('panoramic_image'),
        'landmarks': data.get('landmarks', []),
        'paragraphs': data.get('paragraphs', []),
        'recommendations': data.get('recommendations', []),
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d'))
    }
    
    # Datos para página 2
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
            'time': data.get('time', '2h 35m'),
            'distance': data.get('distance', '11,0 km'),
            'elevation_up': data.get('elevation_up', '167 m'),
            'elevation_down': data.get('elevation_down', '167 m'),
            'route_type': data.get('route_type', 'Circular'),
            'emergency': data.get('emergency', '112'),
            'phone': data.get('phone', '949 88 53 00'),
            'web': data.get('web', 'http://areasprotegidas.castillalamancha.es')
        }
    }
    
    generator.generate(page1_data, page2_data, logo_left, logo_right)
    
    return output_path
