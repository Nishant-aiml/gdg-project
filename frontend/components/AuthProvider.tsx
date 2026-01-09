'use client';

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User as FirebaseUser, onAuthStateChanged } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { initializeAuth, getCurrentUser, AuthUser, getDemoUser } from '@/lib/auth';

interface AuthContextType {
  user: AuthUser | null;
  loading: boolean;
  initialized: boolean;
  isDemoMode: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  initialized: false,
  isDemoMode: false,
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    let mounted = true;

    // Check for demo user first
    const demoUser = getDemoUser();
    if (demoUser) {
      if (mounted) {
        setUser(demoUser);
        setIsDemoMode(true);
        setLoading(false);
        setInitialized(true);
      }
      return;
    }

    // Initialize regular auth
    initializeAuth().then((authUser) => {
      if (mounted) {
        setUser(authUser);
        setIsDemoMode(false);
        setLoading(false);
        setInitialized(true);
      }
    });

    // Listen for auth state changes
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser: FirebaseUser | null) => {
      if (mounted) {
        // Check if demo user is set (demo mode takes precedence)
        const demoUser = getDemoUser();
        if (demoUser) {
          setUser(demoUser);
          setIsDemoMode(true);
        } else if (firebaseUser) {
          // User is signed in, get backend user info
          const currentUser = getCurrentUser();
          setUser(currentUser);
          setIsDemoMode(false);
        } else {
          // User is signed out
          setUser(null);
          setIsDemoMode(false);
        }
        setLoading(false);
        setInitialized(true);
      }
    });

    return () => {
      mounted = false;
      unsubscribe();
    };
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, initialized, isDemoMode }}>
      {children}
    </AuthContext.Provider>
  );
}

