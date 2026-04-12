import { Module } from "@nestjs/common";
import { OidcModule } from "../oidc/oidc.module";
import { CsrfService } from "../utils/csrf.service";
import { OAuthService } from "./oauth.service";
import { AuthorizeService } from "./authorize.service";
import { TokenController } from "./token.controller";
import { AuthorizeController } from "./authorize.controller";
import { RevokeController } from "./revoke.controller";
import { IntrospectController } from "./introspect.controller";
import { UserinfoController } from "./userinfo.controller";
import { BearerAuthGuard } from "./bearer.guard";

@Module({
  imports: [OidcModule],
  controllers: [
    TokenController,
    AuthorizeController,
    RevokeController,
    IntrospectController,
    UserinfoController,
  ],
  providers: [OAuthService, AuthorizeService, CsrfService, BearerAuthGuard],
  exports: [OAuthService, AuthorizeService, BearerAuthGuard],
})
export class OAuthModule {}
