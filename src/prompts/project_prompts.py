from server import server as mcp


@mcp.prompt(
    name="initiate_project_using_blocks_cli",
    enabled=True,
    title="Initiate Project Using Blocks CLI",
    description="Initiate a project using Blocks CLI with the provided project key, name, and application domain.",
)
async def initiate_project_using_blocks_cli(
    project_key: str, project_name: str, app_domain: str
) -> str:
    """
    Initiate a project using Blocks CLI.
    this prompt checks if Blocks CLI is installed, installs it if not,
    and then runs the command to create a new web project with the provided details.
    this will initiate the blocks project in the current directory.

    Args:
        project_key: Unique identifier for the project
        project_name: Name of the project
        app_domain: Domain of the application

    Returns:
        JSON string with initiation result
    """

    if not project_key or not app_domain or not project_name:
        return """Error: project_key, app_domain, and project_name are required. ask the user to provide them."""

    return f"""check if blocks cli is installed, if not, install it by running `npm install -g @seliseblocks/cli`.
    Then, run the command `blocks new web {project_name} --blocks-key {project_key} --app-domain {app_domain}` to initiate the project.
    Finally, return a JSON string with the message: "Project {project_name} initiated successfully."""
