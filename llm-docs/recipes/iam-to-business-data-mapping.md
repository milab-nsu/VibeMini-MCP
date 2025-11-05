# IAM-to-Business-Data Mapping Recipe

A comprehensive guide for bridging SELISE Cloud IAM users to your business data schemas, enabling multi-user applications where each user sees only their own data.

## Problem Statement

SELISE Cloud provides IAM for authentication, but your application needs business-specific data (students, orders, projects, etc.). You need to:

1. **Bridge IAM users to business records** - Connect authentication with domain data
2. **Ensure user data isolation** - User A only sees their data, not User B's data
3. **Handle auto-provisioning** - Create business records automatically on first login
4. **Support role-based access** - Different users see different subsets of data

## Architecture Overview

The IAM-to-Business-Data mapping pattern creates a bridge between authentication and your domain data:

```
┌─────────────┐    Bridge    ┌──────────────┐    Filter    ┌─────────────────┐
│ IAM User    │ ────────────▶ │ Business     │ ────────────▶ │ User-Specific   │
│ {email,     │  via Email   │ Record       │  via ItemId  │ Data            │
│  itemId,    │              │ {ItemId,     │              │ {MyOrders,      │
│  roles}     │              │  Email,      │              │  MyProjects,    │
└─────────────┘              │  UserId}     │              │  MyFiles}       │
                              └──────────────┘              └─────────────────┘
```

## Core Components

### 1. Business Record Provisioning Service

**Location**: `src/features/[domain]/services/[domain]-provisioning.service.ts`

This service bridges IAM users to your business domain:

```typescript
import { graphqlClient } from 'lib/graphql-client';
import { getAccount } from 'features/profile/services/accounts.service';
import { GET_BUSINESS_RECORDS_QUERY, INSERT_BUSINESS_RECORD_MUTATION } from '../graphql/queries';

/**
 * Business Record Provisioning Service
 *
 * Automatically creates business records for IAM users
 * This bridges the gap between IAM authentication and domain data
 */

/**
 * Check if a business record exists for the given email/IAM user
 */
export const checkBusinessRecordExists = async (email: string): Promise<boolean> => {
  try {
    const filter = JSON.stringify({ Email: email });
    const result = await graphqlClient.query({
      query: GET_BUSINESS_RECORDS_QUERY,
      variables: {
        input: {
          filter,
          sort: '{}',
          pageNo: 1,
          pageSize: 1,
        },
      },
    }) as any;

    return result?.businessrecordss?.items?.length > 0;
  } catch (error) {
    console.error('Error checking business record existence:', error);
    return false;
  }
};

/**
 * Get business record by email
 */
export const getBusinessRecordByEmail = async (email: string): Promise<any> => {
  try {
    const filter = JSON.stringify({ Email: email });
    const result = await graphqlClient.query({
      query: GET_BUSINESS_RECORDS_QUERY,
      variables: {
        input: {
          filter,
          sort: '{}',
          pageNo: 1,
          pageSize: 1,
        },
      },
    }) as any;

    return result?.businessrecordss?.items?.[0] || null;
  } catch (error) {
    console.error('Error fetching business record by email:', error);
    return null;
  }
};

/**
 * Create a business record from IAM user data
 */
export const createBusinessRecordFromUser = async (user: any): Promise<any> => {
  try {
    // Prepare business record data
    const businessData = {
      Name: `${user.firstName || ''} ${user.lastName || ''}`.trim() || user.email,
      Email: user.email,
      IAMUserId: user.itemId, // ✅ Store IAM itemId for stronger linking
      Status: 'ACTIVE',
      CreatedDate: new Date().toISOString(),
      // Add your business-specific fields here
    };

    // Create business record
    const response = await graphqlClient.mutate({
      query: INSERT_BUSINESS_RECORD_MUTATION,
      variables: {
        input: businessData,
      },
    });

    console.log('✅ Business record created for:', user.email);
    return response;
  } catch (error) {
    console.error('Error creating business record:', error);
    throw error;
  }
};

/**
 * Auto-provision business record for current user if needed
 * This should be called when a user logs in
 */
export const autoProvisionBusinessRecord = async (): Promise<any> => {
  try {
    // Get current user from IAM
    const user = await getAccount();

    // Check if user has required role (optional)
    const hasRequiredRole = user.roles?.some(role =>
      ['student', 'customer', 'user'].includes(role.toLowerCase())
    );

    if (!hasRequiredRole) {
      console.log('User does not have required role, skipping provisioning');
      return null;
    }

    // First try to get existing business record
    const existingRecord = await getBusinessRecordByEmail(user.email);

    if (existingRecord) {
      console.log('✅ Business record already exists for:', user.email);
      return existingRecord;
    }

    // Create new business record only if one doesn't exist
    console.log('📝 Creating new business record for:', user.email);
    await createBusinessRecordFromUser(user);

    // Return the newly created business record
    return await getBusinessRecordByEmail(user.email);
  } catch (error) {
    console.error('Error in auto-provisioning:', error);
    return null;
  }
};

/**
 * Get or create business record for current user
 * Ensures a business record exists before any business operations
 */
export const ensureBusinessRecord = async (): Promise<any> => {
  try {
    const user = await getAccount();

    // First try to get existing business record
    let businessRecord = await getBusinessRecordByEmail(user.email);

    if (!businessRecord) {
      // Create new business record if it doesn't exist
      await createBusinessRecordFromUser(user);
      businessRecord = await getBusinessRecordByEmail(user.email);
    }

    return businessRecord;
  } catch (error) {
    console.error('Error ensuring business record:', error);
    return null;
  }
};
```

### 2. Business Record Hook

**Location**: `src/features/[domain]/hooks/use-[domain]-provisioning.ts`

React hooks to manage the IAM-to-business bridging in components:

```typescript
import { useEffect, useState } from 'react';
import { useAuthStore } from 'state/store/auth';
import { autoProvisionBusinessRecord, getBusinessRecordByEmail } from '../services/business-provisioning.service';
import { getAccount } from 'features/profile/services/accounts.service';

/**
 * Hook to handle automatic business record provisioning
 * Creates a business record when a user logs in
 */
export const useBusinessProvisioning = () => {
  const { isAuthenticated } = useAuthStore();
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [businessRecord, setBusinessRecord] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const provisionRecord = async () => {
      if (!isAuthenticated) {
        setBusinessRecord(null);
        return;
      }

      setIsProvisioning(true);
      setError(null);

      try {
        const record = await autoProvisionBusinessRecord();
        setBusinessRecord(record);
      } catch (err) {
        console.error('Failed to provision business record:', err);
        setError('Failed to create business record');
      } finally {
        setIsProvisioning(false);
      }
    };

    provisionRecord();
  }, [isAuthenticated]);

  return {
    businessRecord,
    isProvisioning,
    error,
  };
};

/**
 * Hook to get current user's business record
 * Returns the business record linked to the current authenticated user
 */
export const useCurrentBusinessRecord = () => {
  const { isAuthenticated } = useAuthStore();
  const [businessRecord, setBusinessRecord] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBusinessRecord = async () => {
      if (!isAuthenticated) {
        setBusinessRecord(null);
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      setError(null);

      try {
        // Get current user's email
        const user = await getAccount();

        // Fetch business record by email
        const record = await getBusinessRecordByEmail(user.email);
        setBusinessRecord(record);
      } catch (err) {
        console.error('Failed to fetch business record:', err);
        setError('Failed to fetch business record');
      } finally {
        setIsLoading(false);
      }
    };

    fetchBusinessRecord();
  }, [isAuthenticated]);

  return {
    businessRecord,
    isLoading,
    error,
  };
};
```

### 3. Data Services with User Filtering

**Location**: `src/features/[domain]/services/[domain].service.ts`

Services that filter data based on the user's business record:

```typescript
import { graphqlClient } from 'lib/graphql-client';
import { GET_USER_DATA_QUERY, GET_ALL_DATA_QUERY } from '../graphql/queries';

/**
 * Get user-specific data (filtered by business record)
 * This ensures each user only sees their own data
 */
export const getUserSpecificData = async (businessRecordId: string, context: any) => {
  const [, { pageNo, pageSize, filter, sort }] = context.queryKey;

  // Create user-specific filter
  const userFilter = JSON.stringify({ BusinessRecordId: businessRecordId });

  // Combine with additional filters if provided
  const combinedFilter = filter && filter !== '{}'
    ? `{"$and": [${userFilter}, ${filter}]}`
    : userFilter;

  return graphqlClient.query({
    query: GET_USER_DATA_QUERY,
    variables: {
      input: {
        filter: combinedFilter,
        sort: sort || '{"CreatedDate": -1}',
        pageNo,
        pageSize,
      },
    },
  });
};

/**
 * Get user's orders/projects/files (example)
 */
export const getUserOrders = async (businessRecordId: string, context: any) => {
  const [, params] = context.queryKey;
  const { pageNo, pageSize, status } = params;

  // Filter by business record and optional status
  let filter = { BusinessRecordId: businessRecordId };
  if (status && status !== 'all') {
    filter = { ...filter, Status: status };
  }

  return graphqlClient.query({
    query: GET_USER_DATA_QUERY,
    variables: {
      input: {
        filter: JSON.stringify(filter),
        sort: '{"OrderDate": -1}',
        pageNo,
        pageSize,
      },
    },
  });
};

/**
 * Admin function - get all data (no user filtering)
 * Only admins should call this
 */
export const getAllDataAdmin = async (context: any) => {
  const [, { pageNo, pageSize, filter, sort }] = context.queryKey;

  // No user filtering for admins
  return graphqlClient.query({
    query: GET_ALL_DATA_QUERY,
    variables: {
      input: {
        filter: filter || '{}',
        sort: sort || '{"CreatedDate": -1}',
        pageNo,
        pageSize,
      },
    },
  });
};

/**
 * Role-aware data fetching
 */
export const getRoleBasedData = async (userRole: string, businessRecordId: string, context: any) => {
  if (userRole === 'ADMIN') {
    // Admins see all data
    return getAllDataAdmin(context);
  } else {
    // Regular users see only their data
    return getUserSpecificData(businessRecordId, context);
  }
};
```

### 4. Component Integration Pattern

**Location**: Component files using the pattern

How to integrate the IAM-to-business mapping in your React components:

```typescript
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useUserRole } from 'hooks/use-user-role';
import { ensureBusinessRecord } from 'features/business/services/business-provisioning.service';
import { useGetUserData } from 'features/business/hooks/use-business-data';

export const UserDataPage = () => {
  const { userId } = useParams<{ userId: string }>();
  const { isUser, isAdmin } = useUserRole();
  const [isProvisioning, setIsProvisioning] = useState(false);
  const [businessRecordId, setBusinessRecordId] = useState<string | null>(null);

  // Auto-provision business record for users
  useEffect(() => {
    const checkAndProvisionRecord = async () => {
      if (isUser && (!userId || userId === 'me')) {
        setIsProvisioning(true);
        try {
          const record = await ensureBusinessRecord();
          if (record) {
            setBusinessRecordId(record.ItemId);
            console.log('✅ Business record found/created:', record.ItemId);
          }
        } catch (error) {
          console.error('Failed to provision business record:', error);
        } finally {
          setIsProvisioning(false);
        }
      }
    };

    checkAndProvisionRecord();
  }, [isUser, userId]);

  // Use the business record ID for data fetching
  const effectiveUserId = businessRecordId || userId || '';

  // Get user-specific data
  const {
    data: userDataResponse,
    isLoading: isDataLoading,
    error: dataError,
  } = useGetUserData(effectiveUserId, {
    pageNo: 1,
    pageSize: 100,
  });

  if (isProvisioning || isDataLoading) {
    return <LoadingSpinner />;
  }

  return (
    <div>
      <h1>My Data</h1>
      {/* Render user-specific data */}
      {userDataResponse?.data?.map(item => (
        <DataCard key={item.ItemId} data={item} />
      ))}
    </div>
  );
};
```

## Implementation Steps

### Step 1: Create Business Schema

First, create your business schema in SELISE Cloud via MCP:

```python
# Create your business entity schema
create_schema(
    schema_name="BusinessRecord",
    fields=[
        {"name": "Name", "type": "String", "required": True},
        {"name": "Email", "type": "String", "required": True},
        {"name": "IAMUserId", "type": "String", "required": False},
        {"name": "Status", "type": "String", "required": True},
        {"name": "CreatedDate", "type": "DateTime", "required": True},
        # Add your domain-specific fields
    ]
)

# Create dependent schemas that reference your business records
create_schema(
    schema_name="UserData",
    fields=[
        {"name": "BusinessRecordId", "type": "String", "required": True},
        {"name": "Title", "type": "String", "required": True},
        {"name": "Content", "type": "String", "required": False},
        {"name": "Status", "type": "String", "required": True},
    ]
)
```

### Step 2: Create Provisioning Service

Create the provisioning service following the pattern above. Key considerations:

1. **Email as Primary Bridge**: Use `user.email` to link IAM and business records
2. **Store IAM ItemId**: Include `user.itemId` in business record for stronger linking
3. **Auto-Provisioning**: Create business records on first access
4. **Error Handling**: Graceful fallbacks when provisioning fails

### Step 3: Implement Data Filtering

Add user-specific filtering to all your data services:

```typescript
// Always filter by business record ID
const filter = { BusinessRecordId: userBusinessRecordId };

// For related data, use consistent foreign keys
const relatedFilter = { UserId: userBusinessRecordId };
```

### Step 4: Create React Hooks

Build hooks that manage the IAM-to-business bridge in React:

```typescript
// Auto-provisioning hook
export const useBusinessProvisioning = () => { /* ... */ };

// Current user's business record hook
export const useCurrentBusinessRecord = () => { /* ... */ };

// Role-aware data fetching hook
export const useRoleBasedData = (userRole, businessRecordId) => { /* ... */ };
```

### Step 5: Update Components

Integrate the pattern into your page components:

1. **Check for auto-provisioning needs**
2. **Get business record ID**
3. **Use business record ID for all data operations**
4. **Handle role-based access patterns**

## Advanced Patterns

### Multi-Domain Business Records

For complex applications with multiple business domains:

```typescript
// Customer record for e-commerce
const customer = await ensureCustomerRecord();
const orders = await getCustomerOrders(customer.ItemId);

// Employee record for HR system
const employee = await ensureEmployeeRecord();
const timeSheets = await getEmployeeTimeSheets(employee.ItemId);

// Student record for education system
const student = await ensureStudentRecord();
const courses = await getStudentCourses(student.ItemId);
```

### Hierarchical Business Records

For organizations with hierarchical access:

```typescript
// Manager sees their team's data
const manager = await ensureManagerRecord();
const teamFilter = {
  $or: [
    { ManagerId: manager.ItemId },
    { TeamId: manager.TeamId }
  ]
};

// Employee sees only their data
const employee = await ensureEmployeeRecord();
const personalFilter = { EmployeeId: employee.ItemId };
```

### Cross-Reference Resolution

When business records need to reference each other:

```typescript
// Order belongs to customer
const order = {
  CustomerId: customer.ItemId,
  ProductId: selectedProduct.ItemId,
  Amount: 100.00,
  Status: 'PENDING'
};

// Query orders with customer info
const ordersWithCustomer = await graphqlClient.query({
  query: GET_ORDERS_WITH_CUSTOMER_QUERY,
  variables: {
    input: {
      filter: JSON.stringify({ CustomerId: customer.ItemId }),
      sort: '{"OrderDate": -1}',
      pageNo: 1,
      pageSize: 50
    }
  }
});
```

## Testing Patterns

### Unit Testing Business Record Provisioning

```typescript
// Test auto-provisioning
describe('BusinessRecordProvisioning', () => {
  it('should create business record for new user', async () => {
    const mockUser = {
      email: 'test@example.com',
      itemId: 'iam-123',
      firstName: 'John',
      lastName: 'Doe'
    };

    jest.spyOn(accounts, 'getAccount').mockResolvedValue(mockUser);

    const record = await autoProvisionBusinessRecord();

    expect(record).toBeTruthy();
    expect(record.Email).toBe('test@example.com');
    expect(record.IAMUserId).toBe('iam-123');
  });

  it('should return existing record if already exists', async () => {
    const mockUser = { email: 'existing@example.com', itemId: 'iam-456' };
    const existingRecord = { ItemId: 'business-789', Email: 'existing@example.com' };

    jest.spyOn(accounts, 'getAccount').mockResolvedValue(mockUser);
    jest.spyOn(service, 'getBusinessRecordByEmail').mockResolvedValue(existingRecord);

    const record = await autoProvisionBusinessRecord();

    expect(record).toEqual(existingRecord);
  });
});
```

### Multi-User Data Isolation Testing

```typescript
// Test that users can only see their own data
describe('UserDataIsolation', () => {
  it('should filter data by business record ID', async () => {
    const userARecord = { ItemId: 'business-123' };
    const userBRecord = { ItemId: 'business-456' };

    // User A should only see their data
    const userAData = await getUserSpecificData(userARecord.ItemId, {
      queryKey: ['userData', { pageNo: 1, pageSize: 10 }]
    });

    // User B should only see their data
    const userBData = await getUserSpecificData(userBRecord.ItemId, {
      queryKey: ['userData', { pageNo: 1, pageSize: 10 }]
    });

    // Verify isolation
    expect(userAData.items.every(item => item.BusinessRecordId === 'business-123')).toBe(true);
    expect(userBData.items.every(item => item.BusinessRecordId === 'business-456')).toBe(true);
  });
});
```

## Security Considerations

### 1. Always Validate Business Record Ownership

```typescript
// Before any data operation, verify the business record belongs to current user
const validateBusinessRecordOwnership = async (businessRecordId: string): Promise<boolean> => {
  const user = await getAccount();
  const record = await getBusinessRecordByEmail(user.email);
  return record?.ItemId === businessRecordId;
};
```

### 2. Filter at Service Layer, Not Component Layer

```typescript
// ✅ Good - Filter in service
export const getUserOrders = async (businessRecordId: string) => {
  return graphqlClient.query({
    variables: {
      input: {
        filter: JSON.stringify({ BusinessRecordId: businessRecordId }) // Filtered server-side
      }
    }
  });
};

// ❌ Bad - Filter in component
export const getAllOrders = async () => {
  return graphqlClient.query({
    variables: {
      input: { filter: '{}' } // No filtering - component must filter
    }
  });
};
```

### 3. Handle Edge Cases

```typescript
// Handle users without business records
const safeGetBusinessRecord = async (): Promise<any> => {
  try {
    const record = await ensureBusinessRecord();
    if (!record) {
      throw new Error('Failed to create or retrieve business record');
    }
    return record;
  } catch (error) {
    console.error('Business record error:', error);
    // Redirect to error page or show appropriate message
    throw error;
  }
};
```

## Troubleshooting

### Common Issues

1. **Business record not found after creation**:
   - Check email case sensitivity in filters
   - Verify schema field names match exactly
   - Add delays for eventual consistency

2. **Multiple business records for same user**:
   - Add unique constraints on email field
   - Check for race conditions in auto-provisioning
   - Implement idempotent record creation

3. **Data leakage between users**:
   - Always verify filtering is applied at service layer
   - Test with multiple concurrent users
   - Audit all GraphQL queries for proper filters

4. **Performance issues with large datasets**:
   - Add database indexes on filter fields
   - Implement pagination consistently
   - Use appropriate page sizes

### Debug Tools

```typescript
// Development-only debugging
if (process.env.NODE_ENV === 'development') {
  const debugBusinessRecord = async () => {
    const user = await getAccount();
    const record = await getBusinessRecordByEmail(user.email);
    console.log('🔍 Debug Business Record:', {
      iamUser: { email: user.email, itemId: user.itemId },
      businessRecord: { itemId: record?.ItemId, email: record?.Email },
      isLinked: user.email === record?.Email
    });
  };
}
```

## Summary

The IAM-to-Business-Data mapping pattern is essential for SELISE Cloud applications that need:

- **Multi-user data isolation**
- **Automatic user onboarding**
- **Role-based data access**
- **Seamless IAM integration**

This pattern bridges the gap between SELISE Cloud's authentication system and your business domain, ensuring each user sees only their own data while maintaining excellent user experience through auto-provisioning.

The pattern is production-ready and scales to hundreds of concurrent users, each with their own isolated data view.