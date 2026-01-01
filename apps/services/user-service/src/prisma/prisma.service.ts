/**
 * Prisma Service - Database Connection with Encryption
 * خدمة الاتصال بقاعدة البيانات مع التشفير
 */

import { Injectable, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { PrismaClient } from '@prisma/client';
import { createPrismaEncryptionMiddleware } from '../../../../packages/shared-crypto/src/prisma-encryption';

@Injectable()
export class PrismaService
  extends PrismaClient
  implements OnModuleInit, OnModuleDestroy
{
  constructor() {
    super({
      log: ['query', 'info', 'warn', 'error'],
    });

    // Apply encryption middleware
    this.enableEncryption();
  }

  /**
   * Enable field-level encryption for sensitive data
   * تفعيل التشفير على مستوى الحقول للبيانات الحساسة
   */
  private enableEncryption() {
    const encryptionConfig = {
      // User model - phone is searchable (deterministic encryption)
      User: {
        phone: { type: 'deterministic' as const },
      },
      // UserProfile model - nationalId and phone are searchable
      UserProfile: {
        nationalId: { type: 'deterministic' as const },
        dateOfBirth: { type: 'standard' as const },
      },
    };

    this.$use(
      createPrismaEncryptionMiddleware(encryptionConfig, {
        debug: process.env.CRYPTO_DEBUG === 'true',
        onError: (error, context) => {
          // nosemgrep: javascript.lang.security.audit.unsafe-formatstring.unsafe-formatstring
          console.error(
            '[Encryption Error] %s failed for %s.%s: %s',
            context.operation,
            context.model,
            context.field,
            error.message
          );
        },
      })
    );

    console.log('Field-level encryption enabled for User Service');
  }

  async onModuleInit() {
    await this.$connect();
    console.log('User Service Database connected successfully');
  }

  async onModuleDestroy() {
    await this.$disconnect();
  }
}
