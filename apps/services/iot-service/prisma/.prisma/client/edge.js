
Object.defineProperty(exports, "__esModule", { value: true });

const {
  PrismaClientKnownRequestError,
  PrismaClientUnknownRequestError,
  PrismaClientRustPanicError,
  PrismaClientInitializationError,
  PrismaClientValidationError,
  NotFoundError,
  getPrismaClient,
  sqltag,
  empty,
  join,
  raw,
  skip,
  Decimal,
  Debug,
  objectEnumValues,
  makeStrictEnum,
  Extensions,
  warnOnce,
  defineDmmfProperty,
  Public,
  getRuntime
} = require('./runtime/edge.js')


const Prisma = {}

exports.Prisma = Prisma
exports.$Enums = {}

/**
 * Prisma Client JS version: 5.22.0
 * Query Engine version: 605197351a3c8bdd595af2d2a9bc3025bca48ea2
 */
Prisma.prismaVersion = {
  client: "5.22.0",
  engine: "605197351a3c8bdd595af2d2a9bc3025bca48ea2"
}

Prisma.PrismaClientKnownRequestError = PrismaClientKnownRequestError;
Prisma.PrismaClientUnknownRequestError = PrismaClientUnknownRequestError
Prisma.PrismaClientRustPanicError = PrismaClientRustPanicError
Prisma.PrismaClientInitializationError = PrismaClientInitializationError
Prisma.PrismaClientValidationError = PrismaClientValidationError
Prisma.NotFoundError = NotFoundError
Prisma.Decimal = Decimal

/**
 * Re-export of sql-template-tag
 */
Prisma.sql = sqltag
Prisma.empty = empty
Prisma.join = join
Prisma.raw = raw
Prisma.validator = Public.validator

/**
* Extensions
*/
Prisma.getExtensionContext = Extensions.getExtensionContext
Prisma.defineExtension = Extensions.defineExtension

/**
 * Shorthand utilities for JSON filtering
 */
Prisma.DbNull = objectEnumValues.instances.DbNull
Prisma.JsonNull = objectEnumValues.instances.JsonNull
Prisma.AnyNull = objectEnumValues.instances.AnyNull

Prisma.NullTypes = {
  DbNull: objectEnumValues.classes.DbNull,
  JsonNull: objectEnumValues.classes.JsonNull,
  AnyNull: objectEnumValues.classes.AnyNull
}





/**
 * Enums
 */
exports.Prisma.TransactionIsolationLevel = makeStrictEnum({
  ReadUncommitted: 'ReadUncommitted',
  ReadCommitted: 'ReadCommitted',
  RepeatableRead: 'RepeatableRead',
  Serializable: 'Serializable'
});

exports.Prisma.DeviceScalarFieldEnum = {
  id: 'id',
  tenantId: 'tenantId',
  deviceId: 'deviceId',
  name: 'name',
  type: 'type',
  status: 'status',
  lastSeen: 'lastSeen',
  metadata: 'metadata',
  fieldId: 'fieldId',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.SensorScalarFieldEnum = {
  id: 'id',
  deviceId: 'deviceId',
  sensorType: 'sensorType',
  unit: 'unit',
  calibrationData: 'calibrationData',
  lastReading: 'lastReading',
  lastReadingAt: 'lastReadingAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.SensorReadingScalarFieldEnum = {
  id: 'id',
  sensorId: 'sensorId',
  deviceId: 'deviceId',
  value: 'value',
  unit: 'unit',
  timestamp: 'timestamp',
  quality: 'quality',
  metadata: 'metadata'
};

exports.Prisma.ActuatorScalarFieldEnum = {
  id: 'id',
  deviceId: 'deviceId',
  actuatorType: 'actuatorType',
  name: 'name',
  currentState: 'currentState',
  lastCommand: 'lastCommand',
  lastCommandAt: 'lastCommandAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ActuatorCommandScalarFieldEnum = {
  id: 'id',
  actuatorId: 'actuatorId',
  command: 'command',
  parameters: 'parameters',
  status: 'status',
  requestedAt: 'requestedAt',
  executedAt: 'executedAt',
  completedAt: 'completedAt',
  errorMessage: 'errorMessage',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.DeviceAlertScalarFieldEnum = {
  id: 'id',
  deviceId: 'deviceId',
  tenantId: 'tenantId',
  alertType: 'alertType',
  severity: 'severity',
  message: 'message',
  acknowledged: 'acknowledged',
  acknowledgedBy: 'acknowledgedBy',
  acknowledgedAt: 'acknowledgedAt',
  resolvedAt: 'resolvedAt',
  metadata: 'metadata',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.SortOrder = {
  asc: 'asc',
  desc: 'desc'
};

exports.Prisma.NullableJsonNullValueInput = {
  DbNull: Prisma.DbNull,
  JsonNull: Prisma.JsonNull
};

exports.Prisma.QueryMode = {
  default: 'default',
  insensitive: 'insensitive'
};

exports.Prisma.JsonNullValueFilter = {
  DbNull: Prisma.DbNull,
  JsonNull: Prisma.JsonNull,
  AnyNull: Prisma.AnyNull
};

exports.Prisma.NullsOrder = {
  first: 'first',
  last: 'last'
};
exports.DeviceType = exports.$Enums.DeviceType = {
  SOIL_MOISTURE_SENSOR: 'SOIL_MOISTURE_SENSOR',
  TEMPERATURE_SENSOR: 'TEMPERATURE_SENSOR',
  HUMIDITY_SENSOR: 'HUMIDITY_SENSOR',
  WATER_FLOW_METER: 'WATER_FLOW_METER',
  WEATHER_STATION: 'WEATHER_STATION',
  VALVE_CONTROLLER: 'VALVE_CONTROLLER',
  PUMP_CONTROLLER: 'PUMP_CONTROLLER',
  IRRIGATION_CONTROLLER: 'IRRIGATION_CONTROLLER',
  CAMERA: 'CAMERA',
  GATEWAY: 'GATEWAY',
  CUSTOM: 'CUSTOM'
};

exports.DeviceStatus = exports.$Enums.DeviceStatus = {
  ONLINE: 'ONLINE',
  OFFLINE: 'OFFLINE',
  MAINTENANCE: 'MAINTENANCE',
  ERROR: 'ERROR',
  INACTIVE: 'INACTIVE'
};

exports.SensorType = exports.$Enums.SensorType = {
  SOIL_MOISTURE: 'SOIL_MOISTURE',
  SOIL_TEMPERATURE: 'SOIL_TEMPERATURE',
  AIR_TEMPERATURE: 'AIR_TEMPERATURE',
  AIR_HUMIDITY: 'AIR_HUMIDITY',
  LIGHT_INTENSITY: 'LIGHT_INTENSITY',
  WATER_FLOW: 'WATER_FLOW',
  WATER_PRESSURE: 'WATER_PRESSURE',
  WATER_LEVEL: 'WATER_LEVEL',
  PH_LEVEL: 'PH_LEVEL',
  EC_LEVEL: 'EC_LEVEL',
  BATTERY_LEVEL: 'BATTERY_LEVEL',
  SIGNAL_STRENGTH: 'SIGNAL_STRENGTH',
  RAINFALL: 'RAINFALL',
  WIND_SPEED: 'WIND_SPEED',
  WIND_DIRECTION: 'WIND_DIRECTION',
  CUSTOM: 'CUSTOM'
};

exports.ActuatorType = exports.$Enums.ActuatorType = {
  VALVE: 'VALVE',
  PUMP: 'PUMP',
  MOTOR: 'MOTOR',
  RELAY: 'RELAY',
  SWITCH: 'SWITCH',
  SERVO: 'SERVO',
  CUSTOM: 'CUSTOM'
};

exports.CommandStatus = exports.$Enums.CommandStatus = {
  PENDING: 'PENDING',
  EXECUTING: 'EXECUTING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  TIMEOUT: 'TIMEOUT',
  CANCELLED: 'CANCELLED'
};

exports.AlertSeverity = exports.$Enums.AlertSeverity = {
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL'
};

exports.Prisma.ModelName = {
  Device: 'Device',
  Sensor: 'Sensor',
  SensorReading: 'SensorReading',
  Actuator: 'Actuator',
  ActuatorCommand: 'ActuatorCommand',
  DeviceAlert: 'DeviceAlert'
};
/**
 * Create the Client
 */
const config = {
  "generator": {
    "name": "client",
    "provider": {
      "fromEnvVar": null,
      "value": "prisma-client-js"
    },
    "output": {
      "value": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/iot-service/prisma/.prisma/client",
      "fromEnvVar": null
    },
    "config": {
      "engineType": "library"
    },
    "binaryTargets": [
      {
        "fromEnvVar": null,
        "value": "debian-openssl-3.0.x",
        "native": true
      },
      {
        "fromEnvVar": null,
        "value": "linux-musl-openssl-3.0.x"
      },
      {
        "fromEnvVar": null,
        "value": "debian-openssl-3.0.x"
      }
    ],
    "previewFeatures": [],
    "sourceFilePath": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/iot-service/prisma/schema.prisma",
    "isCustomOutput": true
  },
  "relativeEnvPaths": {
    "rootEnvPath": null
  },
  "relativePath": "../..",
  "clientVersion": "5.22.0",
  "engineVersion": "605197351a3c8bdd595af2d2a9bc3025bca48ea2",
  "datasourceNames": [
    "db"
  ],
  "activeProvider": "postgresql",
  "postinstall": false,
  "ciName": "GitHub Actions",
  "inlineDatasources": {
    "db": {
      "url": {
        "fromEnvVar": "DATABASE_URL",
        "value": null
      }
    }
  },
  "inlineSchema": "// This is your Prisma schema file for the IoT Service\n// Learn more about it in the docs: https://pris.ly/d/prisma-schema\n\ngenerator client {\n  provider      = \"prisma-client-js\"\n  output        = \".prisma/client\"\n  binaryTargets = [\"native\", \"linux-musl-openssl-3.0.x\", \"debian-openssl-3.0.x\"]\n}\n\ndatasource db {\n  provider = \"postgresql\"\n  url      = env(\"DATABASE_URL\")\n}\n\n// Enums\nenum DeviceType {\n  SOIL_MOISTURE_SENSOR\n  TEMPERATURE_SENSOR\n  HUMIDITY_SENSOR\n  WATER_FLOW_METER\n  WEATHER_STATION\n  VALVE_CONTROLLER\n  PUMP_CONTROLLER\n  IRRIGATION_CONTROLLER\n  CAMERA\n  GATEWAY\n  CUSTOM\n}\n\nenum DeviceStatus {\n  ONLINE\n  OFFLINE\n  MAINTENANCE\n  ERROR\n  INACTIVE\n}\n\nenum SensorType {\n  SOIL_MOISTURE\n  SOIL_TEMPERATURE\n  AIR_TEMPERATURE\n  AIR_HUMIDITY\n  LIGHT_INTENSITY\n  WATER_FLOW\n  WATER_PRESSURE\n  WATER_LEVEL\n  PH_LEVEL\n  EC_LEVEL\n  BATTERY_LEVEL\n  SIGNAL_STRENGTH\n  RAINFALL\n  WIND_SPEED\n  WIND_DIRECTION\n  CUSTOM\n}\n\nenum ActuatorType {\n  VALVE\n  PUMP\n  MOTOR\n  RELAY\n  SWITCH\n  SERVO\n  CUSTOM\n}\n\nenum AlertSeverity {\n  INFO\n  WARNING\n  ERROR\n  CRITICAL\n}\n\nenum CommandStatus {\n  PENDING\n  EXECUTING\n  COMPLETED\n  FAILED\n  TIMEOUT\n  CANCELLED\n}\n\n// Main Models\nmodel Device {\n  id       String       @id @default(uuid())\n  tenantId String\n  deviceId String // Unique device identifier from the physical device\n  name     String\n  type     DeviceType\n  status   DeviceStatus @default(OFFLINE)\n  lastSeen DateTime?\n  metadata Json? // Additional device metadata (manufacturer, model, firmware version, etc.)\n  fieldId  String? // Optional reference to field/zone\n\n  createdAt DateTime @default(now())\n  updatedAt DateTime @updatedAt\n\n  // Relations\n  sensors        Sensor[]\n  sensorReadings SensorReading[]\n  actuators      Actuator[]\n  alerts         DeviceAlert[]\n\n  @@unique([tenantId, deviceId])\n  @@index([tenantId])\n  @@index([deviceId])\n  @@index([status])\n  @@index([fieldId])\n  @@index([lastSeen])\n  @@index([tenantId, status])\n  @@index([tenantId, fieldId])\n  @@map(\"devices\")\n}\n\nmodel Sensor {\n  id              String     @id @default(uuid())\n  deviceId        String\n  sensorType      SensorType\n  unit            String // Unit of measurement (e.g., \"%\", \"°C\", \"L/min\")\n  calibrationData Json? // Calibration parameters and coefficients\n  lastReading     Float?\n  lastReadingAt   DateTime?\n\n  createdAt DateTime @default(now())\n  updatedAt DateTime @updatedAt\n\n  // Relations\n  device   Device          @relation(fields: [deviceId], references: [id], onDelete: Cascade)\n  readings SensorReading[]\n\n  @@index([deviceId])\n  @@index([sensorType])\n  @@index([deviceId, sensorType])\n  @@map(\"sensors\")\n}\n\nmodel SensorReading {\n  id        String   @id @default(uuid())\n  sensorId  String\n  deviceId  String\n  value     Float\n  unit      String\n  timestamp DateTime @default(now())\n  quality   Float?   @default(1.0) // Quality indicator 0-1, null means unknown\n  metadata  Json? // Additional reading metadata (raw value, calibrated value, etc.)\n\n  // Relations\n  sensor Sensor @relation(fields: [sensorId], references: [id], onDelete: Cascade)\n  device Device @relation(fields: [deviceId], references: [id], onDelete: Cascade)\n\n  @@index([sensorId])\n  @@index([deviceId])\n  @@index([timestamp])\n  @@index([sensorId, timestamp])\n  @@index([deviceId, timestamp])\n  @@map(\"sensor_readings\")\n}\n\nmodel Actuator {\n  id            String       @id @default(uuid())\n  deviceId      String\n  actuatorType  ActuatorType\n  name          String?\n  currentState  Json? // Current state (e.g., {\"position\": 50, \"enabled\": true})\n  lastCommand   String?\n  lastCommandAt DateTime?\n\n  createdAt DateTime @default(now())\n  updatedAt DateTime @updatedAt\n\n  // Relations\n  device   Device            @relation(fields: [deviceId], references: [id], onDelete: Cascade)\n  commands ActuatorCommand[]\n\n  @@index([deviceId])\n  @@index([actuatorType])\n  @@index([deviceId, actuatorType])\n  @@map(\"actuators\")\n}\n\nmodel ActuatorCommand {\n  id           String        @id @default(uuid())\n  actuatorId   String\n  command      String // Command name (e.g., \"open\", \"close\", \"set_position\")\n  parameters   Json? // Command parameters\n  status       CommandStatus @default(PENDING)\n  requestedAt  DateTime      @default(now())\n  executedAt   DateTime?\n  completedAt  DateTime?\n  errorMessage String?\n\n  createdAt DateTime @default(now())\n  updatedAt DateTime @updatedAt\n\n  // Relations\n  actuator Actuator @relation(fields: [actuatorId], references: [id], onDelete: Cascade)\n\n  @@index([actuatorId])\n  @@index([status])\n  @@index([requestedAt])\n  @@index([actuatorId, status])\n  @@index([actuatorId, requestedAt])\n  @@map(\"actuator_commands\")\n}\n\nmodel DeviceAlert {\n  id             String        @id @default(uuid())\n  deviceId       String\n  tenantId       String\n  alertType      String // Type of alert (e.g., \"offline\", \"battery_low\", \"sensor_error\")\n  severity       AlertSeverity\n  message        String\n  acknowledged   Boolean       @default(false)\n  acknowledgedBy String?\n  acknowledgedAt DateTime?\n  resolvedAt     DateTime?\n  metadata       Json? // Additional alert data\n\n  createdAt DateTime @default(now())\n  updatedAt DateTime @updatedAt\n\n  // Relations\n  device Device @relation(fields: [deviceId], references: [id], onDelete: Cascade)\n\n  @@index([deviceId])\n  @@index([tenantId])\n  @@index([severity])\n  @@index([acknowledged])\n  @@index([createdAt])\n  @@index([tenantId, acknowledged])\n  @@index([tenantId, severity])\n  @@index([deviceId, acknowledged])\n  @@map(\"device_alerts\")\n}\n",
  "inlineSchemaHash": "752f7f460cd4e4b6947236663daab86d128b4fe5e6c58c5452bc050a5c3d0ad2",
  "copyEngine": true
}
config.dirname = '/'

config.runtimeDataModel = JSON.parse("{\"models\":{\"Device\":{\"dbName\":\"devices\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DeviceType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DeviceStatus\",\"default\":\"OFFLINE\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastSeen\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"metadata\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fieldId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"sensors\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Sensor\",\"relationName\":\"DeviceToSensor\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"sensorReadings\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"SensorReading\",\"relationName\":\"DeviceToSensorReading\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"actuators\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Actuator\",\"relationName\":\"ActuatorToDevice\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"alerts\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DeviceAlert\",\"relationName\":\"DeviceToDeviceAlert\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[[\"tenantId\",\"deviceId\"]],\"uniqueIndexes\":[{\"name\":null,\"fields\":[\"tenantId\",\"deviceId\"]}],\"isGenerated\":false},\"Sensor\":{\"dbName\":\"sensors\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"sensorType\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"SensorType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unit\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"calibrationData\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastReading\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastReadingAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"device\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Device\",\"relationName\":\"DeviceToSensor\",\"relationFromFields\":[\"deviceId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"readings\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"SensorReading\",\"relationName\":\"SensorToSensorReading\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"SensorReading\":{\"dbName\":\"sensor_readings\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"sensorId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"value\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"unit\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"timestamp\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"quality\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Float\",\"default\":1,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"metadata\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"sensor\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Sensor\",\"relationName\":\"SensorToSensorReading\",\"relationFromFields\":[\"sensorId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"device\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Device\",\"relationName\":\"DeviceToSensorReading\",\"relationFromFields\":[\"deviceId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"Actuator\":{\"dbName\":\"actuators\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"actuatorType\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"ActuatorType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"currentState\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastCommand\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"lastCommandAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"device\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Device\",\"relationName\":\"ActuatorToDevice\",\"relationFromFields\":[\"deviceId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"commands\",\"kind\":\"object\",\"isList\":true,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"ActuatorCommand\",\"relationName\":\"ActuatorToActuatorCommand\",\"relationFromFields\":[],\"relationToFields\":[],\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"ActuatorCommand\":{\"dbName\":\"actuator_commands\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"actuatorId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"command\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"parameters\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"status\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"CommandStatus\",\"default\":\"PENDING\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"requestedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"executedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"completedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"errorMessage\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"actuator\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Actuator\",\"relationName\":\"ActuatorToActuatorCommand\",\"relationFromFields\":[\"actuatorId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"DeviceAlert\":{\"dbName\":\"device_alerts\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"deviceId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":true,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"alertType\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"severity\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"AlertSeverity\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"message\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"acknowledged\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":false,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"acknowledgedBy\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"acknowledgedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"resolvedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"metadata\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true},{\"name\":\"device\",\"kind\":\"object\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Device\",\"relationName\":\"DeviceToDeviceAlert\",\"relationFromFields\":[\"deviceId\"],\"relationToFields\":[\"id\"],\"relationOnDelete\":\"Cascade\",\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false}},\"enums\":{\"DeviceType\":{\"values\":[{\"name\":\"SOIL_MOISTURE_SENSOR\",\"dbName\":null},{\"name\":\"TEMPERATURE_SENSOR\",\"dbName\":null},{\"name\":\"HUMIDITY_SENSOR\",\"dbName\":null},{\"name\":\"WATER_FLOW_METER\",\"dbName\":null},{\"name\":\"WEATHER_STATION\",\"dbName\":null},{\"name\":\"VALVE_CONTROLLER\",\"dbName\":null},{\"name\":\"PUMP_CONTROLLER\",\"dbName\":null},{\"name\":\"IRRIGATION_CONTROLLER\",\"dbName\":null},{\"name\":\"CAMERA\",\"dbName\":null},{\"name\":\"GATEWAY\",\"dbName\":null},{\"name\":\"CUSTOM\",\"dbName\":null}],\"dbName\":null},\"DeviceStatus\":{\"values\":[{\"name\":\"ONLINE\",\"dbName\":null},{\"name\":\"OFFLINE\",\"dbName\":null},{\"name\":\"MAINTENANCE\",\"dbName\":null},{\"name\":\"ERROR\",\"dbName\":null},{\"name\":\"INACTIVE\",\"dbName\":null}],\"dbName\":null},\"SensorType\":{\"values\":[{\"name\":\"SOIL_MOISTURE\",\"dbName\":null},{\"name\":\"SOIL_TEMPERATURE\",\"dbName\":null},{\"name\":\"AIR_TEMPERATURE\",\"dbName\":null},{\"name\":\"AIR_HUMIDITY\",\"dbName\":null},{\"name\":\"LIGHT_INTENSITY\",\"dbName\":null},{\"name\":\"WATER_FLOW\",\"dbName\":null},{\"name\":\"WATER_PRESSURE\",\"dbName\":null},{\"name\":\"WATER_LEVEL\",\"dbName\":null},{\"name\":\"PH_LEVEL\",\"dbName\":null},{\"name\":\"EC_LEVEL\",\"dbName\":null},{\"name\":\"BATTERY_LEVEL\",\"dbName\":null},{\"name\":\"SIGNAL_STRENGTH\",\"dbName\":null},{\"name\":\"RAINFALL\",\"dbName\":null},{\"name\":\"WIND_SPEED\",\"dbName\":null},{\"name\":\"WIND_DIRECTION\",\"dbName\":null},{\"name\":\"CUSTOM\",\"dbName\":null}],\"dbName\":null},\"ActuatorType\":{\"values\":[{\"name\":\"VALVE\",\"dbName\":null},{\"name\":\"PUMP\",\"dbName\":null},{\"name\":\"MOTOR\",\"dbName\":null},{\"name\":\"RELAY\",\"dbName\":null},{\"name\":\"SWITCH\",\"dbName\":null},{\"name\":\"SERVO\",\"dbName\":null},{\"name\":\"CUSTOM\",\"dbName\":null}],\"dbName\":null},\"AlertSeverity\":{\"values\":[{\"name\":\"INFO\",\"dbName\":null},{\"name\":\"WARNING\",\"dbName\":null},{\"name\":\"ERROR\",\"dbName\":null},{\"name\":\"CRITICAL\",\"dbName\":null}],\"dbName\":null},\"CommandStatus\":{\"values\":[{\"name\":\"PENDING\",\"dbName\":null},{\"name\":\"EXECUTING\",\"dbName\":null},{\"name\":\"COMPLETED\",\"dbName\":null},{\"name\":\"FAILED\",\"dbName\":null},{\"name\":\"TIMEOUT\",\"dbName\":null},{\"name\":\"CANCELLED\",\"dbName\":null}],\"dbName\":null}},\"types\":{}}")
defineDmmfProperty(exports.Prisma, config.runtimeDataModel)
config.engineWasm = undefined

config.injectableEdgeEnv = () => ({
  parsed: {
    DATABASE_URL: typeof globalThis !== 'undefined' && globalThis['DATABASE_URL'] || typeof process !== 'undefined' && process.env && process.env.DATABASE_URL || undefined
  }
})

if (typeof globalThis !== 'undefined' && globalThis['DEBUG'] || typeof process !== 'undefined' && process.env && process.env.DEBUG || undefined) {
  Debug.enable(typeof globalThis !== 'undefined' && globalThis['DEBUG'] || typeof process !== 'undefined' && process.env && process.env.DEBUG || undefined)
}

const PrismaClient = getPrismaClient(config)
exports.PrismaClient = PrismaClient
Object.assign(exports, Prisma)

