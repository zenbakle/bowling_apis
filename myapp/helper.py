import os
from openai import  OpenAI
from dotenv import load_dotenv

load_dotenv()




# Helper function to calculate the score for a game
def calculate_current_score(rolls):
    """
    Calculates the current score and frame breakdown for a bowling game.

    This function iterates through the list of rolls and computes the score
    frame by frame, accounting for strikes, spares, and open frames according
    to standard bowling rules. It returns the total score and a breakdown of
    the score per frame.

    Args:
        rolls (list): A list of recorded rolls, where each roll is a list of two
                      integers. The first integer indicates the roll number
                      (1 or 2), and the second integer indicates the number of pins knocked down.

    Returns:
        tuple: A tuple containing:
            - total score (int): The overall score up to the current roll.
            - scores (dict): A dictionary with frame-by-frame scores and annotations
                             like "Strike", "Spare", or "Open frame".
    """
    current_score = 0  # Initialize the total score
    frame_index = 0  # Tracks the current frame in the rolls
    scores = {}  # Dictionary to store the score and type for each frame

    # Iterate through the list of rolls to calculate the score for each frame
    while frame_index < len(rolls):
        roll1 = rolls[frame_index]  # First roll in the current frame
        roll2 = rolls[frame_index + 1] if frame_index + 1 < len(rolls) else None  # Second roll, if available
        where = "Open frame"
        # Case 1: Strike (first roll in the frame knocks down all 10 pins)
        if roll1[1] == 10:
            # Add 10 for the strike plus the pins knocked down in the next two rolls
            current_score += 10 + (rolls[frame_index + 1][1] if frame_index + 1 < len(rolls) else 0) + \
                                  (rolls[frame_index + 2][1] if frame_index + 2 < len(rolls) else 0)
            frame_index += 1  # Move to the next frame after a strike
            # scores[f"frame_{frame_index}"] = [current_score, "Strike"]
            where = "Strike"
        # Case 2: Spare (sum of two rolls in the frame equals 10 pins)
        elif roll1[1] + roll2[1] == 10:
            # Add 10 for the spare plus the pins knocked down in the next roll
            current_score += 10 + (rolls[frame_index + 2][1] if frame_index + 2 < len(rolls) else 0)
            frame_index += 2  # Move to the next frame after a spare
            # scores[f"frame_{frame_index - 1}"] = [current_score, "Spare"]
            where = "Spare"
        # Case 3: Open frame (sum of two rolls is less than 10)
        else:
            # Add the total pins knocked down in the two rolls
            current_score += roll1[1] + roll2[1]
            frame_index += 2  # Move to the next frame after two rolls
            # scores[f"frame_{frame_index - 1}"] = [current_score, "Open frame"]
    scores[f"frame_{frame_index}"] = [current_score, where]

    return current_score, scores



# Helper function to generate a natural language summary of the game
def generate_summary(rolls):
    """
    Generates a natural language summary of the bowling game using OpenAI's GPT model.

    This function takes a list of recorded rolls, calculates the current score, and
    uses OpenAI's GPT model to generate a natural language summary of the game's
    progress. The summary includes the total score and a frame-by-frame breakdown.

    Args:
        rolls (list): A list of recorded rolls, where each roll is a list of two
                      integers. The first integer indicates the roll number
                      (1 or 2), and the second integer indicates the number of pins knocked down.

    Returns:
        str: A natural language summary of the game, generated by GPT.
    """
    # Calculate the current score and frame breakdown based on the recorded rolls
    score = calculate_current_score(rolls)

    # Initialize the OpenAI API client using the provided API key from environment variables
    client = OpenAI(api_key=os.environ.get("OPENAI_API"))

    # Create a GPT-based chat completion request to generate a game summary
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Specify the model to use
        messages=[
            {"role": "system", "content": "You are a bowling scorekeeper."},  # Set the system's role
            {
                "role": "user",  # The user request message
                "content": f"summarize the rolls of this bowling game. "
                           f"Total score so far {score[0]},"
                           f"Detailed score breakdown for each frame {score[1]}"
            }
        ]
    )

    # Extract and return the content of the first choice from the GPT response
    return str(completion.choices[0].message.content)
