export interface User {
  id: string;
  email: string;
  name?: string | null;
  role: "user" | "admin";
  status: "active" | "suspended";
  createdAt: string;
}

export interface ApiUsage {
  userId: string;
  date: string;
  sentinelCalls: number;
  sentinelLimit: number;
  weatherCalls: number;
  weatherLimit: number;
}
