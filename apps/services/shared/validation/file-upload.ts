/**
 * File Upload Validation Utilities
 * أدوات التحقق من تحميل الملفات
 *
 * @module shared/validation
 * @description Utilities for validating file uploads (type, size, content)
 */

import { BadRequestException } from '@nestjs/common';
import { extname } from 'path';
import * as crypto from 'crypto';

// ═══════════════════════════════════════════════════════════════════════════
// File Type Definitions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Allowed file types for different contexts
 */
export const ALLOWED_FILE_TYPES = {
  IMAGES: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'],
  DOCUMENTS: ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'csv'],
  ARCHIVES: ['zip', 'tar', 'gz', 'rar'],
  VIDEOS: ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'],
  AUDIO: ['mp3', 'wav', 'ogg', 'flac', 'm4a'],
  ALL: [] as string[], // Will be populated below
};

// Populate ALL with all allowed types
ALLOWED_FILE_TYPES.ALL = [
  ...ALLOWED_FILE_TYPES.IMAGES,
  ...ALLOWED_FILE_TYPES.DOCUMENTS,
  ...ALLOWED_FILE_TYPES.ARCHIVES,
  ...ALLOWED_FILE_TYPES.VIDEOS,
  ...ALLOWED_FILE_TYPES.AUDIO,
];

/**
 * MIME type mappings
 */
export const MIME_TYPES: Record<string, string[]> = {
  // Images
  jpg: ['image/jpeg'],
  jpeg: ['image/jpeg'],
  png: ['image/png'],
  gif: ['image/gif'],
  webp: ['image/webp'],
  svg: ['image/svg+xml'],
  bmp: ['image/bmp'],
  ico: ['image/x-icon'],

  // Documents
  pdf: ['application/pdf'],
  doc: ['application/msword'],
  docx: [
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  ],
  xls: ['application/vnd.ms-excel'],
  xlsx: ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'],
  txt: ['text/plain'],
  csv: ['text/csv', 'application/csv'],
  json: ['application/json'],
  xml: ['application/xml', 'text/xml'],

  // Archives
  zip: ['application/zip', 'application/x-zip-compressed'],
  tar: ['application/x-tar'],
  gz: ['application/gzip', 'application/x-gzip'],
  rar: ['application/x-rar-compressed'],

  // Videos
  mp4: ['video/mp4'],
  avi: ['video/x-msvideo'],
  mov: ['video/quicktime'],
  wmv: ['video/x-ms-wmv'],
  flv: ['video/x-flv'],
  webm: ['video/webm'],

  // Audio
  mp3: ['audio/mpeg'],
  wav: ['audio/wav'],
  ogg: ['audio/ogg'],
  flac: ['audio/flac'],
  m4a: ['audio/mp4'],
};

/**
 * Magic number signatures for file type validation
 * First few bytes of files to verify actual file type
 */
export const MAGIC_NUMBERS: Record<string, Buffer[]> = {
  jpg: [
    Buffer.from([0xff, 0xd8, 0xff, 0xe0]),
    Buffer.from([0xff, 0xd8, 0xff, 0xe1]),
    Buffer.from([0xff, 0xd8, 0xff, 0xe2]),
  ],
  png: [Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a])],
  gif: [Buffer.from([0x47, 0x49, 0x46, 0x38])],
  pdf: [Buffer.from([0x25, 0x50, 0x44, 0x46])],
  zip: [Buffer.from([0x50, 0x4b, 0x03, 0x04])],
  docx: [Buffer.from([0x50, 0x4b, 0x03, 0x04])], // DOCX is a ZIP file
  xlsx: [Buffer.from([0x50, 0x4b, 0x03, 0x04])], // XLSX is a ZIP file
};

// ═══════════════════════════════════════════════════════════════════════════
// File Size Limits
// ═══════════════════════════════════════════════════════════════════════════

/**
 * File size limits (in bytes)
 */
export const FILE_SIZE_LIMITS = {
  IMAGE: 10 * 1024 * 1024, // 10 MB
  DOCUMENT: 50 * 1024 * 1024, // 50 MB
  VIDEO: 100 * 1024 * 1024, // 100 MB
  AUDIO: 20 * 1024 * 1024, // 20 MB
  ARCHIVE: 100 * 1024 * 1024, // 100 MB
  DEFAULT: 10 * 1024 * 1024, // 10 MB
};

// ═══════════════════════════════════════════════════════════════════════════
// Validation Functions
// ═══════════════════════════════════════════════════════════════════════════

/**
 * File upload validation options
 */
export interface FileUploadOptions {
  /**
   * Allowed file extensions
   */
  allowedExtensions?: string[];

  /**
   * Maximum file size in bytes
   */
  maxSize?: number;

  /**
   * Validate MIME type
   */
  validateMimeType?: boolean;

  /**
   * Validate magic numbers (file signature)
   */
  validateMagicNumber?: boolean;

  /**
   * Check for malicious content
   */
  checkMalicious?: boolean;
}

/**
 * Default file upload validation options
 */
const DEFAULT_FILE_UPLOAD_OPTIONS: FileUploadOptions = {
  allowedExtensions: ALLOWED_FILE_TYPES.ALL,
  maxSize: FILE_SIZE_LIMITS.DEFAULT,
  validateMimeType: true,
  validateMagicNumber: true,
  checkMalicious: true,
};

/**
 * Validate file extension
 *
 * @param filename - Filename to validate
 * @param allowedExtensions - Array of allowed extensions
 * @returns True if extension is allowed
 */
export function validateFileExtension(
  filename: string,
  allowedExtensions: string[],
): boolean {
  const ext = extname(filename).toLowerCase().replace('.', '');
  return allowedExtensions.map((e) => e.toLowerCase()).includes(ext);
}

/**
 * Validate file size
 *
 * @param size - File size in bytes
 * @param maxSize - Maximum allowed size in bytes
 * @returns True if size is within limit
 */
export function validateFileSize(size: number, maxSize: number): boolean {
  return size > 0 && size <= maxSize;
}

/**
 * Validate MIME type
 *
 * @param mimetype - File MIME type
 * @param extension - File extension
 * @returns True if MIME type matches extension
 */
export function validateMimeType(mimetype: string, extension: string): boolean {
  const ext = extension.toLowerCase().replace('.', '');
  const allowedMimes = MIME_TYPES[ext];

  if (!allowedMimes) {
    return false;
  }

  return allowedMimes.includes(mimetype);
}

/**
 * Validate file magic number (file signature)
 *
 * @param buffer - File buffer (first few bytes)
 * @param extension - File extension
 * @returns True if magic number matches extension
 */
export function validateMagicNumber(
  buffer: Buffer,
  extension: string,
): boolean {
  const ext = extension.toLowerCase().replace('.', '');
  const magicNumbers = MAGIC_NUMBERS[ext];

  if (!magicNumbers) {
    // If we don't have magic numbers for this type, skip validation
    return true;
  }

  return magicNumbers.some((magic) => {
    if (buffer.length < magic.length) {
      return false;
    }
    return buffer.slice(0, magic.length).equals(magic);
  });
}

/**
 * Check for malicious content in filename
 *
 * @param filename - Filename to check
 * @returns True if filename appears safe
 */
export function checkMaliciousFilename(filename: string): boolean {
  // Check for path traversal
  if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
    return false;
  }

  // Check for null bytes
  if (filename.includes('\x00')) {
    return false;
  }

  // Check for executable extensions
  const dangerousExtensions = [
    'exe',
    'bat',
    'cmd',
    'sh',
    'ps1',
    'dll',
    'so',
    'dylib',
    'app',
    'deb',
    'rpm',
    'msi',
    'apk',
    'jar',
    'com',
    'scr',
    'vbs',
    'js',
    'jse',
    'wsf',
    'wsh',
  ];

  const ext = extname(filename).toLowerCase().replace('.', '');
  if (dangerousExtensions.includes(ext)) {
    return false;
  }

  // Check for double extensions (e.g., file.pdf.exe)
  const parts = filename.split('.');
  if (parts.length > 2) {
    for (let i = 1; i < parts.length - 1; i++) {
      if (dangerousExtensions.includes(parts[i].toLowerCase())) {
        return false;
      }
    }
  }

  return true;
}

/**
 * Comprehensive file upload validation
 *
 * @param file - File object from multer
 * @param options - Validation options
 * @throws BadRequestException if validation fails
 */
export function validateFileUpload(
  file: Express.Multer.File,
  options: FileUploadOptions = {},
): void {
  const opts = { ...DEFAULT_FILE_UPLOAD_OPTIONS, ...options };

  // Check if file exists
  if (!file) {
    throw new BadRequestException('No file provided');
  }

  const filename = file.originalname;
  const extension = extname(filename).toLowerCase().replace('.', '');

  // Validate filename for malicious content
  if (opts.checkMalicious && !checkMaliciousFilename(filename)) {
    throw new BadRequestException(
      'Malicious filename detected. Please use a safe filename.',
    );
  }

  // Validate file extension
  if (opts.allowedExtensions && opts.allowedExtensions.length > 0) {
    if (!validateFileExtension(filename, opts.allowedExtensions)) {
      throw new BadRequestException(
        `File type .${extension} is not allowed. Allowed types: ${opts.allowedExtensions.join(', ')}`,
      );
    }
  }

  // Validate file size
  if (opts.maxSize && !validateFileSize(file.size, opts.maxSize)) {
    const maxSizeMB = (opts.maxSize / (1024 * 1024)).toFixed(2);
    const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
    throw new BadRequestException(
      `File size ${fileSizeMB}MB exceeds maximum allowed size of ${maxSizeMB}MB`,
    );
  }

  // Validate MIME type
  if (opts.validateMimeType && !validateMimeType(file.mimetype, extension)) {
    throw new BadRequestException(
      `MIME type ${file.mimetype} does not match file extension .${extension}`,
    );
  }

  // Validate magic number (file signature)
  if (opts.validateMagicNumber && file.buffer) {
    if (!validateMagicNumber(file.buffer, extension)) {
      throw new BadRequestException(
        `File signature does not match extension .${extension}. File may be corrupted or renamed.`,
      );
    }
  }
}

/**
 * Generate safe filename
 * Removes dangerous characters and adds timestamp
 *
 * @param originalFilename - Original filename
 * @param prefix - Optional prefix
 * @returns Safe filename
 */
export function generateSafeFilename(
  originalFilename: string,
  prefix?: string,
): string {
  // Get extension
  const ext = extname(originalFilename);

  // Remove extension and dangerous characters
  let basename = originalFilename
    .replace(ext, '')
    .replace(/[^a-zA-Z0-9_-]/g, '_')
    .toLowerCase();

  // Limit length
  if (basename.length > 50) {
    basename = basename.substring(0, 50);
  }

  // Add timestamp and random string
  const timestamp = Date.now();
  const random = crypto.randomBytes(4).toString('hex');

  // Construct filename
  const parts = [prefix, basename, timestamp, random].filter(Boolean);
  return `${parts.join('_')}${ext}`;
}

/**
 * Calculate file hash (SHA-256)
 * Useful for detecting duplicate uploads
 *
 * @param buffer - File buffer
 * @returns SHA-256 hash
 */
export function calculateFileHash(buffer: Buffer): string {
  return crypto.createHash('sha256').update(buffer).digest('hex');
}

// ═══════════════════════════════════════════════════════════════════════════
// NestJS Multer File Filter
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create Multer file filter for NestJS
 *
 * @param allowedExtensions - Array of allowed file extensions
 * @returns Multer file filter function
 */
export function createFileFilter(allowedExtensions: string[]) {
  return (
    req: any,
    file: Express.Multer.File,
    callback: (error: Error | null, acceptFile: boolean) => void,
  ) => {
    if (!validateFileExtension(file.originalname, allowedExtensions)) {
      const ext = extname(file.originalname).toLowerCase().replace('.', '');
      callback(
        new BadRequestException(
          `File type .${ext} is not allowed. Allowed types: ${allowedExtensions.join(', ')}`,
        ),
        false,
      );
      return;
    }

    if (!checkMaliciousFilename(file.originalname)) {
      callback(
        new BadRequestException('Malicious filename detected'),
        false,
      );
      return;
    }

    callback(null, true);
  };
}

/**
 * Image file filter (JPG, PNG, GIF, WEBP)
 */
export const imageFileFilter = createFileFilter(ALLOWED_FILE_TYPES.IMAGES);

/**
 * Document file filter (PDF, DOC, DOCX, XLS, XLSX, TXT, CSV)
 */
export const documentFileFilter = createFileFilter(
  ALLOWED_FILE_TYPES.DOCUMENTS,
);

// ═══════════════════════════════════════════════════════════════════════════
// Export all file upload utilities
// ═══════════════════════════════════════════════════════════════════════════

export const FILE_UPLOAD_UTILITIES = {
  ALLOWED_FILE_TYPES,
  MIME_TYPES,
  MAGIC_NUMBERS,
  FILE_SIZE_LIMITS,
  validateFileExtension,
  validateFileSize,
  validateMimeType,
  validateMagicNumber,
  checkMaliciousFilename,
  validateFileUpload,
  generateSafeFilename,
  calculateFileHash,
  createFileFilter,
  imageFileFilter,
  documentFileFilter,
};
