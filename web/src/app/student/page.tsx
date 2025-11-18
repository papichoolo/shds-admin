"use client";

import { useAuth } from "@/providers/auth-provider";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { apiFetch } from "@/lib/api";
import { toast } from "sonner";

const ADMINish = ["admin", "staff", "super_admin"];

const hasAnyRole = (roles?: string[], bucket?: string[]) => {
  if (!roles || !bucket) return false;
  return roles.some((role) => bucket.includes(role));
};

type StudentDoc = {
  id?: string;
  firstName?: string;
  lastName?: string;
  branchId?: string;
  status?: string;
  guardianLinks?: { guardianId: string; relationship?: string }[];
};

export default function StudentDashboard() {
  const { user, token, loading, logout } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<any | null>(null);
  const [student, setStudent] = useState<StudentDoc | null>(null);
  const [loadingStudent, setLoadingStudent] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (!token) return;
    async function load() {
      try {
        const me = await apiFetch<any>("/users/me", { method: "GET" }, token);
        setProfile(me);
        if (hasAnyRole(me?.roles, ADMINish)) {
          router.replace("/dashboard");
          return;
        }
        const studentId = me?.profile?.studentId;
        if (!studentId) {
          setStudent(null);
          setLoadingStudent(false);
          return;
        }
        setLoadingStudent(true);
        const result = await apiFetch<StudentDoc[]>(`/collections/students?id=${studentId}`, { method: "GET" }, token);
        setStudent(result?.[0] || null);
      } catch (err: any) {
        toast.error(err?.message || "Failed to load student info");
      } finally {
        setLoadingStudent(false);
      }
    }
    load();
  }, [token, router]);

  const displayName = useMemo(() => {
    const base = student?.firstName ? `${student.firstName} ${student?.lastName ?? ""}`.trim() : profile?.profile?.displayName;
    return base || user?.displayName || user?.email || "Student";
  }, [student, profile, user]);

  const branchDisplay = student?.branchId || profile?.branchId || profile?.profile?.branchId || "-";
  const guardianLinks = student?.guardianLinks || [];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-600 text-white pb-10">
      <div className="max-w-4xl mx-auto p-4 sm:p-6 space-y-4 sm:space-y-6">
        <header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          <div>
            <p className="text-sm uppercase tracking-wide text-white/80">Student Portal</p>
            <h1 className="text-2xl font-semibold">Hello, {displayName}</h1>
            <p className="text-sm text-white/80">Branch: {branchDisplay}</p>
          </div>
          <Button variant="secondary" onClick={() => logout()}>Logout</Button>
        </header>

        <div className="grid gap-4 sm:grid-cols-2">
          <Card className="bg-white/10 text-white border-white/20">
            <CardHeader>
              <CardTitle>Enrollment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="text-sm text-white/80">Status</div>
              <Badge variant="secondary">{student?.status || "pending"}</Badge>
              <div className="text-sm text-white/80 mt-4">Student ID</div>
              <div className="font-mono text-lg">{student?.id || "-"}</div>
            </CardContent>
          </Card>
          <Card className="bg-white text-gray-900">
            <CardHeader>
              <CardTitle>Guardians</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              {guardianLinks.length > 0 ? (
                guardianLinks.map((g) => (
                  <div key={g.guardianId} className="flex items-center justify-between border rounded px-3 py-2">
                    <div>
                      <div className="font-medium">{g.relationship || "Guardian"}</div>
                      <div className="text-xs text-muted-foreground">ID: {g.guardianId}</div>
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-muted-foreground">No guardians linked yet.</p>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="bg-white text-gray-900">
          <CardHeader>
            <CardTitle>What&apos;s next</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm text-muted-foreground">
            {loadingStudent ? (
              <p>Loading your schedule...</p>
            ) : (
              <>
                <p>Attendance tracking and fee alerts will appear here once your branch publishes them.</p>
                <p>Need help? Contact your branch admin and share your invite ID.</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
