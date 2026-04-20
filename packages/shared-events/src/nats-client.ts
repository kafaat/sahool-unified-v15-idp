/**
 * SAHOOL Event Bus - NATS Client Singleton
 * Manages connection lifecycle with automatic reconnection
 */

import { connect, NatsConnection, ConnectionOptions, Events } from 'nats';

/**
 * Safely parse a NATS URL that may contain credentials.
 * Uses lastIndexOf('@') so passwords containing '@' are handled correctly.
 *
 * nats://user:p@ssword@host:4222  →  { serverUrl: 'nats://host:4222', user, pass }
 */
function parseNatsUrl(urlStr: string): { serverUrl: string; user?: string; pass?: string } {
  const atIdx = urlStr.lastIndexOf('@');
  if (atIdx === -1) return { serverUrl: urlStr };

  const schemeEnd = urlStr.indexOf('://');
  if (schemeEnd === -1) return { serverUrl: urlStr };

  const scheme = urlStr.slice(0, schemeEnd + 3);
  const userinfo = urlStr.slice(schemeEnd + 3, atIdx);
  const host = urlStr.slice(atIdx + 1);

  const colonIdx = userinfo.indexOf(':');
  if (colonIdx === -1) {
    return { serverUrl: `${scheme}${host}`, user: userinfo };
  }

  return {
    serverUrl: `${scheme}${host}`,
    user: userinfo.slice(0, colonIdx),
    pass: userinfo.slice(colonIdx + 1),
  };
}

export interface NatsClientConfig {
  servers: string | string[];
  name?: string;
  user?: string;
  pass?: string;
  maxReconnectAttempts?: number;
  reconnectTimeWait?: number;
  timeout?: number;
  debug?: boolean;
}

export class NatsClient {
  private static instance: NatsClient | null = null;
  private connection: NatsConnection | null = null;
  private config: NatsClientConfig;
  private isConnecting: boolean = false;
  private reconnectTimer: NodeJS.Timeout | null = null;

  private constructor(config: NatsClientConfig) {
    this.config = {
      maxReconnectAttempts: -1, // infinite reconnect
      reconnectTimeWait: 2000, // 2 seconds between attempts
      timeout: 10000, // 10 second connection timeout
      debug: false,
      ...config,
    };
  }

  /**
   * Get or create the singleton instance
   */
  public static getInstance(config?: NatsClientConfig): NatsClient {
    if (!NatsClient.instance) {
      if (!config) {
        throw new Error('NatsClient configuration is required for first initialization');
      }
      NatsClient.instance = new NatsClient(config);
    }
    return NatsClient.instance;
  }

  /**
   * Connect to NATS server
   */
  public async connect(): Promise<NatsConnection> {
    if (this.connection && !this.connection.isClosed()) {
      return this.connection;
    }

    if (this.isConnecting) {
      // Wait for ongoing connection attempt
      await this.waitForConnection();
      if (this.connection) {
        return this.connection;
      }
    }

    this.isConnecting = true;

    try {
      // Extract credentials from URL when the caller embeds them as
      // nats://user:pass@host:port.  Passwords containing '@' or '#' break
      // the URL constructor, so we parse manually with lastIndexOf('@').
      let servers = this.config.servers;
      let user = this.config.user;
      let pass = this.config.pass;
      if (!user && typeof servers === 'string') {
        const parsed = parseNatsUrl(servers);
        servers = parsed.serverUrl;
        user = parsed.user;
        pass = parsed.pass;
      }

      const connectionOptions: ConnectionOptions = {
        servers,
        name: this.config.name || 'sahool-service',
        user,
        pass,
        maxReconnectAttempts: this.config.maxReconnectAttempts,
        reconnectTimeWait: this.config.reconnectTimeWait,
        timeout: this.config.timeout,
        debug: this.config.debug,
      };

      this.log('Connecting to NATS server...');
      this.connection = await connect(connectionOptions);
      this.log('Successfully connected to NATS server');

      this.setupEventHandlers();
      this.isConnecting = false;

      return this.connection;
    } catch (error) {
      this.isConnecting = false;
      this.log('Failed to connect to NATS server:', error);

      // Schedule reconnection
      this.scheduleReconnect();

      throw error;
    }
  }

  /**
   * Get the current connection
   */
  public getConnection(): NatsConnection | null {
    return this.connection;
  }

  /**
   * Check if connected
   */
  public isConnected(): boolean {
    return this.connection !== null && !this.connection.isClosed();
  }

  /**
   * Disconnect from NATS server
   */
  public async disconnect(): Promise<void> {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.connection && !this.connection.isClosed()) {
      this.log('Disconnecting from NATS server...');
      await this.connection.drain();
      await this.connection.close();
      this.log('Disconnected from NATS server');
    }

    this.connection = null;
  }

  /**
   * Reset the singleton instance (useful for testing)
   */
  public static reset(): void {
    if (NatsClient.instance) {
      NatsClient.instance.disconnect().catch((err) => {
        console.error('Error during disconnect:', err);
      });
    }
    NatsClient.instance = null;
  }

  /**
   * Setup event handlers for connection lifecycle
   */
  private setupEventHandlers(): void {
    if (!this.connection) return;

    // Handle disconnect
    (async () => {
      for await (const status of this.connection!.status()) {
        const type = status.type;

        switch (type) {
          case Events.Disconnect:
            this.log('Disconnected from NATS server');
            break;

          case Events.Reconnect:
            this.log('Reconnected to NATS server');
            break;

          case Events.Update:
            this.log('NATS connection updated');
            break;

          case Events.LDM:
            this.log('NATS Lame Duck Mode activated');
            break;

          case Events.Error:
            this.log('NATS connection error:', status.data);
            break;
        }
      }
    })().catch((err) => {
      this.log('Error in status monitoring:', err);
    });
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    if (this.reconnectTimer) {
      return; // Already scheduled
    }

    this.log(`Scheduling reconnection in ${this.config.reconnectTimeWait}ms...`);

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect().catch((err) => {
        this.log('Reconnection failed:', err);
      });
    }, this.config.reconnectTimeWait);
  }

  /**
   * Wait for ongoing connection attempt
   */
  private async waitForConnection(maxWait: number = 30000): Promise<void> {
    const startTime = Date.now();

    while (this.isConnecting && Date.now() - startTime < maxWait) {
      await new Promise((resolve) => setTimeout(resolve, 100));
    }
  }

  /**
   * Log helper
   */
  private log(message: string, ...args: unknown[]): void {
    if (this.config.debug) {
      console.log(`[NatsClient] ${message}`, ...args);
    }
  }
}

/**
 * Helper function to initialize NATS client
 */
export async function initializeNatsClient(config?: NatsClientConfig): Promise<NatsConnection> {
  const defaultConfig: NatsClientConfig = {
    servers: process.env.NATS_URL || 'nats://localhost:4222',
    name: process.env.SERVICE_NAME || 'sahool-service',
    debug: process.env.NODE_ENV !== 'production',
  };

  const client = NatsClient.getInstance(config || defaultConfig);
  return await client.connect();
}

/**
 * Helper function to get current NATS connection
 */
export function getNatsConnection(): NatsConnection | null {
  const client = NatsClient.getInstance({
    servers: process.env.NATS_URL || 'nats://localhost:4222',
  });
  return client.getConnection();
}
