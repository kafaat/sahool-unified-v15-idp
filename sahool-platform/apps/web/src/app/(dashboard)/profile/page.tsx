"use client";

import { useState } from "react";
import { useAuthStore } from "@/stores/auth.store";
import { api } from "@/lib/api";

export default function ProfilePage() {
  const { user, updateUser } = useAuthStore();
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [profileMsg, setProfileMsg] = useState("");

  const [currentPwd, setCurrentPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [pwdMsg, setPwdMsg] = useState("");

  async function handleProfile(e: React.FormEvent) {
    e.preventDefault();
    setProfileMsg("");
    try {
      const res = await api.patch("/api/v1/users/me", { name, email });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Update failed");
      }
      const updated = await res.json();
      updateUser({ name: updated.name, email: updated.email });
      setProfileMsg("Profile updated successfully");
    } catch (err: unknown) {
      setProfileMsg(err instanceof Error ? err.message : "Error");
    }
  }

  async function handlePassword(e: React.FormEvent) {
    e.preventDefault();
    setPwdMsg("");
    try {
      const res = await api.post("/api/v1/users/me/change-password", {
        current_password: currentPwd,
        new_password: newPwd,
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Password change failed");
      }
      setCurrentPwd("");
      setNewPwd("");
      setPwdMsg("Password changed successfully");
    } catch (err: unknown) {
      setPwdMsg(err instanceof Error ? err.message : "Error");
    }
  }

  return (
    <div className="max-w-lg">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Profile Settings</h1>

      {/* Profile */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Personal Information</h2>
        {profileMsg && (
          <div className={`mb-4 p-2 rounded text-sm ${profileMsg.includes("success") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {profileMsg}
          </div>
        )}
        <form onSubmit={handleProfile} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 text-sm font-medium"
          >
            Save changes
          </button>
        </form>
      </section>

      {/* Change password */}
      <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h2 className="text-lg font-semibold text-gray-700 mb-4">Change Password</h2>
        {pwdMsg && (
          <div className={`mb-4 p-2 rounded text-sm ${pwdMsg.includes("success") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
            {pwdMsg}
          </div>
        )}
        <form onSubmit={handlePassword} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">Current Password</label>
            <input
              type="password"
              value={currentPwd}
              onChange={(e) => setCurrentPwd(e.target.value)}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-600 mb-1">New Password</label>
            <input
              type="password"
              value={newPwd}
              onChange={(e) => setNewPwd(e.target.value)}
              required
              minLength={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:outline-none"
            />
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 text-sm font-medium"
          >
            Update password
          </button>
        </form>
      </section>
    </div>
  );
}
