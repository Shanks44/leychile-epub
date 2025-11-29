import streamlit as st
import os
import tempfile
import zipfile
import io
from bcn_scraper import scrape_bcn_law
from epub_generator import generate_law_epub


st.set_page_config(
    page_title="Generador de eBooks - Leyes Chile",
    page_icon="📚",
    layout="centered"
)

st.title("Generador de eBooks de Leyes Chilenas")
st.markdown("Convierte leyes del sitio de la Biblioteca del Congreso Nacional (BCN) a formato ePub.")

st.markdown("---")

mode = st.radio(
    "Modo de procesamiento:",
    options=['single', 'batch'],
    format_func=lambda x: 'Ley individual' if x == 'single' else 'Multiples leyes (lote)',
    horizontal=True
)

if mode == 'single':
    st.subheader("Ingresa la URL de la ley")

    default_url = "https://www.bcn.cl/leychile/navegar?idNorma=30082&idVersion=2018-09-06&idParte="

    url = st.text_input(
        "URL de la ley en bcn.cl/leychile:",
        value=default_url,
        help="Copia y pega la URL completa de la ley desde el sitio de Ley Chile"
    )
else:
    st.subheader("Ingresa las URLs de las leyes")
    
    urls_text = st.text_area(
        "URLs de las leyes (una por linea):",
        value="https://www.bcn.cl/leychile/navegar?idNorma=30082\nhttps://www.bcn.cl/leychile/navegar?idNorma=61107",
        height=150,
        help="Ingresa una URL por linea. Puedes procesar hasta 10 leyes a la vez."
    )
    
    urls_list = [u.strip() for u in urls_text.strip().split('\n') if u.strip()]
    if len(urls_list) > 10:
        st.warning("Maximo 10 leyes por lote. Solo se procesaran las primeras 10.")
        urls_list = urls_list[:10]
    
    st.info(f"Leyes a procesar: {len(urls_list)}")

st.markdown("---")

if 'law_data' not in st.session_state:
    st.session_state.law_data = None
if 'epub_path' not in st.session_state:
    st.session_state.epub_path = None
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'batch_results' not in st.session_state:
    st.session_state.batch_results = None
if 'batch_zip' not in st.session_state:
    st.session_state.batch_zip = None

col1, col2 = st.columns(2)

with col1:
    generate_button = st.button("Generar ePub", type="primary", use_container_width=True)

with col2:
    if st.button("Limpiar", use_container_width=True):
        st.session_state.law_data = None
        st.session_state.epub_path = None
        st.session_state.processing = False
        st.session_state.batch_results = None
        st.session_state.batch_zip = None
        st.rerun()

if mode == 'single':
    if generate_button and url:
        if 'bcn.cl/leychile' not in url and 'leychile' not in url:
            st.error("Por favor, ingresa una URL valida del sitio bcn.cl/leychile")
        else:
            st.session_state.processing = True
            st.session_state.batch_results = None
            st.session_state.batch_zip = None
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress: float, message: str):
                progress_bar.progress(progress)
                status_text.text(message)
            
            try:
                update_progress(0.1, "Conectando con el sitio de Ley Chile...")
                
                law_data = scrape_bcn_law(url, update_progress)
                st.session_state.law_data = law_data
                
                update_progress(0.7, "Generando archivo ePub...")
                
                metadata = law_data.get('metadata', {})
                law_type = metadata.get('type', 'Ley')
                law_number = metadata.get('number', 'documento')
                filename = f"{law_type}_{law_number}.epub"
                
                temp_dir = tempfile.gettempdir()
                epub_path = os.path.join(temp_dir, filename)
                
                epub_path = generate_law_epub(law_data, epub_path)
                st.session_state.epub_path = epub_path
                
                update_progress(1.0, "Completado!")
                
                st.session_state.processing = False
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al procesar la ley: {str(e)}")
                st.session_state.processing = False

else:
    if generate_button and urls_list:
        invalid_urls = [u for u in urls_list if 'bcn.cl/leychile' not in u and 'leychile' not in u]
        if invalid_urls:
            st.error(f"Las siguientes URLs no son validas: {', '.join(invalid_urls[:3])}")
        else:
            st.session_state.processing = True
            st.session_state.law_data = None
            st.session_state.epub_path = None
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            batch_results = []
            temp_dir = tempfile.gettempdir()
            
            try:
                total_urls = len(urls_list)
                
                for i, batch_url in enumerate(urls_list):
                    base_progress = i / total_urls
                    step_progress = 1 / total_urls
                    
                    status_text.text(f"Procesando ley {i+1} de {total_urls}...")
                    progress_bar.progress(base_progress)
                    
                    try:
                        def batch_progress(p, msg):
                            overall = base_progress + (p * step_progress * 0.8)
                            progress_bar.progress(min(overall, 0.99))
                            status_text.text(f"Ley {i+1}/{total_urls}: {msg}")
                        
                        law_data = scrape_bcn_law(batch_url, batch_progress)
                        
                        metadata = law_data.get('metadata', {})
                        law_type = metadata.get('type', 'Ley')
                        law_number = metadata.get('number', 'documento')
                        filename = f"{law_type}_{law_number}.epub"
                        
                        epub_path = os.path.join(temp_dir, filename)
                        epub_path = generate_law_epub(law_data, epub_path)
                        
                        batch_results.append({
                            'success': True,
                            'url': batch_url,
                            'title': metadata.get('title', 'Sin titulo'),
                            'type': law_type,
                            'number': law_number,
                            'epub_path': epub_path,
                            'filename': filename
                        })
                        
                    except Exception as e:
                        batch_results.append({
                            'success': False,
                            'url': batch_url,
                            'error': str(e)
                        })
                
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    for result in batch_results:
                        if result['success'] and os.path.exists(result['epub_path']):
                            zip_file.write(result['epub_path'], result['filename'])
                
                zip_buffer.seek(0)
                st.session_state.batch_zip = zip_buffer.getvalue()
                st.session_state.batch_results = batch_results
                
                progress_bar.progress(1.0)
                status_text.text("Completado!")
                
                st.session_state.processing = False
                st.rerun()
                
            except Exception as e:
                st.error(f"Error en el procesamiento por lotes: {str(e)}")
                st.session_state.processing = False

if st.session_state.batch_results and st.session_state.batch_zip:
    successful = [r for r in st.session_state.batch_results if r['success']]
    failed = [r for r in st.session_state.batch_results if not r['success']]
    
    if successful:
        st.success(f"Se generaron {len(successful)} ePubs exitosamente!")
    if failed:
        st.warning(f"{len(failed)} leyes no pudieron ser procesadas.")
    
    st.subheader("Resultados del procesamiento por lotes")
    
    for result in st.session_state.batch_results:
        if result['success']:
            st.markdown(f"- {result['type']} {result['number']}: {result['title'][:60]}...")
        else:
            st.markdown(f"- Error: {result['url'][:50]}... - {result.get('error', 'Error desconocido')}")
    
    st.markdown("---")
    
    zip_size = len(st.session_state.batch_zip) / 1024
    
    st.download_button(
        label=f"Descargar todos los ePubs ({zip_size:.1f} KB)",
        data=st.session_state.batch_zip,
        file_name="leyes_chile.zip",
        mime="application/zip",
        type="primary",
        use_container_width=True
    )

elif st.session_state.law_data and st.session_state.epub_path:
    st.success("El ePub ha sido generado exitosamente!")
    
    metadata = st.session_state.law_data.get('metadata', {})
    
    st.subheader("Informacion de la Ley")
    
    law_type = metadata.get('type', '')
    law_number = metadata.get('number', '')
    if law_type and law_number:
        st.markdown(f"### {law_type} N° {law_number}")
    
    st.markdown(f"**Titulo:** {metadata.get('title', 'No disponible')}")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Organismo:** {metadata.get('organism', 'No disponible')}")
    with col2:
        source = metadata.get('source', '')
        if source:
            st.markdown(f"**Publicado en:** {source}")
    
    subjects = metadata.get('subjects', [])
    if subjects:
        unique_subjects = list(dict.fromkeys(subjects))[:5]
        st.markdown(f"**Materias:** {', '.join(unique_subjects)}")
    
    content = st.session_state.law_data.get('content', [])
    
    titulos = [item for item in content if item.get('type') == 'titulo']
    parrafos = [item for item in content if item.get('type') == 'parrafo']
    articulos = [item for item in content if item.get('type') == 'articulo']
    
    st.markdown("---")
    st.markdown("**Estadisticas del documento:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Titulos", len(titulos))
    with col2:
        st.metric("Parrafos", len(parrafos))
    with col3:
        st.metric("Articulos", len(articulos))
    
    st.markdown("---")
    
    if os.path.exists(st.session_state.epub_path):
        with open(st.session_state.epub_path, 'rb') as f:
            epub_data = f.read()
        
        file_size = len(epub_data) / 1024
        
        download_filename = f"{law_type}_{law_number}.epub"
        
        st.download_button(
            label=f"Descargar ePub ({file_size:.1f} KB)",
            data=epub_data,
            file_name=download_filename,
            mime="application/epub+zip",
            type="primary",
            use_container_width=True
        )
    
    with st.expander("Ver estructura del documento"):
        for item in content[:50]:
            item_type = item.get('type', '')
            if item_type == 'titulo':
                st.markdown(f"### {item.get('text', '')}")
            elif item_type == 'parrafo':
                st.markdown(f"**{item.get('text', '')}**")
            elif item_type == 'articulo':
                title = item.get('title', '')
                if title:
                    st.markdown(f"- {title}")
        
        if len(content) > 50:
            st.markdown(f"*...y {len(content) - 50} elementos mas*")

st.markdown("---")

with st.expander("Instrucciones de uso"):
    st.markdown("""
    ### Como usar esta herramienta
    
    1. **Busca la ley** en el sitio de [Ley Chile](https://www.bcn.cl/leychile/)
    2. **Copia la URL** completa de la pagina de la ley
    3. **Pega la URL** en el campo de arriba
    4. **Personaliza** el formato (opcional): tamano de fuente, espaciado, margenes
    5. **Haz clic en "Generar ePub"** y espera a que se procese
    6. **Descarga el archivo** ePub generado
    
    ### Caracteristicas del ePub
    
    - Portada profesional con informacion de la ley
    - Tabla de contenidos navegable
    - Hipervinculo internos entre articulos referenciados
    - Estructura jerarquica (titulos, parrafos, articulos)
    - Metadatos completos (organismo, materias, fuente)
    
    ### Formatos compatibles
    
    El archivo ePub puede ser leido en:
    - Kindle (convirtiendo con Calibre)
    - Kobo
    - Apple Books
    - Google Play Books
    - Cualquier lector de ePub
    
    ### Notas
    
    - El proceso puede tardar varios segundos dependiendo del tamano de la ley
    - Se preserva la estructura jerarquica completa de la ley
    - Las referencias cruzadas entre articulos se convierten en enlaces navegables
    """)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "Fuente de datos: Biblioteca del Congreso Nacional de Chile"
    "</div>",
    unsafe_allow_html=True
)
