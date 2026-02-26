import io

import pytest

from agent_teams.api import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestHealth:
    def test_health_check(self, client):
        resp = client.get("/api/health")
        assert resp.status_code == 200
        assert resp.get_json() == {"status": "ok"}


class TestCountText:
    def test_basic_count(self, client):
        resp = client.post("/api/count", data="hello world\nfoo bar baz\n")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["lines"] == 2
        assert data["words"] == 5
        assert data["chars"] == 24
        assert data["bytes"] == 24
        assert data["max_line_length"] == 11

    def test_empty_body(self, client):
        resp = client.post("/api/count", data="")
        assert resp.status_code == 400
        assert "empty" in resp.get_json()["error"].lower()

    def test_single_line_no_newline(self, client):
        resp = client.post("/api/count", data="hello")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["lines"] == 0
        assert data["words"] == 1
        assert data["chars"] == 5

    def test_multibyte_utf8(self, client):
        text = "café\n"
        resp = client.post("/api/count", data=text.encode("utf-8"))
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["chars"] == 5
        assert data["bytes"] == 6

    def test_filter_lines_only(self, client):
        resp = client.post(
            "/api/count?lines=true", data="hello\nworld\n"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {"lines": 2}

    def test_filter_words_and_chars(self, client):
        resp = client.post(
            "/api/count?words=true&chars=true", data="hello world\n"
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert data == {"words": 2, "chars": 12}

    def test_filter_all_fields(self, client):
        resp = client.post(
            "/api/count?lines=true&words=true&chars=true&bytes=true&max_line_length=true",
            data="hi\n",
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data) == 5

    def test_no_filter_returns_all(self, client):
        resp = client.post("/api/count", data="test\n")
        data = resp.get_json()
        assert set(data.keys()) == {"lines", "words", "chars", "bytes", "max_line_length"}


class TestCountFile:
    def test_upload_file(self, client):
        data = {"file": (io.BytesIO(b"hello world\nfoo bar baz\n"), "test.txt")}
        resp = client.post("/api/count/file", data=data, content_type="multipart/form-data")
        assert resp.status_code == 200
        result = resp.get_json()
        assert result["lines"] == 2
        assert result["words"] == 5
        assert result["chars"] == 24
        assert result["bytes"] == 24
        assert result["max_line_length"] == 11
        assert result["filename"] == "test.txt"

    def test_no_file_field(self, client):
        resp = client.post("/api/count/file", data={}, content_type="multipart/form-data")
        assert resp.status_code == 400
        assert "file" in resp.get_json()["error"].lower()

    def test_empty_filename(self, client):
        data = {"file": (io.BytesIO(b""), "")}
        resp = client.post("/api/count/file", data=data, content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_file_with_filter(self, client):
        data = {"file": (io.BytesIO(b"one two\nthree\n"), "sample.txt")}
        resp = client.post(
            "/api/count/file?words=true",
            data=data,
            content_type="multipart/form-data",
        )
        assert resp.status_code == 200
        result = resp.get_json()
        assert result == {"words": 3, "filename": "sample.txt"}


class TestErrorHandling:
    def test_wrong_method_on_count(self, client):
        resp = client.get("/api/count")
        assert resp.status_code == 405

    def test_wrong_method_on_count_file(self, client):
        resp = client.get("/api/count/file")
        assert resp.status_code == 405

    def test_not_found(self, client):
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
        assert "error" in resp.get_json()


class TestCORS:
    def test_cors_headers_present(self, client):
        resp = client.post(
            "/api/count",
            data="test",
            headers={"Origin": "http://example.com"},
        )
        assert "access-control-allow-origin" in {k.lower() for k in resp.headers.keys()}
