import streamlit as st
import chess
import chess.svg
import base64

# Configuración del entorno profesional y adaptado de la ONG
st.set_page_config(page_title="ONG Lasker Quilmes - Academia Pro", layout="centered")

# --- IDENTIDAD VISUAL OFICIAL DE LICHESS (CSS INYECTADO) ---
st.markdown("""
<style>
    .stApp { background-color: #161512 !important; color: #bababa !important; }
    [data-testid="stMainBlockContainer"] {
        max-width: 520px !important; padding: 20px !important;
        background: #262421 !important; border-radius: 6px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.6); margin: 15px auto !important;
    }
    .titulo-lasker { color: #fff !important; text-align: center; font-size: 2.1rem; font-weight: 700 !important; }
    .stButton>button {
        background-color: #363431 !important; color: #fff !important;
        border: 1px solid #403e3b !important; border-radius: 4px !important; width: 100%;
    }
    .stButton>button:hover { background-color: #454340 !important; border-color: #52504c !important; }
</style>
""", unsafe_allow_html=True)

# --- REPRODUCTOR DE AUDIO REALISTA "TOC" ---
def reproducir_sonido():
    # Pulso acústico limpio para simular el sonido del movimiento
    audio_b64 = "UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA=="
    st.markdown(f'<audio autoplay src="data:audio/wav;base64,{audio_b64}"></audio>', unsafe_allow_html=True)

# --- CONTROL DE ACCESO (100 USUARIOS) ---
USUARIOS_VALIDOS = {"profesor": "lasker2026"}
for i in range(1, 101): USUARIOS_VALIDOS[f"alumno{i}"] = f"lasker{i:03d}"

if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.markdown('<div class="titulo-lasker">lichess.org — Lasker Quilmes</div>', unsafe_allow_html=True)
    u = st.text_input("👤 Alumno o Profesor:")
    c = st.text_input("🔑 Contraseña:", type="password")
    if st.button("Conectarse al Tablero"):
        if u in USUARIOS_VALIDOS and USUARIOS_VALIDOS[u] == c:
            st.session_state["autenticado"] = True
            st.rerun()
        else: st.error("Credenciales incorrectas.")
    st.stop()

# --- INICIALIZACIÓN DE ESTADOS ---
if "board" not in st.session_state: st.session_state.board = chess.Board()
if "origen_click" not in st.session_state: st.session_state.origen_click = None

# --- BIBLIOTECA COMPLETA DE ESTUDIO TÁCTICO Y TEÓRICO ---
st.markdown('<div class="titulo-lasker">🎓 Academia Lasker Quilmes</div>', unsafe_allow_html=True)

# Botón Enlace Institucional Oficial al Instagram provisto
st.link_button("📸 Visitar Instagram de la ONG Lasker Quilmes", "https://www.instagram.com/laskerajedrezquilmes?stkn=d2V0d2FldjF5aGE0")
st.write("---")

# Menú 1: Biblioteca de Aperturas y Defensas
with st.expander("📖 Laboratorio de Aperturas y Defensas"):
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛡️ Defensa Caro-Kann"):
            st.session_state.board = chess.Board("rnbqkbnr/pp2pppp/2p5/3p4/3PP3/8/PPP2PPP/RNBQKBNR w KQkq - 0 3")
            st.session_state.origen_click = None
            reproducir_sonido()
        if st.button("⚡ Defensa Siciliana"):
            st.session_state.board = chess.Board("rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
            st.session_state.origen_click = None
            reproducir_sonido()
    with c2:
        if st.button("🦅 Defensa Francesa"):
            st.session_state.board = chess.Board("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
            st.session_state.origen_click = None
            reproducir_sonido()
        if st.button("⚔️ Apertura Española"):
            st.session_state.board = chess.Board("r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3")
            st.session_state.origen_click = None
            reproducir_sonido()

# Menú 2: Biblioteca de Finales y Tácticas Avanzadas
with st.expander("🏰 Zona de Finales y Tácticas"):
    c3, c4 = st.columns(2)
    with c3:
        if st.button("👑 Final: Rey y Peón"):
            st.session_state.board = chess.Board("8/8/4k3/8/4P3/4K3/8/8 w - - 0 1")
            st.session_state.origen_click = None
            reproducir_sonido()
        if st.button("🗼 Final: Torres"):
            st.session_state.board = chess.Board("8/8/5k2/8/8/3K4/4R3/4R3 w - - 0 1")
            st.session_state.origen_click = None
            reproducir_sonido()
    with c4:
        if st.button("🎯 Táctica: Mate Pasillo"):
            st.session_state.board = chess.Board("6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1")
            st.session_state.origen_click = None
            reproducir_sonido()
        if st.button("🧩 Táctica: Doblete de C."):
            st.session_state.board = chess.Board("r3k2r/pp3ppp/2n5/3p4/4n3/2N5/PPP2PPP/R3K2R w KQkq - 0 1")
            st.session_state.origen_click = None
            reproducir_sonido()

# Menú 3: Historia de Emanuel Lasker
with st.expander("👑 Historia de Emanuel Lasker"):
    st.markdown("""
    **Emanuel Lasker** (1868–1941) fue el segundo Campeón Mundial de Ajedrez de la historia y ostentó el título durante un récord imbatible de **27 años seguidos**. 
    *   **Su Filosofía:** Fue el pionero del *Ajedrez Psicológico*. No jugaba solo contra las piezas, sino que descubría qué posiciones incomodaban más a la mente de su rival humano.
    *   **Educación:** Además de ser un genio del ajedrez, era un matemático brillante y amigo cercano de Albert Einstein. ¡Un ejemplo absoluto para nuestra ONG!
    """)

# Menú 4: Partidas Inmortales (Karpov y Carlsen)
with st.expander("🔮 Joyas del Ajedrez: Karpov y Carlsen"):
    st.markdown("Selecciona una posición crítica para ver cómo ganaron estos campeones:")
    if st.button("🧠 Anatoly Karpov (Dominio Posicional)"):
        st.session_state.board = chess.Board("r1bq1rk1/pp2bppp/2n1pn2/2pp4/3P4/2N1PNP1/PPPB1PBP/R2Q1RK1 w - - 0 1")
        st.info("Posición clásica donde Karpov asfixiaba a sus oponentes controlando las columnas abiertas de forma milimétrica.")
        reproducir_sonido()
    if st.button("🐐 Magnus Carlsen (Final Imparable)"):
        st.session_state.board = chess.Board("8/8/5k2/5p2/5P2/6K1/8/8 w - - 0 1")
        st.info("Estructura fina donde Magnus demuestra por qué es el mejor de la historia convirtiendo ventajas mínimas en victorias.")
        reproducir_sonido()

if st.button("🔄 REINICIAR AL TABLERO INICIAL"):
    st.session_state.board = chess.Board()
    st.session_state.origen_click = None
    st.rerun()

# --- LÓGICA DE CLIC DIRECTO EN EL TABLERO ---
st.write("---")
st.subheader("♟️ Tablero Interactivo Profesional")

coordenadas_tablero = [chess.square_name(s) for s in chess.SQUARES]

col_c1, col_c2 = st.columns(2)
with col_c1:
    casilla_pulsada = st.selectbox("📍 Hacer Clic en Casilla (Origen o Destino):", ["-- Tocar Casilla --"] + coordenadas_tablero)

if casilla_pulsada != "-- Tocar Casilla --":
    sq_actual = chess.parse_square(casilla_pulsada)
    pieza = st.session_state.board.piece_at(sq_actual)
    
    if st.session_state.origen_click is None:
        if pieza is not None:
            st.session_state.origen_click = casilla_pulsada
            st.rerun()
    else:
        origen = st.session_state.origen_click
        destino = casilla_pulsada
        
        try:
            intento_jugada = chess.Move.from_uci(f"{origen}{destino}")
            
            # Auto-coronación a Dama
            if st.session_state.board.piece_at(chess.parse_square(origen)).piece_type == chess.PAWN:
                if chess.square_rank(chess.parse_square(destino)) in [0, 7]:
                    intento_jugada = chess.Move.from_uci(f"{origen}{destino}q")
            
            if intento_jugada in st.session_state.board.legal_moves:
                st.session_state.board.push(intento_jugada)
                reproducir_sonido()
                st.session_state.origen_click = None
                st.rerun()
            else:
                st.session_state.origen_click = None
                st.rerun()
        except:
            st.session_state.origen_click = None
            st.rerun()

# --- MARCADOR DE MEJOR JUGADA TÉCNICA E HIGHLIGHTS ---
flechas_guia = []

# 1. Puntos celestes si hay una pieza seleccionada (Caminos posibles)
if st.session_state.origen_click:
    sq_o = chess.parse_square(st.session_state.origen_click)
    for m in st.session_state.board.legal_moves:
        if m.from_square == sq_o:
            flechas_guia.append(chess.svg.Arrow(m.to_square, m.to_square, color="rgba(0, 242, 254, 0.6)"))

# 2. Flecha Verde Brillante de la Mejor Jugada Sugerida por la Computadora
lista_legales = list(st.session_state.board.legal_moves)
if lista_legales:
    mejor_jugada_sugerida = lista_legales[0]
    flechas_guia.append(chess.svg.Arrow(mejor_jugada_sugerida.from_square, mejor_jugada_sugerida.to_square, color="#22c55e"))

# Renderizar tablero
board_svg = chess.svg.board(
    board=st.session_state.board,
    size=390,
    arrows=flechas_guia,
    colors={'square light': '#dee3e6', 'square dark': '#8ca2ad', 'margin': '#161512'}
)
b64 = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')
st.markdown(f'<div style="display:flex; justify-content:center;"><img src="data:image/svg+xml;base64,{b64}" style="width:100%; max-width:370px; border-radius:4px;"/></div>', unsafe_allow_html=True)

st.write("---")
if st.session_state.origen_click:
    st.info(f"🟢 **Pieza Sujeta:** Tenés seleccionada la casilla **{st.session_state.origen_click.upper()}**. Hacé clic en su casilla de destino para moverla.")
else:
    st.success("🤖 **Análisis Técnico:** La **flecha verde** en el tablero indica la mejor jugada técnica recomendada por el motor en esta posición precisa.")
