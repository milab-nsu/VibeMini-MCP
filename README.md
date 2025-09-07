# Selise Cloud MCP Server

A comprehensive Model Context Protocol (MCP) server for Selise Cloud platform integration. This server provides 33 MCP tools covering authentication, project management, schema operations, IAM (Identity & Access Management), security configurations, and repository setup within the Selise Cloud ecosystem. Designed for AI agents to streamline enterprise development workflows with complete platform control.

## Features

### 🔐 **Authentication & Security**
- **Multi-Factor Authentication (MFA)**: Email and authenticator app support
- **Single Sign-On (SSO)**: OAuth integration for Google, Facebook, GitHub, and other providers  
- **CAPTCHA Management**: Google reCAPTCHA and hCaptcha configuration
- **Token Management**: Automatic access token handling with expiration tracking

### 🏗️ **Project & Infrastructure**
- **Project Management**: Create, list, and configure Selise Cloud projects
- **Repository Integration**: GitHub/Git repository linking and local repository creation
- **Application Domains**: Automatic domain extraction and configuration
- **Blocks CLI Integration**: Automated CLI installation and repository scaffolding

### 📊 **GraphQL Schema Management**
- **Schema Operations**: Create, list, update, and finalize GraphQL schemas
- **Field Management**: Dynamic schema field addition and modification
- **Data Gateway**: Configure GraphQL data gateway for real-time operations

### 👥 **Identity & Access Management (IAM)**
- **Role Management**: Create and list user roles with descriptions and slugs
- **Permission System**: Comprehensive CRUD operations for permissions with resource groups
- **Role-Permission Assignment**: Assign/remove permissions from roles dynamically
- **Resource Groups**: Organize permissions into logical resource groupings

### 🔧 **Configuration & State**
- **Global State Management**: Track authentication, domains, and project context
- **Authentication Configuration**: Social login activation and settings management
- **Security Headers**: Enterprise-grade API security with proper CORS handling

## Setup

### Prerequisites

- Python 3.8 or higher
- Node.js and npm (for Blocks CLI installation)
- Claude Code or another MCP-compatible client

### Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Add the MCP server to Claude Code**:
   - Open a folder containing the server files in Claude Code
   - Run the following command to add the MCP server:
   ```bash
   claude mcp add selise-cloud python /absolute/path/to/selise_mcp_server.py
   ```

   Replace `/absolute/path/to/selise_mcp_server.py` with the actual path to your server file.

## Available Tools (33 Total)

### 🔐 Authentication & Core (3 tools)
- `login(username, password)` - Authenticate with Selise Cloud API
- `get_auth_status()` - Check current authentication status and token validity
- `get_global_state()` - Get current global state including auth and app state

### 🏗️ Project Management (2 tools)
- `get_projects(tenant_group_id, page, page_size)` - List projects and extract application domains
- `create_project(project_name, repo_name, repo_link, repo_id, is_production)` - Create new Selise Cloud project

### 📊 GraphQL Schema Management (5 tools)
- `create_schema(schema_name, project_key)` - Create new GraphQL schema
- `list_schemas(project_key, keyword, page_size, page_number, sort_descending, sort_by)` - List existing schemas
- `get_schema(schema_id, project_key)` - Get schema details and fields by ID
- `update_schema_fields(schema_id, fields, project_key)` - Update schema field definitions
- `finalize_schema(schema_id, project_key)` - Finalize and commit schema changes

### 🔧 Repository & CLI Management (4 tools)
- `set_application_domain(domain, tenant_id, project_name)` - Set application domain and tenant ID
- `check_blocks_cli()` - Check if Blocks CLI is installed and available
- `install_blocks_cli()` - Install Blocks CLI using npm package manager
- `create_local_repository(repository_name, template, use_cli)` - Create local Selise repository

### 🔑 Authentication Configuration (2 tools)
- `activate_social_login(item_id, project_key, ...)` - Activate social login with token configurations
- `get_authentication_config(project_key)` - Get current authentication configuration

### 🛡️ CAPTCHA Management (3 tools)
- `save_captcha_config(provider, site_key, secret_key, project_key, is_enable)` - Configure Google reCAPTCHA or hCaptcha
- `list_captcha_configs(project_key)` - List all CAPTCHA configurations for project
- `update_captcha_status(item_id, is_enable, project_key)` - Enable/disable CAPTCHA configurations

### 👥 IAM Role Management (2 tools)
- `list_roles(project_key, page, page_size, search, sort_by, sort_descending)` - List all roles with pagination
- `create_role(name, description, slug, project_key)` - Create new role with slug identifier

### 🔐 IAM Permission Management (4 tools)
- `list_permissions(project_key, page, page_size, search, sort_by, sort_descending, is_built_in, resource_group)` - List permissions with filtering
- `create_permission(name, description, resource, resource_group, tags, project_key, type, dependent_permissions, is_built_in)` - Create new permission
- `update_permission(item_id, name, description, resource, resource_group, tags, project_key, type, dependent_permissions, is_built_in)` - Update existing permission
- `get_resource_groups(project_key)` - Get available resource groups for organizing permissions

### 🔗 Role-Permission Assignment (2 tools)
- `set_role_permissions(role_slug, add_permissions, remove_permissions, project_key)` - Assign/remove permissions from roles
- `get_role_permissions(role_slugs, project_key, page, page_size, search, is_built_in, resource_group)` - Get permissions assigned to specific roles

### 🔒 Multi-Factor Authentication (4 tools)
- `enable_mfa(project_key, mfa_types)` - Enable MFA with custom types (email, authenticator)
- `enable_email_mfa(project_key)` - Enable email-only MFA configuration
- `enable_authenticator_mfa(project_key)` - Enable authenticator app-only MFA
- `enable_both_mfa_types(project_key)` - Enable both email and authenticator MFA

### 🌐 Data Gateway (1 tool)
- `configure_blocks_data_gateway(project_key, gateway_config)` - Configure GraphQL data gateway with real-time subscriptions

### 🔑 Single Sign-On (1 tool)
- `add_sso_credential(provider, client_id, client_secret, project_key, is_enable, redirect_uri)` - Add OAuth SSO credentials for providers (Google, Facebook, GitHub, etc.)

## Usage Examples

### Basic Authentication
```python
# Login to Selise Cloud
await login("your-email@example.com", "your-password")

# Check authentication status
await get_auth_status()
```

### Project Setup
```python
# Get list of projects
await get_projects()

# Create a new project
await create_project(
    project_name="my-new-project",
    repo_name="username/my-repo",
    repo_link="https://github.com/username/my-repo.git",
    repo_id="123456789"
)
```

### Schema Management
```python
# Create a new schema
await create_schema("User")

# List all schemas
await list_schemas()

# Get schema by ID
await get_schema("schema-id-here")
```

### Local Repository Creation
```python
# Check if Blocks CLI is installed
await check_blocks_cli()

# Install Blocks CLI if needed
await install_blocks_cli()

# Create a local repository
await create_local_repository("my-app", "web", use_cli=True)
```

### Security & Authentication
```python
# Configure CAPTCHA (Google reCAPTCHA)
await save_captcha_config("recaptcha", "site_key_here", "secret_key_here")

# Enable Multi-Factor Authentication
await enable_both_mfa_types()  # Enables both email and authenticator

# Add Google OAuth SSO
await add_sso_credential("google", "client_id", "client_secret")
```

### Identity & Access Management
```python
# Create roles
await create_role("admin", "Administrator role", "admin")
await create_role("editor", "Editor role", "editor")

# Create permissions
await create_permission("user_management", "Manage users", "Users", "Administration", ["create", "read", "update", "delete"])

# Assign permissions to roles
await set_role_permissions("admin", add_permissions=["permission_id_here"])

# List role permissions
await get_role_permissions(["admin", "editor"])
```

### Data Gateway Configuration
```python
# Configure GraphQL data gateway
await configure_blocks_data_gateway(gateway_config={
    "enableDataGateway": True,
    "enableRealTimeSubscriptions": True
})
```

## Configuration

The server maintains global state for:
- **Authentication**: Access tokens, refresh tokens, and expiration times
- **Application State**: Current application domain, tenant ID, and project name

This state is automatically managed and updated as you use the various tools.

## Error Handling

All tools return JSON responses with:
- `status`: "success" or "error"
- `message`: Descriptive message about the result
- Additional data specific to each tool

## Security Notes

- Access tokens are automatically managed and validated
- Tokens expire and need to be refreshed by re-authenticating
- The server includes security headers matching the Selise Cloud web interface
- Never commit credentials or tokens to version control

## Troubleshooting

### Authentication Issues
- You need to register an account in Selise Cloud first. 

### CLI Issues
- Ensure Node.js and npm are installed
- Check if the Blocks CLI installation was successful
- Verify global npm permissions

### Schema/Project Issues
- Selise cloud doesn't support the same schema names (to be fixed), even for different projects & accounts. If schema creation fails, try a different name. The agent should tell you when it fails due to naming conflicts.

## Security Architecture Discovery

During development, we discovered critical security gaps in Selise Cloud's IAM implementation:

### ⚠️ **Important Security Findings**
- **Permission Enforcement**: Selise's IAM system is purely cosmetic for UI organization
- **No Backend Validation**: `resource` and `resourceGroup` fields accept arbitrary strings
- **API Security**: Only validates Bearer tokens, no role/permission middleware checks
- **Impact**: Any authenticated user can access any API endpoint regardless of assigned permissions

### 🔒 **Defensive Measures Available**
Despite these gaps, this MCP server provides complete IAM tooling for:
- Role-based access control UI development
- Permission system organization and management
- Future-proofing when Selise addresses enforcement gaps

## API Endpoints

The server communicates with the following Selise Cloud API endpoints:

### Core Services
- **Authentication**: `https://api.seliseblocks.com/authentication/v1/OAuth/Token`
- **Projects**: `https://api.seliseblocks.com/identifier/v1/Project/*`
- **GraphQL Schemas**: `https://api.seliseblocks.com/graphql/v1/schemas/*`
- **Configuration**: `https://api.seliseblocks.com/authentication/v1/Configuration/*`

### Security & IAM
- **CAPTCHA**: `https://api.seliseblocks.com/captcha/v1/Configuration/*`
- **IAM Roles**: `https://api.seliseblocks.com/iam/v1/Resource/GetRoles`, `CreateRole`
- **IAM Permissions**: `https://api.seliseblocks.com/iam/v1/Resource/GetPermissions`, `CreatePermission`, `UpdatePermission`
- **Role Assignment**: `https://api.seliseblocks.com/iam/v1/Resource/SetRoles`
- **Resource Groups**: `https://api.seliseblocks.com/iam/v1/Resource/GetResourceGroups`

### Advanced Features
- **Multi-Factor Authentication**: `https://api.seliseblocks.com/mfa/v1/Configuration/Save`
- **Data Gateway**: `https://api.seliseblocks.com/graphql/v1/configurations`
- **SSO Credentials**: `https://api.seliseblocks.com/authentication/v1/Social/SaveSsoCredential`

## Enterprise Features

This MCP server provides enterprise-grade capabilities:

### 🏢 **Complete Platform Control**
- **33 MCP Tools**: Comprehensive Selise Cloud management
- **Zero Manual Configuration**: Automated setup and deployment workflows
- **Enterprise Security**: MFA, SSO, CAPTCHA, and IAM management
- **Production Ready**: Token management, error handling, and state persistence

### 🔧 **Development Workflow Integration**
- **AI Agent Compatible**: Designed for Claude Code and other MCP clients
- **Automated Repository Setup**: GitHub integration with local development
- **Schema Management**: GraphQL schema lifecycle management
- **CLI Integration**: Blocks CLI automation for rapid development

### 📊 **Monitoring & Management**
- **Global State Tracking**: Authentication, projects, and configuration state
- **Comprehensive Error Handling**: Detailed error messages and status codes
- **Security Headers**: Enterprise CORS and security header management
- **Token Validation**: Automatic token refresh and expiration handling