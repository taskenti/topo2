"""
TopoGuide Pro Generator - Aplicación Streamlit para Creación de Topoguías de Senderismo

Esta aplicación permite generar documentos PDF profesionales de 2 páginas para rutas de senderismo,
replicando el diseño de las topoguías oficiales de Castilla-La Mancha.

Usage:
    streamlit run app.py

Author: MiniMax Agent
"""

import streamlit as st
import tempfile
import os
from datetime import datetime
from pdf_generator import create_topoguide_pdf


# Configuración de la página
st.set_page_config(
    page_title="TopoGuide Pro Generator",
    page_icon="🥾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Constantes de colores (replicando los del PDF)
COLOR_PRIMARY = "#007A33"
COLOR_SECONDARY = "#E8AF2E"


def apply_custom_css():
    """Aplica estilos CSS personalizados"""
    st.markdown(f"""
        <style>
        .main {{
            background-color: #f8f9fa;
        }}
        .stApp {{
            background-color: #f8f9fa;
        }}
        h1, h2, h3 {{
            color: {COLOR_PRIMARY};
        }}
        .section-header {{
            background-color: {COLOR_PRIMARY};
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .info-box {{
            background-color: #E8F5E9;
            border-left: 4px solid {COLOR_PRIMARY};
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 15px;
        }}
        .metric-card {{
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: {COLOR_PRIMARY};
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
        }}
        div.stButton > button {{
            background-color: {COLOR_PRIMARY};
            color: white;
            border: none;
            padding: 10px 25px;
            font-size: 16px;
            border-radius: 5px;
        }}
        div.stButton > button:hover {{
            background-color: #005a26;
            color: white;
        }}
        .success-message {{
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        </style>
    """, unsafe_allow_html=True)


def tab_datos_basicos():
    """Pestaña de datos básicos de la ruta"""
    st.markdown('<div class="section-header">📍 Datos Básicos de la Ruta</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        route_code = st.text_input(
            "Código de Ruta",
            value="PR-GU 08",
            help="Código oficial de la ruta (ej: PR-GU 08, SL-123, etc.)"
        )
    
    with col2:
        route_name = st.text_input(
            "Nombre del Sendero",
            value="Sendero Mandayona-Mirabueno-Aragosa",
            help="Nombre completo de la ruta"
        )
    
    with col3:
        route_type = st.selectbox(
            "Tipo de Ruta",
            options=["Circular", "Lineal", "Travesía", "Ida y Vuelta"],
            index=0,
            help="Tipo de recorrido según su configuración"
        )
    
    st.markdown("---")
    
    # Descripción de la ruta
    st.subheader("Descripción del Recorrido")
    
    col_desc1, col_desc2 = st.columns(2)
    
    with col_desc1:
        paragraph1 = st.text_area(
            "Párrafo 1: Introducción",
            value="Esta ruta parte desde el Centro de Interpretación Natural (C.I.N.) de Mandayona, discurriendo en un primer tramo por caminos vecinales y aprovechando el antiguo camino de herradura que comunicaba los pueblos de la zona. El sendero atraviesa un paisaje de transición entre la sierra y la campiña, donde se pueden apreciar ejemplos de arquitectura tradicional en piedra y adobe.",
            height=100,
            help="Introducción general de la ruta: origen, distancia total y características principales"
        )
        
        paragraph2 = st.text_area(
            "Párrafo 2: Descripción del Recorrido",
            value="El recorrido discurre principalmente por caminos vecinales y antiguas vías pecuarias que han sido recuperadas para el senderismo. Se atraviesa el típico paisaje de la Sierra de Altomira, caracterizado por suavemente onduladas laderas cubiertas de encinas, robles y matorrales mediterráneos. La arquitectura tradicional de los pequeños pueblos que atraviesa el sendero, con sus casas de piedra y tejados de teja árabe, añade un atractivo cultural al recorrido.",
            height=100,
            help="Descripción detallada del trazado y los tipos de caminos"
        )
    
    with col_desc2:
        paragraph3 = st.text_area(
            "Párrafo 3: Vegetación y Vistas",
            value="La vegetación predominante está formada por encinas, quejigos y matorrales como el tomillo, romero y espliego. En las zonas más umbrías aparecen manchas de roble melojo y vegetación de ribera en los pequeños arroyos. Los miradores naturales ofrecen amplias panorámicas de la Sierra de Altomira, permitiendo apreciar la belleza del paisaje serrano en todas sus direcciones.",
            height=100,
            help="Descripción de la vegetación y los puntos de vista"
        )
        
        paragraph4 = st.text_area(
            "Párrafo 4: Fauna",
            value="Este territorio alberga una rica fauna mediterránea. Es habitual observar aves rapaces como el buitre leonado, el águila real y el halcón peregrino. En los cursos de agua vive el mirlo acuático y la garza real. Entre los mamíferos encontramos jabalíes, corzos, zorros y, con un poco de suerte, alguna nutria en los arroyos.",
            height=100,
            help="Descripción de la fauna observable en la ruta"
        )
    
    return {
        'route_code': route_code,
        'route_name': route_name,
        'route_type': route_type,
        'paragraphs': [paragraph1, paragraph2, paragraph3, paragraph4]
    }


def tab_imagenes():
    """Pestaña de carga de imágenes"""
    st.markdown('<div class="section-header">📸 Imágenes de la Ruta</div>', unsafe_allow_html=True)
    
    st.info("📁 Formatos admitidos: JPG, PNG. Tamaño máximo: 5 MB por imagen.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Página 1: Imagen Panorámica")
        panoramic = st.file_uploader(
            "Foto Panorámica del Paisaje",
            type=['jpg', 'jpeg', 'png'],
            help="Imagen de paisaje que se mostrará en la parte superior de la página 1"
        )
        
        if panoramic:
            st.image(panoramic, caption="Vista previa imagen panorámica", use_container_width=True)
        
        # Etiquetas de paisaje
        st.markdown("#### Etiquetas en la Imagen (Opcional)")
        with st.expander("Añadir etiquetas a la imagen"):
            landmarks_text = st.text_area(
                "Nombres de picos y lugares (uno por línea)",
                value="Pico Ocejón\nCastillo de Atienza",
                help="Escribe los nombres que quieres que aparezcan sobre la imagen"
            )
    
    with col2:
        st.subheader("Página 2: Mapas Técnicos")
        
        map_image = st.file_uploader(
            "Mapa Topográfico",
            type=['jpg', 'jpeg', 'png'],
            help="Mapa topográfico con el trazado de la ruta"
        )
        
        if map_image:
            st.image(map_image, caption="Vista previa mapa topográfico", use_container_width=True)
        
        profile_image = st.file_uploader(
            "Gráfico de Perfil de Elevación",
            type=['jpg', 'jpeg', 'png'],
            help="Perfil de elevación de la ruta (gráfico de elevación vs distancia)"
        )
        
        if profile_image:
            st.image(profile_image, caption="Vista previa perfil de elevación", use_container_width=True)
    
    return {
        'panoramic': panoramic,
        'map': map_image,
        'profile': profile_image,
        'landmarks': landmarks_text if 'landmarks_text' in dir() else ""
    }


def tab_metricas():
    """Pestaña de métricas de la ruta"""
    st.markdown('<div class="section-header">📏 Métricas de la Ruta</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        distance = st.number_input(
            "Distancia Total (km)",
            min_value=0.0,
            max_value=100.0,
            value=11.0,
            step=0.1,
            help="Longitud total del recorrido en kilómetros"
        )
    
    with col2:
        hours = st.number_input(
            "Horas",
            min_value=0,
            max_value=12,
            value=2,
            step=1
        )
        minutes = st.number_input(
            "Minutos",
            min_value=0,
            max_value=59,
            value=35,
            step=5
        )
        time_str = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
    
    with col3:
        elevation_up = st.number_input(
            "Desnivel Subida (m)",
            min_value=0,
            max_value=3000,
            value=167,
            step=10,
            help="Desnivel acumulado de subida"
        )
    
    with col4:
        elevation_down = st.number_input(
            "Desnivel Bajada (m)",
            min_value=0,
            max_value=3000,
            value=167,
            step=10,
            help="Desnivel acumulado de bajada"
        )
    
    st.markdown("---")
    
    # Visualización de métricas
    st.subheader("Resumen de Métricas")
    
    mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
    
    with mcol1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{distance:.1f} km</div>
            <div class="metric-label">Distancia</div>
        </div>
        """, unsafe_allow_html=True)
    
    with mcol2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{time_str}</div>
            <div class="metric-label">Tiempo</div>
        </div>
        """, unsafe_allow_html=True)
    
    with mcol3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">↑ {elevation_up}m</div>
            <div class="metric-label">Subida</div>
        </div>
        """, unsafe_allow_html=True)
    
    with mcol4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">↓ {elevation_down}m</div>
            <div class="metric-label">Bajada</div>
        </div>
        """, unsafe_allow_html=True)
    
    with mcol5:
        elevation_gain = elevation_up + elevation_down
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">∓ {elevation_gain}m</div>
            <div class="metric-label">Desnivel Total</div>
        </div>
        """, unsafe_allow_html=True)
    
    return {
        'distance': f"{distance:.1f} km",
        'time': time_str,
        'elevation_up': f"{elevation_up} m",
        'elevation_down': f"{elevation_down} m"
    }


def tab_mide():
    """Pestaña del sistema MIDE"""
    st.markdown('<div class="section-header">⚠️ Sistema MIDE</div>', unsafe_allow_html=True)
    
    st.markdown("""
    El **Método de Información de Excursiones (MIDE)** es un sistema de evaluación de rutas 
    que permite valorar las dificultades objetivas y la exigencia física de cada sendero.
    Cada criterio se puntúa del 1 (bajo) al 5 (muy alto).
    """)
    
    col_info, col_grid = st.columns([1, 2])
    
    with col_info:
        st.markdown("""
        ### Escala de Valoración
        
        | Valor | Significado | Color |
        |-------|-------------|-------|
        | 1 | Bajo | Verde |
        | 2 | Medio-Bajo | Verde |
        | 3 | Medio | Amarillo |
        | 4 | Medio-Alto | Naranja |
        | 5 | Alto | Rojo |
        """)
    
    with col_grid:
        # Matriz MIDE interactiva
        st.subheader("Evaluación de la Ruta")
        
        mcol1, mcol2 = st.columns(2)
        
        with mcol1:
            severity = st.select_slider(
                "🔍 Severidad del Medio",
                options=[1, 2, 3, 4, 5],
                value=1,
                help="Exposición del medio natural, condiciones climáticas, etc."
            )
            
            orientation = st.select_slider(
                "🧭 Orientación en el Itinerario",
                options=[1, 2, 3, 4, 5],
                value=2,
                help="Dificultad para orientarse en el terreno"
            )
        
        with mcol2:
            difficulty = st.select_slider(
                "⛰️ Dificultad en el Desplazamiento",
                options=[1, 2, 3, 4, 5],
                value=2,
                help="Dificultad física del terreno"
            )
            
            effort = st.select_slider(
                "💪 Esfuerzo Necesario",
                options=[1, 2, 3, 4, 5],
                value=2,
                help="Exigencia física acumulada"
            )
    
    # Visualización de la matriz MIDE
    st.markdown("### Matriz MIDE")
    
    mide_values = [severity, orientation, difficulty, effort]
    mide_labels = ["SEVERIDAD DEL\nMEDIO", "ORIENTACIÓN", "DIFICULTAD\nDESPLAZAMIENTO", "ESFUERZO\nNECESARIO"]
    mide_colors = []
    
    for val in mide_values:
        if val <= 2:
            mide_colors.append(COLOR_PRIMARY)
        elif val == 3:
            mide_colors.append(COLOR_SECONDARY)
        else:
            mide_colors.append("#E74C3C")
    
    # Mostrar grid de valores
    grid_cols = st.columns(4)
    for i, (col, val, label, color) in enumerate(zip(grid_cols, mide_values, mide_labels, mide_colors)):
        with col:
            st.markdown(f"""
            <div style="
                border: 3px solid {color};
                border-radius: 10px;
                padding: 15px;
                text-align: center;
                background-color: white;
            ">
                <div style="
                    font-size: 28px;
                    font-weight: bold;
                    color: {color};
                ">{val}</div>
                <div style="
                    font-size: 10px;
                    color: #333;
                    margin-top: 5px;
                ">{label.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
    
    return {
        'severity': severity,
        'orientation': orientation,
        'difficulty': difficulty,
        'effort': effort
    }


def tab_info_adicional():
    """Pestaña de información adicional"""
    st.markdown('<div class="section-header">ℹ️ Información Adicional</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recomendaciones de Seguridad")
        recommendations_text = st.text_area(
            "Recomendaciones (una por línea)",
            value="Evitar realizar la ruta en los meses más calurosos del verano debido al calor intenso.\nPrestar especial atención al cruzar la carretera CM-1003.\nLlevar agua suficiente y protección solar.\nConsultar la previsión meteorológica antes de iniciar la ruta.",
            height=120,
            help="Advertencias y consejos de seguridad para los excursionistas"
        )
        
        recommendations = [r.strip() for r in recommendations_text.split('\n') if r.strip()]
        
        st.subheader("Contactos de Interés")
        emergency = st.text_input(
            "Teléfono de Emergencias",
            value="112"
        )
        
        phone_park = st.text_input(
            "Teléfono del Parque",
            value="949 88 53 00"
        )
    
    with col2:
        st.subheader("Información Web")
        web_url = st.text_input(
            "URL del Sendero (para código QR)",
            value="http://areasprotegidas.castillalamancha.es"
        )
        
        st.info("📱 Se generará automáticamente un código QR que enlazará a esta URL")
        
        st.subheader("Logos Institucionales (Opcional)")
        logo_left = st.file_uploader(
            "Logo Izquierda (opcional)",
            type=['png', 'jpg', 'jpeg'],
            help="Logo institucional que aparecerá en la esquina izquierda de la cabecera"
        )
        
        logo_right = st.file_uploader(
            "Logo Derecha (opcional)",
            type=['png', 'jpg', 'jpeg'],
            help="Logo del parque natural o entidad colaboradora"
        )
    
    return {
        'recommendations': recommendations,
        'emergency': emergency,
        'phone': phone_park,
        'web': web_url,
        'logo_left': logo_left,
        'logo_right': logo_right
    }


def generate_pdf(data):
    """Genera el PDF y lo guarda en un archivo temporal"""
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp()
    output_path = os.path.join(temp_dir, f"topoguia_{data['route_code'].replace(' ', '_')}.pdf")
    
    # Procesar imágenes
    processed_images = {}
    
    for key in ['panoramic', 'map', 'profile']:
        if data['images'].get(key):
            img_ext = data['images'][key].name.split('.')[-1]
            img_path = os.path.join(temp_dir, f"{key}.{img_ext}")
            with open(img_path, 'wb') as f:
                f.write(data['images'][key].getvalue())
            processed_images[key] = img_path
        else:
            processed_images[key] = None
    
    # Procesar logos
    logo_paths = {}
    if data['additional'].get('logo_left'):
        logo_paths['logo_left'] = data['additional']['logo_left']
    if data['additional'].get('logo_right'):
        logo_paths['logo_right'] = data['additional']['logo_right']
    
    # Preparar datos completos para el PDF
    pdf_data = {
        # Datos básicos
        'route_code': data['basic']['route_code'],
        'route_name': data['basic']['route_name'],
        'route_type': data['basic']['route_type'],
        'paragraphs': data['basic']['paragraphs'],
        
        # Imágenes
        'panoramic_image': processed_images['panoramic'],
        'map_image': processed_images['map'],
        'profile_image': processed_images['profile'],
        'landmarks': parse_landmarks(data['images'].get('landmarks', '')),
        
        # Métricas
        'distance': data['metrics']['distance'],
        'time': data['metrics']['time'],
        'elevation_up': data['metrics']['elevation_up'],
        'elevation_down': data['metrics']['elevation_down'],
        
        # MIDE
        'mide': data['mide'],
        
        # Info adicional
        'recommendations': data['additional']['recommendations'],
        'emergency': data['additional']['emergency'],
        'phone': data['additional']['phone'],
        'web': data['additional']['web'],
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # Generar PDF
    create_topoguide_pdf(output_path, pdf_data)
    
    return output_path


def parse_landmarks(landmarks_text):
    """Parsea el texto de landmarks y devuelve una lista de diccionarios"""
    landmarks = []
    if landmarks_text:
        lines = landmarks_text.strip().split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if line:
                # Distribuir horizontalmente
                x_pos = 20 + (i * 25) if i < 3 else 50
                landmarks.append({
                    'text': line,
                    'x': x_pos,
                    'y': 35,
                    'type': 'landmark'
                })
    return landmarks


def main():
    """Función principal de la aplicación"""
    apply_custom_css()
    
    # Título principal
    st.title("🥾 TopoGuide Pro Generator")
    st.markdown(f"""
    <div style="
        background-color: {COLOR_PRIMARY};
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 30px;
    ">
        <h2 style="color: white; margin: 0;">Generador Profesional de Topoguías de Senderismo</h2>
        <p style="margin: 10px 0 0 0; opacity: 0.9;">
            Crea documentos PDF de 2 páginas replicando el diseño oficial de las topoguías 
            de Castilla-La Mancha con información técnica, mapas y descripciones.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        st.markdown("---")
        
        st.markdown("### Colores Corporativos")
        st.color_picker("Color Primario", COLOR_PRIMARY, disabled=True)
        st.caption("Verde corporativo (#007A33)")
        st.color_picker("Color Secundario", COLOR_SECONDARY, disabled=True)
        st.caption("Amarillo/Ocre (#E8AF2E)")
        
        st.markdown("---")
        st.markdown("### Acerca de")
        st.markdown("""
        **TopoGuide Pro Generator** permite crear topoguías de senderismo profesionales 
        listas para imprimir o distribuir digitalmente.
        
        Diseño optimizado para formato A4 Landscape (horizontal).
        """)
    
    # Sistema de pestañas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍 Datos Básicos",
        "📸 Imágenes", 
        "📏 Métricas",
        "⚠️ MIDE",
        "ℹ️ Info Adicional"
    ])
    
    # Recopilar datos de cada pestaña
    with tab1:
        basic_data = tab_datos_basicos()
    
    with tab2:
        image_data = tab_imagenes()
    
    with tab3:
        metrics_data = tab_metricas()
    
    with tab4:
        mide_data = tab_mide()
    
    with tab5:
        additional_data = tab_info_adicional()
    
    # Botón de generación
    st.markdown("---")
    
    col_gen1, col_gen2, col_gen3 = st.columns([1, 2, 1])
    
    with col_gen2:
        generate_btn = st.button(
            "🖨️ GENERAR TOPOGUÍA PDF",
            use_container_width=True,
            type="primary"
        )
    
    # Procesar generación del PDF
    if generate_btn:
        st.markdown("---")
        
        # Validar datos mínimos requeridos
        if not basic_data['route_code'] or not basic_data['route_name']:
            st.error("❌ Error: Debes completar al menos el código y nombre de la ruta.")
        else:
            with st.spinner("Generando topoguía PDF..."):
                # Recopilar todos los datos
                all_data = {
                    'basic': basic_data,
                    'images': image_data,
                    'metrics': metrics_data,
                    'mide': mide_data,
                    'additional': additional_data
                }
                
                try:
                    # Generar PDF
                    pdf_path = generate_pdf(all_data)
                    
                    # Leer archivo para mostrarlo
                    with open(pdf_path, 'rb') as pdf_file:
                        pdf_bytes = pdf_file.read()
                    
                    # Mostrar mensaje de éxito
                    st.markdown(f"""
                    <div class="success-message">
                        <strong>✅ Topoguía generada correctamente:</strong><br>
                        Ruta: {basic_data['route_code']} - {basic_data['route_name']}<br>
                        Tipo: {basic_data['route_type']} | Distancia: {metrics_data['distance']} | Tiempo: {metrics_data['time']}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón de descarga
                    st.download_button(
                        label="📥 Descargar PDF de la Topoguía",
                        data=pdf_bytes,
                        file_name=f"Topoguia_{basic_data['route_code'].replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        type="primary"
                    )
                    
                    # Mostrar vista previa del PDF
                    with st.expander("👁️ Vista Previa del PDF"):
                        st.info("El PDF se ha generado correctamente. Descárgalo para ver el documento completo.")
                    
                except Exception as e:
                    st.error(f"❌ Error al generar el PDF: {str(e)}")
                    st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align: center; color: #666; font-size: 12px;">
        TopoGuide Pro Generator | Generador de Topoguías de Senderismo<br>
        Diseñado según las especificaciones del formato oficial de Castilla-La Mancha
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
