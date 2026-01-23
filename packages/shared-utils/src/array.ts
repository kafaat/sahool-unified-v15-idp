/**
 * Array Utility Functions
 * دوال المصفوفات المساعدة
 */

/**
 * Remove duplicate values from an array
 * إزالة القيم المكررة من المصفوفة
 *
 * @param array - المصفوفة - Array to deduplicate
 * @param key - المفتاح - Optional key function for objects
 * @returns مصفوفة فريدة - Array with unique values
 *
 * @example
 * unique([1, 2, 2, 3]) // [1, 2, 3]
 * unique([{id: 1}, {id: 1}, {id: 2}], (item) => item.id) // [{id: 1}, {id: 2}]
 */
export function unique<T>(array: T[], key?: (item: T) => unknown): T[] {
  if (!key) {
    return [...new Set(array)];
  }

  const seen = new Set<unknown>();
  return array.filter((item) => {
    const k = key(item);
    if (seen.has(k)) {
      return false;
    }
    seen.add(k);
    return true;
  });
}

/**
 * Split an array into chunks of specified size
 * تقسيم المصفوفة إلى أجزاء بحجم محدد
 *
 * @param array - المصفوفة - Array to chunk
 * @param size - الحجم - Size of each chunk
 * @returns مصفوفة من الأجزاء - Array of chunks
 *
 * @example
 * chunk([1, 2, 3, 4, 5], 2) // [[1, 2], [3, 4], [5]]
 */
export function chunk<T>(array: T[], size: number): T[][] {
  if (size <= 0) {
    throw new Error("Chunk size must be greater than 0");
  }

  const result: T[][] = [];
  for (let i = 0; i < array.length; i += size) {
    result.push(array.slice(i, i + size));
  }
  return result;
}

/**
 * Shuffle an array using Fisher-Yates algorithm
 * خلط المصفوفة باستخدام خوارزمية فيشر-ييتس
 *
 * @param array - المصفوفة - Array to shuffle
 * @returns مصفوفة مخلوطة - New shuffled array
 *
 * @example
 * shuffle([1, 2, 3, 4, 5]) // [3, 1, 5, 2, 4] (random order)
 */
export function shuffle<T>(array: T[]): T[] {
  const result = [...array];
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

/**
 * Group array items by a key
 * تجميع عناصر المصفوفة حسب مفتاح
 *
 * @param array - المصفوفة - Array to group
 * @param key - المفتاح - Key function or property name
 * @returns خريطة المجموعات - Map of grouped items
 *
 * @example
 * groupBy([{type: 'a', v: 1}, {type: 'b', v: 2}, {type: 'a', v: 3}], 'type')
 * // { a: [{type: 'a', v: 1}, {type: 'a', v: 3}], b: [{type: 'b', v: 2}] }
 */
export function groupBy<T, K extends string | number>(
  array: T[],
  key: keyof T | ((item: T) => K),
): Record<K, T[]> {
  const getKey = typeof key === "function" ? key : (item: T) => item[key] as unknown as K;

  return array.reduce(
    (groups, item) => {
      const groupKey = getKey(item);
      if (!groups[groupKey]) {
        groups[groupKey] = [];
      }
      groups[groupKey].push(item);
      return groups;
    },
    {} as Record<K, T[]>,
  );
}

/**
 * Flatten a nested array to a specified depth
 * تسطيح المصفوفة المتداخلة إلى عمق محدد
 *
 * @param array - المصفوفة - Array to flatten
 * @param depth - العمق - Maximum depth to flatten (default: 1)
 * @returns مصفوفة مسطحة - Flattened array
 *
 * @example
 * flatten([[1, 2], [3, [4, 5]]]) // [1, 2, 3, [4, 5]]
 * flatten([[1, 2], [3, [4, 5]]], 2) // [1, 2, 3, 4, 5]
 */
export function flatten<T>(array: unknown[], depth: number = 1): T[] {
  if (depth <= 0) {
    return array.slice() as T[];
  }

  return array.reduce<T[]>((acc, val) => {
    if (Array.isArray(val)) {
      acc.push(...flatten<T>(val, depth - 1));
    } else {
      acc.push(val as T);
    }
    return acc;
  }, []);
}

/**
 * Find the first item matching a predicate, or undefined
 * البحث عن أول عنصر يطابق الشرط
 *
 * @param array - المصفوفة - Array to search
 * @param predicate - الشرط - Predicate function
 * @returns العنصر أو undefined - Found item or undefined
 */
export function findFirst<T>(
  array: T[],
  predicate: (item: T, index: number) => boolean,
): T | undefined {
  for (let i = 0; i < array.length; i++) {
    if (predicate(array[i], i)) {
      return array[i];
    }
  }
  return undefined;
}

/**
 * Find the last item matching a predicate, or undefined
 * البحث عن آخر عنصر يطابق الشرط
 *
 * @param array - المصفوفة - Array to search
 * @param predicate - الشرط - Predicate function
 * @returns العنصر أو undefined - Found item or undefined
 */
export function findLast<T>(
  array: T[],
  predicate: (item: T, index: number) => boolean,
): T | undefined {
  for (let i = array.length - 1; i >= 0; i--) {
    if (predicate(array[i], i)) {
      return array[i];
    }
  }
  return undefined;
}

/**
 * Partition an array into two groups based on a predicate
 * تقسيم المصفوفة إلى مجموعتين بناءً على شرط
 *
 * @param array - المصفوفة - Array to partition
 * @param predicate - الشرط - Predicate function
 * @returns [matching, nonMatching] - Two arrays
 *
 * @example
 * partition([1, 2, 3, 4, 5], n => n > 3) // [[4, 5], [1, 2, 3]]
 */
export function partition<T>(
  array: T[],
  predicate: (item: T, index: number) => boolean,
): [T[], T[]] {
  const matching: T[] = [];
  const nonMatching: T[] = [];

  array.forEach((item, index) => {
    if (predicate(item, index)) {
      matching.push(item);
    } else {
      nonMatching.push(item);
    }
  });

  return [matching, nonMatching];
}

/**
 * Get the intersection of two arrays
 * الحصول على تقاطع مصفوفتين
 *
 * @param a - المصفوفة الأولى - First array
 * @param b - المصفوفة الثانية - Second array
 * @returns العناصر المشتركة - Common elements
 */
export function intersection<T>(a: T[], b: T[]): T[] {
  const setB = new Set(b);
  return [...new Set(a)].filter((item) => setB.has(item));
}

/**
 * Get the difference of two arrays (items in a but not in b)
 * الحصول على الفرق بين مصفوفتين
 *
 * @param a - المصفوفة الأولى - First array
 * @param b - المصفوفة الثانية - Second array
 * @returns العناصر في a فقط - Items only in a
 */
export function difference<T>(a: T[], b: T[]): T[] {
  const setB = new Set(b);
  return a.filter((item) => !setB.has(item));
}

/**
 * Calculate sum of array numbers
 * حساب مجموع الأرقام في المصفوفة
 *
 * @param array - المصفوفة - Array of numbers
 * @returns المجموع - Sum of all numbers
 */
export function sum(array: number[]): number {
  return array.reduce((acc, val) => acc + val, 0);
}

/**
 * Calculate average of array numbers
 * حساب متوسط الأرقام في المصفوفة
 *
 * @param array - المصفوفة - Array of numbers
 * @returns المتوسط - Average of all numbers
 */
export function average(array: number[]): number {
  if (array.length === 0) {
    return 0;
  }
  return sum(array) / array.length;
}

/**
 * Get min and max values from an array
 * الحصول على أصغر وأكبر قيمة من المصفوفة
 *
 * @param array - المصفوفة - Array of numbers
 * @returns [min, max] - Minimum and maximum values
 */
export function minMax(array: number[]): [number, number] | null {
  if (array.length === 0) {
    return null;
  }

  let min = array[0];
  let max = array[0];

  for (let i = 1; i < array.length; i++) {
    if (array[i] < min) min = array[i];
    if (array[i] > max) max = array[i];
  }

  return [min, max];
}

/**
 * Sort array by a key with multiple sort options
 * فرز المصفوفة حسب مفتاح مع خيارات متعددة
 *
 * @param array - المصفوفة - Array to sort
 * @param key - المفتاح - Key function or property name
 * @param order - الترتيب - Sort order ('asc' | 'desc')
 * @returns مصفوفة مفروزة - Sorted array (new array)
 */
export function sortBy<T>(
  array: T[],
  key: keyof T | ((item: T) => unknown),
  order: "asc" | "desc" = "asc",
): T[] {
  const getKey = typeof key === "function" ? key : (item: T) => item[key];
  const multiplier = order === "asc" ? 1 : -1;

  return [...array].sort((a, b) => {
    const aVal = getKey(a);
    const bVal = getKey(b);

    if (aVal === bVal) return 0;
    if (aVal === null || aVal === undefined) return 1 * multiplier;
    if (bVal === null || bVal === undefined) return -1 * multiplier;

    if (typeof aVal === "string" && typeof bVal === "string") {
      return aVal.localeCompare(bVal) * multiplier;
    }

    return (aVal < bVal ? -1 : 1) * multiplier;
  });
}

/**
 * Take first n items from an array
 * أخذ أول n عناصر من المصفوفة
 *
 * @param array - المصفوفة - Source array
 * @param n - العدد - Number of items to take
 * @returns العناصر - First n items
 */
export function take<T>(array: T[], n: number): T[] {
  return array.slice(0, Math.max(0, n));
}

/**
 * Skip first n items from an array
 * تخطي أول n عناصر من المصفوفة
 *
 * @param array - المصفوفة - Source array
 * @param n - العدد - Number of items to skip
 * @returns العناصر - Remaining items
 */
export function skip<T>(array: T[], n: number): T[] {
  return array.slice(Math.max(0, n));
}

/**
 * Create a range of numbers
 * إنشاء نطاق من الأرقام
 *
 * @param start - البداية - Start value
 * @param end - النهاية - End value (exclusive)
 * @param step - الخطوة - Step value (default: 1)
 * @returns النطاق - Array of numbers
 *
 * @example
 * range(0, 5) // [0, 1, 2, 3, 4]
 * range(0, 10, 2) // [0, 2, 4, 6, 8]
 */
export function range(start: number, end: number, step: number = 1): number[] {
  if (step === 0) {
    throw new Error("Step cannot be 0");
  }

  const result: number[] = [];

  if (step > 0) {
    for (let i = start; i < end; i += step) {
      result.push(i);
    }
  } else {
    for (let i = start; i > end; i += step) {
      result.push(i);
    }
  }

  return result;
}
