def GameState(): 
    return {
    "player_name": None,
    "round": 1,
    "user_score": 0,
    "bot_score": 0,
    "user_used_bomb": False,
    "bot_used_bomb": False,
    "game_over": False
}

game_state = GameState()