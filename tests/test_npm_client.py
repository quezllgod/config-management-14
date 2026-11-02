import io
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from src.npm_client import get_dependencies


class NpmClientTests(unittest.TestCase):
    def load_data(self, data):
        response = io.BytesIO(json.dumps(data).encode("utf-8"))
        with patch("src.npm_client.urlopen", return_value=response):
            return get_dependencies(
                "https://registry.npmjs.org", "express", "4.18.2"
            )

    def test_dependencies(self):
        data = {"dependencies": {"accepts": "~1.3.8"}}
        self.assertEqual(self.load_data(data), {"accepts": "~1.3.8"})

    def test_no_dependencies(self):
        self.assertEqual(self.load_data({}), {})

    def test_bad_dependencies(self):
        with self.assertRaises(ValueError):
            self.load_data({"dependencies": []})

    def test_bad_dependency_version(self):
        with self.assertRaises(ValueError):
            self.load_data({"dependencies": {"accepts": 123}})

    def test_bad_document(self):
        with self.assertRaises(ValueError):
            self.load_data([])

    def test_not_found(self):
        error = HTTPError("https://example.com", 404, "Not Found", {}, None)
        with patch("src.npm_client.urlopen", side_effect=error):
            with self.assertRaisesRegex(ValueError, "не найдены"):
                get_dependencies("https://example.com", "express", "1.0.0")

    def test_network_error(self):
        with patch("src.npm_client.urlopen", side_effect=URLError("offline")):
            with self.assertRaisesRegex(ValueError, "подключиться"):
                get_dependencies("https://example.com", "express", "1.0.0")

    def test_invalid_json(self):
        response = io.BytesIO(b"not json")
        with patch("src.npm_client.urlopen", return_value=response):
            with self.assertRaisesRegex(ValueError, "JSON"):
                get_dependencies("https://example.com", "express", "1.0.0")

    def test_scoped_package_url(self):
        response = io.BytesIO(b"{}")
        with patch(
            "src.npm_client.urlopen", return_value=response
        ) as request:
            get_dependencies(
                "https://example.com/", "@scope/name", "1.2.3"
            )
        request.assert_called_once_with(
            "https://example.com/%40scope%2Fname/1.2.3", timeout=20
        )


if __name__ == "__main__":
    unittest.main()