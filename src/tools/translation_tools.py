from services import translation_service
from server import server as mcp


@mcp.tool()
async def get_translation_languages(project_key: str = "") -> str:
    """
    Get available languages for translation in a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with available languages including language names, codes, and default status
    """
    return await translation_service.get_languages(project_key)


@mcp.tool()
async def get_translation_modules(project_key: str = "") -> str:
    """
    Get available modules for translation in a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with available modules including module names and IDs
    """
    return await translation_service.get_modules(project_key)


@mcp.tool()
async def save_translation_key_with_translations(
    key_name: str, module_name: str, translations: list[dict], project_key: str = ""
) -> str:
    """
    Save a translation key with provided translations to the project.

    Args:
        key_name: The translation key name to add
        module_name: The module name where the key should be added (e.g., "common", "auth", "profile")
        translations: List of translation objects with "value" and "culture" keys
                     Format: [{"value": "translated text", "culture": "en-US"}, ...]
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with translation key creation result
    """
    return await translation_service.save_translation_key(
        key_name, module_name, translations, project_key
    )
