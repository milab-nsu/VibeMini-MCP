import json
import utils.http_client as http_client
import utils.misc as misc


async def get_languages(project_key: str = "") -> str:
    """
    Get available languages for a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with available languages
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps(
                {
                    "status": "error",
                    "message": "Authentication required. Please login first using the login tool.",
                },
                indent=2,
            )

        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key.",
                    },
                    indent=2,
                )
            project_key = misc.app_state["tenant_id"]

        params = {"projectKey": project_key}

        response = await http_client.get(
            misc.API_CONFIG["UILM_GET_LANGUAGES_URL"],
            params=params,
            access_token=misc.auth_state["access_token"],
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        # Response is already a list
        if isinstance(response, list):
            languages = response
        else:
            languages = []

        result = {
            "status": "success",
            "message": f"Found {len(languages)} language(s)",
            "project_key": project_key,
            "languages": languages,
            "summary": [],
        }

        # Add summary for easier reading
        for lang in languages:
            result["summary"].append(
                {
                    "name": lang.get("languageName"),
                    "code": lang.get("languageCode"),
                    "is_default": lang.get("isDefault", False),
                    "item_id": lang.get("itemId"),
                }
            )

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting languages: {str(e)}"},
            indent=2,
        )


async def get_modules(project_key: str = "") -> str:
    """
    Get available modules for a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with available modules
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps(
                {
                    "status": "error",
                    "message": "Authentication required. Please login first using the login tool.",
                },
                indent=2,
            )

        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key.",
                    },
                    indent=2,
                )
            project_key = misc.app_state["tenant_id"]

        params = {"projectKey": project_key}

        response = await http_client.get(
            misc.API_CONFIG["UILM_GET_MODULES_URL"],
            params=params,
            access_token=misc.auth_state["access_token"],
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        # Response is already a list
        if isinstance(response, list):
            modules = response
        else:
            modules = []

        result = {
            "status": "success",
            "message": f"Found {len(modules)} module(s)",
            "project_key": project_key,
            "modules": modules,
            "summary": [],
        }

        # Add summary for easier reading
        for module in modules:
            result["summary"].append(
                {
                    "name": module.get("moduleName"),
                    "item_id": module.get("itemId"),
                    "created": module.get("createDate"),
                }
            )

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting modules: {str(e)}"},
            indent=2,
        )


async def translate_text(text: str, target_language: str) -> str:
    """
    Translate the given text to the target language.

    IMPORTANT FOR AI AGENT: When this function is called, you MUST translate the text
    to the specified target_language. Do not return the original text.

    - Convert underscores to spaces first (e.g., "About_Us" -> "About Us")
    - Then translate it naturally to the target language
    - Return ONLY the translated text, nothing else

    Examples:
    - translate_text("Home", "German") -> "Startseite"
    - translate_text("About", "Bengali") -> "সম্পর্কে"
    - translate_text("Contact_Us", "Spanish") -> "Contáctenos"

    Args:
        text: Text to translate (usually a key name with underscores)
        target_language: Target language name (e.g., "German", "Bengali", "Spanish")

    Returns:
        Translated text in the target language
    """
    # AI Agent: Translate the text here based on the instructions above
    readable_text = text.replace("_", " ")
    return readable_text


async def save_translation_key(
    key_name: str, module_name: str, translations: list[dict], project_key: str = ""
) -> str:
    """
    Save a translation key with provided translations to the project.

    Args:
        key_name: The translation key name to add
        module_name: The module name (e.g., "common", "auth", "profile")
        translations: List of translation objects with "value" and "culture" keys
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with translation key creation result
    """
    try:
        # Check if authenticated
        if not misc.is_token_valid():
            return json.dumps(
                {
                    "status": "error",
                    "message": "Authentication required. Please login first using the login tool.",
                },
                indent=2,
            )

        # Use global tenant_id if project_key is not provided
        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "No project key provided and no tenant ID in global state. Please run get_projects or provide project_key.",
                    },
                    indent=2,
                )
            project_key = misc.app_state["tenant_id"]

        # Get modules and find the matching module
        modules_result = await get_modules(project_key)
        modules_data = json.loads(modules_result)

        if modules_data.get("status") != "success":
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to retrieve modules",
                    "details": modules_data,
                },
                indent=2,
            )

        modules = modules_data.get("modules", [])
        module_id = None
        for module in modules:
            if module.get("moduleName") == module_name:
                module_id = module.get("itemId")
                break

        if not module_id:
            available_modules = [m.get("moduleName") for m in modules]
            return json.dumps(
                {
                    "status": "error",
                    "message": f"Module '{module_name}' not found",
                    "available_modules": available_modules,
                },
                indent=2,
            )

        # Build payload and save
        payload = {
            "keyName": key_name,
            "moduleId": module_id,
            "resources": translations,
            "routes": [],
            "isPartiallyTranslated": True,
            "projectKey": project_key,
            "itemId": "",
            "isNewKey": True,
        }

        response = await http_client.post(
            misc.API_CONFIG["UILM_SAVE_KEY_URL"],
            json=payload,
            access_token=misc.auth_state["access_token"],
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        if response.get("success"):
            result = {
                "status": "success",
                "message": f"Translation key '{key_name}' added successfully to module '{module_name}'",
                "key_details": {
                    "key_name": key_name,
                    "module_name": module_name,
                    "module_id": module_id,
                    "project_key": project_key,
                    "languages_count": len(translations),
                },
                "translations": translations,
                "response": response,
            }
        else:
            result = {
                "status": "error",
                "message": "Failed to add translation key",
                "errors": response.get("errors"),
                "response": response,
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error saving translation key: {str(e)}"},
            indent=2,
        )
