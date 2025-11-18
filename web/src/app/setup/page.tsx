"use client";

import { useAuth } from "@/providers/auth-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

const ADMINish = ["admin", "staff", "super_admin"];
const STUDENTish = ["student", "guardian"];

export default function SetupPage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();
  const params = useSearchParams();
  const inviteFromUrl = params?.get("token") ?? "";
  const [inviteToken, setInviteToken] = useState(inviteFromUrl);
  const [displayName, setDisplayName] = useState("");
  const [branchId, setBranchId] = useState("");
  const [manualRole, setManualRole] = useState<"student" | "guardian">("student");
  const [manualMode, setManualMode] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    setInviteToken(inviteFromUrl);
  }, [inviteFromUrl]);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  const resolveHome = useMemo(() => {
    return (roles?: string[], branch?: string | null) => {
      if (!branch) return "/setup";
      if (roles?.some((role) => ADMINish.includes(role))) return "/dashboard";
      if (roles?.some((role) => STUDENTish.includes(role))) return "/student";
      return "/setup";
    };
  }, []);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    const trimmed = inviteToken.trim();
    const isManual = manualMode || trimmed === "" || trimmed === "-1";
    if (isManual && !branchId.trim()) {
      toast.error("Branch id is required");
      return;
    }
    if (!isManual && !trimmed) {
      toast.error("Enter the invite token from your email");
      return;
    }
    setBusy(true);
    try {
      const body = isManual
        ? {
            inviteToken: "-1",
            confirmedName: displayName || undefined,
            branchId: branchId.trim(),
            roles: [manualRole],
            targetType: manualRole,
          }
        : { inviteToken: trimmed, confirmedName: displayName || undefined };

      const result = await apiFetch<{ roles: string[]; branchId: string }>(
        "/users/setup",
        {
          method: "POST",
          body: JSON.stringify(body),
        },
        token,
      );
      toast.success("Setup complete");
      router.replace(resolveHome(result?.roles, result?.branchId));
    } catch (e: any) {
      toast.error(e.message || "Setup failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4 sm:p-6">
      <Card className="w-full max-w-md sm:max-w-xl shadow-xl">
        <CardHeader className="space-y-1 text-center sm:text-left">
          <CardTitle>User Invite Activation</CardTitle>
          <CardDescription>Use an invite token to auto-fill, or enter your details manually if you do not have one.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <form onSubmit={onSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="token">Invite token</Label>
              <Input id="token" value={inviteToken} onChange={(e) => { setInviteToken(e.target.value); if (e.target.value) setManualMode(false); }} placeholder="gm14mLr0wF8..." />
              <p className="text-xs text-muted-foreground">Paste the invite token from your email. Leave empty to enter details manually.</p>
            </div>
            <div className="flex items-start gap-2 text-sm">
              <input id="manual" type="checkbox" checked={manualMode} onChange={(e) => setManualMode(e.target.checked)} className="mt-1 h-4 w-4 border rounded" />
              <Label htmlFor="manual" className="text-sm leading-snug">I don&apos;t have an invite token</Label>
            </div>
            {manualMode && (
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="branchId">Branch ID</Label>
                  <Input id="branchId" value={branchId} onChange={(e) => setBranchId(e.target.value)} placeholder="branch_001" required />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Select value={manualRole} onValueChange={(val) => setManualRole(val as "student" | "guardian")}>
                    <SelectTrigger id="role">
                      <SelectValue placeholder="Choose role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="student">Student</SelectItem>
                      <SelectItem value="guardian">Guardian</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="displayName">Display name (optional)</Label>
              <Input id="displayName" value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="How should we address you?" />
            </div>
            <Button type="submit" disabled={busy || !token} className="w-full">{busy ? "Verifying..." : "Complete Setup"}</Button>
            <p className="text-xs text-muted-foreground text-center">Need help? Ask the SHDS admin team to resend your invite.</p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
