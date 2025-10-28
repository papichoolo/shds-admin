"use client";

import { useAuth } from "@/providers/auth-provider";
import { useCallback, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { apiFetch } from "@/lib/api";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

type Student = {
  id: string;
  name: string;
  guardianPhone: string;
  branchId: string;
  createdAt?: string;
};

export default function DashboardPage() {
  const { user, token, loading, logout } = useAuth();
  const router = useRouter();
  const [students, setStudents] = useState<Student[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [user, loading, router]);

  const fetchStudents = useCallback(async () => {
    if (!token) return;
    setLoadingStudents(true);
    try {
      const data = await apiFetch<Student[]>("/students", { method: "GET" }, token);
      setStudents(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingStudents(false);
    }
  }, [token]);

  useEffect(() => { fetchStudents(); }, [fetchStudents]);

  const initials = useMemo(() => (user?.displayName || user?.email || "?").slice(0,1).toUpperCase(), [user]);

  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
        <div className="max-w-6xl mx-auto p-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">SHDS Admin Dashboard</h1>
          <div className="flex items-center gap-3">
            <div className="hidden sm:block text-sm">
              <div className="font-medium">{user?.displayName || "User"}</div>
              <div className="opacity-80">{user?.email}</div>
            </div>
            <Avatar>
              <AvatarFallback>{initials}</AvatarFallback>
            </Avatar>
            <Button variant="destructive" onClick={() => logout()}>Logout</Button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-4">
        <Card>
          <CardHeader>
            <CardTitle>Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="students">
              <TabsList>
                <TabsTrigger value="students">Student Info</TabsTrigger>
                <TabsTrigger value="attendance">Attendance Info</TabsTrigger>
                <TabsTrigger value="fees">Fees Info</TabsTrigger>
              </TabsList>
              <TabsContent value="students">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-sm text-muted-foreground">Students in your branch</div>
                  <Button size="sm" variant="outline" onClick={fetchStudents} disabled={loadingStudents}>Refresh</Button>
                </div>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Guardian Phone</TableHead>
                        <TableHead>Student ID</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {students.map((s) => (
                        <TableRow key={s.id}>
                          <TableCell>{s.name}</TableCell>
                          <TableCell>{s.guardianPhone}</TableCell>
                          <TableCell className="text-muted-foreground">{s.id}</TableCell>
                        </TableRow>
                      ))}
                      {students.length === 0 && (
                        <TableRow>
                          <TableCell colSpan={3} className="text-center text-muted-foreground">No students yet</TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
              <TabsContent value="attendance">
                <p className="text-sm text-muted-foreground">Attendance module coming soon.</p>
              </TabsContent>
              <TabsContent value="fees">
                <p className="text-sm text-muted-foreground">Fees management coming soon.</p>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
