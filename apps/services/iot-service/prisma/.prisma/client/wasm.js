
Object.defineProperty(exports, "__esModule", { value: true });

const {
  Decimal,
  objectEnumValues,
  makeStrictEnum,
  Public,
  getRuntime,
  skip
} = require('./runtime/index-browser.js')


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

Prisma.PrismaClientKnownRequestError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientKnownRequestError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)};
Prisma.PrismaClientUnknownRequestError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientUnknownRequestError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientRustPanicError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientRustPanicError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientInitializationError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientInitializationError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.PrismaClientValidationError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`PrismaClientValidationError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.NotFoundError = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`NotFoundError is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.Decimal = Decimal

/**
 * Re-export of sql-template-tag
 */
Prisma.sql = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`sqltag is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.empty = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`empty is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.join = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`join is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.raw = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`raw is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.validator = Public.validator

/**
* Extensions
*/
Prisma.getExtensionContext = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`Extensions.getExtensionContext is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}
Prisma.defineExtension = () => {
  const runtimeName = getRuntime().prettyName;
  throw new Error(`Extensions.defineExtension is unable to run in this browser environment, or has been bundled for the browser (running in ${runtimeName}).
In case this error is unexpected for you, please report it in https://pris.ly/prisma-prisma-bug-report`,
)}

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
 * This is a stub Prisma Client that will error at runtime if called.
 */
class PrismaClient {
  constructor() {
    return new Proxy(this, {
      get(target, prop) {
        let message
        const runtime = getRuntime()
        if (runtime.isEdge) {
          message = `PrismaClient is not configured to run in ${runtime.prettyName}. In order to run Prisma Client on edge runtime, either:
- Use Prisma Accelerate: https://pris.ly/d/accelerate
- Use Driver Adapters: https://pris.ly/d/driver-adapters
`;
        } else {
          message = 'PrismaClient is unable to run in this browser environment, or has been bundled for the browser (running in `' + runtime.prettyName + '`).'
        }
        
        message += `
If this is unexpected, please open an issue: https://pris.ly/prisma-prisma-bug-report`

        throw new Error(message)
      }
    })
  }
}

exports.PrismaClient = PrismaClient

Object.assign(exports, Prisma)
