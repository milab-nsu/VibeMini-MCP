#!/usr/bin/env python3
"""
Test script for IAM Permission Management tools - Phase 4 Implementation
Tests list_permissions, create_permission, update_permission, and get_resource_groups functions independently before MCP integration.
"""

import httpx
import json
import asyncio

# Hardcoded auth for testing (replace with actual token)
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJkN2U1NTU0Yzc1ODU0MWRiOGExODY5NGI2NGVmNDIzZCIsInN1YiI6ImJsb2Nrc3wwNDQ4YWFlNS0xNTE4LTQxZDgtYTg3MC02NGE4Y2M3NWIxMDciLCJ1c2VyX2lkIjoiMDQ0OGFhZTUtMTUxOC00MWQ4LWE4NzAtNjRhOGNjNzViMTA3IiwiaWF0IjoxNzU3MjAyOTAxLCJvcmdfaWQiOiJkZWZhdWx0IiwiZW1haWwiOiJtdXN0YXZpa2hhbjA1QGdtYWlsLmNvbSIsInVzZXJfbmFtZSI6Im11c3RhdmlraGFuMDVAZ21haWwuY29tIiwibmFtZSI6Ik11c3RhdmkgS2hhbiIsInBob25lIjoiIiwibmJmIjoxNzU3MjAyOTAxLCJleHAiOjE3NTc2ODI5MDEsImlzcyI6IlNlbGlzZS1CbG9ja3MiLCJhdWQiOiJodHRwczovL2Nsb3VkLnNlbGlzZWJsb2Nrcy5jb20ifQ.nUCHEVRpFlf0UzSjsNrenIVUuv4C84s7C070LVw4YjTmxXVgwJGGiaeRnavQ_mlJfreLekF0TWMD-CDGyK7oim0fTGPfb4ngQfrJuJyPB8WRqrP1IN1f9s857NxTi1VY2VcReLKV3dfPEKnXtii6JWD4MOaMYz1fIDFh_MSAJPKf-2dpybwXaPqqIWgdFK5PWt2yPtfoy02y83t6L3mklvYP66L5vs55Br4CbGYw1vp9jve6SWpjfibhJTuQ7NtULdjgjlduwHBVgxdeWZNyBxpBVCmy1wyij340SGVhgrgZ3uS-ksz2YGxV1NVGDwLUikzIj4dADWX-mnH3embjnw"
PROJECT_KEY = "95E5FD12E64E429295758B2CB1EA29D2"  # MyTodoApp project

# API Configuration
IAM_GET_PERMISSIONS_URL = "https://api.seliseblocks.com/iam/v1/Resource/GetPermissions"
IAM_CREATE_PERMISSION_URL = "https://api.seliseblocks.com/iam/v1/Resource/CreatePermission"
IAM_UPDATE_PERMISSION_URL = "https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission"
IAM_GET_RESOURCE_GROUPS_URL = "https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups"

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


async def list_permissions(
    project_key: str = PROJECT_KEY,
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    sort_by: str = "Name",
    sort_descending: bool = False,
    is_built_in: str = "",
    resource_group: str = ""
) -> str:
    """
    List all permissions for a project.
    
    Args:
        project_key: Project key (tenant ID)
        page: Page number (default: 0)
        page_size: Number of items per page (default: 10)
        search: Search filter (default: "")
        sort_by: Field to sort by (default: "Name")
        sort_descending: Sort order (default: false)
        is_built_in: Filter by built-in status (default: "")
        resource_group: Filter by resource group (default: "")
    
    Returns:
        JSON string with permission list result
    """
    try:
        headers = get_headers()
        
        payload = {
            "page": page,
            "pageSize": page_size,
            "projectKey": project_key,
            "roles": [],
            "sort": {
                "property": sort_by,
                "isDescending": sort_descending
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
            "message": f"Found {len(permissions)} permission(s) (total: {total_count})",
            "project_key": project_key,
            "total_count": total_count,
            "permissions": permissions,
            "summary": []
        }
        
        # Add summary for easier reading
        for perm in permissions:
            result["summary"].append({
                "name": perm.get("name"),
                "resource": perm.get("resource"),
                "resource_group": perm.get("resourceGroup"),
                "type": perm.get("type"),
                "tags": perm.get("tags", []),
                "is_built_in": perm.get("isBuiltIn"),
                "item_id": perm.get("itemId"),
                "created_date": perm.get("createdDate")
            })
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error listing permissions: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error listing permissions: {str(e)}"
        }, indent=2)


async def create_permission(
    name: str,
    description: str,
    resource: str,
    resource_group: str,
    tags: list,
    project_key: str = PROJECT_KEY,
    type: int = 3,
    dependent_permissions: list = None,
    is_built_in: bool = False
) -> str:
    """
    Create a new permission.
    
    Args:
        name: Permission name
        description: Permission description
        resource: Resource name (arbitrary string)
        resource_group: Resource group name (arbitrary string)
        tags: List of action tags (e.g., ["create", "read", "update", "delete"])
        project_key: Project key (tenant ID)
        type: Permission type (default: 3 for "Data protection")
        dependent_permissions: List of dependent permission IDs (default: [])
        is_built_in: Whether it's a built-in permission (default: false)
    
    Returns:
        JSON string with permission creation result
    """
    try:
        if dependent_permissions is None:
            dependent_permissions = []
            
        headers = get_headers()
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IAM_CREATE_PERMISSION_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            create_data = response.json()
        
        if create_data.get("isSuccess"):
            # Get updated permission list to show the result
            try:
                list_result = await list_permissions(project_key)
                list_data = json.loads(list_result)
                updated_permissions = list_data.get("permissions", []) if list_data.get("status") == "success" else []
            except Exception:
                updated_permissions = []
            
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
                "response": create_data,
                "updated_permissions": updated_permissions
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to create permission",
                "errors": create_data.get("errors"),
                "response": create_data
            }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error creating permission: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error creating permission: {str(e)}"
        }, indent=2)


async def update_permission(
    item_id: str,
    name: str,
    description: str,
    resource: str,
    resource_group: str,
    tags: list,
    project_key: str = PROJECT_KEY,
    type: int = 3,
    dependent_permissions: list = None,
    is_built_in: bool = False
) -> str:
    """
    Update an existing permission.
    
    Args:
        item_id: The ID of the permission to update
        name: Permission name
        description: Permission description
        resource: Resource name (arbitrary string)
        resource_group: Resource group name (arbitrary string)
        tags: List of action tags (e.g., ["create", "read", "update", "delete"])
        project_key: Project key (tenant ID)
        type: Permission type (default: 3 for "Data protection")
        dependent_permissions: List of dependent permission IDs (default: [])
        is_built_in: Whether it's a built-in permission (default: false)
    
    Returns:
        JSON string with permission update result
    """
    try:
        if dependent_permissions is None:
            dependent_permissions = []
            
        headers = get_headers()
        
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
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IAM_UPDATE_PERMISSION_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            update_data = response.json()
        
        if update_data.get("isSuccess"):
            # Get updated permission list to confirm the change
            try:
                list_result = await list_permissions(project_key)
                list_data = json.loads(list_result)
                updated_permissions = list_data.get("permissions", []) if list_data.get("status") == "success" else []
            except Exception:
                updated_permissions = []
            
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
                "response": update_data,
                "updated_permissions": updated_permissions
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to update permission",
                "errors": update_data.get("errors"),
                "response": update_data
            }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error updating permission: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error updating permission: {str(e)}"
        }, indent=2)


async def get_resource_groups(project_key: str = PROJECT_KEY) -> str:
    """
    Get available resource groups for a project.
    
    Args:
        project_key: Project key (tenant ID)
    
    Returns:
        JSON string with resource groups result
    """
    try:
        headers = get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{IAM_GET_RESOURCE_GROUPS_URL}?ProjectKey={project_key}",
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            groups_data = response.json()
        
        result = {
            "status": "success",
            "message": f"Found {len(groups_data)} resource group(s)",
            "project_key": project_key,
            "resource_groups": groups_data,
            "summary": []
        }
        
        # Add summary for easier reading
        for group in groups_data:
            result["summary"].append({
                "resource_group": group.get("resourceGroup"),
                "count": group.get("count", 0)
            })
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error getting resource groups: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting resource groups: {str(e)}"
        }, indent=2)


async def main():
    """Test all permission management functions."""
    print("🔍 IAM Permission Management Test Suite")
    print("=" * 50)
    
    # Test 1: Get resource groups
    print("\n1️⃣ Testing get_resource_groups...")
    groups_result = await get_resource_groups()
    print(groups_result)
    
    # Test 2: List existing permissions
    print("\n2️⃣ Testing list_permissions...")
    list_result = await list_permissions()
    print(list_result)
    
    # Test 3: Create a new permission
    print("\n3️⃣ Testing create_permission...")
    create_result = await create_permission(
        name="automation_test",
        description="Test permission created by automated script",
        resource="AutomationResource",
        resource_group="AutomationGroup",
        tags=["create", "read", "update", "delete"]
    )
    print(create_result)
    
    # Test 4: Update the permission we just created
    print("\n4️⃣ Testing update_permission...")
    # Extract item_id from create result
    create_data = json.loads(create_result)
    if create_data.get("status") == "success":
        item_id = create_data["permission_details"]["item_id"]
        
        update_result = await update_permission(
            item_id=item_id,
            name="automation_test_updated",
            description="Updated test permission",
            resource="UpdatedResource",
            resource_group="UpdatedGroup",
            tags=["read", "update", "admin"]
        )
        print(update_result)
    else:
        print("❌ Skipping update test - create failed")
    
    # Test 5: List permissions again to confirm changes
    print("\n5️⃣ Verifying permission changes...")
    final_list_result = await list_permissions()
    print(final_list_result)
    
    print("\n✅ Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())