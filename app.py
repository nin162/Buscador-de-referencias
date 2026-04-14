import streamlit as st
import feedparser
import datetime
import re

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Portal QFB", page_icon="🔬", layout="wide")

# CSS para mejorar la apariencia
st.markdown("""
    <style>
    .stMetric { background-color: #1e2129; padding: 15px; border-radius: 10px; border: 1px solid #3d414b; }
    .stContainer { border: 1px solid #3d414b; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Función para limpiar etiquetas como <i> de los títulos
def limpiar_html(texto):
    return re.sub('<[^<]+?>', '', texto)

st.title("🔬 Portal de Vigilancia Microbiológica")
st.caption("Filtro inteligente de literatura científica")

# --- 2. BARRA LATERAL ---
with st.sidebar:
    st.header("Configuración")
    fuentes_dict = {
        "Nature Microbiology": "https://www.nature.com/nmicrobiol.rss",
        "CDC - EID Journal": "https://wwwnc.cdc.gov/eid/rss/current.xml",
        "ScienceDaily": "https://www.sciencedaily.com/rss/plants_animals/microbiology.xml",
        "BioMed Central": "https://microbiomejournal.biomedcentral.com/articles/most-recent/rss.xml",
        "Biología Molecular México": "https://invdes.com.mx/category/ciencia/biotecnologia/feed/"
    }
    seleccion = st.multiselect("Fuentes:", options=list(fuentes_dict.keys()), default=list(fuentes_dict.keys())[:2])
    cantidad = st.slider("Noticias por fuente:", 1, 10, 3)
    busqueda = st.text_input("🔍 Filtrar por palabra:")

# --- 3. LÓGICA DE PROCESAMIENTO (UNA SOLA VEZ) ---
noticias_totales = []
titulos_vistos = set()

if seleccion:
    for fuente in seleccion:
        feed = feedparser.parse(fuentes_dict[fuente])
        for entry in feed.entries[:cantidad]:
            # Limpiamos el título para evitar duplicados y errores de <i>
            titulo_puro = limpiar_html(entry.title)
            id_titulo = titulo_puro.strip().lower()
            
            if id_titulo not in titulos_vistos:
                if busqueda.lower() in id_titulo:
                    # Detección de acceso
                    meta = (entry.get('description', '') + entry.title).lower()
                    es_abierto = any(p in meta for p in ["open access", "full text", "free", "oa", "creative commons"]) or \
                                 fuente in ["CDC - EID Journal", "BioMed Central"]
                    
                    noticias_totales.append({
                        "titulo": titulo_puro,
                        "link": entry.link,
                        "fuente": fuente,
                        "fecha": entry.get('published', 'N/A'),
                        "acceso": "Abierto" if es_abierto else "Suscripción/Duda"
                    })
                    titulos_vistos.add(id_titulo)

# --- 4. INTERFAZ VISUAL ---
c1, c2, c3 = st.columns(3)
c1.metric("Noticias Únicas", len(noticias_totales))
c2.metric("Fuentes", len(seleccion))
c3.metric("Actualizado", datetime.datetime.now().strftime("%H:%M"))

st.divider()

if not noticias_totales:
    st.info("No hay noticias nuevas para mostrar.")
else:
    cols = st.columns(2)
    for i, n in enumerate(noticias_totales):
        with cols[i % 2]:
            with st.container(border=True):
                head1, head2 = st.columns([2, 1])
                head1.markdown(f"**{n['fuente']}**")
                if n["acceso"] == "Abierto":
                    head2.success("🔓 Gratis")
                else:
                    head2.warning("🔒 Paga/Duda")
                
                # Usamos markdown para que el título se vea grande y limpio
                st.markdown(f"#### {n['titulo']}")
                st.caption(f"🗓 {n['fecha']}")
                st.link_button("Leer Artículo Completo", n['link'])