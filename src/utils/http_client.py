from typing import Any, Optional
import httpx
from utils.logger import get_logger

logger = get_logger(__name__)


async def get(
    url: str,
    params: Optional[dict] = None,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send a GET request and return the JSON response."""
    return await send(
        method="GET",
        url=url,
        params=params,
        blocks_key=blocks_key,
        access_token=access_token,
    )


async def post(
    url: str,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send a POST request and return the JSON response."""
    return await send(
        method="POST",
        url=url,
        json=json,
        data=data,
        blocks_key=blocks_key,
        access_token=access_token,
    )


async def put(
    url: str,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send a PUT request and return the JSON response."""
    return await send(
        method="PUT",
        url=url,
        json=json,
        data=data,
        blocks_key=blocks_key,
        access_token=access_token,
    )


async def delete(
    url: str,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send a DELETE request and return the JSON response."""
    return await send(
        method="DELETE",
        url=url,
        blocks_key=blocks_key,
        access_token=access_token,
    )


async def send(
    method: str,
    url: str,
    json: Optional[dict] = None,
    data: Optional[dict] = None,
    params: Optional[dict] = None,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send an HTTP request and return the JSON response."""
    # Determine content type
    content_type = "application/json"
    if data is not None:
        content_type = "application/x-www-form-urlencoded"
        json = None

    headers = _get_headers(
        content_type=content_type,
        authorization=access_token,
        blocks_key=blocks_key,
    )

    request = _get_request(method, url, headers, json=json, data=data, params=params)
    return await _send_request(request)


async def _send_request(request: httpx.Request) -> Any:
    """Send an HTTP request and return the response."""
    logger.debug(f"Sending {request.method} request to {request.url}")

    try:
        with httpx.Client() as client:
            response = client.send(request)

            logger.debug(f"HTTP response status: {response.status_code}")

            # Check if response is successful
            response.raise_for_status()

            # Log successful response
            logger.info(f"HTTP request successful - Status: {response.status_code}")

            try:
                response_data = response.json()
                logger.debug(f"Response data: {response_data}")
            except Exception as e:
                logger.warning(f"Could not parse response as JSON: {e}")

            return response.json() if response.content else None

    except httpx.TimeoutException as e:
        logger.error(f"HTTP request timeout: {e}", exc_info=True)
        raise
    except httpx.NetworkError as e:
        logger.error(f"Network error during HTTP request: {e}", exc_info=True)
        raise
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error {e.response.status_code}: {e.response.text}", exc_info=True
        )
        raise
    except Exception as e:
        logger.error("Unexpected error during HTTP request", exc_info=True)
        raise


def _get_headers(
    content_type: str = "application/json",
    authorization: Optional[str] = None,
    blocks_key: Optional[str] = None,
) -> dict[str, str]:
    """Set up headers for the request."""
    headers = {
        "Content-Type": content_type,
    }

    # Only add headers if they have valid values
    if authorization:
        headers["Authorization"] = f"Bearer {authorization}"

    if blocks_key:
        headers["X-Blocks-Key"] = blocks_key

    return headers


def _get_request(
    method: str,
    url: str,
    headers: dict,
    json: Optional[dict],
    data: Optional[dict],
    params: Optional[dict] = None,
) -> httpx.Request:
    """Set up an HTTP request."""
    return httpx.Request(
        method, url, headers=headers, data=data, json=json, params=params
    )


# Legacy function for backward compatibility
async def send_json_request(
    method: str,
    url: str,
    json: dict,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send a JSON request (legacy function)."""
    return await send(
        method=method,
        url=url,
        json=json,
        blocks_key=blocks_key,
        access_token=access_token,
    )


async def send_data_request(
    method: str,
    url: str,
    data: dict,
    blocks_key: Optional[str] = None,
    access_token: Optional[str] = None,
) -> Any:
    """Send a form data request (legacy function)."""
    return await send(
        method=method,
        url=url,
        data=data,
        blocks_key=blocks_key,
        access_token=access_token,
    )
