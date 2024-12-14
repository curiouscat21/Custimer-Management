import pytest
from flask import Flask
from flask.testing import FlaskClient
from unittest.mock import MagicMock, patch
from werkzeug.exceptions import BadRequest
from api import app, data_fetch

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["MYSQL_HOST"] = "mock_host"
    app.config["MYSQL_USER"] = "mock_user"
    app.config["MYSQL_PASSWORD"] = "mock_password"
    app.config["MYSQL_DB"] = "mock_db"
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_db(mocker):
    # Create a mock cursor
    mock_cursor = MagicMock()
    
    # Create a mock connection
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Create a mock MySQL instance
    mock_mysql = MagicMock()
    mock_mysql.connection = mock_connection
    
    # Patch the MySQL instance in your application
    with patch('api.mysql', mock_mysql):
        yield mock_cursor

# Basic Route Tests
def test_hello_world(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello, World!" in response.data

# Countries Endpoint Tests
def test_get_countries_success(client: FlaskClient, mock_db):
    mock_db.fetchall.return_value = [
        {"Country_ID": 1, "Country_Name": "Test Country", "Country_Code": "TC"}
    ]
    response = client.get("/countries")
    assert response.status_code == 200
    assert "Test Country" in response.get_data(as_text=True)

def test_get_countries_error(client: FlaskClient, mock_db):
    mock_db.execute.side_effect = Exception("Database error")
    response = client.get("/countries")
    assert response.status_code == 500
    assert "Database error" in response.get_data(as_text=True)

def test_add_country_success(client: FlaskClient, mock_db):
    response = client.post("/countries", 
                         json={"country_name": "New Country", "country_code": "NC"})
    assert response.status_code == 201
    assert "Country added successfully" in response.get_data(as_text=True)

def test_add_country_missing_data(client: FlaskClient):
    response = client.post("/countries", json={"country_name": "Test"})
    assert response.status_code == 400

# Roles Endpoint Tests
def test_get_roles_success(client: FlaskClient, mock_db):
    mock_db.fetchall.return_value = [
        {"Role_ID": 1, "Role_Code": "ADMIN", "Role_Description": "Administrator"}
    ]
    response = client.get("/roles")
    assert response.status_code == 200
    assert "ADMIN" in response.get_data(as_text=True)

def test_add_role_single(client: FlaskClient, mock_db):
    response = client.post("/roles", 
                         json={"role_code": "MGR", "role_description": "Manager"})
    assert response.status_code == 201

def test_add_role_bulk(client: FlaskClient, mock_db):
    roles = [
        {"role_code": "MGR", "role_description": "Manager"},
        {"role_code": "EMP", "role_description": "Employee"}
    ]
    response = client.post("/roles", json=roles)
    assert response.status_code == 201

# Permission Levels Endpoint Tests
def test_get_permission_levels_success(client: FlaskClient, mock_db):
    mock_db.fetchall.return_value = [
        {"Permission_Level_ID": 1, "Permission_Level_Code": "READ"}
    ]
    response = client.get("/permission_levels")
    assert response.status_code == 200

def test_add_permission_level(client: FlaskClient):
    data = {
        "Permission_Level_Code": "WRITE",
        "Permission_Level_Description": "Write Access"
    }
    response = client.post("/permission_levels", json=data)
    assert response.status_code == 201
    assert "Permission level(s) added successfully" in response.get_data(as_text=True)

def test_update_permission_level(client: FlaskClient, mock_db):
    data = {
        "permission_description": "Updated Description"
    }
    response = client.put("/permission_levels/1", json=data)
    assert response.status_code == 200
    assert "Permission level updated successfully" in response.get_data(as_text=True)

# People Endpoint Tests
def test_add_person_success(client: FlaskClient, mock_db):
    person_data = {
        "Permission_Level_Code": "READ",
        "Login_Name": "testuser",
        "Password": "password123",
        "Personal_Details": "Test User",
        "Other_Details": "None",
        "Country_Name": "US",
        "Role_Description": "USER"
    }
    response = client.post("/people", json=person_data)
    assert response.status_code == 201
    assert "Person added successfully" in response.get_data(as_text=True)

# Internal Messages Endpoint Tests
def test_get_messages_success(client: FlaskClient, mock_db):
    mock_db.fetchall.return_value = [
        {"Message_ID": 1, "message_text": "Test message"}
    ]
    response = client.get("/internal_messages")
    assert response.status_code == 200

# Edge Cases and Error Handling
def test_delete_nonexistent_country(client: FlaskClient, mock_db):
    mock_db.rowcount = 0
    response = client.delete("/countries/999")
    assert response.status_code == 404

def test_update_country_invalid_data(client: FlaskClient):
    response = client.put("/countries/1", json={})
    assert response.status_code == 400

def test_database_connection_error(client: FlaskClient, mock_db):
    mock_db.execute.side_effect = Exception("Connection error")
    response = client.get("/countries")
    assert response.status_code == 500

# Data Fetch Utility Function Test
def test_data_fetch_success(mock_db):
    mock_db.fetchall.return_value = [{"test": "data"}]
    result = data_fetch("SELECT * FROM test")
    assert result == [{"test": "data"}]

def test_data_fetch_error(mock_db):
    mock_db.execute.side_effect = Exception("Database error")
    with pytest.raises(Exception):
        data_fetch("SELECT * FROM test")

# Payments Endpoint Tests
def test_get_payments_success(client: FlaskClient, mock_db):
    mock_db.fetchall.return_value = [
        {"Payment_ID": 1, "Amount": 100.00}
    ]
    response = client.get("/payments")
    assert response.status_code == 200

def test_add_payment_success(client: FlaskClient, mock_db):
    payment_data = {
        "amount": 100.00,
        "payment_date": "2023-01-01",
        "payment_method": "CREDIT"
    }
    response = client.post("/payments", json=payment_data)
    assert response.status_code == 201

# Monthly Reports Endpoint Tests
def test_get_monthly_reports_success(client: FlaskClient, mock_db):
    mock_db.fetchall.return_value = [
        {"Report_ID": 1, "Report_Text": "Monthly Report"}
    ]
    response = client.get("/monthly_reports")
    assert response.status_code == 200

# Additional Edge Cases
def test_update_nonexistent_role(client: FlaskClient, mock_db):
    mock_db.rowcount = 0
    response = client.put("/roles/999", 
                         json={"role_description": "Updated Role"})
    assert response.status_code == 404

def test_invalid_permission_level_data(client: FlaskClient):
    response = client.post("/permission_levels", json={})
    assert response.status_code == 400

def test_delete_nonexistent_message(client: FlaskClient, mock_db):
    mock_db.rowcount = 0
    response = client.delete("/internal_messages/999")
    assert response.status_code == 404