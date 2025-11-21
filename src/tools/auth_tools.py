from server import server as mcp
from services import auth_service


@mcp.tool()
async def login(username: str, password: str) -> str:
    """
    Authenticate with Selise Blocks API and retrieve access tokens.

    Args:
        username: Email address for login
        password: Password for login

    Returns:
        JSON string with authentication status and token info
    """
    return await auth_service.login(username, password)


@mcp.tool()
async def activate_social_login(
    item_id: str = "682c40c3872fab1bc2cc8988",
    project_key: str = "",
    refresh_token_minutes: int = 300,
    access_token_minutes: int = 15,
    remember_me_minutes: int = 43200,
    allowed_grant_types: list = None,
    wrong_attempts_lock: int = 5,
    lock_duration_minutes: int = 5
) -> str:
    """
    Activate social login for the project by updating authentication configuration.

    Args:
        item_id: Configuration item ID (default: "682c40c3872fab1bc2cc8988")
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        refresh_token_minutes: Refresh token validity in minutes (default: 300)
        access_token_minutes: Access token validity in minutes (default: 15)
        remember_me_minutes: Remember me token validity in minutes (default: 43200)
        allowed_grant_types: List of allowed grant types (default: ["password", "refresh_token", "social"])
        wrong_attempts_lock: Number of wrong attempts to lock account (default: 5)
        lock_duration_minutes: Account lock duration in minutes (default: 5)

    Returns:
        JSON string with social login activation result
    """
    return await auth_service.activate_social_login(
        item_id,
        project_key,
        refresh_token_minutes,
        access_token_minutes,
        remember_me_minutes,
        allowed_grant_types,
        wrong_attempts_lock,
        lock_duration_minutes
    )


@mcp.tool()
async def get_authentication_config(project_key: str = "") -> str:
    """
    Get the current authentication configuration for the project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with current authentication configuration
    """
    return await auth_service.get_authentication_config(project_key)


@mcp.tool()
async def add_sso_credential(
    provider: str,
    client_id: str,
    client_secret: str,
    project_key: str = "",
    is_enable: bool = True,
    redirect_uri: str = ""
) -> str:
    """
    Add social login credentials for OAuth providers (Google, Facebook, GitHub, etc.).

    Args:
        provider: OAuth provider name (e.g., "google", "facebook", "github")
        client_id: OAuth client ID from provider console
        client_secret: OAuth client secret from provider console
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        is_enable: Whether to enable this SSO provider (default: True)
        redirect_uri: OAuth redirect URI (optional)

    Returns:
        JSON string with SSO credential save result
    """
    return await auth_service.add_sso_credential(
        provider,
        client_id,
        client_secret,
        project_key,
        is_enable,
        redirect_uri
    )
