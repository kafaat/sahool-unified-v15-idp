import { Module } from "@nestjs/common";
import { DiscoveryController } from "./discovery.controller";
import { JwksController } from "./jwks.controller";
import { JwkService } from "./jwk.service";
import { IdTokenService } from "./id-token.service";

@Module({
  controllers: [DiscoveryController, JwksController],
  providers: [JwkService, IdTokenService],
  exports: [JwkService, IdTokenService],
})
export class OidcModule {}
