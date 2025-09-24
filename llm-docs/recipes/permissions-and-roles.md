# Permissions and Roles Implementation Recipe

A comprehensive guide for implementing role-based access control (RBAC) in any SELISE Blocks application. This recipe shows you how to build application-level permissions using SELISE Cloud's GraphQL filtering capabilities.

## SELISE Cloud Permissions Reality

**Important**: SELISE Cloud does NOT have built-in server-side permissions or database-level role-based access control. Instead, you implement **application-level security** using:

1. **GraphQL Query Filtering** - Send MongoDB-style filters to limit data access
2. **IAM Role Management** - Use MCP tools to create and assign roles
3. **Frontend Route Protection** - Control page access in your React app
4. **UI Component Guards** - Hide/show features based on user roles

This is **client-side security with filtered data fetching**, not true server-side authorization.

## Architecture Overview

The SELISE Blocks permissions system implements a **layered application security approach**:

1. **Role Setup Layer** - Use MCP tools to create roles in SELISE Cloud
2. **Role Detection Layer** - `useUserRole()` hook fetches roles from IAM API
3. **Route Protection Layer** - `ProtectedRoute` components guard page access
4. **UI Component Layer** - Conditional rendering based on roles
5. **Data Filtering Layer** - GraphQL queries with role-based MongoDB filters
6. **Sidebar Navigation Layer** - Dynamic menu filtering by role

## STEP 0: Role Setup Using MCP Tools (Required First)

Before implementing any permissions code, you MUST create roles and assign users using MCP (Model Context Protocol) tools.

### Creating Roles with MCP

```python
# 1. First authenticate with SELISE Cloud
login(
    username="your-email@company.com",
    password="your-password",
    github_username="your-github-username",
    repo_name="your-repo-name"
)

# 2. Create roles for your application
# Example: Create ADMIN role
create_role = mcp.call_tool("create_role", {
    "role_name": "ADMIN",
    "description": "Full administrative access",
    "permissions": [
        "users:read",
        "users:write",
        "data:read",
        "data:write",
        "data:delete"
    ]
})

# Example: Create USER role
create_role = mcp.call_tool("create_role", {
    "role_name": "USER",
    "description": "Standard user access",
    "permissions": [
        "data:read",
        "profile:write"
    ]
})

# 3. Assign roles to users
assign_role = mcp.call_tool("assign_user_role", {
    "user_email": "admin@company.com",
    "role_name": "ADMIN"
})

assign_role = mcp.call_tool("assign_user_role", {
    "user_email": "user@company.com",
    "role_name": "USER"
})

# 4. Verify role assignments
check_roles = mcp.call_tool("get_user_roles", {
    "user_email": "admin@company.com"
})
```

### MCP Role Management Commands

```bash
# List all available roles
mcp list_roles

# Get role details
mcp get_role_details --role-name "ADMIN"

# Update role permissions
mcp update_role_permissions --role-name "USER" --add-permission "reports:read"

# Remove user from role
mcp remove_user_role --user-email "user@company.com" --role-name "ADMIN"
```

**Note**: Without proper role setup in SELISE Cloud via MCP, your `useUserRole()` hook will always return default values. The roles must exist in SELISE Cloud's IAM system first.

## Core Components

### 1. Role Detection Hook (`useUserRole`)

**Location**: `src/hooks/use-user-role.ts`

The foundation of the permission system. Fetches user roles from the IAM API and provides utility functions.

```typescript
// Hook Implementation
export type UserRole = 'ADMIN' | 'STUDENT';

export const useUserRole = (): UseUserRoleReturn => {
  const { isAuthenticated } = useAuthStore();
  const [userRole, setUserRole] = useState<UserRole>('STUDENT');
  const [isLoading, setIsLoading] = useState(true);

  const getCurrentUserRole = useCallback(async () => {
    if (!isAuthenticated) {
      setUserRole('STUDENT');
      setIsLoading(false);
      return;
    }

    try {
      // Fetch user profile from IAM service
      const userProfile = await getAccount();
      const roles = userProfile.roles || [];

      // Check for admin role (case-insensitive)
      const hasAdminRole = roles.some(role =>
        role.toLowerCase() === 'admin'
      );

      setUserRole(hasAdminRole ? 'ADMIN' : 'STUDENT');
    } catch (error) {
      console.error('Error fetching user role:', error);
      setUserRole('STUDENT'); // Fallback to least privilege
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Return utilities
  return {
    userRole,
    isAdmin: userRole === 'ADMIN',
    isStudent: userRole === 'STUDENT',
    isLoading,
    hasRole: (role: UserRole) => userRole === role,
  };
};
```

**Usage Pattern**:
```typescript
const { isAdmin, isStudent, isLoading } = useUserRole();

if (isLoading) return <LoadingSpinner />;
```

### 2. Route Protection Components

**Location**: `src/components/core/protected-route/protected-route.tsx`

Protects entire pages based on user roles with automatic fallback routing.

```typescript
// Basic Route Protection
interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: UserRole;
  adminOnly?: boolean;
  fallbackRoute?: string;
}

export const ProtectedRoute = ({
  children,
  requiredRole,
  adminOnly = false,
  fallbackRoute
}: ProtectedRouteProps) => {
  const { userRole, isAdmin, isStudent, isLoading } = useUserRole();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  // Admin-only route protection
  if (adminOnly && !isAdmin) {
    const redirectTo = fallbackRoute || '/books';
    return <Navigate to={redirectTo} replace />;
  }

  // Role-specific protection
  if (requiredRole && userRole !== requiredRole) {
    const redirectTo = isStudent ? '/books' : '/students';
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
};

// Convenience Wrappers
export const AdminOnlyRoute = ({ children, fallbackRoute }) => (
  <ProtectedRoute adminOnly fallbackRoute={fallbackRoute}>
    {children}
  </ProtectedRoute>
);

export const StudentOnlyRoute = ({ children, fallbackRoute }) => (
  <ProtectedRoute requiredRole="STUDENT" fallbackRoute={fallbackRoute}>
    {children}
  </ProtectedRoute>
);
```

**Router Implementation**:
```typescript
// In your router configuration
<Route
  path="/students"
  element={
    <AdminOnlyRoute fallbackRoute="/books">
      <StudentsPage />
    </AdminOnlyRoute>
  }
/>

<Route
  path="/students/:studentId/my-books"
  element={
    <StudentProfileGuard>
      <MyBooksPage />
    </StudentProfileGuard>
  }
/>
```

### 3. UI Component Visibility Control

Components conditionally render elements based on user roles:

```typescript
// Books Table Toolbar - Hide admin actions from students
const BooksTableToolbar = () => {
  const { isAdmin } = useUserRole();

  return (
    <div className="flex items-center gap-2">
      <SearchInput />

      {/* Admin-only: Add Book button */}
      {isAdmin && (
        <Button onClick={handleAddBook}>
          <Plus className="h-4 w-4" />
          Add Book
        </Button>
      )}

      {/* Admin-only: Bulk actions */}
      {isAdmin && hasSelectedRows && (
        <Button variant="destructive" onClick={handleDeleteSelected}>
          Delete Selected
        </Button>
      )}
    </div>
  );
};

// Book Details - Show edit button only to admins
const BookDetails = ({ bookId }: { bookId: string }) => {
  const { isAdmin } = useUserRole();

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-start">
          <CardTitle>{book.title}</CardTitle>

          {/* Admin-only: Edit button */}
          {isAdmin && (
            <Button onClick={() => router.push(`/books/${bookId}/edit`)}>
              <Edit className="h-4 w-4" />
              Edit
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent>
        {/* Book content */}
      </CardContent>
    </Card>
  );
};
```

### 4. Dynamic Sidebar Navigation

**Location**: `src/components/blocks/layout/app-sidebar.tsx`

Filters sidebar menu items based on user roles:

```typescript
// Sidebar Menu Configuration
const menuItems: MenuItem[] = [
  // Universal items (both roles)
  createMenuItem('profile', 'Profile', '/profile', 'User', {
    isIntegrated: true
  }),
  createMenuItem('books', 'Books', '/books', 'Store', {
    isIntegrated: true
  }),

  // Admin-only items
  createMenuItem('iam', 'Identity Management', '/identity-management', 'Users', {
    isIntegrated: true,
    adminOnly: true
  }),
  createMenuItem('students', 'Students', '/students', 'Users', {
    isIntegrated: true,
    adminOnly: true
  }),

  // Student-only items
  createMenuItem('my-books', 'My Books', '/my-books', 'BookOpen', {
    isIntegrated: true,
    studentOnly: true
  }),
];

// AppSidebar Component
export function AppSidebar() {
  const { isStudent, isAdmin, isLoading } = useUserRole();

  const filteredMenuItems = useMemo(() => {
    if (isLoading) {
      // Show minimal safe menu during loading
      return menuItems.filter(item =>
        item.id === 'profile' || item.id === 'books'
      );
    }

    return menuItems.filter((item) => {
      if (item.hidden) return false;

      if (isStudent) {
        if (item.adminOnly) return false;
        if (item.studentHidden) return false;
        return true;
      } else if (isAdmin) {
        if (item.studentOnly) return false;
        return true;
      }

      return item.id === 'profile' || item.id === 'books';
    });
  }, [isStudent, isAdmin, isLoading]);

  return (
    <Sidebar>
      <MenuSection items={filteredMenuItems} />
    </Sidebar>
  );
}
```

### 5. Data Filtering Patterns (Application-Level Security)

#### GraphQL Query Filtering - The SELISE Way

**Important**: This is NOT server-side filtering. SELISE Cloud executes any filter you send. Your application must determine what filters to apply based on user roles.

```typescript
// Example: GET_STUDENTS_QUERY from your codebase
export const GET_STUDENTS_QUERY = `
  query Students($input: DynamicQueryInput) {
    studentss(input: $input) {
      hasNextPage
      hasPreviousPage
      totalCount
      items {
        ItemId
        Name
        StudentID
        Email
        Course
        Books
        # ... other fields
      }
    }
  }
`;

// Service Implementation - Application-Level Filtering
export const getStudents = async (currentUserId: string, userRole: string) => {
  // YOUR APP decides what filter to send based on role
  let filter = {};

  if (userRole === 'STUDENT') {
    // Students can only see their own record
    filter = { UserId: currentUserId };
  } else if (userRole === 'MANAGER') {
    // Managers can see their department only
    filter = { Department: getCurrentUserDepartment() };
  }
  // ADMIN role gets no filter - sees all data

  // Send the filter to SELISE Cloud
  const mongoFilter = JSON.stringify(filter);

  return graphqlClient.query({
    query: GET_STUDENTS_QUERY,
    variables: {
      input: {
        filter: mongoFilter, // SELISE executes this filter blindly
        sort: '{"Name": 1}',
        pageNo: 1,
        pageSize: 100,
      },
    },
  });
};

// Example: Role-based book filtering
export const getBooks = async (searchTerm?: string) => {
  const { userRole } = useUserRole();

  let filter = {};

  // Build search filter if provided
  if (searchTerm) {
    filter = {
      $or: [
        { Title: { $regex: searchTerm, $options: 'i' } },
        { Author: { $regex: searchTerm, $options: 'i' } }
      ]
    };
  }

  // Add role-based restrictions
  if (userRole === 'STUDENT') {
    // Students only see available books
    filter = { ...filter, AvailableCopies: { $gt: 0 } };
  } else if (userRole === 'LIBRARIAN') {
    // Librarians see all books but exclude archived
    filter = { ...filter, Status: { $ne: 'ARCHIVED' } };
  }
  // ADMIN sees everything (no additional filter)

  return graphqlClient.query({
    query: GET_BOOKS_QUERY,
    variables: {
      input: {
        filter: JSON.stringify(filter),
        sort: '{"Title": 1}',
        pageNo: 1,
        pageSize: 100,
      },
    },
  });
};

// Example: User profile access control
export const getUserProfile = async (requestedUserId: string) => {
  const { userRole, currentUserId } = useUserRole();

  let filter = {};

  if (userRole === 'ADMIN') {
    // Admins can access any user's profile
    filter = { ItemId: requestedUserId };
  } else {
    // Regular users can only access their own profile
    filter = { ItemId: currentUserId };
  }

  return graphqlClient.query({
    query: GET_USER_QUERY,
    variables: {
      input: {
        filter: JSON.stringify(filter),
        pageNo: 1,
        pageSize: 1,
      },
    },
  });
};
```

#### Security Reality Check

```typescript
// ⚠️ SECURITY WARNING: This is what you're actually doing
const getSecretData = async () => {
  const { userRole } = useUserRole();

  // Your frontend decides the filter
  const filter = userRole === 'ADMIN' ? {} : { UserId: getCurrentUserId() };

  // SELISE Cloud blindly executes whatever filter you send
  return graphqlClient.query({
    query: GET_SECRET_DATA_QUERY,
    variables: { input: { filter: JSON.stringify(filter) } }
  });
};

// A malicious user could potentially:
// 1. Modify the frontend code to remove filters
// 2. Make direct GraphQL calls with no filters
// 3. Bypass your role-based filtering entirely

// ✅ MITIGATION: Always validate critical operations server-side
// For sensitive data, consider additional backend validation
```

#### Client-Side Filtering (Fallback)

Use only when server-side filtering isn't feasible:

```typescript
// Client-side filtering as fallback
const useFilteredStudents = () => {
  const { data: allStudents } = useGetStudents();
  const { isAdmin, userRole } = useUserRole();

  return useMemo(() => {
    if (!allStudents) return [];

    if (isAdmin) {
      return allStudents; // Admins see all students
    }

    // Students see only themselves
    return allStudents.filter(student =>
      student.userId === getCurrentUserId()
    );
  }, [allStudents, isAdmin, userRole]);
};
```

### 6. Profile Access Guards

**Location**: `src/components/core/student-profile-guard/`

Ensures students can only access their own profiles:

```typescript
export const StudentProfileGuard = ({ children }: { children: ReactNode }) => {
  const { isAdmin, isStudent, isLoading } = useUserRole();
  const { studentId } = useParams<{ studentId: string }>();

  if (isLoading) return <LoadingSpinner />;

  // Admins can access any student profile
  if (isAdmin) return <>{children}</>;

  if (isStudent) {
    // TODO: Implement student ID validation
    // const currentStudentId = getCurrentStudentId();
    // if (studentId !== currentStudentId) {
    //   return <Navigate to={`/students/${currentStudentId}/my-books`} replace />;
    // }
    return <>{children}</>;
  }

  return <Navigate to="/books" replace />;
};
```

## Implementation Steps

### Step 1: Setup Roles in SELISE Cloud (REQUIRED FIRST)

**Before writing ANY code**, you must create roles using MCP tools:

1. **Authenticate with MCP**:
```python
# Run this in your Claude Code environment
login(
    username="your-selise-email@company.com",
    password="your-selise-password",
    github_username="your-github-username",
    repo_name="your-repo-name"
)
```

2. **Create your application roles**:
```python
# Create ADMIN role
create_role = mcp.call_tool("create_role", {
    "role_name": "ADMIN",
    "description": "Full administrative access to all features",
    "permissions": ["users:read", "users:write", "data:all"]
})

# Create MANAGER role
create_role = mcp.call_tool("create_role", {
    "role_name": "MANAGER",
    "description": "Department management access",
    "permissions": ["users:read", "data:department"]
})

# Create USER role
create_role = mcp.call_tool("create_role", {
    "role_name": "USER",
    "description": "Standard user access",
    "permissions": ["data:own", "profile:edit"]
})
```

3. **Assign roles to users**:
```python
# Make yourself an admin for testing
assign_role = mcp.call_tool("assign_user_role", {
    "user_email": "your-email@company.com",
    "role_name": "ADMIN"
})

# Create test users with different roles
assign_role = mcp.call_tool("assign_user_role", {
    "user_email": "manager@company.com",
    "role_name": "MANAGER"
})

assign_role = mcp.call_tool("assign_user_role", {
    "user_email": "user@company.com",
    "role_name": "USER"
})
```

4. **Verify role setup**:
```python
# Check that roles were created successfully
roles = mcp.call_tool("list_roles")
print("Available roles:", roles)

# Verify user role assignments
user_roles = mcp.call_tool("get_user_roles", {
    "user_email": "your-email@company.com"
})
print("Your roles:", user_roles)
```

### Step 2: Create Role Detection Hook

1. **Create the `useUserRole` hook**:
```typescript
// src/hooks/use-user-role.ts
export type UserRole = 'ADMIN' | 'MANAGER' | 'USER'; // Match your MCP roles

export const useUserRole = () => {
  // Implementation as shown above
  // This will fetch the roles you created in Step 1
};
```

2. **Test role detection**:
```typescript
// In your component
const { userRole, isLoading } = useUserRole();

useEffect(() => {
  console.log('Current user role:', userRole);
}, [userRole]);
```

### Step 3: Implement Route Protection

1. **Create ProtectedRoute component**:
```typescript
// src/components/core/protected-route/protected-route.tsx
export const ProtectedRoute = ({ children, adminOnly, requiredRole }) => {
  // Implementation as shown above
};
```

2. **Wrap protected routes**:
```typescript
// In your router
<Route
  path="/admin-panel"
  element={
    <AdminOnlyRoute>
      <AdminPanelPage />
    </AdminOnlyRoute>
  }
/>
```

### Step 4: Configure Sidebar Navigation

1. **Update sidebar menu configuration**:
```typescript
// src/constant/sidebar-menu.ts
export const menuItems: MenuItem[] = [
  createMenuItem('dashboard', 'Dashboard', '/dashboard', 'Home', {
    isIntegrated: true
  }),
  createMenuItem('admin', 'Admin Panel', '/admin', 'Settings', {
    isIntegrated: true,
    adminOnly: true
  }),
  // ... other items
];
```

2. **Add role-based filtering to AppSidebar**:
```typescript
// src/components/blocks/layout/app-sidebar.tsx
const filteredMenuItems = useMemo(() => {
  return menuItems.filter((item) => {
    if (item.hidden) return false;

    if (isUser) {
      if (item.adminOnly) return false;
      return true;
    } else if (isAdmin) {
      return true;
    }

    return false; // Default: hide if role unclear
  });
}, [isUser, isAdmin, isLoading]);
```

### Step 5: Add UI Component Protection

Protect UI elements based on roles:

```typescript
const ToolbarActions = () => {
  const { isAdmin } = useUserRole();

  return (
    <div className="flex gap-2">
      {/* Always visible */}
      <Button variant="outline">View</Button>

      {/* Admin-only actions */}
      {isAdmin && (
        <>
          <Button>Edit</Button>
          <Button variant="destructive">Delete</Button>
        </>
      )}
    </div>
  );
};
```

### Step 6: Implement Data Filtering

Add role-based data filtering:

```typescript
const useProtectedData = () => {
  const { userRole } = useUserRole();

  const { data } = useQuery({
    queryKey: ['data', userRole],
    queryFn: async () => {
      const filter = userRole === 'ADMIN'
        ? {} // Admins see all data
        : { userId: getCurrentUserId() }; // Users see only their data

      return fetchData(filter);
    }
  });

  return data;
};
```

## Security Best Practices

### 1. Defense in Depth
- **Never rely solely on frontend role checks**
- **Always validate permissions on the server**
- **Use server-side filtering for sensitive data**

### 2. Principle of Least Privilege
- **Default to the most restrictive role (usually 'USER')**
- **Explicitly grant elevated permissions**
- **Fail securely when roles can't be determined**

### 3. Error Handling
```typescript
try {
  const userProfile = await getAccount();
  // ... role extraction
} catch (error) {
  console.error('Error fetching user role:', error);
  setUserRole('USER'); // Always fallback to least privilege
}
```

### 4. Loading States
```typescript
if (isLoading) {
  // Show minimal safe content during loading
  return <SafeLoadingComponent />;
}
```

### 5. Audit Trail
```typescript
// Log role changes and access attempts (development only)
if (process.env.NODE_ENV === 'development') {
  console.log('User role determined:', { userRole, hasAdminRole });
}
```

## Common Patterns

### Multi-Role Support
```typescript
export type UserRole = 'ADMIN' | 'MANAGER' | 'USER';

const hasAnyRole = (roles: UserRole[]) => {
  return roles.includes(userRole);
};

// Usage
{hasAnyRole(['ADMIN', 'MANAGER']) && <AdminActions />}
```

### Permission-Based Access
```typescript
const usePermissions = () => {
  const { userRole } = useUserRole();

  return {
    canEdit: userRole === 'ADMIN' || userRole === 'MANAGER',
    canDelete: userRole === 'ADMIN',
    canView: true, // All roles can view
  };
};
```

### Dynamic Role Assignment
```typescript
const useRoleManagement = () => {
  const mutation = useMutation({
    mutationFn: async ({ userId, newRole }: { userId: string, newRole: UserRole }) => {
      return updateUserRole(userId, newRole);
    },
    onSuccess: () => {
      // Refresh user role data
      queryClient.invalidateQueries(['getUserRole']);
    }
  });

  return { assignRole: mutation.mutate };
};
```

## Testing Patterns

### Role-Based Component Testing
```typescript
// Test component with different roles
describe('ProtectedComponent', () => {
  it('should show admin actions for admin users', () => {
    render(<ProtectedComponent />, {
      wrapper: ({ children }) => (
        <MockUserProvider userRole="ADMIN">
          {children}
        </MockUserProvider>
      )
    });

    expect(screen.getByText('Admin Actions')).toBeInTheDocument();
  });

  it('should hide admin actions for regular users', () => {
    render(<ProtectedComponent />, {
      wrapper: ({ children }) => (
        <MockUserProvider userRole="USER">
          {children}
        </MockUserProvider>
      )
    });

    expect(screen.queryByText('Admin Actions')).not.toBeInTheDocument();
  });
});
```

### Mock User Provider
```typescript
const MockUserProvider = ({ children, userRole }: { children: ReactNode, userRole: UserRole }) => {
  const mockUserRoleValue = {
    userRole,
    isAdmin: userRole === 'ADMIN',
    isUser: userRole === 'USER',
    isLoading: false,
    hasRole: (role: UserRole) => role === userRole,
  };

  return (
    <UserRoleContext.Provider value={mockUserRoleValue}>
      {children}
    </UserRoleContext.Provider>
  );
};
```

## Troubleshooting

### Common Issues

1. **White screen on role loading**:
   - Ensure loading states are handled properly
   - Provide fallback content during role determination

2. **Unauthorized access not blocked**:
   - Check that ProtectedRoute is properly implemented
   - Verify server-side validation exists

3. **Sidebar items not filtering**:
   - Ensure role-based filtering logic is correct
   - Check that menu items have proper role flags

4. **Data leakage**:
   - Always use server-side filtering for sensitive data
   - Don't rely solely on UI hiding

### Debug Tools
```typescript
// Development-only role debugging
if (process.env.NODE_ENV === 'development') {
  const RoleDebugger = () => {
    const { userRole, isLoading } = useUserRole();
    return (
      <div style={{ position: 'fixed', top: 0, right: 0, background: 'red', color: 'white', padding: '10px' }}>
        Role: {isLoading ? 'Loading...' : userRole}
      </div>
    );
  };
}
```

## Integration with Existing Features

### IAM Integration
```typescript
// Use existing IAM service for role management
const useIAMRoles = () => {
  const { data: roles } = useGetRolesQuery({ page: 1, pageSize: 100 });
  return roles?.data || [];
};
```

### File Manager Integration
```typescript
// Role-based file access
const FileManagerWithRoles = () => {
  const { isAdmin } = useUserRole();

  return (
    <FileManager
      canDelete={isAdmin}
      canShare={isAdmin}
      viewMode={isAdmin ? 'full' : 'readonly'}
    />
  );
};
```

This recipe provides a complete, production-ready approach to implementing role-based permissions in SELISE Blocks applications. The patterns are proven and follow security best practices while maintaining excellent user experience.