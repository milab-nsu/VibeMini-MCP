from server import server as mcp
from services import repository_service


@mcp.tool()
async def list_github_repos(project_key: str = "") -> str:
    """
    Get all GitHub repositories for a project.

    Args:
        project_key: Project key (tenant ID). Uses global tenant_id if not provided

    Returns:
        JSON string with GitHub repositories list
    """
    return await repository_service.list_github_repos(project_key)


@mcp.tool()
async def init_git_repository(github_name: str, repo_name: str, directory_path: str = ".") -> str:
    """
    Initialize a git repository with the specified remote origin and push to dev branch.

    Args:
        github_name: GitHub username or organization name
        repo_name: Repository name on GitHub
        directory_path: Path to the directory to initialize (default: current directory)

    Returns:
        JSON string with git initialization result
    """
    return await repository_service.init_git_repository(github_name, repo_name, directory_path)


@mcp.tool()
async def create_local_repository(repository_name: str = "", template: str = "web", use_cli: bool = True) -> str:
    """
    Create a local Selise repository using Blocks CLI.

    Args:
        repository_name: Name for the local repository (uses project name if empty)
        template: Template to use for the repository (default: "web")
        use_cli: Whether to use CLI mode (default: True)

    Returns:
        JSON string with repository creation result
    """
    return await repository_service.create_local_repository(repository_name, template, use_cli)
