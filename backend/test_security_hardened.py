import io
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from main import app
from auth import ADMIN_MASTER_PIN

client = TestClient(app)

class TestHardenedSecurity(unittest.TestCase):
    def test_01_security_headers_present(self):
        resp = client.get("/api/v1/categories")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("x-content-type-options"), "nosniff")
        self.assertEqual(resp.headers.get("x-frame-options"), "SAMEORIGIN")
        self.assertEqual(resp.headers.get("x-xss-protection"), "1; mode=block")
        self.assertEqual(resp.headers.get("referrer-policy"), "strict-origin-when-cross-origin")
        print("[PASS] Security response headers verified.")

    def test_02_image_proxy_path_traversal_blocked(self):
        # Attempt to escape uploads directory
        resp = client.get("/api/v1/image-proxy", params={"url": "/uploads/../../jachai.db"})
        self.assertIn(resp.status_code, [400, 403, 404])
        self.assertNotEqual(resp.headers.get("content-type"), "application/x-sqlite3")
        print("[PASS] Path traversal attempt safely blocked.")

    def test_03_image_proxy_ssrf_blocked(self):
        # Attempt SSRF to loopback / internal port
        resp = client.get("/api/v1/image-proxy", params={"url": "http://127.0.0.1:8000/api/v1/admin/overview"})
        self.assertEqual(resp.status_code, 400)
        self.assertIn("prohibited", resp.json()["detail"].lower())
        print("[PASS] SSRF to loopback/internal IP strictly blocked.")

    def test_04_svg_xss_upload_blocked(self):
        malicious_svg = b'<svg xmlns="http://www.w3.org/2000/svg"><script>alert(1)</script></svg>'
        files = {"file": ("evil.svg", io.BytesIO(malicious_svg), "image/svg+xml")}
        headers = {"X-Admin-Pin": ADMIN_MASTER_PIN}
        resp = client.post("/api/v1/admin/upload-banner", files=files, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("prohibited executable scripts", resp.json()["detail"].lower())
        print("[PASS] SVG script injection upload blocked.")

    def test_05_oversized_upload_blocked(self):
        oversized = b"A" * (11 * 1024 * 1024)  # 11MB
        files = {"file": ("huge.png", io.BytesIO(oversized), "image/png")}
        headers = {"X-Admin-Pin": ADMIN_MASTER_PIN}
        resp = client.post("/api/v1/admin/upload-banner", files=files, headers=headers)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("exceeds", resp.json()["detail"].lower())
        print("[PASS] Oversized file upload blocked.")

if __name__ == "__main__":
    unittest.main()

