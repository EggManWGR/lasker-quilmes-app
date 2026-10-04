import streamlit as st
import chess
import base64
import time
from streamlit_server_state import server_state, server_state_lock

# Configuración del entorno competitivo estilo Lichess Arena
st.set_page_config(page_title="Lasker Quilmes - Arena Blitz Drag", layout="centered")

# --- INTERFAZ PREMIUM (CSS INYECTADO) ---
st.markdown("""
<style>
    .stApp { background-color: #161512 !important; color: #bababa !important; }
    [data-testid="stMainBlockContainer"] {
        max-width: 500px !important; padding: 20px !important;
        background: #262421 !important; border-radius: 4px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.5); margin: 15px auto !important;
    }
    .titulo-lichess { color: #fff !important; text-align: center; font-size: 1.8rem; font-weight: 600 !important; }
    .reloj-contenedor { display: flex; justify-content: space-between; margin: 10px 0; }
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
    .chat-box { background: #161512; padding: 8px; border-radius: 4px; max-height: 120px; overflow-y: auto; border: 1px solid #403e3b; margin-bottom: 8px; font-size: 0.9rem; }
    
    /* Contenedor del Tablero Arrastrable */
    .contenedor-tablero {
        display: flex; justify-content: center; margin: 15px 0; width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- BASE DE DATOS DE USUARIOS (100 ALUMNOS) ---
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

# --- GESTIÓN DE SALAS MULTIJUGADOR ---
st.markdown('<div class="titulo-lichess">⚔️ Arena Blitz Drag: 5+2 ⚔️</div>', unsafe_allow_html=True)
sala_id = st.text_input("🎮 Código de la Sala:", placeholder="Ej: sala1")

if not sala_id:
    st.warning("⚠️ Ingresa un código de sala para conectarte con tu compañero.")
    st.stop()

with server_state_lock[sala_id]:
    if sala_id not in server_state:
        server_state[sala_id] = {
            "fen": chess.STARTING_FEN, "blancas": "", "negras": "", "turno": "W",
            "tiempo_blancas": 300.0, "tiempo_negras": 300.0, "last_update": time.time(),
            "chat": [], "partida_iniciada": False
        }

sala = server_state[sala_id]

# Asignación de bandos en la sala
col_b, col_n = st.columns(2)
with col_b:
    if sala["blancas"] == "":
        if st.button("⬜ Jugar con Blancas"):
            with server_state_lock[sala_id]: sala["blancas"] = st.session_state["usuario_activo"]
            st.rerun()
    else: st.write(f"⬜ Blancas: **{sala['blancas']}**")
with col_n:
    if sala["negras"] == "":
        if st.button("⬛ Jugar con Negras"):
            with server_state_lock[sala_id]:
                if sala["blancas"] != st.session_state["usuario_activo"]:
                    sala["negras"] = st.session_state["usuario_activo"]
            st.rerun()
    else: st.write(f"⬛ Negras: **{sala['negras']}**")

if sala["blancas"] and sala["negras"] and not sala["partida_iniciada"]:
    with server_state_lock[sala_id]:
        sala["partida_iniciada"] = True
        sala["last_update"] = time.time()

# Sistema de Control de Relojes
if sala["partida_iniciada"]:
    now = time.time()
    elapsed = now - sala["last_update"]
    with server_state_lock[sala_id]:
        sala["last_update"] = now
        if sala["turno"] == "W": sala["tiempo_blancas"] = max(0.0, sala["tiempo_blancas"] - elapsed)
        else: sala["tiempo_negras"] = max(0.0, sala["tiempo_negras"] - elapsed)

def formatear_tiempo(t):
    return f"{int(t // 60):02d}:{int(t % 60):02d}"

cl_b_css = "reloj-activo" if sala["turno"] == "W" else "reloj-inactivo"
cl_n_css = "reloj-activo" if sala["turno"] == "B" else "reloj-inactivo"

st.markdown(f"""
<div class="reloj-contenedor">
    <div class="reloj-caja {cl_b_css}">⬜ BLANCAS: {formatear_tiempo(sala['tiempo_blancas'])}</div>
    <div class="reloj-caja {cl_n_css}">⬛ NEGRAS: {formatear_tiempo(sala['tiempo_negras'])}</div>
</div>
""", unsafe_allow_html=True)

if sala["tiempo_blancas"] <= 0: st.error("🏁 ¡Tiempo agotado! Ganan las Negras. 🎉"); st.stop()
if sala["tiempo_negras"] <= 0: st.error("🏁 ¡Tiempo agotado! Ganan las Blancas. 🎉"); st.stop()

# --- CAPTURA DE JUGADAS DE INTERNET ---
puedo_mover = False
if sala["turno"] == "W" and st.session_state["usuario_activo"] == sala["blancas"]: puedo_mover = True
if sala["turno"] == "B" and st.session_state["usuario_activo"] == sala["negras"]: puedo_mover = True

jugada_recibida = st.query_params.get("move", None)
if jugada_recibida and puedo_mover:
    board_actual = chess.Board(sala["fen"])
    try:
        movimiento = chess.Move.from_uci(jugada_recibida)
        # Soporte para promociones automáticas
        if movimiento not in board_actual.legal_moves:
            movimiento_promo = chess.Move.from_uci(f"{jugada_recibida}q")
            if movimiento_promo in board_actual.legal_moves:
                movimiento = movimiento_promo

        if movimiento in board_actual.legal_moves:
            board_actual.push(movimiento)
            with server_state_lock[sala_id]:
                sala["fen"] = board_actual.fen()
                if sala["turno"] == "W":
                    sala["tiempo_blancas"] += 2.0
                    sala["turno"] = "B"
                else:
                    sala["tiempo_negras"] += 2.0
                    sala["turno"] = "W"
                sala["last_update"] = time.time()
            st.query_params.clear()
            st.rerun()
    except:
        pass

# --- INYECCIÓN COMPLETA DEL TABLERO ARRASTRABLE SIN FALLOS ---
orientacion_tablero = "black" if st.session_state["usuario_activo"] == sala["negras"] else "white"

html_drag_and_drop = f"""
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cloudflare.com">
    <script src="https://jquery.com"></script>
    <script src="https://cloudflare.com"></script>
    <script src="https://cloudflare.com"></script>
</head>
<body style="margin:0; background:#262421; display:flex; justify-content:center; align-items:center;">
    <div id="board_lasker" style="width: 340px;"></div>
    <audio id="audioMove" src="https://mixkit.co" preload="auto"></audio>
    <script>
        var game = new Chess("{sala['fen']}");
        var snd = document.getElementById("audioMove");

        function onDragStart (source, piece, position, orientation) {{
            if (game.game_over()) return false;
            if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
                (game.turn() === 'b' && piece.search(/^w/) !== -1)) {{
                return false;
            }}
        }}

        function onDrop (source, target) {{
            var move = game.move({{
                from: source,
                to: target,
                promotion: 'q'
            }});

            if (move === null) return 'snapback';
            
            try {{ snd.play(); }} catch(e) {{}}
            
            var uciMove = source + target;
            window.top.location.href = window.top.location.pathname + "?move=" + uciMove + "&sala=" + "{sala_id}";
        }}

        var config = {{
            draggable: true,
            position: "{sala['fen']}",
            orientation: "{orientacion_tablero}",
            onDragStart: onDragStart,
            onDrop: onDrop,
            pieceTheme: 'https://chessboardjs.com{{piece}}.png'
        }};
        Chessboard('board_lasker', config);
    </script>
</body>
</html>
"""

st.markdown('<div class="contenedor-tablero">', unsafe_allow_html=True)
st.components.v1.html(html_drag_and_drop, height=350, width=350)
st.markdown('</div>', unsafe_allow_html=True)

# Botón de reinicio de la sala
if st.button("🔄 Reiniciar Partida en esta Sala"):
    with server_state_lock[sala_id]:
        sala["fen"] = chess.STARTING_FEN
        sala["turno"] = "W"
        sala["tiempo_blancas"] = 300.0
        sala["tiempo_negras"] = 300.0
        sala["partida_iniciada"] = False
        sala["blancas"] = ""
        sala["negras"] = ""
    st.query_params.clear()
    st.rerun()

# --- CHAT COMPARTIDO ---
st.write("---")
texto_chat = ""
for m in sala["chat"]: texto_chat += f"<b>{m['user']}:</b> {m['text']}<br>"
st.markdown(f'<div class="chat-box">{texto_chat if texto_chat else "<i>Chat activo...</i>"}</div>', unsafe_allow_html=True)

n_msg = st.text_input("💬 Mensaje para tu rival:", key="chat_blitz")
if st.button("Enviar"):
    if n_msg.strip():
        with server_state_lock[sala_id]: sala["chat"].append({"user": st.session_state["usuario_activo"], "text": n_msg})
        st.rerun()

