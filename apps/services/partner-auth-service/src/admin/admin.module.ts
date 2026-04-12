import { Module } from "@nestjs/common";
import { OidcModule } from "../oidc/oidc.module";
import { AdminGuard } from "./admin.guard";
import { ClientsController } from "./clients.controller";
import { ClientsService } from "./clients.service";
import { ConsentsController } from "./consents.controller";
import { TokensController } from "./tokens.controller";
import { SigningKeysController } from "./signing-keys.controller";

@Module({
  imports: [OidcModule],
  controllers: [
    ClientsController,
    ConsentsController,
    TokensController,
    SigningKeysController,
  ],
  providers: [AdminGuard, ClientsService],
  exports: [ClientsService],
})
export class AdminModule {}
