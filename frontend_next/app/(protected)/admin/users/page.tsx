"use client";

import { useEffect, useState } from "react";
import { useApp } from "@/components/layout/providers";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getAdminUsers, toggleUserActive, changeUserRole, deleteUser } from "@/lib/api";
import { User } from "@/lib/types";
import { toast } from "sonner";
import { UserCheck, UserX, Trash2, RefreshCw } from "lucide-react";

const ROLES = ["merchant", "influencer", "admin"];

export default function AdminUsersPage() {
  const { lang } = useApp();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);
  const [rolePickerId, setRolePickerId] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    try {
      const r = await getAdminUsers();
      setUsers(Array.isArray(r.data) ? r.data : (r.data?.data ?? r.data?.users ?? []));
    } catch {
      toast.error("Failed to load users");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleToggle(id: string, name: string) {
    setActing(id);
    try {
      const r = await toggleUserActive(id);
      toast.success(`${name} → ${r.data.is_active ? "Active" : "Inactive"}`);
      await load();
    } catch {
      toast.error("Failed");
    } finally {
      setActing(null);
    }
  }

  async function handleRole(id: string, newRole: string, currentRole: string) {
    if (newRole === currentRole) { setRolePickerId(null); return; }
    setRolePickerId(null);
    setActing(id);
    try {
      await changeUserRole(id, newRole);
      toast.success(`Role changed to ${newRole}`);
      await load();
    } catch {
      toast.error("Failed to change role");
    } finally {
      setActing(null);
    }
  }

  async function handleDelete(id: string, email: string) {
    if (!confirm(`Deactivate user: ${email}?`)) return;
    setActing(id);
    try {
      await deleteUser(id);
      toast.success(`User ${email} deactivated`);
      await load();
    } catch {
      toast.error("Failed to delete");
    } finally {
      setActing(null);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-white/40 text-sm">Loading...</div>
      </div>
    );
  }

  const active   = users.filter((u) => u.is_active).length;
  const inactive = users.length - active;

  return (
    <div className="space-y-4 max-w-6xl">
      <div className="admin-banner flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">
            👥 {lang === "ar" ? "إدارة المستخدمين" : "User Management"}
          </h1>
          <p className="text-white/50 text-sm mt-1">
            {lang === "ar"
              ? `${users.length} مستخدم — ${active} نشط · ${inactive} غير نشط`
              : `${users.length} users — ${active} active · ${inactive} inactive`}
          </p>
        </div>
        <Button size="sm" variant="outline" onClick={load} className="gap-2">
          <RefreshCw size={14} /> {lang === "ar" ? "تحديث" : "Refresh"}
        </Button>
      </div>

      <div className="space-y-2">
        {users.map((u) => (
          <div
            key={u.id}
            className={`aria-card flex items-center justify-between gap-4 transition-opacity ${
              !u.is_active ? "opacity-50" : ""
            }`}
          >
            <div className="flex-1 min-w-0">
              <div className="text-white text-sm font-medium">
                {u.full_name_en ?? u.full_name ?? u.full_name_ar ?? u.username}
                <span className="text-white/30 font-normal ml-2">@{u.username ?? u.email?.split("@")[0]}</span>
              </div>
              <div className="text-white/40 text-xs mt-0.5">
                {u.email} · ID #{u.id} · {u.created_at?.slice(0, 10)}
              </div>
            </div>

            <div className="flex items-center gap-2 flex-shrink-0">
              <Badge variant={u.role === "merchant" ? "amber" : u.role === "admin" ? "destructive" : "default"}>
                {u.role}
              </Badge>
              <Badge variant={u.is_active ? "success" : "secondary"}>
                {u.is_active ? "active" : "inactive"}
              </Badge>

              {/* Toggle active */}
              <Button
                size="icon"
                variant="ghost"
                className={`h-7 w-7 ${u.is_active ? "text-green-400/60 hover:text-green-400 hover:bg-green-400/10" : "text-white/30 hover:text-white/60 hover:bg-white/5"}`}
                disabled={acting === u.id}
                onClick={() => handleToggle(u.id, u.email)}
                title={u.is_active ? "Deactivate" : "Activate"}
              >
                {u.is_active ? <UserCheck size={13} /> : <UserX size={13} />}
              </Button>

              {/* Change role */}
              {rolePickerId === u.id ? (
                <select
                  autoFocus
                  defaultValue={u.role}
                  onBlur={() => setRolePickerId(null)}
                  onChange={(e) => handleRole(u.id, e.target.value, u.role)}
                  className="h-7 rounded-md border border-violet-500/40 bg-[#1a1a26] text-violet-300 text-xs px-1 focus:outline-none focus:border-violet-400"
                >
                  {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
                </select>
              ) : (
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 text-xs text-violet-400/70 hover:text-violet-400 hover:bg-violet-400/10"
                  disabled={acting === u.id || u.role === "admin"}
                  onClick={() => setRolePickerId(u.id)}
                >
                  {lang === "ar" ? "الدور" : "Role"}
                </Button>
              )}

              {/* Delete (soft) */}
              {u.role !== "admin" && (
                <Button
                  size="icon"
                  variant="ghost"
                  className="h-7 w-7 text-red-400/50 hover:text-red-400 hover:bg-red-400/10"
                  disabled={acting === u.id}
                  onClick={() => handleDelete(u.id, u.email)}
                  title="Deactivate user"
                >
                  <Trash2 size={13} />
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
