# Repository Overview

FlaskBlog is a modern blog application built with Flask 3.1+, SQLite3, and TailwindCSS/DaisyUI. The project uses `uv` package manager for dependency management and Tamga for comprehensive logging. It includes features like multi-language support, user authentication, post analytics, and theming.

## Python Style Guide

- **Modern Python:** Use Python 3.9+ features including f-strings and type hints where beneficial. Follow PEP 8 conventions.
- **Docstrings:** Focus on what the function does for the application, not implementation details. Keep them concise and business-focused.
- **Database Patterns:** Always use parameterized queries and close connections. Follow the existing pattern with `connection.set_trace_callback(Log.database)` for database operation logging.
- **Security:** Always check `session["userName"]` for authenticated routes and escape user content in templates with `{{ content | e }}`.
- **Simplicity:** Follow existing patterns in routes/ and utils/. New code should match the straightforward style already present.
- **Logging:** Use the Tamga logger (`utils.log.Log`) extensively. Key levels: `Log.info()` for general info, `Log.error()` for errors, `Log.success()` for successful operations, `Log.database()` for all DB queries, `Log.warning()` for warnings. Logging is critical for debugging and monitoring.

## Development Guidelines

- **Running the Project:** `cd app && uv run app.py`
- **URL Structure:** Maintain existing patterns: `/post/{slug}-{urlID}`, `/user/{username}`, `/category/{name}`
- **Translations:** Update all 11 language files in `translations/` when adding new UI text
- **Flash Messages:** Use the existing `flashMessage()` helper with proper page/message keys
- **Forms:** Create form classes in `utils/forms/` following WTForms patterns
