/**
 * Object Utility Functions
 * دوال الكائنات المساعدة
 */

/**
 * Deep clone an object using structured cloning
 * نسخ عميق للكائن باستخدام النسخ المهيكل
 *
 * @param obj - الكائن - Object to clone
 * @returns نسخة جديدة - New cloned object
 *
 * @example
 * const original = { a: 1, nested: { b: 2 } };
 * const cloned = deepClone(original);
 */
export function deepClone<T>(obj: T): T {
  // Handle null, undefined, primitives
  if (obj === null || obj === undefined) {
    return obj;
  }

  if (typeof obj !== "object") {
    return obj;
  }

  // Handle Date
  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }

  // Handle Array
  if (Array.isArray(obj)) {
    return obj.map((item) => deepClone(item)) as T;
  }

  // Handle Map
  if (obj instanceof Map) {
    const clonedMap = new Map();
    obj.forEach((value, key) => {
      clonedMap.set(deepClone(key), deepClone(value));
    });
    return clonedMap as T;
  }

  // Handle Set
  if (obj instanceof Set) {
    const clonedSet = new Set();
    obj.forEach((value) => {
      clonedSet.add(deepClone(value));
    });
    return clonedSet as T;
  }

  // Handle plain object
  const clonedObj: Record<string, unknown> = {};
  for (const key of Object.keys(obj)) {
    clonedObj[key] = deepClone((obj as Record<string, unknown>)[key]);
  }
  return clonedObj as T;
}

/**
 * Deep merge multiple objects
 * دمج عميق لعدة كائنات
 *
 * @param target - الهدف - Target object
 * @param sources - المصادر - Source objects to merge
 * @returns الكائن المدمج - Merged object
 *
 * @example
 * deepMerge({ a: 1, b: { c: 2 } }, { b: { d: 3 } })
 * // { a: 1, b: { c: 2, d: 3 } }
 */
export function deepMerge<T extends Record<string, unknown>>(
  target: T,
  ...sources: Array<Partial<T>>
): T {
  if (!sources.length) {
    return target;
  }

  const isPlainObject = (item: unknown): item is Record<string, unknown> => {
    return (
      typeof item === "object" &&
      item !== null &&
      !Array.isArray(item) &&
      !(item instanceof Date) &&
      !(item instanceof Map) &&
      !(item instanceof Set)
    );
  };

  const result = deepClone(target);

  for (const source of sources) {
    if (!source) continue;

    for (const key of Object.keys(source)) {
      const sourceValue = source[key as keyof T];
      const targetValue = result[key as keyof T];

      if (isPlainObject(sourceValue) && isPlainObject(targetValue)) {
        (result as Record<string, unknown>)[key] = deepMerge(
          targetValue as Record<string, unknown>,
          sourceValue as Record<string, unknown>,
        );
      } else if (sourceValue !== undefined) {
        (result as Record<string, unknown>)[key] = deepClone(sourceValue);
      }
    }
  }

  return result;
}

/**
 * Pick specific keys from an object
 * اختيار مفاتيح محددة من الكائن
 *
 * @param obj - الكائن - Source object
 * @param keys - المفاتيح - Keys to pick
 * @returns كائن جديد - New object with only selected keys
 *
 * @example
 * pick({ a: 1, b: 2, c: 3 }, ['a', 'c']) // { a: 1, c: 3 }
 */
export function pick<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  keys: K[],
): Pick<T, K> {
  const result = {} as Pick<T, K>;
  for (const key of keys) {
    if (key in obj) {
      result[key] = obj[key];
    }
  }
  return result;
}

/**
 * Omit specific keys from an object
 * استبعاد مفاتيح محددة من الكائن
 *
 * @param obj - الكائن - Source object
 * @param keys - المفاتيح - Keys to omit
 * @returns كائن جديد - New object without specified keys
 *
 * @example
 * omit({ a: 1, b: 2, c: 3 }, ['b']) // { a: 1, c: 3 }
 */
export function omit<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  keys: K[],
): Omit<T, K> {
  const keysSet = new Set(keys as string[]);
  const result = {} as Omit<T, K>;

  for (const key of Object.keys(obj)) {
    if (!keysSet.has(key)) {
      (result as Record<string, unknown>)[key] = obj[key];
    }
  }

  return result;
}

/**
 * Flatten a nested object into a single-level object with dot notation keys
 * تسطيح كائن متداخل إلى كائن من مستوى واحد بمفاتيح نقطية
 *
 * @param obj - الكائن - Object to flatten
 * @param prefix - البادئة - Prefix for keys (used internally)
 * @param delimiter - الفاصل - Key delimiter (default: '.')
 * @returns كائن مسطح - Flattened object
 *
 * @example
 * flattenObject({ a: { b: { c: 1 } }, d: 2 })
 * // { 'a.b.c': 1, 'd': 2 }
 */
export function flattenObject(
  obj: Record<string, unknown>,
  prefix: string = "",
  delimiter: string = ".",
): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  for (const key of Object.keys(obj)) {
    const value = obj[key];
    const newKey = prefix ? `${prefix}${delimiter}${key}` : key;

    if (
      typeof value === "object" &&
      value !== null &&
      !Array.isArray(value) &&
      !(value instanceof Date)
    ) {
      Object.assign(result, flattenObject(value as Record<string, unknown>, newKey, delimiter));
    } else {
      result[newKey] = value;
    }
  }

  return result;
}

/**
 * Unflatten a dot-notation object back to nested structure
 * إعادة كائن نقطي إلى هيكل متداخل
 *
 * @param obj - الكائن - Flattened object
 * @param delimiter - الفاصل - Key delimiter (default: '.')
 * @returns كائن متداخل - Nested object
 *
 * @example
 * unflattenObject({ 'a.b.c': 1, 'd': 2 })
 * // { a: { b: { c: 1 } }, d: 2 }
 */
export function unflattenObject(
  obj: Record<string, unknown>,
  delimiter: string = ".",
): Record<string, unknown> {
  const result: Record<string, unknown> = {};

  for (const flatKey of Object.keys(obj)) {
    const keys = flatKey.split(delimiter);
    let current = result;

    for (let i = 0; i < keys.length; i++) {
      const key = keys[i];
      const isLast = i === keys.length - 1;

      if (isLast) {
        current[key] = obj[flatKey];
      } else {
        if (!(key in current) || typeof current[key] !== "object") {
          current[key] = {};
        }
        current = current[key] as Record<string, unknown>;
      }
    }
  }

  return result;
}

/**
 * Check if an object is empty
 * التحقق مما إذا كان الكائن فارغاً
 *
 * @param obj - الكائن - Object to check
 * @returns هل الكائن فارغ - True if empty
 */
export function isEmptyObject(obj: Record<string, unknown>): boolean {
  return Object.keys(obj).length === 0;
}

/**
 * Get a nested value from an object using a path
 * الحصول على قيمة متداخلة من الكائن باستخدام مسار
 *
 * @param obj - الكائن - Source object
 * @param path - المسار - Dot-notation path or array of keys
 * @param defaultValue - القيمة الافتراضية - Default value if not found
 * @returns القيمة - Value at path or default
 *
 * @example
 * get({ a: { b: { c: 1 } } }, 'a.b.c') // 1
 * get({ a: { b: 1 } }, 'a.x.y', 'default') // 'default'
 */
export function get<T = unknown>(
  obj: unknown,
  path: string | string[],
  defaultValue?: T,
): T | undefined {
  const keys = Array.isArray(path) ? path : path.split(".");
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || current === undefined) {
      return defaultValue;
    }

    if (typeof current !== "object") {
      return defaultValue;
    }

    current = (current as Record<string, unknown>)[key];
  }

  return (current === undefined ? defaultValue : current) as T;
}

/**
 * Set a nested value in an object using a path
 * تعيين قيمة متداخلة في الكائن باستخدام مسار
 *
 * @param obj - الكائن - Target object
 * @param path - المسار - Dot-notation path or array of keys
 * @param value - القيمة - Value to set
 * @returns الكائن المعدل - Modified object
 *
 * @example
 * set({}, 'a.b.c', 1) // { a: { b: { c: 1 } } }
 */
export function set<T extends Record<string, unknown>>(
  obj: T,
  path: string | string[],
  value: unknown,
): T {
  const keys = Array.isArray(path) ? path : path.split(".");
  let current: Record<string, unknown> = obj;

  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i];
    if (!(key in current) || typeof current[key] !== "object" || current[key] === null) {
      current[key] = {};
    }
    current = current[key] as Record<string, unknown>;
  }

  current[keys[keys.length - 1]] = value;
  return obj;
}

/**
 * Check if an object has a nested path
 * التحقق مما إذا كان الكائن يحتوي على مسار متداخل
 *
 * @param obj - الكائن - Source object
 * @param path - المسار - Dot-notation path or array of keys
 * @returns هل المسار موجود - True if path exists
 */
export function has(obj: unknown, path: string | string[]): boolean {
  const keys = Array.isArray(path) ? path : path.split(".");
  let current: unknown = obj;

  for (const key of keys) {
    if (current === null || current === undefined) {
      return false;
    }

    if (typeof current !== "object") {
      return false;
    }

    if (!(key in (current as Record<string, unknown>))) {
      return false;
    }

    current = (current as Record<string, unknown>)[key];
  }

  return true;
}

/**
 * Deep equality comparison between two values
 * مقارنة عميقة للمساواة بين قيمتين
 *
 * @param a - القيمة الأولى - First value
 * @param b - القيمة الثانية - Second value
 * @returns هل متساويان - True if deeply equal
 */
export function deepEqual(a: unknown, b: unknown): boolean {
  // Same reference or identical primitives
  if (a === b) {
    return true;
  }

  // Handle null/undefined
  if (a === null || b === null || a === undefined || b === undefined) {
    return a === b;
  }

  // Different types
  if (typeof a !== typeof b) {
    return false;
  }

  // Handle Date
  if (a instanceof Date && b instanceof Date) {
    return a.getTime() === b.getTime();
  }

  // Handle Arrays
  if (Array.isArray(a) && Array.isArray(b)) {
    if (a.length !== b.length) {
      return false;
    }
    return a.every((item, index) => deepEqual(item, b[index]));
  }

  // Handle Maps
  if (a instanceof Map && b instanceof Map) {
    if (a.size !== b.size) {
      return false;
    }
    for (const [key, value] of a) {
      if (!b.has(key) || !deepEqual(value, b.get(key))) {
        return false;
      }
    }
    return true;
  }

  // Handle Sets
  if (a instanceof Set && b instanceof Set) {
    if (a.size !== b.size) {
      return false;
    }
    for (const item of a) {
      if (!b.has(item)) {
        return false;
      }
    }
    return true;
  }

  // Handle Objects
  if (typeof a === "object" && typeof b === "object") {
    const aKeys = Object.keys(a as Record<string, unknown>);
    const bKeys = Object.keys(b as Record<string, unknown>);

    if (aKeys.length !== bKeys.length) {
      return false;
    }

    return aKeys.every((key) =>
      deepEqual(
        (a as Record<string, unknown>)[key],
        (b as Record<string, unknown>)[key],
      ),
    );
  }

  return false;
}

/**
 * Map object values with a transform function
 * تحويل قيم الكائن باستخدام دالة
 *
 * @param obj - الكائن - Source object
 * @param fn - الدالة - Transform function
 * @returns كائن جديد - New object with transformed values
 *
 * @example
 * mapValues({ a: 1, b: 2 }, (v) => v * 2) // { a: 2, b: 4 }
 */
export function mapValues<T, U>(
  obj: Record<string, T>,
  fn: (value: T, key: string) => U,
): Record<string, U> {
  const result: Record<string, U> = {};
  for (const key of Object.keys(obj)) {
    result[key] = fn(obj[key], key);
  }
  return result;
}

/**
 * Map object keys with a transform function
 * تحويل مفاتيح الكائن باستخدام دالة
 *
 * @param obj - الكائن - Source object
 * @param fn - الدالة - Transform function
 * @returns كائن جديد - New object with transformed keys
 *
 * @example
 * mapKeys({ a: 1, b: 2 }, (k) => k.toUpperCase()) // { A: 1, B: 2 }
 */
export function mapKeys<T>(
  obj: Record<string, T>,
  fn: (key: string, value: T) => string,
): Record<string, T> {
  const result: Record<string, T> = {};
  for (const key of Object.keys(obj)) {
    result[fn(key, obj[key])] = obj[key];
  }
  return result;
}

/**
 * Filter object entries based on a predicate
 * تصفية مدخلات الكائن بناءً على شرط
 *
 * @param obj - الكائن - Source object
 * @param predicate - الشرط - Filter predicate
 * @returns كائن مفلتر - Filtered object
 */
export function filterObject<T>(
  obj: Record<string, T>,
  predicate: (value: T, key: string) => boolean,
): Record<string, T> {
  const result: Record<string, T> = {};
  for (const key of Object.keys(obj)) {
    if (predicate(obj[key], key)) {
      result[key] = obj[key];
    }
  }
  return result;
}

/**
 * Create an object from key-value pairs
 * إنشاء كائن من أزواج المفتاح-القيمة
 *
 * @param entries - المدخلات - Array of [key, value] pairs
 * @returns كائن جديد - New object
 */
export function fromEntries<K extends string | number | symbol, V>(
  entries: Array<[K, V]>,
): Record<K, V> {
  return Object.fromEntries(entries) as Record<K, V>;
}

/**
 * Invert object keys and values
 * عكس مفاتيح وقيم الكائن
 *
 * @param obj - الكائن - Source object
 * @returns كائن معكوس - Inverted object
 *
 * @example
 * invert({ a: '1', b: '2' }) // { '1': 'a', '2': 'b' }
 */
export function invert<K extends string, V extends string | number>(
  obj: Record<K, V>,
): Record<string, K> {
  const result: Record<string, K> = {};
  for (const key of Object.keys(obj) as K[]) {
    result[String(obj[key])] = key;
  }
  return result;
}
