/**
 * Update User DTO
 * كائن نقل البيانات لتحديث مستخدم
 */

import { ApiPropertyOptional } from '@nestjs/swagger';
import {
  IsEmail,
  IsString,
  IsEnum,
  IsOptional,
  MinLength,
  MaxLength,
  IsBoolean,
} from 'class-validator';
import { UserRole, UserStatus } from '@prisma/client';

export class UpdateUserDto {
  @ApiPropertyOptional({
    description: 'User email address',
    example: 'user@example.com',
  })
  @IsOptional()
  @IsEmail()
  email?: string;

  @ApiPropertyOptional({
    description: 'User phone number',
    example: '+966501234567',
  })
  @IsOptional()
  @IsString()
  phone?: string;

  @ApiPropertyOptional({
    description: 'User password (min 8 characters)',
    example: 'NewSecurePassword123!',
  })
  @IsOptional()
  @IsString()
  @MinLength(8)
  password?: string;

  @ApiPropertyOptional({
    description: 'User first name',
    example: 'أحمد',
  })
  @IsOptional()
  @IsString()
  @MinLength(2)
  @MaxLength(50)
  firstName?: string;

  @ApiPropertyOptional({
    description: 'User last name',
    example: 'محمد',
  })
  @IsOptional()
  @IsString()
  @MinLength(2)
  @MaxLength(50)
  lastName?: string;

  @ApiPropertyOptional({
    description: 'User role',
    enum: UserRole,
  })
  @IsOptional()
  @IsEnum(UserRole)
  role?: UserRole;

  @ApiPropertyOptional({
    description: 'User status',
    enum: UserStatus,
  })
  @IsOptional()
  @IsEnum(UserStatus)
  status?: UserStatus;

  @ApiPropertyOptional({
    description: 'Email verification status',
  })
  @IsOptional()
  @IsBoolean()
  emailVerified?: boolean;

  @ApiPropertyOptional({
    description: 'Phone verification status',
  })
  @IsOptional()
  @IsBoolean()
  phoneVerified?: boolean;
}
