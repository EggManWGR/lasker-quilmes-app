import streamlit as st
import chess
import time

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN Y AUTENTICACIÓN
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Lasker Quilmes Chess", layout="wide", page_icon="♟️")

# Generar credenciales de alumno1 a alumno100
USERS = {f"alumno{i}": f"lasker{i}" for i in range(1, 101)}

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("♟️ Lasker Quilmes Chess - Iniciar Sesión")
    col1, col2 = st.columns(2)
    with col1:
        username = st.text_input("Usuario (ej. alumno1):")
        password = st.text_input("Contraseña:", type="password")
        if st.button("Ingresar"):
            if username in USERS and USERS[username] == password:
                st.session_state.user = username
                st.success(f"¡Bienvenido, {username}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")
    st.stop()

# -----------------------------------------------------------------------------
# 2. GESTIÓN DE SALAS Y ESTADO GLOBAL DE PARTIDAS
# -----------------------------------------------------------------------------
if "games" not in st.session_state:
    # Estructura: room_id -> { fen, white, black, moves, is_private }
    st.session_state.games = {}

st.sidebar.title(f"👤 {st.session_state.user}")
if st.sidebar.button("Cerrar Sesión"):
    st.session_state.user = None
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("🚪 Salas de Juego")

# Crear Nueva Sala
with st.sidebar.expander("➕ Crear Nueva Sala"):
    new_room_id = st.text_input("Nombre de la Sala:", key="new_room").strip()
    is_private = st.checkbox("Sala Privada")
    color_pref = st.selectbox("Jugar con:", ["Blancas", "Negras", "Aleatorio"])
    if st.button("Crear Sala"):
        if not new_room_id:
            st.warning("Escribe un nombre para la sala.")
        elif new_room_id in st.session_state.games:
            st.error("Esa sala ya existe.")
        else:
            white_player = st.session_state.user if color_pref != "Negras" else None
            black_player = st.session_state.user if color_pref == "Negras" else None
            st.session_state.games[new_room_id] = {
                "fen": chess.STARTING_FEN,
                "white": white_player,
                "black": black_player,
                "moves": [],
                "is_private": is_private,
                "last_update": time.time()
            }
            st.session_state.current_room = new_room_id
            st.rerun()

# Unirse a Sala Privada por Código
with st.sidebar.expander("🔑 Unirse por Código"):
    join_code = st.text_input("Código de Sala Privada:").strip()
    if st.button("Entrar a Sala Privada"):
        if join_code in st.session_state.games:
            st.session_state.current_room = join_code
            st.rerun()
        else:
            st.error("Sala no encontrada.")

# Lista de Salas Públicas
st.sidebar.subheader("🌐 Salas Públicas")
public_rooms = [r for r, data in st.session_state.games.items() if not data.get("is_private")]

if public_rooms:
    for r_id in public_rooms:
        game_data = st.session_state.games[r_id]
        status = f"({game_data['white'] or 'Libre'} vs {game_data['black'] or 'Libre'})"
        if st.sidebar.button(f"Unirse: {r_id} {status}", key=f"btn_{r_id}"):
            st.session_state.current_room = r_id
            st.rerun()
else:
    st.sidebar.caption("No hay salas públicas abiertas.")

# -----------------------------------------------------------------------------
# 3. INTERFAZ PRINCIPAL DE JUEGO
# -----------------------------------------------------------------------------
if "current_room" not in st.session_state or st.session_state.current_room not in st.session_state.games:
    st.title("♟️ Lasker Quilmes Chess")
    st.info("Selecciona o crea una sala en la barra lateral para empezar a jugar.")
    st.stop()

room_id = st.session_state.current_room
game = st.session_state.games[room_id]
board = chess.Board(game["fen"])

# Asignación automática de asientos
current_user = st.session_state.user
if game["white"] is None and game["black"] != current_user:
    game["white"] = current_user
elif game["black"] is None and game["white"] != current_user:
    game["black"] = current_user

# Procesar movimientos enviados desde la interfaz
query_params = st.query_params
if "move" in query_params:
    move_san_or_uci = query_params["move"]
    try:
        move = board.parse_san(move_san_or_uci) if move_san_or_uci in [board.san(m) for m in board.legal_moves] else chess.Move.from_uci(move_san_or_uci)
        if move in board.legal_moves:
            # Verificar turno de jugador
            is_white_turn = board.turn == chess.WHITE
            if (is_white_turn and current_user == game["white"]) or (not is_white_turn and current_user == game["black"]):
                board.push(move)
                game["fen"] = board.fen()
                game["moves"].append(move.uci())
                game["last_update"] = time.time()
    except Exception:
        pass
    st.query_params.clear()
    st.rerun()

# -----------------------------------------------------------------------------
# 4. DISPOSICIÓN ESTILO LICHESS
# -----------------------------------------------------------------------------
col_left, col_board, col_right = st.columns([1, 2, 1])

with col_left:
    st.markdown(f"### Sala: `{room_id}`")
    st.write(f"⚪ **Blancas:** {game['white'] or 'Esperando...'}")
    st.write(f"⚫ **Negras:** {game['black'] or 'Esperando...'}")
    st.markdown("---")
    
    # Determinación de orientación del tablero
    orientation = "white"
    if current_user == game["black"]:
        orientation = "black"
    
    st.caption(f"Jugando como: **{current_user}**")
    if st.button("🔄 Actualizar Tablero"):
        st.rerun()

# Componente HTML con Chessboard.js + Chess.js estilo Lichess
with col_board:
    fen = board.fen()
    
    # Determinar si el usuario actual tiene el turno
    is_my_turn = False
    if board.turn == chess.WHITE and current_user == game["white"]:
        is_my_turn = True
    elif board.turn == chess.BLACK and current_user == game["black"]:
        is_my_turn = True

    chessboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.css">
        <script src="https://code.jquery.com/jquery-3.5.1.min.min.js"></script>
        <script src="https://unpkg.com/@chrisoakman/chessboardjs@1.0.0/dist/chessboard-1.0.0.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.10.3/chess.min.js"></script>
        <style>
            body {{ background-color: #161512; color: #bababa; font-family: sans-serif; display: flex; justify-content: center; margin: 0; }}
            #board {{ width: 450px; margin-top: 10px; }}
            .highlight {{ background-color: #a9a9a9 !important; }}
        </style>
    </head>
    <body>
        <div id="board"></div>

        <script>
            var board = null;
            var game = new Chess('{fen}');
            var canMove = { 'true' if is_my_turn else 'false' };

            function onDragStart (source, piece, position, orientation) {{
                if (game.game_over() || !canMove) return false;
                if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
                    (game.turn() === 'b' && piece.search(/^w/) !== -1)) {{
                    return false;
                }}
            }}

            function onDrop (source, target) {{
                var move = game.move({{
                    from: source,
                    to: target,
                    promotion: 'q' // Promoción por defecto a Dama segun FIDE básica
                }});

                if (move === null) return 'snapback';

                // Enviar el movimiento a Streamlit
                window.parent.location.href = window.parent.location.pathname + '?move=' + move.from + move.to + (move.promotion ? move.promotion : '');
            }}

            function onSnapEnd () {{
                board.position(game.fen());
            }}

            var config = {{
                draggable: true,
                position: '{fen}',
                orientation: '{orientation}',
                onDragStart: onDragStart,
                onDrop: onDrop,
                onSnapEnd: onSnapEnd,
                pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{{piece}}.png'
            }};
            board = Chessboard('board', config);
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(chessboard_html, height=500)

with col_right:
    st.subheader("📊 Estado de la Partida")
    if board.is_checkmate():
        st.error("¡Jaque Mate!")
    elif board.is_stalemate():
        st.warning("Tablas por Ahogado.")
    elif board.is_check():
        st.warning("⚠️ ¡Jaque!")
    else:
        turn_text = "Blancas" if board.turn == chess.WHITE else "Negras"
        st.info(f"Turno de las **{turn_text}**")

    st.markdown("---")
    st.subheader("📜 Historial de Jugadas")
    moves_list = game["moves"]
    if moves_list:
        formatted_moves = []
        for i in range(0, len(moves_list), 2):
            w_move = moves_list[i]
            b_move = moves_list[i+1] if i+1 < len(moves_list) else ""
            formatted_moves.append(f"{i//2 + 1}. {w_move} {b_move}")
        st.text_area("Movimientos", "\n".join(formatted_moves), height=200)
    else:
        st.caption("Aún no se realizaron movimientos.")
