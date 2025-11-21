import json
from utils import http_client, misc


async def save_captcha_config(
    provider: str,
    site_key: str,
    secret_key: str,
    project_key: str = "",
    is_enable: bool = False
) -> str:
    """Save CAPTCHA configuration for Google reCAPTCHA or hCaptcha."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        if provider not in ["recaptcha", "hcaptcha"]:
            return json.dumps({
                "status": "error",
                "message": "Invalid provider. Must be 'recaptcha' for Google reCAPTCHA or 'hcaptcha' for hCaptcha."
            }, indent=2)

        payload = {
            "projectKey": project_key,
            "isEnable": is_enable,
            "provider": provider,
            "captchaKey": site_key,
            "captchaSecret": secret_key,
            "captchaGenerator": ""
        }

        save_data = await http_client.post(
            url=misc.API_CONFIG["CAPTCHA_SAVE_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if save_data.get("isSuccess"):
            result = {
                "status": "success",
                "message": f"{provider.capitalize()} CAPTCHA configuration saved successfully",
                "config_details": {
                    "provider": provider,
                    "project_key": project_key,
                    "is_enabled": is_enable,
                    "site_key": site_key[:20] + "..." if len(site_key) > 20 else site_key
                },
                "response": save_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to save CAPTCHA configuration",
                "errors": save_data.get("errors"),
                "response": save_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error saving CAPTCHA config: {str(e)}"}, indent=2)


async def list_captcha_configs(project_key: str = "") -> str:
    """List all CAPTCHA configurations for a project."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        configs_data = await http_client.get(
            url=misc.API_CONFIG["CAPTCHA_LIST_URL"],
            params={"ProjectKey": project_key},
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        configurations = configs_data.get("configurations", [])

        result = {
            "status": "success",
            "message": f"Found {len(configurations)} CAPTCHA configuration(s)",
            "project_key": project_key,
            "configurations": configurations,
            "summary": [
                {
                    "provider": config.get("provider"),
                    "status": "Enabled" if config.get("isEnable") else "Disabled",
                    "item_id": config.get("itemId"),
                    "created_date": config.get("createdDate")
                }
                for config in configurations
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error listing CAPTCHA configs: {str(e)}"}, indent=2)


async def update_captcha_status(item_id: str, is_enable: bool, project_key: str = "") -> str:
    """Enable or disable a CAPTCHA configuration."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "projectKey": project_key,
            "isEnable": is_enable,
            "itemId": item_id
        }

        update_data = await http_client.post(
            url=misc.API_CONFIG["CAPTCHA_UPDATE_STATUS_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if update_data.get("isSuccess"):
            status_text = "enabled" if is_enable else "disabled"
            result = {
                "status": "success",
                "message": f"CAPTCHA configuration {status_text} successfully",
                "config_details": {
                    "item_id": item_id,
                    "project_key": project_key,
                    "is_enabled": is_enable
                },
                "response": update_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to update CAPTCHA configuration status",
                "errors": update_data.get("errors"),
                "response": update_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error updating CAPTCHA status: {str(e)}"}, indent=2)
