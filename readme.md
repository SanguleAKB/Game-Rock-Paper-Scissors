# Rock-Paper-Scissors-Plus Game Referee

A conversational AI game referee built with Google ADK that manages a best-of-3 Rock-Paper-Scissors game with an added "bomb" move.

## State Model

The game state is managed through a centralized dictionary with the following structure:

```python
{
    "player_name": str | None,      # Player's name
    "round": int,                    # Current round (1-3)
    "user_score": int,               # Player's score
    "bot_score": int,                # Bot's score
    "user_used_bomb": bool,          # Tracks if player used bomb
    "bot_used_bomb": bool,           # Tracks if bot used bomb
    "game_over": bool                # Game completion flag
}
```

State persists in memory throughout the game session and is mutated exclusively through explicit tool functions, never by the LLM directly.

## Agent/Tool Design

### Architecture Separation

The solution cleanly separates three core responsibilities:

1. **Intent Understanding** (`agent.py`): The agent orchestrates game flow, interprets user input, and determines which tools to invoke
2. **Game Logic** (`tools.py`): Pure functions handle validation, rule enforcement, and state mutations
3. **Response Generation** (`agent.py` via ADK): The LLM agent generates natural language feedback based on game state

### Tools

Four explicit tools enforce game rules and manage state:

- **`set_player_name(name, state)`**: Captures and formats player name
- **`validate_move(move, state, player)`**: Validates move legality (checks valid moves and bomb usage)
- **`resolve_round(user_move, bot_move)`**: Determines round winner based on game rules
- **`update_game_state(state, winner, user_move, bot_move)`**: Updates scores, bomb flags, round counter, and game-over status

These tools are called programmatically in the game loop rather than via LLM function calling, ensuring deterministic state management.

### Agent Role

The Gemini-2.0-flash agent acts purely as a conversational referee:
- Explains rules concisely
- Narrates round outcomes
- Provides encouragement and commentary
- **Never** modifies game state or rules

## Tradeoffs Made

1. **Programmatic Tool Invocation**: Tools are called directly in the game loop rather than via LLM function calling. This ensures deterministic state management and prevents hallucinated state changes, trading flexibility for reliability.

2. **Synchronous Bot Move**: Bot chooses moves randomly without strategic AI. This keeps the scope focused on referee logic rather than game-playing strategy.

3. **Simple CLI Interface**: Uses basic input/output rather than a rich UI, allowing focus on agent design and state management.

4. **In-Memory State Only**: State lives in a Python dictionary for the session. No persistence across restarts, but meets the "no databases" constraint.

## What I Would Improve With More Time

1. **True ADK Function Calling**: Implement tools as proper ADK functions that the agent can invoke autonomously, allowing more natural conversation flow where the agent decides when to check state vs. respond.

2. **Better Input Parsing**: Add fuzzy matching (e.g., "rok" → "rock") and natural language understanding (e.g., "I'll throw a rock" → "rock").

3. **Richer Feedback**: Include move history, suggestion of optimal strategies, or personality-driven commentary based on game progress.

4. **Error Recovery**: Allow users to restart mid-game or undo accidental invalid inputs.

5. **State Persistence**: Add optional JSON file export/import for game history or multi-session tournaments.

6. **Testing**: Add unit tests for tools and integration tests for game flow scenarios.

## Running the Game

```bash
# Install dependencies
pip install google-adk python-dotenv

# Set your Google API key in .env file
GOOGLE_API_KEY=your-key-here

# Run the game
python agent.py
```

The game will prompt for your name, explain rules, and guide you through 3 rounds. Invalid inputs waste the round. The bomb can only be used once per player.

## Project Structure

```
.
├── agent.py          # Main game loop and agent orchestration
├── tools.py          # Game logic functions (validation, resolution, state updates)
├── state.py          # State model definition
├── __init__.py       # Module initialization
├── .env              # Environment variables (API key)
└── README.md         # This file
```

## Game Rules

- Best of 3 rounds
- Valid moves: rock, paper, scissors, bomb
- Standard rules apply (rock beats scissors, scissors beats paper, paper beats rock)
- Bomb beats all other moves (rock, paper, scissors)
- Bomb vs bomb results in a draw
- Each player can use bomb only once per game
- Invalid input wastes the round
- Game ends automatically after 3 rounds