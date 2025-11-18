"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardHome() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Welcome</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>Select a section from the menu to manage students, attendance, fees, or invites.</p>
          <p>This home page is intentionally empty for now.</p>
        </CardContent>
      </Card>
    </div>
  );
}
