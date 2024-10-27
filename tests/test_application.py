import json

from flask_testing import TestCase

from config import create_app
from db import db
from tests.base import generate_token
from tests.facotries import UserFactory


class TestApp(TestCase):
    def create_app(self):
        return create_app("config.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_protected(self):
        for method, url in [
            ("PUT", "approvers/complaints/1/approve"),
            ("PUT", "approvers/complaints/1/reject"),
            ("GET", "/complainers/complaints"),
            ("POST", "/complainers/complaints"),
            ("POST", "/admins/users"),
            ("POST", "/users/change-password"),
        ]:
            if method == "POST":
                resp = self.client.post(
                    url,
                    data=json.dumps({}),
                )
            elif method == "GET":
                resp = self.client.get(url)
            elif method == "PUT":
                resp = self.client.put(
                    url,
                    data=json.dumps({}),
                )
            else:
                resp = self.client.delete(url)
            expected_message = {"message": "Invalid or missing token"}
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(resp.json, expected_message)

    def test_protected_admin_endpoints_require_admin_rights(self):
        for method, url in [
            ("POST", "/admins/users"),
            # If you wrote your homework from previous lectures add your delete claim endpoint here
            # ("DELETE", "/admins/complains/1"),
        ]:
            complainer = UserFactory()
            token = generate_token(complainer)
            headers = {"Authorization": f"Bearer {token}"}
            if method == "POST":
                resp = self.client.post(url, data=json.dumps({}), headers=headers)
            # elif method == "DELETE":
            #     resp = self.client.delete(url, headers=headers)
            expected_message = {
                "message": "You do not have permissions to access this resource"
            }
            self.assertEqual(resp.status_code, 403)
            self.assertEqual(resp.json, expected_message)
