import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocketDisconnect
from app.main import app
from app.room_manager import room_manager
import json


@pytest.fixture
def client():
    room_manager.rooms.clear()
    return TestClient(app)


def test_connect_with_valid_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        response = websocket.receive_json()
        assert response["type"] == "system"
        assert "connected" in response["text"]


def test_connect_without_username(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/rooms/python"):
            pass
    assert exc_info.value.code == 1008


def test_connect_with_empty_username(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/rooms/python?username="):
            pass
    assert exc_info.value.code == 1008


def test_connect_with_spaces_only_username(client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with client.websocket_connect("/ws/rooms/python?username=%20%20%20"):
            pass
    assert exc_info.value.code == 1008


def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        websocket.send_json({"type": "message", "text": "Hello everyone"})

        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["room_id"] == "python"
        assert response["username"] == "alice"
        assert response["text"] == "Hello everyone"


def test_two_clients_same_room_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket_alice:
        websocket_alice.receive_json()

        with client.websocket_connect("/ws/rooms/python?username=bob") as websocket_bob:
            websocket_bob.receive_json()

            websocket_alice.send_json({"type": "message", "text": "Hello Bob"})

            response_alice = websocket_alice.receive_json()
            assert response_alice["type"] == "message"
            assert response_alice["text"] == "Hello Bob"

            response_bob = websocket_bob.receive_json()
            assert response_bob["type"] == "message"
            assert response_bob["text"] == "Hello Bob"


def test_different_rooms_dont_share_messages(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket_python:
        websocket_python.receive_json()

        with client.websocket_connect("/ws/rooms/java?username=bob") as websocket_java:
            websocket_java.receive_json()

            websocket_python.send_json({"type": "message", "text": "Python message"})

            response_python = websocket_python.receive_json()
            assert response_python["text"] == "Python message"

            with pytest.raises(Exception):
                websocket_java.receive_json(timeout=1)


def test_long_message_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        long_text = "a" * 301
        websocket.send_json({"type": "message", "text": long_text})

        response = websocket.receive_json()
        assert response["type"] == "error"
        assert response["detail"] == "Message is too long"


def test_short_message_does_not_return_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        short_text = "a" * 300
        websocket.send_json({"type": "message", "text": short_text})

        response = websocket.receive_json()
        assert response["type"] == "message"
        assert response["text"] == short_text


def test_user_removed_from_room_after_disconnect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        websocket.receive_json()

        response = client.get("/rooms/python/users")
        assert response.status_code == 200
        assert response.json()["users"] == ["alice"]

    response = client.get("/rooms/python/users")
    assert response.status_code == 200
    assert response.json()["users"] == []


def test_multiple_users_in_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket_alice:
        websocket_alice.receive_json()

        with client.websocket_connect("/ws/rooms/python?username=bob") as websocket_bob:
            websocket_bob.receive_json()

            with client.websocket_connect("/ws/rooms/python?username=charlie") as websocket_charlie:
                websocket_charlie.receive_json()

                response = client.get("/rooms/python/users")
                assert response.status_code == 200
                users = response.json()["users"]
                assert len(users) == 3
                assert "alice" in users
                assert "bob" in users
                assert "charlie" in users


def test_get_users_empty_room(client):
    response = client.get("/rooms/empty/users")
    assert response.status_code == 200
    assert response.json()["users"] == []
    assert response.json()["room_id"] == "empty"


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_system_message_on_connect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        message = websocket.receive_json()
        assert message["type"] == "system"
        assert "alice" in message["text"]


def test_system_message_on_disconnect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as websocket:
        connect_msg = websocket.receive_json()
        assert connect_msg["type"] == "system"

        with client.websocket_connect("/ws/rooms/python?username=bob") as websocket_bob:
            bob_connect = websocket_bob.receive_json()
            assert bob_connect["type"] == "system"

    response = client.get("/rooms/python/users")
    assert response.json()["users"] == ["alice"]