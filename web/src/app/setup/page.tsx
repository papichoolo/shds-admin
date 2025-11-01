"use client";

import { useAuth } from "@/providers/auth-provider";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

// add simple checkbox component as shadcn's Checkbox is not added by default in v4
function SimpleCheckbox({ checked, onChange, id }: { checked: boolean; onChange: (v: boolean) => void; id: string }) {
  return (
    <input id={id} type="checkbox" className="size-4 border rounded" checked={checked} onChange={(e) => onChange(e.target.checked)} />
  );
}

export default function SetupPage() {
  const { user, token, loading } = useAuth();
  const router = useRouter();
  const [branchId, setBranchId] = useState("");
  const [roles, setRoles] = useState<{ admin: boolean; staff: boolean }>({ admin: false, staff: true });
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    if (!roles.admin && !roles.staff) {
      toast.error("Pick at least one role");
      return;
    }
    setBusy(true);
    try {
      await apiFetch("/users/setup", {
        method: "POST",
        body: JSON.stringify({ branchId, roles: [roles.admin && "admin", roles.staff && "staff"].filter(Boolean) }),
      }, token);
      toast.success("Setup complete");
      router.replace("/dashboard");
    } catch (e: any) {
      toast.error(e.message || "Setup failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>User Profile Setup</CardTitle>
          <CardDescription>Configure your roles and branch access</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="branch">Branch ID</Label>
              <Input id="branch" value={branchId} onChange={(e) => setBranchId(e.target.value)} required placeholder="1 or branch_001" />
            </div>
            <div className="space-y-2">
              <Label>Roles</Label>
              <div className="flex items-center gap-2">
                <SimpleCheckbox id="admin" checked={roles.admin} onChange={(v) => setRoles((r) => ({ ...r, admin: v }))} />
                <Label htmlFor="admin" className="font-normal">Admin - Full access</Label>
              </div>
              <div className="flex items-center gap-2">
                <SimpleCheckbox id="staff" checked={roles.staff} onChange={(v) => setRoles((r) => ({ ...r, staff: v }))} />
                <Label htmlFor="staff" className="font-normal">Staff - Branch access</Label>
              </div>
            </div>
            <Button type="submit" disabled={busy} className="w-full">{busy ? "Saving..." : "Complete Setup"}</Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
