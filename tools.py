# valid rules 
VALID_MOVES = ["rock", "paper", "scissors", "bomb"]

def set_player_name(name: str, state: dict) -> dict:
    state["player_name"] = name.strip().title()
    return state


def validate_move(move: str, state: dict, player: str) -> dict:
    if move not in VALID_MOVES:
        return {"valid": False, "reason": "Invalid move"}

    if move == "bomb":
        if player == "user" and state["user_used_bomb"]:
            return {"valid": False, "reason": "User bomb already used"}
        if player == "bot" and state["bot_used_bomb"]:
            return {"valid": False, "reason": "Bot bomb already used"}

    return {"valid": True}


def resolve_round(user_move: str, bot_move: str) -> str:
    if user_move == bot_move:
        return "draw"

    if user_move == "bomb":
        return "user"
    if bot_move == "bomb":
        return "bot"

    rules = {
        "rock": "scissors",
        "scissors": "paper",
        "paper": "rock"
    }

    return "user" if rules[user_move] == bot_move else "bot"


def update_game_state(state: dict, winner: str, user_move: str, bot_move: str) -> dict:
    if user_move == "bomb":
        state["user_used_bomb"] = True
    if bot_move == "bomb":
        state["bot_used_bomb"] = True

    if winner == "user":
        state["user_score"] += 1
    elif winner == "bot":
        state["bot_score"] += 1

    state["round"] += 1
    if state["round"] > 3:
        state["game_over"] = True

    return state
