import json
from utils import http_client, misc


async def list_github_repos(project_key: str = "") -> str:
    """Get all GitHub repositories for a project."""
    try:
        if not misc.is_token_valid():
            return json.dumps({"status": "error", "message": "Authentication required."}, indent=2)

        if not project_key:
            if not misc.app_state["tenant_id"]:
                return json.dumps({"status": "error", "message": "No project key provided."}, indent=2)
            project_key = misc.app_state["tenant_id"]

        repos_data = await http_client.get(
            url=misc.API_CONFIG["GITHUB_REPOS_URL"],
            params={"ProjectKey": project_key},
            blocks_key=misc.API_CONFIG["BLOCKS_KEY"],
        )

        result = {
            "status": "success",
            "message": f"Found {len(repos_data)} GitHub repository/repositories",
            "project_key": project_key,
            "repositories": repos_data,
            "summary": [
                {
                    "name": repo.get("name"),
                    "full_name": repo.get("fullName"),
                    "url": repo.get("url"),
                    "description": repo.get("description"),
                    "language": repo.get("language"),
                    "is_private": repo.get("isPrivate"),
                    "default_branch": repo.get("defaultBranch"),
                    "stars": repo.get("stargazersCount", 0),
                    "forks": repo.get("forksCount", 0),
                    "size": repo.get("size", 0),
                    "created_at": repo.get("createdAt"),
                    "updated_at": repo.get("updatedAt")
                }
                for repo in repos_data
            ]
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps({"status": "error", "message": f"Error listing GitHub repos: {str(e)}"}, indent=2)


async def init_git_repository(github_name: str, repo_name: str, directory_path: str = ".") -> str:
    """Initialize a git repository with the specified remote origin and push to dev branch."""
    try:
        import os

        # Change to the specified directory if provided
        if directory_path != ".":
            if not os.path.exists(directory_path):
                return json.dumps({
                    "status": "error",
                    "message": f"Directory '{directory_path}' does not exist"
                }, indent=2)
            os.chdir(directory_path)

        commands = [
            "git init",
            f"git remote add origin https://github.com/{github_name}/{repo_name}",
            "git branch -M dev",
            "git add .",
            "git commit -m 'feat: initiate project'",
            "git push -u origin dev"
        ]

        results = []
        for command in commands:
            result = await misc.run_command(command)
            results.append({
                "command": command,
                "success": result["success"],
                "stdout": result["stdout"],
                "stderr": result["stderr"]
            })

            # If any command fails, return the error
            if not result["success"]:
                return json.dumps({
                    "status": "error",
                    "message": f"Git initialization failed at command: {command}",
                    "error": result["stderr"],
                    "commands_executed": results
                }, indent=2)

        return json.dumps({
            "status": "success",
            "message": f"Git repository initialized successfully with remote origin: https://github.com/{github_name}/{repo_name}",
            "branch": "dev",
            "commands_executed": results
        }, indent=2)

    except Exception as e:
        return json.dumps({
            "status": "error",
            "message": f"Error during git initialization: {str(e)}"
        }, indent=2)


async def create_local_repository(repository_name: str = "", template: str = "web", use_cli: bool = True) -> str:
    """Create a local Selise repository using Blocks CLI."""
    try:
        # Check if we have the required information
        if not misc.app_state["tenant_id"] or not misc.app_state["application_domain"]:
            return json.dumps({
                "status": "error",
                "message": "Missing tenant ID or application domain. Please run get_projects or set_application_domain first."
            }, indent=2)

        # Use project name from global state if repository_name is not provided
        if not repository_name:
            if misc.app_state["project_name"]:
                repository_name = misc.app_state["project_name"]
            else:
                repository_name = "selise-repository"

        # Check if Blocks CLI is available
        cli_check = await misc.run_command("blocks --version")
        if not cli_check["success"]:
            return json.dumps({
                "status": "error",
                "message": "Blocks CLI is not installed. Please run install_blocks_cli first.",
                "details": cli_check["stderr"]
            }, indent=2)

        # Build the command
        cli_flag = "--cli" if use_cli else ""
        command = f"blocks new {template} {repository_name} {cli_flag} --blocks-key {misc.app_state['tenant_id']} --app-domain {misc.app_state['application_domain']}"

        # Create the repository
        result = await misc.run_command(command)

        if result["success"]:
            return json.dumps({
                "status": "success",
                "message": f"Local repository '{repository_name}' created successfully",
                "command_used": command,
                "output": result["stdout"],
                "tenant_id": misc.app_state["tenant_id"],
                "application_domain": misc.app_state["application_domain"],
                "git_prompt": "Git initialization is mandatory for deployment to Selise Cloud. Use the 'init_git_repository' tool to initialize git with your GitHub repository."
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
