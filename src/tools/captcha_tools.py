from server import server as mcp
from services import captcha_service


@mcp.tool()
async def save_captcha_config(
    provider: str,
    site_key: str,
    secret_key: str,
    project_key: str = "",
    is_enable: bool = False
) -> str:
    """
    Save CAPTCHA configuration for Google reCAPTCHA or hCaptcha.

    Args:
        provider: CAPTCHA provider - "recaptcha" for Google reCAPTCHA or "hcaptcha" for hCaptcha
        site_key: Public site key from CAPTCHA provider console
        secret_key: Private secret key from CAPTCHA provider console
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        is_enable: Whether to enable the configuration immediately (default: False)

    Returns:
        JSON string with CAPTCHA configuration save result
    """
    return await captcha_service.save_captcha_config(provider, site_key, secret_key, project_key, is_enable)


@mcp.tool()
async def list_captcha_configs(project_key: str = "") -> str:
    """
    List all CAPTCHA configurations for a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with list of CAPTCHA configurations
    """
    return await captcha_service.list_captcha_configs(project_key)


@mcp.tool()
async def update_captcha_status(item_id: str, is_enable: bool, project_key: str = "") -> str:
    """
    Enable or disable a CAPTCHA configuration.

    Args:
        item_id: The ID of the CAPTCHA configuration to update
        is_enable: True to enable, False to disable the configuration
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with status update result
    """
    return await captcha_service.update_captcha_status(item_id, is_enable, project_key)
