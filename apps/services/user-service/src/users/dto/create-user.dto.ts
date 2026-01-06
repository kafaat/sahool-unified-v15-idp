/**
 * Create User DTO
 * كائن نقل البيانات لإنشاء مستخدم
 */

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import {
  IsEmail,
  IsString,
  IsEnum,
  IsOptional,
  MinLength,
  MaxLength,
  IsPhoneNumber,
  IsBoolean,
} from 'class-validator';
import { UserRole, UserStatus } from '@prisma/client';
import { IsYemeniPhone, IsStrongPassword, SanitizePlainText } from '../../../shared/validation';

export class CreateUserDto {
  @ApiProperty({
    description: 'Tenant ID',
    example: '123e4567-e89b-12d3-a456-426614174000',
  })
  @IsString()
  tenantId: string;

  @ApiProperty({
    description: 'User email address',
    example: 'user@example.com',
  })
  @IsEmail()
  email: string;

  @ApiPropertyOptional({
    description: 'User phone number (Yemen format: +967XXXXXXXX or 7XXXXXXXX)',
    example: '+967712345678',
  })
  @IsOptional()
  @IsYemeniPhone()
  phone?: string;

  @ApiProperty({
    description: 'User password (min 8 characters, must contain uppercase, lowercase, number, and special character)',
    example: 'SecurePassword123!',
  })
  @IsStrongPassword(8)
  password: string;

  @ApiProperty({
    description: 'User first name',
    example: 'أحمد',
  })
  @IsString()
  @MinLength(2)
  @MaxLength(50)
  @SanitizePlainText()
  firstName: string;

  @ApiProperty({
    description: 'User last name',
    example: 'محمد',
  })
  @IsString()
  @MinLength(2)
  @MaxLength(50)
  @SanitizePlainText()
  lastName: string;

  @ApiPropertyOptional({
    description: 'User role',
    enum: UserRole,
    default: UserRole.VIEWER,
  })
  @IsOptional()
  @IsEnum(UserRole)
  role?: UserRole;

  @ApiPropertyOptional({
    description: 'User status',
    enum: UserStatus,
    default: UserStatus.PENDING,
  })
  @IsOptional()
  @IsEnum(UserStatus)
  status?: UserStatus;

  @ApiPropertyOptional({
    description: 'Email verification status',
    default: false,
  })
  @IsOptional()
  @IsBoolean()
  emailVerified?: boolean;

  @ApiPropertyOptional({
    description: 'Phone verification status',
    default: false,
  })
  @IsOptional()
  @IsBoolean()
  phoneVerified?: boolean;
}
