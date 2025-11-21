import json
from typing import Optional
from utils import http_client, misc


async def get_projects(tenant_group_id: str = "", page: int = 0, page_size: int = 100) -> str:
    """
    Get projects from Selise Blocks API and extract application domains.
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)

        params = {
            "page": page,
            "pageSize": page_size
        }

        if tenant_group_id:
            params["tenantGroupId"] = tenant_group_id

        projects_data = await http_client.get(
            url=misc.API_CONFIG["GET_PROJECTS_URL"],
            params=params,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

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
                    if (project.get("name") == misc.app_state.get("project_name") or
                        not misc.app_state["application_domain"]):
                        misc.app_state["application_domain"] = app_domain
                        misc.app_state["tenant_id"] = project.get("tenantId")
                        misc.app_state["project_name"] = project.get("name")

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
                            if (project.get("name") == misc.app_state.get("project_name") or
                                not misc.app_state["application_domain"]):
                                misc.app_state["application_domain"] = app_domain
                                misc.app_state["tenant_id"] = project.get("tenantId")
                                misc.app_state["project_name"] = project.get("name")
                    except Exception as domain_error:
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
                        if context.get("domain") and not misc.app_state["application_domain"]:
                            misc.app_state["application_domain"] = context.get("domain")
                            misc.app_state["tenant_id"] = project.get("tenantId")
                            misc.app_state["project_name"] = project.get("name")

                extracted_data.append(project_info)

        result = {
            "status": "success",
            "message": "Projects retrieved successfully",
            "projects": extracted_data,
            "global_state": {
                "application_domain": misc.app_state["application_domain"],
                "tenant_id": misc.app_state["tenant_id"],
                "project_name": misc.app_state["project_name"]
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during project retrieval: {str(e)}"
        }, indent=2)


async def set_application_domain(domain: str, tenant_id: str, project_name: str = "", tenant_group_id: str = "") -> str:
    """
    Manually set the application domain and tenant ID for repository creation.
    """
    misc.app_state["application_domain"] = domain
    misc.app_state["tenant_id"] = tenant_id
    misc.app_state["project_name"] = project_name
    if tenant_group_id:
        misc.app_state["tenant_group_id"] = tenant_group_id

    return json.dumps({
        "status": "success",
        "message": "Application domain and tenant ID set successfully",
        "global_state": {
            "application_domain": misc.app_state["application_domain"],
            "tenant_id": misc.app_state["tenant_id"],
            "project_name": misc.app_state["project_name"]
        }
    }, indent=2)


async def create_project(
    project_name: str,
    repo_name: str,
    repo_link: str,
    repo_id: str="Any",
    is_production: bool = False
) -> str:
    """
    Create a new project in Selise Cloud.
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps({
                "status": "error",
                "message": "Authentication required. Please login first using the login tool."
            }, indent=2)

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

        create_data = await http_client.post(
            url=misc.API_CONFIG["CREATE_URL"],
            json=create_payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

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
            misc.app_state["tenant_id"] = tenant_id
            misc.app_state["tenant_group_id"] = tenant_group_id
            misc.app_state["project_name"] = project_name

            # Try to get the real application domain using the new method
            try:
                application_domain = await get_application_domain_by_tenant_group(tenant_group_id, project_name)

                if application_domain:
                    misc.app_state["application_domain"] = application_domain
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
                                    misc.app_state["application_domain"] = application_domain
                                    break

                    # If we still couldn't get the real domain, keep placeholder
                    if not application_domain:
                        misc.app_state["application_domain"] = f"https://dev-{project_name}-placeholder.seliseblocks.com"

            except Exception as domain_error:
                misc.app_state["application_domain"] = f"https://dev-{project_name}-placeholder.seliseblocks.com"

        result = {
            "status": "success",
            "message": f"Project '{project_name}' created successfully",
            "project_details": {
                "name": project_name,
                "tenantGroupId": tenant_group_id,
                "tenantId": tenant_id,
                "application_domain": misc.app_state.get("application_domain"),
                "repository": {
                    "name": repo_name,
                    "link": repo_link,
                    "id": repo_id
                },
                "is_production": is_production
            }
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during project creation: {str(e)}"
        }, indent=2)


async def get_auth_status() -> str:
    """
    Check current authentication status and token validity.
    """
    if not misc.auth_state["access_token"]:
        status = {
            "authenticated": False,
            "message": "No authentication token available"
        }
    elif misc.is_token_valid():
        status = {
            "authenticated": True,
            "message": "Authentication token is valid",
            "token_type": misc.auth_state["token_type"],
            "expires_at": misc.auth_state["expires_at"].isoformat() if misc.auth_state["expires_at"] else None,
            "has_refresh_token": misc.auth_state["refresh_token"] is not None
        }
    else:
        status = {
            "authenticated": False,
            "message": "Authentication token has expired",
            "expired_at": misc.auth_state["expires_at"].isoformat() if misc.auth_state["expires_at"] else None
        }

    return json.dumps(status, indent=2)


async def get_global_state() -> str:
    """
    Get the current global state including authentication and application domain.
    """
    return json.dumps({
        "auth_state": {
            "authenticated": misc.is_token_valid(),
            "token_type": misc.auth_state.get("token_type"),
            "expires_at": misc.auth_state["expires_at"].isoformat() if misc.auth_state.get("expires_at") else None
        },
        "app_state": {
            "application_domain": misc.app_state["application_domain"],
            "tenant_id": misc.app_state["tenant_id"],
            "project_name": misc.app_state["project_name"]
        }
    }, indent=2)


# Helper functions

async def get_tenant_id(tenant_group_id: str, project_name: str) -> Optional[str]:
    """Get tenant ID for a project."""
    try:
        params = {
            "page": 0,
            "pageSize": 100,
            "tenantGroupId": tenant_group_id
        }

        projects_data = await http_client.get(
            url=misc.API_CONFIG["GET_PROJECTS_URL"],
            params=params,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

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
        params = {
            "page": 0,
            "pageSize": 100,
            "tenantGroupId": tenant_group_id
        }

        projects_data = await http_client.get(
            url=misc.API_CONFIG["GET_PROJECTS_URL"],
            params=params,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

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
        params = {"id": item_id}

        project_detail = await http_client.get(
            url=misc.API_CONFIG["GET_ITEM_URL"],
            params=params,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

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
