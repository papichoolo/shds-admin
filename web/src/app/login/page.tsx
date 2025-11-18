"use client";

import { useAuth } from "@/providers/auth-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import Link from "next/link";
import { apiFetch } from "@/lib/api";

const ADMINish = ["admin", "staff", "super_admin"];
const STUDENTish = ["student", "guardian"];

export default function LoginPage() {
  const { user, token, loading, loginWithEmail, loginWithGoogle } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const resolveHome = useMemo(() => {
    return (roles?: string[] | null, branchId?: string | null) => {
      if (!branchId) return "/setup";
      if (roles?.some((role) => ADMINish.includes(role))) return "/dashboard";
      if (roles?.some((role) => STUDENTish.includes(role))) return "/student";
      return "/setup";
    };
  }, []);

  useEffect(() => {
    async function decide() {
      if (!loading && user && token) {
        try {
          const me = await apiFetch<{ uid: string; roles?: string[]; branchId?: string }>("/users/me", { method: "GET" }, token);
          router.replace(resolveHome(me?.roles, me?.branchId));
        } catch {
          router.replace("/setup");
        }
      }
    }
    decide();
  }, [user, token, loading, router, resolveHome]);

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
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4 sm:p-6">
      <Card className="w-full max-w-md sm:max-w-lg shadow-xl">
        <CardHeader className="space-y-1 text-center sm:text-left">
          <CardTitle>SHDS Admin</CardTitle>
          <CardDescription>Sign in to continue</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
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
            <Link className="text-primary underline" href="/setup">Have an invite token? Complete setup</Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
