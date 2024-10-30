from models import RoleType, UserModel
from tests.base import APIBaseTestCase, generate_token
from tests.factories import UserFactory


class TestCreateUser(APIBaseTestCase):
    def test_permission_required_only_admins_allowed(self):
        user = UserFactory()
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        resp = self.client.post("/admins/users", headers=headers)

        self.assertEqual(resp.status_code, 403)
        self.assertEqual(
            resp.json,
            {"message": "You do not have permissions to access this resource"},
        )

    def test_invalid_missing_fields(self):
        pass

    def test_invalid_schema_values(self):
        pass

    def test_register_user(self):
        user = UserFactory(id=0, role=RoleType.admin)
        token = generate_token(user)
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "email": "new@new.com",
            "password": "asd",
            "first_name": "Test",
            "last_name": "testov",
            "phone": "08888888",
            "iban": "BG1234",
            "role": RoleType.admin.value,
        }

        users = UserModel.query.all()
        self.assertEqual(len(users), 1)

        resp = self.client.post("/admins/users", headers=headers, json=data)

        self.assertEqual(resp.status_code, 201)
        users = UserModel.query.all()
        self.assertEqual(len(users), 2)

        new_user = UserModel.query.filter_by(email=data["email"]).all()
        self.assertEqual(len(new_user), 1)
        self.assertEqual(new_user[0].role, RoleType.admin)
