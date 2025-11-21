from server import server as mcp
from services import project_service


@mcp.tool()
async def get_projects(tenant_group_id: str = "", page: int = 0, page_size: int = 100) -> str:
    """
    Get projects from Selise Blocks API and extract application domains.

    Args:
        tenant_group_id: Tenant Group ID to filter projects (optional)
        page: Page number for pagination (default: 0)
        page_size: Number of items per page (default: 100)

    Returns:
        JSON string with projects data and extracted application domains
    """
    return await project_service.get_projects(tenant_group_id, page, page_size)


@mcp.tool()
async def set_application_domain(domain: str, tenant_id: str, project_name: str = "", tenant_group_id: str = "") -> str:
    """
    Manually set the application domain and tenant ID for repository creation.

    Args:
        domain: Application domain URL
        tenant_id: Tenant ID for the project
        project_name: Project name (optional)
        tenant_group_id: Tenant Group ID (optional)

    Returns:
        JSON string with confirmation
    """
    return await project_service.set_application_domain(domain, tenant_id, project_name, tenant_group_id)


@mcp.tool()
async def create_project(
    project_name: str,
    repo_name: str,
    repo_link: str,
    repo_id: str="Any",
    is_production: bool = False
) -> str:
    """
    Create a new project in Selise Cloud.

    Args:
        project_name: Name of the project to create
        repo_name: Repository name (e.g., 'username/repo')
        repo_link: Full GitHub repository URL
        repo_id: Repository ID from GitHub or Git provider
        is_production: Whether this is a production environment (default: False)

    Returns:
        JSON string with project creation results
    """
    return await project_service.create_project(project_name, repo_name, repo_link, repo_id, is_production)


@mcp.tool()
async def get_auth_status() -> str:
    """
    Check current authentication status and token validity.

    Returns:
        JSON string with authentication status
    """
    return await project_service.get_auth_status()


@mcp.tool()
async def get_global_state() -> str:
    """
    Get the current global state including authentication and application domain.

    Returns:
        JSON string with current global state
    """
    return await project_service.get_global_state()
