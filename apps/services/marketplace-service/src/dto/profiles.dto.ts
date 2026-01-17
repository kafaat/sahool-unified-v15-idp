/**
 * Profiles DTOs - Data Transfer Objects
 * كائنات نقل البيانات للملفات الشخصية
 */

import {
  IsString,
  IsNumber,
  IsOptional,
  IsBoolean,
  IsEnum,
  IsNotEmpty,
  IsArray,
  Min,
  Max,
  IsObject,
} from "class-validator";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

// ═══════════════════════════════════════════════════════════════════════════
// Seller Profile DTOs
// ═══════════════════════════════════════════════════════════════════════════

export enum BusinessType {
  INDIVIDUAL = "INDIVIDUAL",
  FARM = "FARM",
  COOPERATIVE = "COOPERATIVE",
  DISTRIBUTOR = "DISTRIBUTOR",
  RETAILER = "RETAILER",
}

export class CreateSellerProfileDto {
  @ApiProperty({ description: "User ID", example: "user-123" })
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ApiProperty({ description: "Tenant ID", example: "tenant-123" })
  @IsString()
  @IsNotEmpty()
  tenantId: string;

  @ApiProperty({
    description: "Business name",
    example: "مزرعة الأمل الزراعية",
  })
  @IsString()
  @IsNotEmpty()
  businessName: string;

  @ApiProperty({
    description: "Business type",
    enum: BusinessType,
    example: BusinessType.FARM,
  })
  @IsEnum(BusinessType)
  businessType: BusinessType;

  @ApiPropertyOptional({ description: "Tax ID", example: "123456789" })
  @IsString()
  @IsOptional()
  taxId?: string;

  @ApiPropertyOptional({
    description: "Bank account information",
    example: {
      bankName: "CAC Bank",
      accountNumber: "1234567890",
      iban: "YE12345",
    },
  })
  @IsObject()
  @IsOptional()
  bankAccount?: any;

  @ApiPropertyOptional({
    description: "Payout preferences",
    example: { method: "bank_transfer", frequency: "weekly" },
  })
  @IsObject()
  @IsOptional()
  payoutPreferences?: any;
}

export class UpdateSellerProfileDto {
  @ApiPropertyOptional({ description: "Business name" })
  @IsString()
  @IsOptional()
  businessName?: string;

  @ApiPropertyOptional({ description: "Business type", enum: BusinessType })
  @IsEnum(BusinessType)
  @IsOptional()
  businessType?: BusinessType;

  @ApiPropertyOptional({ description: "Tax ID" })
  @IsString()
  @IsOptional()
  taxId?: string;

  @ApiPropertyOptional({ description: "Bank account information" })
  @IsObject()
  @IsOptional()
  bankAccount?: any;

  @ApiPropertyOptional({ description: "Payout preferences" })
  @IsObject()
  @IsOptional()
  payoutPreferences?: any;
}

export class VerifySellerDto {
  @ApiProperty({ description: "Verification status", example: true })
  @IsBoolean()
  verified: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// Buyer Profile DTOs
// ═══════════════════════════════════════════════════════════════════════════

export class ShippingAddress {
  @ApiProperty({ description: "Address label", example: "Home" })
  @IsString()
  label: string;

  @ApiProperty({ description: "Full address", example: "صنعاء، شارع الزبيري" })
  @IsString()
  address: string;

  @ApiProperty({ description: "City", example: "صنعاء" })
  @IsString()
  city: string;

  @ApiPropertyOptional({ description: "Phone number" })
  @IsString()
  @IsOptional()
  phone?: string;

  @ApiProperty({ description: "Default address", example: true })
  @IsBoolean()
  isDefault: boolean;
}

export class CreateBuyerProfileDto {
  @ApiProperty({ description: "User ID", example: "user-123" })
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ApiProperty({ description: "Tenant ID", example: "tenant-123" })
  @IsString()
  @IsNotEmpty()
  tenantId: string;

  @ApiPropertyOptional({
    description: "Shipping addresses",
    type: [ShippingAddress],
  })
  @IsArray()
  @IsOptional()
  shippingAddresses?: ShippingAddress[];

  @ApiPropertyOptional({
    description: "Preferred payment method",
    example: "wallet",
    enum: ["wallet", "cash", "bank_transfer"],
  })
  @IsString()
  @IsOptional()
  preferredPayment?: string;
}

export class UpdateBuyerProfileDto {
  @ApiPropertyOptional({ description: "Shipping addresses" })
  @IsArray()
  @IsOptional()
  shippingAddresses?: ShippingAddress[];

  @ApiPropertyOptional({
    description: "Preferred payment method",
    enum: ["wallet", "cash", "bank_transfer"],
  })
  @IsString()
  @IsOptional()
  preferredPayment?: string;
}

export class AddShippingAddressDto {
  @ApiProperty({ description: "Address label", example: "Home" })
  @IsString()
  @IsNotEmpty()
  label: string;

  @ApiProperty({ description: "Full address", example: "صنعاء، شارع الزبيري" })
  @IsString()
  @IsNotEmpty()
  address: string;

  @ApiProperty({ description: "City", example: "صنعاء" })
  @IsString()
  @IsNotEmpty()
  city: string;

  @ApiPropertyOptional({ description: "Phone number" })
  @IsString()
  @IsOptional()
  phone?: string;

  @ApiProperty({ description: "Set as default address", example: false })
  @IsBoolean()
  @IsOptional()
  isDefault?: boolean;
}

export class UpdateLoyaltyPointsDto {
  @ApiProperty({ description: "Points to add/subtract", example: 100 })
  @IsNumber()
  points: number;

  @ApiPropertyOptional({ description: "Reason for points change" })
  @IsString()
  @IsOptional()
  reason?: string;
}
