#!/usr/bin/env python3
"""
Test script for IAM Role Management tools - Phase 4 Implementation
Tests both list_roles and create_role functions independently before MCP integration.
"""

import httpx
import json
import asyncio

# Hardcoded auth for testing (replace with actual token)
ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0ZW5hbnRfaWQiOiJkN2U1NTU0Yzc1ODU0MWRiOGExODY5NGI2NGVmNDIzZCIsInN1YiI6ImJsb2Nrc3wwNDQ4YWFlNS0xNTE4LTQxZDgtYTg3MC02NGE4Y2M3NWIxMDciLCJ1c2VyX2lkIjoiMDQ0OGFhZTUtMTUxOC00MWQ4LWE4NzAtNjRhOGNjNzViMTA3IiwiaWF0IjoxNzU3MjAxMzUzLCJvcmdfaWQiOiJkZWZhdWx0IiwiZW1haWwiOiJtdXN0YXZpa2hhbjA1QGdtYWlsLmNvbSIsInVzZXJfbmFtZSI6Im11c3RhdmlraGFuMDVAZ21haWwuY29tIiwibmFtZSI6Ik11c3RhdmkgS2hhbiIsInBob25lIjoiIiwibmJmIjoxNzU3MjAxMzUzLCJleHAiOjE3NTc2ODEzNTMsImlzcyI6IlNlbGlzZS1CbG9ja3MiLCJhdWQiOiJodHRwczovL2Nsb3VkLnNlbGlzZWJsb2Nrcy5jb20ifQ.qloBzNbWu7Hvvsfnchw7iLQIdBxZpyl1p4F7wQjJcw8hy0AvB4moG24U6nyzAY-_Z_x5QprcGHR0CjL5YvMmkUtBaMS4xg-fwnzXZUtLgF5bl9mdogq69z3cLFB225jx58GIyJBtF2kJ2y5TGsyRC3zqhmUJ5BlcA5l1N0X-NnzY1dWUuM9mrTnfvvWYfZmLI0SfptlnnwA2oLwInGqRd6GZV-LpLoCC-sjS6S94u5WHgSgyKSQYj1x6hY15eK0LdL43dhYGcCwmiBDNcRk21QBmFwEByslMZC3iv5SPjEdw7267D9dNm4iNpk-Sv5siCDi1mZNjvnmhmTYJQkhspw"
PROJECT_KEY = "95E5FD12E64E429295758B2CB1EA29D2"  # MyTodoApp project

# API Configuration
IAM_GET_ROLES_URL = "https://api.seliseblocks.com/iam/v1/Resource/GetRoles"
IAM_CREATE_ROLE_URL = "https://api.seliseblocks.com/iam/v1/Resource/CreateRole"

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


async def list_roles(
    project_key: str = PROJECT_KEY,
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    sort_by: str = "Name",
    sort_descending: bool = False
) -> str:
    """
    List all roles for a project.
    
    Args:
        project_key: Project key (tenant ID)
        page: Page number (default: 0)
        page_size: Number of items per page (default: 10)
        search: Search filter (default: "")
        sort_by: Field to sort by (default: "Name")
        sort_descending: Sort order (default: false)
    
    Returns:
        JSON string with role list result
    """
    try:
        headers = get_headers()
        
        payload = {
            "projectKey": project_key,
            "page": page,
            "pageSize": page_size,
            "filter": {
                "search": search
            },
            "sort": {
                "property": sort_by,
                "isDescending": sort_descending
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IAM_GET_ROLES_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            roles_data = response.json()
        
        roles = roles_data.get("data", [])
        total_count = roles_data.get("totalCount", 0)
        
        result = {
            "status": "success",
            "message": f"Found {len(roles)} role(s) (total: {total_count})",
            "project_key": project_key,
            "total_count": total_count,
            "roles": roles,
            "summary": []
        }
        
        # Add summary for easier reading
        for role in roles:
            result["summary"].append({
                "name": role.get("name"),
                "slug": role.get("slug"),
                "description": role.get("description"),
                "permissions_count": role.get("count", 0),
                "item_id": role.get("itemId"),
                "created_date": role.get("createdDate")
            })
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error listing roles: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error listing roles: {str(e)}"
        }, indent=2)


async def create_role(
    name: str,
    description: str,
    slug: str,
    project_key: str = PROJECT_KEY
) -> str:
    """
    Create a new role.
    
    Args:
        name: Role name
        description: Role description
        slug: Role slug (URL-friendly identifier)
        project_key: Project key (tenant ID)
    
    Returns:
        JSON string with role creation result
    """
    try:
        headers = get_headers()
        
        payload = {
            "name": name,
            "description": description,
            "slug": slug,
            "projectKey": project_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                IAM_CREATE_ROLE_URL,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            create_data = response.json()
        
        if create_data.get("isSuccess"):
            # Get updated role list to show the result
            try:
                list_result = await list_roles(project_key)
                list_data = json.loads(list_result)
                updated_roles = list_data.get("roles", []) if list_data.get("status") == "success" else []
            except Exception:
                updated_roles = []
            
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
                "response": create_data,
                "updated_roles": updated_roles
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to create role",
                "errors": create_data.get("errors"),
                "response": create_data
            }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error creating role: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error creating role: {str(e)}"
        }, indent=2)


async def main():
    """Test both role management functions."""
    print("🔍 IAM Role Management Test Suite")
    print("=" * 50)
    
    # Test 1: List existing roles
    print("\n1️⃣ Testing list_roles...")
    list_result = await list_roles()
    print(list_result)
    
    # Test 2: Create a new role
    print("\n2️⃣ Testing create_role...")
    create_result = await create_role(
        name="tester",
        description="Test role created by automated script",
        slug="tester"
    )
    print(create_result)
    
    # Test 3: List roles again to confirm creation
    print("\n3️⃣ Verifying role creation...")
    final_list_result = await list_roles()
    print(final_list_result)
    
    print("\n✅ Test suite completed!")


if __name__ == "__main__":
    asyncio.run(main())