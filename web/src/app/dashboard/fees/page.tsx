"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function FeesPage() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>Fees</CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Fees reminders and payments will show up here later.
        </CardContent>
      </Card>
    </div>
  );
}
