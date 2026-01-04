from dotenv import load_dotenv
load_dotenv()

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.types import Content, Part
from tools import set_player_name, validate_move, resolve_round, update_game_state, VALID_MOVES
import random
from state import game_state
import asyncio
import os
import warnings

# Suppress the Google API key warning
warnings.filterwarnings("ignore")
os.environ['GOOGLE_GENAI_USE_PYTHON_LOGGING'] = '0'

# Create the agent
game_agent = Agent(
    name="game_referee",
    model="gemini-2.0-flash",
    instruction="""
You are a friendly game referee.
You explain rules, round outcomes, score updates, and the final result.
You never change game state or game rules.
You remember previous rounds via conversation history.
"""
)

# Create session service and runner
session_service = InMemorySessionService()
runner = Runner(
    app_name="rock_paper_scissors_game",
    agent=game_agent,
    session_service=session_service
)

# Create a session ID for the game
SESSION_ID = "game_session_1"
USER_ID = "player_1"


async def agent_say_async(prompt: str):
    """Call the agent asynchronously and print its response."""
    # Create a proper message object
    message = Content(
        role="user",
        parts=[Part(text=prompt)]
    )
    
    response_text = ""
    async for chunk in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        # Check different possible attributes for the response
        if hasattr(chunk, 'content'):
            # Extract text from content parts
            if hasattr(chunk.content, 'parts'):
                for part in chunk.content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text += part.text
        elif hasattr(chunk, 'message') and chunk.message:
            response_text = chunk.message
        elif hasattr(chunk, 'text') and chunk.text:
            response_text += chunk.text
    
    if response_text:
        print(f"\nAgent: {response_text}\n")
    else:
        print(f"\nAgent: (No response received)\n")


async def explain_rules_async():
    await agent_say_async("""
                Explain the rules of Rock Paper Scissors Plus in 5 lines.
                Moves: rock, paper, scissors, bomb.
                Bomb can be used only once.
                Game is best of 3 rounds.
                Invalid input wastes the round.
                """)


async def agent_step_async(user_input: str | None, state: dict):

    # 1️⃣ Ask for name
    if state["player_name"] is None:
        if not user_input:
            print("Before we start, what's your name?")
            return

        set_player_name(user_input, state)

        await agent_say_async(f"""
                        The player's name is {state['player_name']}.
                        Greet the player and welcome them to the game.
                        """)

        await explain_rules_async()
        print(f"Round {state['round']}/3")
        print("Choose your move:")
        return

    # 2️⃣ Game already over
    if state["game_over"]:
        return
    
    # Check if we've completed 3 rounds
    if state["round"] > 3:
        state["game_over"] = True
        
        # Determine final winner
        if state["user_score"] > state["bot_score"]:
            final_result = f"{state['player_name']} wins!"
        elif state["bot_score"] > state["user_score"]:
            final_result = "Bot wins!"
        else:
            final_result = "It's a tie!"
        
        await agent_say_async(f"""
        Game Over! All 3 rounds have been played.
        Final score:
        {state['player_name']}: {state['user_score']}
        Bot: {state['bot_score']}
        Result: {final_result}
        Explain the final result in a congratulatory or encouraging way.
        """)
        return

    # 3️⃣ Play round
    user_move = user_input.lower().strip()
    validation = validate_move(user_move, state, "user")

    bot_move = random.choice(VALID_MOVES)
    if not validate_move(bot_move, state, "bot")["valid"]:
        bot_move = random.choice(["rock", "paper", "scissors"])

    if not validation["valid"]:
        state["round"] += 1

        await agent_say_async(f"""
            Round {state['round'] - 1}
            The player entered an invalid move: "{user_input}".
            The round is wasted.
            Current score:
            {state['player_name']}: {state['user_score']}
            Bot: {state['bot_score']}
            Explain what happened.
            """)

    else:
        winner = resolve_round(user_move, bot_move)
        update_game_state(state, winner, user_move, bot_move)

        await agent_say_async(f"""
            Round {state['round'] - 1}
            Player move: {user_move}
            Bot move: {bot_move}
            Winner: {winner}
            Current score:
            {state['player_name']}: {state['user_score']}
            Bot: {state['bot_score']}
            Explain this round and the current status.
            """)

    # After 3 rounds, end the game
    if state["round"] > 3:
        state["game_over"] = True
        
        # Determine final winner
        if state["user_score"] > state["bot_score"]:
            final_result = f"{state['player_name']} wins!"
        elif state["bot_score"] > state["user_score"]:
            final_result = "Bot wins!"
        else:
            final_result = "It's a tie!"
        
        await agent_say_async(f"""
        Game Over! All 3 rounds have been played.
        Final score:
        {state['player_name']}: {state['user_score']}
        Bot: {state['bot_score']}
        Result: {final_result}
        Explain the final result in a congratulatory or encouraging way.
        """)
        return

    if not state["game_over"]:
        print(f"Round {state['round']}/3")
        print("Choose your move:")


# -----------------------------
# MAIN ASYNC GAME LOOP
# -----------------------------

async def main():
    """Main async game loop."""
    # Create session before first use
    await session_service.create_session(
        app_name="rock_paper_scissors_game",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    
    # Start game
    await agent_step_async(None, game_state)

    while not game_state["game_over"]:
        user_message = input("> ")
        await agent_step_async(user_message, game_state)


if __name__ == "__main__":
    asyncio.run(main())