"use client";

import { useAuth } from "@/providers/auth-provider";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { apiFetch } from "@/lib/api";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";
import { useRouter } from "next/navigation";

const hasAnyRole = (roles: string[] | undefined, bucket: string[]) => roles?.some((role) => bucket.includes(role));

export default function InvitesPage() {
  const { token } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<any | null>(null);
  const [loadingProfile, setLoadingProfile] = useState(true);
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteBranch, setInviteBranch] = useState("");
  const [inviteTarget, setInviteTarget] = useState("staff");
  const [inviteRoles, setInviteRoles] = useState({ admin: false, staff: true, student: false, guardian: false });
  const [inviteStudentName, setInviteStudentName] = useState("");
  const [inviteBatchName, setInviteBatchName] = useState("");
  const [inviteMessage, setInviteMessage] = useState("");
  const [inviting, setInviting] = useState(false);
  const [lastInviteLink, setLastInviteLink] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    apiFetch<any>("/users/me", { method: "GET" }, token)
      .then((me) => {
        setProfile(me);
        setInviteBranch(me?.branchId || me?.profile?.branchId || "");
        if (!hasAnyRole(me?.roles, ["super_admin"])) {
          router.replace("/dashboard");
        }
      })
      .catch(() => router.replace("/dashboard"))
      .finally(() => setLoadingProfile(false));
  }, [token, router]);

  const isSuperAdmin = useMemo(() => hasAnyRole(profile?.roles, ["super_admin"]), [profile]);

  function roleSelections() {
    return [
      inviteRoles.admin && "admin",
      inviteRoles.staff && "staff",
      inviteRoles.student && "student",
      inviteRoles.guardian && "guardian",
    ].filter(Boolean) as string[];
  }

  async function submitInvite(e: React.FormEvent) {
    e.preventDefault();
    if (!token) return;
    if (!inviteEmail) {
      toast.error("Recipient email is required");
      return;
    }
    const roles = roleSelections();
    if (roles.length === 0) {
      toast.error("Select at least one role");
      return;
    }
    if (!inviteBranch) {
      toast.error("Branch id is required");
      return;
    }
    setInviting(true);
    try {
      const payload = {
        email: inviteEmail,
        branchId: inviteBranch,
        roles,
        targetType: inviteTarget,
        studentName: inviteStudentName || undefined,
        batchName: inviteBatchName || undefined,
        message: inviteMessage || undefined,
      };
      const response = await apiFetch<any>("/users/invites", { method: "POST", body: JSON.stringify(payload) }, token);
      const link = response?.inviteLink || (response?.token ? `/setup?token=${response.token}` : null);
      setLastInviteLink(link);
      toast.success("Invite sent");
      setInviteEmail("");
      setInviteMessage("");
      setInviteStudentName("");
      setInviteBatchName("");
    } catch (err: any) {
      toast.error(err?.message || "Failed to send invite");
    } finally {
      setInviting(false);
    }
  }

  async function copyInviteLink() {
    if (!lastInviteLink) return;
    try {
      await navigator.clipboard.writeText(lastInviteLink);
      toast.success("Invite link copied");
    } catch {
      toast.error("Unable to copy link");
    }
  }

  if (loadingProfile) return null;

  if (!isSuperAdmin) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Invites</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          You need super admin permissions to send invites.
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base sm:text-lg">Invite staff, students, or guardians</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={submitInvite} className="grid gap-3 sm:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="invite-email">Email</Label>
              <Input id="invite-email" type="email" value={inviteEmail} onChange={(e) => setInviteEmail(e.target.value)} placeholder="someone@example.com" required />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-branch">Branch ID</Label>
              <Input id="invite-branch" value={inviteBranch} onChange={(e) => setInviteBranch(e.target.value)} placeholder="branch_001" required />
            </div>
            <div className="space-y-2">
              <Label>Target type</Label>
              <Select value={inviteTarget} onValueChange={setInviteTarget}>
                <SelectTrigger>
                  <SelectValue placeholder="Select target" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="staff">Staff</SelectItem>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="student">Student</SelectItem>
                  <SelectItem value="guardian">Guardian</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Roles</Label>
              <div className="flex flex-wrap gap-3 text-sm">
                {(["admin", "staff", "student", "guardian"] as const).map((role) => (
                  <label key={role} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      className="size-4 border rounded"
                      checked={(inviteRoles as any)[role]}
                      onChange={(e) => setInviteRoles((prev) => ({ ...prev, [role]: e.target.checked }))}
                    />
                    {role.charAt(0).toUpperCase() + role.slice(1)}
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-student">Student name (optional)</Label>
              <Input id="invite-student" value={inviteStudentName} onChange={(e) => setInviteStudentName(e.target.value)} placeholder="Student for guardians or students" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="invite-batch">Batch name (optional)</Label>
              <Input id="invite-batch" value={inviteBatchName} onChange={(e) => setInviteBatchName(e.target.value)} placeholder="Batch Alpha" />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="invite-msg">Message</Label>
              <Textarea id="invite-msg" value={inviteMessage} onChange={(e) => setInviteMessage(e.target.value)} placeholder="Context for the invitee" rows={3} />
            </div>
            <div className="sm:col-span-2 flex flex-col gap-2">
              <Button type="submit" disabled={inviting}>{inviting ? "Sending..." : "Send invite"}</Button>
              {lastInviteLink && (
                <div className="text-xs text-muted-foreground flex items-center gap-2 flex-wrap">
                  <span>Last invite link:</span>
                  <code className="bg-muted px-2 py-1 rounded break-all">{lastInviteLink}</code>
                  <Button type="button" variant="secondary" size="sm" onClick={copyInviteLink}>Copy</Button>
                </div>
              )}
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
