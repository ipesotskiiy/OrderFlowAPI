from rest_framework import status


def test_check_health(api_client):
    response = api_client.get("/api/v1/health/")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status': 'ok'}
