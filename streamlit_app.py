import streamlit as st
import random

# -----------------------------------------------------------------------------
# Helper: Initialize the Game Board
# -----------------------------------------------------------------------------
def init_board():
    """
    Create a board of 40 spaces arranged as a square.
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
    
    # A set of thematic spaces for one side
    thematic_spaces = [
        {"name": "VOM Venture", "type": "property", "cost": 100, "connection_degree": 3},
        {"name": "Trail of Trials", "type": "chance", "description": "A twist of fate! Advance 2 spaces."},
        {"name": "Kim’s Crossroads", "type": "property", "cost": 150, "connection_degree": 2},
        {"name": "Council Conundrum", "type": "risk", "description": "Unexpected fines for unnecessary trail spending. Pay $50 penalty."},
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
        {"name": "Intimidation Intersection", "type": "risk", "description": "Threats abound! Pay a $50 penalty."},
        {"name": "Neighbor Nexus", "type": "property", "cost": 110, "connection_degree": 4},
        {"name": "Proxy Plaza", "type": "chance", "description": "Move forward 3 spaces."},
        {"name": "Legal Labyrinth", "type": "property", "cost": 180, "connection_degree": 2},
        {"name": "Complaint Court", "type": "risk", "description": "Legal fees! Pay $75."},
        {"name": "Settlement Street", "type": "property", "cost": 160, "connection_degree": 3},
        {"name": "Dispute Drive", "type": "chance", "description": "Draw a card: Advance 2 spaces."},
        {"name": "Fines Fee Lane", "type": "risk", "description": "Pay a $100 fine."},
        {"name": "Appeal Avenue", "type": "property", "cost": 150, "connection_degree": 4},
    ]
    while len(board) < 40:
        board.append(random.choice(themes))
    return board

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

# -----------------------------------------------------------------------------
# UI: Title and Player Status
# -----------------------------------------------------------------------------
st.title("VOM Monopoly: The GO Bond Edition (Streamlit Version)")
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
        penalty = 50
        # Special handling for specific obstacles can be added here (e.g., skip turn)
        player['money'] -= penalty
        st.session_state.message += f" Obstacle encountered! {player['name']} loses ${penalty}."
    elif current_space.get('type') == 'blessing':
        bonus = 100
        player['money'] += bonus
        st.session_state.message += f" Magical blessing! {player['name']} gains ${bonus}."
    
    # Update the player and advance turn
    st.session_state.players[current_turn] = player
    st.session_state.current_turn = (current_turn + 1) % len(st.session_state.players)
    st.experimental_rerun()

st.write(st.session_state.message)

# -----------------------------------------------------------------------------
# Action: Buy Property Button
# -----------------------------------------------------------------------------
# The buyer is the player who rolled in the previous turn
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
        st.experimental_rerun()

# -----------------------------------------------------------------------------
# Option: Reset Game
# -----------------------------------------------------------------------------
if st.button("Reset Game"):
    for key in ['players', 'current_turn', 'board', 'message']:
        if key in st.session_state:
            del st.session_state[key]
    st.experimental_rerun()

# -----------------------------------------------------------------------------
# Optional: Display Interactive Board View
# -----------------------------------------------------------------------------
st.write("### Interactive Board View")
cols = st.columns(10)
board = st.session_state.board
for idx, space in enumerate(board):
    col = cols[idx % 10]
    if col.button(f"{idx}: {space['name']}", key=f"space_{idx}"):
        st.info(f"**Space {idx}:** {space['name']}\nType: {space['type']}\nDescription: {space.get('description', 'N/A')}\n" +
                (f"Cost: ${space.get('cost')}" if space.get('cost') else ""))
