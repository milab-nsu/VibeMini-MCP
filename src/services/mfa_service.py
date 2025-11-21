import json
from utils import http_client, misc


async def enable_email_mfa(project_key: str = "") -> str:
    """Enable Email Multi-Factor Authentication for a project."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "projectKey": project_key,
            "enableMfa": True,
            "userMfaType": [2]  # 2 represents email MFA
        }

        mfa_data = await http_client.post(
            url=misc.API_CONFIG["MFA_SAVE_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": "Email MFA has been enabled successfully",
            "project_key": project_key,
            "mfa_config": {
                "enabled": True,
                "type": "email",
                "type_code": 2
            },
            "response_data": mfa_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error enabling email MFA: {str(e)}"}, indent=2)


async def enable_authenticator_mfa(project_key: str = "") -> str:
    """Enable Authenticator Multi-Factor Authentication for a project."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "projectKey": project_key,
            "enableMfa": True,
            "userMfaType": [2, 1]  # 2 = email MFA, 1 = authenticator MFA
        }

        mfa_data = await http_client.post(
            url=misc.API_CONFIG["MFA_SAVE_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": "Authenticator MFA has been enabled successfully",
            "project_key": project_key,
            "mfa_config": {
                "enabled": True,
                "type": "authenticator",
                "type_code": 1,
                "includes_email": True
            },
            "response_data": mfa_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error enabling authenticator MFA: {str(e)}"}, indent=2)
