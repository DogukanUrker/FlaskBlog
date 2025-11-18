from flask import request, session
from utils.log import Log
from utils.securityAuditLogger import SecurityAuditLogger


def afterRequestLogger(response):
    """
    This function is used to log the response of an HTTP request.

    Parameters:
        response (Response): The response object returned by the HTTP request.

    Returns:
        Response: The response object returned by the HTTP request.
    """

    # Extract status code from response
    status_code = response.status_code

    if response.status == "200 OK":
        Log.success(
            f"Adress: {request.remote_addr} | Method: {request.method} | Path: {request.path} | Scheme: {request.scheme} | Status: {response.status} | Content Length: {response.content_length} | Referrer: {request.referrer} | User Agent: {request.user_agent}",
        )
    elif response.status == "404 NOT FOUND":
        Log.error(
            f"Adress: {request.remote_addr} | Method: {request.method} | Path: {request.path} | Scheme: {request.scheme} | Status: {response.status} | Content Length: {response.content_length} | Referrer: {request.referrer} | User Agent: {request.user_agent}",
        )
    else:
        Log.info(
            f"Adress: {request.remote_addr} | Method: {request.method} | Path: {request.path} | Scheme: {request.scheme} | Status: {response.status} | Content Length: {response.content_length} | Referrer: {request.referrer} | User Agent: {request.user_agent}",
        )

    # Log important page accesses to security audit database
    # Only log admin panel pages, login/logout, and sensitive operations
    sensitive_paths = ['/admin', '/login', '/logout', '/signup', '/password-reset']
    path_is_sensitive = any(
        request.path.startswith(sensitive_path) for sensitive_path in sensitive_paths
    )

    # Also log static files to reduce database bloat
    is_static = request.path.startswith('/static')

    if path_is_sensitive and not is_static:
        userName = session.get('userName', None)
        SecurityAuditLogger.log_page_access(
            userName=userName,
            ip_address=request.remote_addr,
            user_agent=str(request.user_agent),
            path=request.path,
            method=request.method,
            status_code=status_code
        )

    return response
