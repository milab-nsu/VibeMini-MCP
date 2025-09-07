import httpx
import json
import subprocess
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("Selise Blocks API")

# Global state for authentication
auth_state = {
    "access_token": None,
    "refresh_token": None,
    "expires_at": None,
    "token_type": "bearer"
}

# Global state for application domain
app_state = {
    "application_domain": None,
    "tenant_id": None,
    "project_name": None
}

# API Configuration
API_CONFIG = {
    "LOGIN_URL": "https://api.seliseblocks.com/authentication/v1/OAuth/Token",
    "CREATE_URL": "https://api.seliseblocks.com/identifier/v1/Project/Create",
    "GET_PROJECTS_URL": "https://api.seliseblocks.com/identifier/v1/Project/Gets",
    "GET_ITEM_URL": "https://api.seliseblocks.com/identifier/v1/Project/Get",
    "CREATE_SCHEMA_URL": "https://api.seliseblocks.com/graphql/v1/schemas/info",
    "LIST_SCHEMAS_URL": "https://api.seliseblocks.com/graphql/v1/schemas",
    "SCHEMA_FIELDS_URL": "https://api.seliseblocks.com/graphql/v1/schemas/fields",
    "GET_SCHEMA_URL": "https://api.seliseblocks.com/graphql/v1/schemas",
    "UPDATE_CONFIG_URL": "https://api.seliseblocks.com/authentication/v1/Configuration/Update",
    "GET_CONFIG_URL": "https://api.seliseblocks.com/authentication/v1/Configuration/Get",
    "CAPTCHA_SAVE_URL": "https://api.seliseblocks.com/captcha/v1/Configuration/Save",
    "CAPTCHA_LIST_URL": "https://api.seliseblocks.com/captcha/v1/Configuration/Gets",
    "CAPTCHA_UPDATE_STATUS_URL": "https://api.seliseblocks.com/captcha/v1/Configuration/UpdateStatus",
    "IAM_GET_ROLES_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetRoles",
    "IAM_CREATE_ROLE_URL": "https://api.seliseblocks.com/iam/v1/Resource/CreateRole",
    "IAM_GET_PERMISSIONS_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetPermissions",
    "IAM_CREATE_PERMISSION_URL": "https://api.seliseblocks.com/iam/v1/Resource/CreatePermission",
    "IAM_UPDATE_PERMISSION_URL": "https://api.seliseblocks.com/iam/v1/Resource/UpdatePermission",
    "IAM_GET_RESOURCE_GROUPS_URL": "https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups",
    "HEADERS": {
        "x-blocks-key": "d7e5554c758541db8a18694b64ef423d",
        "Origin": "https://cloud.seliseblocks.com",
        "Referer": "https://cloud.seliseblocks.com/",
        "accept": "application/json",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/json",
        "dnt": "1",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36"
    }
}


def is_token_valid() -> bool:
    """Check if the current access token is valid and not expired."""
    if not auth_state["access_token"] or not auth_state["expires_at"]:
        return False
    return datetime.now() < auth_state["expires_at"]


def get_auth_headers() -> dict:
    """Get headers with authorization if token is available."""
    headers = API_CONFIG["HEADERS"].copy()
    if auth_state["access_token"]:
        headers["Authorization"] = f"Bearer {auth_state['access_token']}"
    return headers


async def run_command(command: str) -> Dict[str, Any]:
    """Run a shell command asynchronously and return the result."""
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        return {
            "success": process.returncode == 0,
            "returncode": process.returncode,
            "stdout": stdout.decode('utf-8').strip(),
            "stderr": stderr.decode('utf-8').strip()
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }


@mcp.tool()
async def login(username: str, password: str) -> str:
    """
    Authenticate with Selise Blocks API and retrieve access tokens.
    
    Args:
        username: Email address for login
        password: Password for login
    
    Returns:
        JSON string with authentication status and token info
    """
    try:
        login_payload = {
            "grant_type": "password",
            "username": username,
            "password": password
        }
        
        # Create headers without content-type for form data
        login_headers = {k: v for k, v in API_CONFIG["HEADERS"].items() if k != "content-type"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["LOGIN_URL"],
                headers=login_headers,
                data=login_payload,
                timeout=30.0
            )
            response.raise_for_status()
            login_data = response.json()
        
        # Extract token information
        access_token = login_data.get("access_token")
        refresh_token = login_data.get("refresh_token")
        expires_in = login_data.get("expires_in", 8000)
        token_type = login_data.get("token_type", "bearer")
        
        if not access_token:
            return json.dumps({
                "status": "error",
                "message": "Login failed. No access token received.",
                "response": login_data
            }, indent=2)
        
        # Calculate expiration time with 5-minute buffer
        expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
        
        # Update global auth state
        auth_state.update({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "token_type": token_type
        })
        
        result = {
            "status": "success",
            "message": f"Login successful for {username}",
            "token_info": {
                "token_type": token_type,
                "expires_in": expires_in,
                "expires_at": expires_at.isoformat(),
                "has_refresh_token": refresh_token is not None
            }
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error during login: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during login: {str(e)}"
        }, indent=2)


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
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        headers = get_auth_headers()
        params = {
            "page": page,
            "pageSize": page_size
        }
        
        if tenant_group_id:
            params["tenantGroupId"] = tenant_group_id
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["GET_PROJECTS_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            projects_data = response.json()
        
        # Extract application domains and tenant information
        extracted_data = []
        for group in projects_data:
            tenant_group_id = group.get("tenantGroupId")
            for project in group.get("projects", []):
                item_id = project.get("itemId")
                app_domain = project.get("applicationDomain")  # Extract the real domain from the response
                
                project_info = {
                    "project_name": project.get("name"),
                    "tenant_id": project.get("tenantId"),
                    "tenant_group_id": tenant_group_id,
                    "item_id": item_id,
                    "application_contexts": []
                }
                
                # Use the applicationDomain from the response if available
                if app_domain:
                    project_info["application_contexts"] = [{
                        "environment": project.get("environment", "dev"),
                        "domain": app_domain,
                        "cookie_domain": project.get("cookieDomain", "seliseblocks.com")
                    }]
                    
                    # Update global state with the real domain for the matching project
                    if (project.get("name") == app_state.get("project_name") or 
                        not app_state["application_domain"]):
                        app_state["application_domain"] = app_domain
                        app_state["tenant_id"] = project.get("tenantId")
                        app_state["project_name"] = project.get("name")
                        
                # Fallback: If we have an itemId but no applicationDomain, try to get it via the old method
                elif item_id:
                    try:
                        app_domain = await get_application_domain(item_id)
                        if app_domain:
                            project_info["application_contexts"] = [{
                                "environment": "dev",
                                "domain": app_domain,
                                "cookie_domain": "seliseblocks.com"
                            }]
                            
                            # Update global state with the real domain for the matching project
                            if (project.get("name") == app_state.get("project_name") or 
                                not app_state["application_domain"]):
                                app_state["application_domain"] = app_domain
                                app_state["tenant_id"] = project.get("tenantId")
                                app_state["project_name"] = project.get("name")
                    except Exception as domain_error:
                        print(f"Error getting domain for project {project.get('name')}: {domain_error}")
                        # Fallback to placeholder if domain extraction fails
                        placeholder_domain = f"https://dev-{project.get('name', 'unknown')}-placeholder.seliseblocks.com"
                        project_info["application_contexts"] = [{
                            "environment": "dev",
                            "domain": placeholder_domain,
                            "cookie_domain": "seliseblocks.com"
                        }]
                else:
                    # Final fallback: use applicationContexts if present
                    for context in project.get("applicationContexts", []):
                        app_context = {
                            "environment": context.get("environment"),
                            "domain": context.get("domain"),
                            "cookie_domain": context.get("cookieDomain")
                        }
                        project_info["application_contexts"].append(app_context)
                        
                        # Update global state with the first domain found
                        if context.get("domain") and not app_state["application_domain"]:
                            app_state["application_domain"] = context.get("domain")
                            app_state["tenant_id"] = project.get("tenantId")
                            app_state["project_name"] = project.get("name")
                
                extracted_data.append(project_info)
        
        result = {
            "status": "success",
            "message": "Projects retrieved successfully",
            "projects": extracted_data,
            "global_state": {
                "application_domain": app_state["application_domain"],
                "tenant_id": app_state["tenant_id"],
                "project_name": app_state["project_name"]
            }
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error during project retrieval: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during project retrieval: {str(e)}"
        }, indent=2)


@mcp.tool()
async def create_schema(schema_name: str, project_key: str = "") -> str:
    """
    Create a new schema in Selise Blocks GraphQL API.
    
    Args:
        schema_name: Name of the schema to create
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with schema creation result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
            "x-blocks-key": "d7e5554c758541db8a18694b64ef423d"  # Use the account's tenant_id from JWT
        }
        
        # Prepare payload - collection name is schema name with 's' appended (lowercased)
        collection_name = f"{schema_name}s"
        schema_payload = {
            "schemaName": schema_name,
            "collectionName": collection_name,
            "schemaType": 1,
            "projectKey": project_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["CREATE_SCHEMA_URL"],
                headers=headers,
                json=schema_payload,
                timeout=30.0
            )
            
            # Check if response is successful
            if response.status_code == 200:
                try:
                    schema_data = response.json()
                    result = {
                        "status": "success",
                        "message": f"Schema '{schema_name}' created successfully",
                        "schema_details": {
                            "schema_name": schema_name,
                            "collection_name": collection_name,
                            "schema_type": 1,
                            "project_key": project_key
                        },
                        "response": schema_data
                    }
                    
                    # Automatically fetch updated schema list
                    try:
                        schemas_list_result = await list_schemas(project_key)
                        schemas_list_data = json.loads(schemas_list_result)
                        if schemas_list_data.get("status") == "success":
                            result["updated_schemas_list"] = schemas_list_data.get("schemas")
                    except Exception as list_error:
                        result["schemas_list_error"] = f"Could not fetch updated schema list: {str(list_error)}"
                    
                    return json.dumps(result, indent=2)
                except json.JSONDecodeError:
                    # If response is not JSON, it might be plain text success
                    result = {
                        "status": "success",
                        "message": f"Schema '{schema_name}' created successfully",
                        "schema_details": {
                            "schema_name": schema_name,
                            "collection_name": collection_name,
                            "schema_type": 1,
                            "project_key": project_key
                        },
                        "response": response.text
                    }
                    
                    # Automatically fetch updated schema list
                    try:
                        schemas_list_result = await list_schemas(project_key)
                        schemas_list_data = json.loads(schemas_list_result)
                        if schemas_list_data.get("status") == "success":
                            result["updated_schemas_list"] = schemas_list_data.get("schemas")
                    except Exception as list_error:
                        result["schemas_list_error"] = f"Could not fetch updated schema list: {str(list_error)}"
                    
                    return json.dumps(result, indent=2)
            else:
                # Handle non-200 responses
                return json.dumps({
                    "status": "error",
                    "message": f"HTTP error during schema creation: {response.status_code}",
                    "details": response.text,
                    "request_payload": schema_payload
                }, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error during schema creation: {e.response.status_code}",
            "details": e.response.text,
            "request_payload": schema_payload if 'schema_payload' in locals() else None
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during schema creation: {str(e)}",
            "request_payload": schema_payload if 'schema_payload' in locals() else None
        }, indent=2)


@mcp.tool()
async def list_schemas(project_key: str = "", keyword: str = "", page_size: int = 100, page_number: int = 1, sort_descending: bool = True, sort_by: str = "CreatedDate") -> str:
    """
    List schemas from Selise Blocks GraphQL API.
    
    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        keyword: Search keyword for filtering schemas
        page_size: Number of items per page (default: 100)
        page_number: Page number for pagination (default: 1) 
        sort_descending: Sort in descending order (default: True)
        sort_by: Field to sort by (default: "CreatedDate")
    
    Returns:
        JSON string with schemas listing result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
        
        # Prepare query parameters
        params = {
            "Keyword": keyword,
            "PageSize": page_size,
            "PageNumber": page_number,
            "SortDescending": sort_descending,
            "SortBy": sort_by,
            "ProjectKey": project_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["LIST_SCHEMAS_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            schemas_data = response.json()
        
        result = {
            "status": "success",
            "message": "Schemas retrieved successfully",
            "project_key": project_key,
            "schemas": schemas_data
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error during schema listing: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during schema listing: {str(e)}"
        }, indent=2)


@mcp.tool()
async def get_schema(schema_id: str, project_key: str = "") -> str:
    """
    Get a schema's current fields using its ID (step 1 of schema field management).
    
    Args:
        schema_id: The ID of the schema to retrieve
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with schema fields and metadata
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
        
        # Get schema details using schema ID
        url = f"{API_CONFIG['GET_SCHEMA_URL']}/{schema_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            schema_data = response.json()
        
        result = {
            "status": "success",
            "message": f"Schema {schema_id} retrieved successfully",
            "schema": schema_data
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error getting schema: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting schema: {str(e)}"
        }, indent=2)


@mcp.tool()
async def update_schema_fields(schema_id: str, fields: list, project_key: str = "") -> str:
    """
    Update schema fields (step 2 of schema field management).
    
    Args:
        schema_id: The ID of the schema to update
        fields: Complete list of fields for the schema (existing + new)
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with update result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
        
        # Prepare payload matching the curl example
        payload = {
            "fields": fields,
            "schemaDefinitionItemId": schema_id,
            "deletableFieldNames": []
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["SCHEMA_FIELDS_URL"],
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            update_data = response.json()
        
        result = {
            "status": "success", 
            "message": f"Schema {schema_id} fields updated successfully",
            "schema_id": schema_id,
            "updated_fields": fields,
            "response": update_data
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error updating schema fields: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error updating schema fields: {str(e)}"
        }, indent=2)


@mcp.tool()
async def finalize_schema(schema_id: str, project_key: str = "") -> str:
    """
    Finalize schema changes by retrieving updated schema (step 3 of schema field management).
    
    Args:
        schema_id: The ID of the schema to finalize
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with finalized schema data
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
        
        # Get finalized schema data
        url = f"{API_CONFIG['GET_SCHEMA_URL']}/{schema_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            schema_data = response.json()
        
        result = {
            "status": "success",
            "message": f"Schema {schema_id} finalized successfully",
            "schema": schema_data
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error finalizing schema: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error finalizing schema: {str(e)}"
        }, indent=2)


@mcp.tool()
async def activate_social_login(
    item_id: str = "682c40c3872fab1bc2cc8988",
    project_key: str = "",
    refresh_token_minutes: int = 300,
    access_token_minutes: int = 15,
    remember_me_minutes: int = 43200,
    allowed_grant_types: list = None,
    wrong_attempts_lock: int = 5,
    lock_duration_minutes: int = 5
) -> str:
    """
    Activate social login for the project by updating authentication configuration.
    
    Args:
        item_id: Configuration item ID (default: "682c40c3872fab1bc2cc8988")
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        refresh_token_minutes: Refresh token validity in minutes (default: 300)
        access_token_minutes: Access token validity in minutes (default: 15)
        remember_me_minutes: Remember me token validity in minutes (default: 43200)
        allowed_grant_types: List of allowed grant types (default: ["password", "refresh_token", "mfa_code", "social"])
        wrong_attempts_lock: Number of wrong attempts to lock account (default: 5)
        lock_duration_minutes: Account lock duration in minutes (default: 5)
    
    Returns:
        JSON string with social login activation result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Set default allowed grant types if not provided
        if allowed_grant_types is None:
            allowed_grant_types = ["password", "refresh_token", "mfa_code", "social"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
            "x-blocks-key": "d7e5554c758541db8a18694b64ef423d"  # Use the original tenant from JWT
        }
        
        # Prepare payload for social login activation
        config_payload = {
            "itemId": item_id,
            "refreshTokenValidForNumberMinutes": refresh_token_minutes,
            "accessTokenValidForNumberMinutes": access_token_minutes,
            "rememberMeRefreshTokenValidForNumberMinutes": remember_me_minutes,
            "allowedGrantTypes": allowed_grant_types,
            "getNumberOfWrongAttemptsToLockTheAccount": wrong_attempts_lock,
            "accountLockDurationInMinutes": lock_duration_minutes,
            "projectKey": project_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["UPDATE_CONFIG_URL"],
                headers=headers,
                json=config_payload,
                timeout=30.0
            )
            response.raise_for_status()
            response_data = response.json()
        
        # Get the updated configuration to confirm changes
        try:
            config_result = await get_authentication_config(project_key)
            config_result_data = json.loads(config_result)
            updated_config = config_result_data.get("configuration") if config_result_data.get("status") == "success" else None
        except Exception as config_error:
            updated_config = f"Could not fetch updated config: {str(config_error)}"

        result = {
            "status": "success",
            "message": f"Social login activated successfully for project {project_key}",
            "config_details": {
                "item_id": item_id,
                "project_key": project_key,
                "allowed_grant_types": allowed_grant_types,
                "refresh_token_minutes": refresh_token_minutes,
                "access_token_minutes": access_token_minutes,
                "remember_me_minutes": remember_me_minutes
            },
            "response": response_data,
            "updated_configuration": updated_config
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error during social login activation: {e.response.status_code}",
            "details": e.response.text,
            "config_payload": config_payload if 'config_payload' in locals() else None
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error activating social login: {str(e)}",
            "config_payload": config_payload if 'config_payload' in locals() else None
        }, indent=2)


@mcp.tool()
async def get_authentication_config(project_key: str = "") -> str:
    """
    Get the current authentication configuration for the project.
    
    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with current authentication configuration
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Prepare headers matching the curl example
        headers = {
            "accept": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {auth_state['access_token']}",
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
        
        # Prepare query parameters
        params = {
            "ProjectKey": project_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["GET_CONFIG_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            config_data = response.json()
        
        result = {
            "status": "success",
            "message": f"Authentication configuration retrieved successfully for project {project_key}",
            "project_key": project_key,
            "configuration": config_data
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error getting authentication config: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error getting authentication config: {str(e)}"
        }, indent=2)


@mcp.tool()
async def set_application_domain(domain: str, tenant_id: str, project_name: str = "") -> str:
    """
    Manually set the application domain and tenant ID for repository creation.
    
    Args:
        domain: Application domain URL
        tenant_id: Tenant ID for the project
        project_name: Project name (optional)
    
    Returns:
        JSON string with confirmation
    """
    app_state["application_domain"] = domain
    app_state["tenant_id"] = tenant_id
    app_state["project_name"] = project_name
    
    return json.dumps({
        "status": "success",
        "message": "Application domain and tenant ID set successfully",
        "global_state": {
            "application_domain": app_state["application_domain"],
            "tenant_id": app_state["tenant_id"],
            "project_name": app_state["project_name"]
        }
    }, indent=2)


@mcp.tool()
async def check_blocks_cli() -> str:
    """
    Check if Blocks CLI is installed and available.
    
    Returns:
        JSON string with CLI availability status
    """
    # Check if blocks command is available
    result = await run_command("blocks --version")
    
    if result["success"]:
        return json.dumps({
            "status": "success",
            "message": "Blocks CLI is installed and available",
            "version": result["stdout"]
        }, indent=2)
    else:
        return json.dumps({
            "status": "not_installed",
            "message": "Blocks CLI is not installed",
            "error": result["stderr"]
        }, indent=2)


@mcp.tool()
async def install_blocks_cli() -> str:
    """
    Install Blocks CLI using npm.
    
    Returns:
        JSON string with installation result
    """
    result = await run_command("npm install -g @seliseblocks/cli")
    
    if result["success"]:
        # Verify installation
        verify_result = await run_command("blocks --version")
        
        return json.dumps({
            "status": "success",
            "message": "Blocks CLI installed successfully",
            "installation_output": result["stdout"],
            "version": verify_result["stdout"] if verify_result["success"] else "Unknown"
        }, indent=2)
    else:
        return json.dumps({
            "status": "error",
            "message": "Failed to install Blocks CLI",
            "error": result["stderr"],
            "output": result["stdout"]
        }, indent=2)


@mcp.tool()
async def create_local_repository(repository_name: str = "", 
                                template: str = "web", 
                                use_cli: bool = True) -> str:
    """
    Create a local Selise repository using Blocks CLI.
    
    Args:
        repository_name: Name for the local repository (uses project name if empty)
        template: Template to use for the repository (default: "web")
        use_cli: Whether to use CLI mode (default: True)
    
    Returns:
        JSON string with repository creation result
    """
    try:
        # Check if we have the required information
        if not app_state["tenant_id"] or not app_state["application_domain"]:
            return json.dumps({
                "status": "error",
                "message": "Missing tenant ID or application domain. Please run get_projects or set_application_domain first."
            }, indent=2)
        
        # Use project name from global state if repository_name is not provided
        if not repository_name:
            if app_state["project_name"]:
                repository_name = app_state["project_name"]
            else:
                repository_name = "selise-repository"
        
        # Check if Blocks CLI is available
        cli_check = await run_command("blocks --version")
        if not cli_check["success"]:
            return json.dumps({
                "status": "error",
                "message": "Blocks CLI is not installed. Please run install_blocks_cli first.",
                "details": cli_check["stderr"]
            }, indent=2)
        
        # Build the command
        cli_flag = "--cli" if use_cli else ""
        command = f"blocks new {template} {repository_name} {cli_flag} --blocks-key {app_state['tenant_id']} --app-domain {app_state['application_domain']}"
        
        # Create the repository
        result = await run_command(command)
        
        if result["success"]:
            return json.dumps({
                "status": "success",
                "message": f"Local repository '{repository_name}' created successfully",
                "command_used": command,
                "output": result["stdout"],
                "tenant_id": app_state["tenant_id"],
                "application_domain": app_state["application_domain"]
            }, indent=2)
        else:
            return json.dumps({
                "status": "error",
                "message": "Failed to create local repository",
                "command_used": command,
                "error": result["stderr"],
                "output": result["stdout"]
            }, indent=2)
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during repository creation: {str(e)}"
        }, indent=2)


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
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Prepare headers with authorization
        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"
        
        # Prepare payload
        create_payload = {
            "name": project_name,
            "isAcceptBlocksTerms": True,
            "isUseBlocksExclusively": True,
            "isProduction": is_production,
            "resources": [{
                "name": repo_name,
                "link": repo_link,
                "resourceId": repo_id
            }],
            "applicationContexts": [{
                "environment": "dev",
                "domain": f"https://dev-{project_name}-placeholder.seliseblocks.com",
                "cookieDomain": "seliseblocks.com"
            }]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["CREATE_URL"],
                headers=headers,
                json=create_payload,
                timeout=30.0
            )
            response.raise_for_status()
            create_data = response.json()
        
        tenant_group_id = create_data.get("tenantGroupId")
        
        if not tenant_group_id:
            return json.dumps({
                "status": "error",
                "message": "Project creation failed. No tenantGroupId received.",
                "response": create_data
            }, indent=2)
        
        # Try to get the tenant ID and real application domain
        tenant_id = await get_tenant_id(tenant_group_id, project_name)
        application_domain = None
        
        if tenant_id:
            app_state["tenant_id"] = tenant_id
            app_state["project_name"] = project_name
            
            # Try to get the real application domain using the new method
            try:
                application_domain = await get_application_domain_by_tenant_group(tenant_group_id, project_name)
                
                if application_domain:
                    app_state["application_domain"] = application_domain
                else:
                    # Fallback: try the old method with get_projects
                    projects_result = await get_projects(tenant_group_id)
                    projects_data = json.loads(projects_result)
                    
                    if projects_data.get("status") == "success":
                        # Find the project and extract its real domain
                        for project_info in projects_data.get("projects", []):
                            if project_info.get("project_name") == project_name:
                                contexts = project_info.get("application_contexts", [])
                                if contexts and contexts[0].get("domain"):
                                    application_domain = contexts[0]["domain"]
                                    app_state["application_domain"] = application_domain
                                    break
                    
                    # If we still couldn't get the real domain, keep placeholder
                    if not application_domain:
                        app_state["application_domain"] = f"https://dev-{project_name}-placeholder.seliseblocks.com"
                    
            except Exception as domain_error:
                print(f"Error fetching real domain: {domain_error}")
                app_state["application_domain"] = f"https://dev-{project_name}-placeholder.seliseblocks.com"
        
        result = {
            "status": "success",
            "message": f"Project '{project_name}' created successfully",
            "project_details": {
                "name": project_name,
                "tenantGroupId": tenant_group_id,
                "tenantId": tenant_id,
                "application_domain": app_state.get("application_domain"),
                "repository": {
                    "name": repo_name,
                    "link": repo_link,
                    "id": repo_id
                },
                "is_production": is_production
            }
        }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error during project creation: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during project creation: {str(e)}"
        }, indent=2)


@mcp.tool()
async def get_auth_status() -> str:
    """
    Check current authentication status and token validity.
    
    Returns:
        JSON string with authentication status
    """
    if not auth_state["access_token"]:
        status = {
            "authenticated": False,
            "message": "No authentication token available"
        }
    elif is_token_valid():
        status = {
            "authenticated": True,
            "message": "Authentication token is valid",
            "token_type": auth_state["token_type"],
            "expires_at": auth_state["expires_at"].isoformat() if auth_state["expires_at"] else None,
            "has_refresh_token": auth_state["refresh_token"] is not None
        }
    else:
        status = {
            "authenticated": False,
            "message": "Authentication token has expired",
            "expired_at": auth_state["expires_at"].isoformat() if auth_state["expires_at"] else None
        }
    
    return json.dumps(status, indent=2)


@mcp.tool()
async def get_global_state() -> str:
    """
    Get the current global state including authentication and application domain.
    
    Returns:
        JSON string with current global state
    """
    return json.dumps({
        "auth_state": {
            "authenticated": is_token_valid(),
            "token_type": auth_state.get("token_type"),
            "expires_at": auth_state["expires_at"].isoformat() if auth_state.get("expires_at") else None
        },
        "app_state": {
            "application_domain": app_state["application_domain"],
            "tenant_id": app_state["tenant_id"],
            "project_name": app_state["project_name"]
        }
    }, indent=2)


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
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        # Validate provider
        if provider not in ["recaptcha", "hcaptcha"]:
            return json.dumps({
                "status": "error",
                "message": "Invalid provider. Must be 'recaptcha' for Google reCAPTCHA or 'hcaptcha' for hCaptcha."
            }, indent=2)
        
        headers = get_auth_headers()
        
        payload = {
            "projectKey": project_key,
            "isEnable": is_enable,
            "provider": provider,
            "captchaKey": site_key,
            "captchaSecret": secret_key,
            "captchaGenerator": ""
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["CAPTCHA_SAVE_URL"],
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            save_data = response.json()
        
        if save_data.get("isSuccess"):
            # Get updated configurations to show the result
            try:
                list_result = await list_captcha_configs(project_key)
                list_data = json.loads(list_result)
                updated_configs = list_data.get("configurations", []) if list_data.get("status") == "success" else []
            except Exception:
                updated_configs = []
            
            result = {
                "status": "success",
                "message": f"{provider.capitalize()} CAPTCHA configuration saved successfully",
                "config_details": {
                    "provider": provider,
                    "project_key": project_key,
                    "is_enabled": is_enable,
                    "site_key": site_key[:20] + "..." if len(site_key) > 20 else site_key
                },
                "response": save_data,
                "updated_configurations": updated_configs
            }
        else:
            result = {
                "status": "error", 
                "message": "Failed to save CAPTCHA configuration",
                "errors": save_data.get("errors"),
                "response": save_data
            }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error saving CAPTCHA config: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error saving CAPTCHA config: {str(e)}"
        }, indent=2)


@mcp.tool()
async def list_captcha_configs(project_key: str = "") -> str:
    """
    List all CAPTCHA configurations for a project.
    
    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with list of CAPTCHA configurations
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        headers = get_auth_headers()
        params = {"ProjectKey": project_key}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["CAPTCHA_LIST_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            configs_data = response.json()
        
        configurations = configs_data.get("configurations", [])
        
        result = {
            "status": "success",
            "message": f"Found {len(configurations)} CAPTCHA configuration(s)",
            "project_key": project_key,
            "configurations": configurations,
            "summary": []
        }
        
        # Add summary for easier reading
        for config in configurations:
            status = "Enabled" if config.get("isEnable") else "Disabled"
            result["summary"].append({
                "provider": config.get("provider"),
                "status": status,
                "item_id": config.get("itemId"),
                "created_date": config.get("createdDate")
            })
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error listing CAPTCHA configs: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error listing CAPTCHA configs: {str(e)}"
        }, indent=2)


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
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        headers = get_auth_headers()
        
        payload = {
            "projectKey": project_key,
            "isEnable": is_enable,
            "itemId": item_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["CAPTCHA_UPDATE_STATUS_URL"],
                headers=headers,
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            update_data = response.json()
        
        if update_data.get("isSuccess"):
            status_text = "enabled" if is_enable else "disabled"
            
            # Get updated configurations to confirm the change
            try:
                list_result = await list_captcha_configs(project_key)
                list_data = json.loads(list_result)
                updated_configs = list_data.get("configurations", []) if list_data.get("status") == "success" else []
            except Exception:
                updated_configs = []
            
            result = {
                "status": "success",
                "message": f"CAPTCHA configuration {status_text} successfully",
                "config_details": {
                    "item_id": item_id,
                    "project_key": project_key,
                    "is_enabled": is_enable
                },
                "response": update_data,
                "updated_configurations": updated_configs
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to update CAPTCHA configuration status",
                "errors": update_data.get("errors"),
                "response": update_data
            }
        
        return json.dumps(result, indent=2)
        
    except httpx.HTTPStatusError as e:
        return json.dumps({
            "status": "error",
            "message": f"HTTP error updating CAPTCHA status: {e.response.status_code}",
            "details": e.response.text
        }, indent=2)
    
    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error updating CAPTCHA status: {str(e)}"
        }, indent=2)


@mcp.tool()
async def list_roles(
    project_key: str = "",
    page: int = 0,
    page_size: int = 10,
    search: str = "",
    sort_by: str = "Name",
    sort_descending: bool = False
) -> str:
    """
    List all roles for a project.
    
    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        page: Page number (default: 0)
        page_size: Number of items per page (default: 10)
        search: Search filter (default: "")
        sort_by: Field to sort by (default: "Name")
        sort_descending: Sort order (default: false)
    
    Returns:
        JSON string with role list result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        headers = get_auth_headers()
        
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
                API_CONFIG["IAM_GET_ROLES_URL"],
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


@mcp.tool()
async def create_role(
    name: str,
    description: str,
    slug: str,
    project_key: str = ""
) -> str:
    """
    Create a new role.
    
    Args:
        name: Role name
        description: Role description
        slug: Role slug (URL-friendly identifier)
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with role creation result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        headers = get_auth_headers()
        
        payload = {
            "name": name,
            "description": description,
            "slug": slug,
            "projectKey": project_key
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                API_CONFIG["IAM_CREATE_ROLE_URL"],
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
    """
    List all permissions for a project.
    
    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
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
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        headers = get_auth_headers()
        
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
                API_CONFIG["IAM_GET_PERMISSIONS_URL"],
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
    """
    Create a new permission.
    
    Args:
        name: Permission name
        description: Permission description
        resource: Resource name (arbitrary string)
        resource_group: Resource group name (arbitrary string)
        tags: List of action tags (e.g., ["create", "read", "update", "delete"])
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        type: Permission type (default: 3 for "Data protection")
        dependent_permissions: List of dependent permission IDs (default: [])
        is_built_in: Whether it's a built-in permission (default: false)
    
    Returns:
        JSON string with permission creation result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        if dependent_permissions is None:
            dependent_permissions = []
        
        headers = get_auth_headers()
        
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
                API_CONFIG["IAM_CREATE_PERMISSION_URL"],
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
    """
    Update an existing permission.
    
    Args:
        item_id: The ID of the permission to update
        name: Permission name
        description: Permission description
        resource: Resource name (arbitrary string)
        resource_group: Resource group name (arbitrary string)
        tags: List of action tags (e.g., ["create", "read", "update", "delete"])
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        type: Permission type (default: 3 for "Data protection")
        dependent_permissions: List of dependent permission IDs (default: [])
        is_built_in: Whether it's a built-in permission (default: false)
    
    Returns:
        JSON string with permission update result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        if dependent_permissions is None:
            dependent_permissions = []
        
        headers = get_auth_headers()
        
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
                API_CONFIG["IAM_UPDATE_PERMISSION_URL"],
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


@mcp.tool()
async def get_resource_groups(project_key: str = "") -> str:
    """
    Get available resource groups for a project.
    
    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
    
    Returns:
        JSON string with resource groups result
    """
    try:
        # Check if authenticated
        if not is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)
        
        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not app_state["tenant_id"]:
                return json.dumps({
                    "status": "error",
                    "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key."
                }, indent=2)
            project_key = app_state["tenant_id"]
        
        headers = get_auth_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_CONFIG['IAM_GET_RESOURCE_GROUPS_URL']}?ProjectKey={project_key}",
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


async def get_tenant_id(tenant_group_id: str, project_name: str) -> Optional[str]:
    """Get tenant ID for a project."""
    try:
        headers = get_auth_headers()
        params = {
            "page": 0,
            "pageSize": 100,
            "tenantGroupId": tenant_group_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["GET_PROJECTS_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            projects_data = response.json()
        
        # Search for the tenant ID
        for group in projects_data:
            for project in group.get("projects", []):
                if project.get("name") == project_name:
                    return project.get("tenantId")
        
        return None
        
    except Exception as e:
        print(f"Error getting tenant ID: {str(e)}")
        return None


async def get_application_domain_by_tenant_group(tenant_group_id: str, project_name: str) -> Optional[str]:
    """Get the real application domain for a project using tenant group ID and project name."""
    try:
        headers = get_auth_headers()
        params = {
            "page": 0,
            "pageSize": 100,
            "tenantGroupId": tenant_group_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["GET_PROJECTS_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            projects_data = response.json()
        
        # Search for the project and extract its real domain
        for group in projects_data:
            for project in group.get("projects", []):
                if project.get("name") == project_name:
                    domain = project.get("applicationDomain")
                    if domain:
                        return domain
        
        return None
        
    except Exception as e:
        print(f"Error getting application domain for tenant group {tenant_group_id}, project {project_name}: {str(e)}")
        return None


async def get_application_domain(item_id: str) -> Optional[str]:
    """Get the real application domain for a project using its itemId."""
    try:
        headers = get_auth_headers()
        params = {"id": item_id}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                API_CONFIG["GET_ITEM_URL"],
                headers=headers,
                params=params,
                timeout=30.0
            )
            response.raise_for_status()
            project_detail = response.json()
        
        # Extract the application domain from the project detail
        application_contexts = project_detail.get("applicationContexts", [])
        for context in application_contexts:
            if context.get("environment") == "dev":
                domain = context.get("domain")
                if domain:
                    return domain
        
        # If no dev environment found, return the first domain available
        if application_contexts and application_contexts[0].get("domain"):
            return application_contexts[0].get("domain")
        
        return None
        
    except Exception as e:
        print(f"Error getting application domain for item {item_id}: {str(e)}")
        return None


if __name__ == "__main__":
    mcp.run()
