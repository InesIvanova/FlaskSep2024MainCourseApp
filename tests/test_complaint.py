import json
import os
from unittest.mock import patch

from flask_testing import TestCase

from constants import TEMP_FILE_FOLDER
from db import db
from config import create_app
from managers.complainer import ComplainerManager
from models import ComplaintModel
from services.s3 import S3Service
from tests.base import generate_token, mock_uuid
from tests.facotries import UserFactory
from tests.helpers import encoded_file


class TestComplaint(TestCase):
    url = "/complainers/complaints"

    def create_app(self):
        return create_app("config.TestingConfig")

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_complaint_missing_input_fields_raises(self):
        comp = UserFactory()
        token = generate_token(comp)

        complaints = ComplaintModel.query.all()
        self.assertEqual(len(complaints), 0)
        data = {
            "title": "Test",
            "description": "Test test",
            "photo": encoded_file,
            "photo_extension": "png",
            "amount": 10.00,
        }

        for key in data:
            current_data = data.copy()
            current_data.pop(key)
            resp = self.client.post(
                self.url,
                data=json.dumps(current_data),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}",
                },
            )

            message = resp.json["message"]
            expected_message = (
                "Invalid payload {'" + key + "': ['Missing data for required field.']}"
            )
            self.assert400(resp)
            self.assertEqual(message, expected_message)

        complaints = ComplaintModel.query.all()
        self.assertEqual(len(complaints), 0)

    @patch("uuid.uuid4", mock_uuid)
    @patch.object(ComplainerManager, "issue_transaction", return_value=None)
    @patch.object(S3Service, "upload_photo", return_value="some.s3.url")
    def test_complaint(self, mocked_upload, mock_transaction):
        comp = UserFactory()
        token = generate_token(comp)

        complaints = ComplaintModel.query.all()
        self.assertEqual(len(complaints), 0)

        data = {
            "title": "Test",
            "description": "Test test",
            "photo": encoded_file,
            "photo_extension": "png",
            "amount": 10.00,
        }
        resp = self.client.post(
            self.url,
            data=json.dumps(data),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )

        self.assert200(resp)

        name = mock_uuid() + "." + data["photo_extension"]
        path = os.path.join(TEMP_FILE_FOLDER, name)

        complaints = ComplaintModel.query.all()
        self.assertEqual(len(complaints), 1)
        complaint = complaints[0]
        self.assertEqual(complaint.title, data["title"])
        self.assertEqual(complaint.description, data["description"])
        self.assertEqual(complaint.photo_url, mocked_upload.return_value)
        self.assertEqual(complaint.amount, data["amount"])

        mocked_upload.assert_called_once_with(
            path, f"{mock_uuid()}.{data['photo_extension']}", data["photo_extension"]
        )
        mock_transaction.assert_called_once_with(
            data["amount"], comp.first_name, comp.last_name, comp.iban, complaints[0].id
        )
