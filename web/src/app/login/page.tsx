"use client";

import { useAuth } from "@/providers/auth-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { toast } from "sonner";
import Link from "next/link";
import { apiFetch } from "@/lib/api";

export default function LoginPage() {
  const { user, token, loading, loginWithEmail, loginWithGoogle } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    async function decide() {
      if (!loading && user && token) {
        try {
          const me = await apiFetch<{ uid: string; roles?: string[]; branchId?: string }>("/users/me", { method: "GET" }, token);
          router.replace(me?.branchId ? "/dashboard" : "/setup");
        } catch {
          router.replace("/setup");
        }
      }
    }
    decide();
  }, [user, token, loading, router]);

  async function onEmailLogin(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    try {
      await loginWithEmail(email, password);
      toast.success("Signed in");
    } catch (e: any) {
      toast.error(e.message ?? "Login failed");
    } finally {
      setBusy(false);
    }
  }

  async function onGoogleLogin() {
    setBusy(true);
    try {
      await loginWithGoogle();
      toast.success("Signed in with Google");
    } catch (e: any) {
      toast.error(e.message ?? "Google sign-in failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>SHDS Admin</CardTitle>
          <CardDescription>Sign in to continue</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onEmailLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required placeholder="you@example.com" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <Button disabled={busy} className="w-full" type="submit">{busy ? "Signing in..." : "Sign in"}</Button>
          </form>
          <div className="relative my-6 text-center text-sm text-muted-foreground">
            <span className="bg-background px-2 relative z-10">OR</span>
            <div className="absolute inset-0 flex items-center" aria-hidden="true">
              <div className="w-full border-t" />
            </div>
          </div>
          <Button disabled={busy} variant="outline" className="w-full" onClick={onGoogleLogin}>
            Continue with Google
          </Button>
          <div className="mt-4 text-center text-sm">
            <Link className="text-primary underline" href="/setup">New here? Complete setup</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
