"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { firebaseAuth, firebaseApp } from "@/lib/firebase";
import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  User,
} from "firebase/auth";

type AuthContextShape = {
  user: User | null;
  token: string | null;
  loading: boolean;
  loginWithEmail: (email: string, password: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextShape | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Ensure app initialized
    firebaseApp();
    const auth = firebaseAuth();
    const unsub = onAuthStateChanged(auth, async (u) => {
      setUser(u);
      if (u) {
        const t = await u.getIdToken();
        setToken(t);
      } else {
        setToken(null);
      }
      setLoading(false);
    });
    return () => unsub();
  }, []);

  const value = useMemo<AuthContextShape>(() => ({
    user,
    token,
    loading,
    async loginWithEmail(email: string, password: string) {
      const auth = firebaseAuth();
      await signInWithEmailAndPassword(auth, email, password);
    },
    async loginWithGoogle() {
      const auth = firebaseAuth();
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
    },
    async logout() {
      const auth = firebaseAuth();
      await signOut(auth);
    },
  }), [user, token, loading]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
