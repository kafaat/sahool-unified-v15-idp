import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { PermissionGate, RoleGate, AdminGate } from './PermissionGate';

// Mock the useAuth hook
const mockUseAuth = vi.fn();
vi.mock('@sahool/shared-hooks', () => ({
  useAuth: () => mockUseAuth(),
}));

describe('PermissionGate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('when user has required permission', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: '1',
          permissions: ['field:view', 'field:create'],
          roles: ['farmer'],
        },
        isAuthenticated: true,
        isLoading: false,
      });
    });

    it('should render children', () => {
      render(
        <PermissionGate permission="field:view">
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
      expect(screen.getByText('المحتوى المحمي')).toBeInTheDocument();
    });

    it('should not render fallback', () => {
      render(
        <PermissionGate
          permission="field:view"
          fallback={<div data-testid="fallback">غير مصرح</div>}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.queryByTestId('fallback')).not.toBeInTheDocument();
    });
  });

  describe('when user lacks required permission', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: '1',
          permissions: ['field:view'],
          roles: ['farmer'],
        },
        isAuthenticated: true,
        isLoading: false,
      });
    });

    it('should not render children', () => {
      render(
        <PermissionGate permission="admin:users">
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });

    it('should render fallback when provided', () => {
      render(
        <PermissionGate
          permission="admin:users"
          fallback={<div data-testid="fallback">غير مصرح</div>}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.getByTestId('fallback')).toBeInTheDocument();
      expect(screen.getByText('غير مصرح')).toBeInTheDocument();
    });
  });

  describe('when user is not authenticated', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    });

    it('should not render children', () => {
      render(
        <PermissionGate permission="field:view">
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('when loading', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: true,
      });
    });

    it('should render loading state when provided', () => {
      render(
        <PermissionGate
          permission="field:view"
          loading={<div data-testid="loading">جاري التحميل...</div>}
        >
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.getByTestId('loading')).toBeInTheDocument();
      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('with multiple permissions (requireAll=false)', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: '1',
          permissions: ['field:view'],
          roles: ['farmer'],
        },
        isAuthenticated: true,
        isLoading: false,
      });
    });

    it('should render when user has any of the permissions', () => {
      render(
        <PermissionGate permission={['field:view', 'field:edit']}>
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });
  });

  describe('with multiple permissions (requireAll=true)', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: '1',
          permissions: ['field:view'],
          roles: ['farmer'],
        },
        isAuthenticated: true,
        isLoading: false,
      });
    });

    it('should not render when user lacks any permission', () => {
      render(
        <PermissionGate permission={['field:view', 'field:edit']} requireAll>
          <div data-testid="protected-content">المحتوى المحمي</div>
        </PermissionGate>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });
});

describe('RoleGate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render children when user has required role', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: '1',
        permissions: [],
        roles: ['agronomist'],
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <RoleGate role="agronomist">
        <div data-testid="role-content">محتوى المهندس الزراعي</div>
      </RoleGate>
    );

    expect(screen.getByTestId('role-content')).toBeInTheDocument();
  });

  it('should not render when user lacks role', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: '1',
        permissions: [],
        roles: ['farmer'],
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <RoleGate role="admin">
        <div data-testid="role-content">محتوى المدير</div>
      </RoleGate>
    );

    expect(screen.queryByTestId('role-content')).not.toBeInTheDocument();
  });
});

describe('AdminGate', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render for admin user', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: '1',
        permissions: ['admin:users'],
        roles: ['admin'],
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <AdminGate>
        <div data-testid="admin-content">لوحة التحكم</div>
      </AdminGate>
    );

    expect(screen.getByTestId('admin-content')).toBeInTheDocument();
  });

  it('should render for super_admin user', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: '1',
        permissions: ['admin:system'],
        roles: ['super_admin'],
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <AdminGate>
        <div data-testid="admin-content">لوحة التحكم</div>
      </AdminGate>
    );

    expect(screen.getByTestId('admin-content')).toBeInTheDocument();
  });

  it('should not render for non-admin user', () => {
    mockUseAuth.mockReturnValue({
      user: {
        id: '1',
        permissions: ['field:view'],
        roles: ['farmer'],
      },
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <AdminGate>
        <div data-testid="admin-content">لوحة التحكم</div>
      </AdminGate>
    );

    expect(screen.queryByTestId('admin-content')).not.toBeInTheDocument();
  });
});
