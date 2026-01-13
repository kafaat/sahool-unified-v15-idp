/**
 * Reviews DTOs - Data Transfer Objects
 * كائنات نقل البيانات للتقييمات
 */

import {
  IsString,
  IsNumber,
  IsOptional,
  IsBoolean,
  IsArray,
  IsNotEmpty,
  Min,
  Max,
} from "class-validator";
import { Type } from "class-transformer";
import { ApiProperty, ApiPropertyOptional } from "@nestjs/swagger";

// ═══════════════════════════════════════════════════════════════════════════
// Product Review DTOs
// ═══════════════════════════════════════════════════════════════════════════

export class CreateProductReviewDto {
  @ApiProperty({ description: "Product ID", example: "prod-123" })
  @IsString()
  @IsNotEmpty()
  productId: string;

  @ApiProperty({ description: "Buyer profile ID", example: "buyer-123" })
  @IsString()
  @IsNotEmpty()
  buyerId: string;

  @ApiProperty({ description: "Order ID", example: "order-123" })
  @IsString()
  @IsNotEmpty()
  orderId: string;

  @ApiProperty({
    description: "Rating from 1 to 5 stars",
    minimum: 1,
    maximum: 5,
    example: 5,
  })
  @IsNumber()
  @Min(1)
  @Max(5)
  rating: number;

  @ApiProperty({ description: "Review title", example: "منتج ممتاز" })
  @IsString()
  @IsNotEmpty()
  title: string;

  @ApiPropertyOptional({
    description: "Review comment",
    example: "المنتج ذو جودة عالية وسعر مناسب",
  })
  @IsString()
  @IsOptional()
  comment?: string;

  @ApiPropertyOptional({
    description: "Array of photo URLs",
    example: [
      "https://example.com/photo1.jpg",
      "https://example.com/photo2.jpg",
    ],
  })
  @IsArray()
  @IsOptional()
  photos?: string[];
}

export class UpdateProductReviewDto {
  @ApiPropertyOptional({
    description: "Rating from 1 to 5 stars",
    minimum: 1,
    maximum: 5,
  })
  @IsNumber()
  @Min(1)
  @Max(5)
  @IsOptional()
  rating?: number;

  @ApiPropertyOptional({ description: "Review title" })
  @IsString()
  @IsOptional()
  title?: string;

  @ApiPropertyOptional({ description: "Review comment" })
  @IsString()
  @IsOptional()
  comment?: string;

  @ApiPropertyOptional({ description: "Array of photo URLs" })
  @IsArray()
  @IsOptional()
  photos?: string[];
}

export class MarkReviewHelpfulDto {
  @ApiProperty({ description: "Whether the review was helpful", example: true })
  @IsBoolean()
  helpful: boolean;
}

export class ReportReviewDto {
  @ApiProperty({
    description: "Reason for reporting",
    example: "Inappropriate content",
  })
  @IsString()
  @IsNotEmpty()
  reason: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Review Response DTOs
// ═══════════════════════════════════════════════════════════════════════════

export class CreateReviewResponseDto {
  @ApiProperty({ description: "Review ID", example: "review-123" })
  @IsString()
  @IsNotEmpty()
  reviewId: string;

  @ApiProperty({ description: "Seller profile ID", example: "seller-123" })
  @IsString()
  @IsNotEmpty()
  sellerId: string;

  @ApiProperty({
    description: "Response message",
    example: "شكراً لك على تقييمك الإيجابي",
  })
  @IsString()
  @IsNotEmpty()
  response: string;
}

export class UpdateReviewResponseDto {
  @ApiProperty({ description: "Updated response message" })
  @IsString()
  @IsNotEmpty()
  response: string;
}

// ═══════════════════════════════════════════════════════════════════════════
// Query Parameter DTOs
// ═══════════════════════════════════════════════════════════════════════════

export class GetProductReviewsQueryDto {
  @ApiPropertyOptional({
    description: "Filter by minimum rating",
    minimum: 1,
    maximum: 5,
    example: 3,
  })
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(5)
  @IsOptional()
  minRating?: number;

  @ApiPropertyOptional({
    description: "Filter by maximum rating",
    minimum: 1,
    maximum: 5,
    example: 5,
  })
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(5)
  @IsOptional()
  maxRating?: number;

  @ApiPropertyOptional({
    description: "Filter by verified purchases",
    example: true,
  })
  @Type(() => Boolean)
  @IsBoolean()
  @IsOptional()
  verified?: boolean;

  @ApiPropertyOptional({
    description: "Number of reviews to return",
    minimum: 1,
    maximum: 100,
    example: 20,
  })
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(100)
  @IsOptional()
  limit?: number;

  @ApiPropertyOptional({
    description: "Number of reviews to skip",
    minimum: 0,
    example: 0,
  })
  @Type(() => Number)
  @IsNumber()
  @Min(0)
  @IsOptional()
  offset?: number;
}

export class PaginationQueryDto {
  @ApiPropertyOptional({
    description: "Number of items to return",
    minimum: 1,
    maximum: 100,
    example: 20,
  })
  @Type(() => Number)
  @IsNumber()
  @Min(1)
  @Max(100)
  @IsOptional()
  limit?: number;

  @ApiPropertyOptional({
    description: "Number of items to skip",
    minimum: 0,
    example: 0,
  })
  @Type(() => Number)
  @IsNumber()
  @Min(0)
  @IsOptional()
  offset?: number;
}
