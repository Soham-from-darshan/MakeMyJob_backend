from tests.controller import signup, valid_user
from icecream import ic


def test_get_user(client):
    token = signup(client) 
    res = client.get('/account/getUser',headers={"Authorization":f'Bearer {token}'})
    ic(res.json)
    assert res.status_code == 200
    for key in valid_user:
        assert valid_user[key] == res.json[key]


def test_deleted_account(client):
    token = signup(client)
    res = client.get('/account/deleteUser', headers={'Authorization':f'Bearer {token}'}) 
    ic(res.json)
    assert res.status_code == 200

    res = client.get('/account/getUser', headers={'Authorization':f'Bearer {token}'})
    assert res.status_code == 404
    ic(res.json)

    res = client.get('/account/deleteUser', headers={'Authorization':f'Bearer {token}'}) 
    ic(res.json)
    assert res.status_code == 404

