/**
 * Mock Data Utilities
 * أدوات البيانات الوهمية
 */

/**
 * Generate a random UUID
 */
export function generateId(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Get a random item from an array
 */
export function randomItem<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

/**
 * Get random items from an array
 */
export function randomItems<T>(items: T[], count: number): T[] {
  const shuffled = [...items].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

/**
 * Generate a random number between min and max
 */
export function randomNumber(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

/**
 * Generate a random float between min and max with precision
 */
export function randomFloat(min: number, max: number, precision = 2): number {
  const value = Math.random() * (max - min) + min;
  return parseFloat(value.toFixed(precision));
}

/**
 * Generate a random date between two dates
 */
export function randomDate(start: Date, end: Date): Date {
  return new Date(
    start.getTime() + Math.random() * (end.getTime() - start.getTime()),
  );
}

/**
 * Generate a random past date within days
 */
export function randomPastDate(days: number): Date {
  const now = new Date();
  const past = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
  return randomDate(past, now);
}

/**
 * Arabic names for mock data
 */
export const arabicNames = {
  firstNames: [
    "أحمد",
    "محمد",
    "علي",
    "عمر",
    "خالد",
    "يوسف",
    "إبراهيم",
    "سالم",
    "عبدالله",
    "حسن",
    "فاطمة",
    "مريم",
    "نورة",
    "سارة",
    "آمنة",
  ],
  lastNames: [
    "الأحمدي",
    "المحمدي",
    "السالمي",
    "الحسني",
    "العلوي",
    "الخليلي",
    "الزهراني",
    "القحطاني",
    "المطيري",
    "الشمري",
  ],
  crops: [
    "قمح",
    "شعير",
    "ذرة",
    "قطن",
    "بن",
    "عنب",
    "تمر",
    "موز",
    "مانجو",
    "ليمون",
  ],
  regions: ["صنعاء", "عدن", "تعز", "الحديدة", "إب", "ذمار", "حضرموت", "المكلا"],
};

/**
 * Check if mock data should be enabled
 */
export function isMockEnabled(): boolean {
  if (typeof window === "undefined") {
    return process.env.ENABLE_MOCK_DATA === "true";
  }
  return (
    process.env.NODE_ENV === "development" ||
    localStorage.getItem("enableMockData") === "true"
  );
}
