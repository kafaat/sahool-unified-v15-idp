/**
 * Marketplace DTOs - Data Transfer Objects
 * كائنات نقل البيانات للسوق
 */

import { IsString, IsNumber, IsOptional, IsPositive, Min, Max, IsEnum, IsUUID, IsNotEmpty } from 'class-validator';

/**
 * Create Product DTO
 * كائن إنشاء منتج
 */
export class CreateProductDto {
  @IsString()
  @IsNotEmpty()
  name: string;

  @IsString()
  @IsOptional()
  nameAr?: string;

  @IsString()
  @IsOptional()
  description?: string;

  @IsString()
  @IsNotEmpty()
  category: string;

  @IsNumber()
  @IsPositive()
  price: number;

  @IsNumber()
  @IsPositive()
  quantity: number;

  @IsString()
  @IsOptional()
  unit?: string;

  @IsString()
  @IsNotEmpty()
  sellerId: string;

  @IsString()
  @IsOptional()
  governorate?: string;

  @IsString()
  @IsOptional()
  imageUrl?: string;
}

/**
 * Create Order DTO
 * كائن إنشاء طلب
 */
export class CreateOrderDto {
  @IsString()
  @IsNotEmpty()
  productId: string;

  @IsString()
  @IsNotEmpty()
  buyerId: string;

  @IsNumber()
  @IsPositive()
  quantity: number;

  @IsString()
  @IsOptional()
  shippingAddress?: string;

  @IsString()
  @IsOptional()
  notes?: string;
}

/**
 * List Harvest DTO
 * كائن عرض الحصاد
 */
export class ListHarvestDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @IsNotEmpty()
  yieldData: {
    fieldId: string;
    cropType: string;
    estimatedQuantity: number;
    harvestDate?: string;
    quality?: string;
  };
}

/**
 * Calculate Credit Score DTO
 * كائن حساب التصنيف الائتماني
 */
export class CalculateCreditScoreDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @IsNotEmpty()
  farmData: {
    fieldCount?: number;
    totalArea?: number;
    avgNdvi?: number;
    cropDiversity?: number;
    harvestHistory?: number;
  };
}

/**
 * Calculate Advanced Credit Score DTO
 * كائن حساب التصنيف الائتماني المتقدم
 */
export class CalculateAdvancedCreditScoreDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @IsNotEmpty()
  factors: {
    fieldHealth?: number;
    paymentHistory?: number;
    marketActivity?: number;
    loanRepayment?: number;
    verificationLevel?: string;
  };
}

/**
 * Record Credit Event DTO
 * كائن تسجيل حدث ائتماني
 */
export class RecordCreditEventDto {
  @IsString()
  @IsNotEmpty()
  userId: string;

  @IsString()
  @IsNotEmpty()
  eventType: string;

  @IsNumber()
  @IsOptional()
  amount?: number;

  @IsString()
  @IsOptional()
  description?: string;

  @IsNumber()
  @IsOptional()
  @Min(-100)
  @Max(100)
  scoreImpact?: number;
}

/**
 * Request Loan DTO
 * كائن طلب قرض
 */
export class RequestLoanDto {
  @IsString()
  @IsNotEmpty()
  walletId: string;

  @IsNumber()
  @IsPositive()
  amount: number;

  @IsString()
  @IsNotEmpty()
  purpose: string;

  @IsNumber()
  @IsPositive()
  @Min(1)
  @Max(60)
  termMonths: number;

  @IsString()
  @IsOptional()
  collateral?: string;
}

/**
 * Deposit/Withdraw DTO
 * كائن الإيداع/السحب
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
 * كائن سداد القرض
 */
export class RepayLoanDto {
  @IsNumber()
  @IsPositive()
  amount: number;
}

/**
 * Create Escrow DTO
 * كائن إنشاء الإسكرو
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
 * كائن إطلاق/استرداد الإسكرو
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
 * كائن إنشاء دفعة مجدولة
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
