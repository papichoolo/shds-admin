"use client";

import { useAuth } from "@/providers/auth-provider";
import { useCallback, useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { apiFetch } from "@/lib/api";

type Student = {
  id: string;
  name?: string;
  guardianPhone?: string;
  branchId: string;
  createdAt?: string;
};

export default function StudentsPage() {
  const { token } = useAuth();
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchStudents = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const data = await apiFetch<Student[]>("/students", { method: "GET" }, token);
      setStudents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchStudents(); }, [fetchStudents]);

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="p-4 sm:p-6">
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg sm:text-xl">Students</CardTitle>
            <Button size="sm" variant="outline" onClick={fetchStudents} disabled={loading}>
              {loading ? "Refreshing..." : "Refresh"}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="p-4 sm:p-6">
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
                    <TableCell>{s.name || "Unnamed"}</TableCell>
                    <TableCell>{s.guardianPhone || ""}</TableCell>
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
          <div className="sm:hidden space-y-3">
            {students.map((s) => (
              <Card key={s.id}>
                <CardContent className="p-4">
                  <div className="space-y-2">
                    <div>
                      <div className="text-xs text-muted-foreground">Name</div>
                      <div className="font-medium">{s.name || "Unnamed"}</div>
                    </div>
                    <div>
                      <div className="text-xs text-muted-foreground">Guardian Phone</div>
                      <div>{s.guardianPhone || ""}</div>
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
        </CardContent>
      </Card>
    </div>
  );
}
