import pytest

@pytest.mark.asyncio
async def test_read_root(client):
    print("client, read root")
    response = client.get('/')  # Call synchronously
    assert response.status_code == 200
    assert response.json()['message'] == 'Hello World'