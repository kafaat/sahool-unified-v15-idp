/**
 * NestJS Service with Request Logging Middleware
 * Example demonstrating how to integrate request logging into a NestJS service.
 */

import { NestFactory } from '@nestjs/core';
import {
  Module,
  Controller,
  Get,
  Post,
  Body,
  Param,
  Req,
  Injectable,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { APP_INTERCEPTOR } from '@nestjs/core';
import { Request } from 'express';

// Import request logging middleware
import {
  RequestLoggingInterceptor,
  getCorrelationId,
  getRequestContext,
  StructuredLogger,
} from '../request-logging';

// ─────────────────────────────────────────────────────────────────────────────
// DTOs (Data Transfer Objects)
// ─────────────────────────────────────────────────────────────────────────────

interface CreateConversationDto {
  buyer_id: string;
  seller_id: string;
  product_id: string;
}

interface ConversationResponse {
  id: string;
  buyer_id: string;
  seller_id: string;
  product_id: string;
  tenant_id: string;
  correlation_id: string;
}

// ─────────────────────────────────────────────────────────────────────────────
// Service Layer
// ─────────────────────────────────────────────────────────────────────────────

@Injectable()
class ConversationService {
  private readonly logger = new StructuredLogger('chat-service', 'ConversationService');

  /**
   * Find all conversations for a tenant
   */
  async findAll(tenantId: string, correlationId: string): Promise<any[]> {
    this.logger.log('Fetching conversations', {
      correlationId,
      tenantId,
      operation: 'findAll',
    });

    // Simulate database query
    const conversations = [
      {
        id: 'conv-1',
        buyer_id: 'buyer-1',
        seller_id: 'seller-1',
        product_id: 'product-1',
        tenant_id: tenantId,
      },
      {
        id: 'conv-2',
        buyer_id: 'buyer-2',
        seller_id: 'seller-2',
        product_id: 'product-2',
        tenant_id: tenantId,
      },
    ];

    this.logger.log('Conversations fetched', {
      correlationId,
      tenantId,
      operation: 'findAll',
      count: conversations.length,
    });

    return conversations;
  }

  /**
   * Create a new conversation
   */
  async create(
    dto: CreateConversationDto,
    tenantId: string,
    correlationId: string,
  ): Promise<any> {
    this.logger.log('Creating conversation', {
      correlationId,
      tenantId,
      operation: 'create',
      buyerId: dto.buyer_id,
      sellerId: dto.seller_id,
    });

    try {
      // Simulate conversation creation
      const conversation = {
        id: 'conv-new',
        ...dto,
        tenant_id: tenantId,
        created_at: new Date().toISOString(),
      };

      this.logger.log('Conversation created', {
        correlationId,
        tenantId,
        operation: 'create',
        conversationId: conversation.id,
      });

      return conversation;
    } catch (error) {
      this.logger.error('Failed to create conversation', {
        correlationId,
        tenantId,
        operation: 'create',
        error: error.message,
      });
      throw error;
    }
  }

  /**
   * Find conversation by ID
   */
  async findOne(id: string, tenantId: string, correlationId: string): Promise<any> {
    this.logger.log('Fetching conversation', {
      correlationId,
      tenantId,
      operation: 'findOne',
      conversationId: id,
    });

    // Simulate database lookup
    if (id === 'conv-404') {
      this.logger.warn('Conversation not found', {
        correlationId,
        tenantId,
        operation: 'findOne',
        conversationId: id,
      });

      throw new HttpException('Conversation not found', HttpStatus.NOT_FOUND);
    }

    return {
      id,
      buyer_id: 'buyer-1',
      seller_id: 'seller-1',
      product_id: 'product-1',
      tenant_id: tenantId,
    };
  }

  /**
   * Call external service with correlation ID propagation
   */
  async callExternalService(correlationId: string, tenantId: string): Promise<any> {
    this.logger.log('Calling external service', {
      correlationId,
      tenantId,
      operation: 'callExternalService',
      targetService: 'marketplace-service',
    });

    try {
      // Example using fetch or axios
      const response = await fetch('http://marketplace-service:8080/api/v1/products', {
        headers: {
          'X-Correlation-ID': correlationId,
          'X-Tenant-ID': tenantId,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();

      this.logger.log('External service call succeeded', {
        correlationId,
        tenantId,
        operation: 'callExternalService',
        targetService: 'marketplace-service',
      });

      return data;
    } catch (error) {
      this.logger.error('External service call failed', {
        correlationId,
        tenantId,
        operation: 'callExternalService',
        targetService: 'marketplace-service',
        error: error.message,
      });

      throw new HttpException(
        'External service unavailable',
        HttpStatus.SERVICE_UNAVAILABLE,
      );
    }
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Controller Layer
// ─────────────────────────────────────────────────────────────────────────────

@Controller('api/v1/conversations')
class ConversationController {
  constructor(private readonly conversationService: ConversationService) {}

  /**
   * List all conversations
   *
   * Demonstrates:
   * - Automatic request/response logging
   * - Correlation ID extraction
   * - Tenant context extraction
   */
  @Get()
  async findAll(@Req() request: Request) {
    const correlationId = getCorrelationId(request);
    const { tenantId } = getRequestContext(request);

    const conversations = await this.conversationService.findAll(
      tenantId || 'unknown',
      correlationId,
    );

    return {
      conversations,
      total: conversations.length,
      correlation_id: correlationId,
    };
  }

  /**
   * Create a new conversation
   *
   * Demonstrates:
   * - Request body logging (if enabled)
   * - Correlation ID in response
   * - Tenant isolation
   */
  @Post()
  async create(
    @Body() dto: CreateConversationDto,
    @Req() request: Request,
  ): Promise<ConversationResponse> {
    const correlationId = getCorrelationId(request);
    const { tenantId } = getRequestContext(request);

    const conversation = await this.conversationService.create(
      dto,
      tenantId || 'unknown',
      correlationId,
    );

    return {
      ...conversation,
      correlation_id: correlationId,
    };
  }

  /**
   * Get a specific conversation by ID
   *
   * Demonstrates:
   * - Path parameter handling
   * - Error logging (when conversation not found)
   */
  @Get(':id')
  async findOne(@Param('id') id: string, @Req() request: Request) {
    const correlationId = getCorrelationId(request);
    const { tenantId } = getRequestContext(request);

    const conversation = await this.conversationService.findOne(
      id,
      tenantId || 'unknown',
      correlationId,
    );

    return {
      ...conversation,
      correlation_id: correlationId,
    };
  }

  /**
   * Example of calling another service with correlation ID propagation
   *
   * Demonstrates:
   * - Correlation ID propagation to downstream services
   * - Service-to-service communication tracing
   */
  @Get('external/products')
  async getExternalProducts(@Req() request: Request) {
    const correlationId = getCorrelationId(request);
    const { tenantId } = getRequestContext(request);

    const products = await this.conversationService.callExternalService(
      correlationId,
      tenantId || 'unknown',
    );

    return {
      correlation_id: correlationId,
      products,
    };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Health Check Controller
// ─────────────────────────────────────────────────────────────────────────────

@Controller('healthz')
class HealthController {
  @Get()
  check() {
    return { status: 'ok', service: 'chat-service' };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Application Module
// ─────────────────────────────────────────────────────────────────────────────

@Module({
  controllers: [ConversationController, HealthController],
  providers: [
    ConversationService,
    {
      provide: APP_INTERCEPTOR,
      useValue: new RequestLoggingInterceptor('chat-service'),
    },
  ],
})
class AppModule {}

// ─────────────────────────────────────────────────────────────────────────────
// Bootstrap Application
// ─────────────────────────────────────────────────────────────────────────────

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable CORS
  app.enableCors({
    origin: ['http://localhost:3000', 'https://app.sahool.com'],
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Tenant-ID', 'X-Correlation-ID'],
    credentials: true,
  });

  // Global prefix
  app.setGlobalPrefix('api/v1');

  const port = process.env.PORT || 8114;
  await app.listen(port);

  console.log(`
  ╔═══════════════════════════════════════════════════════════════╗
  ║   💬 Chat Service with Request Logging                        ║
  ╠═══════════════════════════════════════════════════════════════╣
  ║   Server running on: http://localhost:${port}                   ║
  ║   Health Check: http://localhost:${port}/healthz              ║
  ╚═══════════════════════════════════════════════════════════════╝
  `);
}

bootstrap();

export { AppModule, ConversationController, ConversationService };
