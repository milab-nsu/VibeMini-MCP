from server import server as mcp
from services import data_gateway_service


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
    return await data_gateway_service.create_schema(schema_name, project_key)


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
    return await data_gateway_service.list_schemas(project_key, keyword, page_size, page_number, sort_descending, sort_by)


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
    return await data_gateway_service.get_schema(schema_id, project_key)


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
    return await data_gateway_service.update_schema_fields(schema_id, fields, project_key)


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
    return await data_gateway_service.finalize_schema(schema_id, project_key)


@mcp.tool()
async def configure_blocks_data_gateway(project_key: str = "", gateway_config: dict = None) -> str:
    """
    Configure Blocks Data Gateway for GraphQL operations.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided
        gateway_config: Gateway configuration dictionary

    Returns:
        JSON string with data gateway configuration result
    """
    return await data_gateway_service.configure_blocks_data_gateway(project_key, gateway_config)
