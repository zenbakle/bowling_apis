from flask import Blueprint, jsonify, request
from .helper import *
from datetime import datetime


game = Blueprint('game', __name__)

game_id_counter = 1
games = {}


@game.route('/games', methods=['POST'])
def create_game():
    """
    Creates a new bowling game by initializing its state.

    This endpoint is used to start a new bowling game. It generates a unique game ID
    and initializes an empty list to store the rolls for this game. Each new game will
    have a unique `game_id`, which is returned in the response.

    Returns:
        JSON: A message confirming the creation of the game along with the game ID.
        Status Code: 201 Created
    """
    global game_id_counter  # Use a global counter to track the game IDs

    # Assign the current value of the counter as the game_id
    game_id = game_id_counter

    # Initialize the game state for the new game; an empty list of rolls
    games[game_id] = []

    # Increment the game ID counter for the next game
    game_id_counter += 1

    # Return a success message and the game ID
    return jsonify({"message": "Game created", "game_id": game_id}), 201


@game.route('/games/<int:game_id>/rolls', methods=['POST'])
def record_roll(game_id):
    """
    Records a roll for a specific bowling game.

    This endpoint accepts a roll input and adds it to the game state for the specified game.
    It validates that the roll is properly structured, ensures that the game exists, and checks for
    proper frame and score logic in accordance with standard bowling rules.

    Args:
        game_id (int): The ID of the game to which the roll belongs.

    Request JSON:
        - roll (list): A list containing the frame number and the number of pins knocked down.

    Returns:
        JSON: A message indicating whether the roll was successfully recorded or if an error occurred.
        Status Code: 200 OK (for successful roll) or 400/404 (for errors).
    """
    # Check if the game exists; return 404 error if not found
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    # Get the roll data from the request JSON payload
    data = request.get_json()
    roll = data.get('roll')

    # Fetch the list of previous rolls for the given game
    rolls = games[game_id]

    # Validate the roll input:
    # - Must be a list
    # - Frame roll number must be 1 or 2
    # - Number of pins knocked down must be between 0 and 10
    # - List must contain exactly two integers
    if ((roll is None) or
            (not isinstance(roll, list)) or
            (roll[0] not in [1, 2]) or
            (roll[1] < 0) or
            (roll[1] > 10) or
            (len(roll) != 2) or
            (type(roll[0]) is not int) or
            (type(roll[1]) is not int)):
        return jsonify({"error": "Invalid roll input"}), 400

    # Check the last roll (if any) to validate that the current roll is legal
    last_roll = rolls[-1] if len(rolls) > 0 else [0, 0]

    # Validate frame rules:
    # - Cannot have two consecutive rolls with frame roll 2.
    # - Cannot start a new frame (roll 1) when the previous roll 1 is not a strike (less than 10 pins).
    # - Various other frame transition checks to ensure legal gameplay.
    if ((last_roll[0] == 2 and roll[0] == 2) or  # Two consecutive frame 2 rolls are invalid
            (last_roll[0] == 1 and last_roll[1] < 10 and roll[
                0] == 1) or  # Cannot roll a new frame 1 after a non-strike roll
            (last_roll[0] == 0 and roll[0] == 2) or  # Cannot start the game with frame 2
            (last_roll[0] == 1 and last_roll[1] == 10 and roll[
                0] == 2)):  # Strike in frame 1, then frame 2 immediately is invalid
        return jsonify({"error": f"roll number {roll[0]} invalid"}), 400

    # Ensure the sum of two rolls in a frame does not exceed 10 (e.g., a spare)
    if last_roll[0] == 1 and roll[0] == 2 and roll[1] + last_roll[1] > 10:
        return jsonify({"error": "Roll points cannot be greater than 10 in a frame"}), 400

    # If all validations pass, record the roll
    games[game_id].append(roll)

    # Return a success message along with the current state of the rolls for the game
    return jsonify({"message": f"Roll {roll} recorded", "records": rolls}), 200


@game.route('/games/<int:game_id>/score', methods=['GET'])
def get_score(game_id):
    """
    Retrieves the current score of a specific bowling game.

    This endpoint calculates and returns the current score for the specified game.
    The score is calculated based on the rolls recorded so far. If the game does not
    exist, it returns a 404 error.

    Args:
        game_id (int): The ID of the game whose score is to be fetched.

    Returns:
        JSON: A message containing the list of recorded rolls, the current score,
              and a detailed score breakdown for each frame.
        Status Code: 200 OK (for successful score retrieval) or 404 (if game is not found).
    """
    # Check if the game exists; return 404 error if not found
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    # Retrieve the list of rolls for the specified game
    rolls = games[game_id]

    # Calculate the current score based on the recorded rolls
    # Assumes `calculate_current_score` returns a tuple (total score, score breakdown)
    score = calculate_current_score(rolls)

    # Return the rolls, current total score, and score breakdown per frame
    return jsonify({
        "records": rolls,  # List of all recorded rolls
        "current score": score[0],  # Total score so far
        "score_list": score[1]  # Detailed score breakdown for each frame
    }), 200



@game.route('/games/<int:game_id>/summary', methods=['GET'])
def get_summary(game_id):
    """
    Retrieves a natural language summary of the current game state for a specific game.

    This endpoint provides a summary of the game's current state, expressed in
    natural language. The summary is generated based on the rolls recorded so far.
    If the game does not exist, a 404 error is returned.

    Args:
        game_id (int): The ID of the game whose summary is to be generated.

    Returns:
        JSON: A message containing a natural language summary of the game's state.
        Status Code: 200 OK (for successful summary generation) or 404 (if the game is not found).
    """
    # Check if the game exists; return 404 error if not found
    if game_id not in games:
        return jsonify({"error": "Game not found"}), 404

    # Retrieve the list of rolls for the specified game
    rolls = games[game_id]

    # Generate a natural language summary of the current game state
    summary = generate_summary(rolls)

    # Return the summary as a JSON response
    return jsonify({"summary": summary}), 200




