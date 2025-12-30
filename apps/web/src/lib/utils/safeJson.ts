/**
 * Safe JSON Parsing Utilities
 * Utilities for safely parsing JSON data with validation
 */

import { z, ZodSchema } from 'zod';

/**
 * Safely parse JSON string with optional Zod schema validation
 * @param jsonString - The JSON string to parse
 * @param schema - Optional Zod schema for validation
 * @returns Parsed and validated data, or null if parsing/validation fails
 */
export function safeJsonParse<T = unknown>(
  jsonString: string,
  schema?: ZodSchema<T>
): T | null {
  try {
    // First, attempt to parse the JSON
    const parsed = JSON.parse(jsonString);

    // If a schema is provided, validate the parsed data
    if (schema) {
      const validated = schema.parse(parsed);
      return validated;
    }

    return parsed as T;
  } catch (error) {
    if (error instanceof SyntaxError) {
      console.error('JSON parsing error:', error.message);
    } else if (error instanceof z.ZodError) {
      console.error('JSON validation error:', error.issues);
    } else {
      console.error('Unexpected error during JSON parsing:', error);
    }
    return null;
  }
}

/**
 * Safely parse JSON with a default fallback value
 * @param jsonString - The JSON string to parse
 * @param defaultValue - Default value to return if parsing fails
 * @param schema - Optional Zod schema for validation
 * @returns Parsed data or default value
 */
export function safeJsonParseWithDefault<T>(
  jsonString: string,
  defaultValue: T,
  schema?: ZodSchema<T>
): T {
  const result = safeJsonParse(jsonString, schema);
  return result !== null ? result : defaultValue;
}

/**
 * Safely stringify an object to JSON
 * @param data - The data to stringify
 * @param pretty - Whether to pretty-print the JSON
 * @returns JSON string or null if stringification fails
 */
export function safeJsonStringify(
  data: unknown,
  pretty: boolean = false
): string | null {
  try {
    return JSON.stringify(data, null, pretty ? 2 : 0);
  } catch (error) {
    console.error('JSON stringification error:', error);
    return null;
  }
}

/**
 * Validate if a string is valid JSON
 * @param jsonString - The string to validate
 * @returns True if valid JSON, false otherwise
 */
export function isValidJson(jsonString: string): boolean {
  try {
    JSON.parse(jsonString);
    return true;
  } catch {
    return false;
  }
}
