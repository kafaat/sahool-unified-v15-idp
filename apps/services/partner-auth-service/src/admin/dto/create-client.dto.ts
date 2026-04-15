/**
 * DTOs for partner client registration / update.
 * class-validator decorators enforce input shape at the controller boundary.
 */

import {
  ArrayMaxSize,
  ArrayMinSize,
  ArrayUnique,
  IsArray,
  IsEmail,
  IsEnum,
  IsNotEmpty,
  IsOptional,
  IsString,
  IsUrl,
  Length,
  Matches,
} from "class-validator";

const HTTPS_URL_OPTS = { require_tld: false, require_protocol: true, protocols: ["http", "https"] };

export class CreateClientDto {
  /** Human-readable partner name (shown on consent screen) */
  @IsString()
  @IsNotEmpty()
  @Length(2, 255)
  name!: string;

  @IsOptional()
  @IsString()
  @Length(2, 255)
  nameAr?: string;

  @IsOptional()
  @IsString()
  @Length(0, 2000)
  description?: string;

  @IsOptional()
  @IsUrl(HTTPS_URL_OPTS)
  homepageUrl?: string;

  @IsOptional()
  @IsUrl(HTTPS_URL_OPTS)
  logoUrl?: string;

  /** Allowed redirect URIs for the authorization_code flow (exact match on /authorize) */
  @IsArray()
  @ArrayMinSize(1)
  @ArrayMaxSize(20)
  @ArrayUnique()
  @IsUrl(HTTPS_URL_OPTS, { each: true })
  redirectUris!: string[];

  /** Scopes this partner may request. Subset of PARTNER_OAUTH_SCOPES — enforced by service */
  @IsArray()
  @ArrayMinSize(1)
  @ArrayMaxSize(50)
  @ArrayUnique()
  @IsString({ each: true })
  @Matches(/^[a-z][a-z0-9_:]*$/, {
    each: true,
    message: "Each scope must match /^[a-z][a-z0-9_:]*$/",
  })
  allowedScopes!: string[];

  /** Rate/throttle tier — maps to a Kong rate-limit plan */
  @IsOptional()
  @IsEnum(["starter", "pro", "enterprise"])
  rateTier?: "starter" | "pro" | "enterprise";

  /** Security contact email for token-rotation + breach notifications */
  @IsOptional()
  @IsEmail()
  contactEmail?: string;
}

export class UpdateClientDto {
  @IsOptional() @IsString() @Length(2, 255)
  name?: string;

  @IsOptional() @IsString() @Length(2, 255)
  nameAr?: string;

  @IsOptional() @IsString() @Length(0, 2000)
  description?: string;

  @IsOptional() @IsUrl(HTTPS_URL_OPTS)
  homepageUrl?: string;

  @IsOptional() @IsUrl(HTTPS_URL_OPTS)
  logoUrl?: string;

  @IsOptional()
  @IsArray() @ArrayMinSize(1) @ArrayMaxSize(20) @ArrayUnique()
  @IsUrl(HTTPS_URL_OPTS, { each: true })
  redirectUris?: string[];

  @IsOptional()
  @IsArray() @ArrayMinSize(1) @ArrayMaxSize(50) @ArrayUnique()
  @IsString({ each: true })
  @Matches(/^[a-z][a-z0-9_:]*$/, { each: true })
  allowedScopes?: string[];

  @IsOptional()
  @IsEnum(["starter", "pro", "enterprise"])
  rateTier?: "starter" | "pro" | "enterprise";

  @IsOptional() @IsEmail()
  contactEmail?: string;
}

export class ListClientsQueryDto {
  @IsOptional()
  @IsEnum(["active", "suspended", "revoked"])
  status?: "active" | "suspended" | "revoked";

  @IsOptional()
  @IsString()
  /** Substring search on name (case-insensitive) */
  name?: string;

  @IsOptional()
  @Matches(/^\d+$/)
  limit?: string;

  @IsOptional()
  @Matches(/^\d+$/)
  offset?: string;
}
