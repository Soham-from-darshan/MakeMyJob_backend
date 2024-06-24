from tests.controller import signup, valid_user
from icecream import ic
from sqlalchemy import text
import datetime
import time
from Application.models import User


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


def test_inactive_account_deletion(app, client, database):
    token = signup(client)
    one_year_ago = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
    with app.app_context():
        conn = database.engine.connect()
        conn.execute(text('''
            UPDATE user
            SET last_active_at = :one_year_ago
            WHERE id = :id
        '''),dict(one_year_ago=one_year_ago, id=1))
        conn.commit()
        database.session.commit()
        time.sleep(2)
        assert any(database.session.execute(database.select(User).filter_by(id=1)).scalars()) == False
    res = client.get('/account/getUser', headers=dict(Authorization=f'Bearer {token}'))
    assert res.status_code == 404


# def test_scheduler_3_times(app, client, database):
#     test_inactive_account_deletion(app, client, database)
#     test_inactive_account_deletion(app, client, database)
#     test_inactive_account_deletion(app, client, database)
