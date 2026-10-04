import streamlit as st
import chess
import chess.svg
import base64
import time
from streamlit_server_state import server_state, server_state_lock

# Configuración del entorno competitivo
st.set_page_config(page_title="Lasker Quilmes - Arena Blitz", layout="centered")

# --- ESTILO GRÁFICO OFICIAL DE LICHESS ---
st.markdown("""
<style>
    .stApp { background-color: #161512 !important; color: #bababa !important; }
    [data-testid="stMainBlockContainer"] {
        max-width: 500px !important; padding: 20px !important;
        background: #262421 !important; border-radius: 4px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 15px auto !important;
    }
    .titulo-lichess { color: #fff !important; text-align: center; font-size: 1.8rem; font-weight: 600 !important; }
    .reloj-contenedor {
        display: flex; justify-content: space-between; margin: 10px 0;
    }
    .reloj-caja {
        background: #161512; padding: 10px 20px; border-radius: 3px;
        font-family: monospace; font-size: 1.6rem; font-weight: bold; border: 1px solid #403e3b;
    }
    .reloj-activo { color: #fff !important; border-color: #78b450 !important; background: #1e2c18 !important; }
    .reloj-inactivo { color: #8a8a8a; }
    .stButton>button {
        background-color: #363431 !important; color: #fff !important;
        border: 1px solid #403e3b !important; border-radius: 4px !important; width: 100%;
    }
    .stButton>button:hover { background-color: #454340 !important; border-color: #52504c !important; }
    .chat-box { background: #161512; padding: 8px; border-radius: 4px; max-height: 120px; overflow-y: auto; border: 1px solid #403e3b; margin-bottom: 8px; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

def reproducir_sonido():
    audio_b64 = "UklGRigAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQQAAAAAAA=="
    st.markdown(f'<audio autoplay src="data:audio/wav;base64,{audio_b64}"></audio>', unsafe_allow_html=True)

# --- BASE DE DATOS DE USUARIOS ---
USUARIOS_VALIDOS = {"profesor": "lasker2026"}
for i in range(1, 101): USUARIOS_VALIDOS[f"alumno{i}"] = f"lasker{i:03d}"

if "autenticado" not in st.session_state: st.session_state["autenticado"] = False
if "usuario_activo" not in st.session_state: st.session_state["usuario_activo"] = ""

if not st.session_state["autenticado"]:
    st.markdown('<div class="titulo-lichess">lichess.org — Lasker Arena</div>', unsafe_allow_html=True)
    u = st.text_input("👤 Usuario:")
    c = st.text_input("🔑 Contraseña:", type="password")
    if st.button("Iniciar Sesión"):
        if u in USUARIOS_VALIDOS and USUARIOS_VALIDOS[u] == c:
            st.session_state["autenticado"] = True
            st.session_state["usuario_activo"] = u.upper()
            st.rerun()
        else: st.error("❌ Credenciales incorrectas.")
    st.stop()

# --- GESTIÓN DE SALAS MULTIJUGADOR EN EL SERVIDOR ---
st.markdown('<div class="titulo-lichess">⚔️ Arena Blitz: 5+2 ⚔️</div>', unsafe_allow_html=True)
st.caption("ONG Lasker Quilmes - Modalidad Multijugador en Tiempo Real")

sala_id = st.text_input("🎮 Introduce el código de la Sala (Ej: sala1, claseA):", placeholder="Escribe el nombre de la sala...")

if not sala_id:
    st.warning("⚠️ Ingresa un código de sala para conectarte con tu compañero.")
    st.stop()

# Inicializar la estructura de la sala en la memoria global del servidor
with server_state_lock[sala_id]:
    if sala_id not in server_state:
        server_state[sala_id] = {
            "fen": chess.STARTING_FEN,
            "blancas": "",
            "negras": "",
            "turno": "W",
            "tiempo_blancas": 300.0,
            "tiempo_negras": 300.0,
            "last_update": time.time(),
            "chat": [],
            "partida_iniciada": False
        }

sala = server_state[sala_id]

# --- ASIGNACIÓN DE BANDOS (BLANCAS / NEGRAS) ---
col_b, col_n = st.columns(2)
with col_b:
    if sala["blancas"] == "":
        if st.button("⬜ Jugar con Blancas"):
            with server_state_lock[sala_id]:
                sala["blancas"] = st.session_state["usuario_activo"]
            st.rerun()
    else:
        st.write(f"⬜ Blancas: **{sala['blancas']}**")

with col_n:
    if sala["negras"] == "":
        if st.button("⬛ Jugar con Negras"):
            with server_state_lock[sala_id]:
                if sala["blancas"] != st.session_state["usuario_activo"]:
                    sala["negras"] = st.session_state["usuario_activo"]
            st.rerun()
    else:
        st.write(f"⬛ Negras: **{sala['negras']}**")

# Activar partida cuando ambos se sientan
if sala["blancas"] and sala["negras"] and not sala["partida_iniciada"]:
    with server_state_lock[sala_id]:
        sala["partida_iniciada"] = True
        sala["last_update"] = time.time()

# --- ACTUALIZACIÓN DE RELOJES EN TIEMPO REAL (LÓGICA BLITZ 5+2) ---
if sala["partida_iniciada"]:
    now = time.time()
    elapsed = now - sala["last_update"]
    
    with server_state_lock[sala_id]:
        sala["last_update"] = now
        if sala["turno"] == "W":
            sala["tiempo_blancas"] = max(0.0, sala["tiempo_blancas"] - elapsed)
        else:
            sala["tiempo_negras"] = max(0.0, sala["tiempo_negras"] - elapsed)

# Formatear el tiempo de los relojes (Minutos:Segundos)
def formatear_tiempo(t):
    mins = int(t // 60)
    secs = int(t % 60)
    return f"{mins:02d}:{secs:02d}"

cl_b_css = "reloj-activo" if sala["turno"] == "W" else "reloj-inactivo"
cl_n_css = "reloj-activo" if sala["turno"] == "B" else "reloj-inactivo"

# Mostrar Relojes Oficiales
st.markdown(f"""
<div class="reloj-contenedor">
    <div class="reloj-caja {cl_b_css}">⬜ BLANCAS: {formatear_tiempo(sala['tiempo_blancas'])}</div>
    <div class="reloj-caja {cl_n_css}">⬛ NEGRAS: {formatear_tiempo(sala['tiempo_negras'])}</div>
</div>
""", unsafe_allow_html=True)

if sala["tiempo_blancas"] <= 0: st.error("🏁 ¡Tiempo agotado! Ganan las Negras. 🎉"); st.stop()
if sala["tiempo_negras"] <= 0: st.error("🏁 ¡Tiempo agotado! Ganan las Blancas. 🎉"); st.stop()

# --- TABLERO COMPARTIDO E INTERACTIVO ---
board = chess.Board(sala["fen"])

coordenadas = [chess.square_name(s) for s in chess.SQUARES]
c_pulsada = st.selectbox("📍 Selecciona tu movimiento (Origen / Destino):", ["-- Tocar Casilla --"] + coordenadas)

# Validar que el jugador solo mueva en su propio turno
puedo_mover = False
if sala["turno"] == "W" and st.session_state["usuario_activo"] == sala["blancas"]: puedo_mover = True
if sala["turno"] == "B" and st.session_state["usuario_activo"] == sala["negras"]: puedo_mover = True

if c_pulsada != "-- Tocar Casilla --":
    if not puedo_mover:
        st.warning("⏳ Espera el turno de tu rival o asegúrate de haber reclamado un bando.")
    else:
        sq = chess.parse_square(c_pulsada)
        if st.session_state.get("origen_blitz") is None:
            if board.piece_at(sq) is not None:
                st.session_state["origen_blitz"] = c_pulsada
                st.rerun()
        else:
            orig = st.session_state["origen_blitz"]
            try:
                movimiento = chess.Move.from_uci(f"{orig}{c_pulsada}")
                # Auto-coronación escolar
                if board.piece_at(chess.parse_square(orig)).piece_type == chess.PAWN:
                    if chess.square_rank(chess.parse_square(c_pulsada)) in:
                        movimiento = chess.Move.from_uci(f"{orig}{c_pulsada}q")
                
                if movimiento in board.legal_moves:
                    board.push(movimiento)
                    reproducir_sonido()
                    
                    with server_state_lock[sala_id]:
                        sala["fen"] = board.fen()
                        # Aplicar incremento oficial Lichess (+2 segundos) e invertir turno
                        if sala["turno"] == "W":
                            sala["tiempo_blancas"] += 2.0
                            sala["turno"] = "B"
                        else:
                            sala["tiempo_negras"] += 2.0
                            sala["turno"] = "W"
                        sala["last_update"] = time.time()
                        
                    st.session_state["origen_blitz"] = None
                    st.rerun()
                else:
                    st.session_state["origen_blitz"] = None
                    st.rerun()
            except:
                st.session_state["origen_blitz"] = None
                st.rerun()

# Renderizar el SVG oficial
board_svg = chess.svg.board(board=board, size=380, colors={'square light': '#dee3e6', 'square dark': '#8ca2ad', 'margin': '#161512'})
b64 = base64.b64encode(board_svg.encode('utf-8')).decode('utf-8')
st.markdown(f'<div style="display:flex; justify-content:center; margin:10px 0;"><img src="data:image/svg+xml;base64,{b64}" style="width:100%; max-width:360px; border-radius:3px;"/></div>', unsafe_allow_html=True)

# Botón de reinicio de emergencia
if st.button("🔄 Reiniciar Partida en esta Sala"):
    with server_state_lock[sala_id]:
        sala["fen"] = chess.STARTING_FEN
        sala["turno"] = "W"
        sala["tiempo_blancas"] = 300.0
        sala["tiempo_negras"] = 300.0
        sala["partida_iniciada"] = False
        sala["blancas"] = ""
        sala["negras"] = ""
    st.rerun()

# --- 💬 CHAT DE LA SALA ---
st.write("---")
texto_chat = ""
for m in sala["chat"]: texto_chat += f"<b>{m['user']}:</b> {m['text']}<br>"
st.markdown(f'<div class="chat-box">{texto_chat if texto_chat else "<i>Chat de la sala activo...</i>"}</div>', unsafe_allow_html=True)

n_msg = st.text_input("💬 Mensaje para tu rival:", key="chat_blitz")
if st.button("Enviar"):
    if n_msg.strip():
        with server_state_lock[sala_id]:
            sala["chat"].append({"user": st.session_state["usuario_activo"], "text": n_msg})
        st.rerun()

# Auto-refresco de pantalla para sincronizar los relojes cada segundo
time.sleep(1.0)
st.rerun()
