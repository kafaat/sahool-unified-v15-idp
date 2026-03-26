/**
 * AuthGuard Tests
 * اختبارات حارس المصادقة
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import React from 'react';
import { AuthGuard } from '../AuthGuard';

const mockPush = vi.fn();
const mockCheckAuth = vi.fn();

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: mockPush,
    replace: vi.fn(),
    back: vi.fn(),
  }),
  usePathname: () => '/dashboard',
}));

// Mock lucide-react
vi.mock('lucide-react', () => ({
  Loader2: (props: Record<string, unknown>) =>
    React.createElement('svg', { 'data-testid': 'loader', ...props }),
}));

// Default mock state
let mockAuthState = {
  user: null as null | {
    id: string;
    email: string;
    name: string;
    role: 'admin' | 'supervisor' | 'viewer';
  },
  isAuthenticated: false,
  isLoading: true,
  login: vi.fn(),
  logout: vi.fn(),
  checkAuth: mockCheckAuth,
};

vi.mock('@/stores/auth.store', () => ({
  useAuth: () => mockAuthState,
}));

describe('AuthGuard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthState = {
      user: null,
      isAuthenticated: false,
      isLoading: true,
      login: vi.fn(),
      logout: vi.fn(),
      checkAuth: mockCheckAuth,
    };
  });

  it('shows loading state while checking auth', () => {
    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    );

    expect(screen.getByText('جاري التحميل...')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('calls checkAuth on mount', () => {
    render(
      <AuthGuard>
        <div>Content</div>
      </AuthGuard>
    );

    expect(mockCheckAuth).toHaveBeenCalled();
  });

  it('renders children when authenticated', () => {
    mockAuthState = {
      ...mockAuthState,
      user: { id: '1', email: 'a@b.com', name: 'Admin', role: 'admin' },
      isAuthenticated: true,
      isLoading: false,
    };

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to login when not authenticated', async () => {
    mockAuthState = {
      ...mockAuthState,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    };

    render(
      <AuthGuard>
        <div>Protected Content</div>
      </AuthGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login?returnTo=%2Fdashboard');
    });

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('allows admin to access admin-required routes', () => {
    mockAuthState = {
      ...mockAuthState,
      user: { id: '1', email: 'a@b.com', name: 'Admin', role: 'admin' },
      isAuthenticated: true,
      isLoading: false,
    };

    render(
      <AuthGuard requiredRole="admin">
        <div>Admin Content</div>
      </AuthGuard>
    );

    expect(screen.getByText('Admin Content')).toBeInTheDocument();
  });

  it('redirects viewer from admin-required routes', async () => {
    mockAuthState = {
      ...mockAuthState,
      user: { id: '1', email: 'a@b.com', name: 'Viewer', role: 'viewer' },
      isAuthenticated: true,
      isLoading: false,
    };

    render(
      <AuthGuard requiredRole="admin">
        <div>Admin Only</div>
      </AuthGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });

    expect(screen.queryByText('Admin Only')).not.toBeInTheDocument();
  });

  it('allows supervisor to access viewer-required routes', () => {
    mockAuthState = {
      ...mockAuthState,
      user: { id: '1', email: 'a@b.com', name: 'Supervisor', role: 'supervisor' },
      isAuthenticated: true,
      isLoading: false,
    };

    render(
      <AuthGuard requiredRole="viewer">
        <div>Viewer Content</div>
      </AuthGuard>
    );

    expect(screen.getByText('Viewer Content')).toBeInTheDocument();
  });

  it('blocks supervisor from admin-only routes', async () => {
    mockAuthState = {
      ...mockAuthState,
      user: { id: '1', email: 'a@b.com', name: 'Supervisor', role: 'supervisor' },
      isAuthenticated: true,
      isLoading: false,
    };

    render(
      <AuthGuard requiredRole="admin">
        <div>Admin Only</div>
      </AuthGuard>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });
});
