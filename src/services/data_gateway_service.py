import json
from utils import http_client, misc


async def create_schema(schema_name: str, project_key: str = "") -> str:
    """Create a new schema in Selise Blocks GraphQL API."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        collection_name = f"{schema_name}s"
        schema_payload = {
            "schemaName": schema_name,
            "collectionName": collection_name,
            "schemaType": 1,
            "projectKey": project_key
        }

        schema_data = await http_client.post(
            url=misc.API_CONFIG["CREATE_SCHEMA_URL"],
            json=schema_payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

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

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error during schema creation: {str(e)}"}, indent=2)


async def list_schemas(project_key: str = "", keyword: str = "", page_size: int = 100, page_number: int = 1, sort_descending: bool = True, sort_by: str = "CreatedDate") -> str:
    """List schemas from Selise Blocks GraphQL API."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        params = {
            "Keyword": keyword,
            "PageSize": page_size,
            "PageNumber": page_number,
            "SortDescending": sort_descending,
            "SortBy": sort_by,
            "ProjectKey": project_key
        }

        schemas_data = await http_client.get(
            url=misc.API_CONFIG["LIST_SCHEMAS_URL"],
            params=params,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": "Schemas retrieved successfully",
            "project_key": project_key,
            "schemas": schemas_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error during schema listing: {str(e)}"}, indent=2)


async def get_schema(schema_id: str, project_key: str = "") -> str:
    """Get a schema's current fields using its ID."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        url = f"{misc.API_CONFIG['GET_SCHEMA_URL']}/{schema_id}"

        schema_data = await http_client.get(
            url=url,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": f"Schema {schema_id} retrieved successfully",
            "schema": schema_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error getting schema: {str(e)}"}, indent=2)


async def update_schema_fields(schema_id: str, fields: list, project_key: str = "") -> str:
    """Update schema fields."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        payload = {
            "fields": fields,
            "schemaDefinitionItemId": schema_id,
            "deletableFieldNames": []
        }

        update_data = await http_client.post(
            url=misc.API_CONFIG["SCHEMA_FIELDS_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": f"Schema {schema_id} fields updated successfully",
            "schema_id": schema_id,
            "updated_fields": fields,
            "response": update_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error updating schema fields: {str(e)}"}, indent=2)


async def finalize_schema(schema_id: str, project_key: str = "") -> str:
    """Finalize schema changes by retrieving updated schema."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        url = f"{misc.API_CONFIG['GET_SCHEMA_URL']}/{schema_id}"

        schema_data = await http_client.get(
            url=url,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": f"Schema {schema_id} finalized successfully",
            "schema": schema_data
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error finalizing schema: {str(e)}"}, indent=2)


async def configure_blocks_data_gateway(project_key: str = "", gateway_config: dict = None) -> str:
    """Configure Blocks Data Gateway for GraphQL operations."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        if gateway_config is None:
            gateway_config = {
                "enableDataGateway": True,
                "gatewayEndpoint": f"https://api.seliseblocks.com/graphql/v1/{project_key}",
                "enableRealTimeSubscriptions": True
            }

        payload = {
            "projectKey": project_key,
            **gateway_config
        }

        gateway_data = await http_client.post(
            url=misc.API_CONFIG["DATA_GATEWAY_URL"],
            json=payload,
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if gateway_data.get("success", True):
            result = {
                "status": "success",
                "message": "Data Gateway configured successfully",
                "config_details": {
                    "project_key": project_key,
                    "gateway_config": gateway_config
                },
                "response": gateway_data
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to configure Data Gateway",
                "errors": gateway_data.get("errors"),
                "response": gateway_data
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error configuring Data Gateway: {str(e)}"}, indent=2)
