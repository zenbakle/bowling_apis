# Bowling Game API

This project is a simple RESTful API built using Flask for managing and scoring a bowling game. It provides endpoints to create a new game, record rolls, calculate the current score, and generate a summary of the game state.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
  - [POST /games](#post-games)
  - [POST /games/{game_id}/rolls](#post-gamesgame_idrolls)
  - [GET /games/{game_id}/score](#get-gamesgame_idscore)
  - [GET /games/{game_id}/summary](#get-gamesgame_idsummary)
- [Testing](#testing)
- [Deploying the API](#deploying-the-api)

## Prerequisites

Before running this project, ensure that you have the following software installed on your system:

- Python 3.x
- pip (Python package installer)
- [OpenAI API Key](https://beta.openai.com/signup/): To generate natural language summaries, you will need an OpenAI API key.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/zenbakle/bowling_apis.git
   cd Game-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables for the OpenAI API key:
   ```bash
   export OPENAI_API=<your-openai-api-key>
   ```
   (For Windows, use `set` instead of `export`)

## Running the Application

To start the Flask application, run the following command:

```bash
python run.py
```

The API will now be available at `http://127.0.0.1:5000/`.

## API Endpoints

### POST /games

Create a new game. This will initialize a new bowling game and return a game ID.

- **URL**: `/games`
- **Method**: `POST`
- **Response**:
  ```json
  {
    "message": "Game created",
    "game_id": <game_id>
  }
  ```
- **Status Code**: `201 Created`

### POST /games/{game_id}/rolls

Record a roll for a specific game. You need to specify the roll as a list in the request body.

- **URL**: `/games/{game_id}/rolls`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "roll": [<roll_number>, <pins_knocked_down>]
  }
  ```
  Example:
  ```json
  {
    "roll": [1, 7]
  }
  ```
- **Response**:
  ```json
  {
    "message": "Roll [1, 7] recorded",
    "records": [[1, 7], ...]
  }
  ```
- **Status Code**: `200 OK`
- **Error Codes**: `404 Game not found`, `400 Invalid roll input`

### GET /games/{game_id}/score

Get the current score of the game, including a breakdown of each frame.

- **URL**: `/games/{game_id}/score`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "records": [[1, 7], [2, 2], ...],
    "current score": 18,
    "score_list": {
      "frame_1": [9, "Open frame"],
      "frame_2": [18, "Open frame"]
    }
  }
  ```
- **Status Code**: `200 OK`
- **Error Codes**: `404 Game not found`

### GET /games/{game_id}/summary

Get a natural language summary of the current game state, generated using GPT.

- **URL**: `/games/{game_id}/summary`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "summary": "You have scored 18 points over two frames. ..."
  }
  ```
- **Status Code**: `200 OK`
- **Error Codes**: `404 Game not found`

## Testing

The project uses `pytest` for unit testing. Tests can be found in the `test_game_api.py` file.

To run the tests, simply execute the following command:

```bash
pytest
```

Ensure that the Flask app is not running while running the tests, as the tests will start their own instance of the application.

## Deploying the API

To deploy the API to a production environment, follow these steps:

1. Install a production server like `gunicorn`:
   ```bash
   pip install gunicorn
   ```

2. Run the Flask app using `gunicorn`:
   ```bash
   gunicorn -w 4 app:game
   ```

   This will start the app with 4 worker processes for better performance.

3. To deploy on cloud services (like AWS, Heroku, or DigitalOcean), follow their respective deployment documentation and ensure that your environment variables (like the OpenAI API key) are properly set.

### Deploying to Heroku Example

1. Install the Heroku CLI:
   ```bash
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. Log in to Heroku:
   ```bash
   heroku login
   ```

3. Create a new Heroku app:
   ```bash
   heroku create bowling-game-api
   ```

4. Add the OpenAI API key to the Heroku environment:
   ```bash
   heroku config:set OPENAI_API=<your-openai-api-key>
   ```

5. Deploy the app:
   ```bash
   git push heroku main
   ```

6. Your app should now be live, and you can access it via the URL provided by Heroku.

---

### Notes:
- Make sure to replace `<your-openai-api-key>` with your actual OpenAI API key.
- The environment variables must be set up properly in both local and production environments to ensure the API runs successfully.
```
