import json
from utils import http_client, misc


async def list_roles(
    project_key: str = "",
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    sort_by: str = "Name",
    sort_descending: bool = False
) -> str:
    """List all roles for a project."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "projectKey": project_key,
            "page": page,
            "pageSize": page_size,
            "filter": {"search": search},
            "sort": {"property": sort_by, "isDescending": sort_descending}
        }

        roles_data = await http_client.post(
            url=misc.API_CONFIG["IAM_GET_ROLES_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        roles = roles_data.get("data", [])
        total_count = roles_data.get("totalCount", 0)

        result = {
            "status": "success",
            "message": f"Found {len(roles)} role(s) (total: {total_count})",
            "project_key": project_key,
            "total_count": total_count,
            "roles": roles,
            "summary": [
                {
                    "name": role.get("name"),
                    "slug": role.get("slug"),
                    "description": role.get("description"),
                    "permissions_count": role.get("count", 0),
                    "item_id": role.get("itemId"),
                    "created_date": role.get("createdDate")
                }
                for role in roles
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error listing roles: {str(e)}"}, indent=2)


async def create_role(name: str, description: str, slug: str, project_key: str = "") -> str:
    """Create a new role."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "name": name,
            "description": description,
            "slug": slug,
            "projectKey": project_key
        }

        create_data = await http_client.post(
            url=misc.API_CONFIG["IAM_CREATE_ROLE_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if create_data.get("isSuccess"):
            result = {
                "status": "success",
                "message": f"Role '{name}' created successfully",
                "role_details": {
                    "name": name,
                    "description": description,
                    "slug": slug,
                    "project_key": project_key,
                    "item_id": create_data.get("itemId")
                },
                "response": create_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to create role",
                "errors": create_data.get("errors"),
                "response": create_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error creating role: {str(e)}"}, indent=2)


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
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "page": page,
            "pageSize": page_size,
            "projectKey": project_key,
            "roles": [],
            "sort": {"property": sort_by, "isDescending": sort_descending},
            "filter": {
                "search": search,
                "isBuiltIn": is_built_in,
                "resourceGroup": resource_group
            }
        }

        permissions_data = await http_client.post(
            url=misc.API_CONFIG["IAM_GET_PERMISSIONS_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        permissions = permissions_data.get("data", [])
        total_count = permissions_data.get("totalCount", 0)

        result = {
            "status": "success",
            "message": f"Found {len(permissions)} permission(s) (total: {total_count})",
            "project_key": project_key,
            "total_count": total_count,
            "permissions": permissions,
            "summary": [
                {
                    "name": perm.get("name"),
                    "resource": perm.get("resource"),
                    "resource_group": perm.get("resourceGroup"),
                    "type": perm.get("type"),
                    "tags": perm.get("tags", []),
                    "is_built_in": perm.get("isBuiltIn"),
                    "item_id": perm.get("itemId"),
                    "created_date": perm.get("createdDate")
                }
                for perm in permissions
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error listing permissions: {str(e)}"}, indent=2)


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
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        if dependent_permissions is None:
            dependent_permissions = []

        payload = {
            "name": name,
            "type": type,
            "resource": resource,
            "resourceGroup": resource_group,
            "tags": tags,
            "description": description,
            "dependentPermissions": dependent_permissions,
            "projectKey": project_key,
            "isBuiltIn": is_built_in
        }

        create_data = await http_client.post(
            url=misc.API_CONFIG["IAM_CREATE_PERMISSION_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if create_data.get("isSuccess"):
            result = {
                "status": "success",
                "message": f"Permission '{name}' created successfully",
                "permission_details": {
                    "name": name,
                    "description": description,
                    "resource": resource,
                    "resource_group": resource_group,
                    "tags": tags,
                    "type": type,
                    "project_key": project_key,
                    "item_id": create_data.get("itemId")
                },
                "response": create_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to create permission",
                "errors": create_data.get("errors"),
                "response": create_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error creating permission: {str(e)}"}, indent=2)


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
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        if dependent_permissions is None:
            dependent_permissions = []

        payload = {
            "name": name,
            "type": type,
            "resource": resource,
            "resourceGroup": resource_group,
            "tags": tags,
            "description": description,
            "dependentPermissions": dependent_permissions,
            "projectKey": project_key,
            "isBuiltIn": is_built_in,
            "itemId": item_id
        }

        update_data = await http_client.post(
            url=misc.API_CONFIG["IAM_UPDATE_PERMISSION_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if update_data.get("isSuccess"):
            result = {
                "status": "success",
                "message": f"Permission '{name}' updated successfully",
                "permission_details": {
                    "item_id": item_id,
                    "name": name,
                    "description": description,
                    "resource": resource,
                    "resource_group": resource_group,
                    "tags": tags,
                    "type": type,
                    "project_key": project_key
                },
                "response": update_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to update permission",
                "errors": update_data.get("errors"),
                "response": update_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error updating permission: {str(e)}"}, indent=2)


async def get_resource_groups(project_key: str = "") -> str:
    """Get available resource groups for a project."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        groups_data = await http_client.get(
            url=f"{misc.API_CONFIG['IAM_GET_RESOURCE_GROUPS_URL']}?ProjectKey={project_key}",
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": f"Found {len(groups_data)} resource group(s)",
            "project_key": project_key,
            "resource_groups": groups_data,
            "summary": [
                {
                    "resource_group": group.get("resourceGroup"),
                    "count": group.get("count", 0)
                }
                for group in groups_data
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error getting resource groups: {str(e)}"}, indent=2)


async def set_role_permissions(
    role_slug: str,
    add_permissions: list = None,
    remove_permissions: list = None,
    project_key: str = ""
) -> str:
    """Assign or remove permissions from a role."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        if add_permissions is None:
            add_permissions = []
        if remove_permissions is None:
            remove_permissions = []

        payload = {
            "addPermissions": add_permissions,
            "removePermissions": remove_permissions,
            "projectKey": project_key,
            "slug": role_slug
        }

        set_data = await http_client.post(
            url=misc.API_CONFIG["IAM_SET_ROLES_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if set_data.get("success"):
            result = {
                "status": "success",
                "message": f"Role permissions updated successfully for '{role_slug}'",
                "role_details": {
                    "role_slug": role_slug,
                    "added_permissions": add_permissions,
                    "removed_permissions": remove_permissions,
                    "project_key": project_key
                },
                "response": set_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to update role permissions",
                "response": set_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error setting role permissions: {str(e)}"}, indent=2)


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
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "page": page,
            "pageSize": page_size,
            "roles": role_slugs,
            "projectKey": project_key,
            "sort": {"property": "Name", "isDescending": False},
            "filter": {
                "search": search,
                "isBuiltIn": is_built_in,
                "resourceGroup": resource_group
            }
        }

        permissions_data = await http_client.post(
            url=misc.API_CONFIG["IAM_GET_PERMISSIONS_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        permissions = permissions_data.get("data", [])
        total_count = permissions_data.get("totalCount", 0)

        result = {
            "status": "success",
            "message": f"Found {len(permissions)} permission(s) for role(s): {', '.join(role_slugs)} (total: {total_count})",
            "role_slugs": role_slugs,
            "project_key": project_key,
            "total_count": total_count,
            "permissions": permissions,
            "summary": [
                {
                    "name": perm.get("name"),
                    "roles": perm.get("roles", []),
                    "resource": perm.get("resource"),
                    "resource_group": perm.get("resourceGroup"),
                    "tags": perm.get("tags", []),
                    "item_id": perm.get("itemId"),
                    "created_date": perm.get("createdDate")
                }
                for perm in permissions
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error getting role permissions: {str(e)}"}, indent=2)
