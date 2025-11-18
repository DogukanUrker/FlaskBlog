"""
API endpoint for rendering markdown preview in the post editor.
"""

from flask import Blueprint, request, jsonify, render_template, session
from markupsafe import escape
from utils.markdown_renderer import SafeMarkdownRenderer
from utils.log import Log

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


@markdownPreviewBlueprint.route("/preview/post", methods=["GET", "POST"])
def preview_post_page():
    """
    Full-page preview of post with all content.

    POST: Accepts form data and stores in session, then redirects to GET
    GET: Displays stored preview from session

    Returns:
        Rendered preview page template
    """
    if request.method == "POST":
        # Store preview data in session
        session["preview_data"] = {
            "title": request.form.get("postTitle", ""),
            "tags": request.form.get("postTags", ""),
            "abstract": request.form.get("postAbstract", ""),
            "content": request.form.get("postContent", ""),
            "category": request.form.get("postCategory", ""),
        }

        Log.info(f"Preview data stored for user: {session.get('userName', 'anonymous')}")

        # Return success response for AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"success": True, "url": "/preview/post"}), 200

        # Redirect for regular form submission
        from flask import redirect
        return redirect("/preview/post")

    # GET request - display preview
    preview_data = session.get("preview_data", {})

    if not preview_data:
        Log.warning("No preview data found in session")
        return render_template(
            "previewPost.html",
            title="",
            tags="",
            abstract="",
            content="",
            category="",
            rendered_content="",
            empty=True
        )

    # Render markdown content
    content = preview_data.get("content", "")
    rendered_content = markdown_renderer.render(content) if content else ""

    Log.success(f"Rendering preview page with title: {preview_data.get('title', 'Untitled')}")

    return render_template(
        "previewPost.html",
        title=preview_data.get("title", ""),
        tags=preview_data.get("tags", ""),
        abstract=preview_data.get("abstract", ""),
        content=preview_data.get("content", ""),
        category=preview_data.get("category", ""),
        rendered_content=rendered_content,
        empty=False
    )
