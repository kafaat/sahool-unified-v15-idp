/**
 * Admin controller for partner OAuth clients.
 * Route prefix: /api/v1/admin/partner-auth/clients
 *
 * All endpoints require an `Authorization: Bearer <jwt>` carrying role=ADMIN
 * (enforced by AdminGuard).
 */

import {
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  Param,
  Patch,
  Post,
  Query,
  Req,
  UseGuards,
} from "@nestjs/common";
import {
  ApiBearerAuth,
  ApiOperation,
  ApiResponse,
  ApiTags,
} from "@nestjs/swagger";
import type { Request } from "express";
import { AdminGuard } from "./admin.guard";
import { ClientsService } from "./clients.service";
import {
  CreateClientDto,
  UpdateClientDto,
  ListClientsQueryDto,
} from "./dto/create-client.dto";

@ApiTags("Admin — Partner Clients")
@ApiBearerAuth()
@UseGuards(AdminGuard)
@Controller("api/v1/admin/partner-auth/clients")
export class ClientsController {
  constructor(private readonly clients: ClientsService) {}

  @Post()
  @HttpCode(201)
  @ApiOperation({
    summary: "Register a new partner OAuth client",
    description:
      "Returns client_secret and partnerApiKey as plaintext EXACTLY ONCE. " +
      "Caller must capture and store them securely — they cannot be retrieved later.",
  })
  @ApiResponse({ status: 201, description: "Created" })
  async create(@Body() dto: CreateClientDto, @Req() req: Request) {
    return this.clients.create(dto, adminId(req));
  }

  @Get()
  @ApiOperation({ summary: "List partner clients (paginated)" })
  list(@Query() q: ListClientsQueryDto) {
    return this.clients.list(q);
  }

  @Get(":clientId")
  @ApiOperation({ summary: "Retrieve one partner client" })
  get(@Param("clientId") clientId: string) {
    return this.clients.get(clientId);
  }

  @Patch(":clientId")
  @ApiOperation({ summary: "Update partner client metadata" })
  update(
    @Param("clientId") clientId: string,
    @Body() dto: UpdateClientDto,
    @Req() req: Request,
  ) {
    return this.clients.update(clientId, dto, adminId(req));
  }

  @Post(":clientId/rotate-secret")
  @HttpCode(200)
  @ApiOperation({
    summary: "Rotate client_secret — returns new plaintext ONCE",
  })
  rotateSecret(@Param("clientId") clientId: string, @Req() req: Request) {
    return this.clients.rotateSecret(clientId, adminId(req));
  }

  @Post(":clientId/rotate-api-key")
  @HttpCode(200)
  @ApiOperation({
    summary: "Rotate X-Sahool-Partner-Key — returns new plaintext ONCE",
  })
  rotateApiKey(@Param("clientId") clientId: string, @Req() req: Request) {
    return this.clients.rotateApiKey(clientId, adminId(req));
  }

  @Post(":clientId/suspend")
  @HttpCode(200)
  @ApiOperation({ summary: "Suspend a client (blocks all flows)" })
  suspend(@Param("clientId") clientId: string, @Req() req: Request) {
    return this.clients.setStatus(clientId, "suspended", adminId(req));
  }

  @Post(":clientId/unsuspend")
  @HttpCode(200)
  @ApiOperation({ summary: "Reactivate a suspended client" })
  unsuspend(@Param("clientId") clientId: string, @Req() req: Request) {
    return this.clients.setStatus(clientId, "active", adminId(req));
  }

  @Delete(":clientId")
  @HttpCode(200)
  @ApiOperation({
    summary: "Permanently revoke a client (cascade-revokes all tokens)",
    description:
      "Sets status=revoked + revokes every outstanding access/refresh token and consent grant for this client. Irreversible.",
  })
  revoke(@Param("clientId") clientId: string, @Req() req: Request) {
    return this.clients.setStatus(clientId, "revoked", adminId(req));
  }
}

function adminId(req: Request): string {
  return req.adminPrincipal?.id ?? "unknown-admin";
}
