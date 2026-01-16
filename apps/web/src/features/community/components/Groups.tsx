/**
 * Groups Component
 * مكون المجموعات
 */

"use client";

import React, { useState } from "react";
import Image from "next/image";
import { Users, Search, Plus, Lock, Globe } from "lucide-react";
import { useGroups, useJoinGroup } from "../hooks/useGroups";
import type { GroupFilters, GroupCategory } from "../types";

export const Groups: React.FC = () => {
  const [filters, setFilters] = useState<GroupFilters>({
    sortBy: "popular",
  });

  const { data: groups, isLoading } = useGroups(filters);
  const joinMutation = useJoinGroup();

  const categories: Array<{
    value: GroupCategory | "all";
    label: string;
    labelAr: string;
  }> = [
    { value: "all", label: "All", labelAr: "الكل" },
    { value: "crops", label: "Crops", labelAr: "المحاصيل" },
    { value: "livestock", label: "Livestock", labelAr: "الثروة الحيوانية" },
    { value: "irrigation", label: "Irrigation", labelAr: "الري" },
    { value: "pests", label: "Pests", labelAr: "الآفات" },
    { value: "organic", label: "Organic", labelAr: "الزراعة العضوية" },
    { value: "technology", label: "Technology", labelAr: "التقنية" },
  ];

  const handleJoinGroup = (groupId: string) => {
    joinMutation.mutate(groupId);
  };

  return (
    <div className="min-h-screen bg-gray-50" dir="rtl">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">المجموعات</h1>
              <p className="text-sm text-gray-600 mt-1">Community Groups</p>
            </div>
            <button className="flex items-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-colors">
              <Plus className="w-5 h-5" />
              <span>إنشاء مجموعة</span>
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-200 mb-6">
          <div className="flex items-center gap-4 flex-wrap">
            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="ابحث عن مجموعة..."
                  value={filters.search || ""}
                  onChange={(e) =>
                    setFilters({ ...filters, search: e.target.value })
                  }
                  className="w-full pr-10 pl-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Category Filter */}
            <select
              value={filters.category || "all"}
              onChange={(e) =>
                setFilters({
                  ...filters,
                  category:
                    e.target.value === "all"
                      ? undefined
                      : (e.target.value as GroupCategory),
                })
              }
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            >
              {categories.map((cat) => (
                <option key={cat.value} value={cat.value}>
                  {cat.labelAr}
                </option>
              ))}
            </select>

            {/* Joined Filter */}
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={filters.joined || false}
                onChange={(e) =>
                  setFilters({ ...filters, joined: e.target.checked })
                }
                className="w-5 h-5 text-green-500 rounded focus:ring-green-500"
              />
              <span className="text-sm font-medium text-gray-700">
                المجموعات المنضمة
              </span>
            </label>
          </div>
        </div>

        {/* Groups Grid */}
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
          </div>
        ) : groups && groups.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {groups.map((group) => (
              <div
                key={group.id}
                className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Cover Image */}
                <div className="relative h-32 bg-gradient-to-br from-green-400 to-green-600">
                  {group.coverImage && (
                    <Image
                      src={group.coverImage}
                      alt={group.nameAr}
                      fill
                      sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                      className="object-cover"
                      loading="lazy"
                      placeholder="blur"
                      blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAb/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWEREiMxUf/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
                    />
                  )}
                  <div className="absolute top-3 right-3">
                    {group.privacy === "private" ? (
                      <div className="bg-white bg-opacity-90 px-2 py-1 rounded-full flex items-center gap-1">
                        <Lock className="w-4 h-4 text-gray-700" />
                        <span className="text-xs text-gray-700">خاصة</span>
                      </div>
                    ) : (
                      <div className="bg-white bg-opacity-90 px-2 py-1 rounded-full flex items-center gap-1">
                        <Globe className="w-4 h-4 text-gray-700" />
                        <span className="text-xs text-gray-700">عامة</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Content */}
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {group.nameAr}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                    {group.descriptionAr}
                  </p>

                  <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                    <div className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      <span>{group.memberCount.toLocaleString("ar-SA")}</span>
                    </div>
                    <span>•</span>
                    <span>{group.postCount.toLocaleString("ar-SA")} منشور</span>
                  </div>

                  {group.isJoined ? (
                    <div className="flex gap-2">
                      <button className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                        عرض المجموعة
                      </button>
                      {group.isModerator && (
                        <button className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                          إدارة
                        </button>
                      )}
                    </div>
                  ) : (
                    <button
                      onClick={() => handleJoinGroup(group.id)}
                      disabled={joinMutation.isPending}
                      className="w-full px-4 py-2 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 disabled:bg-gray-300 transition-colors"
                    >
                      انضمام
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200 text-center">
            <p className="text-gray-600">لا توجد مجموعات</p>
            <p className="text-sm text-gray-500 mt-1">No groups found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Groups;
