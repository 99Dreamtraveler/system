"""Regression tests for named image-folder uploads."""
import io
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from flask import Flask

import routes.upload as upload_routes
import services.repository as repository


class NamedFolderUploadTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.database_path = self.root / "tasks.sqlite3"
        self.upload_root = self.root / "uploads"
        self.task_root = self.upload_root / "tasks"
        self.task_root.mkdir(parents=True)

        self.database_patch = patch.object(repository, "DATABASE_PATH", self.database_path)
        self.upload_root_patch = patch.object(upload_routes, "UPLOAD_FOLDER", self.upload_root)
        self.task_root_patch = patch.object(upload_routes, "TASK_UPLOAD_FOLDER", self.task_root)
        self.database_patch.start()
        self.upload_root_patch.start()
        self.task_root_patch.start()
        repository.initialize_database()

        app = Flask(__name__)
        app.register_blueprint(upload_routes.upload_bp)
        self.client = app.test_client()

    def tearDown(self):
        self.task_root_patch.stop()
        self.upload_root_patch.stop()
        self.database_patch.stop()
        self.temp_dir.cleanup()

    def upload_folder(self):
        return self.client.post(
            "/api/upload/folder",
            data={
                "folder_name": "loan_batch",
                "files": (io.BytesIO(b"image contents"), "loan_batch/loan_001/photo.jpg"),
            },
            content_type="multipart/form-data",
        )

    def test_same_named_folders_create_independent_tasks(self):
        first = self.upload_folder()
        second = self.upload_folder()

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        first_data = first.get_json()["data"]
        second_data = second.get_json()["data"]
        self.assertNotEqual(first_data["session_id"], second_data["session_id"])
        self.assertEqual(first_data["folder_name"], "loan_batch")
        self.assertEqual(second_data["folder_name"], "loan_batch")

        for session_id in (first_data["session_id"], second_data["session_id"]):
            self.assertTrue((self.task_root / session_id / "loan_001" / "photo.jpg").is_file())

        with sqlite3.connect(self.database_path) as conn:
            rows = conn.execute(
                "SELECT task_id, folder_name FROM detection_tasks ORDER BY task_id"
            ).fetchall()

        self.assertEqual(len(rows), 2)
        self.assertEqual({row[0] for row in rows}, {first_data["session_id"], second_data["session_id"]})
        self.assertEqual({row[1] for row in rows}, {"loan_batch"})


if __name__ == "__main__":
    unittest.main()
