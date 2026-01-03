/**
 * Marketplace DTOs - Data Transfer Objects
 * كائنات نقل البيانات للسوق
 *
 * These DTOs must match the interfaces defined in the service files
 */

import { IsString, IsNumber, IsOptional, IsPositive, IsArray, ValidateNested, IsBoolean, IsIn, Min, Max, IsNotEmpty, IsEnum, IsDateString, IsObject } from 'class-validator';
import { Type } from 'class-transformer';

// ═══════════════════════════════════════════════════════════════════════════
// Market DTOs
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create Product DTO - matches CreateProductDto in market.service.ts
 */
export class CreateProductDto {
  @IsString()
  @IsNotEmpty()
  name: string;

  @IsString()
  @IsNotEmpty()
  nameAr: string;

  @IsString()
  @IsNotEmpty()
  category: string;

  @IsNumber()
  @IsPositive()
  price: number;

  @IsNumber()
  @Min(0)
  stock: number;

  @IsString()
  @IsNotEmpty()
  unit: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsString()
  @IsOptional()
  descriptionAr?: string;

  @IsString()
  @IsOptional()
  imageUrl?: string;

  @IsString()
  @IsNotEmpty()
  sellerId: string;

  @IsString()
  @IsNotEmpty()
  sellerType: string;

  @IsString()
  @IsOptional()
  sellerName?: string;

  @IsString()
  @IsOptional()
  cropType?: string;

  @IsString()
  @IsOptional()
  governorate?: string;
}

/**
 * Order Item for CreateOrderDto
 */
class OrderItemDto {
  @IsString()
  @IsNotEmpty()
  productId: string;

  @IsNumber()
  @IsPositive()
  quantity: number;
}

/**
 * Create Order DTO - matches CreateOrderDto in market.service.ts
 */
export class CreateOrderDto {
  @IsString()
  @IsNotEmpty()
  buyerId: string;

  @IsString()
  @IsOptional()
  buyerName?: string;

  @IsString()
  @IsOptional()
  buyerPhone?: string;

  @IsArray()
  @ValidateNested({ each: true })
  @Type(() => OrderItemDto)
  items: OrderItemDto[];

  @IsString()
  @IsOptional()
  deliveryAddress?: string;

  @IsString()
  @IsOptional()
  paymentMethod?: string;
}

/**
 * YieldData for ListHarvestDto - matches YieldData in market.service.ts
 */
class YieldDataDto {
  @IsString()
  @IsNotEmpty()
  crop: string;

  @IsString()
  @IsNotEmpty()
  cropAr: string;

  @IsNumber()
  @IsPositive()
  predictedYieldTons: number;

  @IsNumber()
  @IsPositive()
  pricePerTon: number;

  @IsString()
  @IsOptional()
  harvestDate?: string;

  @IsString()
  @IsOptional()
  qualityGrade?: string;

  @IsString()
  @IsOptional()
  governorate?: string;

  @IsString()
  @IsOptional()
  district?: string;
}

/**
 * List Harvest DTO
 */
export class ListHarvestDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ValidateNested()
  @Type(() => YieldDataDto)
  yieldData: YieldDataDto;
}

// ═══════════════════════════════════════════════════════════════════════════
// FinTech DTOs
// ═══════════════════════════════════════════════════════════════════════════

/**
 * FarmData for CalculateCreditScoreDto - matches FarmData in fintech.service.ts
 */
class FarmDataDto {
  @IsNumber()
  @Min(0)
  totalArea: number;

  @IsNumber()
  @Min(0)
  activeSeasons: number;

  @IsNumber()
  @Min(0)
  fieldCount: number;

  @IsString()
  @IsIn(['Low', 'Medium', 'High'])
  diseaseRisk: 'Low' | 'Medium' | 'High';

  @IsString()
  @IsNotEmpty()
  irrigationType: string;

  @IsNumber()
  @Min(0)
  @Max(100)
  avgYieldScore: number;

  @IsNumber()
  @Min(0)
  onTimePayments: number;

  @IsNumber()
  @Min(0)
  latePayments: number;
}

/**
 * Calculate Credit Score DTO - matches FarmData interface
 */
export class CalculateCreditScoreDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ValidateNested()
  @Type(() => FarmDataDto)
  farmData: FarmDataDto;
}

/**
 * CreditFactors for CalculateAdvancedCreditScoreDto - matches CreditFactors in fintech.service.ts
 */
class CreditFactorsDto {
  @IsNumber()
  @Min(0)
  farmArea: number;

  @IsNumber()
  @Min(0)
  numberOfSeasons: number;

  @IsNumber()
  @Min(0)
  @Max(100)
  diseaseRiskScore: number;

  @IsString()
  @IsIn(['rainfed', 'drip', 'flood', 'sprinkler'])
  irrigationType: 'rainfed' | 'drip' | 'flood' | 'sprinkler';

  @IsNumber()
  @Min(0)
  @Max(100)
  yieldScore: number;

  @IsNumber()
  @Min(0)
  @Max(100)
  paymentHistory: number;

  @IsNumber()
  @Min(1)
  @Max(10)
  cropDiversity: number;

  @IsNumber()
  @Min(0)
  @Max(100)
  marketplaceHistory: number;

  @IsNumber()
  @Min(0)
  @Max(100)
  loanRepaymentRate: number;

  @IsString()
  @IsIn(['basic', 'verified', 'premium'])
  verificationLevel: 'basic' | 'verified' | 'premium';

  @IsString()
  @IsIn(['owned', 'leased', 'shared'])
  landOwnership: 'owned' | 'leased' | 'shared';

  @IsBoolean()
  cooperativeMember: boolean;

  @IsNumber()
  @Min(0)
  yearsOfExperience: number;

  @IsBoolean()
  satelliteVerified: boolean;
}

/**
 * Calculate Advanced Credit Score DTO
 */
export class CalculateAdvancedCreditScoreDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @ValidateNested()
  @Type(() => CreditFactorsDto)
  factors: CreditFactorsDto;
}

/**
 * Metadata for RecordCreditEventDto - provides structured metadata information
 */
export class MetadataDto {
  @IsString()
  @IsOptional()
  source?: string;

  @IsString()
  @IsOptional()
  timestamp?: string;

  @IsObject()
  @IsOptional()
  additionalInfo?: Record<string, unknown>;
}

/**
 * Record Credit Event DTO - matches RecordCreditEventDto in fintech.service.ts
 */
export class RecordCreditEventDto {
  @IsString()
  @IsNotEmpty()
  walletId: string;

  @IsString()
  @IsNotEmpty()
  eventType: string;

  @IsNumber()
  @IsOptional()
  amount?: number;

  @IsString()
  @IsNotEmpty()
  description: string;

  @IsOptional()
  @ValidateNested()
  @Type(() => MetadataDto)
  metadata?: MetadataDto;
}

/**
 * Request Loan DTO - matches CreateLoanDto in fintech.service.ts
 */
export class RequestLoanDto {
  @IsString()
  @IsNotEmpty()
  walletId: string;

  @IsNumber()
  @IsPositive()
  amount: number;

  @IsNumber()
  @IsPositive()
  @Min(1)
  @Max(60)
  termMonths: number;

  @IsString()
  @IsNotEmpty()
  purpose: string;

  @IsString()
  @IsOptional()
  purposeDetails?: string;

  @IsString()
  @IsOptional()
  collateralType?: string;

  @IsNumber()
  @IsOptional()
  @IsPositive()
  collateralValue?: number;
}

/**
 * Deposit/Withdraw DTO
 */
export class WalletTransactionDto {
  @IsNumber()
  @IsPositive()
  amount: number;

  @IsString()
  @IsOptional()
  description?: string;
}

/**
 * Repay Loan DTO
 */
export class RepayLoanDto {
  @IsNumber()
  @IsPositive()
  amount: number;
}

/**
 * Create Escrow DTO
 */
export class CreateEscrowDto {
  @IsString()
  @IsNotEmpty()
  orderId: string;

  @IsString()
  @IsNotEmpty()
  buyerWalletId: string;

  @IsString()
  @IsNotEmpty()
  sellerWalletId: string;

  @IsNumber()
  @IsPositive()
  amount: number;

  @IsString()
  @IsOptional()
  notes?: string;
}

/**
 * Release/Refund Escrow DTO
 */
export class EscrowActionDto {
  @IsString()
  @IsOptional()
  notes?: string;

  @IsString()
  @IsOptional()
  reason?: string;
}

/**
 * Create Scheduled Payment DTO
 */
export class CreateScheduledPaymentDto {
  @IsNumber()
  @IsPositive()
  amount: number;

  @IsString()
  @IsNotEmpty()
  @IsEnum(['DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY'])
  frequency: string;

  @IsString()
  @IsNotEmpty()
  @IsDateString()
  nextPaymentDate: string;

  @IsString()
  @IsOptional()
  loanId?: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsString()
  @IsOptional()
  descriptionAr?: string;
}
