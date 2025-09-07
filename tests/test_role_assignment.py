#!/usr/bin/env python3
"""
Test script for IAM Role-Permission Assignment tools - Phase 4 Implementation
Tests set_role_permissions and get_role_permissions functions independently before MCP integration.
"""

import httpx
import json
import asyncio

# Hardcoded auth for testing (replace with actual token)
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJkN2U1NTU0Yzc1ODU0MWRiOGExODY5NGI2NGVmNDIzZCIsInN1YiI6ImJsb2Nrc3wwNDQ4YWFlNS0xNTE4LTQxZDgtYTg3MC02NGE4Y2M3NWIxMDciLCJ1c2VyX2lkIjoiMDQ0OGFhZTUtMTUxOC00MWQ4LWE4NzAtNjRhOGNjNzViMTA3IiwiaWF0IjoxNzU3MTg4MDQ5LCJvcmdfaWQiOiJkZWZhdWx0IiwiZW1haWwiOiJtdXN0YXZpa2hhbjA1QGdtYWlsLmNvbSIsInVzZXJfbmFtZSI6Im11c3RhdmlraGFuMDVAZ21haWwuY29tIiwibmFtZSI6Ik11c3RhdmkgS2hhbiIsInBob25lIjoiIiwibmJmIjoxNzU3MTg4MDQ5LCJleHAiOjE3NTc2NjgwNDksImlzcyI6IlNlbGlzZS1CbG9ja3MiLCJhdWQiOiJodHRwczovL2Nsb3VkLnNlbGlzZWJsb2Nrcy5jb20ifQ.r5Ta6aRo7oxg36-7RGUkbV-rrKeJlxeC5ZtI7a3NmYxCM84T7nSdHBJvQRQLWZnpP3R6b5iXbAjpOEqx0BVER-LN9NNYg8YWAYY9lomtvf7Ad5GCInbM4HlZ-SyuCb6oGA2e03ywgjgSBdZD7Wn31Iou2UjmQcozlqVGbueEwF5IwMDWHQoibNOA9LfFX_9fHfB_9WUa7EgOR6CERgZ1lC1UyBFz7MKT3F5qqD42vJaDRDBry0d3XTFEntMtvEevDnUcsdCzV-F_EnebuGI8OOHnv7yZpWE0fvEt1OfnX11hnT6eOXvGQv4Jwnyr0Gd1NdYVzrNCe_f2l6ediaGALw"
PROJECT_KEY = "95E5FD12E64E429295758B2CB1EA29D2"  # MyTodoApp project

# API Configuration
IAM_SET_ROLES_URL = "https://api.seliseblocks.com/iam/v1/Resource/SetRoles"
IAM_GET_PERMISSIONS_URL = "https://api.seliseblocks.com/iam/v1/Resource/GetPermissions"

def get_headers():
    """Get headers with authorization."""
    return {
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://cloud.seliseblocks.com",
        "priority": "u=1, i",
        "referer": "https://cloud.seliseblocks.com/",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "x-blocks-key": "d7e5554c758541db8a18694b64ef423d"
    }


async def set_role_permissions(
    role_slug: str,
    add_permissions: list = None,
    remove_permissions: list = None,
    project_key: str = PROJECT_KEY
) -> str:
    """
    Assign or remove permissions from a role.
    
    Args:
        role_slug: Role slug identifier
        add_permissions: List of permission IDs to add to the role (default: [])
        remove_permissions: List of permission IDs to remove from the role (default: [])
        project_key: Project key (tenant ID)
    
    Returns:
        JSON string with role permission assignment result
    """
    try:
        if add_permissions is None:
            add_permissions = []
        if remove_permissions is None:
            remove_permissions = []
            
        headers = get_headers()
        
        payload = {
            "addPermissions": add_permissions,
            "removePermissions": remove_permissions,
            "projectKey": project_key,
            "slug": role_slug
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IAM_SET_ROLES_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            set_data = response.json()
        
        if set_data.get("success"):
            # Get updated permissions to show the result
            try:
                updated_result = await get_role_permissions([role_slug], project_key)
                updated_data = json.loads(updated_result)
                updated_permissions = updated_data.get("permissions", []) if updated_data.get("status") == "success" else []
            except Exception:
                updated_permissions = []
            
            result = {
                "status": "success",
                "message": f"Role permissions updated successfully for '{role_slug}'",
                "role_details": {
                    "role_slug": role_slug,
                    "added_permissions": add_permissions,
                    "removed_permissions": remove_permissions,
                    "project_key": project_key
                },
                "response": set_data,
                "updated_permissions": updated_permissions
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to update role permissions",
                "response": set_data
            }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error setting role permissions: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error setting role permissions: {str(e)}"
        }, indent=2)


async def get_role_permissions(
    role_slugs: list,
    project_key: str = PROJECT_KEY,
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    is_built_in: str = "",
    resource_group: str = ""
) -> str:
    """
    Get permissions assigned to specific role(s).
    
    Args:
        role_slugs: List of role slugs to filter by
        project_key: Project key (tenant ID)
        page: Page number (default: 0)
        page_size: Number of items per page (default: 10)
        search: Search filter (default: "")
        is_built_in: Filter by built-in status (default: "")
        resource_group: Filter by resource group (default: "")
    
    Returns:
        JSON string with role permissions result
    """
    try:
        headers = get_headers()
        
        payload = {
            "page": page,
            "pageSize": page_size,
            "roles": role_slugs,
            "projectKey": project_key,
            "sort": {
                "property": "Name",
                "isDescending": False
            },
            "filter": {
                "search": search,
                "isBuiltIn": is_built_in,
                "resourceGroup": resource_group
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IAM_GET_PERMISSIONS_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            permissions_data = response.json()
        
        permissions = permissions_data.get("data", [])
        total_count = permissions_data.get("totalCount", 0)
        
        result = {
            "status": "success",
            "message": f"Found {len(permissions)} permission(s) for role(s): {', '.join(role_slugs)} (total: {total_count})",
            "role_slugs": role_slugs,
            "project_key": project_key,
            "total_count": total_count,
            "permissions": permissions,
            "summary": []
        }
        
        # Add summary for easier reading
        for perm in permissions:
            result["summary"].append({
                "name": perm.get("name"),
                "roles": perm.get("roles", []),
                "resource": perm.get("resource"),
                "resource_group": perm.get("resourceGroup"),
                "tags": perm.get("tags", []),
                "item_id": perm.get("itemId"),
                "created_date": perm.get("createdDate")
            })
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error getting role permissions: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting role permissions: {str(e)}"
        }, indent=2)


async def main():
    """Test all role-permission assignment functions."""
    print("🔗 IAM Role-Permission Assignment Test Suite")
    print("=" * 50)
    
    # Test 1: Get current role permissions for admin and moderator
    print("\n1️⃣ Testing get_role_permissions for admin...")
    admin_result = await get_role_permissions(["admin"])
    print(admin_result)
    
    print("\n2️⃣ Testing get_role_permissions for moderator...")
    moderator_result = await get_role_permissions(["moderator"])
    print(moderator_result)
    
    # Test 3: Assign permission to editor role (currently has none)
    print("\n3️⃣ Testing set_role_permissions - assign permission to editor...")
    assign_result = await set_role_permissions(
        role_slug="editor",
        add_permissions=["8f1c10cb-15cd-43f6-80bc-a812d4f980ca"]  # master_access permission
    )
    print(assign_result)
    
    # Test 4: Get permissions for multiple roles at once
    print("\n4️⃣ Testing get_role_permissions for multiple roles...")
    multi_result = await get_role_permissions(["admin", "editor", "moderator"])
    print(multi_result)
    
    # Test 5: Remove permission from editor role
    print("\n5️⃣ Testing set_role_permissions - remove permission from editor...")
    remove_result = await set_role_permissions(
        role_slug="editor",
        remove_permissions=["8f1c10cb-15cd-43f6-80bc-a812d4f980ca"]  # master_access permission
    )
    print(remove_result)
    
    # Test 6: Verify editor role has no permissions again
    print("\n6️⃣ Verifying editor role permissions after removal...")
    final_editor_result = await get_role_permissions(["editor"])
    print(final_editor_result)
    
    print("\n✅ Role-Permission Assignment Test Suite completed!")


if __name__ == "__main__":
    asyncio.run(main())