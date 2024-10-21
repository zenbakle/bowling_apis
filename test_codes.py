import pytest
from run import app, games


@pytest.fixture
def client():
    """Set up the Flask test client for testing the API endpoints."""
    with app.test_client() as client:
        yield client

def new_game(client):
    """Create a new bowling game and return the game ID."""
    res = client.post('/games')
    data = res.get_json()
    game_id = data["game_id"]
    return game_id


def test_create_game(client):
    """Test the creation of a new bowling game via the API."""
    response = client.post('/games')
    assert response.status_code == 201
    data = response.get_json()
    assert "game_id" in data
    assert data["game_id"] == 1
    assert data["message"] == "Game created"


def test_game_not_found(client):
    """Test accessing a non-existent game."""
    response = client.get('/games/99/score')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Game not found"

def test_record_valid_roll(client):
    """Test recording a roll in a game."""
    # Create a game first
    game_id = new_game(client)

    # Record a valid roll
    response = client.post(f'/games/{game_id}/rolls', json={'roll': [1,2]})
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == 'Roll [1, 2] recorded'

def test_record_invalid_roll(client):
    """Test various invalid roll inputs for the bowling game API."""
    # Create a game first
    game_id = new_game(client)

    # List of invalid rolls to test
    invalid_rolls = [
        (None, "Invalid roll input"),  # roll is None
        ((2, 10), "roll number 2 invalid"),  # roll number 2 is inserted before roll number 1
        ([1, 12], "Invalid roll input"),  # roll points are not in range 0-10
        ([1, 2, 3], "Invalid roll input"),  # roll length is greater than 2
        (["a", "b"], "Invalid roll input")  # roll elements in list are not integers
    ]

    for roll, expected_error in invalid_rolls:
        response = client.post(f'/games/{game_id}/rolls', json={'roll': roll})
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == expected_error

def test_record_invalid_roll_2(client):
    """Test various scenarios of invalid roll inputs for the bowling game API."""
    # Create a game first
    game_id = new_game(client)

    # List of invalid roll scenarios to test
    invalid_roll_scenarios = [
        ([1, 1], [2, 3], [2, 1], 'roll number 2 invalid'),  # Consecutive roll number 2
        ([1, 1], [1, 3], 'roll number 1 invalid'),  # Roll number 1 after a non-strike roll number 1
        ([2, 3], 'roll number 2 invalid'),  # Roll number 2 as first roll in a new game
        ([1, 10], [2, 3], 'roll number 2 invalid')  # Roll number 2 after a strike instead of roll number 1
    ]

    for scenario in invalid_roll_scenarios:
        if len(scenario) == 4:  # Handle the first scenario with two previous rolls

            first_roll, second_roll, invalid_roll, expected_error = scenario
            client.post(f'/games/{game_id}/rolls', json={'roll': first_roll})
            client.post(f'/games/{game_id}/rolls', json={'roll': second_roll})
            response = client.post(f'/games/{game_id}/rolls', json={'roll': invalid_roll})
        elif len(scenario) == 3:
            game_id = new_game(client)
            first_roll, invalid_roll, expected_error = scenario
            client.post(f'/games/{game_id}/rolls', json={'roll': first_roll})
            response = client.post(f'/games/{game_id}/rolls', json={'roll': invalid_roll})

        else:  # Handle the other scenarios
            game_id = new_game(client)
            previous_roll, expected_error = scenario
            response = client.post(f'/games/{game_id}/rolls', json={'roll': previous_roll})

        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == expected_error

        # Reset the game_id for scenarios that require a new game
        if len(scenario) == 4:
            game_id = new_game(client)


def test_record_invalid_roll_3(client):
    """Test recording a roll in a game."""
    # Create a game first
    game_id = new_game(client)

    # Record an invalid roll (e.g., sum of roll number 1 and 2 grater than 10)
    client.post(f'/games/{game_id}/rolls', json={'roll': [1, 9]})
    response = client.post(f'/games/{game_id}/rolls',json={'roll': [2,5]})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Roll points cannot be greater than 10 in a frame"

def test_record_score(client):
    """Test retrieving the current score for a bowling game after recording rolls."""
    # Create a game first
    game_id = new_game(client)

    # Test case 1: Game with an open frame
    client.post(f'/games/{game_id}/rolls', json={'roll': [1, 9]})
    client.post(f'/games/{game_id}/rolls', json={'roll': [2, 0]})
    response = client.get(f'/games/{game_id}/score')
    assert response.status_code == 200
    data = response.get_json()
    assert data["current score"] == 9
    assert data["records"] == [[1, 9], [2, 0]]

    # Create a new game for the next test case
    game_id = new_game(client)

    # Test case 2: Game with a strike
    client.post(f'/games/{game_id}/rolls', json={'roll': [1, 9]})
    client.post(f'/games/{game_id}/rolls', json={'roll': [2, 0]})
    client.post(f'/games/{game_id}/rolls', json={'roll': [1, 10]})
    response = client.get(f'/games/{game_id}/score')
    assert response.status_code == 200
    data = response.get_json()
    assert data["current score"] == 19
    assert data["records"] == [[1, 9], [2, 0], [1, 10]]


def test_get_summary(client):
    """Test getting the summary of a game."""
    # Create a game and record a few rolls
    res = client.post('/games')
    assert res.status_code == 201
    data = res.get_json()
    game_id = data["game_id"]
    client.post(f'/games/{game_id}/rolls', json={'roll':[1, 10]})  # Strike
    client.post(f'/games/{game_id}/rolls', json={'roll':[1, 5]})
    client.post(f'/games/{game_id}/rolls', json={'roll': [2,5]})  # Spare
    client.post(f'/games/{game_id}/rolls', json={'roll': [1,9]})
    client.post(f'/games/{game_id}/rolls', json={'roll': [2,0]})  # Open frame
    response = client.get(f'/games/{game_id}/summary')
    assert response.status_code == 200
    data = response.get_json()
    assert "summary" in data
    assert "Strike" or "strike" in data["summary"]
    assert "Spare" or "spare"in data["summary"]
#
