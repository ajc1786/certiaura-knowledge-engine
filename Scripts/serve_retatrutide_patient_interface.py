from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}
MAX_REQUEST_BYTES = 131072

def validate_bind_host(host: str) -> None:
    if host not in LOOPBACK_HOSTS:
        raise ValueError("This baseline may bind only to a loopback host")

def run_json_command(arguments: list[str], output_path: Path) -> dict:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(arguments, capture_output=True, text=True, encoding="utf-8", env=env, check=False)
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "Controlled process failed")
    return json.loads(output_path.read_text(encoding="utf-8"))

def handler_factory(repository: Path, ui_root: Path):
    repository = repository.resolve()
    ui_root = ui_root.resolve()
    class Handler(BaseHTTPRequestHandler):
        server_version = "CertiauraLocal/1.0"
        def log_message(self, format, *args):
            sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))
        def security_headers(self):
            self.send_header("Cache-Control", "no-store, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("X-Frame-Options", "DENY")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
            self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        def send_json(self, status: int, value: dict):
            body = json.dumps(value, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.security_headers()
            self.end_headers()
            self.wfile.write(body)
        def read_json(self):
            content_type = self.headers.get("Content-Type", "")
            if not content_type.lower().startswith("application/json"):
                raise ValueError("Content-Type must be application/json")
            raw_length = self.headers.get("Content-Length")
            if raw_length is None:
                raise ValueError("Content-Length is required")
            length = int(raw_length)
            if length < 1 or length > MAX_REQUEST_BYTES:
                raise ValueError("Request size is outside the permitted range")
            return json.loads(self.rfile.read(length).decode("utf-8"))
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/api/health":
                self.send_json(HTTPStatus.OK, {"status": "ok", "storage": "memory_only", "binding": "loopback"})
                return
            relative = "index.html" if parsed.path in {"", "/"} else parsed.path.lstrip("/")
            candidate = (ui_root / relative).resolve()
            if ui_root not in candidate.parents and candidate != ui_root:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            if not candidate.is_file() or candidate.suffix.lower() not in {".html", ".css", ".js"}:
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            types = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "application/javascript; charset=utf-8"}
            body = candidate.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", types[candidate.suffix.lower()])
            self.send_header("Content-Length", str(len(body)))
            self.security_headers()
            self.end_headers()
            self.wfile.write(body)
        def do_POST(self):
            try:
                request = self.read_json()
                with tempfile.TemporaryDirectory(prefix="certiaura_0044_api_") as temp:
                    root = Path(temp)
                    if self.path == "/api/report":
                        profile = request.get("profile")
                        if not isinstance(profile, dict):
                            raise ValueError("profile object is required")
                        input_path, output_json, output_md = root / "profile.json", root / "report.json", root / "report.md"
                        input_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
                        result = run_json_command([
                            sys.executable, "-B", str(repository / "Scripts/generate_retatrutide_patient_journey_report.py"), str(input_path),
                            "--repository", str(repository), "--output-json", str(output_json), "--output-md", str(output_md)
                        ], output_json)
                        self.send_json(HTTPStatus.OK, {"valid": True, "report": result})
                        return
                    if self.path == "/api/conversation":
                        session = request.get("session")
                        if not isinstance(session, dict):
                            raise ValueError("session object is required")
                        input_path, output_path = root / "session.json", root / "conversation.json"
                        input_path.write_text(json.dumps(session, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
                        result = run_json_command([
                            sys.executable, "-B", str(repository / "Scripts/run_retatrutide_controlled_conversation.py"), str(input_path),
                            "--repository", str(repository), "--output", str(output_path)
                        ], output_path)
                        self.send_json(HTTPStatus.OK, {"valid": True, "conversation": result})
                        return
                    self.send_json(HTTPStatus.NOT_FOUND, {"valid": False, "error": "Endpoint not found"})
            except (ValueError, json.JSONDecodeError) as exc:
                self.send_json(HTTPStatus.BAD_REQUEST, {"valid": False, "error": str(exc)})
            except Exception:
                self.send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"valid": False, "error": "Controlled operation failed. Review the local terminal for technical diagnostics."})
    return Handler

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    validate_bind_host(args.host)
    if not 1024 <= args.port <= 65535:
        raise ValueError("Port must be between 1024 and 65535")
    repository = Path(args.repository).resolve()
    ui_root = repository / "13_Project_Genesis/UI/Retatrutide_Patient_Interface"
    if not ui_root.is_dir():
        raise FileNotFoundError("Patient interface files are not installed")
    server = ThreadingHTTPServer((args.host, args.port), handler_factory(repository, ui_root))
    print(f"Certiaura local patient interface: http://{args.host}:{args.port}")
    print("No request bodies are persisted. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
