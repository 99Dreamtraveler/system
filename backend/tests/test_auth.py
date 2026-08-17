"""Authentication response regression tests."""
import unittest
from unittest.mock import patch

from flask import Flask

import routes.auth as auth_routes


class AuthenticationTests(unittest.TestCase):
    def setUp(self):
        auth_routes.users.clear()
        self.log_patch = patch.object(auth_routes, "create_operation_log")
        self.log_patch.start()
        app = Flask(__name__)
        app.config["SECRET_KEY"] = "test-secret"
        app.register_blueprint(auth_routes.auth_bp)
        self.client = app.test_client()

    def tearDown(self):
        self.log_patch.stop()
        auth_routes.users.clear()

    def test_login_returns_sales_role_and_server_login_time(self):
        response = self.client.post(
            "/api/login", json={"username": "sales-user", "password": "password"}
        )

        self.assertEqual(response.status_code, 200)
        data = response.get_json()["data"]
        self.assertEqual(data["username"], "sales-user")
        self.assertTrue(data["token"])
        self.assertEqual(data["role"], "业务员")
        self.assertRegex(data["loginTime"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

    def test_register_response_does_not_include_login_time(self):
        response = self.client.post(
            "/api/register", json={"username": "new-user", "password": "password"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("loginTime", response.get_json()["data"])


if __name__ == "__main__":
    unittest.main()
