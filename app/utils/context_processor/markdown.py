from utils.markdown_renderer import SafeMarkdownRenderer

_renderer = SafeMarkdownRenderer()


def markdown_processor():
    def render_markdown(text):
        return _renderer.render(text)

    return dict(render_markdown=render_markdown)
