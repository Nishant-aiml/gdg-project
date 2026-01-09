'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from './AuthProvider';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredRole?: 'institution' | 'department';
}

export default function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { user, loading, initialized } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (initialized && !loading) {
      if (!user) {
        // Not authenticated - redirect to login
        router.push('/login?redirect=' + encodeURIComponent(window.location.pathname));
        return;
      }

      if (requiredRole) {
        // Check role
        const roleHierarchy: Record<string, number> = {
          'department': 1,
          'institution': 2,
        };

        const userRoleLevel = roleHierarchy[user.role] || 0;
        const requiredRoleLevel = roleHierarchy[requiredRole] || 0;

        if (userRoleLevel < requiredRoleLevel) {
          // Insufficient permissions
          router.push('/unauthorized');
          return;
        }
      }
    }
  }, [user, loading, initialized, requiredRole, router]);

  // Show loading state
  if (loading || !initialized) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return null; // Will redirect
  }

  // Check role if required
  if (requiredRole) {
    const roleHierarchy: Record<string, number> = {
      'department': 1,
      'institution': 2,
    };

    const userRoleLevel = roleHierarchy[user.role] || 0;
    const requiredRoleLevel = roleHierarchy[requiredRole] || 0;

    if (userRoleLevel < requiredRoleLevel) {
      return null; // Will redirect
    }
  }

  return <>{children}</>;
}

