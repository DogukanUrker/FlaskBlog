"""
API endpoint for rendering markdown preview in the post editor.
"""

from flask import Blueprint, request, jsonify, render_template_string
from markupsafe import escape
from utils.markdown_renderer import SafeMarkdownRenderer

markdownPreviewBlueprint = Blueprint("markdownPreview", __name__)

# Initialize markdown renderer
markdown_renderer = SafeMarkdownRenderer()


@markdownPreviewBlueprint.route("/api/v1/markdown/preview", methods=["POST"])
def markdown_preview():
    """
    Renders markdown content and returns HTML for preview.

    Accepts JSON with fields: title, tags, abstract, content
    Returns JSON with 'html' field containing complete post preview.

    Returns:
        JSON response with rendered HTML or error message
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Extract fields
        title = escape(data.get("title", "")).strip()
        tags = escape(data.get("tags", "")).strip()
        abstract = escape(data.get("abstract", "")).strip()
        content = data.get("content", "").strip()

        # Render markdown content to safe HTML
        rendered_content = markdown_renderer.render(content) if content else ""

        # Build complete preview HTML
        preview_html = f"""
        <div class="post-preview-container">
            <h1 class="preview-title">{title if title else '<span class="preview-empty">No title yet</span>'}</h1>

            {f'<div class="preview-tags"><i class="ti ti-tags"></i> {tags.replace(",", ", ")}</div>' if tags else '<div class="preview-tags preview-empty"><i class="ti ti-tags"></i> No tags</div>'}

            {f'<div class="preview-abstract">{abstract}</div>' if abstract else '<div class="preview-abstract preview-empty">No abstract</div>'}

            <div class="divider"></div>

            <div class="markdown-content">
                {rendered_content if content else '<div class="preview-empty">No content yet. Start writing to see the preview.</div>'}
            </div>
        </div>
        """

        return jsonify({"html": preview_html}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
