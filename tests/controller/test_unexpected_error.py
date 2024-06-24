def test_internal_server_error(client):
    response = client.get('/throw_error/single')
    assert response.status_code == 500
    assert len(response.json) == 1
    assert response.json['description'] == 'Single arg'

    response = client.get('/throw_error/multi')
    assert response.status_code == 500
    assert len(response.json) == 1
    assert response.json['description'] == 'Multi arg'.split()

    description = (
        "The server encountered an internal error and was unable to"
        " complete your request. Either the server is overloaded or"
        " there is an error in the application."
    )

    response = client.get('/throw_error/none')
    assert response.status_code == 500
    assert len(response.json) == 1
    assert response.json['description'] == ''.join(description)