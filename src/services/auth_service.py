import json
from datetime import timedelta, datetime
from typing import Optional
from utils import http_client, misc


async def get_authentication_tokens(username: str, password: str) -> dict:
    """
    Authenticate with Selise Blocks API and retrieve access tokens.
    Used by middleware - returns dict instead of JSON string.

    Args:
        username: Email address for login
        password: Password for login

    Returns:
        Dictionary with authentication tokens
    """
    try:
        login_data = await http_client.post(
            url=misc.API_CONFIG["LOGIN_URL"],
            data={
                "grant_type": "password",
                "username": username,
                "password": password,
            },
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        # Extract token information
        access_token = login_data.get("access_token")
        refresh_token = login_data.get("refresh_token")
        expires_in = login_data.get("expires_in", 8000)
        token_type = login_data.get("token_type", "bearer")

        if not access_token:
            return {
                "access_token": None,
                "refresh_token": None,
                "expires_at": None,
                "token_type": "bearer"
            }

        # Calculate expiration time with 5-minute buffer
        expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

        response = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "token_type": token_type,
        }

        # Update global auth state
        misc.auth_state.update(response)

        return response

    except Exception as e:
        return {
            "access_token": None,
            "refresh_token": None,
            "expires_at": None,
            "token_type": "bearer"
        }


async def login(username: str, password: str) -> str:
    """
    Authenticate with Selise Blocks API and retrieve access tokens.

    Args:
        username: Email address for login
        password: Password for login

    Returns:
        JSON string with authentication status and token info
    """
    try:
        login_payload = {
            "grant_type": "password",
            "username": username,
            "password": password
        }

        # Login endpoint uses form data, not JSON
        login_data = await http_client.post(
            url=misc.API_CONFIG["LOGIN_URL"],
            data=login_payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        # Extract token information
        access_token = login_data.get("access_token")
        refresh_token = login_data.get("refresh_token")
        expires_in = login_data.get("expires_in", 8000)
        token_type = login_data.get("token_type", "bearer")

        if not access_token:
            return json.dumps({
                "status": "error",
                "message": "Login failed. No access token received.",
                "response": login_data
            }, indent=2)

        # Calculate expiration time with 5-minute buffer
        expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

        # Update global auth state
        misc.auth_state.update({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "token_type": token_type
        })

        result = {
            "status": "success",
            "message": f"Login successful for {username}",
            "token_info": {
                "token_type": token_type,
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "has_refresh_token": refresh_token is not None
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during login: {str(e)}"
        }, indent=2)


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
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)

        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = misc.app_state["tenant_id"]

        # Set default allowed grant types if not provided
        if allowed_grant_types is None:
            allowed_grant_types = ["password", "refresh_token", "social"]

        # Prepare payload for social login activation
        config_payload = {
            "itemId": item_id,
            "refreshTokenValidForNumberMinutes": refresh_token_minutes,
            "accessTokenValidForNumberMinutes": access_token_minutes,
            "rememberMeRefreshTokenValidForNumberMinutes": remember_me_minutes,
            "allowedGrantTypes": allowed_grant_types,
            "getNumberOfWrongAttemptsToLockTheAccount": wrong_attempts_lock,
            "accountLockDurationInMinutes": lock_duration_minutes,
            "projectKey": project_key
        }

        response_data = await http_client.post(
            url=misc.API_CONFIG["UPDATE_CONFIG_URL"],
            json=config_payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        # Get the updated configuration to confirm changes
        try:
            config_result = await get_authentication_config(project_key)
            config_result_data = json.loads(config_result)
            updated_config = config_result_data.get("configuration") if config_result_data.get("status") == "success" else None
        except Exception as config_error:
            updated_config = f"Could not fetch updated config: {str(config_error)}"

        result = {
            "status": "success",
            "message": f"Social login activated successfully for project {project_key}",
            "config_details": {
                "item_id": item_id,
                "project_key": project_key,
                "allowed_grant_types": allowed_grant_types,
                "refresh_token_minutes": refresh_token_minutes,
                "access_token_minutes": access_token_minutes,
                "remember_me_minutes": remember_me_minutes
            },
            "response": response_data,
            "updated_configuration": updated_config
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error activating social login: {str(e)}"
        }, indent=2)


async def get_authentication_config(project_key: str = "") -> str:
    """
    Get the current authentication configuration for the project.
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)

        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = misc.app_state["tenant_id"]

        config_data = await http_client.get(
            url=misc.API_CONFIG["GET_CONFIG_URL"],
            params={"ProjectKey": project_key},
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": f"Authentication configuration retrieved successfully for project {project_key}",
            "project_key": project_key,
            "configuration": config_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting authentication config: {str(e)}"
        }, indent=2)


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
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)

        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = misc.app_state["tenant_id"]

        # Set default redirect URI if not provided
        if not redirect_uri and misc.app_state.get("application_domain"):
            redirect_uri = f"{misc.app_state['application_domain']}/auth/{provider}/callback"

        payload = {
            "projectKey": project_key,
            "provider": provider,
            "clientId": client_id,
            "clientSecret": client_secret,
            "isEnable": is_enable,
            "redirectUri": redirect_uri
        }

        sso_data = await http_client.post(
            url=misc.API_CONFIG["SAVE_SSO_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if sso_data.get("isSuccess", True):
            result = {
                "status": "success",
                "message": f"{provider.capitalize()} SSO credentials saved successfully",
                "config_details": {
                    "provider": provider,
                    "project_key": project_key,
                    "client_id": client_id[:20] + "..." if len(client_id) > 20 else client_id,
                    "is_enabled": is_enable,
                    "redirect_uri": redirect_uri
                },
                "response": sso_data
            }
        else:
            result = {
                "status": "error",
                "message": f"Failed to save {provider} SSO credentials",
                "errors": sso_data.get("errors"),
                "response": sso_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error saving SSO credentials: {str(e)}"
        }, indent=2)
