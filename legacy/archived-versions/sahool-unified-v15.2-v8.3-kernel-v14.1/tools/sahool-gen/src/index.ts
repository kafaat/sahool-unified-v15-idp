#!/usr/bin/env node

// ============================================
// SAHOOL-GEN CLI
// Code Generation & Automation Tool
// أداة توليد الكود والأتمتة لمنصة سهول
// ============================================

import { Command } from 'commander';
import * as fs from 'fs';
import * as path from 'path';
import chalk from 'chalk';
import inquirer from 'inquirer';
import { execSync } from 'child_process';

const VERSION = '1.0.0';
const SAHOOL_ROOT = process.env.SAHOOL_ROOT || path.resolve(__dirname, '../../..');

// ============================================
// LAYER DEFINITIONS
// ============================================

const LAYERS = {
  1: { name: 'Platform Core', path: 'platform-core', port: 3000 },
  2: { name: 'Signal Producers', path: 'signal-producers', port: 3010 },
  3: { name: 'Decision Services', path: 'decision-services', port: 3020 },
  4: { name: 'Execution Services', path: 'execution-services', port: 3030 }
};

// ============================================
// TEMPLATES
// ============================================

const TEMPLATES = {
  // TypeScript Service Index
  serviceIndex: (serviceName: string, port: number, layer: number) => `
// ============================================
// SAHOOL - ${toTitleCase(serviceName)} Service
// Layer ${layer}: ${LAYERS[layer as keyof typeof LAYERS].name}
// ============================================

import express, { Express, Request, Response } from 'express';
import { Pool } from 'pg';
import Redis from 'ioredis';
import amqp, { Channel, Connection } from 'amqplib';
import cors from 'cors';
import helmet from 'helmet';
import { createLogger, format, transports } from 'winston';

// ============================================
// CONFIGURATION
// ============================================

const config = {
  port: parseInt(process.env.PORT || '${port}'),
  serviceName: '${serviceName}',
  database: process.env.DATABASE_URL || 'postgresql://sahool:sahool_secret@localhost:5432/sahool_main',
  redis: process.env.REDIS_URL || 'redis://localhost:6379',
  rabbitmq: process.env.RABBITMQ_URL || 'amqp://localhost:5672',
};

// ============================================
// LOGGER
// ============================================

const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.json()
  ),
  defaultMeta: { service: config.serviceName },
  transports: [
    new transports.Console({
      format: format.combine(
        format.colorize(),
        format.simple()
      )
    })
  ]
});

// ============================================
// SERVICE CLASS
// ============================================

class ${toPascalCase(serviceName)}Service {
  private app: Express;
  private pool: Pool;
  private redis: Redis;
  private channel: Channel | null = null;
  private connection: Connection | null = null;

  constructor() {
    this.app = express();
    this.setupMiddleware();
    
    this.pool = new Pool({ connectionString: config.database });
    this.redis = new Redis(config.redis);
    
    this.setupRoutes();
  }

  // ============================================
  // MIDDLEWARE
  // ============================================

  private setupMiddleware(): void {
    this.app.use(helmet());
    this.app.use(cors());
    this.app.use(express.json());
    
    // Request logging
    this.app.use((req, res, next) => {
      logger.info(\`\${req.method} \${req.path}\`);
      next();
    });
  }

  // ============================================
  // ROUTES
  // ============================================

  private setupRoutes(): void {
    // Health check
    this.app.get('/health', (req: Request, res: Response) => {
      res.json({ 
        status: 'healthy', 
        service: config.serviceName,
        timestamp: new Date().toISOString()
      });
    });

    // Ready check
    this.app.get('/ready', async (req: Request, res: Response) => {
      try {
        await this.pool.query('SELECT 1');
        await this.redis.ping();
        res.json({ ready: true });
      } catch (error) {
        res.status(503).json({ ready: false, error: 'Dependencies not ready' });
      }
    });

    // TODO: Add your routes here
    this.app.get('/api/v1/${serviceName}', async (req: Request, res: Response) => {
      res.json({ success: true, message: '${toPascalCase(serviceName)} Service' });
    });
  }

  // ============================================
  // RABBITMQ
  // ============================================

  private async connectRabbitMQ(): Promise<void> {
    try {
      this.connection = await amqp.connect(config.rabbitmq);
      this.channel = await this.connection.createChannel();
      
      await this.channel.assertExchange('sahool.events', 'topic', { durable: true });
      
      logger.info('Connected to RabbitMQ');
    } catch (error) {
      logger.error('Failed to connect to RabbitMQ:', error);
      throw error;
    }
  }

  protected async publishEvent(routingKey: string, event: any): Promise<void> {
    if (!this.channel) {
      await this.connectRabbitMQ();
    }
    
    this.channel!.publish(
      'sahool.events',
      routingKey,
      Buffer.from(JSON.stringify(event)),
      { persistent: true }
    );
    
    logger.info(\`Published event: \${routingKey}\`);
  }

  protected async subscribeToEvents(queue: string, routingKey: string, handler: (msg: any) => Promise<void>): Promise<void> {
    if (!this.channel) {
      await this.connectRabbitMQ();
    }
    
    await this.channel!.assertQueue(queue, { durable: true });
    await this.channel!.bindQueue(queue, 'sahool.events', routingKey);
    
    this.channel!.consume(queue, async (msg) => {
      if (msg) {
        try {
          const content = JSON.parse(msg.content.toString());
          await handler(content);
          this.channel!.ack(msg);
        } catch (error) {
          logger.error('Error processing message:', error);
          this.channel!.nack(msg, false, false);
        }
      }
    });
    
    logger.info(\`Subscribed to: \${routingKey}\`);
  }

  // ============================================
  // LIFECYCLE
  // ============================================

  async start(): Promise<void> {
    try {
      await this.connectRabbitMQ();
      await this.initDatabase();
      
      this.app.listen(config.port, () => {
        logger.info(\`🚀 \${config.serviceName} running on port \${config.port}\`);
      });
    } catch (error) {
      logger.error('Failed to start service:', error);
      process.exit(1);
    }
  }

  private async initDatabase(): Promise<void> {
    // TODO: Add your database initialization here
    logger.info('Database initialized');
  }

  async shutdown(): Promise<void> {
    logger.info('Shutting down...');
    
    if (this.channel) await this.channel.close();
    if (this.connection) await this.connection.close();
    await this.pool.end();
    await this.redis.quit();
    
    logger.info('Shutdown complete');
  }
}

// ============================================
// GRACEFUL SHUTDOWN
// ============================================

const service = new ${toPascalCase(serviceName)}Service();

process.on('SIGTERM', async () => {
  await service.shutdown();
  process.exit(0);
});

process.on('SIGINT', async () => {
  await service.shutdown();
  process.exit(0);
});

// ============================================
// START
// ============================================

service.start();

export { ${toPascalCase(serviceName)}Service };
`,

  // Package.json template
  packageJson: (serviceName: string) => ({
    name: `@sahool/${serviceName}`,
    version: '1.0.0',
    private: true,
    main: 'dist/index.js',
    scripts: {
      'dev': 'tsx watch src/index.ts',
      'build': 'tsc',
      'start': 'node dist/index.js',
      'test': 'jest',
      'lint': 'eslint src/**/*.ts'
    },
    dependencies: {
      'express': '^4.18.2',
      'pg': '^8.11.3',
      'ioredis': '^5.3.2',
      'amqplib': '^0.10.3',
      'cors': '^2.8.5',
      'helmet': '^7.1.0',
      'winston': '^3.11.0',
      'uuid': '^9.0.0',
      'zod': '^3.22.4'
    },
    devDependencies: {
      '@types/express': '^4.17.21',
      '@types/node': '^20.10.0',
      '@types/amqplib': '^0.10.4',
      '@types/cors': '^2.8.17',
      '@types/uuid': '^9.0.7',
      'typescript': '^5.3.2',
      'tsx': '^4.6.2',
      'jest': '^29.7.0',
      '@types/jest': '^29.5.11',
      'eslint': '^8.55.0'
    }
  }),

  // Dockerfile template
  dockerfile: (serviceName: string) => `
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app
RUN addgroup -g 1001 -S nodejs && adduser -S sahool -u 1001

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./

USER sahool
EXPOSE 3000

CMD ["node", "dist/index.js"]
`,

  // tsconfig.json
  tsconfig: () => ({
    compilerOptions: {
      target: 'ES2022',
      module: 'commonjs',
      lib: ['ES2022'],
      outDir: './dist',
      rootDir: './src',
      strict: true,
      esModuleInterop: true,
      skipLibCheck: true,
      forceConsistentCasingInFileNames: true,
      resolveJsonModule: true,
      declaration: true,
      declarationMap: true,
      sourceMap: true
    },
    include: ['src/**/*'],
    exclude: ['node_modules', 'dist']
  }),

  // Flutter Feature Bloc
  flutterBloc: (featureName: string) => `
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

// ============================================
// ${toTitleCase(featureName)} Events
// ============================================

abstract class ${toPascalCase(featureName)}Event extends Equatable {
  const ${toPascalCase(featureName)}Event();

  @override
  List<Object?> get props => [];
}

class Load${toPascalCase(featureName)} extends ${toPascalCase(featureName)}Event {}

class Refresh${toPascalCase(featureName)} extends ${toPascalCase(featureName)}Event {}

// ============================================
// ${toTitleCase(featureName)} State
// ============================================

enum ${toPascalCase(featureName)}Status { initial, loading, success, failure }

class ${toPascalCase(featureName)}State extends Equatable {
  const ${toPascalCase(featureName)}State({
    this.status = ${toPascalCase(featureName)}Status.initial,
    this.data,
    this.errorMessage,
  });

  final ${toPascalCase(featureName)}Status status;
  final dynamic data;
  final String? errorMessage;

  ${toPascalCase(featureName)}State copyWith({
    ${toPascalCase(featureName)}Status? status,
    dynamic data,
    String? errorMessage,
  }) {
    return ${toPascalCase(featureName)}State(
      status: status ?? this.status,
      data: data ?? this.data,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }

  @override
  List<Object?> get props => [status, data, errorMessage];
}

// ============================================
// ${toTitleCase(featureName)} Bloc
// ============================================

class ${toPascalCase(featureName)}Bloc extends Bloc<${toPascalCase(featureName)}Event, ${toPascalCase(featureName)}State> {
  ${toPascalCase(featureName)}Bloc() : super(const ${toPascalCase(featureName)}State()) {
    on<Load${toPascalCase(featureName)}>(_onLoad);
    on<Refresh${toPascalCase(featureName)}>(_onRefresh);
  }

  Future<void> _onLoad(
    Load${toPascalCase(featureName)} event,
    Emitter<${toPascalCase(featureName)}State> emit,
  ) async {
    emit(state.copyWith(status: ${toPascalCase(featureName)}Status.loading));
    
    try {
      // TODO: Load data
      emit(state.copyWith(
        status: ${toPascalCase(featureName)}Status.success,
        data: null,
      ));
    } catch (e) {
      emit(state.copyWith(
        status: ${toPascalCase(featureName)}Status.failure,
        errorMessage: e.toString(),
      ));
    }
  }

  Future<void> _onRefresh(
    Refresh${toPascalCase(featureName)} event,
    Emitter<${toPascalCase(featureName)}State> emit,
  ) async {
    add(Load${toPascalCase(featureName)}());
  }
}
`,

  // Flutter Screen
  flutterScreen: (featureName: string) => `
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '${toSnakeCase(featureName)}_bloc.dart';

class ${toPascalCase(featureName)}Screen extends StatelessWidget {
  const ${toPascalCase(featureName)}Screen({super.key});

  static const routeName = '/${toSnakeCase(featureName)}';

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => ${toPascalCase(featureName)}Bloc()..add(Load${toPascalCase(featureName)}()),
      child: const ${toPascalCase(featureName)}View(),
    );
  }
}

class ${toPascalCase(featureName)}View extends StatelessWidget {
  const ${toPascalCase(featureName)}View({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('${toTitleCase(featureName)}'),
      ),
      body: BlocBuilder<${toPascalCase(featureName)}Bloc, ${toPascalCase(featureName)}State>(
        builder: (context, state) {
          switch (state.status) {
            case ${toPascalCase(featureName)}Status.initial:
            case ${toPascalCase(featureName)}Status.loading:
              return const Center(child: CircularProgressIndicator());
            case ${toPascalCase(featureName)}Status.failure:
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text('Error: \${state.errorMessage}'),
                    ElevatedButton(
                      onPressed: () => context.read<${toPascalCase(featureName)}Bloc>().add(Refresh${toPascalCase(featureName)}()),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              );
            case ${toPascalCase(featureName)}Status.success:
              return RefreshIndicator(
                onRefresh: () async {
                  context.read<${toPascalCase(featureName)}Bloc>().add(Refresh${toPascalCase(featureName)}());
                },
                child: ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    // TODO: Build your UI here
                    const Text('${toPascalCase(featureName)} content'),
                  ],
                ),
              );
          }
        },
      ),
    );
  }
}
`
};

// ============================================
// UTILITY FUNCTIONS
// ============================================

function toPascalCase(str: string): string {
  return str
    .split(/[-_]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join('');
}

function toSnakeCase(str: string): string {
  return str.replace(/([A-Z])/g, '_$1').toLowerCase().replace(/^_/, '').replace(/-/g, '_');
}

function toTitleCase(str: string): string {
  return str
    .split(/[-_]/)
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

// ============================================
// CLI COMMANDS
// ============================================

const program = new Command();

program
  .name('sahool-gen')
  .description('SAHOOL Platform Code Generator')
  .version(VERSION);

// Service Command
program
  .command('service')
  .description('Create a new microservice')
  .argument('<action>', 'Action: create, list')
  .argument('[name]', 'Service name')
  .option('-l, --layer <number>', 'Layer number (1-4)', '2')
  .option('-p, --port <number>', 'Port number')
  .action(async (action: string, name: string, options: any) => {
    if (action === 'create') {
      if (!name) {
        console.error(chalk.red('Service name is required'));
        process.exit(1);
      }
      await createService(name, parseInt(options.layer), options.port ? parseInt(options.port) : undefined);
    } else if (action === 'list') {
      listServices();
    }
  });

// Mobile Feature Command
program
  .command('mobile')
  .description('Create a Flutter mobile feature')
  .argument('<action>', 'Action: feature')
  .argument('[name]', 'Feature name')
  .option('--with-bloc', 'Include BLoC pattern')
  .option('--with-offline', 'Include offline support')
  .action(async (action: string, name: string, options: any) => {
    if (action === 'feature' && name) {
      await createMobileFeature(name, options);
    }
  });

// API Command
program
  .command('api')
  .description('Generate API endpoints')
  .argument('<action>', 'Action: create')
  .argument('[service]', 'Service name')
  .option('-e, --endpoints <endpoints>', 'Comma-separated endpoint names')
  .action(async (action: string, service: string, options: any) => {
    if (action === 'create' && service && options.endpoints) {
      await generateApiEndpoints(service, options.endpoints.split(','));
    }
  });

// Event Command
program
  .command('event')
  .description('Generate event handlers')
  .argument('<action>', 'Action: create')
  .argument('[service]', 'Service name')
  .option('-e, --events <events>', 'Comma-separated event names')
  .action(async (action: string, service: string, options: any) => {
    if (action === 'create' && service && options.events) {
      await generateEventHandlers(service, options.events.split(','));
    }
  });

// Init Command
program
  .command('init')
  .description('Initialize SAHOOL development environment')
  .action(async () => {
    await initEnvironment();
  });

// ============================================
// COMMAND IMPLEMENTATIONS
// ============================================

async function createService(name: string, layer: number, port?: number): Promise<void> {
  console.log(chalk.blue(`\n🚀 Creating service: ${name} (Layer ${layer})\n`));

  const layerInfo = LAYERS[layer as keyof typeof LAYERS];
  if (!layerInfo) {
    console.error(chalk.red('Invalid layer. Use 1-4.'));
    process.exit(1);
  }

  const servicePath = path.join(SAHOOL_ROOT, layerInfo.path, name);
  const servicePort = port || (layerInfo.port + Math.floor(Math.random() * 10));

  // Create directories
  const dirs = ['src', 'src/routes', 'src/services', 'src/models', 'tests'];
  for (const dir of dirs) {
    fs.mkdirSync(path.join(servicePath, dir), { recursive: true });
  }

  // Create files
  fs.writeFileSync(
    path.join(servicePath, 'src', 'index.ts'),
    TEMPLATES.serviceIndex(name, servicePort, layer)
  );

  fs.writeFileSync(
    path.join(servicePath, 'package.json'),
    JSON.stringify(TEMPLATES.packageJson(name), null, 2)
  );

  fs.writeFileSync(
    path.join(servicePath, 'Dockerfile'),
    TEMPLATES.dockerfile(name)
  );

  fs.writeFileSync(
    path.join(servicePath, 'tsconfig.json'),
    JSON.stringify(TEMPLATES.tsconfig(), null, 2)
  );

  // Create .env.example
  fs.writeFileSync(path.join(servicePath, '.env.example'), `
PORT=${servicePort}
NODE_ENV=development
DATABASE_URL=postgresql://sahool:sahool_secret@localhost:5432/sahool_main
REDIS_URL=redis://localhost:6379
RABBITMQ_URL=amqp://localhost:5672
`);

  console.log(chalk.green(`✅ Service created at: ${servicePath}`));
  console.log(chalk.yellow(`\nNext steps:`));
  console.log(`  cd ${servicePath}`);
  console.log(`  npm install`);
  console.log(`  npm run dev`);
}

function listServices(): void {
  console.log(chalk.blue('\n📋 SAHOOL Services\n'));

  for (const [layer, info] of Object.entries(LAYERS)) {
    const layerPath = path.join(SAHOOL_ROOT, info.path);
    console.log(chalk.yellow(`Layer ${layer}: ${info.name}`));

    if (fs.existsSync(layerPath)) {
      const services = fs.readdirSync(layerPath).filter(f => {
        return fs.statSync(path.join(layerPath, f)).isDirectory();
      });

      services.forEach(s => console.log(`  - ${s}`));
    }
    console.log();
  }
}

async function createMobileFeature(name: string, options: any): Promise<void> {
  console.log(chalk.blue(`\n📱 Creating mobile feature: ${name}\n`));

  const featurePath = path.join(SAHOOL_ROOT, 'mobile', 'lib', 'features', toSnakeCase(name));

  // Create directories
  const dirs = ['presentation', 'presentation/bloc', 'presentation/screens', 'presentation/widgets', 'data', 'domain'];
  for (const dir of dirs) {
    fs.mkdirSync(path.join(featurePath, dir), { recursive: true });
  }

  if (options.withBloc) {
    fs.writeFileSync(
      path.join(featurePath, 'presentation', 'bloc', `${toSnakeCase(name)}_bloc.dart`),
      TEMPLATES.flutterBloc(name)
    );
  }

  fs.writeFileSync(
    path.join(featurePath, 'presentation', 'screens', `${toSnakeCase(name)}_screen.dart`),
    TEMPLATES.flutterScreen(name)
  );

  console.log(chalk.green(`✅ Feature created at: ${featurePath}`));
}

async function generateApiEndpoints(service: string, endpoints: string[]): Promise<void> {
  console.log(chalk.blue(`\n🔌 Generating API endpoints for: ${service}\n`));

  const routeContent = endpoints.map(endpoint => `
// ${toTitleCase(endpoint)} routes
router.get('/${endpoint}', async (req, res) => {
  // TODO: Implement get all ${endpoint}
  res.json({ success: true, data: [] });
});

router.get('/${endpoint}/:id', async (req, res) => {
  // TODO: Implement get ${endpoint} by id
  res.json({ success: true, data: null });
});

router.post('/${endpoint}', async (req, res) => {
  // TODO: Implement create ${endpoint}
  res.status(201).json({ success: true, data: req.body });
});

router.put('/${endpoint}/:id', async (req, res) => {
  // TODO: Implement update ${endpoint}
  res.json({ success: true, data: req.body });
});

router.delete('/${endpoint}/:id', async (req, res) => {
  // TODO: Implement delete ${endpoint}
  res.status(204).send();
});
`).join('\n');

  console.log(chalk.green('✅ API endpoints generated'));
  console.log(chalk.gray(routeContent));
}

async function generateEventHandlers(service: string, events: string[]): Promise<void> {
  console.log(chalk.blue(`\n📡 Generating event handlers for: ${service}\n`));

  const handlers = events.map(event => `
// Handle ${event}
async function handle${toPascalCase(event)}(payload: any): Promise<void> {
  console.log('Handling ${event}:', payload);
  // TODO: Implement handler
}
`).join('\n');

  console.log(chalk.green('✅ Event handlers generated'));
  console.log(chalk.gray(handlers));
}

async function initEnvironment(): Promise<void> {
  console.log(chalk.blue('\n🔧 Initializing SAHOOL development environment\n'));

  // Generate RSA keys
  const keysPath = path.join(SAHOOL_ROOT, 'infrastructure', 'docker', 'keys');
  fs.mkdirSync(keysPath, { recursive: true });

  console.log('Generating RSA keys...');
  try {
    execSync(`openssl genrsa -out ${keysPath}/private.pem 2048`, { stdio: 'inherit' });
    execSync(`openssl rsa -in ${keysPath}/private.pem -pubout -out ${keysPath}/public.pem`, { stdio: 'inherit' });
    console.log(chalk.green('✅ RSA keys generated'));
  } catch (error) {
    console.log(chalk.yellow('⚠️ OpenSSL not found. Please generate keys manually.'));
  }

  // Create .env file
  const envContent = `
# SAHOOL Platform Environment
NODE_ENV=development

# Database
DB_PASSWORD=sahool_secret

# Redis
REDIS_PASSWORD=redis_secret

# RabbitMQ
RABBITMQ_PASSWORD=rabbitmq_secret

# MinIO
MINIO_USER=sahool_minio
MINIO_PASSWORD=minio_secret

# External APIs
OPENWEATHER_API_KEY=your_key_here
SENTINEL_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Notifications
FCM_KEY=your_key_here
TWILIO_SID=your_sid_here
TWILIO_TOKEN=your_token_here

# Monitoring
GRAFANA_PASSWORD=admin
`;

  fs.writeFileSync(path.join(SAHOOL_ROOT, '.env'), envContent);
  console.log(chalk.green('✅ .env file created'));

  console.log(chalk.green('\n✅ Environment initialized successfully!'));
  console.log(chalk.yellow('\nNext steps:'));
  console.log('  1. Update .env with your actual API keys');
  console.log('  2. Run: docker-compose -f infrastructure/docker/docker-compose.yml up -d');
  console.log('  3. Run: sahool-gen service create <name> --layer <1-4>');
}

// ============================================
// RUN CLI
// ============================================

program.parse();
