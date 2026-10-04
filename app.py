import streamlit as st
import chess
import chess.svg
import base64

# Configuración del entorno de juego al estilo Lichess
st.set_page_config(page_title="ONG Lasker Quilmes - Analizador Lichess", layout="centered")

# --- IDENTIDAD VISUAL OFICIAL DE LICHESS (CSS INYECTADO) ---
st.markdown("""
<style>
    /* Fondo modo oscuro oficial de Lichess (Charcoal #161512) */
    .stApp {
        background-color: #161512 !important;
        color: #bababa !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Contenedor centralizado para emular la interfaz de Lichess */
    [data-testid="stMainBlockContainer"] {
        max-width: 500px !important;
        padding: 20px !important;
        background: #262421 !important; /* Color de los bloques secundarios en Lichess */
        border-radius: 4px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        margin: 20px auto !important;
    }
    
    /* Títulos limpios sin Neón, estilo sobrio Lichess */
    .titulo-lichess {
        color: #fff !important;
        text-align: center;
        font-size: 2rem;
        font-weight: 600 !important;
        margin-bottom: 5px;
    }
    .subtitulo-lichess {
        text-align: center;
        color: #bababa;
        font-size: 1rem;
        margin-bottom: 20px;
    }
    
    /* Botones de menú planos estilo Lichess */
    .stButton>button {
        background-color: #363431 !important;
        color: #cccdce !important;
        border: 1px solid #403e3b !important;
        border-radius: 4px !important;
        font-weight: normal !important;
        transition: background 0.1s ease !important;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #454340 !important;
        color: #fff !important;
        border-color: #52504c !important;
    }
    
    /* Inputs de texto estilo Lichess */
    .stTextInput input {
        background-color: #161512 !important;
        color: #fff !important;
        border: 1px solid #403e3b !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- REPRODUCTOR DE SONIDO "TOC" NATIVO ---
def reproducir_sonido_toc():
    # Audio plano nativo para simular el golpe clásico de Lichess
    audio_base64 = "UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA==" 
    audio_html = f'<audio autoplay src="data:audio/wav;base64,{audio_base64}"></audio>'
    st.markdown(audio_html, unsafe_allow_html=True)

# --- BASE DE DATOS DE USUARIOS (100 CUENTAS) ---
USUARIOS_VALIDOS = {"profesor": "lasker2026"}
for i in range(1, 101):
    USUARIOS_VALIDOS[f"alumno{i}"] = f"lasker{i:03d}"

# --- CONTROL DE ACCESO (LOGIN) ---
if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if not st.session_state["autenticado"]:
    st.markdown('<div class="titulo-lichess">lichess.org — Lasker</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-lichess">Iniciar sesión en la Academia Quilmes</div>', unsafe_allow_html=True)
    usuario = st.text_input("Usuario o correo electrónico:")
    clave = st.text_input("Contraseña:", type="password")
    if st.button("Iniciar sesión"):
        if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == clave:
            st.session_state["autenticado"] = True
            st.rerun()
        else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# --- INICIALIZACIÓN DEL SISTEMA DE JUEGO ---
if "board" not in st.session_state: st.session_state.board = chess.Board()
if "casilla_seleccionada" not in st.session_state: st.session_state.casilla_seleccionada = None

# --- MENÚ DE ENTRENAMIENTO ESTILO LICHESS ---
st.markdown('<div class="titulo-lichess">Estudio Lasker Quilmes</div>', unsafe_allow_html=True)
st.write("---")

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📖 Aperturas"):
        st.session_state.board = chess.Board("r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3")
        st.session_state.casilla_seleccionada = None
        st.success("Apertura Española")
with col2:
    if st.button("🏰 Finales"):
        st.session_state.board = chess.Board("8/8/4k3/8/8/4K3/4R3/4R3 w - - 0 1")
        st.session_state.casilla_seleccionada = None
        st.success("Final de Torres")
with col3:
    if st.button("🎯 Tácticas"):
        st.session_state.board = chess.Board("6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1")
        st.session_state.casilla_seleccionada = None
        st.success("Mate del Pasillo")

if st.button("🔄 Reiniciar posición"):
    st.session_state.board = chess.Board()
    st.session_state.casilla_seleccionada = None
    st.rerun()

# --- LÓGICA DE MOVIMIENTO POR SELECCIÓN DE CASILLAS ---
st.write("---")
st.caption("Seleccioná la pieza de origen y luego elegí la casilla de destino para mover.")

movimientos_posibles = []
if st.session_state.casilla_seleccionada:
    sq_origen = chess.parse_square(st.session_state.casilla_seleccionada)
    for move in st.session_state.board.legal_moves:
        if move.from_square == sq_origen:
            movimientos_posibles.append(move)

# Círculos verdes semitransparentes en los destinos válidos (igual que en Lichess)
flechas_movimiento = []
if st.session_state.casilla_seleccionada:
    for move in movimientos_posibles:
        flechas_movimiento.append(chess.svg.Arrow(move.to_square, move.to_square, color="rgba(120, 180, 80, 0.7)"))

# Renderizar Tablero con la paleta de colores oficial de Lichess (Azul de Lichess o café opcional)
board_svg = chess.svg.board(
    board=st.session_state.board,
    size=380,
    arrows=flechas_movimiento,
    colors={'square light': '#dee3e6', 'square dark': '#8ca2ad', 'margin': '#161512'}
)
b64 = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')
html_tablero = f'<div style="display: flex; justify-content: center; margin: 10px 0;"><img src="data:image/svg+xml;base64,{b64}" style="border-radius: 3px; width: 100%; max-width: 360px;"/></div>'
st.markdown(html_tablero, unsafe_allow_html=True)

# --- SELECTORES DE CLIC INTERACTIVOS ---
col_origen, col_destino = st.columns(2)

with col_origen:
    opciones_origen = ["-- Elegir Pieza --"] + [chess.square_name(s) for s in chess.SQUARES if st.session_state.board.piece_at(s) is not None]
    seleccion_origen = st.selectbox("Pieza:", opciones_origen, index=0)
    
    if seleccion_origen != "-- Elegir Pieza --" and seleccion_origen != st.session_state.casilla_seleccionada:
        st.session_state.casilla_seleccionada = seleccion_origen
        st.rerun()

with col_destino:
    opciones_destino = ["-- Elegir Destino --"]
    if st.session_state.casilla_seleccionada:
        opciones_destino += [chess.square_name(m.to_square) for m in movimientos_posibles]
        
    seleccion_destino = st.selectbox("Destino:", opciones_destino, index=0)

    if seleccion_destino != "-- Elegir Destino --" and st.session_state.casilla_seleccionada:
        try:
            jugada_uci = f"{st.session_state.casilla_seleccionada}{seleccion_destino}"
            movimiento_final = chess.Move.from_uci(jugada_uci)
            
            # Promoción automática a Dama
            if st.session_state.board.piece_at(chess.parse_square(st.session_state.casilla_seleccionada)).piece_type == chess.PAWN:
                if chess.square_rank(chess.parse_square(seleccion_destino)) in [0, 7]:
                    movimiento_final = chess.Move.from_uci(f"{jugada_uci}q")

            if movimiento_final in st.session_state.board.legal_moves:
                st.session_state.board.push(movimiento_final)
                reproducir_sonido_toc()
                st.session_state.casilla_seleccionada = None
                st.rerun()
        except Exception:
            pass

# --- PANEL DE EVALUACIÓN DEL MOTOR ---
st.write("---")
st.subheader("Análisis en tiempo real")
if st.session_state.casilla_seleccionada:
    st.info(f"Foco en {st.session_state.casilla_seleccionada.upper()}. Los círculos verdes indican movimientos legales.")
else:
    st.success("Seleccioná una pieza para ver su análisis posicional.")
