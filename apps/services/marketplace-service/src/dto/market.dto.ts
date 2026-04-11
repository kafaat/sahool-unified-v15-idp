/**
 * Marketplace DTOs - Data Transfer Objects
 * كائنات نقل البيانات للسوق
 *
 * These DTOs must match the interfaces defined in the service files
 */

import {
  IsString,
  IsNumber,
  IsOptional,
  IsPositive,
  IsArray,
  ValidateNested,
  IsBoolean,
  IsIn,
  Min,
  Max,
  IsNotEmpty,
  IsEnum,
  IsDateString,
  IsObject,
  IsUUID,
  IsUrl,
} from "class-validator";
import { Type } from "class-transformer";
import {
  IsMoneyValue,
  SanitizePlainText,
  IsYemeniPhone,
  IsAfterDate,
  IsFutureDate,
} from "../utils/validation";

// ═══════════════════════════════════════════════════════════════════════════
// Market DTOs
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Create Product DTO - matches CreateProductDto in market.service.ts
 */
export class CreateProductDto {
  @IsString()
  @IsNotEmpty()
  @SanitizePlainText()
  name: string;

  @IsString()
  @IsNotEmpty()
  @SanitizePlainText()
  nameAr: string;

  @IsIn(["HARVEST", "SEEDS", "FERTILIZER", "PESTICIDE", "EQUIPMENT", "IRRIGATION", "OTHER"])
  @IsNotEmpty()
  category: string;

  @IsMoneyValue()
  price: number;

  @IsNumber()
  @Min(0)
  stock: number;

  @IsString()
  @IsNotEmpty()
  @SanitizePlainText()
  unit: string;

  @IsString()
  @IsOptional()
  @SanitizePlainText()
  description?: string;

  @IsString()
  @IsOptional()
  @SanitizePlainText()
  descriptionAr?: string;

  @IsUrl()
  @IsOptional()
  imageUrl?: string;

  @IsUUID()
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
  @SanitizePlainText()
  buyerName?: string;

  @IsOptional()
  @IsYemeniPhone()
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

  // Currency allow-list is shared with wallet DTOs below. When absent the
  // service defaults to YER (Yemeni Rial) for backward compatibility with
  // pre-currency order payloads.
  @IsString()
  @IsOptional()
  @IsIn(["SAR", "YER", "USD", "AED", "EUR"], {
    message: "currency must be one of SAR, YER, USD, AED, EUR",
  })
  currency?: "SAR" | "YER" | "USD" | "AED" | "EUR";
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

  @IsMoneyValue()
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
  @IsIn(["Low", "Medium", "High"])
  diseaseRisk: "Low" | "Medium" | "High";

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
  @IsIn(["rainfed", "drip", "flood", "sprinkler"])
  irrigationType: "rainfed" | "drip" | "flood" | "sprinkler";

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
  @IsIn(["basic", "verified", "premium"])
  verificationLevel: "basic" | "verified" | "premium";

  @IsString()
  @IsIn(["owned", "leased", "shared"])
  landOwnership: "owned" | "leased" | "shared";

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

  @IsMoneyValue()
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

  @IsOptional()
  @IsMoneyValue()
  collateralValue?: number;
}

/**
 * Deposit/Withdraw DTO
 *
 * `currency` is optional but when supplied must belong to the allow-list
 * enforced by the SAHOOL platform (SAR, YER, USD, AED, EUR). Rejecting
 * unknown currency codes at the DTO boundary prevents upstream services
 * from having to re-validate.
 */
export const ALLOWED_CURRENCIES = [
  "SAR",
  "YER",
  "USD",
  "AED",
  "EUR",
] as const;
export type AllowedCurrency = (typeof ALLOWED_CURRENCIES)[number];

export class WalletTransactionDto {
  @IsMoneyValue()
  amount: number;

  @IsString()
  @IsOptional()
  description?: string;

  @IsString()
  @IsOptional()
  @IsIn(ALLOWED_CURRENCIES as unknown as string[], {
    message: `currency must be one of ${ALLOWED_CURRENCIES.join(", ")}`,
  })
  currency?: AllowedCurrency;
}

/**
 * Wallet Transfer DTO
 *
 * Promotes the previously-inline transfer body to a typed DTO so we can
 * apply `class-validator` constraints (including the currency allow-list)
 * consistently with deposit/withdraw.
 */
export class WalletTransferDto {
  @IsString()
  @IsNotEmpty()
  fromWalletId: string;

  @IsString()
  @IsNotEmpty()
  toWalletId: string;

  @IsMoneyValue()
  amount: number;

  @IsString()
  @IsOptional()
  description?: string;

  @IsString()
  @IsOptional()
  pin?: string;

  @IsString()
  @IsOptional()
  @IsIn(ALLOWED_CURRENCIES as unknown as string[], {
    message: `currency must be one of ${ALLOWED_CURRENCIES.join(", ")}`,
  })
  currency?: AllowedCurrency;
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
  @IsEnum(["DAILY", "WEEKLY", "BIWEEKLY", "MONTHLY", "QUARTERLY", "YEARLY"])
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
