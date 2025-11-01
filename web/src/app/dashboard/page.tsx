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
        <div className="max-w-6xl mx-auto p-3 sm:p-4">
          <div className="flex items-center justify-between mb-2 sm:mb-0">
            <h1 className="text-lg sm:text-xl font-semibold">SHDS Admin Dashboard</h1>
            <div className="flex items-center gap-2 sm:gap-3">
              <Avatar className="h-8 w-8 sm:h-10 sm:w-10">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
              <Button variant="destructive" size="sm" onClick={() => logout()}>Logout</Button>
            </div>
          </div>
          <div className="sm:hidden text-xs opacity-90 truncate">
            {user?.email}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-3 sm:p-4">
        <Card>
          <CardHeader className="p-4 sm:p-6">
            <CardTitle className="text-lg sm:text-xl">Overview</CardTitle>
          </CardHeader>
          <CardContent className="p-4 sm:p-6">
            <Tabs defaultValue="students">
              <TabsList className="w-full sm:w-auto grid grid-cols-3 sm:inline-flex">
                <TabsTrigger value="students" className="text-xs sm:text-sm">Student Info</TabsTrigger>
                <TabsTrigger value="attendance" className="text-xs sm:text-sm">Attendance</TabsTrigger>
                <TabsTrigger value="fees" className="text-xs sm:text-sm">Fees</TabsTrigger>
              </TabsList>
              <TabsContent value="students" className="mt-4">
                <div className="flex items-center justify-between mb-4">
                  <div className="text-xs sm:text-sm text-muted-foreground">Students in your branch</div>
                  <Button size="sm" variant="outline" onClick={fetchStudents} disabled={loadingStudents}>
                    <span className="hidden sm:inline">Refresh</span>
                    <span className="sm:hidden">↻</span>
                  </Button>
                </div>
                
                {/* Desktop Table View */}
                <div className="hidden sm:block rounded-md border">
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

                {/* Mobile Card View */}
                <div className="sm:hidden space-y-3">
                  {students.map((s) => (
                    <Card key={s.id}>
                      <CardContent className="p-4">
                        <div className="space-y-2">
                          <div>
                            <div className="text-xs text-muted-foreground">Name</div>
                            <div className="font-medium">{s.name}</div>
                          </div>
                          <div>
                            <div className="text-xs text-muted-foreground">Guardian Phone</div>
                            <div>{s.guardianPhone}</div>
                          </div>
                          <div>
                            <div className="text-xs text-muted-foreground">Student ID</div>
                            <div className="text-sm text-muted-foreground">{s.id}</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {students.length === 0 && (
                    <div className="text-center text-muted-foreground py-8 text-sm">No students yet</div>
                  )}
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
