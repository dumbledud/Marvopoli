import streamlit as st
import random

# -----------------------------------------------------------------------------
# Helper: Initialize the Game Board
# -----------------------------------------------------------------------------
def init_board():
    """
    Create a board of 40 spaces arranged along the perimeter of a square.
    - Space 0 is "GO Bond" (starting position).
    - Next 9 spaces are themed (properties, chance, risk, etc.).
    - The remaining spaces are filled randomly from a selection of themes.
    """
    board = []
    # Space 0: GO Bond
    board.append({
        'name': 'GO Bond',
        'type': 'start',
        'description': 'Starting space. Each time you refuse the GO Bond, the VOM increases its traces (a symbolic penalty).'
    })
    
    # Thematic spaces for one side
    thematic_spaces = [
        {"name": "VOM Venture", "type": "property", "cost": 100, "connection_degree": 3},
        {"name": "Trail of Trials", "type": "chance", "description": "A twist of fate! Advance 2 spaces."},
        {"name": "Kim’s Crossroads", "type": "property", "cost": 150, "connection_degree": 2},
        {"name": "Council Conundrum", "type": "risk", "description": "Unexpected fines. Pay a $50 penalty."},
        {"name": "Zoning Zephyr", "type": "property", "cost": 120, "connection_degree": 4},
        {"name": "Corruption Corridor", "type": "property", "cost": 200, "connection_degree": 1},
        {"name": "Easement Error", "type": "chance", "description": "Legal challenge! Lose a turn."},
        {"name": "Trail Tussle", "type": "risk", "description": "Conflict over trail plans; pay a $50 penalty."},
        {"name": "Municipal Maze", "type": "property", "cost": 130, "connection_degree": 5},
        {"name": "Defamation Drive", "type": "property", "cost": 160, "connection_degree": 3},
    ]
    board.extend(thematic_spaces)
    
    # Additional themes to fill the board
    themes = [
        {"name": "Retaliation Road", "type": "property", "cost": 140, "connection_degree": 2},
        {"name": "Intimidation Intersection", "type": "risk", "description": "Threats abound! Pay a penalty between $75 and $200."},
        {"name": "Neighbor Nexus", "type": "property", "cost": 110, "connection_degree": 4},
        {"name": "Proxy Plaza", "type": "chance", "description": "Move forward 3 spaces."},
        {"name": "Legal Labyrinth", "type": "property", "cost": 180, "connection_degree": 2},
        {"name": "Complaint Court", "type": "risk", "description": "Legal fees! Pay a penalty between $75 and $200."},
        {"name": "Settlement Street", "type": "property", "cost": 160, "connection_degree": 3},
        {"name": "Dispute Drive", "type": "chance", "description": "Draw a card: Advance 2 spaces."},
        {"name": "Fines Fee Lane", "type": "risk", "description": "Ridiculous fine! Pay a penalty between $100 and $250."},
        {"name": "Appeal Avenue", "type": "property", "cost": 150, "connection_degree": 4},
    ]
    while len(board) < 40:
        board.append(random.choice(themes))
    return board

# -----------------------------------------------------------------------------
# Mapping function: Determine board index from grid coordinates
# -----------------------------------------------------------------------------
def get_board_index(row, col):
    """
    For an 11x11 grid:
      - Top row (row 0): index = col (col 0 to 10)
      - Right column (col 10, row 1–9): index = 10 + row (11 to 19)
      - Bottom row (row 10): index = 20 + (10 – col) (col 10→index 20, col 0→index 30)
      - Left column (col 0, row 9–1): index = 31 + (9 – row) (row 9→index 31, row 1→index 39)
    Returns the board index if (row, col) is on the perimeter, otherwise returns None.
    """
    if row == 0:
        return col  # 0 to 10
    elif col == 10 and 1 <= row <= 9:
        return 10 + row  # 11 to 19
    elif row == 10:
        return 20 + (10 - col)  # col10->20, col0->30
    elif col == 0 and 1 <= row <= 9:
        return 31 + (9 - row)  # row9->31, row1->39
    else:
        return None

# -----------------------------------------------------------------------------
# Initialize or Reset Game State in Session
# -----------------------------------------------------------------------------
if 'players' not in st.session_state:
    st.session_state.players = [
        {'name': 'Player 1', 'position': 0, 'money': 1500, 'properties': []},
        {'name': 'Player 2', 'position': 0, 'money': 1500, 'properties': []}
    ]
if 'current_turn' not in st.session_state:
    st.session_state.current_turn = 0
if 'board' not in st.session_state:
    st.session_state.board = init_board()
if 'message' not in st.session_state:
    st.session_state.message = ""
if 'game_over' not in st.session_state:
    st.session_state.game_over = False

# -----------------------------------------------------------------------------
# Check for Game Over
# -----------------------------------------------------------------------------
def check_game_over():
    # If any player's money is 0 or less, set game_over flag.
    for player in st.session_state.players:
        if player['money'] <= 0:
            st.session_state.message = f"Game over! {player['name']} is bankrupt."
            st.session_state.game_over = True
            break

# -----------------------------------------------------------------------------
# UI: Title and Player Status
# -----------------------------------------------------------------------------
st.title("VOM Monopoly: The GO Bond Edition (Streamlit Version)")
if st.session_state.game_over:
    st.error(st.session_state.message)
    st.button("Reset Game")  # Offer a reset button when game over.
    st.stop()

st.subheader(f"Current Turn: {st.session_state.players[st.session_state.current_turn]['name']}")
st.write("**Player Status:**")
for player in st.session_state.players:
    st.write(f"{player['name']} — Position: {player['position']}, Money: ${player['money']}, Properties: {player['properties']}")

# -----------------------------------------------------------------------------
# Action: Roll Dice Button
# -----------------------------------------------------------------------------
if st.button("Roll Dice"):
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    roll_value = die1 + die2
    current_turn = st.session_state.current_turn
    player = st.session_state.players[current_turn]
    board_length = len(st.session_state.board)
    
    # Update player's position
    player['position'] = (player['position'] + roll_value) % board_length
    current_space = st.session_state.board[player['position']]
    
    st.session_state.message = f"{player['name']} rolled {die1} and {die2} (total {roll_value}) and landed on '{current_space['name']}'."
    
    # Process space effect based on its type
    if current_space.get('type') == 'property' and 'owner' not in current_space:
        st.session_state.message += " This property is available for purchase."
    elif current_space.get('type') == 'chance':
        st.session_state.message += " Chance card: " + current_space.get('description', '')
    elif current_space.get('type') == 'risk':
        # Increase penalty severity and randomness
        penalty = random.choice([75, 100, 125, 150, 175, 200])
        player['money'] -= penalty
        st.session_state.message += f" Obstacle encountered! {player['name']} loses ${penalty}."
    elif current_space.get('type') == 'blessing':
        bonus = 100
        player['money'] += bonus
        st.session_state.message += f" Magical blessing! {player['name']} gains ${bonus}."
    
    st.session_state.players[current_turn] = player
    # Check if game is over before advancing turn.
    check_game_over()
    if not st.session_state.game_over:
        st.session_state.current_turn = (current_turn + 1) % len(st.session_state.players)
    try:
        st.experimental_rerun()
    except Exception:
        pass

st.write(st.session_state.message)

# -----------------------------------------------------------------------------
# Action: Buy Property Button
# -----------------------------------------------------------------------------
prev_turn = (st.session_state.current_turn - 1) % len(st.session_state.players)
current_player = st.session_state.players[prev_turn]
current_space = st.session_state.board[current_player['position']]

if current_space.get('type') == 'property' and 'owner' not in current_space:
    if st.button("Buy This Property"):
        cost = current_space.get('cost', 0)
        if current_player['money'] >= cost:
            current_player['money'] -= cost
            current_player['properties'].append(current_player['position'])
            current_space['owner'] = current_player['name']
            st.session_state.message = f"{current_player['name']} purchased '{current_space['name']}' for ${cost}."
        else:
            st.session_state.message = f"{current_player['name']} does not have enough money to buy '{current_space['name']}'."
        st.session_state.players[prev_turn] = current_player
        check_game_over()
        try:
            st.experimental_rerun()
        except Exception:
            pass

# -----------------------------------------------------------------------------
# Option: Reset Game
# -----------------------------------------------------------------------------
if st.button("Reset Game"):
    for key in ['players', 'current_turn', 'board', 'message', 'game_over']:
        if key in st.session_state:
            del st.session_state[key]
    try:
        st.experimental_rerun()
    except Exception:
        pass

# -----------------------------------------------------------------------------
# Display Interactive Board View Arranged Around a Square Perimeter
# -----------------------------------------------------------------------------
st.write("### Interactive Board View (Square Perimeter)")

# Add custom CSS to force uniform button sizes.
st.markdown("""
    <style>
    div.stButton > button {
         width: 100%;
         height: 100px;
         font-size: 0.8rem;
    }
    </style>
    """, unsafe_allow_html=True)

grid_size = 11  # 11x11 grid; border cells hold our 40 board spaces.
for row in range(grid_size):
    cols = st.columns([1]*grid_size)
    for col in range(grid_size):
        board_index = get_board_index(row, col)
        if board_index is not None:
            if cols[col].button(f"{board_index}: {st.session_state.board[board_index]['name']}", key=f"space_{row}_{col}"):
                st.info(
                    f"**Space {board_index}:** {st.session_state.board[board_index]['name']}\n"
                    f"Type: {st.session_state.board[board_index]['type']}\n"
                    f"Description: {st.session_state.board[board_index].get('description', 'N/A')}\n" +
                    (f"Cost: ${st.session_state.board[board_index].get('cost')}" if st.session_state.board[board_index].get('cost') else "")
                )
        else:
            cols[col].empty()
