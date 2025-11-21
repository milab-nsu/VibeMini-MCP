import asyncio
from datetime import datetime
from typing import Any, Dict


auth_state = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": None,
    "token_type": "bearer",
}

app_state = {
    "application_domain": None,
    "tenant_id": None,
    "tenant_group_id": None,
    "project_name": None,
}

# API Configuration
API_CONFIG = {
    "LOGIN_URL": "https://api.seliseblocks.com/authentication/v1/OAuth/Token",
    "UPDATE_CONFIG_URL": "https://api.seliseblocks.com/authentication/v1/Configuration/Update",
    "GET_CONFIG_URL": "https://api.seliseblocks.com/authentication/v1/Configuration/Get",
    "SAVE_SSO_URL": "https://api.seliseblocks.com/authentication/v1/Social/SaveSsoCredential",
    "CREATE_URL": "https://api.seliseblocks.com/identifier/v1/Project/Create",
    "GET_PROJECTS_URL": "https://api.seliseblocks.com/identifier/v1/Project/Gets",
    "GET_ITEM_URL": "https://api.seliseblocks.com/identifier/v1/Project/Get",
    "CREATE_SCHEMA_URL": "https://api.seliseblocks.com/graphql/v1/schemas/info",
    "LIST_SCHEMAS_URL": "https://api.seliseblocks.com/graphql/v1/schemas",
    "SCHEMA_FIELDS_URL": "https://api.seliseblocks.com/graphql/v1/schemas/fields",
    "GET_SCHEMA_URL": "https://api.seliseblocks.com/graphql/v1/schemas",
    "DATA_GATEWAY_URL": "https://api.seliseblocks.com/graphql/v1/configurations/datasource",
    "SCHEMA_RELOAD_URL": "https://api.seliseblocks.com/graphql/v1/operations/schemas/reload",
    "CAPTCHA_SAVE_URL": "https://api.seliseblocks.com/captcha/v1/Configuration/Save",
    "CAPTCHA_LIST_URL": "https://api.seliseblocks.com/captcha/v1/Configuration/Gets",
    "CAPTCHA_UPDATE_STATUS_URL": "https://api.seliseblocks.com/captcha/v1/Configuration/UpdateStatus",
    "IAM_GET_ROLES_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetRoles",
    "IAM_CREATE_ROLE_URL": "https://api.seliseblocks.com/iam/v1/Resource/CreateRole",
    "IAM_GET_PERMISSIONS_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetPermissions",
    "IAM_CREATE_PERMISSION_URL": "https://api.seliseblocks.com/iam/v1/Resource/CreatePermission",
    "IAM_UPDATE_PERMISSION_URL": "https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission",
    "IAM_GET_RESOURCE_GROUPS_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups",
    "IAM_SET_ROLES_URL": "https://api.seliseblocks.com/iam/v1/Resource/SetRoles",
    "MFA_SAVE_URL": "https://api.seliseblocks.com/mfa/v1/Configuration/Save",
    "GITHUB_REPOS_URL": "https://api.seliseblocks.com/cloudbuild/v1/github/repos",
    "RUN_BUILD_URL": "https://api.seliseblocks.com/cloudbuild/v1/build/run-build",
    "UILM_GET_LANGUAGES_URL": "https://api.seliseblocks.com/uilm/v1/Language/Gets",
    "UILM_GET_MODULES_URL": "https://api.seliseblocks.com/uilm/v1/Module/Gets",
    "UILM_SAVE_KEY_URL": "https://api.seliseblocks.com/uilm/v1/Key/Save",
    "BLOCKS_KEY": "d7e5554c758541db8a18694b64ef423d",
    "HEADERS": {
        "x-blocks-key": "d7e5554c758541db8a18694b64ef423d",
        "Origin": "https://cloud.seliseblocks.com",
        "Referer": "https://cloud.seliseblocks.com/",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "dnt": "1",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    },
}


def is_token_valid() -> bool:
    """Check if the current access token is valid and not expired."""
    if not auth_state["access_token"] or not auth_state["expires_at"]:
        return False
    return datetime.now() < auth_state["expires_at"]


def get_auth_headers() -> dict:
    """Get headers with authorization if token is available."""
    headers = API_CONFIG["HEADERS"].copy()
    if auth_state["access_token"]:
        headers["Authorization"] = f"Bearer {auth_state['access_token']}"
    return headers


async def run_command(command: str) -> Dict[str, Any]:
    """Run a shell command asynchronously and return the result."""
    try:
        process = await asyncio.create_subprocess_shell(
            command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode("utf-8").strip(),
            "stderr": stderr.decode("utf-8").strip(),
        }
    except Exception as e:
        return {"success": False, "returncode": -1, "stdout": "", "stderr": str(e)}


# Documentation Repository Configuration
DOCS_CONFIG = {
    "BASE_URL": "https://raw.githubusercontent.com/mustavikhan05/selise-blocks-docs/master/",
    "TOPICS_JSON_URL": "https://raw.githubusercontent.com/mustavikhan05/selise-blocks-docs/master/topics.json"
}
