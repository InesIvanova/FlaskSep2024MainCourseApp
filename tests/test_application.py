from flask_testing import TestCase

from models import RoleType, UserModel
from tests.base import generate_token, APIBaseTestCase
from factories import UserFactory


class TestProtectedEndpoints(APIBaseTestCase):
    endpoints = (
        ("GET", "/complainers/complaints"),
        ("POST", "/complainers/complaints"),
        ("PUT", "/approvers/complaints/1/approve"),
        ("PUT", "/approvers/complaints/1/reject"),
        ("POST", "/admins/users"),
        ("POST", "/users/change-password"),
    )

    def make_request(self, method, url, headers=None):
        if method == "GET":
            resp = self.client.get(url, headers=headers)
        elif method == "POST":
            resp = self.client.post(url, headers=headers)
        elif method == "PUT":
            resp = self.client.put(url, headers=headers)
        else:
            resp = self.client.delete(url, headers=headers)

        return resp

    def test_login_required_endpoints_missing_token(self):
        for method, url in self.endpoints:
            resp = self.make_request(method, url)

            self.assertEqual(resp.status_code, 401)
            expected_message = {"message": "Invalid or missing token"}
            self.assertEqual(resp.json, expected_message)

    def test_login_required_endpoints_invalid_token(self):
        headers = {"Authorization": "Bearer invalid"}

        for method, url in self.endpoints:
            resp = self.make_request(method, url, headers=headers)

            self.assertEqual(resp.status_code, 401)
            expected_message = {"message": "Invalid or missing token"}
            self.assertEqual(resp.json, expected_message)

    def test_permission_required_endpoints_approvers(self):
        endpoints = (
            ("PUT", "/approvers/complaints/1/approve"),
            ("PUT", "/approvers/complaints/1/reject"),
        )
        # User is a complainer, not approver
        user = UserFactory()
        user_token = generate_token(user)
        headers = {"Authorization": f"Bearer {user_token}"}
        for method, url in endpoints:
            resp = self.make_request(method, url, headers=headers)

            self.assertEqual(resp.status_code, 403)
            expected_message = {
                "message": "You do not have permissions to access this resource"
            }
            self.assertEqual(resp.json, expected_message)

    def test_permission_required_endpoints_admins(self):
        endpoints = (("POST", "/admins/users"),)
        # User is a complainer, not approver
        user = UserFactory()
        user_token = generate_token(user)
        headers = {"Authorization": f"Bearer {user_token}"}
        for method, url in endpoints:
            resp = self.make_request(method, url, headers=headers)

            self.assertEqual(resp.status_code, 403)
            expected_message = {
                "message": "You do not have permissions to access this resource"
            }
            self.assertEqual(resp.json, expected_message)

    def test_permission_required_endpoints_complainers(self):
        endpoints = (("POST", "/complainers/complaints"),)
        # User is a complainer, not approver
        user = UserFactory(role=RoleType.admin)
        user_token = generate_token(user)
        headers = {"Authorization": f"Bearer {user_token}"}
        for method, url in endpoints:
            resp = self.make_request(method, url, headers=headers)

            self.assertEqual(resp.status_code, 403)
            expected_message = {
                "message": "You do not have permissions to access this resource"
            }
            self.assertEqual(resp.json, expected_message)


class TestRegister(APIBaseTestCase):
    def test_register_schema_missing_fields(self):
        data = {}

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)

        resp = self.client.post("/register", json=data)
        self.assertEqual(resp.status_code, 400)
        error_message = resp.json["message"]
        for field in ("email", "password", "first_name", "last_name", "iban"):
            self.assertIn(field, error_message)

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)

    def test_register_schema_invalid_email(self):
        data = {
            "email": "asd",  # This is invalid value
            "password": "asd",
            "first_name": "Test",
            "last_name": "testov",
            "phone": "08888888",
            "iban": "BG1234",
        }

        users = UserModel.query.all()
        self.assertEqual(len(users), 0)

        resp = self.client.post("/register", json=data)
        self.assertEqual(resp.status_code, 400)
        error_message = resp.json["message"]
        expected_message = "Invalid payload {'email': ['Not a valid email address.']}"
        self.assertEqual(error_message, expected_message)
        users = UserModel.query.all()
        self.assertEqual(len(users), 0)

    def test_register(self):
        # TODO use mocking - uncomment the ses

        self.register_user()

        users = UserModel.query.all()
        self.assertEqual(len(users), 1)

    def test_register_schema_invalid_password(self):
        # TODO need to put custom pass validation in schemas to work
        pass
        # data = {
        #     "email": "a@a.com",
        #     "password": "asd", # This is invalid value
        #     "first_name": "Test",
        #     "last_name": "testov",
        #     "phone": "08888888",
        #     "iban": "BG1234"
        # }
        #
        # resp = self.client.post("/register", json=data)
        # self.assertEqual(resp.status_code, 400)
        # error_message = resp.json["message"]
        # expected_message = "Invalid payload {'email': ['Not a valid email address.']}"
        # self.assertEqual(error_message, expected_message)


class TestLoginSchema(APIBaseTestCase):
    def test_login_schema_missing_fields(self):
        data = {}

        resp = self.client.post("/login", json=data)
        self.assertEqual(resp.status_code, 400)
        error_message = resp.json["message"]
        for field in ("email", "password"):
            self.assertIn(field, error_message)

    def test_login_schema_invalid_email(self):

        email, password = self.register_user()

        data = {
            "email": "asd",  # This is invalid value
            "password": "asd",
        }

        self.assertNotEqual(email, data["email"])

        resp = self.client.post("/login", json=data)
        self.assertEqual(resp.status_code, 400)
        error_message = resp.json["message"]
        expected_message = "Invalid payload {'email': ['Not a valid email address.']}"
        self.assertEqual(error_message, expected_message)

    def test_login(self):
        data = {
            "email": "a@a.com",
            "password": "asd",
        }
        # email, password = self.register_user()
        user = UserFactory(password=data["password"], email=data["email"])

        resp = self.client.post("/login", json=data)
        self.assertEqual(resp.status_code, 200)
        token = resp.json["token"]
        self.assertIsNotNone(token)

    def test_login_invalid_email_raises(self):
        email, password = self.register_user()

        data = {
            "email": "b@a.com",
            "password": "asd",
        }

        self.assertNotEqual(email, data["email"])

        user = UserModel.query.filter_by(email="b@a.com").all()
        self.assertEqual(len(user), 0)

        resp = self.client.post("/login", json=data)
        self.assertEqual(resp.status_code, 401)
        message = resp.json
        expected_message = {
            "message": "The server could not verify that you are authorized to access the "
            "URL requested. You either supplied the wrong credentials (e.g. a "
            "bad password), or your browser doesn't understand how to supply "
            "the credentials required."
        }
        self.assertEqual(message, expected_message)

    def test_login_invalid_password_raises(self):
        email, password = self.register_user()

        data = {
            "email": "a@a.com",
            "password": "invalid",  # wrong password for this email
        }
        self.assertNotEqual(password, data["password"])

        user = UserModel.query.filter_by(email="a@a.com").all()
        self.assertEqual(len(user), 1)

        resp = self.client.post("/login", json=data)
        self.assertEqual(resp.status_code, 401)
        message = resp.json
        expected_message = {
            "message": "The server could not verify that you are authorized to access the "
            "URL requested. You either supplied the wrong credentials (e.g. a "
            "bad password), or your browser doesn't understand how to supply "
            "the credentials required."
        }
        self.assertEqual(message, expected_message)
