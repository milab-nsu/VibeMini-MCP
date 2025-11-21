from server import server as mcp
from services import documentation_service


@mcp.tool()
async def list_sections() -> str:
    """
    ⚠️ CALL THIS FIRST - Discover all available Selise Blocks documentation topics.

    Returns metadata for all documentation including:
    - Workflows (project setup, feature planning, implementation checklist)
    - Recipes (GraphQL CRUD, forms, permissions, modals)
    - Component catalog and architecture patterns
    - Use cases and triggers for when to read each topic

    This tool fetches the topics.json metadata file from GitHub which catalogs
    all available documentation with priority levels, read order, and use cases.

    Returns:
        JSON string with complete topics catalog and metadata
    """
    return await documentation_service.list_sections()


@mcp.tool()
async def get_documentation(topic: str | list[str]) -> str:
    """
    Fetch specific Selise Blocks documentation by topic ID or multiple topics.

    Use this tool to retrieve full documentation content for:
    - Workflows: 'project-setup', 'feature-planning', 'implementation-checklist'
    - Recipes: 'graphql-crud', 'react-hook-form', 'permissions-and-roles'
    - Architecture: 'patterns', 'pitfalls'
    - Components: 'component-quick-reference', 'selise-component-hierarchy'

    Call list_sections first to discover all available topics and their IDs.

    Args:
        topic: Single topic ID (string) or list of topic IDs (e.g., ['graphql-crud', 'patterns'])

    Returns:
        JSON string with full markdown content for requested topics

    Note: Token limit is ~20-25k per call. For large requests, split into multiple calls.
    """
    return await documentation_service.get_documentation(topic)
