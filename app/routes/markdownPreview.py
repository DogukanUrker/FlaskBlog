"""
API endpoint for rendering markdown preview in the post editor.
"""

from flask import Blueprint, request, jsonify
from utils.markdown_renderer import SafeMarkdownRenderer

markdownPreviewBlueprint = Blueprint("markdownPreview", __name__)

# Initialize markdown renderer
markdown_renderer = SafeMarkdownRenderer()


@markdownPreviewBlueprint.route("/api/v1/markdown/preview", methods=["POST"])
def markdown_preview():
    """
    Renders markdown content and returns HTML for preview.

    Accepts JSON with 'content' field containing markdown text.
    Returns JSON with 'html' field containing sanitized HTML.

    Returns:
        JSON response with rendered HTML or error message
    """
    try:
        data = request.get_json()

        if not data or "content" not in data:
            return jsonify({"error": "No content provided"}), 400

        markdown_content = data["content"]

        # Render markdown to safe HTML
        rendered_html = markdown_renderer.render(markdown_content)

        return jsonify({"html": str(rendered_html)}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
