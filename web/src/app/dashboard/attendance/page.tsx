"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AttendancePage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Attendance</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Attendance tracking will appear here soon.
        </CardContent>
      </Card>
    </div>
  );
}
