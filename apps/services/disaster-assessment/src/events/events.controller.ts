// ═══════════════════════════════════════════════════════════════════════════════
// Disaster Events Controller - مراقب أحداث الكوارث
// ═══════════════════════════════════════════════════════════════════════════════
//
// Exposes the frontend-expected /api/v1/disasters/events/* endpoints. All routes
// require a JWT and extract the tenant from the `tid` claim (via JwtAuthGuard →
// `req.user.tenantId`). The TenantGuard (registered globally) further enforces
// X-Tenant-ID consistency.
// ═══════════════════════════════════════════════════════════════════════════════

import {
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  ParseUUIDPipe,
  Post,
  Put,
  Query,
  Req,
  UseGuards,
} from "@nestjs/common";
import { ApiOperation, ApiResponse, ApiTags } from "@nestjs/swagger";
import { EventsService } from "./events.service";
import {
  CreateDisasterEventDto,
  ListEventsQueryDto,
  UpdateDisasterEventDto,
  UpdateEventStatusDto,
} from "./events.dto";
import { JwtAuthGuard } from "../auth/jwt-auth.guard";

@ApiTags("disaster-events")
@Controller("api/v1/disasters/events")
@UseGuards(JwtAuthGuard)
export class EventsController {
  constructor(private readonly events: EventsService) {}

  private tenantId(req: any): string {
    return (
      req.user?.tenantId ||
      req.tenantId ||
      req.headers["x-tenant-id"] ||
      "unassigned"
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GET /api/v1/disasters/events
  // ─────────────────────────────────────────────────────────────────────────

  @Get()
  @ApiOperation({
    summary: "List disaster events",
    description: "قائمة أحداث الكوارث",
  })
  @ApiResponse({ status: 200, description: "Paginated list of events" })
  async list(@Req() req: any, @Query() query: ListEventsQueryDto) {
    return this.events.listEvents(this.tenantId(req), query);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // POST /api/v1/disasters/events
  // ─────────────────────────────────────────────────────────────────────────

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: "Create disaster event",
    description: "إنشاء حدث كارثة",
  })
  @ApiResponse({ status: 201, description: "Event created" })
  async create(@Req() req: any, @Body() dto: CreateDisasterEventDto) {
    return this.events.createEvent(dto, this.tenantId(req));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // GET /api/v1/disasters/events/:id
  // ─────────────────────────────────────────────────────────────────────────

  @Get(":id")
  @ApiOperation({
    summary: "Get disaster event",
    description: "الحصول على حدث كارثة محدد",
  })
  @ApiResponse({ status: 200, description: "Event details" })
  @ApiResponse({ status: 404, description: "Event not found" })
  async get(@Req() req: any, @Param("id", new ParseUUIDPipe()) id: string) {
    return this.events.getEvent(id, this.tenantId(req));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // PUT /api/v1/disasters/events/:id
  // ─────────────────────────────────────────────────────────────────────────

  @Put(":id")
  @ApiOperation({
    summary: "Update disaster event",
    description: "تحديث حدث كارثة مع قفل متفائل",
  })
  @ApiResponse({ status: 200, description: "Event updated" })
  @ApiResponse({ status: 409, description: "Version conflict" })
  async update(
    @Req() req: any,
    @Param("id", new ParseUUIDPipe()) id: string,
    @Body() dto: UpdateDisasterEventDto,
  ) {
    return this.events.updateEvent(id, this.tenantId(req), dto);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // POST /api/v1/disasters/events/:id/status
  // ─────────────────────────────────────────────────────────────────────────

  @Post(":id/status")
  @ApiOperation({
    summary: "Update event status",
    description: "تحديث حالة الحدث",
  })
  @ApiResponse({ status: 200, description: "Status updated" })
  async updateStatus(
    @Req() req: any,
    @Param("id", new ParseUUIDPipe()) id: string,
    @Body() dto: UpdateEventStatusDto,
  ) {
    return this.events.updateStatus(id, this.tenantId(req), dto);
  }
}
