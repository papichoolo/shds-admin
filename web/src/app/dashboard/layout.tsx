"use client";

import { useAuth } from "@/providers/auth-provider";
import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Menu, Users, FileBarChart, Banknote, Send, Home, X } from "lucide-react";
import { apiFetch } from "@/lib/api";

const ADMINish = ["admin", "staff", "super_admin"];
const hasAnyRole = (roles: string[] | undefined, bucket: string[]) => roles?.some((r) => bucket.includes(r));

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, token, loading, logout } = useAuth();
  const router = useRouter();
  const [profile, setProfile] = useState<any | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!loading && !user) {
      router.replace("/login");
    }
  }, [loading, user, router]);

  useEffect(() => {
    if (!token) return;
    apiFetch<any>("/users/me", { method: "GET" }, token)
      .then((me) => {
        setProfile(me);
        if (!hasAnyRole(me?.roles, ADMINish)) {
          router.replace("/student");
        }
      })
      .catch(() => {})
      .finally(() => setProfileLoading(false));
  }, [token, router]);

  useEffect(() => {
    function handleClickAway(e: MouseEvent) {
      if (!menuOpen) return;
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickAway);
    return () => document.removeEventListener("mousedown", handleClickAway);
  }, [menuOpen]);

  const initials = useMemo(() => {
    const fallback = profile?.profile?.displayName || user?.displayName || user?.email || "?";
    return fallback.slice(0, 1).toUpperCase();
  }, [profile, user]);

  const displayName = useMemo(() => {
    return profile?.profile?.displayName || user?.displayName || user?.email || "User";
  }, [profile, user]);

  const roleLabel = useMemo(() => {
    if (profile?.roles?.length) return profile.roles.join(", ");
    return "Pending role";
  }, [profile]);

  const branchDisplay = profileLoading ? "Loading..." : (profile?.branchId || profile?.profile?.branchId || "-");
  const isSuperAdmin = hasAnyRole(profile?.roles, ["super_admin"]);

  const menuItems = [
    { label: "Home", icon: Home, action: () => router.push("/dashboard") },
    { label: "Students", icon: Users, action: () => router.push("/dashboard/students") },
    { label: "Attendance", icon: FileBarChart, action: () => router.push("/dashboard/attendance") },
    { label: "Fees", icon: Banknote, action: () => router.push("/dashboard/fees") },
    isSuperAdmin ? { label: "Invites", icon: Send, action: () => router.push("/dashboard/invites") } : null,
  ].filter(Boolean) as { label: string; icon: any; action: () => void }[];

  if (!user || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
        <div className="max-w-6xl mx-auto p-3 sm:p-4">
          <div className="flex items-center justify-between mb-2 sm:mb-0 gap-3">
            <div className="flex items-center gap-3">
              <div className="relative" ref={menuRef}>
                <Button variant="secondary" size="icon" className="h-10 w-10" onClick={() => setMenuOpen((prev) => !prev)}>
                  {menuOpen ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
                </Button>
                {menuOpen && (
                  <div className="absolute left-0 mt-3 w-72 max-w-[calc(100vw-2rem)] rounded-xl bg-white text-gray-900 shadow-xl border z-30">
                    <div className="flex items-center gap-3 p-4">
                      <Avatar className="h-10 w-10">
                        <AvatarFallback>{initials}</AvatarFallback>
                      </Avatar>
                      <div className="min-w-0">
                        <div className="font-semibold truncate">{displayName}</div>
                        <div className="text-xs text-muted-foreground truncate">{user?.email || "Signed in"}</div>
                        <div className="text-[11px] text-muted-foreground truncate">{roleLabel}</div>
                      </div>
                    </div>
                    <div className="divide-y">
                      {menuItems.map((item) => (
                        <button
                          key={item.label}
                          onClick={() => { setMenuOpen(false); item.action(); }}
                          className="w-full flex items-center gap-3 px-4 py-3 text-sm hover:bg-gray-50 transition-colors text-left"
                        >
                          <item.icon className="h-4 w-4 text-gray-500" />
                          <span>{item.label}</span>
                        </button>
                      ))}
                    </div>
                    <div className="p-3 grid grid-cols-2 gap-2">
                      <Button variant="outline" size="sm" onClick={() => { setMenuOpen(false); router.push("/setup"); }}>Profile</Button>
                      <Button variant="destructive" size="sm" onClick={() => { setMenuOpen(false); logout(); }}>Logout</Button>
                    </div>
                  </div>
                )}
              </div>
              <h1 className="text-lg sm:text-xl font-semibold">SHDS Admin Dashboard</h1>
            </div>
            <div className="flex items-center gap-3 sm:gap-4">
              <div className="text-right leading-tight hidden sm:block">
                <div className="text-sm font-semibold truncate">{displayName}</div>
                <div className="text-xs text-white/90 truncate">{user?.email}</div>
                <div className="text-[11px] text-white/80 truncate">{roleLabel}</div>
              </div>
              <Avatar className="h-8 w-8 sm:h-10 sm:w-10">
                <AvatarFallback>{initials}</AvatarFallback>
              </Avatar>
            </div>
          </div>
          <div className="text-xs opacity-90 truncate">
            Branch: {branchDisplay}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto p-3 sm:p-4 space-y-4">
        {children}
      </div>
    </div>
  );
}
