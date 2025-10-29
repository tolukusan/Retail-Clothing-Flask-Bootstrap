def test_homepage(client):
    """
    Tests that the main index route returns a status code of 200 (OK).
    """
    # Use the client fixture to make a GET request to the root URL ('/')
    response = client.get("/")

    # Assert that the HTTP status code is 200
    assert response.status_code == 200
