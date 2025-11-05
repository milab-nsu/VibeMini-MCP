# CLAUDE.md

**MUST DO: READ LLM DOCS: llm-docs/ as per the usage guidelines in this file. Don't implement or do anything without following this step. if you fail to find it, do a full directory search first, go back forward etc. dont just start path guidance:  /llm-docs**

This file provides guidance to Claude Code (claude.ai/code) when working with Selise Blocks applications.

## 🚨 CRITICAL: MCP Server Integration

This project uses a FastMCP (Model Context Protocol) server for automating Selise Cloud operations. The MCP tools MUST be used for all project setup and schema management.

### Available MCP Tools

**Authentication (Required First):**
- `login`: Authenticate with Selise Blocks API (ask for username, password, GitHub username, repo name)
- `get_auth_status`: Check authentication status

**Project Management:**
- `create_project`: Create new Selise Cloud project (ALWAYS use for new projects)
- `get_projects`: List existing projects
- `create_local_repository`: Create local repository after cloud project

**Schema Management:**
- `create_schema`: Create new schemas in Selise Cloud
- `list_schemas`: List all schemas
- `get_schema_details`: Get schema field information
- `update_schema_fields`: Update existing schema fields
- `finalize_schema`: Finalize schema changes

**Other Tools:**
- `activate_social_login`: Enable social authentication
- `get_authentication_config`: Check auth configuration
- `get_global_state`: Get current system state

## 📋 Project Setup Workflow (MCP-First)

### Vibecoding Experience Flow (MUST FOLLOW IN ORDER):

**When User Wants to Create Any Webapp/Website:**

1. **FIRST: Read Documentation** (Before talking to user):
   - Read `workflows/user-interaction.md` 
   - Read `workflows/feature-planning.md`
   - Read `agent-instructions/selise-development-agent.md`

2. **User Interaction & Requirements Gathering:**
   - Follow patterns from `user-interaction.md`
   - Create tracking files: `FEATURELIST.md`, `TASKS.md`, `SCRATCHPAD.md`, `CLOUD.md`
   - Ask clarifying questions about features
   - Document everything in FEATURELIST.md
   - Create tasks.md
   - Get user confirmation before proceeding

3. **Project Setup** (After user confirms features):
   - Get project name from user
   - Authentication Flow (Ask one by one if NOT IN user-info.txt):
     ```
     - Username/email for Selise Blocks
     - Password for Selise Blocks  
     - GitHub username
     - GitHub repository name to connect
     ```
   - Project Creation Flow:
     ```python
     # ALWAYS create new project - don't look for existing domains
     create_project(
         project_name="UserProvidedName",
         github_username="from_step_1",
         repository_name="from_step_1"
     )
     
     # If user wants local setup:
     create_local_repository(project_name="UserProvidedName")
     ```

4. **Feature Planning & Schema Design** (AFTER user confirmation):
   - Read `workflows/feature-planning.md` again in full.
   - **IF MULTI-USER APP**: Read `iam-to-business-data-mapping.md` and `permissions-and-roles.md`
   - Break down confirmed features into technical requirements in Tasks.md
   - Analyze what schemas are needed based on FEATURELIST.md
   - **For multi-user apps**: Plan business record bridging and user data isolation
   - Document schema plan in CLOUD.md and ask the user if they are okay if not keep talking to the user to confirm the schemas
   - Create schemas using MCP:
     ```python
     # For each entity the app needs:
     create_schema(
         schema_name="Tasks", 
         fields=[
             {"name": "title", "type": "String", "required": True},
             {"name": "status", "type": "String", "required": True}
         ]
     )
     ```
   - Document all MCP operations and results in CLOUD.md
   - **CONTINUE TO STEP 5 BELOW** - Do not stop here!
   - Move to the next steps as listed here, follow this strictly
   - **After schemas are created, proceed immediately to Implementation Process (Step 5)** 

## 📚 FIRST: Read All Documentation

**BEFORE any implementation, you MUST read these files IN ORDER:**

```
llm-docs/
├── workflows/                  # 🚨 READ FIRST - User interaction patterns
│   ├── user-interaction.md    # How to talk to users, gather requirements
│   └── feature-planning.md     # How to break down tasks and plan
├── recipes/                    # Implementation patterns (MUST FOLLOW)
│   ├── graphql-crud.md         # 🚨 CRITICAL: Only source for data operations!
│   ├── react-hook-form-integration.md
│   ├── confirmation-modal-patterns.md
│   ├── iam-to-business-data-mapping.md  # Multi-user apps: Bridge IAM to business data
│   └── permissions-and-roles.md         # Multi-user apps: Role-based access control
├── component-catalog/          # Component hierarchy (3-layer rule)
│   ├── component-quick-reference.md
│   └── selise-component-hierarchy.md
├── agent-instructions/         # Development workflows
└── llms.txt                   # Project context
```

**MANDATORY READING ORDER:**
1. `workflows/user-interaction.md` - BEFORE talking to user
2. `workflows/feature-planning.md` - BEFORE creating tasks
3. `recipes/graphql-crud.md` - BEFORE any data operations (NOT inventory!)
4. `agent-instructions/selise-development-agent.md` - Development patterns
5. **IF MULTI-USER APP** - Read BEFORE implementation:
   - `recipes/iam-to-business-data-mapping.md` - Bridge IAM users to business data
   - `recipes/permissions-and-roles.md` - Role-based access control
6. Other recipes as needed

**Multi-User App Decision Tree:**
```
Does the app have ANY of these characteristics?
├── Multiple user accounts with different data? ────────────────┐
├── Admin vs regular user access levels? ──────────────────────┤
├── Users should only see "their own" data? ───────────────────┤  YES → Multi-User App
├── Role-based permissions (admin, manager, user)? ────────────┤  READ: iam-to-business + permissions recipes
├── User profiles or account management? ───────────────────────┤
├── Different UI based on user type? ──────────────────────────┘
│
NO → Single-User App (skip multi-user recipes)
```

**Multi-User App Keywords to Watch For:**
- "users", "roles", "admin", "permissions", "accounts", "login", "authentication"
- "only see their own", "different access", "user management", "multi-tenant" 
- "manager can see", "admin controls", "user profiles", "role-based"


## 🔄 Development Workflow

**FOLLOW THE VIBECODING EXPERIENCE FLOW ABOVE FIRST!**

### Continuous Update Cycle
```
┌─────────────────────────────────────────────────┐
│  Pick Task → Update Status → Implement → Test   │
│      ↓            ↓             ↓          ↓     │
│  TASKS.md    TASKS.md      SCRATCHPAD   Code    │
│   [ ]→[🔄]      [🔄]          Notes              │
│      ↓            ↓             ↓          ↓     │
│   Commit → Update Status → Next Task → Repeat   │
│              TASKS.md [x]                        │
│            FEATURELIST.md                        │
└─────────────────────────────────────────────────┘
```

After completing steps 1-4 of the Vibecoding Experience Flow, continue with implementation:

### 5. Implementation Process (Using Your Tracking Files)

#### Step 1: Work from TASKS.md (WITH CONTINUOUS UPDATES)

**Update Frequency:**
- **TASKS.md**: Update IMMEDIATELY when:
  - Starting a task: `[ ]` → `[🔄]`
  - Completing a task: `[🔄]` → `[x]`
  - Discovering sub-tasks: Add below parent task
  - Encountering blockers: Add `[⚠️]` and note in SCRATCHPAD.md

- **SCRATCHPAD.md**: Update CONTINUOUSLY:
  - Every decision made
  - Every error encountered and fix
  - Every insight or pattern discovered
  - Format: `[timestamp] Topic: Details`

- **FEATURELIST.md**: Update when:
  - Feature completed: Mark `[x]`
  - Scope changes: Document what changed
  - New feature discovered: Add to backlog

- **CLOUD.md**: Update when:
  - Schema modified
  - New MCP operations performed
  - Configuration changes made

#### Step 2: Frontend Implementation  
- Follow recipes from llm-docs/recipes/
- Use 3-layer hierarchy: Feature → Block → UI
- Reference graphql-crud.md for data operations (with MCP schema names from CLOUD.md)
- Update TASKS.md as you complete each component

#### Step 3: Testing & Quality
- Use existing test patterns
- Run linting and type checking  
- Test all CRUD operations
- Mark testing tasks complete in TASKS.md

#### Step 4: Sidebar Management (CRITICAL)
**🚨 SIDEBAR RULES:**

1. **DEFAULT = NO SIDEBAR** - Hide/remove unless TASKS.md explicitly requires navigation
2. **Check TASKS.md first** - Only add sidebar if tasks mention "navigation", "menu", or "sidebar"  
3. **Remove ALL template items** - No inventory, IAM, invoices, or "design only" labels
4. **If sidebar needed (per TASKS.md)**:
   ```typescript
   // Start with empty array - remove ALL defaults
   const sidebarItems = []; 
   
   // Only add items that match user's actual features
   // Example for task management app (if TASKS.md requires navigation):
   const sidebarItems = [
     { label: 'Dashboard', path: '/dashboard', icon: 'home' },
     { label: 'Tasks', path: '/tasks', icon: 'list' },
     { label: 'Settings', path: '/settings', icon: 'settings' }
   ];
   ```
5. **Remove "design only" label** - Delete any placeholder text/labels

**Implementation approach:**
- First check: Does TASKS.md have a task for navigation/sidebar?
- If NO: Remove AppSidebar component entirely
- If YES: Empty the default items, add only what's needed

#### Step 5: Git Workflow (COMMIT FREQUENTLY WITH UPDATED TRACKING)

**Commit Frequency: After EVERY completed task or sub-task**

```bash
# Branch for each feature
git checkout -b feature/[task-name]

# BEFORE EVERY COMMIT - Update tracking files:
# 1. Update TASKS.md - mark current task [x]
# 2. Update SCRATCHPAD.md - add implementation notes
# 3. Update FEATURELIST.md - if feature complete
# 4. Update CLOUD.md - if schemas/config changed

# Then commit:
git add .
git diff --staged  # Review ALL changes including tracking files

# Compliance checklist:
# - Used MCP for schema creation?
# - Followed 3-layer hierarchy?
# - Used AdvanceDataTable for tables?
# - Used ConfirmationModal for confirmations?
# - Followed recipes from llm-docs?
# - Updated TASKS.md with completion status?

git commit -m "feat: implement [task] using MCP and Selise patterns

- Completed: [specific features from FEATURELIST.md]
- Updated: TASKS.md, SCRATCHPAD.md status
- References: [relevant schemas from CLOUD.md]"

git checkout main
git merge feature/[task-name]
```

## 🏗️ Architecture & Patterns

### Core Stack
- **Framework**: React TypeScript with Selise Blocks
- **State**: TanStack Query (server) + Zustand (client)
- **Forms**: React Hook Form + Zod validation
- **Styling**: Tailwind CSS
- **GraphQL**: Use recipes/graphql-crud.md (NOT inventory patterns!)

### Feature Structure (MUST FOLLOW)

**Directory Structure - Follow inventory pattern:**
```
src/features/[feature-name]/
├── components/         # Feature-specific components
├── graphql/           # Queries and mutations (if using GraphQL)
├── hooks/             # Feature-specific hooks
├── services/          # API calls and business logic
├── types/             # TypeScript interfaces
└── index.ts           # Public exports
```

**⚠️ CRITICAL: Inventory is for STRUCTURE ONLY, not data operations!**
- Use `src/features/inventory/` as template for folder structure
- NEVER copy inventory's GraphQL patterns - they're different
- For data operations, ONLY follow `recipes/graphql-crud.md`

### Component Hierarchy (3-Layer Rule)
```
1. Feature Components (src/features/*/components/)
2. Block Components (src/components/blocks/)
3. UI Components (src/components/ui/)
```

### Critical Patterns from Recipes

#### GraphQL Operations (from graphql-crud.md - NOT inventory!)
**🚨 CRITICAL QUIRKS - MUST KNOW:**
- **ALWAYS get schema names from MCP first** using `list_schemas()` and `get_schema_details()`
- **Query fields**: Schema name + single 's' (TodoTask → TodoTasks)
- **Mutations**: operation + schema name (insertTodoTask, updateTodoTask)
- **Input types**: SchemaName + Operation + Input (TodoTaskInsertInput)
- ALWAYS use MongoDB filter: `JSON.stringify({_id: "123"})`
- Use `_id` field for filtering, NEVER `ItemId`
- NEVER use Apollo Client - use `graphqlClient` from `lib/graphql-client`
- Response: `result.[SchemaName]s.items` (no 'data' wrapper)
- **MANDATORY**: Use MCP to verify exact schema names before implementing

#### Data Tables (from data-table-with-crud-operations.md)
- ALWAYS use AdvanceDataTable component
- Never create custom table implementations
- Follow the column definition patterns

#### Forms (from react-hook-form-integration.md)
- Use React Hook Form with Zod schemas
- Follow validation patterns from recipe
- Use Form components from UI layer

#### Confirmations (from confirmation-modal-patterns.md)
- ALWAYS use ConfirmationModal
- Never use browser confirm() or AlertDialog
- Follow async confirmation pattern

#### Multi-User Apps (from iam-to-business-data-mapping.md & permissions-and-roles.md)
**🚨 CRITICAL for apps with multiple users:**
- **IAM Bridging**: Use business record provisioning to bridge IAM users to domain data
- **Data Isolation**: Filter all queries by business record ID - users only see their data
- **Role-Based Access**: Use `useUserRole()` hook for permissions and UI control
- **MCP Role Setup**: MUST create roles in Selise Cloud via MCP before implementing
- **Security Pattern**: Apply filtering at service layer, not component layer
- **User Provisioning**: Auto-create business records on first login

## ⚠️ Common Pitfalls to Avoid

1. **DON'T** look for existing domains - always create new project
2. **DON'T** create schemas manually - use MCP tools
3. **DON'T** skip reading recipes before implementation
4. **DON'T** create custom components when Selise components exist
5. **DON'T** use Apollo Client - use graphqlClient from recipes
6. **DON'T** bypass the 3-layer component hierarchy

## 📝 Implementation Checklist

Before ANY implementation:
- [ ] Authenticated with MCP login tool
- [ ] Created project with MCP create_project
- [ ] Read ALL recipes in llm-docs/recipes/
- [ ] Understood 3-layer component hierarchy
- [ ] Created tracking files (TASKS.md, SCRATCHPAD.md, etc.)
- [ ] Created schemas with MCP tools
- [ ] Documented operations in CLOUD.md

## 🚀 Quick Start Commands

```bash
# After MCP project creation
cd [project-name]
npm install
npm start

# Development
npm run lint       # Check code quality
npm test           # Run tests
npm run build      # Production build
```

## 📖 Priority Documentation

When conflicts arise, follow this priority:
1. **MCP tool usage** (this file's MCP section)
2. **Recipes** (llm-docs/recipes/)
3. **Component hierarchy** (llm-docs/component-catalog/)
4. **General patterns** (other docs)

Remember: MCP automation takes precedence over manual processes. Always use MCP tools for project setup, authentication, and schema management.