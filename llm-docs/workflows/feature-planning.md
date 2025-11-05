# Feature Planning Workflow

## Overview
This guide explains how to break down user requirements into actionable tasks and maintain organized development.

## Required Files Structure

### 1. FEATURELIST.md - Source of Truth (UPDATE TRIGGERS)

**When to Update FEATURELIST.md:**
- ✅ **Task completion**: When all TASKS.md items for a feature are complete
- ✅ **Scope changes**: When user adds/removes/modifies features  
- ✅ **Feature discovery**: When implementation reveals new requirements
- ✅ **Version planning**: When preparing next sprint/release

```markdown
# Feature List for [App Name]

## Version 1.0 (Current Sprint)
- [x] User authentication ← Mark [x] when ALL auth tasks complete in TASKS.md
- [x] Basic CRUD for [entity] ← Mark [x] when ALL CRUD tasks complete
- [🔄] Search and filtering ← Mark [🔄] when any related task starts
- [ ] Export functionality

## Version 1.1 (Next Sprint)  
- [ ] Advanced permissions
- [ ] Bulk operations
- [ ] Email notifications

## Recently Added (During Development)
- [ ] User profile management ← Add here if discovered during implementation
- [ ] Data validation improvements

## Technical Debt
- [ ] Optimize GraphQL queries
- [ ] Add comprehensive error handling  
- [ ] Improve loading states

## Status Legend
- [ ] Not started
- [🔄] In progress (at least one related task active in TASKS.md)
- [x] Complete (all related tasks complete in TASKS.md)
```

### 2. TASKS.md - Implementation Tracking (EXECUTION DOCUMENT)
```markdown
# Development Tasks

## Setup & Configuration
- [ ] Initialize project structure
- [ ] Configure GraphQL client  
- [ ] Setup routing
- [ ] Remove default sidebar (check if navigation needed)

## Feature: [Feature Name from FEATURELIST.md]

### Backend Integration
- [ ] Check CLOUD.md for schema documentation
- [ ] Call get_schema_details("SchemaName") to verify field types
- [ ] Create GraphQL queries matching exact schema types
- [ ] Create GraphQL mutations with correct input types
- [ ] Setup React Query hooks

### UI Components  
- [ ] Create list view with AdvanceDataTable
- [ ] Create add/edit forms with React Hook Form
- [ ] Add ConfirmationModal for delete operations
- [ ] Hide sidebar unless TASKS require navigation
- [ ] Remove "design only" labels if present

### Data Operations
- [ ] Test Create operation - verify types match
- [ ] Test Read/List operation - check pagination
- [ ] Test Update operation - verify _id filtering
- [ ] Test Delete operation - soft delete by default

### Quality Checks
- [ ] Run linting (npm run lint)
- [ ] Run type checking  
- [ ] Test all CRUD operations
- [ ] Verify NoSQL patterns (no JOINs, use references)
```

**IMPORTANT**: 
- Tasks should be **granular and executable** (complete in 15-30 min)
- Update status immediately: `[ ]` → `[🔄]` → `[x]`
- If a task reveals more work, add sub-tasks below it
- **This is your execution guide** - work through it linearly

### 3. SCRATCHPAD.md - Append-Only Notes (TOP)
```markdown
# Development Notes (Newest First)

---
[2024-01-20 10:30] Completed user authentication
- Used BasePasswordForm for consistency
- Added remember me checkbox
- Need to implement password reset next

---
[2024-01-20 09:15] GraphQL field name issue
- ERROR: Field 'getUsers' not found
- FIXED: Changed to 'users' (Selise convention)
- Remember: queries use plural, mutations use singular

---
[2024-01-20 08:00] Starting authentication feature
- Creating new branch: feature/user-auth
- Will use React Hook Form + Zod
- Need to check existing auth patterns in codebase
```

### 4. CLOUD.md - Selise Cloud Configuration
```markdown
# Selise Cloud Configuration

## Entities Created

### User Entity
- Created: 2024-01-20
- Fields:
  - email (String, required, unique)
  - password (String, required)
  - role (String, enum: admin|user)
  - createdAt (DateTime)
- Screenshot: ![User Entity](./screenshots/user-entity.png)

### Task Entity
- Created: 2024-01-20
- Fields:
  - title (String, required)
  - description (Text)
  - status (String, enum: pending|completed)
  - userId (Reference to User)
- Screenshot: ![Task Entity](./screenshots/task-entity.png)

## Permissions Configured
- Admin: Full access to all entities
- User: CRUD own tasks only
- Screenshot: ![Permissions](./screenshots/permissions.png)

## API Keys
- GraphQL Endpoint: https://api.selise.cloud/graphql
- API Key: Stored in .env as REACT_APP_API_KEY
```

## Feature Breakdown Process

### Step 0: Schema Analysis & CLOUD.md Setup (FIRST)

After user confirmation, analyze ALL features to determine backend requirements:

```markdown
# Schema Requirements Analysis
Based on confirmed features:
- User Authentication → User entity (email, role, password)
- Task Management → Tasks entity (title, description, status, userId) 
- File Attachments → Files entity (filename, url, taskId)
- Categories → Categories entity (name, color)
- Team Management → Teams entity (name, memberIds)

# Required Relationships
- Task belongs to User (userId reference)
- Task can have multiple Files (taskId reference)
- Task belongs to Category (categoryId reference)
- User can belong to Team (teamId reference)

# Permission Requirements
- Admin: Full CRUD on all entities
- Manager: CRUD own team's data
- User: CRUD own data only
```

#### CLOUD.md Population Process
1. **Document schema plan** before any MCP operations
2. **Execute MCP operations** for schema creation
3. **Log all operations** with timestamps and results
4. **Document manual fallbacks** if MCP fails
5. **Validate completion** before proceeding to implementation

See: `docs/llm-docs/cloud-setup.md` for complete CLOUD.md workflow

### Step 1: Analyze Feature Requirements
```typescript
// From FEATURELIST.md entry:
"User Management System"

// Break down into:
1. User list view
2. User creation form
3. User edit form
4. User deletion
5. Role assignment
6. Permissions
```

### Step 2: Create Technical Tasks
```markdown
## User Management System

### Feature Structure (MANDATORY)
- [ ] Create feature folder following src/features/inventory/ pattern exactly
- [ ] Setup folder structure: components/, hooks/, services/, types/, index.ts
- [ ] Study inventory feature implementation before starting

### Data Layer
- [ ] Create GraphQL queries for users
- [ ] Create GraphQL mutations (create, update, delete)
- [ ] Setup React Query hooks
- [ ] Add error handling

### UI Components
- [ ] User list with AdvanceDataTable
- [ ] User form with validation
- [ ] Role selector component
- [ ] Delete confirmation modal

### Navigation
- [ ] Remove/hide irrelevant sidebar items
- [ ] Add only app-specific navigation items
- [ ] Configure AppSidebar for this app's needs

### Business Logic
- [ ] Permission checking
- [ ] Email validation
- [ ] Password requirements
- [ ] Audit logging
```

### Step 3: Prioritize and Sequence
```markdown
## Implementation Order

1. **Foundation** (Do First)
   - GraphQL setup
   - Basic list view
   - Route configuration

2. **Core Features** (Do Second)
   - Create functionality
   - Edit functionality
   - Delete functionality

3. **Enhancements** (Do Last)
   - Advanced filtering
   - Bulk operations
   - Export features
```

## Task Status Management

### Status Indicators
- `[ ]` - Not started
- `[🔄]` - In progress
- `[x]` - Completed
- `[⚠️]` - Blocked
- `[🔍]` - In review

### Progress Tracking Example
```markdown
### Current Task: User List View [🔄]
- [x] Create component structure
- [x] Setup AdvanceDataTable
- [🔄] Connect GraphQL query
- [ ] Add loading states
- [ ] Add error handling

**Blockers**: Waiting for API endpoint from backend
**Notes**: Using inventory feature as reference
```

## Git Workflow Integration

### Branch per Feature
```bash
# For each major feature
git checkout -b feature/user-management

# For sub-tasks if needed
git checkout -b feature/user-management-list-view
```

### Commit Messages Tied to Tasks
```bash
# Reference task in commit
git commit -m "feat: implement user list view with AdvanceDataTable

- Added GraphQL query for users
- Setup AdvanceDataTable with sorting
- Added loading and error states

Task: User Management System - List View"
```

## Common Task Patterns

### CRUD Feature Tasks
```markdown
## [Entity] Management

### Backend Setup
- [ ] Create entity in Selise Cloud
- [ ] Configure permissions
- [ ] Test GraphQL queries

### List View
- [ ] Setup AdvanceDataTable
- [ ] Add column definitions
- [ ] Implement sorting/filtering
- [ ] Add pagination

### Create/Edit
- [ ] Build form with React Hook Form
- [ ] Add Zod validation
- [ ] Connect mutations
- [ ] Handle success/error

### Delete
- [ ] Add delete button
- [ ] Setup ConfirmationModal
- [ ] Connect delete mutation
- [ ] Refresh list after delete
```

### Authentication Tasks
```markdown
## Authentication System

### Login
- [ ] Create login page
- [ ] Setup auth context
- [ ] Token management
- [ ] Redirect logic

### Registration
- [ ] Registration form
- [ ] Email verification
- [ ] Password requirements
- [ ] Terms acceptance

### Security
- [ ] Protected routes
- [ ] Token refresh
- [ ] Logout functionality
- [ ] Session management
```

## Decision Documentation

Always document key decisions in SCRATCHPAD.md:

```markdown
---
[Date Time] Architecture Decision: State Management
- Considered: Redux, Zustand, Context
- Chose: Zustand
- Reason: Simpler than Redux, better than Context for complex state
- Reference: Used in inventory feature
```

## Review Checklist

Before marking a task complete:

```markdown
## Task Completion Checklist
- [ ] Feature works as specified
- [ ] Error handling in place
- [ ] Loading states implemented
- [ ] Responsive design verified
- [ ] Code follows patterns from existing features
- [ ] GraphQL queries optimized
- [ ] Permissions checked (if applicable)
- [ ] Tests written (if applicable)
```

## MANDATORY: Inventory Pattern Following

### Before Creating Any Feature
```bash
# ALWAYS study inventory structure first
ls -la src/features/inventory/

# Required folder structure to replicate:
src/features/[your-feature]/
├── components/           # Feature-specific components
├── hooks/               # Feature-specific hooks
├── services/            # API calls and business logic
├── types/               # TypeScript interfaces
└── index.ts            # Clean exports
```

### Pattern Analysis Checklist
- [ ] **Component organization** - How are components grouped?
- [ ] **Service layer structure** - How are API calls organized?
- [ ] **Type definitions** - What naming conventions are used?
- [ ] **Hook patterns** - How are React Query hooks structured?
- [ ] **Export strategy** - What gets exported in index.ts?

### Implementation Rules
1. **Never deviate** from inventory folder structure
2. **Mirror naming conventions** exactly
3. **Follow service patterns** for consistency
4. **Use same export approach** in index.ts

## CRITICAL: After Tasks.md Creation

### Continue to Implementation (CLAUDE.md Step 5)
Once TASKS.md is populated with technical tasks:
1. **STOP** - Do not start implementing yet
2. **Return to CLAUDE.md step 5**: "Implementation Process"  
3. **Work through TASKS.md line by line**:
   - Pick first `[ ]` task
   - Change to `[🔄]` when starting
   - Implement following recipes
   - Mark `[x]` when complete
   - Update SCRATCHPAD.md with notes
4. **NEVER** skip ahead in TASKS.md
5. **ALWAYS** complete current task before moving to next
6. **If blocked**: Document in SCRATCHPAD.md and move to next task

### Implementation Flow with Tracking Updates
```
TASKS.md → Pick Task → Update [🔄] → Implement → Test → Update [x] → Commit → Next
     ↑         ↓                         ↓         ↓        ↓           ↓        ↓
     └── SCRATCHPAD.md ← Log decisions ← Log errors ← Log fixes ← Update notes ──┘
              ↓
         FEATURELIST.md ← Update when feature complete
              ↓
         CLOUD.md ← Update if schemas/config changed
```

### Commit & Update Rhythm
```bash
# EVERY TASK COMPLETION:
1. Update TASKS.md: [🔄] → [x]
2. Add to SCRATCHPAD.md: Implementation notes
3. Git add all changes (code + tracking files)
4. Commit with descriptive message
5. Move to next task

# EVERY FEATURE COMPLETION:
1. Update FEATURELIST.md: Mark feature complete
2. Review all related TASKS.md items are [x]
3. Major commit with feature summary
4. Consider merging to main
```

## Best Practices

1. **Study inventory first** - MANDATORY before any feature work
2. **One task at a time** - Focus prevents context switching
3. **Document blockers** immediately in SCRATCHPAD.md with `[⚠️]`
4. **Update status IN REAL-TIME** - Not after, but AS you work
5. **Reference existing code** - Check src/features/ for patterns
6. **Test incrementally** - Don't wait until end
7. **Commit frequently** - After EVERY task completion (not just features)
8. **Screenshot Selise Cloud** configs for CLOUD.md
9. **Keep tracking files current** - They're your source of truth