/**
 * SAHOOL Tasks Page
 * صفحة المهام
 */

import { Metadata } from "next";
import TasksClient from "./TasksClient";

export const metadata: Metadata = {
  title: "Tasks Management | SAHOOL",
  description: "إدارة المهام - Manage farm tasks, schedules, and activities",
  keywords: ["tasks", "المهام", "farm activities", "scheduling", "sahool"],
  openGraph: {
    title: "Tasks Management | SAHOOL",
    description: "Farm tasks and activities management",
    type: "website",
  },
};

export default function TasksPage() {
  return <TasksClient />;
}
