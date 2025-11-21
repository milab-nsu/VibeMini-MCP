from server import server as mcp
from services import mfa_service


@mcp.tool()
async def enable_email_mfa(project_key: str = "") -> str:
    """
    Enable Email Multi-Factor Authentication for a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with Email MFA configuration result
    """
    return await mfa_service.enable_email_mfa(project_key)


@mcp.tool()
async def enable_authenticator_mfa(project_key: str = "") -> str:
    """
    Enable Authenticator Multi-Factor Authentication for a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with Authenticator MFA configuration result
    """
    return await mfa_service.enable_authenticator_mfa(project_key)
