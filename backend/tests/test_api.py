import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app import app

client = TestClient(app)


class TestAuth:
    @patch("app.supabase.auth")
    def test_signup_success(self, mock_supabase):
        mock_supabase.auth.sign_up.return_value = Mock(user={"id": "123"})

        response = client.post(
            "/signup", json={"email": "test@example.com", "password": "password123"}
        )

        assert response.status_code == 200
        assert "user" in response.json()

    @patch("app.supabase.auth")
    def test_signin_success(self, mock_supabase):
        mock_user = Mock()
        mock_session = Mock()
        mock_session.access_token = "test_token"
        mock_response = Mock(user=mock_user, session=mock_session)
        mock_supabase.auth.sign_in_with_password.return_value = mock_response

        response = client.post(
            "/signin", json={"email": "test@example.com", "password": "password123"}
        )

        assert response.status_code == 200
        assert "access_token" in response.json()


class TestExpenses:
    @patch("app.supabase")
    def test_add_expense_success(self, mock_supabase):
        mock_expense_response = Mock()
        mock_expense_response.data = [{"id": "exp123"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_expense_response
        )

        mock_debtors_response = Mock()
        mock_debtors_response.data = [{"id": "debt123"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_debtors_response
        )

        response = client.post(
            "/expenses",
            json={
                "name": "Test Expense",
                "amount": 100.0,
                "payer_id": "person1",
                "group_id": "group1",
                "debtors": ["person1", "person2"],
            },
        )

        assert response.status_code == 200
        assert response.json()["message"] == "Expense added"

    @patch("app.supabase")
    def test_get_expenses_for_group(self, mock_supabase):
        mock_expenses = [{"id": "1", "name": "Test", "amount": 50}]
        mock_response = Mock()
        mock_response.data = mock_expenses
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        response = client.get("/expenses/group123")

        assert response.status_code == 200
        assert "expenses" in response.json()

    @patch("app.supabase")
    def test_delete_expense_success(self, mock_supabase):
        mock_response = Mock()
        mock_response.data = [{"id": "exp123", "name": "Deleted Expense"}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        response = client.delete("/expenses/exp123")

        assert response.status_code == 200
        assert response.json()["message"] == "Expense deleted"


class TestGroups:
    @patch("app.supabase")
    def test_get_groups_success(self, mock_supabase):
        mock_groups = [{"id": "1", "name": "Test Group"}]
        mock_response = Mock()
        mock_response.data = mock_groups
        mock_supabase.table.return_value.select.return_value.execute.return_value = (
            mock_response
        )

        response = client.get("/groups")

        assert response.status_code == 200
        assert "groups" in response.json()

    @patch("app.supabase")
    def test_add_group_success(self, mock_supabase):
        mock_response = Mock()
        mock_response.data = [{"id": "group123", "name": "New Group"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        response = client.post("/groups", json={"name": "New Group"})

        assert response.status_code == 200
        assert response.json()["message"] == "Group added"

    @patch("app.supabase")
    def test_get_group_persons(self, mock_supabase):
        mock_persons = [{"id": "1", "name": "John", "group_id": "group123"}]
        mock_response = Mock()
        mock_response.data = mock_persons
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        response = client.get("/groups/group123/persons")

        assert response.status_code == 200
        assert "persons" in response.json()


class TestPersons:
    @patch("app.supabase")
    def test_add_person_success(self, mock_supabase):
        mock_response = Mock()
        mock_response.data = [{"id": "person123", "name": "John", "group_id": "group1"}]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        response = client.post("/persons", json={"name": "John", "group_id": "group1"})

        assert response.status_code == 200
        assert response.json()["message"] == "Person added"

    @patch("app.supabase")
    def test_delete_person_success(self, mock_supabase):
        mock_response = Mock()
        mock_response.data = [{"id": "person123", "name": "John"}]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        response = client.delete("/persons/person123")

        assert response.status_code == 200
        assert response.json()["message"] == "Persone deleted"


class TestBalances:
    @patch("app.supabase")
    def test_get_group_balances_success(self, mock_supabase):
        mock_group_table = Mock()
        mock_persons_table = Mock()
        mock_expenses_table = Mock()
        mock_debtors_table = Mock()

        mock_group_response = Mock()
        mock_group_response.data = {"id": "group123"}
        mock_group_table.select.return_value.eq.return_value.single.return_value.execute.return_value = (
            mock_group_response
        )

        mock_persons_response = Mock()
        mock_persons_response.data = [
            {"id": "person1", "name": "John"},
            {"id": "person2", "name": "Jane"},
        ]
        mock_persons_table.select.return_value.eq.return_value.execute.return_value = (
            mock_persons_response
        )

        mock_expenses_response = Mock()
        mock_expenses_response.data = [
            {"id": "exp1", "amount": 100, "payer_id": "person1"}
        ]
        mock_expenses_table.select.return_value.eq.return_value.execute.return_value = (
            mock_expenses_response
        )

        mock_debtors_response = Mock()
        mock_debtors_response.data = [
            {"person_id": "person1", "amount": 50, "expense_id": "exp1"},
            {"person_id": "person2", "amount": 50, "expense_id": "exp1"},
        ]
        mock_debtors_table.select.return_value.in_.return_value.execute.return_value = (
            mock_debtors_response
        )

        def table_side_effect(table_name):
            if table_name == "groups":
                return mock_group_table
            elif table_name == "persons":
                return mock_persons_table
            elif table_name == "expenses":
                return mock_expenses_table
            elif table_name == "expenses_debtors":
                return mock_debtors_table
            return Mock()

        mock_supabase.table.side_effect = table_side_effect

        response = client.get("/groups/group123/balances")

        assert response.status_code == 200
        assert "balances" in response.json()


def test_hello_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello!"}
