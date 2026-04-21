import Cookies from "js-cookie";
import { User } from "./types";

const TOKEN_KEY = "waslai_token";
const USER_KEY = "waslai_user";

export function setToken(token: string) {
  Cookies.set(TOKEN_KEY, token, { expires: 7, sameSite: "lax" });
}

export function getToken(): string | undefined {
  return Cookies.get(TOKEN_KEY);
}

export function removeToken() {
  Cookies.remove(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

export function setUser(user: User) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getUser(): User | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}

export function isLoggedIn(): boolean {
  return !!getToken();
}

export function logout() {
  removeToken();
  window.location.href = "/login";
}

export function getDashboardPath(role: string): string {
  if (role === "merchant") return "/merchant/dashboard";
  if (role === "influencer") return "/influencer/dashboard";
  if (role === "admin") return "/admin";
  return "/";
}
