"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Badge } from "@/components/ui/badge";
import { getAdminUsers } from "@/lib/api";
import { User } from "@/lib/types";
import { toast } from "sonner";

export default function AdminUsersPage() {
  const { lang } = useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAdminUsers()
      .then((r) => setUsers(Array.isArray(r.data) ? r.data : (r.data?.data ?? r.data?.users ?? [])))
      .catch(() => toast.error("Failed to load users"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-w-5xl">
      <div className="admin-banner">
        <h1 className="text-2xl font-bold text-white">
          👥 {lang === "ar" ? "إدارة المستخدمين" : "User Management"}
        </h1>
        <p className="text-white/50 text-sm mt-1">
          {lang === "ar" ? `${users.length} مستخدم مسجل` : `${users.length} registered users`}
        </p>
      </div>

      <div className="space-y-2">
        {users.map((u) => (
          <div key={u.id} className="aria-card flex items-center justify-between">
            <div>
              <div className="text-white text-sm font-medium">
                {u.full_name_en ?? u.full_name_ar ?? u.username}
              </div>
              <div className="text-white/40 text-xs mt-0.5">
                {u.email} · @{u.username} · {u.created_at?.slice(0, 10)}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={u.role === "merchant" ? "amber" : u.role === "admin" ? "destructive" : "default"}>
                {u.role}
              </Badge>
              <Badge variant={u.is_active ? "success" : "secondary"}>
                {u.is_active ? "active" : "inactive"}
              </Badge>
            </div>
          </div>
        ))}
        {users.length === 0 && (
          <div className="text-white/30 text-sm text-center py-10">
            {lang === "ar" ? "لا مستخدمين" : "No users found"}
          </div>
        )}
      </div>
    </div>
  );
}
