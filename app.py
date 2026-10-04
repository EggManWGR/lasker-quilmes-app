import streamlit as st
import chess
import chess.svg
import base64

# Configuración premium del espacio de juego
st.set_page_config(page_title="ONG Lasker Quilmes - Portal Gamer", layout="centered")

# --- INTERFAZ ULTRA-ATRAYENTE Y DIVERTIDA (CSS INYECTADO) ---
st.markdown("""
<style>
    /* Fondo espacial en movimiento constante */
    .stApp {
        background: linear-gradient(-45deg, #0b0f19, #1e1b4b, #431407, #0b0f19);
        background-size: 400% 400%;
        animation: gradient 10s ease infinite;
        color: #f8fafc !important;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Letras Neón estilo Videojuego */
    .titulo-gamer {
        color: #00f2fe !important;
        text-shadow: 0 0 10px #00f2fe, 0 0 30px #00f2fe;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 900 !important;
        letter-spacing: 1px;
    }
    .subtitulo-gamer {
        text-align: center;
        color: #f43f5e;
        font-weight: bold;
        text-shadow: 0 0 8px rgba(244, 63, 94, 0.6);
        font-size: 1.2rem;
        margin-bottom: 20px;
    }
    
    /* Contenedores con luces de neón */
    .stTextInput, .stButton, div[data-testid="stNotification"] {
        background: rgba(15, 23, 42, 0.75) !important;
        border: 2px solid #00f2fe !important;
        border-radius: 16px !important;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.2);
    }
    
    /* Botones Interactivos que se agrandan al pasar el mouse */
    .stButton>button {
        background: linear-gradient(135deg, #f43f5e 0%, #ca8a04 100%) !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        transition: all 0.2s ease-in-out !important;
    }
    .stButton>button:hover {
        transform: scale(1.06) rotate(1deg);
        box-shadow: 0 0 20px #f43f5e;
    }
</style>
""", unsafe_allow_html=True)

# --- GENERADOR AUTOMÁTICO DE 100 USUARIOS GAMER ---
USUARIOS_VALIDOS = {"profesor": "lasker2026"} 
for i in range(1, 101):
    USUARIOS_VALIDOS[f"alumno{i}"] = f"lasker{i:03d}"

# --- TEORÍA DE APERTURAS DIVERTIDAS ---
APERTURAS = {
    "e2e4 e7e5 g1f3 b8c6 f1b5": "⚔️ ¡APERTURA ESPAÑOLA! Estás usando la estrategia de los campeones del mundo.",
    "e2e4 c7c5": "⚡ ¡DEFENSA SICILIANA! Alerta de combate táctico. ¡Máxima adrenalina!",
    "d2d4 d7d5 c2c4": "👑 ¡GAMBITO DE DAMA! Sacrificio inteligente para dominar el mapa.",
    "e2e4 e7e5 g1f3 d7d6": "🛡️ ¡DEFENSA PHILIDOR! Bloqueo defensivo activado. ¡Inquebrantable!"
}

# --- PANTALLA DE LOGUEO DE ALUMNOS ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown('<div class="titulo-gamer">🎮 LASKER QUILMES</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitulo-gamer">⚡ Batalla de Mentes - Modo Estudio ⚡</div>', unsafe_allow_html=True)
    
    # Icono animado de corona de rey
    st.markdown('<div style="text-align:center; margin-bottom:15px;"><img src="https://icons8.com" width="85" style="filter:drop-shadow(0 0 15px #f43f5e);"/></div>', unsafe_allow_html=True)
    
    usuario = st.text_input("👤 TU USUARIO DE ALUMNO (Ej: alumno1):")
    clave = st.text_input("🔑 TU CLAVE SECRETA:", type="password")
    
    if st.button("🚀 ENTRAR AL SIMULADOR"):
        if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == clave:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("❌ Código erróneo. ¡Pídele tus coordenadas de acceso al profesor!")
    st.stop()

# --- INTERFAZ DEL TABLERO DE JUEGO ACTIVADO ---
st.markdown('<div class="titulo-gamer">🧠 MODO ENTRENAMIENTO</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#00f2fe; font-weight:bold;">📍 Academia Virtual ONG Lasker</p>', unsafe_allow_html=True)

if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "historial_movimientos" not in st.session_state:
    st.session_state.historial_movimientos = []

if st.button("🔄 REINICIAR MAPA DE JUEGO"):
    st.session_state.board = chess.Board()
    st.session_state.historial_movimientos = []
    st.rerun()

# Lógica del detector de estrategia
historial_str = " ".join(st.session_state.historial_movimientos)
apertura_detectada = "🪐 Campo de batalla libre. ¡Crea una estrategia única!"
for jugadas, nombre_apertura in APERTURAS.items():
    if historial_str.startswith(jugadas):
        apertura_detectada = nombre_apertura

st.info(f"{apertura_detectada}")

# Renderizar tablero neón (Azul Eléctrico y Blanco Puro)
board_svg = chess.svg.board(
    board=st.session_state.board, 
    size=420,
    colors={'square light': '#ffffff', 'square dark': '#1d4ed8', 'margin': '#0b0f19'}
)
b64 = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')
html_tablero = f'<div style="display: flex; justify-content: center; margin: 15px 0;"><img src="data:image/svg+xml;base64,{b64}" style="border: 4px solid #f43f5e; border-radius: 12px; box-shadow: 0 0 30px rgba(244,63,94,0.6); transform: rotate(0deg);"/></div>'
st.markdown(html_tablero, unsafe_allow_html=True)

# Barra de energía simulada
st.write("🔋 **Poder de cálculo del motor:**")
st.progress(100)

# Entrada de comandos
movimiento_usuario = st.text_input("🎯 Tu movimiento rápido (Ej: e4, Nf3, d5):", key="move_input", placeholder="Escribe aquí y presiona Enter...")

if movimiento_usuario:
    try:
        move = st.session_state.board.parse_san(movimiento_usuario)
        st.session_state.board.push(move)
        st.session_state.historial_movimientos.append(move.uci())
        st.rerun()
    except ValueError:
        st.error("⚠️ ¡Movimiento inválido! El sistema no reconoce esa jugada. ¡Revisa tu estrategia!")

# Mentor Gamer Integrado
st.subheader("🤖 Consejos de tu Coach de Inteligencia Artificial")
if not st.session_state.board.is_game_over():
    if st.session_state.historial_movimientos:
        ultima_jugada = st.session_state.historial_movimientos[-1]
        if "e4" in ultima_jugada or "d4" in ultima_jugada:
            st.success("🏆 **¡Nivel Pro!** Has conquistado el centro del tablero. Tus piezas obtienen bonificación de espacio.")
        elif "f3" in ultima_jugada or "c3" in ultima_jugada:
            st.success("🐴 **¡Despliegue Táctico!** Tus caballos saltan a la acción para proteger al rey. ¡Buen trabajo!")
        else:
            st.warning("🔮 **Evolución Posicional:** Estás armando una red silenciosa. ¡Analiza bien el contraataque del oponente!")
else:
    st.error("🏁 **¡PARTIDA FINALIZADA!** Lograron el objetivo. Analicen los movimientos clave antes de iniciar otra partida.")
