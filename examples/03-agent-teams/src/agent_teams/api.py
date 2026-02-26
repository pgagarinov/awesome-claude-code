from flask import Flask, jsonify, request
from flask_cors import CORS

from agent_teams.cli import count_content


def create_app():
    app = Flask(__name__)
    CORS(app)

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e.description)), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify(error="Not found"), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify(error="Method not allowed"), 405

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify(error="Internal server error"), 500

    @app.get("/api/health")
    def health():
        return jsonify(status="ok")

    @app.post("/api/count")
    def count_text():
        body = request.get_data(as_text=True)
        if not body and not request.content_length:
            return jsonify(error="Request body is empty"), 400

        lines, words, chars, bytes_, max_line_length = count_content(body)
        result = _filter_counts(lines, words, chars, bytes_, max_line_length)
        return jsonify(result)

    @app.post("/api/count/file")
    def count_file():
        if "file" not in request.files:
            return jsonify(error="No file provided. Use multipart field 'file'."), 400

        uploaded = request.files["file"]
        if uploaded.filename == "":
            return jsonify(error="No file selected"), 400

        content = uploaded.read().decode("utf-8", errors="replace")
        lines, words, chars, bytes_, max_line_length = count_content(content)
        result = _filter_counts(lines, words, chars, bytes_, max_line_length)
        result["filename"] = uploaded.filename
        return jsonify(result)

    def _filter_counts(lines, words, chars, bytes_, max_line_length):
        all_counts = {
            "lines": lines,
            "words": words,
            "chars": chars,
            "bytes": bytes_,
            "max_line_length": max_line_length,
        }

        requested = {
            k for k in all_counts if request.args.get(k, "").lower() == "true"
        }

        if not requested:
            return all_counts

        return {k: v for k, v in all_counts.items() if k in requested}

    return app
