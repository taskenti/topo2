# TopoGuide Pro Generator

## Descripción General

**TopoGuide Pro Generator** es una aplicación web desarrollada en Python que permite generar documentos PDF profesionales de dos páginas para rutas de senderismo. La aplicación replica el diseño oficial de las topoguías de Castilla-La Mancha, incluyendo información técnica, mapas topográficos, perfiles de elevación, datos MIDE y toda la información necesaria para los excursionistas.

Esta herramienta está diseñada para ser utilizada por oficinas de turismo, clubes de senderismo, técnicos ambientales, agentes forestales y cualquier persona interesada en crear documentación de calidad para rutas de senderismo.

---

## Características Principales

### Interfaz de Usuario

La aplicación ofrece una interfaz moderna e intuitiva organizada en cinco pestañas que permiten introducir todos los datos necesarios de forma estructurada:

- **Datos Básicos**: Código de ruta, nombre, tipo de recorrido y cuatro párrafos descriptivos que cubren introducción, descripción del itinerario, vegetación y fauna.
- **Imágenes**: Carga de imagen panorámica para la cabecera, mapa topográfico con traza y gráfico de perfil de elevación.
- **Métricas**: Distancia total, tiempo estimado, desniveles de subida y-bajada con cálculo automático del desnivel total.
- **Sistema MIDE**: Evaluación de cuatro criterios (severidad del medio, orientación, dificultad de desplazamiento y esfuerzo necesario) en escala del 1 al 5.
- **Información Adicional**: Recomendaciones de seguridad, contactos de emergencia, teléfono del parque, URL web para código QR y logos institucionales opcionales.

### Generación de PDF

El documento PDF generado contiene dos páginas en formato A4 horizontal con las siguientes características:

**Página 1 - Información General:**
- Cabecera institucional con logos (si se proporcionan)
- Título del sendero en verde corporativo con código oficial
- Imagen panorámica con etiquetas de paisaje
- Cuatro párrafos descriptivos justificados
- Panel de recomendaciones con viñetas

**Página 2 - Información Técnica:**
- Mapa topográfico grande con marcadores de ruta
- Perfil de elevación con etiquetas de puntos clave
- Ficha técnica con todos los datos numéricos
- Matriz visual MIDE con código de colores
- Panel de señalización, consejos y teléfonos
- Código QR automático enlazado a la URL proporcionada

### Diseño Profesional

El documento mantiene un diseño consistente con los siguientes elementos de identidad corporativa:

- Color primario verde corporativo (#007A33) para cabeceras, bordes y elementos destacados
- Color secundario ocre (#E8AF2E) para el perfil de elevación y viñetas
- Tipografía Sans-serif (Helvetica/Arial) con títulos en negrita
- Diseño limpio con bloques de texto justificados
- Uso intensivo de imágenes técnicas y espacios equilibrados

---

## Requisitos del Sistema

### Requisitos de Software

Para ejecutar la aplicación se necesitan los siguientes componentes:

- Python 3.8 o superior
- Sistema operativo: Windows, macOS o Linux
- Navegador web moderno (Chrome, Firefox, Edge, Safari)
- Al menos 100 MB de espacio libre en disco
- Conexión a internet recomendada para la primera instalación

### Dependencias de Python

Las siguientes bibliotecas de Python son necesarias para el funcionamiento de la aplicación:

- **streamlit** (versión 1.28.0 o superior): Framework principal de la aplicación web
- **reportlab** (versión 4.0.0 o superior): Generación de documentos PDF profesionales
- **qrcode** (versión 7.4.0 o superior): Generación de códigos QR
- **Pillow** (versión 10.0.0 o superior): Procesamiento de imágenes
- **pandas** (versión 2.0.0 o superior): Manejo de datos estructurados

---

## Instalación

### Método 1: Instalación desde Código Fuente

1. **Clonar o descargar el proyecto**

   Obtenga los archivos del proyecto y colóquelos en una carpeta de su elección:

   ```bash
   git clone <repositorio>
   cd topoguide-generator
   ```

2. **Crear entorno virtual (recomendado)**

   Es altamente recomendable utilizar un entorno virtual para aislar las dependencias:

   ```bash
   python -m venv venv
   source venv/bin/activate   # En Linux/macOS
   venv\Scripts\activate      # En Windows
   ```

3. **Instalar dependencias**

   Instale todas las bibliotecas necesarias mediante pip:

   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**

   Inicie el servidor de Streamlit:

   ```bash
   streamlit run app.py
   ```

5. **Acceder a la aplicación**

   Abra su navegador web y navegue a la dirección que aparece en la terminal, típicamente:

   ```
   http://localhost:8501
   ```

### Método 2: Instalación con pip

Si prefiere instalar las dependencias directamente:

```bash
pip install streamlit reportlab qrcode Pillow pandas
streamlit run app.py
```

---

## Manual de Uso

### Paso 1: Introducir Datos Básicos

En la primera pestaña, complete la información fundamental de la ruta:

1. Escriba el código oficial del sendero (ejemplo: PR-GU 08)
2. Introduzca el nombre completo de la ruta
3. Seleccione el tipo de recorrido (Circular, Lineal, Travesía, Ida y Vuelta)
4. Redacte los cuatro párrafos descriptivos siguiendo las indicaciones de ayuda

### Paso 2: Cargar Imágenes

En la pestaña de imágenes, suba los siguientes archivos:

- **Foto Panorámica**: Imagen de paisaje que aparecerá en la cabecera (formato JPG o PNG)
- **Mapa Topográfico**: Mapa de la zona con el trazado de la ruta marcado
- **Perfil de Elevación**: Gráfico que muestra la variación de altitud a lo largo del recorrido

Opcionalmente, puede añadir etiquetas a la imagen panorámica indicando nombres de picos y lugares visibles.

### Paso 3: Introducir Métricas

Complete los datos técnicos de la ruta:

- Distancia total en kilómetros
- Tiempo estimado de duración (horas y minutos)
- Desnivel acumulado de subida en metros
- Desnivel acumulado de bajada en metros

El sistema calculará automáticamente el desnivel total y mostrará un resumen visual.

### Paso 4: Evaluar con Sistema MIDE

Utilice los deslizadores para puntuar cada criterio del sistema MIDE:

- **Severidad del Medio** (1-5): Condiciones ambientales y exposición
- **Orientación** (1-5): Dificultad para orientarse en el terreno
- **Dificultad de Desplazamiento** (1-5): Complejidad física del itinerario
- **Esfuerzo Necesario** (1-5): Exigencia física acumulada

La aplicación muestra una matriz visual con código de colores según la puntuación.

### Paso 5: Completar Información Adicional

Finalice con los datos complementarios:

- Recomendaciones de seguridad para los excursionistas
- Teléfono de emergencias (por defecto: 112)
- Teléfono de contacto del parque natural
- URL web del sendero para generar el código QR
- Logos institucionales opcionales para la cabecera

### Paso 6: Generar el PDF

Haga clic en el botón "GENERAR TOPOGUÍA PDF" para crear el documento. Una vez generado:

1. Verá un mensaje de confirmación con los datos de la ruta
2. Descargue el archivo PDF mediante el botón de descarga
3. El archivo se nombrará automáticamente con el código de la ruta

---

## Estructura del Proyecto

```
topoguide-generator/
│
├── app.py                    # Aplicación Streamlit con interfaz de usuario
├── pdf_generator.py          # Módulo de generación de PDFs con ReportLab
├── requirements.txt          # Dependencias de Python
├── README.md                 # Documentación del proyecto
│
├── assets/                   # Carpeta para recursos (logos, iconos)
│   └── (archivos de recursos)
│
└── output/                   # Carpeta para PDFs generados (se crea automáticamente)
```

---

## Personalización

### Colores Corporativos

Si desea modificar los colores del documento PDF, edite las constantes en el archivo `pdf_generator.py`:

```python
# Colores corporativos
GREEN_PRIMARY = colors.HexColor("#007A33")  # Verde principal
OCHRE = colors.HexColor("#E8AF2E")          # Color secundario ocre
```

### Añadir Nuevos Campos

Para añadir campos adicionales al formulario o al PDF:

1. Añada el campo en la función correspondiente de `app.py`
2. Incluya el dato en el diccionario `pdf_data` de la función `generate_pdf`
3. Añada la lógica de dibujo en `pdf_generator.py` siguiendo el patrón existente

### Integración con Otros Sistemas

La función `create_topoguide_pdf` del módulo `pdf_generator.py` puede llamarse programáticamente desde otros scripts Python:

```python
from pdf_generator import create_topoguide_pdf

data = {
    'route_code': 'PR-GU 08',
    'route_name': 'Sendero Ejemplo',
    'distance': '10,5 km',
    'time': '3h 00m',
    # ... más datos
}

create_topoguide_pdf('mi_topoguia.pdf', data)
```

---

## Limitaciones y Consideraciones

### Limitaciones Actuales

- El tamaño máximo de imagen es de 5 MB por archivo
- El documento PDF está optimizado para formato A4 horizontal
- El código QR enlaza a una URL estática proporcionada
- No incluye base de datos para guardar múltiples rutas

### Mejoras Futuras

Las siguientes funcionalidades están previstas para versiones posteriores:

- Guardado de rutas en base de datos local
- Exportación a otros formatos (DOCX, HTML)
- Generación de perfiles de elevación desde datos GPX
- Múltiples plantillas de diseño
- Modo batch para generar múltiples topoguías
- Integración con servicios de mapas online

---

## Solución de Problemas

### Error: "No module named 'streamlit'"

Solucione instalando las dependencias:

```bash
pip install streamlit
```

### Error: "Permission denied" al generar PDF

Ejecute la aplicación con permisos de escritura en la carpeta destino o utilice la carpeta temporal automática.

### Imágenes no aparecen en el PDF

Verifique que las imágenes están en formatos admitidos (JPG, PNG) y no superan el tamaño máximo de 5 MB.

### PDF generado pero no se puede abrir

Asegúrese de que el proceso de generación заверши sin errores. Pruebe a regenerar el documento con menos imágenes.

---

## Licencia

Este proyecto está desarrollado para uso educativo y profesional. Konsulte la licencia específica para usos comerciales.

---

## Contacto y Soporte

Para consultas sobre el uso de la aplicación, reporte de errores o sugerencias de mejora, contacte con el equipo de desarrollo.

---

## Referencias

- Sistema MIDE: www.sendersdemencia.org/mide
- Especificaciones de topoguías oficiales de Castilla-La Mancha
- Documentación de Streamlit: docs.streamlit.io
- Documentación de ReportLab: www.reportlab.com/docs
