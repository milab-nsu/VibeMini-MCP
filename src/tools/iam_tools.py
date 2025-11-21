from server import server as mcp
from services import iam_service


@mcp.tool()
async def list_roles(
    project_key: str = "",
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    sort_by: str = "Name",
    sort_descending: bool = False
) -> str:
    """List all roles for a project."""
    return await iam_service.list_roles(project_key, page, page_size, search, sort_by, sort_descending)


@mcp.tool()
async def create_role(name: str, description: str, slug: str, project_key: str = "") -> str:
    """Create a new role."""
    return await iam_service.create_role(name, description, slug, project_key)


@mcp.tool()
async def list_permissions(
    project_key: str = "",
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    sort_by: str = "Name",
    sort_descending: bool = False,
    is_built_in: str = "",
    resource_group: str = ""
) -> str:
    """List all permissions for a project."""
    return await iam_service.list_permissions(
        project_key, page, page_size, search, sort_by, sort_descending, is_built_in, resource_group
    )


@mcp.tool()
async def create_permission(
    name: str,
    description: str,
    resource: str,
    resource_group: str,
    tags: list,
    project_key: str = "",
    type: int = 3,
    dependent_permissions: list = None,
    is_built_in: bool = False
) -> str:
    """Create a new permission."""
    return await iam_service.create_permission(
        name, description, resource, resource_group, tags, project_key, type, dependent_permissions, is_built_in
    )


@mcp.tool()
async def update_permission(
    item_id: str,
    name: str,
    description: str,
    resource: str,
    resource_group: str,
    tags: list,
    project_key: str = "",
    type: int = 3,
    dependent_permissions: list = None,
    is_built_in: bool = False
) -> str:
    """Update an existing permission."""
    return await iam_service.update_permission(
        item_id, name, description, resource, resource_group, tags, project_key, type, dependent_permissions, is_built_in
    )


@mcp.tool()
async def get_resource_groups(project_key: str = "") -> str:
    """Get available resource groups for a project."""
    return await iam_service.get_resource_groups(project_key)


@mcp.tool()
async def set_role_permissions(
    role_slug: str,
    add_permissions: list = None,
    remove_permissions: list = None,
    project_key: str = ""
) -> str:
    """Assign or remove permissions from a role."""
    return await iam_service.set_role_permissions(role_slug, add_permissions, remove_permissions, project_key)


@mcp.tool()
async def get_role_permissions(
    role_slugs: list,
    project_key: str = "",
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    is_built_in: str = "",
    resource_group: str = ""
) -> str:
    """Get permissions assigned to specific role(s)."""
    return await iam_service.get_role_permissions(
        role_slugs, project_key, page, page_size, search, is_built_in, resource_group
    )
