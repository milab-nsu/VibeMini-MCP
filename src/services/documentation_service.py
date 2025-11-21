import json
from utils import http_client, misc


async def list_sections() -> str:
    """
    Discover all available Selise Blocks documentation topics.
    """
    try:
        # Direct HTTP call without blocks_key (public GitHub content)
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.get(
                misc.DOCS_CONFIG["TOPICS_JSON_URL"],
                timeout=30.0
            )
            response.raise_for_status()
            topics_data = response.json()

        # Extract summary information
        topics_list = topics_data.get("topics", [])
        critical_topics = [t for t in topics_list if t.get("priority") == "critical"]
        workflow_topics = [t for t in topics_list if t.get("type") == "workflow"]
        recipe_topics = [t for t in topics_list if t.get("type") == "recipe"]

        result = {
            "status": "success",
            "message": f"Found {len(topics_list)} documentation topics",
            "metadata": {
                "version": topics_data.get("version"),
                "last_updated": topics_data.get("last_updated"),
                "base_url": topics_data.get("base_url")
            },
            "summary": {
                "total_topics": len(topics_list),
                "critical_count": len(critical_topics),
                "workflow_count": len(workflow_topics),
                "recipe_count": len(recipe_topics)
            },
            "topics": topics_list,
            "critical_first_reads": [
                {
                    "id": t.get("id"),
                    "title": t.get("title"),
                    "read_when": t.get("read_when"),
                    "read_order": t.get("read_order")
                }
                for t in sorted(critical_topics, key=lambda x: x.get("read_order", 999))
            ],
            "next_steps": [
                "For new projects: Call get_documentation with topic='project-setup'",
                "To see all workflow files: Filter topics by type='workflow'",
                "To find patterns: Use the 'use_cases' and 'triggers' fields to match your needs"
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error fetching documentation catalog: {str(e)}",
            "url": misc.DOCS_CONFIG["TOPICS_JSON_URL"]
        }, indent=2)


async def get_documentation(topic: str | list[str]) -> str:
    """
    Fetch specific Selise Blocks documentation by topic ID or multiple topics.
    """
    return await _fetch_documentation(topic)


async def _fetch_documentation(topic: str | list[str]) -> str:
    """
    Helper function to fetch Selise Blocks documentation by topic ID or multiple topics.
    """
    try:
        import httpx

        # Normalize topic to list
        topic_ids = [topic] if isinstance(topic, str) else topic

        # First, fetch topics.json to get metadata
        async with httpx.AsyncClient() as client:
            topics_response = await client.get(
                misc.DOCS_CONFIG["TOPICS_JSON_URL"],
                timeout=30.0
            )
            topics_response.raise_for_status()
            topics_data = topics_response.json()

        topics_list = topics_data.get("topics", [])
        base_url = topics_data.get("base_url", misc.DOCS_CONFIG["BASE_URL"])

        # Find requested topics and fetch their content
        results = []
        not_found = []

        for topic_id in topic_ids:
            # Find topic metadata
            topic_meta = next((t for t in topics_list if t.get("id") == topic_id), None)

            if not topic_meta:
                not_found.append(topic_id)
                continue

            # Fetch documentation content
            doc_url = f"{base_url}{topic_meta.get('path')}"
            try:
                async with httpx.AsyncClient() as client:
                    doc_response = await client.get(doc_url, timeout=30.0)
                    doc_response.raise_for_status()
                    content = doc_response.text

                results.append({
                    "topic_id": topic_id,
                    "title": topic_meta.get("title"),
                    "type": topic_meta.get("type"),
                    "priority": topic_meta.get("priority"),
                    "content": content,
                    "metadata": {
                        "read_when": topic_meta.get("read_when"),
                        "use_cases": topic_meta.get("use_cases"),
                        "warnings": topic_meta.get("warnings", []),
                        "next_steps": topic_meta.get("next_steps", [])
                    }
                })
            except Exception as fetch_error:
                results.append({
                    "topic_id": topic_id,
                    "error": f"Failed to fetch content: {str(fetch_error)}",
                    "url": doc_url
                })

        # Build response
        result = {
            "status": "success" if results else "error",
            "message": f"Retrieved {len(results)} documentation topic(s)",
            "requested": topic_ids,
            "not_found": not_found if not_found else None,
            "documentation": results
        }

        # Add helpful next steps based on what was retrieved
        if any(r.get("topic_id") == "project-setup" for r in results):
            result["reminder"] = "NEXT: Follow Vibecoding flow, then call get_documentation with topic='implementation-checklist'"

        if any(r.get("topic_id") == "implementation-checklist" for r in results):
            result["reminder"] = "NEXT: Call get_documentation for specific patterns like 'graphql-crud' or 'patterns'"

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error fetching documentation: {str(e)}"
        }, indent=2)
