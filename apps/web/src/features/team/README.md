# SAHOOL Team Management Feature

Complete team management UI for managing users, roles, and permissions in the SAHOOL platform.

## Features

- **Team Members Management**: View, invite, edit, and remove team members
- **Role-Based Access Control (RBAC)**: 5 predefined roles with specific permissions
- **Bilingual Support**: Full Arabic/English support
- **Multiple View Modes**: Grid, Table, and Permissions Matrix views
- **Real-time Updates**: Uses React Query for automatic cache invalidation
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## File Structure

```
/apps/web/src/features/team/
├── api/
│   └── team-api.ts           # API client functions
├── hooks/
│   └── useTeam.ts            # React Query hooks
├── components/
│   ├── TeamManagement.tsx    # Main page component
│   ├── MemberCard.tsx        # Member card component
│   ├── InviteMemberDialog.tsx# Invite member modal
│   ├── RoleSelector.tsx      # Role dropdown selector
│   └── PermissionsMatrix.tsx # Permissions grid view
├── types/
│   └── team.ts               # TypeScript types and interfaces
├── index.ts                  # Feature exports
└── README.md                 # This file
```

## Roles & Permissions

### Available Roles

1. **ADMIN** (مدير)
   - Full access to all features
   - Can manage team, settings, fields, tasks, and reports

2. **MANAGER** (مدير فريق)
   - Team management
   - Full access to fields and tasks
   - View-only access to reports and settings

3. **FARMER/SCOUT** (مراقب ميداني)
   - Field monitoring
   - Can create and edit tasks
   - Can create reports
   - No access to team or settings

4. **WORKER/OPERATOR** (مشغل)
   - Task execution
   - Can view fields and edit assigned tasks
   - View-only access to reports

5. **VIEWER** (مشاهد)
   - View-only access to fields, tasks, and reports
   - No access to team or settings

### Permission Categories

- **Fields** (الحقول): Manage agricultural fields
- **Tasks** (المهام): Manage tasks and assignments
- **Reports** (التقارير): View and generate reports
- **Team** (الفريق): Manage team members
- **Settings** (الإعدادات): Configure system settings

## Usage

### Import the main component

```tsx
import { TeamManagement } from '@/features/team';

export default function TeamPage() {
  return <TeamManagement />;
}
```

### Use individual components

```tsx
import { MemberCard, InviteMemberDialog } from '@/features/team';

function MyComponent() {
  const [showInvite, setShowInvite] = useState(false);

  return (
    <>
      <MemberCard member={member} onEditRole={handleEdit} />
      <InviteMemberDialog isOpen={showInvite} onClose={() => setShowInvite(false)} />
    </>
  );
}
```

### Use hooks directly

```tsx
import { useTeamMembers, useInviteMember } from '@/features/team';

function TeamComponent() {
  const { data: members, isLoading } = useTeamMembers();
  const inviteMutation = useInviteMember();

  const handleInvite = async (data) => {
    await inviteMutation.mutateAsync(data);
  };

  return (/* ... */);
}
```

## API Integration

The feature connects to the User Service backend at `/api/v1/users`. The following endpoints are used:

- `GET /api/v1/users` - Get all users with filters
- `GET /api/v1/users/:id` - Get single user
- `POST /api/v1/users` - Create/invite new user
- `PUT /api/v1/users/:id` - Update user role/details
- `DELETE /api/v1/users/:id` - Remove user

## Mock Data

The API layer includes comprehensive mock data for development and testing when the backend is unavailable. Mock data includes 5 sample users with different roles and statuses.

## Styling

The feature uses:
- Tailwind CSS for styling
- Custom sahool color palette (sahool-green, sahool-brown)
- shadcn/ui components (Button, Badge, Modal, Input)
- Lucide React icons

## TypeScript Support

Full TypeScript support with:
- Strict type checking
- Comprehensive interfaces
- Type-safe API calls
- Exported types for reuse

## Accessibility

- ARIA labels and roles
- Keyboard navigation support
- Focus management in modals
- Screen reader friendly

## Future Enhancements

- [ ] Bulk operations (select multiple members)
- [ ] Export team list to CSV/Excel
- [ ] Activity logs for team changes
- [ ] Custom role creation
- [ ] Fine-grained permission editing
- [ ] Email templates for invitations
- [ ] Two-factor authentication management
