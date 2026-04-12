import { Module } from "@nestjs/common";
import { OidcModule } from "../oidc/oidc.module";
import { OAuthService } from "./oauth.service";
import { TokenController } from "./token.controller";
import {
  AuthorizeStubController,
  RevokeStubController,
  IntrospectStubController,
  UserinfoStubController,
} from "./stub.controllers";

@Module({
  imports: [OidcModule],
  controllers: [
    TokenController,
    AuthorizeStubController,
    RevokeStubController,
    IntrospectStubController,
    UserinfoStubController,
  ],
  providers: [OAuthService],
  exports: [OAuthService],
})
export class OAuthModule {}
