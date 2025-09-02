from flask import request
from utils.log import Log


def after_request_logger(response):
    """
    This function is used to log the response of an HTTP request.

    Parameters:
        response (Response): The response object returned by the HTTP request.

    Returns:
        Response: The response object returned by the HTTP request.
    """

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

    return response
