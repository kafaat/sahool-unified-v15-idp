
/**
 * Client
**/

import * as runtime from './runtime/library.js';
import $Types = runtime.Types // general types
import $Public = runtime.Types.Public
import $Utils = runtime.Types.Utils
import $Extensions = runtime.Types.Extensions
import $Result = runtime.Types.Result

export type PrismaPromise<T> = $Public.PrismaPromise<T>


/**
 * Model Device
 * 
 */
export type Device = $Result.DefaultSelection<Prisma.$DevicePayload>
/**
 * Model Sensor
 * 
 */
export type Sensor = $Result.DefaultSelection<Prisma.$SensorPayload>
/**
 * Model SensorReading
 * 
 */
export type SensorReading = $Result.DefaultSelection<Prisma.$SensorReadingPayload>
/**
 * Model Actuator
 * 
 */
export type Actuator = $Result.DefaultSelection<Prisma.$ActuatorPayload>
/**
 * Model ActuatorCommand
 * 
 */
export type ActuatorCommand = $Result.DefaultSelection<Prisma.$ActuatorCommandPayload>
/**
 * Model DeviceAlert
 * 
 */
export type DeviceAlert = $Result.DefaultSelection<Prisma.$DeviceAlertPayload>

/**
 * Enums
 */
export namespace $Enums {
  export const DeviceType: {
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

export type DeviceType = (typeof DeviceType)[keyof typeof DeviceType]


export const DeviceStatus: {
  ONLINE: 'ONLINE',
  OFFLINE: 'OFFLINE',
  MAINTENANCE: 'MAINTENANCE',
  ERROR: 'ERROR',
  INACTIVE: 'INACTIVE'
};

export type DeviceStatus = (typeof DeviceStatus)[keyof typeof DeviceStatus]


export const SensorType: {
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

export type SensorType = (typeof SensorType)[keyof typeof SensorType]


export const ActuatorType: {
  VALVE: 'VALVE',
  PUMP: 'PUMP',
  MOTOR: 'MOTOR',
  RELAY: 'RELAY',
  SWITCH: 'SWITCH',
  SERVO: 'SERVO',
  CUSTOM: 'CUSTOM'
};

export type ActuatorType = (typeof ActuatorType)[keyof typeof ActuatorType]


export const CommandStatus: {
  PENDING: 'PENDING',
  EXECUTING: 'EXECUTING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  TIMEOUT: 'TIMEOUT',
  CANCELLED: 'CANCELLED'
};

export type CommandStatus = (typeof CommandStatus)[keyof typeof CommandStatus]


export const AlertSeverity: {
  INFO: 'INFO',
  WARNING: 'WARNING',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL'
};

export type AlertSeverity = (typeof AlertSeverity)[keyof typeof AlertSeverity]

}

export type DeviceType = $Enums.DeviceType

export const DeviceType: typeof $Enums.DeviceType

export type DeviceStatus = $Enums.DeviceStatus

export const DeviceStatus: typeof $Enums.DeviceStatus

export type SensorType = $Enums.SensorType

export const SensorType: typeof $Enums.SensorType

export type ActuatorType = $Enums.ActuatorType

export const ActuatorType: typeof $Enums.ActuatorType

export type CommandStatus = $Enums.CommandStatus

export const CommandStatus: typeof $Enums.CommandStatus

export type AlertSeverity = $Enums.AlertSeverity

export const AlertSeverity: typeof $Enums.AlertSeverity

/**
 * ##  Prisma Client ʲˢ
 * 
 * Type-safe database client for TypeScript & Node.js
 * @example
 * ```
 * const prisma = new PrismaClient()
 * // Fetch zero or more Devices
 * const devices = await prisma.device.findMany()
 * ```
 *
 * 
 * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client).
 */
export class PrismaClient<
  ClientOptions extends Prisma.PrismaClientOptions = Prisma.PrismaClientOptions,
  U = 'log' extends keyof ClientOptions ? ClientOptions['log'] extends Array<Prisma.LogLevel | Prisma.LogDefinition> ? Prisma.GetEvents<ClientOptions['log']> : never : never,
  ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs
> {
  [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['other'] }

    /**
   * ##  Prisma Client ʲˢ
   * 
   * Type-safe database client for TypeScript & Node.js
   * @example
   * ```
   * const prisma = new PrismaClient()
   * // Fetch zero or more Devices
   * const devices = await prisma.device.findMany()
   * ```
   *
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client).
   */

  constructor(optionsArg ?: Prisma.Subset<ClientOptions, Prisma.PrismaClientOptions>);
  $on<V extends U>(eventType: V, callback: (event: V extends 'query' ? Prisma.QueryEvent : Prisma.LogEvent) => void): void;

  /**
   * Connect with the database
   */
  $connect(): $Utils.JsPromise<void>;

  /**
   * Disconnect from the database
   */
  $disconnect(): $Utils.JsPromise<void>;

  /**
   * Add a middleware
   * @deprecated since 4.16.0. For new code, prefer client extensions instead.
   * @see https://pris.ly/d/extensions
   */
  $use(cb: Prisma.Middleware): void

/**
   * Executes a prepared raw query and returns the number of affected rows.
   * @example
   * ```
   * const result = await prisma.$executeRaw`UPDATE User SET cool = ${true} WHERE email = ${'user@email.com'};`
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $executeRaw<T = unknown>(query: TemplateStringsArray | Prisma.Sql, ...values: any[]): Prisma.PrismaPromise<number>;

  /**
   * Executes a raw query and returns the number of affected rows.
   * Susceptible to SQL injections, see documentation.
   * @example
   * ```
   * const result = await prisma.$executeRawUnsafe('UPDATE User SET cool = $1 WHERE email = $2 ;', true, 'user@email.com')
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $executeRawUnsafe<T = unknown>(query: string, ...values: any[]): Prisma.PrismaPromise<number>;

  /**
   * Performs a prepared raw query and returns the `SELECT` data.
   * @example
   * ```
   * const result = await prisma.$queryRaw`SELECT * FROM User WHERE id = ${1} OR email = ${'user@email.com'};`
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $queryRaw<T = unknown>(query: TemplateStringsArray | Prisma.Sql, ...values: any[]): Prisma.PrismaPromise<T>;

  /**
   * Performs a raw query and returns the `SELECT` data.
   * Susceptible to SQL injections, see documentation.
   * @example
   * ```
   * const result = await prisma.$queryRawUnsafe('SELECT * FROM User WHERE id = $1 OR email = $2;', 1, 'user@email.com')
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/raw-database-access).
   */
  $queryRawUnsafe<T = unknown>(query: string, ...values: any[]): Prisma.PrismaPromise<T>;


  /**
   * Allows the running of a sequence of read/write operations that are guaranteed to either succeed or fail as a whole.
   * @example
   * ```
   * const [george, bob, alice] = await prisma.$transaction([
   *   prisma.user.create({ data: { name: 'George' } }),
   *   prisma.user.create({ data: { name: 'Bob' } }),
   *   prisma.user.create({ data: { name: 'Alice' } }),
   * ])
   * ```
   * 
   * Read more in our [docs](https://www.prisma.io/docs/concepts/components/prisma-client/transactions).
   */
  $transaction<P extends Prisma.PrismaPromise<any>[]>(arg: [...P], options?: { isolationLevel?: Prisma.TransactionIsolationLevel }): $Utils.JsPromise<runtime.Types.Utils.UnwrapTuple<P>>

  $transaction<R>(fn: (prisma: Omit<PrismaClient, runtime.ITXClientDenyList>) => $Utils.JsPromise<R>, options?: { maxWait?: number, timeout?: number, isolationLevel?: Prisma.TransactionIsolationLevel }): $Utils.JsPromise<R>


  $extends: $Extensions.ExtendsHook<"extends", Prisma.TypeMapCb, ExtArgs>

      /**
   * `prisma.device`: Exposes CRUD operations for the **Device** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Devices
    * const devices = await prisma.device.findMany()
    * ```
    */
  get device(): Prisma.DeviceDelegate<ExtArgs>;

  /**
   * `prisma.sensor`: Exposes CRUD operations for the **Sensor** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Sensors
    * const sensors = await prisma.sensor.findMany()
    * ```
    */
  get sensor(): Prisma.SensorDelegate<ExtArgs>;

  /**
   * `prisma.sensorReading`: Exposes CRUD operations for the **SensorReading** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more SensorReadings
    * const sensorReadings = await prisma.sensorReading.findMany()
    * ```
    */
  get sensorReading(): Prisma.SensorReadingDelegate<ExtArgs>;

  /**
   * `prisma.actuator`: Exposes CRUD operations for the **Actuator** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Actuators
    * const actuators = await prisma.actuator.findMany()
    * ```
    */
  get actuator(): Prisma.ActuatorDelegate<ExtArgs>;

  /**
   * `prisma.actuatorCommand`: Exposes CRUD operations for the **ActuatorCommand** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more ActuatorCommands
    * const actuatorCommands = await prisma.actuatorCommand.findMany()
    * ```
    */
  get actuatorCommand(): Prisma.ActuatorCommandDelegate<ExtArgs>;

  /**
   * `prisma.deviceAlert`: Exposes CRUD operations for the **DeviceAlert** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more DeviceAlerts
    * const deviceAlerts = await prisma.deviceAlert.findMany()
    * ```
    */
  get deviceAlert(): Prisma.DeviceAlertDelegate<ExtArgs>;
}

export namespace Prisma {
  export import DMMF = runtime.DMMF

  export type PrismaPromise<T> = $Public.PrismaPromise<T>

  /**
   * Validator
   */
  export import validator = runtime.Public.validator

  /**
   * Prisma Errors
   */
  export import PrismaClientKnownRequestError = runtime.PrismaClientKnownRequestError
  export import PrismaClientUnknownRequestError = runtime.PrismaClientUnknownRequestError
  export import PrismaClientRustPanicError = runtime.PrismaClientRustPanicError
  export import PrismaClientInitializationError = runtime.PrismaClientInitializationError
  export import PrismaClientValidationError = runtime.PrismaClientValidationError
  export import NotFoundError = runtime.NotFoundError

  /**
   * Re-export of sql-template-tag
   */
  export import sql = runtime.sqltag
  export import empty = runtime.empty
  export import join = runtime.join
  export import raw = runtime.raw
  export import Sql = runtime.Sql



  /**
   * Decimal.js
   */
  export import Decimal = runtime.Decimal

  export type DecimalJsLike = runtime.DecimalJsLike

  /**
   * Metrics 
   */
  export type Metrics = runtime.Metrics
  export type Metric<T> = runtime.Metric<T>
  export type MetricHistogram = runtime.MetricHistogram
  export type MetricHistogramBucket = runtime.MetricHistogramBucket

  /**
  * Extensions
  */
  export import Extension = $Extensions.UserArgs
  export import getExtensionContext = runtime.Extensions.getExtensionContext
  export import Args = $Public.Args
  export import Payload = $Public.Payload
  export import Result = $Public.Result
  export import Exact = $Public.Exact

  /**
   * Prisma Client JS version: 5.22.0
   * Query Engine version: 605197351a3c8bdd595af2d2a9bc3025bca48ea2
   */
  export type PrismaVersion = {
    client: string
  }

  export const prismaVersion: PrismaVersion 

  /**
   * Utility Types
   */


  export import JsonObject = runtime.JsonObject
  export import JsonArray = runtime.JsonArray
  export import JsonValue = runtime.JsonValue
  export import InputJsonObject = runtime.InputJsonObject
  export import InputJsonArray = runtime.InputJsonArray
  export import InputJsonValue = runtime.InputJsonValue

  /**
   * Types of the values used to represent different kinds of `null` values when working with JSON fields.
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  namespace NullTypes {
    /**
    * Type of `Prisma.DbNull`.
    * 
    * You cannot use other instances of this class. Please use the `Prisma.DbNull` value.
    * 
    * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
    */
    class DbNull {
      private DbNull: never
      private constructor()
    }

    /**
    * Type of `Prisma.JsonNull`.
    * 
    * You cannot use other instances of this class. Please use the `Prisma.JsonNull` value.
    * 
    * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
    */
    class JsonNull {
      private JsonNull: never
      private constructor()
    }

    /**
    * Type of `Prisma.AnyNull`.
    * 
    * You cannot use other instances of this class. Please use the `Prisma.AnyNull` value.
    * 
    * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
    */
    class AnyNull {
      private AnyNull: never
      private constructor()
    }
  }

  /**
   * Helper for filtering JSON entries that have `null` on the database (empty on the db)
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  export const DbNull: NullTypes.DbNull

  /**
   * Helper for filtering JSON entries that have JSON `null` values (not empty on the db)
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  export const JsonNull: NullTypes.JsonNull

  /**
   * Helper for filtering JSON entries that are `Prisma.DbNull` or `Prisma.JsonNull`
   * 
   * @see https://www.prisma.io/docs/concepts/components/prisma-client/working-with-fields/working-with-json-fields#filtering-on-a-json-field
   */
  export const AnyNull: NullTypes.AnyNull

  type SelectAndInclude = {
    select: any
    include: any
  }

  type SelectAndOmit = {
    select: any
    omit: any
  }

  /**
   * Get the type of the value, that the Promise holds.
   */
  export type PromiseType<T extends PromiseLike<any>> = T extends PromiseLike<infer U> ? U : T;

  /**
   * Get the return type of a function which returns a Promise.
   */
  export type PromiseReturnType<T extends (...args: any) => $Utils.JsPromise<any>> = PromiseType<ReturnType<T>>

  /**
   * From T, pick a set of properties whose keys are in the union K
   */
  type Prisma__Pick<T, K extends keyof T> = {
      [P in K]: T[P];
  };


  export type Enumerable<T> = T | Array<T>;

  export type RequiredKeys<T> = {
    [K in keyof T]-?: {} extends Prisma__Pick<T, K> ? never : K
  }[keyof T]

  export type TruthyKeys<T> = keyof {
    [K in keyof T as T[K] extends false | undefined | null ? never : K]: K
  }

  export type TrueKeys<T> = TruthyKeys<Prisma__Pick<T, RequiredKeys<T>>>

  /**
   * Subset
   * @desc From `T` pick properties that exist in `U`. Simple version of Intersection
   */
  export type Subset<T, U> = {
    [key in keyof T]: key extends keyof U ? T[key] : never;
  };

  /**
   * SelectSubset
   * @desc From `T` pick properties that exist in `U`. Simple version of Intersection.
   * Additionally, it validates, if both select and include are present. If the case, it errors.
   */
  export type SelectSubset<T, U> = {
    [key in keyof T]: key extends keyof U ? T[key] : never
  } &
    (T extends SelectAndInclude
      ? 'Please either choose `select` or `include`.'
      : T extends SelectAndOmit
        ? 'Please either choose `select` or `omit`.'
        : {})

  /**
   * Subset + Intersection
   * @desc From `T` pick properties that exist in `U` and intersect `K`
   */
  export type SubsetIntersection<T, U, K> = {
    [key in keyof T]: key extends keyof U ? T[key] : never
  } &
    K

  type Without<T, U> = { [P in Exclude<keyof T, keyof U>]?: never };

  /**
   * XOR is needed to have a real mutually exclusive union type
   * https://stackoverflow.com/questions/42123407/does-typescript-support-mutually-exclusive-types
   */
  type XOR<T, U> =
    T extends object ?
    U extends object ?
      (Without<T, U> & U) | (Without<U, T> & T)
    : U : T


  /**
   * Is T a Record?
   */
  type IsObject<T extends any> = T extends Array<any>
  ? False
  : T extends Date
  ? False
  : T extends Uint8Array
  ? False
  : T extends BigInt
  ? False
  : T extends object
  ? True
  : False


  /**
   * If it's T[], return T
   */
  export type UnEnumerate<T extends unknown> = T extends Array<infer U> ? U : T

  /**
   * From ts-toolbelt
   */

  type __Either<O extends object, K extends Key> = Omit<O, K> &
    {
      // Merge all but K
      [P in K]: Prisma__Pick<O, P & keyof O> // With K possibilities
    }[K]

  type EitherStrict<O extends object, K extends Key> = Strict<__Either<O, K>>

  type EitherLoose<O extends object, K extends Key> = ComputeRaw<__Either<O, K>>

  type _Either<
    O extends object,
    K extends Key,
    strict extends Boolean
  > = {
    1: EitherStrict<O, K>
    0: EitherLoose<O, K>
  }[strict]

  type Either<
    O extends object,
    K extends Key,
    strict extends Boolean = 1
  > = O extends unknown ? _Either<O, K, strict> : never

  export type Union = any

  type PatchUndefined<O extends object, O1 extends object> = {
    [K in keyof O]: O[K] extends undefined ? At<O1, K> : O[K]
  } & {}

  /** Helper Types for "Merge" **/
  export type IntersectOf<U extends Union> = (
    U extends unknown ? (k: U) => void : never
  ) extends (k: infer I) => void
    ? I
    : never

  export type Overwrite<O extends object, O1 extends object> = {
      [K in keyof O]: K extends keyof O1 ? O1[K] : O[K];
  } & {};

  type _Merge<U extends object> = IntersectOf<Overwrite<U, {
      [K in keyof U]-?: At<U, K>;
  }>>;

  type Key = string | number | symbol;
  type AtBasic<O extends object, K extends Key> = K extends keyof O ? O[K] : never;
  type AtStrict<O extends object, K extends Key> = O[K & keyof O];
  type AtLoose<O extends object, K extends Key> = O extends unknown ? AtStrict<O, K> : never;
  export type At<O extends object, K extends Key, strict extends Boolean = 1> = {
      1: AtStrict<O, K>;
      0: AtLoose<O, K>;
  }[strict];

  export type ComputeRaw<A extends any> = A extends Function ? A : {
    [K in keyof A]: A[K];
  } & {};

  export type OptionalFlat<O> = {
    [K in keyof O]?: O[K];
  } & {};

  type _Record<K extends keyof any, T> = {
    [P in K]: T;
  };

  // cause typescript not to expand types and preserve names
  type NoExpand<T> = T extends unknown ? T : never;

  // this type assumes the passed object is entirely optional
  type AtLeast<O extends object, K extends string> = NoExpand<
    O extends unknown
    ? | (K extends keyof O ? { [P in K]: O[P] } & O : O)
      | {[P in keyof O as P extends K ? K : never]-?: O[P]} & O
    : never>;

  type _Strict<U, _U = U> = U extends unknown ? U & OptionalFlat<_Record<Exclude<Keys<_U>, keyof U>, never>> : never;

  export type Strict<U extends object> = ComputeRaw<_Strict<U>>;
  /** End Helper Types for "Merge" **/

  export type Merge<U extends object> = ComputeRaw<_Merge<Strict<U>>>;

  /**
  A [[Boolean]]
  */
  export type Boolean = True | False

  // /**
  // 1
  // */
  export type True = 1

  /**
  0
  */
  export type False = 0

  export type Not<B extends Boolean> = {
    0: 1
    1: 0
  }[B]

  export type Extends<A1 extends any, A2 extends any> = [A1] extends [never]
    ? 0 // anything `never` is false
    : A1 extends A2
    ? 1
    : 0

  export type Has<U extends Union, U1 extends Union> = Not<
    Extends<Exclude<U1, U>, U1>
  >

  export type Or<B1 extends Boolean, B2 extends Boolean> = {
    0: {
      0: 0
      1: 1
    }
    1: {
      0: 1
      1: 1
    }
  }[B1][B2]

  export type Keys<U extends Union> = U extends unknown ? keyof U : never

  type Cast<A, B> = A extends B ? A : B;

  export const type: unique symbol;



  /**
   * Used by group by
   */

  export type GetScalarType<T, O> = O extends object ? {
    [P in keyof T]: P extends keyof O
      ? O[P]
      : never
  } : never

  type FieldPaths<
    T,
    U = Omit<T, '_avg' | '_sum' | '_count' | '_min' | '_max'>
  > = IsObject<T> extends True ? U : T

  type GetHavingFields<T> = {
    [K in keyof T]: Or<
      Or<Extends<'OR', K>, Extends<'AND', K>>,
      Extends<'NOT', K>
    > extends True
      ? // infer is only needed to not hit TS limit
        // based on the brilliant idea of Pierre-Antoine Mills
        // https://github.com/microsoft/TypeScript/issues/30188#issuecomment-478938437
        T[K] extends infer TK
        ? GetHavingFields<UnEnumerate<TK> extends object ? Merge<UnEnumerate<TK>> : never>
        : never
      : {} extends FieldPaths<T[K]>
      ? never
      : K
  }[keyof T]

  /**
   * Convert tuple to union
   */
  type _TupleToUnion<T> = T extends (infer E)[] ? E : never
  type TupleToUnion<K extends readonly any[]> = _TupleToUnion<K>
  type MaybeTupleToUnion<T> = T extends any[] ? TupleToUnion<T> : T

  /**
   * Like `Pick`, but additionally can also accept an array of keys
   */
  type PickEnumerable<T, K extends Enumerable<keyof T> | keyof T> = Prisma__Pick<T, MaybeTupleToUnion<K>>

  /**
   * Exclude all keys with underscores
   */
  type ExcludeUnderscoreKeys<T extends string> = T extends `_${string}` ? never : T


  export type FieldRef<Model, FieldType> = runtime.FieldRef<Model, FieldType>

  type FieldRefInputType<Model, FieldType> = Model extends never ? never : FieldRef<Model, FieldType>


  export const ModelName: {
    Device: 'Device',
    Sensor: 'Sensor',
    SensorReading: 'SensorReading',
    Actuator: 'Actuator',
    ActuatorCommand: 'ActuatorCommand',
    DeviceAlert: 'DeviceAlert'
  };

  export type ModelName = (typeof ModelName)[keyof typeof ModelName]


  export type Datasources = {
    db?: Datasource
  }

  interface TypeMapCb extends $Utils.Fn<{extArgs: $Extensions.InternalArgs, clientOptions: PrismaClientOptions }, $Utils.Record<string, any>> {
    returns: Prisma.TypeMap<this['params']['extArgs'], this['params']['clientOptions']>
  }

  export type TypeMap<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs, ClientOptions = {}> = {
    meta: {
      modelProps: "device" | "sensor" | "sensorReading" | "actuator" | "actuatorCommand" | "deviceAlert"
      txIsolationLevel: Prisma.TransactionIsolationLevel
    }
    model: {
      Device: {
        payload: Prisma.$DevicePayload<ExtArgs>
        fields: Prisma.DeviceFieldRefs
        operations: {
          findUnique: {
            args: Prisma.DeviceFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.DeviceFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>
          }
          findFirst: {
            args: Prisma.DeviceFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.DeviceFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>
          }
          findMany: {
            args: Prisma.DeviceFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>[]
          }
          create: {
            args: Prisma.DeviceCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>
          }
          createMany: {
            args: Prisma.DeviceCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.DeviceCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>[]
          }
          delete: {
            args: Prisma.DeviceDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>
          }
          update: {
            args: Prisma.DeviceUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>
          }
          deleteMany: {
            args: Prisma.DeviceDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.DeviceUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.DeviceUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DevicePayload>
          }
          aggregate: {
            args: Prisma.DeviceAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateDevice>
          }
          groupBy: {
            args: Prisma.DeviceGroupByArgs<ExtArgs>
            result: $Utils.Optional<DeviceGroupByOutputType>[]
          }
          count: {
            args: Prisma.DeviceCountArgs<ExtArgs>
            result: $Utils.Optional<DeviceCountAggregateOutputType> | number
          }
        }
      }
      Sensor: {
        payload: Prisma.$SensorPayload<ExtArgs>
        fields: Prisma.SensorFieldRefs
        operations: {
          findUnique: {
            args: Prisma.SensorFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.SensorFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>
          }
          findFirst: {
            args: Prisma.SensorFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.SensorFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>
          }
          findMany: {
            args: Prisma.SensorFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>[]
          }
          create: {
            args: Prisma.SensorCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>
          }
          createMany: {
            args: Prisma.SensorCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.SensorCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>[]
          }
          delete: {
            args: Prisma.SensorDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>
          }
          update: {
            args: Prisma.SensorUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>
          }
          deleteMany: {
            args: Prisma.SensorDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.SensorUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.SensorUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorPayload>
          }
          aggregate: {
            args: Prisma.SensorAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateSensor>
          }
          groupBy: {
            args: Prisma.SensorGroupByArgs<ExtArgs>
            result: $Utils.Optional<SensorGroupByOutputType>[]
          }
          count: {
            args: Prisma.SensorCountArgs<ExtArgs>
            result: $Utils.Optional<SensorCountAggregateOutputType> | number
          }
        }
      }
      SensorReading: {
        payload: Prisma.$SensorReadingPayload<ExtArgs>
        fields: Prisma.SensorReadingFieldRefs
        operations: {
          findUnique: {
            args: Prisma.SensorReadingFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.SensorReadingFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>
          }
          findFirst: {
            args: Prisma.SensorReadingFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.SensorReadingFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>
          }
          findMany: {
            args: Prisma.SensorReadingFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>[]
          }
          create: {
            args: Prisma.SensorReadingCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>
          }
          createMany: {
            args: Prisma.SensorReadingCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.SensorReadingCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>[]
          }
          delete: {
            args: Prisma.SensorReadingDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>
          }
          update: {
            args: Prisma.SensorReadingUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>
          }
          deleteMany: {
            args: Prisma.SensorReadingDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.SensorReadingUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.SensorReadingUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SensorReadingPayload>
          }
          aggregate: {
            args: Prisma.SensorReadingAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateSensorReading>
          }
          groupBy: {
            args: Prisma.SensorReadingGroupByArgs<ExtArgs>
            result: $Utils.Optional<SensorReadingGroupByOutputType>[]
          }
          count: {
            args: Prisma.SensorReadingCountArgs<ExtArgs>
            result: $Utils.Optional<SensorReadingCountAggregateOutputType> | number
          }
        }
      }
      Actuator: {
        payload: Prisma.$ActuatorPayload<ExtArgs>
        fields: Prisma.ActuatorFieldRefs
        operations: {
          findUnique: {
            args: Prisma.ActuatorFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.ActuatorFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>
          }
          findFirst: {
            args: Prisma.ActuatorFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.ActuatorFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>
          }
          findMany: {
            args: Prisma.ActuatorFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>[]
          }
          create: {
            args: Prisma.ActuatorCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>
          }
          createMany: {
            args: Prisma.ActuatorCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.ActuatorCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>[]
          }
          delete: {
            args: Prisma.ActuatorDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>
          }
          update: {
            args: Prisma.ActuatorUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>
          }
          deleteMany: {
            args: Prisma.ActuatorDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.ActuatorUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.ActuatorUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorPayload>
          }
          aggregate: {
            args: Prisma.ActuatorAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateActuator>
          }
          groupBy: {
            args: Prisma.ActuatorGroupByArgs<ExtArgs>
            result: $Utils.Optional<ActuatorGroupByOutputType>[]
          }
          count: {
            args: Prisma.ActuatorCountArgs<ExtArgs>
            result: $Utils.Optional<ActuatorCountAggregateOutputType> | number
          }
        }
      }
      ActuatorCommand: {
        payload: Prisma.$ActuatorCommandPayload<ExtArgs>
        fields: Prisma.ActuatorCommandFieldRefs
        operations: {
          findUnique: {
            args: Prisma.ActuatorCommandFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.ActuatorCommandFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>
          }
          findFirst: {
            args: Prisma.ActuatorCommandFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.ActuatorCommandFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>
          }
          findMany: {
            args: Prisma.ActuatorCommandFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>[]
          }
          create: {
            args: Prisma.ActuatorCommandCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>
          }
          createMany: {
            args: Prisma.ActuatorCommandCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.ActuatorCommandCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>[]
          }
          delete: {
            args: Prisma.ActuatorCommandDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>
          }
          update: {
            args: Prisma.ActuatorCommandUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>
          }
          deleteMany: {
            args: Prisma.ActuatorCommandDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.ActuatorCommandUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.ActuatorCommandUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ActuatorCommandPayload>
          }
          aggregate: {
            args: Prisma.ActuatorCommandAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateActuatorCommand>
          }
          groupBy: {
            args: Prisma.ActuatorCommandGroupByArgs<ExtArgs>
            result: $Utils.Optional<ActuatorCommandGroupByOutputType>[]
          }
          count: {
            args: Prisma.ActuatorCommandCountArgs<ExtArgs>
            result: $Utils.Optional<ActuatorCommandCountAggregateOutputType> | number
          }
        }
      }
      DeviceAlert: {
        payload: Prisma.$DeviceAlertPayload<ExtArgs>
        fields: Prisma.DeviceAlertFieldRefs
        operations: {
          findUnique: {
            args: Prisma.DeviceAlertFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.DeviceAlertFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>
          }
          findFirst: {
            args: Prisma.DeviceAlertFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.DeviceAlertFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>
          }
          findMany: {
            args: Prisma.DeviceAlertFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>[]
          }
          create: {
            args: Prisma.DeviceAlertCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>
          }
          createMany: {
            args: Prisma.DeviceAlertCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.DeviceAlertCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>[]
          }
          delete: {
            args: Prisma.DeviceAlertDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>
          }
          update: {
            args: Prisma.DeviceAlertUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>
          }
          deleteMany: {
            args: Prisma.DeviceAlertDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.DeviceAlertUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.DeviceAlertUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$DeviceAlertPayload>
          }
          aggregate: {
            args: Prisma.DeviceAlertAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateDeviceAlert>
          }
          groupBy: {
            args: Prisma.DeviceAlertGroupByArgs<ExtArgs>
            result: $Utils.Optional<DeviceAlertGroupByOutputType>[]
          }
          count: {
            args: Prisma.DeviceAlertCountArgs<ExtArgs>
            result: $Utils.Optional<DeviceAlertCountAggregateOutputType> | number
          }
        }
      }
    }
  } & {
    other: {
      payload: any
      operations: {
        $executeRaw: {
          args: [query: TemplateStringsArray | Prisma.Sql, ...values: any[]],
          result: any
        }
        $executeRawUnsafe: {
          args: [query: string, ...values: any[]],
          result: any
        }
        $queryRaw: {
          args: [query: TemplateStringsArray | Prisma.Sql, ...values: any[]],
          result: any
        }
        $queryRawUnsafe: {
          args: [query: string, ...values: any[]],
          result: any
        }
      }
    }
  }
  export const defineExtension: $Extensions.ExtendsHook<"define", Prisma.TypeMapCb, $Extensions.DefaultArgs>
  export type DefaultPrismaClient = PrismaClient
  export type ErrorFormat = 'pretty' | 'colorless' | 'minimal'
  export interface PrismaClientOptions {
    /**
     * Overwrites the datasource url from your schema.prisma file
     */
    datasources?: Datasources
    /**
     * Overwrites the datasource url from your schema.prisma file
     */
    datasourceUrl?: string
    /**
     * @default "colorless"
     */
    errorFormat?: ErrorFormat
    /**
     * @example
     * ```
     * // Defaults to stdout
     * log: ['query', 'info', 'warn', 'error']
     * 
     * // Emit as events
     * log: [
     *   { emit: 'stdout', level: 'query' },
     *   { emit: 'stdout', level: 'info' },
     *   { emit: 'stdout', level: 'warn' }
     *   { emit: 'stdout', level: 'error' }
     * ]
     * ```
     * Read more in our [docs](https://www.prisma.io/docs/reference/tools-and-interfaces/prisma-client/logging#the-log-option).
     */
    log?: (LogLevel | LogDefinition)[]
    /**
     * The default values for transactionOptions
     * maxWait ?= 2000
     * timeout ?= 5000
     */
    transactionOptions?: {
      maxWait?: number
      timeout?: number
      isolationLevel?: Prisma.TransactionIsolationLevel
    }
  }


  /* Types for Logging */
  export type LogLevel = 'info' | 'query' | 'warn' | 'error'
  export type LogDefinition = {
    level: LogLevel
    emit: 'stdout' | 'event'
  }

  export type GetLogType<T extends LogLevel | LogDefinition> = T extends LogDefinition ? T['emit'] extends 'event' ? T['level'] : never : never
  export type GetEvents<T extends any> = T extends Array<LogLevel | LogDefinition> ?
    GetLogType<T[0]> | GetLogType<T[1]> | GetLogType<T[2]> | GetLogType<T[3]>
    : never

  export type QueryEvent = {
    timestamp: Date
    query: string
    params: string
    duration: number
    target: string
  }

  export type LogEvent = {
    timestamp: Date
    message: string
    target: string
  }
  /* End Types for Logging */


  export type PrismaAction =
    | 'findUnique'
    | 'findUniqueOrThrow'
    | 'findMany'
    | 'findFirst'
    | 'findFirstOrThrow'
    | 'create'
    | 'createMany'
    | 'createManyAndReturn'
    | 'update'
    | 'updateMany'
    | 'upsert'
    | 'delete'
    | 'deleteMany'
    | 'executeRaw'
    | 'queryRaw'
    | 'aggregate'
    | 'count'
    | 'runCommandRaw'
    | 'findRaw'
    | 'groupBy'

  /**
   * These options are being passed into the middleware as "params"
   */
  export type MiddlewareParams = {
    model?: ModelName
    action: PrismaAction
    args: any
    dataPath: string[]
    runInTransaction: boolean
  }

  /**
   * The `T` type makes sure, that the `return proceed` is not forgotten in the middleware implementation
   */
  export type Middleware<T = any> = (
    params: MiddlewareParams,
    next: (params: MiddlewareParams) => $Utils.JsPromise<T>,
  ) => $Utils.JsPromise<T>

  // tested in getLogLevel.test.ts
  export function getLogLevel(log: Array<LogLevel | LogDefinition>): LogLevel | undefined;

  /**
   * `PrismaClient` proxy available in interactive transactions.
   */
  export type TransactionClient = Omit<Prisma.DefaultPrismaClient, runtime.ITXClientDenyList>

  export type Datasource = {
    url?: string
  }

  /**
   * Count Types
   */


  /**
   * Count Type DeviceCountOutputType
   */

  export type DeviceCountOutputType = {
    sensors: number
    sensorReadings: number
    actuators: number
    alerts: number
  }

  export type DeviceCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    sensors?: boolean | DeviceCountOutputTypeCountSensorsArgs
    sensorReadings?: boolean | DeviceCountOutputTypeCountSensorReadingsArgs
    actuators?: boolean | DeviceCountOutputTypeCountActuatorsArgs
    alerts?: boolean | DeviceCountOutputTypeCountAlertsArgs
  }

  // Custom InputTypes
  /**
   * DeviceCountOutputType without action
   */
  export type DeviceCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceCountOutputType
     */
    select?: DeviceCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * DeviceCountOutputType without action
   */
  export type DeviceCountOutputTypeCountSensorsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: SensorWhereInput
  }

  /**
   * DeviceCountOutputType without action
   */
  export type DeviceCountOutputTypeCountSensorReadingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: SensorReadingWhereInput
  }

  /**
   * DeviceCountOutputType without action
   */
  export type DeviceCountOutputTypeCountActuatorsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: ActuatorWhereInput
  }

  /**
   * DeviceCountOutputType without action
   */
  export type DeviceCountOutputTypeCountAlertsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: DeviceAlertWhereInput
  }


  /**
   * Count Type SensorCountOutputType
   */

  export type SensorCountOutputType = {
    readings: number
  }

  export type SensorCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    readings?: boolean | SensorCountOutputTypeCountReadingsArgs
  }

  // Custom InputTypes
  /**
   * SensorCountOutputType without action
   */
  export type SensorCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorCountOutputType
     */
    select?: SensorCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * SensorCountOutputType without action
   */
  export type SensorCountOutputTypeCountReadingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: SensorReadingWhereInput
  }


  /**
   * Count Type ActuatorCountOutputType
   */

  export type ActuatorCountOutputType = {
    commands: number
  }

  export type ActuatorCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    commands?: boolean | ActuatorCountOutputTypeCountCommandsArgs
  }

  // Custom InputTypes
  /**
   * ActuatorCountOutputType without action
   */
  export type ActuatorCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCountOutputType
     */
    select?: ActuatorCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * ActuatorCountOutputType without action
   */
  export type ActuatorCountOutputTypeCountCommandsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: ActuatorCommandWhereInput
  }


  /**
   * Models
   */

  /**
   * Model Device
   */

  export type AggregateDevice = {
    _count: DeviceCountAggregateOutputType | null
    _min: DeviceMinAggregateOutputType | null
    _max: DeviceMaxAggregateOutputType | null
  }

  export type DeviceMinAggregateOutputType = {
    id: string | null
    tenantId: string | null
    deviceId: string | null
    name: string | null
    type: $Enums.DeviceType | null
    status: $Enums.DeviceStatus | null
    lastSeen: Date | null
    fieldId: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type DeviceMaxAggregateOutputType = {
    id: string | null
    tenantId: string | null
    deviceId: string | null
    name: string | null
    type: $Enums.DeviceType | null
    status: $Enums.DeviceStatus | null
    lastSeen: Date | null
    fieldId: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type DeviceCountAggregateOutputType = {
    id: number
    tenantId: number
    deviceId: number
    name: number
    type: number
    status: number
    lastSeen: number
    metadata: number
    fieldId: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type DeviceMinAggregateInputType = {
    id?: true
    tenantId?: true
    deviceId?: true
    name?: true
    type?: true
    status?: true
    lastSeen?: true
    fieldId?: true
    createdAt?: true
    updatedAt?: true
  }

  export type DeviceMaxAggregateInputType = {
    id?: true
    tenantId?: true
    deviceId?: true
    name?: true
    type?: true
    status?: true
    lastSeen?: true
    fieldId?: true
    createdAt?: true
    updatedAt?: true
  }

  export type DeviceCountAggregateInputType = {
    id?: true
    tenantId?: true
    deviceId?: true
    name?: true
    type?: true
    status?: true
    lastSeen?: true
    metadata?: true
    fieldId?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type DeviceAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Device to aggregate.
     */
    where?: DeviceWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Devices to fetch.
     */
    orderBy?: DeviceOrderByWithRelationInput | DeviceOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: DeviceWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Devices from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Devices.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Devices
    **/
    _count?: true | DeviceCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: DeviceMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: DeviceMaxAggregateInputType
  }

  export type GetDeviceAggregateType<T extends DeviceAggregateArgs> = {
        [P in keyof T & keyof AggregateDevice]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateDevice[P]>
      : GetScalarType<T[P], AggregateDevice[P]>
  }




  export type DeviceGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: DeviceWhereInput
    orderBy?: DeviceOrderByWithAggregationInput | DeviceOrderByWithAggregationInput[]
    by: DeviceScalarFieldEnum[] | DeviceScalarFieldEnum
    having?: DeviceScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: DeviceCountAggregateInputType | true
    _min?: DeviceMinAggregateInputType
    _max?: DeviceMaxAggregateInputType
  }

  export type DeviceGroupByOutputType = {
    id: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status: $Enums.DeviceStatus
    lastSeen: Date | null
    metadata: JsonValue | null
    fieldId: string | null
    createdAt: Date
    updatedAt: Date
    _count: DeviceCountAggregateOutputType | null
    _min: DeviceMinAggregateOutputType | null
    _max: DeviceMaxAggregateOutputType | null
  }

  type GetDeviceGroupByPayload<T extends DeviceGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<DeviceGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof DeviceGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], DeviceGroupByOutputType[P]>
            : GetScalarType<T[P], DeviceGroupByOutputType[P]>
        }
      >
    >


  export type DeviceSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    deviceId?: boolean
    name?: boolean
    type?: boolean
    status?: boolean
    lastSeen?: boolean
    metadata?: boolean
    fieldId?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    sensors?: boolean | Device$sensorsArgs<ExtArgs>
    sensorReadings?: boolean | Device$sensorReadingsArgs<ExtArgs>
    actuators?: boolean | Device$actuatorsArgs<ExtArgs>
    alerts?: boolean | Device$alertsArgs<ExtArgs>
    _count?: boolean | DeviceCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["device"]>

  export type DeviceSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    deviceId?: boolean
    name?: boolean
    type?: boolean
    status?: boolean
    lastSeen?: boolean
    metadata?: boolean
    fieldId?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["device"]>

  export type DeviceSelectScalar = {
    id?: boolean
    tenantId?: boolean
    deviceId?: boolean
    name?: boolean
    type?: boolean
    status?: boolean
    lastSeen?: boolean
    metadata?: boolean
    fieldId?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type DeviceInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    sensors?: boolean | Device$sensorsArgs<ExtArgs>
    sensorReadings?: boolean | Device$sensorReadingsArgs<ExtArgs>
    actuators?: boolean | Device$actuatorsArgs<ExtArgs>
    alerts?: boolean | Device$alertsArgs<ExtArgs>
    _count?: boolean | DeviceCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type DeviceIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {}

  export type $DevicePayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Device"
    objects: {
      sensors: Prisma.$SensorPayload<ExtArgs>[]
      sensorReadings: Prisma.$SensorReadingPayload<ExtArgs>[]
      actuators: Prisma.$ActuatorPayload<ExtArgs>[]
      alerts: Prisma.$DeviceAlertPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      tenantId: string
      deviceId: string
      name: string
      type: $Enums.DeviceType
      status: $Enums.DeviceStatus
      lastSeen: Date | null
      metadata: Prisma.JsonValue | null
      fieldId: string | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["device"]>
    composites: {}
  }

  type DeviceGetPayload<S extends boolean | null | undefined | DeviceDefaultArgs> = $Result.GetResult<Prisma.$DevicePayload, S>

  type DeviceCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<DeviceFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: DeviceCountAggregateInputType | true
    }

  export interface DeviceDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Device'], meta: { name: 'Device' } }
    /**
     * Find zero or one Device that matches the filter.
     * @param {DeviceFindUniqueArgs} args - Arguments to find a Device
     * @example
     * // Get one Device
     * const device = await prisma.device.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends DeviceFindUniqueArgs>(args: SelectSubset<T, DeviceFindUniqueArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Device that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {DeviceFindUniqueOrThrowArgs} args - Arguments to find a Device
     * @example
     * // Get one Device
     * const device = await prisma.device.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends DeviceFindUniqueOrThrowArgs>(args: SelectSubset<T, DeviceFindUniqueOrThrowArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Device that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceFindFirstArgs} args - Arguments to find a Device
     * @example
     * // Get one Device
     * const device = await prisma.device.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends DeviceFindFirstArgs>(args?: SelectSubset<T, DeviceFindFirstArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Device that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceFindFirstOrThrowArgs} args - Arguments to find a Device
     * @example
     * // Get one Device
     * const device = await prisma.device.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends DeviceFindFirstOrThrowArgs>(args?: SelectSubset<T, DeviceFindFirstOrThrowArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Devices that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Devices
     * const devices = await prisma.device.findMany()
     * 
     * // Get first 10 Devices
     * const devices = await prisma.device.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const deviceWithIdOnly = await prisma.device.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends DeviceFindManyArgs>(args?: SelectSubset<T, DeviceFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Device.
     * @param {DeviceCreateArgs} args - Arguments to create a Device.
     * @example
     * // Create one Device
     * const Device = await prisma.device.create({
     *   data: {
     *     // ... data to create a Device
     *   }
     * })
     * 
     */
    create<T extends DeviceCreateArgs>(args: SelectSubset<T, DeviceCreateArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Devices.
     * @param {DeviceCreateManyArgs} args - Arguments to create many Devices.
     * @example
     * // Create many Devices
     * const device = await prisma.device.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends DeviceCreateManyArgs>(args?: SelectSubset<T, DeviceCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Devices and returns the data saved in the database.
     * @param {DeviceCreateManyAndReturnArgs} args - Arguments to create many Devices.
     * @example
     * // Create many Devices
     * const device = await prisma.device.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Devices and only return the `id`
     * const deviceWithIdOnly = await prisma.device.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends DeviceCreateManyAndReturnArgs>(args?: SelectSubset<T, DeviceCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Device.
     * @param {DeviceDeleteArgs} args - Arguments to delete one Device.
     * @example
     * // Delete one Device
     * const Device = await prisma.device.delete({
     *   where: {
     *     // ... filter to delete one Device
     *   }
     * })
     * 
     */
    delete<T extends DeviceDeleteArgs>(args: SelectSubset<T, DeviceDeleteArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Device.
     * @param {DeviceUpdateArgs} args - Arguments to update one Device.
     * @example
     * // Update one Device
     * const device = await prisma.device.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends DeviceUpdateArgs>(args: SelectSubset<T, DeviceUpdateArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Devices.
     * @param {DeviceDeleteManyArgs} args - Arguments to filter Devices to delete.
     * @example
     * // Delete a few Devices
     * const { count } = await prisma.device.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends DeviceDeleteManyArgs>(args?: SelectSubset<T, DeviceDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Devices.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Devices
     * const device = await prisma.device.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends DeviceUpdateManyArgs>(args: SelectSubset<T, DeviceUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Device.
     * @param {DeviceUpsertArgs} args - Arguments to update or create a Device.
     * @example
     * // Update or create a Device
     * const device = await prisma.device.upsert({
     *   create: {
     *     // ... data to create a Device
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Device we want to update
     *   }
     * })
     */
    upsert<T extends DeviceUpsertArgs>(args: SelectSubset<T, DeviceUpsertArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Devices.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceCountArgs} args - Arguments to filter Devices to count.
     * @example
     * // Count the number of Devices
     * const count = await prisma.device.count({
     *   where: {
     *     // ... the filter for the Devices we want to count
     *   }
     * })
    **/
    count<T extends DeviceCountArgs>(
      args?: Subset<T, DeviceCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], DeviceCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Device.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends DeviceAggregateArgs>(args: Subset<T, DeviceAggregateArgs>): Prisma.PrismaPromise<GetDeviceAggregateType<T>>

    /**
     * Group by Device.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends DeviceGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: DeviceGroupByArgs['orderBy'] }
        : { orderBy?: DeviceGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends MaybeTupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, DeviceGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetDeviceGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Device model
   */
  readonly fields: DeviceFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Device.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__DeviceClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    sensors<T extends Device$sensorsArgs<ExtArgs> = {}>(args?: Subset<T, Device$sensorsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findMany"> | Null>
    sensorReadings<T extends Device$sensorReadingsArgs<ExtArgs> = {}>(args?: Subset<T, Device$sensorReadingsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findMany"> | Null>
    actuators<T extends Device$actuatorsArgs<ExtArgs> = {}>(args?: Subset<T, Device$actuatorsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findMany"> | Null>
    alerts<T extends Device$alertsArgs<ExtArgs> = {}>(args?: Subset<T, Device$alertsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "findMany"> | Null>
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): $Utils.JsPromise<TResult1 | TResult2>
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): $Utils.JsPromise<T | TResult>
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): $Utils.JsPromise<T>
  }




  /**
   * Fields of the Device model
   */ 
  interface DeviceFieldRefs {
    readonly id: FieldRef<"Device", 'String'>
    readonly tenantId: FieldRef<"Device", 'String'>
    readonly deviceId: FieldRef<"Device", 'String'>
    readonly name: FieldRef<"Device", 'String'>
    readonly type: FieldRef<"Device", 'DeviceType'>
    readonly status: FieldRef<"Device", 'DeviceStatus'>
    readonly lastSeen: FieldRef<"Device", 'DateTime'>
    readonly metadata: FieldRef<"Device", 'Json'>
    readonly fieldId: FieldRef<"Device", 'String'>
    readonly createdAt: FieldRef<"Device", 'DateTime'>
    readonly updatedAt: FieldRef<"Device", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Device findUnique
   */
  export type DeviceFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * Filter, which Device to fetch.
     */
    where: DeviceWhereUniqueInput
  }

  /**
   * Device findUniqueOrThrow
   */
  export type DeviceFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * Filter, which Device to fetch.
     */
    where: DeviceWhereUniqueInput
  }

  /**
   * Device findFirst
   */
  export type DeviceFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * Filter, which Device to fetch.
     */
    where?: DeviceWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Devices to fetch.
     */
    orderBy?: DeviceOrderByWithRelationInput | DeviceOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Devices.
     */
    cursor?: DeviceWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Devices from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Devices.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Devices.
     */
    distinct?: DeviceScalarFieldEnum | DeviceScalarFieldEnum[]
  }

  /**
   * Device findFirstOrThrow
   */
  export type DeviceFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * Filter, which Device to fetch.
     */
    where?: DeviceWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Devices to fetch.
     */
    orderBy?: DeviceOrderByWithRelationInput | DeviceOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Devices.
     */
    cursor?: DeviceWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Devices from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Devices.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Devices.
     */
    distinct?: DeviceScalarFieldEnum | DeviceScalarFieldEnum[]
  }

  /**
   * Device findMany
   */
  export type DeviceFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * Filter, which Devices to fetch.
     */
    where?: DeviceWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Devices to fetch.
     */
    orderBy?: DeviceOrderByWithRelationInput | DeviceOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Devices.
     */
    cursor?: DeviceWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Devices from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Devices.
     */
    skip?: number
    distinct?: DeviceScalarFieldEnum | DeviceScalarFieldEnum[]
  }

  /**
   * Device create
   */
  export type DeviceCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * The data needed to create a Device.
     */
    data: XOR<DeviceCreateInput, DeviceUncheckedCreateInput>
  }

  /**
   * Device createMany
   */
  export type DeviceCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Devices.
     */
    data: DeviceCreateManyInput | DeviceCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Device createManyAndReturn
   */
  export type DeviceCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Devices.
     */
    data: DeviceCreateManyInput | DeviceCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Device update
   */
  export type DeviceUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * The data needed to update a Device.
     */
    data: XOR<DeviceUpdateInput, DeviceUncheckedUpdateInput>
    /**
     * Choose, which Device to update.
     */
    where: DeviceWhereUniqueInput
  }

  /**
   * Device updateMany
   */
  export type DeviceUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Devices.
     */
    data: XOR<DeviceUpdateManyMutationInput, DeviceUncheckedUpdateManyInput>
    /**
     * Filter which Devices to update
     */
    where?: DeviceWhereInput
  }

  /**
   * Device upsert
   */
  export type DeviceUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * The filter to search for the Device to update in case it exists.
     */
    where: DeviceWhereUniqueInput
    /**
     * In case the Device found by the `where` argument doesn't exist, create a new Device with this data.
     */
    create: XOR<DeviceCreateInput, DeviceUncheckedCreateInput>
    /**
     * In case the Device was found with the provided `where` argument, update it with this data.
     */
    update: XOR<DeviceUpdateInput, DeviceUncheckedUpdateInput>
  }

  /**
   * Device delete
   */
  export type DeviceDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
    /**
     * Filter which Device to delete.
     */
    where: DeviceWhereUniqueInput
  }

  /**
   * Device deleteMany
   */
  export type DeviceDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Devices to delete
     */
    where?: DeviceWhereInput
  }

  /**
   * Device.sensors
   */
  export type Device$sensorsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    where?: SensorWhereInput
    orderBy?: SensorOrderByWithRelationInput | SensorOrderByWithRelationInput[]
    cursor?: SensorWhereUniqueInput
    take?: number
    skip?: number
    distinct?: SensorScalarFieldEnum | SensorScalarFieldEnum[]
  }

  /**
   * Device.sensorReadings
   */
  export type Device$sensorReadingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    where?: SensorReadingWhereInput
    orderBy?: SensorReadingOrderByWithRelationInput | SensorReadingOrderByWithRelationInput[]
    cursor?: SensorReadingWhereUniqueInput
    take?: number
    skip?: number
    distinct?: SensorReadingScalarFieldEnum | SensorReadingScalarFieldEnum[]
  }

  /**
   * Device.actuators
   */
  export type Device$actuatorsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    where?: ActuatorWhereInput
    orderBy?: ActuatorOrderByWithRelationInput | ActuatorOrderByWithRelationInput[]
    cursor?: ActuatorWhereUniqueInput
    take?: number
    skip?: number
    distinct?: ActuatorScalarFieldEnum | ActuatorScalarFieldEnum[]
  }

  /**
   * Device.alerts
   */
  export type Device$alertsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    where?: DeviceAlertWhereInput
    orderBy?: DeviceAlertOrderByWithRelationInput | DeviceAlertOrderByWithRelationInput[]
    cursor?: DeviceAlertWhereUniqueInput
    take?: number
    skip?: number
    distinct?: DeviceAlertScalarFieldEnum | DeviceAlertScalarFieldEnum[]
  }

  /**
   * Device without action
   */
  export type DeviceDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Device
     */
    select?: DeviceSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceInclude<ExtArgs> | null
  }


  /**
   * Model Sensor
   */

  export type AggregateSensor = {
    _count: SensorCountAggregateOutputType | null
    _avg: SensorAvgAggregateOutputType | null
    _sum: SensorSumAggregateOutputType | null
    _min: SensorMinAggregateOutputType | null
    _max: SensorMaxAggregateOutputType | null
  }

  export type SensorAvgAggregateOutputType = {
    lastReading: number | null
  }

  export type SensorSumAggregateOutputType = {
    lastReading: number | null
  }

  export type SensorMinAggregateOutputType = {
    id: string | null
    deviceId: string | null
    sensorType: $Enums.SensorType | null
    unit: string | null
    lastReading: number | null
    lastReadingAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type SensorMaxAggregateOutputType = {
    id: string | null
    deviceId: string | null
    sensorType: $Enums.SensorType | null
    unit: string | null
    lastReading: number | null
    lastReadingAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type SensorCountAggregateOutputType = {
    id: number
    deviceId: number
    sensorType: number
    unit: number
    calibrationData: number
    lastReading: number
    lastReadingAt: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type SensorAvgAggregateInputType = {
    lastReading?: true
  }

  export type SensorSumAggregateInputType = {
    lastReading?: true
  }

  export type SensorMinAggregateInputType = {
    id?: true
    deviceId?: true
    sensorType?: true
    unit?: true
    lastReading?: true
    lastReadingAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type SensorMaxAggregateInputType = {
    id?: true
    deviceId?: true
    sensorType?: true
    unit?: true
    lastReading?: true
    lastReadingAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type SensorCountAggregateInputType = {
    id?: true
    deviceId?: true
    sensorType?: true
    unit?: true
    calibrationData?: true
    lastReading?: true
    lastReadingAt?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type SensorAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Sensor to aggregate.
     */
    where?: SensorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Sensors to fetch.
     */
    orderBy?: SensorOrderByWithRelationInput | SensorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: SensorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Sensors from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Sensors.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Sensors
    **/
    _count?: true | SensorCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: SensorAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: SensorSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: SensorMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: SensorMaxAggregateInputType
  }

  export type GetSensorAggregateType<T extends SensorAggregateArgs> = {
        [P in keyof T & keyof AggregateSensor]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateSensor[P]>
      : GetScalarType<T[P], AggregateSensor[P]>
  }




  export type SensorGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: SensorWhereInput
    orderBy?: SensorOrderByWithAggregationInput | SensorOrderByWithAggregationInput[]
    by: SensorScalarFieldEnum[] | SensorScalarFieldEnum
    having?: SensorScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: SensorCountAggregateInputType | true
    _avg?: SensorAvgAggregateInputType
    _sum?: SensorSumAggregateInputType
    _min?: SensorMinAggregateInputType
    _max?: SensorMaxAggregateInputType
  }

  export type SensorGroupByOutputType = {
    id: string
    deviceId: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData: JsonValue | null
    lastReading: number | null
    lastReadingAt: Date | null
    createdAt: Date
    updatedAt: Date
    _count: SensorCountAggregateOutputType | null
    _avg: SensorAvgAggregateOutputType | null
    _sum: SensorSumAggregateOutputType | null
    _min: SensorMinAggregateOutputType | null
    _max: SensorMaxAggregateOutputType | null
  }

  type GetSensorGroupByPayload<T extends SensorGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<SensorGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof SensorGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], SensorGroupByOutputType[P]>
            : GetScalarType<T[P], SensorGroupByOutputType[P]>
        }
      >
    >


  export type SensorSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    sensorType?: boolean
    unit?: boolean
    calibrationData?: boolean
    lastReading?: boolean
    lastReadingAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    device?: boolean | DeviceDefaultArgs<ExtArgs>
    readings?: boolean | Sensor$readingsArgs<ExtArgs>
    _count?: boolean | SensorCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["sensor"]>

  export type SensorSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    sensorType?: boolean
    unit?: boolean
    calibrationData?: boolean
    lastReading?: boolean
    lastReadingAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["sensor"]>

  export type SensorSelectScalar = {
    id?: boolean
    deviceId?: boolean
    sensorType?: boolean
    unit?: boolean
    calibrationData?: boolean
    lastReading?: boolean
    lastReadingAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type SensorInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    device?: boolean | DeviceDefaultArgs<ExtArgs>
    readings?: boolean | Sensor$readingsArgs<ExtArgs>
    _count?: boolean | SensorCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type SensorIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }

  export type $SensorPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Sensor"
    objects: {
      device: Prisma.$DevicePayload<ExtArgs>
      readings: Prisma.$SensorReadingPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      deviceId: string
      sensorType: $Enums.SensorType
      unit: string
      calibrationData: Prisma.JsonValue | null
      lastReading: number | null
      lastReadingAt: Date | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["sensor"]>
    composites: {}
  }

  type SensorGetPayload<S extends boolean | null | undefined | SensorDefaultArgs> = $Result.GetResult<Prisma.$SensorPayload, S>

  type SensorCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<SensorFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: SensorCountAggregateInputType | true
    }

  export interface SensorDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Sensor'], meta: { name: 'Sensor' } }
    /**
     * Find zero or one Sensor that matches the filter.
     * @param {SensorFindUniqueArgs} args - Arguments to find a Sensor
     * @example
     * // Get one Sensor
     * const sensor = await prisma.sensor.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends SensorFindUniqueArgs>(args: SelectSubset<T, SensorFindUniqueArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Sensor that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {SensorFindUniqueOrThrowArgs} args - Arguments to find a Sensor
     * @example
     * // Get one Sensor
     * const sensor = await prisma.sensor.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends SensorFindUniqueOrThrowArgs>(args: SelectSubset<T, SensorFindUniqueOrThrowArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Sensor that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorFindFirstArgs} args - Arguments to find a Sensor
     * @example
     * // Get one Sensor
     * const sensor = await prisma.sensor.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends SensorFindFirstArgs>(args?: SelectSubset<T, SensorFindFirstArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Sensor that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorFindFirstOrThrowArgs} args - Arguments to find a Sensor
     * @example
     * // Get one Sensor
     * const sensor = await prisma.sensor.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends SensorFindFirstOrThrowArgs>(args?: SelectSubset<T, SensorFindFirstOrThrowArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Sensors that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Sensors
     * const sensors = await prisma.sensor.findMany()
     * 
     * // Get first 10 Sensors
     * const sensors = await prisma.sensor.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const sensorWithIdOnly = await prisma.sensor.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends SensorFindManyArgs>(args?: SelectSubset<T, SensorFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Sensor.
     * @param {SensorCreateArgs} args - Arguments to create a Sensor.
     * @example
     * // Create one Sensor
     * const Sensor = await prisma.sensor.create({
     *   data: {
     *     // ... data to create a Sensor
     *   }
     * })
     * 
     */
    create<T extends SensorCreateArgs>(args: SelectSubset<T, SensorCreateArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Sensors.
     * @param {SensorCreateManyArgs} args - Arguments to create many Sensors.
     * @example
     * // Create many Sensors
     * const sensor = await prisma.sensor.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends SensorCreateManyArgs>(args?: SelectSubset<T, SensorCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Sensors and returns the data saved in the database.
     * @param {SensorCreateManyAndReturnArgs} args - Arguments to create many Sensors.
     * @example
     * // Create many Sensors
     * const sensor = await prisma.sensor.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Sensors and only return the `id`
     * const sensorWithIdOnly = await prisma.sensor.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends SensorCreateManyAndReturnArgs>(args?: SelectSubset<T, SensorCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Sensor.
     * @param {SensorDeleteArgs} args - Arguments to delete one Sensor.
     * @example
     * // Delete one Sensor
     * const Sensor = await prisma.sensor.delete({
     *   where: {
     *     // ... filter to delete one Sensor
     *   }
     * })
     * 
     */
    delete<T extends SensorDeleteArgs>(args: SelectSubset<T, SensorDeleteArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Sensor.
     * @param {SensorUpdateArgs} args - Arguments to update one Sensor.
     * @example
     * // Update one Sensor
     * const sensor = await prisma.sensor.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends SensorUpdateArgs>(args: SelectSubset<T, SensorUpdateArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Sensors.
     * @param {SensorDeleteManyArgs} args - Arguments to filter Sensors to delete.
     * @example
     * // Delete a few Sensors
     * const { count } = await prisma.sensor.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends SensorDeleteManyArgs>(args?: SelectSubset<T, SensorDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Sensors.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Sensors
     * const sensor = await prisma.sensor.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends SensorUpdateManyArgs>(args: SelectSubset<T, SensorUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Sensor.
     * @param {SensorUpsertArgs} args - Arguments to update or create a Sensor.
     * @example
     * // Update or create a Sensor
     * const sensor = await prisma.sensor.upsert({
     *   create: {
     *     // ... data to create a Sensor
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Sensor we want to update
     *   }
     * })
     */
    upsert<T extends SensorUpsertArgs>(args: SelectSubset<T, SensorUpsertArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Sensors.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorCountArgs} args - Arguments to filter Sensors to count.
     * @example
     * // Count the number of Sensors
     * const count = await prisma.sensor.count({
     *   where: {
     *     // ... the filter for the Sensors we want to count
     *   }
     * })
    **/
    count<T extends SensorCountArgs>(
      args?: Subset<T, SensorCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], SensorCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Sensor.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends SensorAggregateArgs>(args: Subset<T, SensorAggregateArgs>): Prisma.PrismaPromise<GetSensorAggregateType<T>>

    /**
     * Group by Sensor.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends SensorGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: SensorGroupByArgs['orderBy'] }
        : { orderBy?: SensorGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends MaybeTupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, SensorGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetSensorGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Sensor model
   */
  readonly fields: SensorFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Sensor.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__SensorClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    device<T extends DeviceDefaultArgs<ExtArgs> = {}>(args?: Subset<T, DeviceDefaultArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    readings<T extends Sensor$readingsArgs<ExtArgs> = {}>(args?: Subset<T, Sensor$readingsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findMany"> | Null>
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): $Utils.JsPromise<TResult1 | TResult2>
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): $Utils.JsPromise<T | TResult>
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): $Utils.JsPromise<T>
  }




  /**
   * Fields of the Sensor model
   */ 
  interface SensorFieldRefs {
    readonly id: FieldRef<"Sensor", 'String'>
    readonly deviceId: FieldRef<"Sensor", 'String'>
    readonly sensorType: FieldRef<"Sensor", 'SensorType'>
    readonly unit: FieldRef<"Sensor", 'String'>
    readonly calibrationData: FieldRef<"Sensor", 'Json'>
    readonly lastReading: FieldRef<"Sensor", 'Float'>
    readonly lastReadingAt: FieldRef<"Sensor", 'DateTime'>
    readonly createdAt: FieldRef<"Sensor", 'DateTime'>
    readonly updatedAt: FieldRef<"Sensor", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Sensor findUnique
   */
  export type SensorFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * Filter, which Sensor to fetch.
     */
    where: SensorWhereUniqueInput
  }

  /**
   * Sensor findUniqueOrThrow
   */
  export type SensorFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * Filter, which Sensor to fetch.
     */
    where: SensorWhereUniqueInput
  }

  /**
   * Sensor findFirst
   */
  export type SensorFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * Filter, which Sensor to fetch.
     */
    where?: SensorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Sensors to fetch.
     */
    orderBy?: SensorOrderByWithRelationInput | SensorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Sensors.
     */
    cursor?: SensorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Sensors from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Sensors.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Sensors.
     */
    distinct?: SensorScalarFieldEnum | SensorScalarFieldEnum[]
  }

  /**
   * Sensor findFirstOrThrow
   */
  export type SensorFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * Filter, which Sensor to fetch.
     */
    where?: SensorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Sensors to fetch.
     */
    orderBy?: SensorOrderByWithRelationInput | SensorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Sensors.
     */
    cursor?: SensorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Sensors from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Sensors.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Sensors.
     */
    distinct?: SensorScalarFieldEnum | SensorScalarFieldEnum[]
  }

  /**
   * Sensor findMany
   */
  export type SensorFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * Filter, which Sensors to fetch.
     */
    where?: SensorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Sensors to fetch.
     */
    orderBy?: SensorOrderByWithRelationInput | SensorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Sensors.
     */
    cursor?: SensorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Sensors from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Sensors.
     */
    skip?: number
    distinct?: SensorScalarFieldEnum | SensorScalarFieldEnum[]
  }

  /**
   * Sensor create
   */
  export type SensorCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * The data needed to create a Sensor.
     */
    data: XOR<SensorCreateInput, SensorUncheckedCreateInput>
  }

  /**
   * Sensor createMany
   */
  export type SensorCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Sensors.
     */
    data: SensorCreateManyInput | SensorCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Sensor createManyAndReturn
   */
  export type SensorCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Sensors.
     */
    data: SensorCreateManyInput | SensorCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * Sensor update
   */
  export type SensorUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * The data needed to update a Sensor.
     */
    data: XOR<SensorUpdateInput, SensorUncheckedUpdateInput>
    /**
     * Choose, which Sensor to update.
     */
    where: SensorWhereUniqueInput
  }

  /**
   * Sensor updateMany
   */
  export type SensorUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Sensors.
     */
    data: XOR<SensorUpdateManyMutationInput, SensorUncheckedUpdateManyInput>
    /**
     * Filter which Sensors to update
     */
    where?: SensorWhereInput
  }

  /**
   * Sensor upsert
   */
  export type SensorUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * The filter to search for the Sensor to update in case it exists.
     */
    where: SensorWhereUniqueInput
    /**
     * In case the Sensor found by the `where` argument doesn't exist, create a new Sensor with this data.
     */
    create: XOR<SensorCreateInput, SensorUncheckedCreateInput>
    /**
     * In case the Sensor was found with the provided `where` argument, update it with this data.
     */
    update: XOR<SensorUpdateInput, SensorUncheckedUpdateInput>
  }

  /**
   * Sensor delete
   */
  export type SensorDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
    /**
     * Filter which Sensor to delete.
     */
    where: SensorWhereUniqueInput
  }

  /**
   * Sensor deleteMany
   */
  export type SensorDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Sensors to delete
     */
    where?: SensorWhereInput
  }

  /**
   * Sensor.readings
   */
  export type Sensor$readingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    where?: SensorReadingWhereInput
    orderBy?: SensorReadingOrderByWithRelationInput | SensorReadingOrderByWithRelationInput[]
    cursor?: SensorReadingWhereUniqueInput
    take?: number
    skip?: number
    distinct?: SensorReadingScalarFieldEnum | SensorReadingScalarFieldEnum[]
  }

  /**
   * Sensor without action
   */
  export type SensorDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Sensor
     */
    select?: SensorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorInclude<ExtArgs> | null
  }


  /**
   * Model SensorReading
   */

  export type AggregateSensorReading = {
    _count: SensorReadingCountAggregateOutputType | null
    _avg: SensorReadingAvgAggregateOutputType | null
    _sum: SensorReadingSumAggregateOutputType | null
    _min: SensorReadingMinAggregateOutputType | null
    _max: SensorReadingMaxAggregateOutputType | null
  }

  export type SensorReadingAvgAggregateOutputType = {
    value: number | null
    quality: number | null
  }

  export type SensorReadingSumAggregateOutputType = {
    value: number | null
    quality: number | null
  }

  export type SensorReadingMinAggregateOutputType = {
    id: string | null
    sensorId: string | null
    deviceId: string | null
    value: number | null
    unit: string | null
    timestamp: Date | null
    quality: number | null
  }

  export type SensorReadingMaxAggregateOutputType = {
    id: string | null
    sensorId: string | null
    deviceId: string | null
    value: number | null
    unit: string | null
    timestamp: Date | null
    quality: number | null
  }

  export type SensorReadingCountAggregateOutputType = {
    id: number
    sensorId: number
    deviceId: number
    value: number
    unit: number
    timestamp: number
    quality: number
    metadata: number
    _all: number
  }


  export type SensorReadingAvgAggregateInputType = {
    value?: true
    quality?: true
  }

  export type SensorReadingSumAggregateInputType = {
    value?: true
    quality?: true
  }

  export type SensorReadingMinAggregateInputType = {
    id?: true
    sensorId?: true
    deviceId?: true
    value?: true
    unit?: true
    timestamp?: true
    quality?: true
  }

  export type SensorReadingMaxAggregateInputType = {
    id?: true
    sensorId?: true
    deviceId?: true
    value?: true
    unit?: true
    timestamp?: true
    quality?: true
  }

  export type SensorReadingCountAggregateInputType = {
    id?: true
    sensorId?: true
    deviceId?: true
    value?: true
    unit?: true
    timestamp?: true
    quality?: true
    metadata?: true
    _all?: true
  }

  export type SensorReadingAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which SensorReading to aggregate.
     */
    where?: SensorReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SensorReadings to fetch.
     */
    orderBy?: SensorReadingOrderByWithRelationInput | SensorReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: SensorReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SensorReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SensorReadings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned SensorReadings
    **/
    _count?: true | SensorReadingCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: SensorReadingAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: SensorReadingSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: SensorReadingMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: SensorReadingMaxAggregateInputType
  }

  export type GetSensorReadingAggregateType<T extends SensorReadingAggregateArgs> = {
        [P in keyof T & keyof AggregateSensorReading]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateSensorReading[P]>
      : GetScalarType<T[P], AggregateSensorReading[P]>
  }




  export type SensorReadingGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: SensorReadingWhereInput
    orderBy?: SensorReadingOrderByWithAggregationInput | SensorReadingOrderByWithAggregationInput[]
    by: SensorReadingScalarFieldEnum[] | SensorReadingScalarFieldEnum
    having?: SensorReadingScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: SensorReadingCountAggregateInputType | true
    _avg?: SensorReadingAvgAggregateInputType
    _sum?: SensorReadingSumAggregateInputType
    _min?: SensorReadingMinAggregateInputType
    _max?: SensorReadingMaxAggregateInputType
  }

  export type SensorReadingGroupByOutputType = {
    id: string
    sensorId: string
    deviceId: string
    value: number
    unit: string
    timestamp: Date
    quality: number | null
    metadata: JsonValue | null
    _count: SensorReadingCountAggregateOutputType | null
    _avg: SensorReadingAvgAggregateOutputType | null
    _sum: SensorReadingSumAggregateOutputType | null
    _min: SensorReadingMinAggregateOutputType | null
    _max: SensorReadingMaxAggregateOutputType | null
  }

  type GetSensorReadingGroupByPayload<T extends SensorReadingGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<SensorReadingGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof SensorReadingGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], SensorReadingGroupByOutputType[P]>
            : GetScalarType<T[P], SensorReadingGroupByOutputType[P]>
        }
      >
    >


  export type SensorReadingSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    sensorId?: boolean
    deviceId?: boolean
    value?: boolean
    unit?: boolean
    timestamp?: boolean
    quality?: boolean
    metadata?: boolean
    sensor?: boolean | SensorDefaultArgs<ExtArgs>
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["sensorReading"]>

  export type SensorReadingSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    sensorId?: boolean
    deviceId?: boolean
    value?: boolean
    unit?: boolean
    timestamp?: boolean
    quality?: boolean
    metadata?: boolean
    sensor?: boolean | SensorDefaultArgs<ExtArgs>
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["sensorReading"]>

  export type SensorReadingSelectScalar = {
    id?: boolean
    sensorId?: boolean
    deviceId?: boolean
    value?: boolean
    unit?: boolean
    timestamp?: boolean
    quality?: boolean
    metadata?: boolean
  }

  export type SensorReadingInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    sensor?: boolean | SensorDefaultArgs<ExtArgs>
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }
  export type SensorReadingIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    sensor?: boolean | SensorDefaultArgs<ExtArgs>
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }

  export type $SensorReadingPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "SensorReading"
    objects: {
      sensor: Prisma.$SensorPayload<ExtArgs>
      device: Prisma.$DevicePayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      sensorId: string
      deviceId: string
      value: number
      unit: string
      timestamp: Date
      quality: number | null
      metadata: Prisma.JsonValue | null
    }, ExtArgs["result"]["sensorReading"]>
    composites: {}
  }

  type SensorReadingGetPayload<S extends boolean | null | undefined | SensorReadingDefaultArgs> = $Result.GetResult<Prisma.$SensorReadingPayload, S>

  type SensorReadingCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<SensorReadingFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: SensorReadingCountAggregateInputType | true
    }

  export interface SensorReadingDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['SensorReading'], meta: { name: 'SensorReading' } }
    /**
     * Find zero or one SensorReading that matches the filter.
     * @param {SensorReadingFindUniqueArgs} args - Arguments to find a SensorReading
     * @example
     * // Get one SensorReading
     * const sensorReading = await prisma.sensorReading.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends SensorReadingFindUniqueArgs>(args: SelectSubset<T, SensorReadingFindUniqueArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one SensorReading that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {SensorReadingFindUniqueOrThrowArgs} args - Arguments to find a SensorReading
     * @example
     * // Get one SensorReading
     * const sensorReading = await prisma.sensorReading.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends SensorReadingFindUniqueOrThrowArgs>(args: SelectSubset<T, SensorReadingFindUniqueOrThrowArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first SensorReading that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingFindFirstArgs} args - Arguments to find a SensorReading
     * @example
     * // Get one SensorReading
     * const sensorReading = await prisma.sensorReading.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends SensorReadingFindFirstArgs>(args?: SelectSubset<T, SensorReadingFindFirstArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first SensorReading that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingFindFirstOrThrowArgs} args - Arguments to find a SensorReading
     * @example
     * // Get one SensorReading
     * const sensorReading = await prisma.sensorReading.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends SensorReadingFindFirstOrThrowArgs>(args?: SelectSubset<T, SensorReadingFindFirstOrThrowArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more SensorReadings that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all SensorReadings
     * const sensorReadings = await prisma.sensorReading.findMany()
     * 
     * // Get first 10 SensorReadings
     * const sensorReadings = await prisma.sensorReading.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const sensorReadingWithIdOnly = await prisma.sensorReading.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends SensorReadingFindManyArgs>(args?: SelectSubset<T, SensorReadingFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a SensorReading.
     * @param {SensorReadingCreateArgs} args - Arguments to create a SensorReading.
     * @example
     * // Create one SensorReading
     * const SensorReading = await prisma.sensorReading.create({
     *   data: {
     *     // ... data to create a SensorReading
     *   }
     * })
     * 
     */
    create<T extends SensorReadingCreateArgs>(args: SelectSubset<T, SensorReadingCreateArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many SensorReadings.
     * @param {SensorReadingCreateManyArgs} args - Arguments to create many SensorReadings.
     * @example
     * // Create many SensorReadings
     * const sensorReading = await prisma.sensorReading.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends SensorReadingCreateManyArgs>(args?: SelectSubset<T, SensorReadingCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many SensorReadings and returns the data saved in the database.
     * @param {SensorReadingCreateManyAndReturnArgs} args - Arguments to create many SensorReadings.
     * @example
     * // Create many SensorReadings
     * const sensorReading = await prisma.sensorReading.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many SensorReadings and only return the `id`
     * const sensorReadingWithIdOnly = await prisma.sensorReading.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends SensorReadingCreateManyAndReturnArgs>(args?: SelectSubset<T, SensorReadingCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a SensorReading.
     * @param {SensorReadingDeleteArgs} args - Arguments to delete one SensorReading.
     * @example
     * // Delete one SensorReading
     * const SensorReading = await prisma.sensorReading.delete({
     *   where: {
     *     // ... filter to delete one SensorReading
     *   }
     * })
     * 
     */
    delete<T extends SensorReadingDeleteArgs>(args: SelectSubset<T, SensorReadingDeleteArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one SensorReading.
     * @param {SensorReadingUpdateArgs} args - Arguments to update one SensorReading.
     * @example
     * // Update one SensorReading
     * const sensorReading = await prisma.sensorReading.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends SensorReadingUpdateArgs>(args: SelectSubset<T, SensorReadingUpdateArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more SensorReadings.
     * @param {SensorReadingDeleteManyArgs} args - Arguments to filter SensorReadings to delete.
     * @example
     * // Delete a few SensorReadings
     * const { count } = await prisma.sensorReading.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends SensorReadingDeleteManyArgs>(args?: SelectSubset<T, SensorReadingDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more SensorReadings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many SensorReadings
     * const sensorReading = await prisma.sensorReading.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends SensorReadingUpdateManyArgs>(args: SelectSubset<T, SensorReadingUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one SensorReading.
     * @param {SensorReadingUpsertArgs} args - Arguments to update or create a SensorReading.
     * @example
     * // Update or create a SensorReading
     * const sensorReading = await prisma.sensorReading.upsert({
     *   create: {
     *     // ... data to create a SensorReading
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the SensorReading we want to update
     *   }
     * })
     */
    upsert<T extends SensorReadingUpsertArgs>(args: SelectSubset<T, SensorReadingUpsertArgs<ExtArgs>>): Prisma__SensorReadingClient<$Result.GetResult<Prisma.$SensorReadingPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of SensorReadings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingCountArgs} args - Arguments to filter SensorReadings to count.
     * @example
     * // Count the number of SensorReadings
     * const count = await prisma.sensorReading.count({
     *   where: {
     *     // ... the filter for the SensorReadings we want to count
     *   }
     * })
    **/
    count<T extends SensorReadingCountArgs>(
      args?: Subset<T, SensorReadingCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], SensorReadingCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a SensorReading.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends SensorReadingAggregateArgs>(args: Subset<T, SensorReadingAggregateArgs>): Prisma.PrismaPromise<GetSensorReadingAggregateType<T>>

    /**
     * Group by SensorReading.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SensorReadingGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends SensorReadingGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: SensorReadingGroupByArgs['orderBy'] }
        : { orderBy?: SensorReadingGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends MaybeTupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, SensorReadingGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetSensorReadingGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the SensorReading model
   */
  readonly fields: SensorReadingFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for SensorReading.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__SensorReadingClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    sensor<T extends SensorDefaultArgs<ExtArgs> = {}>(args?: Subset<T, SensorDefaultArgs<ExtArgs>>): Prisma__SensorClient<$Result.GetResult<Prisma.$SensorPayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    device<T extends DeviceDefaultArgs<ExtArgs> = {}>(args?: Subset<T, DeviceDefaultArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): $Utils.JsPromise<TResult1 | TResult2>
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): $Utils.JsPromise<T | TResult>
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): $Utils.JsPromise<T>
  }




  /**
   * Fields of the SensorReading model
   */ 
  interface SensorReadingFieldRefs {
    readonly id: FieldRef<"SensorReading", 'String'>
    readonly sensorId: FieldRef<"SensorReading", 'String'>
    readonly deviceId: FieldRef<"SensorReading", 'String'>
    readonly value: FieldRef<"SensorReading", 'Float'>
    readonly unit: FieldRef<"SensorReading", 'String'>
    readonly timestamp: FieldRef<"SensorReading", 'DateTime'>
    readonly quality: FieldRef<"SensorReading", 'Float'>
    readonly metadata: FieldRef<"SensorReading", 'Json'>
  }
    

  // Custom InputTypes
  /**
   * SensorReading findUnique
   */
  export type SensorReadingFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * Filter, which SensorReading to fetch.
     */
    where: SensorReadingWhereUniqueInput
  }

  /**
   * SensorReading findUniqueOrThrow
   */
  export type SensorReadingFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * Filter, which SensorReading to fetch.
     */
    where: SensorReadingWhereUniqueInput
  }

  /**
   * SensorReading findFirst
   */
  export type SensorReadingFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * Filter, which SensorReading to fetch.
     */
    where?: SensorReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SensorReadings to fetch.
     */
    orderBy?: SensorReadingOrderByWithRelationInput | SensorReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for SensorReadings.
     */
    cursor?: SensorReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SensorReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SensorReadings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of SensorReadings.
     */
    distinct?: SensorReadingScalarFieldEnum | SensorReadingScalarFieldEnum[]
  }

  /**
   * SensorReading findFirstOrThrow
   */
  export type SensorReadingFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * Filter, which SensorReading to fetch.
     */
    where?: SensorReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SensorReadings to fetch.
     */
    orderBy?: SensorReadingOrderByWithRelationInput | SensorReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for SensorReadings.
     */
    cursor?: SensorReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SensorReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SensorReadings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of SensorReadings.
     */
    distinct?: SensorReadingScalarFieldEnum | SensorReadingScalarFieldEnum[]
  }

  /**
   * SensorReading findMany
   */
  export type SensorReadingFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * Filter, which SensorReadings to fetch.
     */
    where?: SensorReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SensorReadings to fetch.
     */
    orderBy?: SensorReadingOrderByWithRelationInput | SensorReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing SensorReadings.
     */
    cursor?: SensorReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SensorReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SensorReadings.
     */
    skip?: number
    distinct?: SensorReadingScalarFieldEnum | SensorReadingScalarFieldEnum[]
  }

  /**
   * SensorReading create
   */
  export type SensorReadingCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * The data needed to create a SensorReading.
     */
    data: XOR<SensorReadingCreateInput, SensorReadingUncheckedCreateInput>
  }

  /**
   * SensorReading createMany
   */
  export type SensorReadingCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many SensorReadings.
     */
    data: SensorReadingCreateManyInput | SensorReadingCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * SensorReading createManyAndReturn
   */
  export type SensorReadingCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many SensorReadings.
     */
    data: SensorReadingCreateManyInput | SensorReadingCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * SensorReading update
   */
  export type SensorReadingUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * The data needed to update a SensorReading.
     */
    data: XOR<SensorReadingUpdateInput, SensorReadingUncheckedUpdateInput>
    /**
     * Choose, which SensorReading to update.
     */
    where: SensorReadingWhereUniqueInput
  }

  /**
   * SensorReading updateMany
   */
  export type SensorReadingUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update SensorReadings.
     */
    data: XOR<SensorReadingUpdateManyMutationInput, SensorReadingUncheckedUpdateManyInput>
    /**
     * Filter which SensorReadings to update
     */
    where?: SensorReadingWhereInput
  }

  /**
   * SensorReading upsert
   */
  export type SensorReadingUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * The filter to search for the SensorReading to update in case it exists.
     */
    where: SensorReadingWhereUniqueInput
    /**
     * In case the SensorReading found by the `where` argument doesn't exist, create a new SensorReading with this data.
     */
    create: XOR<SensorReadingCreateInput, SensorReadingUncheckedCreateInput>
    /**
     * In case the SensorReading was found with the provided `where` argument, update it with this data.
     */
    update: XOR<SensorReadingUpdateInput, SensorReadingUncheckedUpdateInput>
  }

  /**
   * SensorReading delete
   */
  export type SensorReadingDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
    /**
     * Filter which SensorReading to delete.
     */
    where: SensorReadingWhereUniqueInput
  }

  /**
   * SensorReading deleteMany
   */
  export type SensorReadingDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which SensorReadings to delete
     */
    where?: SensorReadingWhereInput
  }

  /**
   * SensorReading without action
   */
  export type SensorReadingDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SensorReading
     */
    select?: SensorReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: SensorReadingInclude<ExtArgs> | null
  }


  /**
   * Model Actuator
   */

  export type AggregateActuator = {
    _count: ActuatorCountAggregateOutputType | null
    _min: ActuatorMinAggregateOutputType | null
    _max: ActuatorMaxAggregateOutputType | null
  }

  export type ActuatorMinAggregateOutputType = {
    id: string | null
    deviceId: string | null
    actuatorType: $Enums.ActuatorType | null
    name: string | null
    lastCommand: string | null
    lastCommandAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type ActuatorMaxAggregateOutputType = {
    id: string | null
    deviceId: string | null
    actuatorType: $Enums.ActuatorType | null
    name: string | null
    lastCommand: string | null
    lastCommandAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type ActuatorCountAggregateOutputType = {
    id: number
    deviceId: number
    actuatorType: number
    name: number
    currentState: number
    lastCommand: number
    lastCommandAt: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type ActuatorMinAggregateInputType = {
    id?: true
    deviceId?: true
    actuatorType?: true
    name?: true
    lastCommand?: true
    lastCommandAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type ActuatorMaxAggregateInputType = {
    id?: true
    deviceId?: true
    actuatorType?: true
    name?: true
    lastCommand?: true
    lastCommandAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type ActuatorCountAggregateInputType = {
    id?: true
    deviceId?: true
    actuatorType?: true
    name?: true
    currentState?: true
    lastCommand?: true
    lastCommandAt?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type ActuatorAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Actuator to aggregate.
     */
    where?: ActuatorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Actuators to fetch.
     */
    orderBy?: ActuatorOrderByWithRelationInput | ActuatorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: ActuatorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Actuators from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Actuators.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Actuators
    **/
    _count?: true | ActuatorCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: ActuatorMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: ActuatorMaxAggregateInputType
  }

  export type GetActuatorAggregateType<T extends ActuatorAggregateArgs> = {
        [P in keyof T & keyof AggregateActuator]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateActuator[P]>
      : GetScalarType<T[P], AggregateActuator[P]>
  }




  export type ActuatorGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: ActuatorWhereInput
    orderBy?: ActuatorOrderByWithAggregationInput | ActuatorOrderByWithAggregationInput[]
    by: ActuatorScalarFieldEnum[] | ActuatorScalarFieldEnum
    having?: ActuatorScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: ActuatorCountAggregateInputType | true
    _min?: ActuatorMinAggregateInputType
    _max?: ActuatorMaxAggregateInputType
  }

  export type ActuatorGroupByOutputType = {
    id: string
    deviceId: string
    actuatorType: $Enums.ActuatorType
    name: string | null
    currentState: JsonValue | null
    lastCommand: string | null
    lastCommandAt: Date | null
    createdAt: Date
    updatedAt: Date
    _count: ActuatorCountAggregateOutputType | null
    _min: ActuatorMinAggregateOutputType | null
    _max: ActuatorMaxAggregateOutputType | null
  }

  type GetActuatorGroupByPayload<T extends ActuatorGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<ActuatorGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof ActuatorGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], ActuatorGroupByOutputType[P]>
            : GetScalarType<T[P], ActuatorGroupByOutputType[P]>
        }
      >
    >


  export type ActuatorSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    actuatorType?: boolean
    name?: boolean
    currentState?: boolean
    lastCommand?: boolean
    lastCommandAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    device?: boolean | DeviceDefaultArgs<ExtArgs>
    commands?: boolean | Actuator$commandsArgs<ExtArgs>
    _count?: boolean | ActuatorCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["actuator"]>

  export type ActuatorSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    actuatorType?: boolean
    name?: boolean
    currentState?: boolean
    lastCommand?: boolean
    lastCommandAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["actuator"]>

  export type ActuatorSelectScalar = {
    id?: boolean
    deviceId?: boolean
    actuatorType?: boolean
    name?: boolean
    currentState?: boolean
    lastCommand?: boolean
    lastCommandAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type ActuatorInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    device?: boolean | DeviceDefaultArgs<ExtArgs>
    commands?: boolean | Actuator$commandsArgs<ExtArgs>
    _count?: boolean | ActuatorCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type ActuatorIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }

  export type $ActuatorPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Actuator"
    objects: {
      device: Prisma.$DevicePayload<ExtArgs>
      commands: Prisma.$ActuatorCommandPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      deviceId: string
      actuatorType: $Enums.ActuatorType
      name: string | null
      currentState: Prisma.JsonValue | null
      lastCommand: string | null
      lastCommandAt: Date | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["actuator"]>
    composites: {}
  }

  type ActuatorGetPayload<S extends boolean | null | undefined | ActuatorDefaultArgs> = $Result.GetResult<Prisma.$ActuatorPayload, S>

  type ActuatorCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<ActuatorFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: ActuatorCountAggregateInputType | true
    }

  export interface ActuatorDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Actuator'], meta: { name: 'Actuator' } }
    /**
     * Find zero or one Actuator that matches the filter.
     * @param {ActuatorFindUniqueArgs} args - Arguments to find a Actuator
     * @example
     * // Get one Actuator
     * const actuator = await prisma.actuator.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends ActuatorFindUniqueArgs>(args: SelectSubset<T, ActuatorFindUniqueArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Actuator that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {ActuatorFindUniqueOrThrowArgs} args - Arguments to find a Actuator
     * @example
     * // Get one Actuator
     * const actuator = await prisma.actuator.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends ActuatorFindUniqueOrThrowArgs>(args: SelectSubset<T, ActuatorFindUniqueOrThrowArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Actuator that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorFindFirstArgs} args - Arguments to find a Actuator
     * @example
     * // Get one Actuator
     * const actuator = await prisma.actuator.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends ActuatorFindFirstArgs>(args?: SelectSubset<T, ActuatorFindFirstArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Actuator that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorFindFirstOrThrowArgs} args - Arguments to find a Actuator
     * @example
     * // Get one Actuator
     * const actuator = await prisma.actuator.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends ActuatorFindFirstOrThrowArgs>(args?: SelectSubset<T, ActuatorFindFirstOrThrowArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Actuators that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Actuators
     * const actuators = await prisma.actuator.findMany()
     * 
     * // Get first 10 Actuators
     * const actuators = await prisma.actuator.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const actuatorWithIdOnly = await prisma.actuator.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends ActuatorFindManyArgs>(args?: SelectSubset<T, ActuatorFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Actuator.
     * @param {ActuatorCreateArgs} args - Arguments to create a Actuator.
     * @example
     * // Create one Actuator
     * const Actuator = await prisma.actuator.create({
     *   data: {
     *     // ... data to create a Actuator
     *   }
     * })
     * 
     */
    create<T extends ActuatorCreateArgs>(args: SelectSubset<T, ActuatorCreateArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Actuators.
     * @param {ActuatorCreateManyArgs} args - Arguments to create many Actuators.
     * @example
     * // Create many Actuators
     * const actuator = await prisma.actuator.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends ActuatorCreateManyArgs>(args?: SelectSubset<T, ActuatorCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Actuators and returns the data saved in the database.
     * @param {ActuatorCreateManyAndReturnArgs} args - Arguments to create many Actuators.
     * @example
     * // Create many Actuators
     * const actuator = await prisma.actuator.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Actuators and only return the `id`
     * const actuatorWithIdOnly = await prisma.actuator.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends ActuatorCreateManyAndReturnArgs>(args?: SelectSubset<T, ActuatorCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Actuator.
     * @param {ActuatorDeleteArgs} args - Arguments to delete one Actuator.
     * @example
     * // Delete one Actuator
     * const Actuator = await prisma.actuator.delete({
     *   where: {
     *     // ... filter to delete one Actuator
     *   }
     * })
     * 
     */
    delete<T extends ActuatorDeleteArgs>(args: SelectSubset<T, ActuatorDeleteArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Actuator.
     * @param {ActuatorUpdateArgs} args - Arguments to update one Actuator.
     * @example
     * // Update one Actuator
     * const actuator = await prisma.actuator.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends ActuatorUpdateArgs>(args: SelectSubset<T, ActuatorUpdateArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Actuators.
     * @param {ActuatorDeleteManyArgs} args - Arguments to filter Actuators to delete.
     * @example
     * // Delete a few Actuators
     * const { count } = await prisma.actuator.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends ActuatorDeleteManyArgs>(args?: SelectSubset<T, ActuatorDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Actuators.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Actuators
     * const actuator = await prisma.actuator.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends ActuatorUpdateManyArgs>(args: SelectSubset<T, ActuatorUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Actuator.
     * @param {ActuatorUpsertArgs} args - Arguments to update or create a Actuator.
     * @example
     * // Update or create a Actuator
     * const actuator = await prisma.actuator.upsert({
     *   create: {
     *     // ... data to create a Actuator
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Actuator we want to update
     *   }
     * })
     */
    upsert<T extends ActuatorUpsertArgs>(args: SelectSubset<T, ActuatorUpsertArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Actuators.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCountArgs} args - Arguments to filter Actuators to count.
     * @example
     * // Count the number of Actuators
     * const count = await prisma.actuator.count({
     *   where: {
     *     // ... the filter for the Actuators we want to count
     *   }
     * })
    **/
    count<T extends ActuatorCountArgs>(
      args?: Subset<T, ActuatorCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], ActuatorCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Actuator.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends ActuatorAggregateArgs>(args: Subset<T, ActuatorAggregateArgs>): Prisma.PrismaPromise<GetActuatorAggregateType<T>>

    /**
     * Group by Actuator.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends ActuatorGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: ActuatorGroupByArgs['orderBy'] }
        : { orderBy?: ActuatorGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends MaybeTupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, ActuatorGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetActuatorGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Actuator model
   */
  readonly fields: ActuatorFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Actuator.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__ActuatorClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    device<T extends DeviceDefaultArgs<ExtArgs> = {}>(args?: Subset<T, DeviceDefaultArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    commands<T extends Actuator$commandsArgs<ExtArgs> = {}>(args?: Subset<T, Actuator$commandsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "findMany"> | Null>
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): $Utils.JsPromise<TResult1 | TResult2>
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): $Utils.JsPromise<T | TResult>
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): $Utils.JsPromise<T>
  }




  /**
   * Fields of the Actuator model
   */ 
  interface ActuatorFieldRefs {
    readonly id: FieldRef<"Actuator", 'String'>
    readonly deviceId: FieldRef<"Actuator", 'String'>
    readonly actuatorType: FieldRef<"Actuator", 'ActuatorType'>
    readonly name: FieldRef<"Actuator", 'String'>
    readonly currentState: FieldRef<"Actuator", 'Json'>
    readonly lastCommand: FieldRef<"Actuator", 'String'>
    readonly lastCommandAt: FieldRef<"Actuator", 'DateTime'>
    readonly createdAt: FieldRef<"Actuator", 'DateTime'>
    readonly updatedAt: FieldRef<"Actuator", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Actuator findUnique
   */
  export type ActuatorFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * Filter, which Actuator to fetch.
     */
    where: ActuatorWhereUniqueInput
  }

  /**
   * Actuator findUniqueOrThrow
   */
  export type ActuatorFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * Filter, which Actuator to fetch.
     */
    where: ActuatorWhereUniqueInput
  }

  /**
   * Actuator findFirst
   */
  export type ActuatorFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * Filter, which Actuator to fetch.
     */
    where?: ActuatorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Actuators to fetch.
     */
    orderBy?: ActuatorOrderByWithRelationInput | ActuatorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Actuators.
     */
    cursor?: ActuatorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Actuators from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Actuators.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Actuators.
     */
    distinct?: ActuatorScalarFieldEnum | ActuatorScalarFieldEnum[]
  }

  /**
   * Actuator findFirstOrThrow
   */
  export type ActuatorFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * Filter, which Actuator to fetch.
     */
    where?: ActuatorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Actuators to fetch.
     */
    orderBy?: ActuatorOrderByWithRelationInput | ActuatorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Actuators.
     */
    cursor?: ActuatorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Actuators from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Actuators.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Actuators.
     */
    distinct?: ActuatorScalarFieldEnum | ActuatorScalarFieldEnum[]
  }

  /**
   * Actuator findMany
   */
  export type ActuatorFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * Filter, which Actuators to fetch.
     */
    where?: ActuatorWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Actuators to fetch.
     */
    orderBy?: ActuatorOrderByWithRelationInput | ActuatorOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Actuators.
     */
    cursor?: ActuatorWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Actuators from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Actuators.
     */
    skip?: number
    distinct?: ActuatorScalarFieldEnum | ActuatorScalarFieldEnum[]
  }

  /**
   * Actuator create
   */
  export type ActuatorCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * The data needed to create a Actuator.
     */
    data: XOR<ActuatorCreateInput, ActuatorUncheckedCreateInput>
  }

  /**
   * Actuator createMany
   */
  export type ActuatorCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Actuators.
     */
    data: ActuatorCreateManyInput | ActuatorCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Actuator createManyAndReturn
   */
  export type ActuatorCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Actuators.
     */
    data: ActuatorCreateManyInput | ActuatorCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * Actuator update
   */
  export type ActuatorUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * The data needed to update a Actuator.
     */
    data: XOR<ActuatorUpdateInput, ActuatorUncheckedUpdateInput>
    /**
     * Choose, which Actuator to update.
     */
    where: ActuatorWhereUniqueInput
  }

  /**
   * Actuator updateMany
   */
  export type ActuatorUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Actuators.
     */
    data: XOR<ActuatorUpdateManyMutationInput, ActuatorUncheckedUpdateManyInput>
    /**
     * Filter which Actuators to update
     */
    where?: ActuatorWhereInput
  }

  /**
   * Actuator upsert
   */
  export type ActuatorUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * The filter to search for the Actuator to update in case it exists.
     */
    where: ActuatorWhereUniqueInput
    /**
     * In case the Actuator found by the `where` argument doesn't exist, create a new Actuator with this data.
     */
    create: XOR<ActuatorCreateInput, ActuatorUncheckedCreateInput>
    /**
     * In case the Actuator was found with the provided `where` argument, update it with this data.
     */
    update: XOR<ActuatorUpdateInput, ActuatorUncheckedUpdateInput>
  }

  /**
   * Actuator delete
   */
  export type ActuatorDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
    /**
     * Filter which Actuator to delete.
     */
    where: ActuatorWhereUniqueInput
  }

  /**
   * Actuator deleteMany
   */
  export type ActuatorDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Actuators to delete
     */
    where?: ActuatorWhereInput
  }

  /**
   * Actuator.commands
   */
  export type Actuator$commandsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    where?: ActuatorCommandWhereInput
    orderBy?: ActuatorCommandOrderByWithRelationInput | ActuatorCommandOrderByWithRelationInput[]
    cursor?: ActuatorCommandWhereUniqueInput
    take?: number
    skip?: number
    distinct?: ActuatorCommandScalarFieldEnum | ActuatorCommandScalarFieldEnum[]
  }

  /**
   * Actuator without action
   */
  export type ActuatorDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Actuator
     */
    select?: ActuatorSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorInclude<ExtArgs> | null
  }


  /**
   * Model ActuatorCommand
   */

  export type AggregateActuatorCommand = {
    _count: ActuatorCommandCountAggregateOutputType | null
    _min: ActuatorCommandMinAggregateOutputType | null
    _max: ActuatorCommandMaxAggregateOutputType | null
  }

  export type ActuatorCommandMinAggregateOutputType = {
    id: string | null
    actuatorId: string | null
    command: string | null
    status: $Enums.CommandStatus | null
    requestedAt: Date | null
    executedAt: Date | null
    completedAt: Date | null
    errorMessage: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type ActuatorCommandMaxAggregateOutputType = {
    id: string | null
    actuatorId: string | null
    command: string | null
    status: $Enums.CommandStatus | null
    requestedAt: Date | null
    executedAt: Date | null
    completedAt: Date | null
    errorMessage: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type ActuatorCommandCountAggregateOutputType = {
    id: number
    actuatorId: number
    command: number
    parameters: number
    status: number
    requestedAt: number
    executedAt: number
    completedAt: number
    errorMessage: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type ActuatorCommandMinAggregateInputType = {
    id?: true
    actuatorId?: true
    command?: true
    status?: true
    requestedAt?: true
    executedAt?: true
    completedAt?: true
    errorMessage?: true
    createdAt?: true
    updatedAt?: true
  }

  export type ActuatorCommandMaxAggregateInputType = {
    id?: true
    actuatorId?: true
    command?: true
    status?: true
    requestedAt?: true
    executedAt?: true
    completedAt?: true
    errorMessage?: true
    createdAt?: true
    updatedAt?: true
  }

  export type ActuatorCommandCountAggregateInputType = {
    id?: true
    actuatorId?: true
    command?: true
    parameters?: true
    status?: true
    requestedAt?: true
    executedAt?: true
    completedAt?: true
    errorMessage?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type ActuatorCommandAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which ActuatorCommand to aggregate.
     */
    where?: ActuatorCommandWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of ActuatorCommands to fetch.
     */
    orderBy?: ActuatorCommandOrderByWithRelationInput | ActuatorCommandOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: ActuatorCommandWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` ActuatorCommands from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` ActuatorCommands.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned ActuatorCommands
    **/
    _count?: true | ActuatorCommandCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: ActuatorCommandMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: ActuatorCommandMaxAggregateInputType
  }

  export type GetActuatorCommandAggregateType<T extends ActuatorCommandAggregateArgs> = {
        [P in keyof T & keyof AggregateActuatorCommand]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateActuatorCommand[P]>
      : GetScalarType<T[P], AggregateActuatorCommand[P]>
  }




  export type ActuatorCommandGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: ActuatorCommandWhereInput
    orderBy?: ActuatorCommandOrderByWithAggregationInput | ActuatorCommandOrderByWithAggregationInput[]
    by: ActuatorCommandScalarFieldEnum[] | ActuatorCommandScalarFieldEnum
    having?: ActuatorCommandScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: ActuatorCommandCountAggregateInputType | true
    _min?: ActuatorCommandMinAggregateInputType
    _max?: ActuatorCommandMaxAggregateInputType
  }

  export type ActuatorCommandGroupByOutputType = {
    id: string
    actuatorId: string
    command: string
    parameters: JsonValue | null
    status: $Enums.CommandStatus
    requestedAt: Date
    executedAt: Date | null
    completedAt: Date | null
    errorMessage: string | null
    createdAt: Date
    updatedAt: Date
    _count: ActuatorCommandCountAggregateOutputType | null
    _min: ActuatorCommandMinAggregateOutputType | null
    _max: ActuatorCommandMaxAggregateOutputType | null
  }

  type GetActuatorCommandGroupByPayload<T extends ActuatorCommandGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<ActuatorCommandGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof ActuatorCommandGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], ActuatorCommandGroupByOutputType[P]>
            : GetScalarType<T[P], ActuatorCommandGroupByOutputType[P]>
        }
      >
    >


  export type ActuatorCommandSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    actuatorId?: boolean
    command?: boolean
    parameters?: boolean
    status?: boolean
    requestedAt?: boolean
    executedAt?: boolean
    completedAt?: boolean
    errorMessage?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    actuator?: boolean | ActuatorDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["actuatorCommand"]>

  export type ActuatorCommandSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    actuatorId?: boolean
    command?: boolean
    parameters?: boolean
    status?: boolean
    requestedAt?: boolean
    executedAt?: boolean
    completedAt?: boolean
    errorMessage?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    actuator?: boolean | ActuatorDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["actuatorCommand"]>

  export type ActuatorCommandSelectScalar = {
    id?: boolean
    actuatorId?: boolean
    command?: boolean
    parameters?: boolean
    status?: boolean
    requestedAt?: boolean
    executedAt?: boolean
    completedAt?: boolean
    errorMessage?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type ActuatorCommandInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    actuator?: boolean | ActuatorDefaultArgs<ExtArgs>
  }
  export type ActuatorCommandIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    actuator?: boolean | ActuatorDefaultArgs<ExtArgs>
  }

  export type $ActuatorCommandPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "ActuatorCommand"
    objects: {
      actuator: Prisma.$ActuatorPayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      actuatorId: string
      command: string
      parameters: Prisma.JsonValue | null
      status: $Enums.CommandStatus
      requestedAt: Date
      executedAt: Date | null
      completedAt: Date | null
      errorMessage: string | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["actuatorCommand"]>
    composites: {}
  }

  type ActuatorCommandGetPayload<S extends boolean | null | undefined | ActuatorCommandDefaultArgs> = $Result.GetResult<Prisma.$ActuatorCommandPayload, S>

  type ActuatorCommandCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<ActuatorCommandFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: ActuatorCommandCountAggregateInputType | true
    }

  export interface ActuatorCommandDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['ActuatorCommand'], meta: { name: 'ActuatorCommand' } }
    /**
     * Find zero or one ActuatorCommand that matches the filter.
     * @param {ActuatorCommandFindUniqueArgs} args - Arguments to find a ActuatorCommand
     * @example
     * // Get one ActuatorCommand
     * const actuatorCommand = await prisma.actuatorCommand.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends ActuatorCommandFindUniqueArgs>(args: SelectSubset<T, ActuatorCommandFindUniqueArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one ActuatorCommand that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {ActuatorCommandFindUniqueOrThrowArgs} args - Arguments to find a ActuatorCommand
     * @example
     * // Get one ActuatorCommand
     * const actuatorCommand = await prisma.actuatorCommand.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends ActuatorCommandFindUniqueOrThrowArgs>(args: SelectSubset<T, ActuatorCommandFindUniqueOrThrowArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first ActuatorCommand that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandFindFirstArgs} args - Arguments to find a ActuatorCommand
     * @example
     * // Get one ActuatorCommand
     * const actuatorCommand = await prisma.actuatorCommand.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends ActuatorCommandFindFirstArgs>(args?: SelectSubset<T, ActuatorCommandFindFirstArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first ActuatorCommand that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandFindFirstOrThrowArgs} args - Arguments to find a ActuatorCommand
     * @example
     * // Get one ActuatorCommand
     * const actuatorCommand = await prisma.actuatorCommand.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends ActuatorCommandFindFirstOrThrowArgs>(args?: SelectSubset<T, ActuatorCommandFindFirstOrThrowArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more ActuatorCommands that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all ActuatorCommands
     * const actuatorCommands = await prisma.actuatorCommand.findMany()
     * 
     * // Get first 10 ActuatorCommands
     * const actuatorCommands = await prisma.actuatorCommand.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const actuatorCommandWithIdOnly = await prisma.actuatorCommand.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends ActuatorCommandFindManyArgs>(args?: SelectSubset<T, ActuatorCommandFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a ActuatorCommand.
     * @param {ActuatorCommandCreateArgs} args - Arguments to create a ActuatorCommand.
     * @example
     * // Create one ActuatorCommand
     * const ActuatorCommand = await prisma.actuatorCommand.create({
     *   data: {
     *     // ... data to create a ActuatorCommand
     *   }
     * })
     * 
     */
    create<T extends ActuatorCommandCreateArgs>(args: SelectSubset<T, ActuatorCommandCreateArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many ActuatorCommands.
     * @param {ActuatorCommandCreateManyArgs} args - Arguments to create many ActuatorCommands.
     * @example
     * // Create many ActuatorCommands
     * const actuatorCommand = await prisma.actuatorCommand.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends ActuatorCommandCreateManyArgs>(args?: SelectSubset<T, ActuatorCommandCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many ActuatorCommands and returns the data saved in the database.
     * @param {ActuatorCommandCreateManyAndReturnArgs} args - Arguments to create many ActuatorCommands.
     * @example
     * // Create many ActuatorCommands
     * const actuatorCommand = await prisma.actuatorCommand.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many ActuatorCommands and only return the `id`
     * const actuatorCommandWithIdOnly = await prisma.actuatorCommand.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends ActuatorCommandCreateManyAndReturnArgs>(args?: SelectSubset<T, ActuatorCommandCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a ActuatorCommand.
     * @param {ActuatorCommandDeleteArgs} args - Arguments to delete one ActuatorCommand.
     * @example
     * // Delete one ActuatorCommand
     * const ActuatorCommand = await prisma.actuatorCommand.delete({
     *   where: {
     *     // ... filter to delete one ActuatorCommand
     *   }
     * })
     * 
     */
    delete<T extends ActuatorCommandDeleteArgs>(args: SelectSubset<T, ActuatorCommandDeleteArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one ActuatorCommand.
     * @param {ActuatorCommandUpdateArgs} args - Arguments to update one ActuatorCommand.
     * @example
     * // Update one ActuatorCommand
     * const actuatorCommand = await prisma.actuatorCommand.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends ActuatorCommandUpdateArgs>(args: SelectSubset<T, ActuatorCommandUpdateArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more ActuatorCommands.
     * @param {ActuatorCommandDeleteManyArgs} args - Arguments to filter ActuatorCommands to delete.
     * @example
     * // Delete a few ActuatorCommands
     * const { count } = await prisma.actuatorCommand.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends ActuatorCommandDeleteManyArgs>(args?: SelectSubset<T, ActuatorCommandDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more ActuatorCommands.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many ActuatorCommands
     * const actuatorCommand = await prisma.actuatorCommand.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends ActuatorCommandUpdateManyArgs>(args: SelectSubset<T, ActuatorCommandUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one ActuatorCommand.
     * @param {ActuatorCommandUpsertArgs} args - Arguments to update or create a ActuatorCommand.
     * @example
     * // Update or create a ActuatorCommand
     * const actuatorCommand = await prisma.actuatorCommand.upsert({
     *   create: {
     *     // ... data to create a ActuatorCommand
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the ActuatorCommand we want to update
     *   }
     * })
     */
    upsert<T extends ActuatorCommandUpsertArgs>(args: SelectSubset<T, ActuatorCommandUpsertArgs<ExtArgs>>): Prisma__ActuatorCommandClient<$Result.GetResult<Prisma.$ActuatorCommandPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of ActuatorCommands.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandCountArgs} args - Arguments to filter ActuatorCommands to count.
     * @example
     * // Count the number of ActuatorCommands
     * const count = await prisma.actuatorCommand.count({
     *   where: {
     *     // ... the filter for the ActuatorCommands we want to count
     *   }
     * })
    **/
    count<T extends ActuatorCommandCountArgs>(
      args?: Subset<T, ActuatorCommandCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], ActuatorCommandCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a ActuatorCommand.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends ActuatorCommandAggregateArgs>(args: Subset<T, ActuatorCommandAggregateArgs>): Prisma.PrismaPromise<GetActuatorCommandAggregateType<T>>

    /**
     * Group by ActuatorCommand.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ActuatorCommandGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends ActuatorCommandGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: ActuatorCommandGroupByArgs['orderBy'] }
        : { orderBy?: ActuatorCommandGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends MaybeTupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, ActuatorCommandGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetActuatorCommandGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the ActuatorCommand model
   */
  readonly fields: ActuatorCommandFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for ActuatorCommand.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__ActuatorCommandClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    actuator<T extends ActuatorDefaultArgs<ExtArgs> = {}>(args?: Subset<T, ActuatorDefaultArgs<ExtArgs>>): Prisma__ActuatorClient<$Result.GetResult<Prisma.$ActuatorPayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): $Utils.JsPromise<TResult1 | TResult2>
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): $Utils.JsPromise<T | TResult>
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): $Utils.JsPromise<T>
  }




  /**
   * Fields of the ActuatorCommand model
   */ 
  interface ActuatorCommandFieldRefs {
    readonly id: FieldRef<"ActuatorCommand", 'String'>
    readonly actuatorId: FieldRef<"ActuatorCommand", 'String'>
    readonly command: FieldRef<"ActuatorCommand", 'String'>
    readonly parameters: FieldRef<"ActuatorCommand", 'Json'>
    readonly status: FieldRef<"ActuatorCommand", 'CommandStatus'>
    readonly requestedAt: FieldRef<"ActuatorCommand", 'DateTime'>
    readonly executedAt: FieldRef<"ActuatorCommand", 'DateTime'>
    readonly completedAt: FieldRef<"ActuatorCommand", 'DateTime'>
    readonly errorMessage: FieldRef<"ActuatorCommand", 'String'>
    readonly createdAt: FieldRef<"ActuatorCommand", 'DateTime'>
    readonly updatedAt: FieldRef<"ActuatorCommand", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * ActuatorCommand findUnique
   */
  export type ActuatorCommandFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * Filter, which ActuatorCommand to fetch.
     */
    where: ActuatorCommandWhereUniqueInput
  }

  /**
   * ActuatorCommand findUniqueOrThrow
   */
  export type ActuatorCommandFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * Filter, which ActuatorCommand to fetch.
     */
    where: ActuatorCommandWhereUniqueInput
  }

  /**
   * ActuatorCommand findFirst
   */
  export type ActuatorCommandFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * Filter, which ActuatorCommand to fetch.
     */
    where?: ActuatorCommandWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of ActuatorCommands to fetch.
     */
    orderBy?: ActuatorCommandOrderByWithRelationInput | ActuatorCommandOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for ActuatorCommands.
     */
    cursor?: ActuatorCommandWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` ActuatorCommands from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` ActuatorCommands.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of ActuatorCommands.
     */
    distinct?: ActuatorCommandScalarFieldEnum | ActuatorCommandScalarFieldEnum[]
  }

  /**
   * ActuatorCommand findFirstOrThrow
   */
  export type ActuatorCommandFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * Filter, which ActuatorCommand to fetch.
     */
    where?: ActuatorCommandWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of ActuatorCommands to fetch.
     */
    orderBy?: ActuatorCommandOrderByWithRelationInput | ActuatorCommandOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for ActuatorCommands.
     */
    cursor?: ActuatorCommandWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` ActuatorCommands from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` ActuatorCommands.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of ActuatorCommands.
     */
    distinct?: ActuatorCommandScalarFieldEnum | ActuatorCommandScalarFieldEnum[]
  }

  /**
   * ActuatorCommand findMany
   */
  export type ActuatorCommandFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * Filter, which ActuatorCommands to fetch.
     */
    where?: ActuatorCommandWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of ActuatorCommands to fetch.
     */
    orderBy?: ActuatorCommandOrderByWithRelationInput | ActuatorCommandOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing ActuatorCommands.
     */
    cursor?: ActuatorCommandWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` ActuatorCommands from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` ActuatorCommands.
     */
    skip?: number
    distinct?: ActuatorCommandScalarFieldEnum | ActuatorCommandScalarFieldEnum[]
  }

  /**
   * ActuatorCommand create
   */
  export type ActuatorCommandCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * The data needed to create a ActuatorCommand.
     */
    data: XOR<ActuatorCommandCreateInput, ActuatorCommandUncheckedCreateInput>
  }

  /**
   * ActuatorCommand createMany
   */
  export type ActuatorCommandCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many ActuatorCommands.
     */
    data: ActuatorCommandCreateManyInput | ActuatorCommandCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * ActuatorCommand createManyAndReturn
   */
  export type ActuatorCommandCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many ActuatorCommands.
     */
    data: ActuatorCommandCreateManyInput | ActuatorCommandCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * ActuatorCommand update
   */
  export type ActuatorCommandUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * The data needed to update a ActuatorCommand.
     */
    data: XOR<ActuatorCommandUpdateInput, ActuatorCommandUncheckedUpdateInput>
    /**
     * Choose, which ActuatorCommand to update.
     */
    where: ActuatorCommandWhereUniqueInput
  }

  /**
   * ActuatorCommand updateMany
   */
  export type ActuatorCommandUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update ActuatorCommands.
     */
    data: XOR<ActuatorCommandUpdateManyMutationInput, ActuatorCommandUncheckedUpdateManyInput>
    /**
     * Filter which ActuatorCommands to update
     */
    where?: ActuatorCommandWhereInput
  }

  /**
   * ActuatorCommand upsert
   */
  export type ActuatorCommandUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * The filter to search for the ActuatorCommand to update in case it exists.
     */
    where: ActuatorCommandWhereUniqueInput
    /**
     * In case the ActuatorCommand found by the `where` argument doesn't exist, create a new ActuatorCommand with this data.
     */
    create: XOR<ActuatorCommandCreateInput, ActuatorCommandUncheckedCreateInput>
    /**
     * In case the ActuatorCommand was found with the provided `where` argument, update it with this data.
     */
    update: XOR<ActuatorCommandUpdateInput, ActuatorCommandUncheckedUpdateInput>
  }

  /**
   * ActuatorCommand delete
   */
  export type ActuatorCommandDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
    /**
     * Filter which ActuatorCommand to delete.
     */
    where: ActuatorCommandWhereUniqueInput
  }

  /**
   * ActuatorCommand deleteMany
   */
  export type ActuatorCommandDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which ActuatorCommands to delete
     */
    where?: ActuatorCommandWhereInput
  }

  /**
   * ActuatorCommand without action
   */
  export type ActuatorCommandDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ActuatorCommand
     */
    select?: ActuatorCommandSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ActuatorCommandInclude<ExtArgs> | null
  }


  /**
   * Model DeviceAlert
   */

  export type AggregateDeviceAlert = {
    _count: DeviceAlertCountAggregateOutputType | null
    _min: DeviceAlertMinAggregateOutputType | null
    _max: DeviceAlertMaxAggregateOutputType | null
  }

  export type DeviceAlertMinAggregateOutputType = {
    id: string | null
    deviceId: string | null
    tenantId: string | null
    alertType: string | null
    severity: $Enums.AlertSeverity | null
    message: string | null
    acknowledged: boolean | null
    acknowledgedBy: string | null
    acknowledgedAt: Date | null
    resolvedAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type DeviceAlertMaxAggregateOutputType = {
    id: string | null
    deviceId: string | null
    tenantId: string | null
    alertType: string | null
    severity: $Enums.AlertSeverity | null
    message: string | null
    acknowledged: boolean | null
    acknowledgedBy: string | null
    acknowledgedAt: Date | null
    resolvedAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type DeviceAlertCountAggregateOutputType = {
    id: number
    deviceId: number
    tenantId: number
    alertType: number
    severity: number
    message: number
    acknowledged: number
    acknowledgedBy: number
    acknowledgedAt: number
    resolvedAt: number
    metadata: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type DeviceAlertMinAggregateInputType = {
    id?: true
    deviceId?: true
    tenantId?: true
    alertType?: true
    severity?: true
    message?: true
    acknowledged?: true
    acknowledgedBy?: true
    acknowledgedAt?: true
    resolvedAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type DeviceAlertMaxAggregateInputType = {
    id?: true
    deviceId?: true
    tenantId?: true
    alertType?: true
    severity?: true
    message?: true
    acknowledged?: true
    acknowledgedBy?: true
    acknowledgedAt?: true
    resolvedAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type DeviceAlertCountAggregateInputType = {
    id?: true
    deviceId?: true
    tenantId?: true
    alertType?: true
    severity?: true
    message?: true
    acknowledged?: true
    acknowledgedBy?: true
    acknowledgedAt?: true
    resolvedAt?: true
    metadata?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type DeviceAlertAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which DeviceAlert to aggregate.
     */
    where?: DeviceAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of DeviceAlerts to fetch.
     */
    orderBy?: DeviceAlertOrderByWithRelationInput | DeviceAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: DeviceAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` DeviceAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` DeviceAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned DeviceAlerts
    **/
    _count?: true | DeviceAlertCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: DeviceAlertMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: DeviceAlertMaxAggregateInputType
  }

  export type GetDeviceAlertAggregateType<T extends DeviceAlertAggregateArgs> = {
        [P in keyof T & keyof AggregateDeviceAlert]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateDeviceAlert[P]>
      : GetScalarType<T[P], AggregateDeviceAlert[P]>
  }




  export type DeviceAlertGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: DeviceAlertWhereInput
    orderBy?: DeviceAlertOrderByWithAggregationInput | DeviceAlertOrderByWithAggregationInput[]
    by: DeviceAlertScalarFieldEnum[] | DeviceAlertScalarFieldEnum
    having?: DeviceAlertScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: DeviceAlertCountAggregateInputType | true
    _min?: DeviceAlertMinAggregateInputType
    _max?: DeviceAlertMaxAggregateInputType
  }

  export type DeviceAlertGroupByOutputType = {
    id: string
    deviceId: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged: boolean
    acknowledgedBy: string | null
    acknowledgedAt: Date | null
    resolvedAt: Date | null
    metadata: JsonValue | null
    createdAt: Date
    updatedAt: Date
    _count: DeviceAlertCountAggregateOutputType | null
    _min: DeviceAlertMinAggregateOutputType | null
    _max: DeviceAlertMaxAggregateOutputType | null
  }

  type GetDeviceAlertGroupByPayload<T extends DeviceAlertGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<DeviceAlertGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof DeviceAlertGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], DeviceAlertGroupByOutputType[P]>
            : GetScalarType<T[P], DeviceAlertGroupByOutputType[P]>
        }
      >
    >


  export type DeviceAlertSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    tenantId?: boolean
    alertType?: boolean
    severity?: boolean
    message?: boolean
    acknowledged?: boolean
    acknowledgedBy?: boolean
    acknowledgedAt?: boolean
    resolvedAt?: boolean
    metadata?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["deviceAlert"]>

  export type DeviceAlertSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    tenantId?: boolean
    alertType?: boolean
    severity?: boolean
    message?: boolean
    acknowledged?: boolean
    acknowledgedBy?: boolean
    acknowledgedAt?: boolean
    resolvedAt?: boolean
    metadata?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["deviceAlert"]>

  export type DeviceAlertSelectScalar = {
    id?: boolean
    deviceId?: boolean
    tenantId?: boolean
    alertType?: boolean
    severity?: boolean
    message?: boolean
    acknowledged?: boolean
    acknowledgedBy?: boolean
    acknowledgedAt?: boolean
    resolvedAt?: boolean
    metadata?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type DeviceAlertInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }
  export type DeviceAlertIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    device?: boolean | DeviceDefaultArgs<ExtArgs>
  }

  export type $DeviceAlertPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "DeviceAlert"
    objects: {
      device: Prisma.$DevicePayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      deviceId: string
      tenantId: string
      alertType: string
      severity: $Enums.AlertSeverity
      message: string
      acknowledged: boolean
      acknowledgedBy: string | null
      acknowledgedAt: Date | null
      resolvedAt: Date | null
      metadata: Prisma.JsonValue | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["deviceAlert"]>
    composites: {}
  }

  type DeviceAlertGetPayload<S extends boolean | null | undefined | DeviceAlertDefaultArgs> = $Result.GetResult<Prisma.$DeviceAlertPayload, S>

  type DeviceAlertCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<DeviceAlertFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: DeviceAlertCountAggregateInputType | true
    }

  export interface DeviceAlertDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['DeviceAlert'], meta: { name: 'DeviceAlert' } }
    /**
     * Find zero or one DeviceAlert that matches the filter.
     * @param {DeviceAlertFindUniqueArgs} args - Arguments to find a DeviceAlert
     * @example
     * // Get one DeviceAlert
     * const deviceAlert = await prisma.deviceAlert.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends DeviceAlertFindUniqueArgs>(args: SelectSubset<T, DeviceAlertFindUniqueArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one DeviceAlert that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {DeviceAlertFindUniqueOrThrowArgs} args - Arguments to find a DeviceAlert
     * @example
     * // Get one DeviceAlert
     * const deviceAlert = await prisma.deviceAlert.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends DeviceAlertFindUniqueOrThrowArgs>(args: SelectSubset<T, DeviceAlertFindUniqueOrThrowArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first DeviceAlert that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertFindFirstArgs} args - Arguments to find a DeviceAlert
     * @example
     * // Get one DeviceAlert
     * const deviceAlert = await prisma.deviceAlert.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends DeviceAlertFindFirstArgs>(args?: SelectSubset<T, DeviceAlertFindFirstArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first DeviceAlert that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertFindFirstOrThrowArgs} args - Arguments to find a DeviceAlert
     * @example
     * // Get one DeviceAlert
     * const deviceAlert = await prisma.deviceAlert.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends DeviceAlertFindFirstOrThrowArgs>(args?: SelectSubset<T, DeviceAlertFindFirstOrThrowArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more DeviceAlerts that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all DeviceAlerts
     * const deviceAlerts = await prisma.deviceAlert.findMany()
     * 
     * // Get first 10 DeviceAlerts
     * const deviceAlerts = await prisma.deviceAlert.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const deviceAlertWithIdOnly = await prisma.deviceAlert.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends DeviceAlertFindManyArgs>(args?: SelectSubset<T, DeviceAlertFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a DeviceAlert.
     * @param {DeviceAlertCreateArgs} args - Arguments to create a DeviceAlert.
     * @example
     * // Create one DeviceAlert
     * const DeviceAlert = await prisma.deviceAlert.create({
     *   data: {
     *     // ... data to create a DeviceAlert
     *   }
     * })
     * 
     */
    create<T extends DeviceAlertCreateArgs>(args: SelectSubset<T, DeviceAlertCreateArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many DeviceAlerts.
     * @param {DeviceAlertCreateManyArgs} args - Arguments to create many DeviceAlerts.
     * @example
     * // Create many DeviceAlerts
     * const deviceAlert = await prisma.deviceAlert.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends DeviceAlertCreateManyArgs>(args?: SelectSubset<T, DeviceAlertCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many DeviceAlerts and returns the data saved in the database.
     * @param {DeviceAlertCreateManyAndReturnArgs} args - Arguments to create many DeviceAlerts.
     * @example
     * // Create many DeviceAlerts
     * const deviceAlert = await prisma.deviceAlert.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many DeviceAlerts and only return the `id`
     * const deviceAlertWithIdOnly = await prisma.deviceAlert.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends DeviceAlertCreateManyAndReturnArgs>(args?: SelectSubset<T, DeviceAlertCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a DeviceAlert.
     * @param {DeviceAlertDeleteArgs} args - Arguments to delete one DeviceAlert.
     * @example
     * // Delete one DeviceAlert
     * const DeviceAlert = await prisma.deviceAlert.delete({
     *   where: {
     *     // ... filter to delete one DeviceAlert
     *   }
     * })
     * 
     */
    delete<T extends DeviceAlertDeleteArgs>(args: SelectSubset<T, DeviceAlertDeleteArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one DeviceAlert.
     * @param {DeviceAlertUpdateArgs} args - Arguments to update one DeviceAlert.
     * @example
     * // Update one DeviceAlert
     * const deviceAlert = await prisma.deviceAlert.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends DeviceAlertUpdateArgs>(args: SelectSubset<T, DeviceAlertUpdateArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more DeviceAlerts.
     * @param {DeviceAlertDeleteManyArgs} args - Arguments to filter DeviceAlerts to delete.
     * @example
     * // Delete a few DeviceAlerts
     * const { count } = await prisma.deviceAlert.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends DeviceAlertDeleteManyArgs>(args?: SelectSubset<T, DeviceAlertDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more DeviceAlerts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many DeviceAlerts
     * const deviceAlert = await prisma.deviceAlert.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends DeviceAlertUpdateManyArgs>(args: SelectSubset<T, DeviceAlertUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one DeviceAlert.
     * @param {DeviceAlertUpsertArgs} args - Arguments to update or create a DeviceAlert.
     * @example
     * // Update or create a DeviceAlert
     * const deviceAlert = await prisma.deviceAlert.upsert({
     *   create: {
     *     // ... data to create a DeviceAlert
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the DeviceAlert we want to update
     *   }
     * })
     */
    upsert<T extends DeviceAlertUpsertArgs>(args: SelectSubset<T, DeviceAlertUpsertArgs<ExtArgs>>): Prisma__DeviceAlertClient<$Result.GetResult<Prisma.$DeviceAlertPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of DeviceAlerts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertCountArgs} args - Arguments to filter DeviceAlerts to count.
     * @example
     * // Count the number of DeviceAlerts
     * const count = await prisma.deviceAlert.count({
     *   where: {
     *     // ... the filter for the DeviceAlerts we want to count
     *   }
     * })
    **/
    count<T extends DeviceAlertCountArgs>(
      args?: Subset<T, DeviceAlertCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], DeviceAlertCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a DeviceAlert.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
     * @example
     * // Ordered by age ascending
     * // Where email contains prisma.io
     * // Limited to the 10 users
     * const aggregations = await prisma.user.aggregate({
     *   _avg: {
     *     age: true,
     *   },
     *   where: {
     *     email: {
     *       contains: "prisma.io",
     *     },
     *   },
     *   orderBy: {
     *     age: "asc",
     *   },
     *   take: 10,
     * })
    **/
    aggregate<T extends DeviceAlertAggregateArgs>(args: Subset<T, DeviceAlertAggregateArgs>): Prisma.PrismaPromise<GetDeviceAlertAggregateType<T>>

    /**
     * Group by DeviceAlert.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {DeviceAlertGroupByArgs} args - Group by arguments.
     * @example
     * // Group by city, order by createdAt, get count
     * const result = await prisma.user.groupBy({
     *   by: ['city', 'createdAt'],
     *   orderBy: {
     *     createdAt: true
     *   },
     *   _count: {
     *     _all: true
     *   },
     * })
     * 
    **/
    groupBy<
      T extends DeviceAlertGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: DeviceAlertGroupByArgs['orderBy'] }
        : { orderBy?: DeviceAlertGroupByArgs['orderBy'] },
      OrderFields extends ExcludeUnderscoreKeys<Keys<MaybeTupleToUnion<T['orderBy']>>>,
      ByFields extends MaybeTupleToUnion<T['by']>,
      ByValid extends Has<ByFields, OrderFields>,
      HavingFields extends GetHavingFields<T['having']>,
      HavingValid extends Has<ByFields, HavingFields>,
      ByEmpty extends T['by'] extends never[] ? True : False,
      InputErrors extends ByEmpty extends True
      ? `Error: "by" must not be empty.`
      : HavingValid extends False
      ? {
          [P in HavingFields]: P extends ByFields
            ? never
            : P extends string
            ? `Error: Field "${P}" used in "having" needs to be provided in "by".`
            : [
                Error,
                'Field ',
                P,
                ` in "having" needs to be provided in "by"`,
              ]
        }[HavingFields]
      : 'take' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "take", you also need to provide "orderBy"'
      : 'skip' extends Keys<T>
      ? 'orderBy' extends Keys<T>
        ? ByValid extends True
          ? {}
          : {
              [P in OrderFields]: P extends ByFields
                ? never
                : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
            }[OrderFields]
        : 'Error: If you provide "skip", you also need to provide "orderBy"'
      : ByValid extends True
      ? {}
      : {
          [P in OrderFields]: P extends ByFields
            ? never
            : `Error: Field "${P}" in "orderBy" needs to be provided in "by"`
        }[OrderFields]
    >(args: SubsetIntersection<T, DeviceAlertGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetDeviceAlertGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the DeviceAlert model
   */
  readonly fields: DeviceAlertFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for DeviceAlert.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__DeviceAlertClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    device<T extends DeviceDefaultArgs<ExtArgs> = {}>(args?: Subset<T, DeviceDefaultArgs<ExtArgs>>): Prisma__DeviceClient<$Result.GetResult<Prisma.$DevicePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    /**
     * Attaches callbacks for the resolution and/or rejection of the Promise.
     * @param onfulfilled The callback to execute when the Promise is resolved.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of which ever callback is executed.
     */
    then<TResult1 = T, TResult2 = never>(onfulfilled?: ((value: T) => TResult1 | PromiseLike<TResult1>) | undefined | null, onrejected?: ((reason: any) => TResult2 | PromiseLike<TResult2>) | undefined | null): $Utils.JsPromise<TResult1 | TResult2>
    /**
     * Attaches a callback for only the rejection of the Promise.
     * @param onrejected The callback to execute when the Promise is rejected.
     * @returns A Promise for the completion of the callback.
     */
    catch<TResult = never>(onrejected?: ((reason: any) => TResult | PromiseLike<TResult>) | undefined | null): $Utils.JsPromise<T | TResult>
    /**
     * Attaches a callback that is invoked when the Promise is settled (fulfilled or rejected). The
     * resolved value cannot be modified from the callback.
     * @param onfinally The callback to execute when the Promise is settled (fulfilled or rejected).
     * @returns A Promise for the completion of the callback.
     */
    finally(onfinally?: (() => void) | undefined | null): $Utils.JsPromise<T>
  }




  /**
   * Fields of the DeviceAlert model
   */ 
  interface DeviceAlertFieldRefs {
    readonly id: FieldRef<"DeviceAlert", 'String'>
    readonly deviceId: FieldRef<"DeviceAlert", 'String'>
    readonly tenantId: FieldRef<"DeviceAlert", 'String'>
    readonly alertType: FieldRef<"DeviceAlert", 'String'>
    readonly severity: FieldRef<"DeviceAlert", 'AlertSeverity'>
    readonly message: FieldRef<"DeviceAlert", 'String'>
    readonly acknowledged: FieldRef<"DeviceAlert", 'Boolean'>
    readonly acknowledgedBy: FieldRef<"DeviceAlert", 'String'>
    readonly acknowledgedAt: FieldRef<"DeviceAlert", 'DateTime'>
    readonly resolvedAt: FieldRef<"DeviceAlert", 'DateTime'>
    readonly metadata: FieldRef<"DeviceAlert", 'Json'>
    readonly createdAt: FieldRef<"DeviceAlert", 'DateTime'>
    readonly updatedAt: FieldRef<"DeviceAlert", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * DeviceAlert findUnique
   */
  export type DeviceAlertFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * Filter, which DeviceAlert to fetch.
     */
    where: DeviceAlertWhereUniqueInput
  }

  /**
   * DeviceAlert findUniqueOrThrow
   */
  export type DeviceAlertFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * Filter, which DeviceAlert to fetch.
     */
    where: DeviceAlertWhereUniqueInput
  }

  /**
   * DeviceAlert findFirst
   */
  export type DeviceAlertFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * Filter, which DeviceAlert to fetch.
     */
    where?: DeviceAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of DeviceAlerts to fetch.
     */
    orderBy?: DeviceAlertOrderByWithRelationInput | DeviceAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for DeviceAlerts.
     */
    cursor?: DeviceAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` DeviceAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` DeviceAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of DeviceAlerts.
     */
    distinct?: DeviceAlertScalarFieldEnum | DeviceAlertScalarFieldEnum[]
  }

  /**
   * DeviceAlert findFirstOrThrow
   */
  export type DeviceAlertFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * Filter, which DeviceAlert to fetch.
     */
    where?: DeviceAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of DeviceAlerts to fetch.
     */
    orderBy?: DeviceAlertOrderByWithRelationInput | DeviceAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for DeviceAlerts.
     */
    cursor?: DeviceAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` DeviceAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` DeviceAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of DeviceAlerts.
     */
    distinct?: DeviceAlertScalarFieldEnum | DeviceAlertScalarFieldEnum[]
  }

  /**
   * DeviceAlert findMany
   */
  export type DeviceAlertFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * Filter, which DeviceAlerts to fetch.
     */
    where?: DeviceAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of DeviceAlerts to fetch.
     */
    orderBy?: DeviceAlertOrderByWithRelationInput | DeviceAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing DeviceAlerts.
     */
    cursor?: DeviceAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` DeviceAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` DeviceAlerts.
     */
    skip?: number
    distinct?: DeviceAlertScalarFieldEnum | DeviceAlertScalarFieldEnum[]
  }

  /**
   * DeviceAlert create
   */
  export type DeviceAlertCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * The data needed to create a DeviceAlert.
     */
    data: XOR<DeviceAlertCreateInput, DeviceAlertUncheckedCreateInput>
  }

  /**
   * DeviceAlert createMany
   */
  export type DeviceAlertCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many DeviceAlerts.
     */
    data: DeviceAlertCreateManyInput | DeviceAlertCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * DeviceAlert createManyAndReturn
   */
  export type DeviceAlertCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many DeviceAlerts.
     */
    data: DeviceAlertCreateManyInput | DeviceAlertCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * DeviceAlert update
   */
  export type DeviceAlertUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * The data needed to update a DeviceAlert.
     */
    data: XOR<DeviceAlertUpdateInput, DeviceAlertUncheckedUpdateInput>
    /**
     * Choose, which DeviceAlert to update.
     */
    where: DeviceAlertWhereUniqueInput
  }

  /**
   * DeviceAlert updateMany
   */
  export type DeviceAlertUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update DeviceAlerts.
     */
    data: XOR<DeviceAlertUpdateManyMutationInput, DeviceAlertUncheckedUpdateManyInput>
    /**
     * Filter which DeviceAlerts to update
     */
    where?: DeviceAlertWhereInput
  }

  /**
   * DeviceAlert upsert
   */
  export type DeviceAlertUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * The filter to search for the DeviceAlert to update in case it exists.
     */
    where: DeviceAlertWhereUniqueInput
    /**
     * In case the DeviceAlert found by the `where` argument doesn't exist, create a new DeviceAlert with this data.
     */
    create: XOR<DeviceAlertCreateInput, DeviceAlertUncheckedCreateInput>
    /**
     * In case the DeviceAlert was found with the provided `where` argument, update it with this data.
     */
    update: XOR<DeviceAlertUpdateInput, DeviceAlertUncheckedUpdateInput>
  }

  /**
   * DeviceAlert delete
   */
  export type DeviceAlertDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
    /**
     * Filter which DeviceAlert to delete.
     */
    where: DeviceAlertWhereUniqueInput
  }

  /**
   * DeviceAlert deleteMany
   */
  export type DeviceAlertDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which DeviceAlerts to delete
     */
    where?: DeviceAlertWhereInput
  }

  /**
   * DeviceAlert without action
   */
  export type DeviceAlertDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the DeviceAlert
     */
    select?: DeviceAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: DeviceAlertInclude<ExtArgs> | null
  }


  /**
   * Enums
   */

  export const TransactionIsolationLevel: {
    ReadUncommitted: 'ReadUncommitted',
    ReadCommitted: 'ReadCommitted',
    RepeatableRead: 'RepeatableRead',
    Serializable: 'Serializable'
  };

  export type TransactionIsolationLevel = (typeof TransactionIsolationLevel)[keyof typeof TransactionIsolationLevel]


  export const DeviceScalarFieldEnum: {
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

  export type DeviceScalarFieldEnum = (typeof DeviceScalarFieldEnum)[keyof typeof DeviceScalarFieldEnum]


  export const SensorScalarFieldEnum: {
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

  export type SensorScalarFieldEnum = (typeof SensorScalarFieldEnum)[keyof typeof SensorScalarFieldEnum]


  export const SensorReadingScalarFieldEnum: {
    id: 'id',
    sensorId: 'sensorId',
    deviceId: 'deviceId',
    value: 'value',
    unit: 'unit',
    timestamp: 'timestamp',
    quality: 'quality',
    metadata: 'metadata'
  };

  export type SensorReadingScalarFieldEnum = (typeof SensorReadingScalarFieldEnum)[keyof typeof SensorReadingScalarFieldEnum]


  export const ActuatorScalarFieldEnum: {
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

  export type ActuatorScalarFieldEnum = (typeof ActuatorScalarFieldEnum)[keyof typeof ActuatorScalarFieldEnum]


  export const ActuatorCommandScalarFieldEnum: {
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

  export type ActuatorCommandScalarFieldEnum = (typeof ActuatorCommandScalarFieldEnum)[keyof typeof ActuatorCommandScalarFieldEnum]


  export const DeviceAlertScalarFieldEnum: {
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

  export type DeviceAlertScalarFieldEnum = (typeof DeviceAlertScalarFieldEnum)[keyof typeof DeviceAlertScalarFieldEnum]


  export const SortOrder: {
    asc: 'asc',
    desc: 'desc'
  };

  export type SortOrder = (typeof SortOrder)[keyof typeof SortOrder]


  export const NullableJsonNullValueInput: {
    DbNull: typeof DbNull,
    JsonNull: typeof JsonNull
  };

  export type NullableJsonNullValueInput = (typeof NullableJsonNullValueInput)[keyof typeof NullableJsonNullValueInput]


  export const QueryMode: {
    default: 'default',
    insensitive: 'insensitive'
  };

  export type QueryMode = (typeof QueryMode)[keyof typeof QueryMode]


  export const JsonNullValueFilter: {
    DbNull: typeof DbNull,
    JsonNull: typeof JsonNull,
    AnyNull: typeof AnyNull
  };

  export type JsonNullValueFilter = (typeof JsonNullValueFilter)[keyof typeof JsonNullValueFilter]


  export const NullsOrder: {
    first: 'first',
    last: 'last'
  };

  export type NullsOrder = (typeof NullsOrder)[keyof typeof NullsOrder]


  /**
   * Field references 
   */


  /**
   * Reference to a field of type 'String'
   */
  export type StringFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'String'>
    


  /**
   * Reference to a field of type 'String[]'
   */
  export type ListStringFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'String[]'>
    


  /**
   * Reference to a field of type 'DeviceType'
   */
  export type EnumDeviceTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'DeviceType'>
    


  /**
   * Reference to a field of type 'DeviceType[]'
   */
  export type ListEnumDeviceTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'DeviceType[]'>
    


  /**
   * Reference to a field of type 'DeviceStatus'
   */
  export type EnumDeviceStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'DeviceStatus'>
    


  /**
   * Reference to a field of type 'DeviceStatus[]'
   */
  export type ListEnumDeviceStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'DeviceStatus[]'>
    


  /**
   * Reference to a field of type 'DateTime'
   */
  export type DateTimeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'DateTime'>
    


  /**
   * Reference to a field of type 'DateTime[]'
   */
  export type ListDateTimeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'DateTime[]'>
    


  /**
   * Reference to a field of type 'Json'
   */
  export type JsonFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Json'>
    


  /**
   * Reference to a field of type 'SensorType'
   */
  export type EnumSensorTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'SensorType'>
    


  /**
   * Reference to a field of type 'SensorType[]'
   */
  export type ListEnumSensorTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'SensorType[]'>
    


  /**
   * Reference to a field of type 'Float'
   */
  export type FloatFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Float'>
    


  /**
   * Reference to a field of type 'Float[]'
   */
  export type ListFloatFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Float[]'>
    


  /**
   * Reference to a field of type 'ActuatorType'
   */
  export type EnumActuatorTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'ActuatorType'>
    


  /**
   * Reference to a field of type 'ActuatorType[]'
   */
  export type ListEnumActuatorTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'ActuatorType[]'>
    


  /**
   * Reference to a field of type 'CommandStatus'
   */
  export type EnumCommandStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'CommandStatus'>
    


  /**
   * Reference to a field of type 'CommandStatus[]'
   */
  export type ListEnumCommandStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'CommandStatus[]'>
    


  /**
   * Reference to a field of type 'AlertSeverity'
   */
  export type EnumAlertSeverityFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertSeverity'>
    


  /**
   * Reference to a field of type 'AlertSeverity[]'
   */
  export type ListEnumAlertSeverityFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertSeverity[]'>
    


  /**
   * Reference to a field of type 'Boolean'
   */
  export type BooleanFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Boolean'>
    


  /**
   * Reference to a field of type 'Int'
   */
  export type IntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Int'>
    


  /**
   * Reference to a field of type 'Int[]'
   */
  export type ListIntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Int[]'>
    
  /**
   * Deep Input Types
   */


  export type DeviceWhereInput = {
    AND?: DeviceWhereInput | DeviceWhereInput[]
    OR?: DeviceWhereInput[]
    NOT?: DeviceWhereInput | DeviceWhereInput[]
    id?: StringFilter<"Device"> | string
    tenantId?: StringFilter<"Device"> | string
    deviceId?: StringFilter<"Device"> | string
    name?: StringFilter<"Device"> | string
    type?: EnumDeviceTypeFilter<"Device"> | $Enums.DeviceType
    status?: EnumDeviceStatusFilter<"Device"> | $Enums.DeviceStatus
    lastSeen?: DateTimeNullableFilter<"Device"> | Date | string | null
    metadata?: JsonNullableFilter<"Device">
    fieldId?: StringNullableFilter<"Device"> | string | null
    createdAt?: DateTimeFilter<"Device"> | Date | string
    updatedAt?: DateTimeFilter<"Device"> | Date | string
    sensors?: SensorListRelationFilter
    sensorReadings?: SensorReadingListRelationFilter
    actuators?: ActuatorListRelationFilter
    alerts?: DeviceAlertListRelationFilter
  }

  export type DeviceOrderByWithRelationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    deviceId?: SortOrder
    name?: SortOrder
    type?: SortOrder
    status?: SortOrder
    lastSeen?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    fieldId?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    sensors?: SensorOrderByRelationAggregateInput
    sensorReadings?: SensorReadingOrderByRelationAggregateInput
    actuators?: ActuatorOrderByRelationAggregateInput
    alerts?: DeviceAlertOrderByRelationAggregateInput
  }

  export type DeviceWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    tenantId_deviceId?: DeviceTenantIdDeviceIdCompoundUniqueInput
    AND?: DeviceWhereInput | DeviceWhereInput[]
    OR?: DeviceWhereInput[]
    NOT?: DeviceWhereInput | DeviceWhereInput[]
    tenantId?: StringFilter<"Device"> | string
    deviceId?: StringFilter<"Device"> | string
    name?: StringFilter<"Device"> | string
    type?: EnumDeviceTypeFilter<"Device"> | $Enums.DeviceType
    status?: EnumDeviceStatusFilter<"Device"> | $Enums.DeviceStatus
    lastSeen?: DateTimeNullableFilter<"Device"> | Date | string | null
    metadata?: JsonNullableFilter<"Device">
    fieldId?: StringNullableFilter<"Device"> | string | null
    createdAt?: DateTimeFilter<"Device"> | Date | string
    updatedAt?: DateTimeFilter<"Device"> | Date | string
    sensors?: SensorListRelationFilter
    sensorReadings?: SensorReadingListRelationFilter
    actuators?: ActuatorListRelationFilter
    alerts?: DeviceAlertListRelationFilter
  }, "id" | "tenantId_deviceId">

  export type DeviceOrderByWithAggregationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    deviceId?: SortOrder
    name?: SortOrder
    type?: SortOrder
    status?: SortOrder
    lastSeen?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    fieldId?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: DeviceCountOrderByAggregateInput
    _max?: DeviceMaxOrderByAggregateInput
    _min?: DeviceMinOrderByAggregateInput
  }

  export type DeviceScalarWhereWithAggregatesInput = {
    AND?: DeviceScalarWhereWithAggregatesInput | DeviceScalarWhereWithAggregatesInput[]
    OR?: DeviceScalarWhereWithAggregatesInput[]
    NOT?: DeviceScalarWhereWithAggregatesInput | DeviceScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"Device"> | string
    tenantId?: StringWithAggregatesFilter<"Device"> | string
    deviceId?: StringWithAggregatesFilter<"Device"> | string
    name?: StringWithAggregatesFilter<"Device"> | string
    type?: EnumDeviceTypeWithAggregatesFilter<"Device"> | $Enums.DeviceType
    status?: EnumDeviceStatusWithAggregatesFilter<"Device"> | $Enums.DeviceStatus
    lastSeen?: DateTimeNullableWithAggregatesFilter<"Device"> | Date | string | null
    metadata?: JsonNullableWithAggregatesFilter<"Device">
    fieldId?: StringNullableWithAggregatesFilter<"Device"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"Device"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Device"> | Date | string
  }

  export type SensorWhereInput = {
    AND?: SensorWhereInput | SensorWhereInput[]
    OR?: SensorWhereInput[]
    NOT?: SensorWhereInput | SensorWhereInput[]
    id?: StringFilter<"Sensor"> | string
    deviceId?: StringFilter<"Sensor"> | string
    sensorType?: EnumSensorTypeFilter<"Sensor"> | $Enums.SensorType
    unit?: StringFilter<"Sensor"> | string
    calibrationData?: JsonNullableFilter<"Sensor">
    lastReading?: FloatNullableFilter<"Sensor"> | number | null
    lastReadingAt?: DateTimeNullableFilter<"Sensor"> | Date | string | null
    createdAt?: DateTimeFilter<"Sensor"> | Date | string
    updatedAt?: DateTimeFilter<"Sensor"> | Date | string
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
    readings?: SensorReadingListRelationFilter
  }

  export type SensorOrderByWithRelationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    sensorType?: SortOrder
    unit?: SortOrder
    calibrationData?: SortOrderInput | SortOrder
    lastReading?: SortOrderInput | SortOrder
    lastReadingAt?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    device?: DeviceOrderByWithRelationInput
    readings?: SensorReadingOrderByRelationAggregateInput
  }

  export type SensorWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: SensorWhereInput | SensorWhereInput[]
    OR?: SensorWhereInput[]
    NOT?: SensorWhereInput | SensorWhereInput[]
    deviceId?: StringFilter<"Sensor"> | string
    sensorType?: EnumSensorTypeFilter<"Sensor"> | $Enums.SensorType
    unit?: StringFilter<"Sensor"> | string
    calibrationData?: JsonNullableFilter<"Sensor">
    lastReading?: FloatNullableFilter<"Sensor"> | number | null
    lastReadingAt?: DateTimeNullableFilter<"Sensor"> | Date | string | null
    createdAt?: DateTimeFilter<"Sensor"> | Date | string
    updatedAt?: DateTimeFilter<"Sensor"> | Date | string
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
    readings?: SensorReadingListRelationFilter
  }, "id">

  export type SensorOrderByWithAggregationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    sensorType?: SortOrder
    unit?: SortOrder
    calibrationData?: SortOrderInput | SortOrder
    lastReading?: SortOrderInput | SortOrder
    lastReadingAt?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: SensorCountOrderByAggregateInput
    _avg?: SensorAvgOrderByAggregateInput
    _max?: SensorMaxOrderByAggregateInput
    _min?: SensorMinOrderByAggregateInput
    _sum?: SensorSumOrderByAggregateInput
  }

  export type SensorScalarWhereWithAggregatesInput = {
    AND?: SensorScalarWhereWithAggregatesInput | SensorScalarWhereWithAggregatesInput[]
    OR?: SensorScalarWhereWithAggregatesInput[]
    NOT?: SensorScalarWhereWithAggregatesInput | SensorScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"Sensor"> | string
    deviceId?: StringWithAggregatesFilter<"Sensor"> | string
    sensorType?: EnumSensorTypeWithAggregatesFilter<"Sensor"> | $Enums.SensorType
    unit?: StringWithAggregatesFilter<"Sensor"> | string
    calibrationData?: JsonNullableWithAggregatesFilter<"Sensor">
    lastReading?: FloatNullableWithAggregatesFilter<"Sensor"> | number | null
    lastReadingAt?: DateTimeNullableWithAggregatesFilter<"Sensor"> | Date | string | null
    createdAt?: DateTimeWithAggregatesFilter<"Sensor"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Sensor"> | Date | string
  }

  export type SensorReadingWhereInput = {
    AND?: SensorReadingWhereInput | SensorReadingWhereInput[]
    OR?: SensorReadingWhereInput[]
    NOT?: SensorReadingWhereInput | SensorReadingWhereInput[]
    id?: StringFilter<"SensorReading"> | string
    sensorId?: StringFilter<"SensorReading"> | string
    deviceId?: StringFilter<"SensorReading"> | string
    value?: FloatFilter<"SensorReading"> | number
    unit?: StringFilter<"SensorReading"> | string
    timestamp?: DateTimeFilter<"SensorReading"> | Date | string
    quality?: FloatNullableFilter<"SensorReading"> | number | null
    metadata?: JsonNullableFilter<"SensorReading">
    sensor?: XOR<SensorRelationFilter, SensorWhereInput>
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
  }

  export type SensorReadingOrderByWithRelationInput = {
    id?: SortOrder
    sensorId?: SortOrder
    deviceId?: SortOrder
    value?: SortOrder
    unit?: SortOrder
    timestamp?: SortOrder
    quality?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    sensor?: SensorOrderByWithRelationInput
    device?: DeviceOrderByWithRelationInput
  }

  export type SensorReadingWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: SensorReadingWhereInput | SensorReadingWhereInput[]
    OR?: SensorReadingWhereInput[]
    NOT?: SensorReadingWhereInput | SensorReadingWhereInput[]
    sensorId?: StringFilter<"SensorReading"> | string
    deviceId?: StringFilter<"SensorReading"> | string
    value?: FloatFilter<"SensorReading"> | number
    unit?: StringFilter<"SensorReading"> | string
    timestamp?: DateTimeFilter<"SensorReading"> | Date | string
    quality?: FloatNullableFilter<"SensorReading"> | number | null
    metadata?: JsonNullableFilter<"SensorReading">
    sensor?: XOR<SensorRelationFilter, SensorWhereInput>
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
  }, "id">

  export type SensorReadingOrderByWithAggregationInput = {
    id?: SortOrder
    sensorId?: SortOrder
    deviceId?: SortOrder
    value?: SortOrder
    unit?: SortOrder
    timestamp?: SortOrder
    quality?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    _count?: SensorReadingCountOrderByAggregateInput
    _avg?: SensorReadingAvgOrderByAggregateInput
    _max?: SensorReadingMaxOrderByAggregateInput
    _min?: SensorReadingMinOrderByAggregateInput
    _sum?: SensorReadingSumOrderByAggregateInput
  }

  export type SensorReadingScalarWhereWithAggregatesInput = {
    AND?: SensorReadingScalarWhereWithAggregatesInput | SensorReadingScalarWhereWithAggregatesInput[]
    OR?: SensorReadingScalarWhereWithAggregatesInput[]
    NOT?: SensorReadingScalarWhereWithAggregatesInput | SensorReadingScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"SensorReading"> | string
    sensorId?: StringWithAggregatesFilter<"SensorReading"> | string
    deviceId?: StringWithAggregatesFilter<"SensorReading"> | string
    value?: FloatWithAggregatesFilter<"SensorReading"> | number
    unit?: StringWithAggregatesFilter<"SensorReading"> | string
    timestamp?: DateTimeWithAggregatesFilter<"SensorReading"> | Date | string
    quality?: FloatNullableWithAggregatesFilter<"SensorReading"> | number | null
    metadata?: JsonNullableWithAggregatesFilter<"SensorReading">
  }

  export type ActuatorWhereInput = {
    AND?: ActuatorWhereInput | ActuatorWhereInput[]
    OR?: ActuatorWhereInput[]
    NOT?: ActuatorWhereInput | ActuatorWhereInput[]
    id?: StringFilter<"Actuator"> | string
    deviceId?: StringFilter<"Actuator"> | string
    actuatorType?: EnumActuatorTypeFilter<"Actuator"> | $Enums.ActuatorType
    name?: StringNullableFilter<"Actuator"> | string | null
    currentState?: JsonNullableFilter<"Actuator">
    lastCommand?: StringNullableFilter<"Actuator"> | string | null
    lastCommandAt?: DateTimeNullableFilter<"Actuator"> | Date | string | null
    createdAt?: DateTimeFilter<"Actuator"> | Date | string
    updatedAt?: DateTimeFilter<"Actuator"> | Date | string
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
    commands?: ActuatorCommandListRelationFilter
  }

  export type ActuatorOrderByWithRelationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    actuatorType?: SortOrder
    name?: SortOrderInput | SortOrder
    currentState?: SortOrderInput | SortOrder
    lastCommand?: SortOrderInput | SortOrder
    lastCommandAt?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    device?: DeviceOrderByWithRelationInput
    commands?: ActuatorCommandOrderByRelationAggregateInput
  }

  export type ActuatorWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: ActuatorWhereInput | ActuatorWhereInput[]
    OR?: ActuatorWhereInput[]
    NOT?: ActuatorWhereInput | ActuatorWhereInput[]
    deviceId?: StringFilter<"Actuator"> | string
    actuatorType?: EnumActuatorTypeFilter<"Actuator"> | $Enums.ActuatorType
    name?: StringNullableFilter<"Actuator"> | string | null
    currentState?: JsonNullableFilter<"Actuator">
    lastCommand?: StringNullableFilter<"Actuator"> | string | null
    lastCommandAt?: DateTimeNullableFilter<"Actuator"> | Date | string | null
    createdAt?: DateTimeFilter<"Actuator"> | Date | string
    updatedAt?: DateTimeFilter<"Actuator"> | Date | string
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
    commands?: ActuatorCommandListRelationFilter
  }, "id">

  export type ActuatorOrderByWithAggregationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    actuatorType?: SortOrder
    name?: SortOrderInput | SortOrder
    currentState?: SortOrderInput | SortOrder
    lastCommand?: SortOrderInput | SortOrder
    lastCommandAt?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: ActuatorCountOrderByAggregateInput
    _max?: ActuatorMaxOrderByAggregateInput
    _min?: ActuatorMinOrderByAggregateInput
  }

  export type ActuatorScalarWhereWithAggregatesInput = {
    AND?: ActuatorScalarWhereWithAggregatesInput | ActuatorScalarWhereWithAggregatesInput[]
    OR?: ActuatorScalarWhereWithAggregatesInput[]
    NOT?: ActuatorScalarWhereWithAggregatesInput | ActuatorScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"Actuator"> | string
    deviceId?: StringWithAggregatesFilter<"Actuator"> | string
    actuatorType?: EnumActuatorTypeWithAggregatesFilter<"Actuator"> | $Enums.ActuatorType
    name?: StringNullableWithAggregatesFilter<"Actuator"> | string | null
    currentState?: JsonNullableWithAggregatesFilter<"Actuator">
    lastCommand?: StringNullableWithAggregatesFilter<"Actuator"> | string | null
    lastCommandAt?: DateTimeNullableWithAggregatesFilter<"Actuator"> | Date | string | null
    createdAt?: DateTimeWithAggregatesFilter<"Actuator"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Actuator"> | Date | string
  }

  export type ActuatorCommandWhereInput = {
    AND?: ActuatorCommandWhereInput | ActuatorCommandWhereInput[]
    OR?: ActuatorCommandWhereInput[]
    NOT?: ActuatorCommandWhereInput | ActuatorCommandWhereInput[]
    id?: StringFilter<"ActuatorCommand"> | string
    actuatorId?: StringFilter<"ActuatorCommand"> | string
    command?: StringFilter<"ActuatorCommand"> | string
    parameters?: JsonNullableFilter<"ActuatorCommand">
    status?: EnumCommandStatusFilter<"ActuatorCommand"> | $Enums.CommandStatus
    requestedAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    executedAt?: DateTimeNullableFilter<"ActuatorCommand"> | Date | string | null
    completedAt?: DateTimeNullableFilter<"ActuatorCommand"> | Date | string | null
    errorMessage?: StringNullableFilter<"ActuatorCommand"> | string | null
    createdAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    updatedAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    actuator?: XOR<ActuatorRelationFilter, ActuatorWhereInput>
  }

  export type ActuatorCommandOrderByWithRelationInput = {
    id?: SortOrder
    actuatorId?: SortOrder
    command?: SortOrder
    parameters?: SortOrderInput | SortOrder
    status?: SortOrder
    requestedAt?: SortOrder
    executedAt?: SortOrderInput | SortOrder
    completedAt?: SortOrderInput | SortOrder
    errorMessage?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    actuator?: ActuatorOrderByWithRelationInput
  }

  export type ActuatorCommandWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: ActuatorCommandWhereInput | ActuatorCommandWhereInput[]
    OR?: ActuatorCommandWhereInput[]
    NOT?: ActuatorCommandWhereInput | ActuatorCommandWhereInput[]
    actuatorId?: StringFilter<"ActuatorCommand"> | string
    command?: StringFilter<"ActuatorCommand"> | string
    parameters?: JsonNullableFilter<"ActuatorCommand">
    status?: EnumCommandStatusFilter<"ActuatorCommand"> | $Enums.CommandStatus
    requestedAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    executedAt?: DateTimeNullableFilter<"ActuatorCommand"> | Date | string | null
    completedAt?: DateTimeNullableFilter<"ActuatorCommand"> | Date | string | null
    errorMessage?: StringNullableFilter<"ActuatorCommand"> | string | null
    createdAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    updatedAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    actuator?: XOR<ActuatorRelationFilter, ActuatorWhereInput>
  }, "id">

  export type ActuatorCommandOrderByWithAggregationInput = {
    id?: SortOrder
    actuatorId?: SortOrder
    command?: SortOrder
    parameters?: SortOrderInput | SortOrder
    status?: SortOrder
    requestedAt?: SortOrder
    executedAt?: SortOrderInput | SortOrder
    completedAt?: SortOrderInput | SortOrder
    errorMessage?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: ActuatorCommandCountOrderByAggregateInput
    _max?: ActuatorCommandMaxOrderByAggregateInput
    _min?: ActuatorCommandMinOrderByAggregateInput
  }

  export type ActuatorCommandScalarWhereWithAggregatesInput = {
    AND?: ActuatorCommandScalarWhereWithAggregatesInput | ActuatorCommandScalarWhereWithAggregatesInput[]
    OR?: ActuatorCommandScalarWhereWithAggregatesInput[]
    NOT?: ActuatorCommandScalarWhereWithAggregatesInput | ActuatorCommandScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"ActuatorCommand"> | string
    actuatorId?: StringWithAggregatesFilter<"ActuatorCommand"> | string
    command?: StringWithAggregatesFilter<"ActuatorCommand"> | string
    parameters?: JsonNullableWithAggregatesFilter<"ActuatorCommand">
    status?: EnumCommandStatusWithAggregatesFilter<"ActuatorCommand"> | $Enums.CommandStatus
    requestedAt?: DateTimeWithAggregatesFilter<"ActuatorCommand"> | Date | string
    executedAt?: DateTimeNullableWithAggregatesFilter<"ActuatorCommand"> | Date | string | null
    completedAt?: DateTimeNullableWithAggregatesFilter<"ActuatorCommand"> | Date | string | null
    errorMessage?: StringNullableWithAggregatesFilter<"ActuatorCommand"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"ActuatorCommand"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"ActuatorCommand"> | Date | string
  }

  export type DeviceAlertWhereInput = {
    AND?: DeviceAlertWhereInput | DeviceAlertWhereInput[]
    OR?: DeviceAlertWhereInput[]
    NOT?: DeviceAlertWhereInput | DeviceAlertWhereInput[]
    id?: StringFilter<"DeviceAlert"> | string
    deviceId?: StringFilter<"DeviceAlert"> | string
    tenantId?: StringFilter<"DeviceAlert"> | string
    alertType?: StringFilter<"DeviceAlert"> | string
    severity?: EnumAlertSeverityFilter<"DeviceAlert"> | $Enums.AlertSeverity
    message?: StringFilter<"DeviceAlert"> | string
    acknowledged?: BoolFilter<"DeviceAlert"> | boolean
    acknowledgedBy?: StringNullableFilter<"DeviceAlert"> | string | null
    acknowledgedAt?: DateTimeNullableFilter<"DeviceAlert"> | Date | string | null
    resolvedAt?: DateTimeNullableFilter<"DeviceAlert"> | Date | string | null
    metadata?: JsonNullableFilter<"DeviceAlert">
    createdAt?: DateTimeFilter<"DeviceAlert"> | Date | string
    updatedAt?: DateTimeFilter<"DeviceAlert"> | Date | string
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
  }

  export type DeviceAlertOrderByWithRelationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    message?: SortOrder
    acknowledged?: SortOrder
    acknowledgedBy?: SortOrderInput | SortOrder
    acknowledgedAt?: SortOrderInput | SortOrder
    resolvedAt?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    device?: DeviceOrderByWithRelationInput
  }

  export type DeviceAlertWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: DeviceAlertWhereInput | DeviceAlertWhereInput[]
    OR?: DeviceAlertWhereInput[]
    NOT?: DeviceAlertWhereInput | DeviceAlertWhereInput[]
    deviceId?: StringFilter<"DeviceAlert"> | string
    tenantId?: StringFilter<"DeviceAlert"> | string
    alertType?: StringFilter<"DeviceAlert"> | string
    severity?: EnumAlertSeverityFilter<"DeviceAlert"> | $Enums.AlertSeverity
    message?: StringFilter<"DeviceAlert"> | string
    acknowledged?: BoolFilter<"DeviceAlert"> | boolean
    acknowledgedBy?: StringNullableFilter<"DeviceAlert"> | string | null
    acknowledgedAt?: DateTimeNullableFilter<"DeviceAlert"> | Date | string | null
    resolvedAt?: DateTimeNullableFilter<"DeviceAlert"> | Date | string | null
    metadata?: JsonNullableFilter<"DeviceAlert">
    createdAt?: DateTimeFilter<"DeviceAlert"> | Date | string
    updatedAt?: DateTimeFilter<"DeviceAlert"> | Date | string
    device?: XOR<DeviceRelationFilter, DeviceWhereInput>
  }, "id">

  export type DeviceAlertOrderByWithAggregationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    message?: SortOrder
    acknowledged?: SortOrder
    acknowledgedBy?: SortOrderInput | SortOrder
    acknowledgedAt?: SortOrderInput | SortOrder
    resolvedAt?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: DeviceAlertCountOrderByAggregateInput
    _max?: DeviceAlertMaxOrderByAggregateInput
    _min?: DeviceAlertMinOrderByAggregateInput
  }

  export type DeviceAlertScalarWhereWithAggregatesInput = {
    AND?: DeviceAlertScalarWhereWithAggregatesInput | DeviceAlertScalarWhereWithAggregatesInput[]
    OR?: DeviceAlertScalarWhereWithAggregatesInput[]
    NOT?: DeviceAlertScalarWhereWithAggregatesInput | DeviceAlertScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"DeviceAlert"> | string
    deviceId?: StringWithAggregatesFilter<"DeviceAlert"> | string
    tenantId?: StringWithAggregatesFilter<"DeviceAlert"> | string
    alertType?: StringWithAggregatesFilter<"DeviceAlert"> | string
    severity?: EnumAlertSeverityWithAggregatesFilter<"DeviceAlert"> | $Enums.AlertSeverity
    message?: StringWithAggregatesFilter<"DeviceAlert"> | string
    acknowledged?: BoolWithAggregatesFilter<"DeviceAlert"> | boolean
    acknowledgedBy?: StringNullableWithAggregatesFilter<"DeviceAlert"> | string | null
    acknowledgedAt?: DateTimeNullableWithAggregatesFilter<"DeviceAlert"> | Date | string | null
    resolvedAt?: DateTimeNullableWithAggregatesFilter<"DeviceAlert"> | Date | string | null
    metadata?: JsonNullableWithAggregatesFilter<"DeviceAlert">
    createdAt?: DateTimeWithAggregatesFilter<"DeviceAlert"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"DeviceAlert"> | Date | string
  }

  export type DeviceCreateInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorCreateNestedManyWithoutDeviceInput
    sensorReadings?: SensorReadingCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertCreateNestedManyWithoutDeviceInput
  }

  export type DeviceUncheckedCreateInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorUncheckedCreateNestedManyWithoutDeviceInput
    sensorReadings?: SensorReadingUncheckedCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorUncheckedCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertUncheckedCreateNestedManyWithoutDeviceInput
  }

  export type DeviceUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUpdateManyWithoutDeviceNestedInput
    sensorReadings?: SensorReadingUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUncheckedUpdateManyWithoutDeviceNestedInput
    sensorReadings?: SensorReadingUncheckedUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUncheckedUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUncheckedUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceCreateManyInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type DeviceUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SensorCreateInput = {
    id?: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    device: DeviceCreateNestedOneWithoutSensorsInput
    readings?: SensorReadingCreateNestedManyWithoutSensorInput
  }

  export type SensorUncheckedCreateInput = {
    id?: string
    deviceId: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    readings?: SensorReadingUncheckedCreateNestedManyWithoutSensorInput
  }

  export type SensorUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    device?: DeviceUpdateOneRequiredWithoutSensorsNestedInput
    readings?: SensorReadingUpdateManyWithoutSensorNestedInput
  }

  export type SensorUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    readings?: SensorReadingUncheckedUpdateManyWithoutSensorNestedInput
  }

  export type SensorCreateManyInput = {
    id?: string
    deviceId: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SensorUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SensorUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SensorReadingCreateInput = {
    id?: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    sensor: SensorCreateNestedOneWithoutReadingsInput
    device: DeviceCreateNestedOneWithoutSensorReadingsInput
  }

  export type SensorReadingUncheckedCreateInput = {
    id?: string
    sensorId: string
    deviceId: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    sensor?: SensorUpdateOneRequiredWithoutReadingsNestedInput
    device?: DeviceUpdateOneRequiredWithoutSensorReadingsNestedInput
  }

  export type SensorReadingUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingCreateManyInput = {
    id?: string
    sensorId: string
    deviceId: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type ActuatorCreateInput = {
    id?: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    device: DeviceCreateNestedOneWithoutActuatorsInput
    commands?: ActuatorCommandCreateNestedManyWithoutActuatorInput
  }

  export type ActuatorUncheckedCreateInput = {
    id?: string
    deviceId: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    commands?: ActuatorCommandUncheckedCreateNestedManyWithoutActuatorInput
  }

  export type ActuatorUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    device?: DeviceUpdateOneRequiredWithoutActuatorsNestedInput
    commands?: ActuatorCommandUpdateManyWithoutActuatorNestedInput
  }

  export type ActuatorUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    commands?: ActuatorCommandUncheckedUpdateManyWithoutActuatorNestedInput
  }

  export type ActuatorCreateManyInput = {
    id?: string
    deviceId: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ActuatorUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ActuatorCommandCreateInput = {
    id?: string
    command: string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: $Enums.CommandStatus
    requestedAt?: Date | string
    executedAt?: Date | string | null
    completedAt?: Date | string | null
    errorMessage?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    actuator: ActuatorCreateNestedOneWithoutCommandsInput
  }

  export type ActuatorCommandUncheckedCreateInput = {
    id?: string
    actuatorId: string
    command: string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: $Enums.CommandStatus
    requestedAt?: Date | string
    executedAt?: Date | string | null
    completedAt?: Date | string | null
    errorMessage?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorCommandUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    actuator?: ActuatorUpdateOneRequiredWithoutCommandsNestedInput
  }

  export type ActuatorCommandUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorId?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ActuatorCommandCreateManyInput = {
    id?: string
    actuatorId: string
    command: string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: $Enums.CommandStatus
    requestedAt?: Date | string
    executedAt?: Date | string | null
    completedAt?: Date | string | null
    errorMessage?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorCommandUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ActuatorCommandUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorId?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceAlertCreateInput = {
    id?: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged?: boolean
    acknowledgedBy?: string | null
    acknowledgedAt?: Date | string | null
    resolvedAt?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
    device: DeviceCreateNestedOneWithoutAlertsInput
  }

  export type DeviceAlertUncheckedCreateInput = {
    id?: string
    deviceId: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged?: boolean
    acknowledgedBy?: string | null
    acknowledgedAt?: Date | string | null
    resolvedAt?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type DeviceAlertUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    device?: DeviceUpdateOneRequiredWithoutAlertsNestedInput
  }

  export type DeviceAlertUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceAlertCreateManyInput = {
    id?: string
    deviceId: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged?: boolean
    acknowledgedBy?: string | null
    acknowledgedAt?: Date | string | null
    resolvedAt?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type DeviceAlertUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceAlertUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StringFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedStringFilter<$PrismaModel> | string
  }

  export type EnumDeviceTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceType | EnumDeviceTypeFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceTypeFilter<$PrismaModel> | $Enums.DeviceType
  }

  export type EnumDeviceStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceStatus | EnumDeviceStatusFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceStatusFilter<$PrismaModel> | $Enums.DeviceStatus
  }

  export type DateTimeNullableFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel> | null
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeNullableFilter<$PrismaModel> | Date | string | null
  }
  export type JsonNullableFilter<$PrismaModel = never> = 
    | PatchUndefined<
        Either<Required<JsonNullableFilterBase<$PrismaModel>>, Exclude<keyof Required<JsonNullableFilterBase<$PrismaModel>>, 'path'>>,
        Required<JsonNullableFilterBase<$PrismaModel>>
      >
    | OptionalFlat<Omit<Required<JsonNullableFilterBase<$PrismaModel>>, 'path'>>

  export type JsonNullableFilterBase<$PrismaModel = never> = {
    equals?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | JsonNullValueFilter
    path?: string[]
    string_contains?: string | StringFieldRefInput<$PrismaModel>
    string_starts_with?: string | StringFieldRefInput<$PrismaModel>
    string_ends_with?: string | StringFieldRefInput<$PrismaModel>
    array_contains?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    array_starts_with?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    array_ends_with?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    lt?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    lte?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    gt?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    gte?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    not?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | JsonNullValueFilter
  }

  export type StringNullableFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedStringNullableFilter<$PrismaModel> | string | null
  }

  export type DateTimeFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeFilter<$PrismaModel> | Date | string
  }

  export type SensorListRelationFilter = {
    every?: SensorWhereInput
    some?: SensorWhereInput
    none?: SensorWhereInput
  }

  export type SensorReadingListRelationFilter = {
    every?: SensorReadingWhereInput
    some?: SensorReadingWhereInput
    none?: SensorReadingWhereInput
  }

  export type ActuatorListRelationFilter = {
    every?: ActuatorWhereInput
    some?: ActuatorWhereInput
    none?: ActuatorWhereInput
  }

  export type DeviceAlertListRelationFilter = {
    every?: DeviceAlertWhereInput
    some?: DeviceAlertWhereInput
    none?: DeviceAlertWhereInput
  }

  export type SortOrderInput = {
    sort: SortOrder
    nulls?: NullsOrder
  }

  export type SensorOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type SensorReadingOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type ActuatorOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type DeviceAlertOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type DeviceTenantIdDeviceIdCompoundUniqueInput = {
    tenantId: string
    deviceId: string
  }

  export type DeviceCountOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    deviceId?: SortOrder
    name?: SortOrder
    type?: SortOrder
    status?: SortOrder
    lastSeen?: SortOrder
    metadata?: SortOrder
    fieldId?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type DeviceMaxOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    deviceId?: SortOrder
    name?: SortOrder
    type?: SortOrder
    status?: SortOrder
    lastSeen?: SortOrder
    fieldId?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type DeviceMinOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    deviceId?: SortOrder
    name?: SortOrder
    type?: SortOrder
    status?: SortOrder
    lastSeen?: SortOrder
    fieldId?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type StringWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedStringWithAggregatesFilter<$PrismaModel> | string
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedStringFilter<$PrismaModel>
    _max?: NestedStringFilter<$PrismaModel>
  }

  export type EnumDeviceTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceType | EnumDeviceTypeFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceTypeWithAggregatesFilter<$PrismaModel> | $Enums.DeviceType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumDeviceTypeFilter<$PrismaModel>
    _max?: NestedEnumDeviceTypeFilter<$PrismaModel>
  }

  export type EnumDeviceStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceStatus | EnumDeviceStatusFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceStatusWithAggregatesFilter<$PrismaModel> | $Enums.DeviceStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumDeviceStatusFilter<$PrismaModel>
    _max?: NestedEnumDeviceStatusFilter<$PrismaModel>
  }

  export type DateTimeNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel> | null
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeNullableWithAggregatesFilter<$PrismaModel> | Date | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedDateTimeNullableFilter<$PrismaModel>
    _max?: NestedDateTimeNullableFilter<$PrismaModel>
  }
  export type JsonNullableWithAggregatesFilter<$PrismaModel = never> = 
    | PatchUndefined<
        Either<Required<JsonNullableWithAggregatesFilterBase<$PrismaModel>>, Exclude<keyof Required<JsonNullableWithAggregatesFilterBase<$PrismaModel>>, 'path'>>,
        Required<JsonNullableWithAggregatesFilterBase<$PrismaModel>>
      >
    | OptionalFlat<Omit<Required<JsonNullableWithAggregatesFilterBase<$PrismaModel>>, 'path'>>

  export type JsonNullableWithAggregatesFilterBase<$PrismaModel = never> = {
    equals?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | JsonNullValueFilter
    path?: string[]
    string_contains?: string | StringFieldRefInput<$PrismaModel>
    string_starts_with?: string | StringFieldRefInput<$PrismaModel>
    string_ends_with?: string | StringFieldRefInput<$PrismaModel>
    array_contains?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    array_starts_with?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    array_ends_with?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    lt?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    lte?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    gt?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    gte?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    not?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | JsonNullValueFilter
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedJsonNullableFilter<$PrismaModel>
    _max?: NestedJsonNullableFilter<$PrismaModel>
  }

  export type StringNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedStringNullableWithAggregatesFilter<$PrismaModel> | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedStringNullableFilter<$PrismaModel>
    _max?: NestedStringNullableFilter<$PrismaModel>
  }

  export type DateTimeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeWithAggregatesFilter<$PrismaModel> | Date | string
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedDateTimeFilter<$PrismaModel>
    _max?: NestedDateTimeFilter<$PrismaModel>
  }

  export type EnumSensorTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.SensorType | EnumSensorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumSensorTypeFilter<$PrismaModel> | $Enums.SensorType
  }

  export type FloatNullableFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel> | null
    in?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatNullableFilter<$PrismaModel> | number | null
  }

  export type DeviceRelationFilter = {
    is?: DeviceWhereInput
    isNot?: DeviceWhereInput
  }

  export type SensorCountOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    sensorType?: SortOrder
    unit?: SortOrder
    calibrationData?: SortOrder
    lastReading?: SortOrder
    lastReadingAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SensorAvgOrderByAggregateInput = {
    lastReading?: SortOrder
  }

  export type SensorMaxOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    sensorType?: SortOrder
    unit?: SortOrder
    lastReading?: SortOrder
    lastReadingAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SensorMinOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    sensorType?: SortOrder
    unit?: SortOrder
    lastReading?: SortOrder
    lastReadingAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SensorSumOrderByAggregateInput = {
    lastReading?: SortOrder
  }

  export type EnumSensorTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.SensorType | EnumSensorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumSensorTypeWithAggregatesFilter<$PrismaModel> | $Enums.SensorType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumSensorTypeFilter<$PrismaModel>
    _max?: NestedEnumSensorTypeFilter<$PrismaModel>
  }

  export type FloatNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel> | null
    in?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatNullableWithAggregatesFilter<$PrismaModel> | number | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _avg?: NestedFloatNullableFilter<$PrismaModel>
    _sum?: NestedFloatNullableFilter<$PrismaModel>
    _min?: NestedFloatNullableFilter<$PrismaModel>
    _max?: NestedFloatNullableFilter<$PrismaModel>
  }

  export type FloatFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel>
    in?: number[] | ListFloatFieldRefInput<$PrismaModel>
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel>
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatFilter<$PrismaModel> | number
  }

  export type SensorRelationFilter = {
    is?: SensorWhereInput
    isNot?: SensorWhereInput
  }

  export type SensorReadingCountOrderByAggregateInput = {
    id?: SortOrder
    sensorId?: SortOrder
    deviceId?: SortOrder
    value?: SortOrder
    unit?: SortOrder
    timestamp?: SortOrder
    quality?: SortOrder
    metadata?: SortOrder
  }

  export type SensorReadingAvgOrderByAggregateInput = {
    value?: SortOrder
    quality?: SortOrder
  }

  export type SensorReadingMaxOrderByAggregateInput = {
    id?: SortOrder
    sensorId?: SortOrder
    deviceId?: SortOrder
    value?: SortOrder
    unit?: SortOrder
    timestamp?: SortOrder
    quality?: SortOrder
  }

  export type SensorReadingMinOrderByAggregateInput = {
    id?: SortOrder
    sensorId?: SortOrder
    deviceId?: SortOrder
    value?: SortOrder
    unit?: SortOrder
    timestamp?: SortOrder
    quality?: SortOrder
  }

  export type SensorReadingSumOrderByAggregateInput = {
    value?: SortOrder
    quality?: SortOrder
  }

  export type FloatWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel>
    in?: number[] | ListFloatFieldRefInput<$PrismaModel>
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel>
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatWithAggregatesFilter<$PrismaModel> | number
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedFloatFilter<$PrismaModel>
    _sum?: NestedFloatFilter<$PrismaModel>
    _min?: NestedFloatFilter<$PrismaModel>
    _max?: NestedFloatFilter<$PrismaModel>
  }

  export type EnumActuatorTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.ActuatorType | EnumActuatorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumActuatorTypeFilter<$PrismaModel> | $Enums.ActuatorType
  }

  export type ActuatorCommandListRelationFilter = {
    every?: ActuatorCommandWhereInput
    some?: ActuatorCommandWhereInput
    none?: ActuatorCommandWhereInput
  }

  export type ActuatorCommandOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type ActuatorCountOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    actuatorType?: SortOrder
    name?: SortOrder
    currentState?: SortOrder
    lastCommand?: SortOrder
    lastCommandAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ActuatorMaxOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    actuatorType?: SortOrder
    name?: SortOrder
    lastCommand?: SortOrder
    lastCommandAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ActuatorMinOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    actuatorType?: SortOrder
    name?: SortOrder
    lastCommand?: SortOrder
    lastCommandAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type EnumActuatorTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.ActuatorType | EnumActuatorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumActuatorTypeWithAggregatesFilter<$PrismaModel> | $Enums.ActuatorType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumActuatorTypeFilter<$PrismaModel>
    _max?: NestedEnumActuatorTypeFilter<$PrismaModel>
  }

  export type EnumCommandStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.CommandStatus | EnumCommandStatusFieldRefInput<$PrismaModel>
    in?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumCommandStatusFilter<$PrismaModel> | $Enums.CommandStatus
  }

  export type ActuatorRelationFilter = {
    is?: ActuatorWhereInput
    isNot?: ActuatorWhereInput
  }

  export type ActuatorCommandCountOrderByAggregateInput = {
    id?: SortOrder
    actuatorId?: SortOrder
    command?: SortOrder
    parameters?: SortOrder
    status?: SortOrder
    requestedAt?: SortOrder
    executedAt?: SortOrder
    completedAt?: SortOrder
    errorMessage?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ActuatorCommandMaxOrderByAggregateInput = {
    id?: SortOrder
    actuatorId?: SortOrder
    command?: SortOrder
    status?: SortOrder
    requestedAt?: SortOrder
    executedAt?: SortOrder
    completedAt?: SortOrder
    errorMessage?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ActuatorCommandMinOrderByAggregateInput = {
    id?: SortOrder
    actuatorId?: SortOrder
    command?: SortOrder
    status?: SortOrder
    requestedAt?: SortOrder
    executedAt?: SortOrder
    completedAt?: SortOrder
    errorMessage?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type EnumCommandStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.CommandStatus | EnumCommandStatusFieldRefInput<$PrismaModel>
    in?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumCommandStatusWithAggregatesFilter<$PrismaModel> | $Enums.CommandStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumCommandStatusFilter<$PrismaModel>
    _max?: NestedEnumCommandStatusFilter<$PrismaModel>
  }

  export type EnumAlertSeverityFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertSeverity | EnumAlertSeverityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertSeverityFilter<$PrismaModel> | $Enums.AlertSeverity
  }

  export type BoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
  }

  export type DeviceAlertCountOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    message?: SortOrder
    acknowledged?: SortOrder
    acknowledgedBy?: SortOrder
    acknowledgedAt?: SortOrder
    resolvedAt?: SortOrder
    metadata?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type DeviceAlertMaxOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    message?: SortOrder
    acknowledged?: SortOrder
    acknowledgedBy?: SortOrder
    acknowledgedAt?: SortOrder
    resolvedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type DeviceAlertMinOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    message?: SortOrder
    acknowledged?: SortOrder
    acknowledgedBy?: SortOrder
    acknowledgedAt?: SortOrder
    resolvedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type EnumAlertSeverityWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertSeverity | EnumAlertSeverityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertSeverityWithAggregatesFilter<$PrismaModel> | $Enums.AlertSeverity
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertSeverityFilter<$PrismaModel>
    _max?: NestedEnumAlertSeverityFilter<$PrismaModel>
  }

  export type BoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
  }

  export type SensorCreateNestedManyWithoutDeviceInput = {
    create?: XOR<SensorCreateWithoutDeviceInput, SensorUncheckedCreateWithoutDeviceInput> | SensorCreateWithoutDeviceInput[] | SensorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorCreateOrConnectWithoutDeviceInput | SensorCreateOrConnectWithoutDeviceInput[]
    createMany?: SensorCreateManyDeviceInputEnvelope
    connect?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
  }

  export type SensorReadingCreateNestedManyWithoutDeviceInput = {
    create?: XOR<SensorReadingCreateWithoutDeviceInput, SensorReadingUncheckedCreateWithoutDeviceInput> | SensorReadingCreateWithoutDeviceInput[] | SensorReadingUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutDeviceInput | SensorReadingCreateOrConnectWithoutDeviceInput[]
    createMany?: SensorReadingCreateManyDeviceInputEnvelope
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
  }

  export type ActuatorCreateNestedManyWithoutDeviceInput = {
    create?: XOR<ActuatorCreateWithoutDeviceInput, ActuatorUncheckedCreateWithoutDeviceInput> | ActuatorCreateWithoutDeviceInput[] | ActuatorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: ActuatorCreateOrConnectWithoutDeviceInput | ActuatorCreateOrConnectWithoutDeviceInput[]
    createMany?: ActuatorCreateManyDeviceInputEnvelope
    connect?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
  }

  export type DeviceAlertCreateNestedManyWithoutDeviceInput = {
    create?: XOR<DeviceAlertCreateWithoutDeviceInput, DeviceAlertUncheckedCreateWithoutDeviceInput> | DeviceAlertCreateWithoutDeviceInput[] | DeviceAlertUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: DeviceAlertCreateOrConnectWithoutDeviceInput | DeviceAlertCreateOrConnectWithoutDeviceInput[]
    createMany?: DeviceAlertCreateManyDeviceInputEnvelope
    connect?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
  }

  export type SensorUncheckedCreateNestedManyWithoutDeviceInput = {
    create?: XOR<SensorCreateWithoutDeviceInput, SensorUncheckedCreateWithoutDeviceInput> | SensorCreateWithoutDeviceInput[] | SensorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorCreateOrConnectWithoutDeviceInput | SensorCreateOrConnectWithoutDeviceInput[]
    createMany?: SensorCreateManyDeviceInputEnvelope
    connect?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
  }

  export type SensorReadingUncheckedCreateNestedManyWithoutDeviceInput = {
    create?: XOR<SensorReadingCreateWithoutDeviceInput, SensorReadingUncheckedCreateWithoutDeviceInput> | SensorReadingCreateWithoutDeviceInput[] | SensorReadingUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutDeviceInput | SensorReadingCreateOrConnectWithoutDeviceInput[]
    createMany?: SensorReadingCreateManyDeviceInputEnvelope
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
  }

  export type ActuatorUncheckedCreateNestedManyWithoutDeviceInput = {
    create?: XOR<ActuatorCreateWithoutDeviceInput, ActuatorUncheckedCreateWithoutDeviceInput> | ActuatorCreateWithoutDeviceInput[] | ActuatorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: ActuatorCreateOrConnectWithoutDeviceInput | ActuatorCreateOrConnectWithoutDeviceInput[]
    createMany?: ActuatorCreateManyDeviceInputEnvelope
    connect?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
  }

  export type DeviceAlertUncheckedCreateNestedManyWithoutDeviceInput = {
    create?: XOR<DeviceAlertCreateWithoutDeviceInput, DeviceAlertUncheckedCreateWithoutDeviceInput> | DeviceAlertCreateWithoutDeviceInput[] | DeviceAlertUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: DeviceAlertCreateOrConnectWithoutDeviceInput | DeviceAlertCreateOrConnectWithoutDeviceInput[]
    createMany?: DeviceAlertCreateManyDeviceInputEnvelope
    connect?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
  }

  export type StringFieldUpdateOperationsInput = {
    set?: string
  }

  export type EnumDeviceTypeFieldUpdateOperationsInput = {
    set?: $Enums.DeviceType
  }

  export type EnumDeviceStatusFieldUpdateOperationsInput = {
    set?: $Enums.DeviceStatus
  }

  export type NullableDateTimeFieldUpdateOperationsInput = {
    set?: Date | string | null
  }

  export type NullableStringFieldUpdateOperationsInput = {
    set?: string | null
  }

  export type DateTimeFieldUpdateOperationsInput = {
    set?: Date | string
  }

  export type SensorUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<SensorCreateWithoutDeviceInput, SensorUncheckedCreateWithoutDeviceInput> | SensorCreateWithoutDeviceInput[] | SensorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorCreateOrConnectWithoutDeviceInput | SensorCreateOrConnectWithoutDeviceInput[]
    upsert?: SensorUpsertWithWhereUniqueWithoutDeviceInput | SensorUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: SensorCreateManyDeviceInputEnvelope
    set?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    disconnect?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    delete?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    connect?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    update?: SensorUpdateWithWhereUniqueWithoutDeviceInput | SensorUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: SensorUpdateManyWithWhereWithoutDeviceInput | SensorUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: SensorScalarWhereInput | SensorScalarWhereInput[]
  }

  export type SensorReadingUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<SensorReadingCreateWithoutDeviceInput, SensorReadingUncheckedCreateWithoutDeviceInput> | SensorReadingCreateWithoutDeviceInput[] | SensorReadingUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutDeviceInput | SensorReadingCreateOrConnectWithoutDeviceInput[]
    upsert?: SensorReadingUpsertWithWhereUniqueWithoutDeviceInput | SensorReadingUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: SensorReadingCreateManyDeviceInputEnvelope
    set?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    disconnect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    delete?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    update?: SensorReadingUpdateWithWhereUniqueWithoutDeviceInput | SensorReadingUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: SensorReadingUpdateManyWithWhereWithoutDeviceInput | SensorReadingUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: SensorReadingScalarWhereInput | SensorReadingScalarWhereInput[]
  }

  export type ActuatorUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<ActuatorCreateWithoutDeviceInput, ActuatorUncheckedCreateWithoutDeviceInput> | ActuatorCreateWithoutDeviceInput[] | ActuatorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: ActuatorCreateOrConnectWithoutDeviceInput | ActuatorCreateOrConnectWithoutDeviceInput[]
    upsert?: ActuatorUpsertWithWhereUniqueWithoutDeviceInput | ActuatorUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: ActuatorCreateManyDeviceInputEnvelope
    set?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    disconnect?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    delete?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    connect?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    update?: ActuatorUpdateWithWhereUniqueWithoutDeviceInput | ActuatorUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: ActuatorUpdateManyWithWhereWithoutDeviceInput | ActuatorUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: ActuatorScalarWhereInput | ActuatorScalarWhereInput[]
  }

  export type DeviceAlertUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<DeviceAlertCreateWithoutDeviceInput, DeviceAlertUncheckedCreateWithoutDeviceInput> | DeviceAlertCreateWithoutDeviceInput[] | DeviceAlertUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: DeviceAlertCreateOrConnectWithoutDeviceInput | DeviceAlertCreateOrConnectWithoutDeviceInput[]
    upsert?: DeviceAlertUpsertWithWhereUniqueWithoutDeviceInput | DeviceAlertUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: DeviceAlertCreateManyDeviceInputEnvelope
    set?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    disconnect?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    delete?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    connect?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    update?: DeviceAlertUpdateWithWhereUniqueWithoutDeviceInput | DeviceAlertUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: DeviceAlertUpdateManyWithWhereWithoutDeviceInput | DeviceAlertUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: DeviceAlertScalarWhereInput | DeviceAlertScalarWhereInput[]
  }

  export type SensorUncheckedUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<SensorCreateWithoutDeviceInput, SensorUncheckedCreateWithoutDeviceInput> | SensorCreateWithoutDeviceInput[] | SensorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorCreateOrConnectWithoutDeviceInput | SensorCreateOrConnectWithoutDeviceInput[]
    upsert?: SensorUpsertWithWhereUniqueWithoutDeviceInput | SensorUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: SensorCreateManyDeviceInputEnvelope
    set?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    disconnect?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    delete?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    connect?: SensorWhereUniqueInput | SensorWhereUniqueInput[]
    update?: SensorUpdateWithWhereUniqueWithoutDeviceInput | SensorUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: SensorUpdateManyWithWhereWithoutDeviceInput | SensorUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: SensorScalarWhereInput | SensorScalarWhereInput[]
  }

  export type SensorReadingUncheckedUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<SensorReadingCreateWithoutDeviceInput, SensorReadingUncheckedCreateWithoutDeviceInput> | SensorReadingCreateWithoutDeviceInput[] | SensorReadingUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutDeviceInput | SensorReadingCreateOrConnectWithoutDeviceInput[]
    upsert?: SensorReadingUpsertWithWhereUniqueWithoutDeviceInput | SensorReadingUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: SensorReadingCreateManyDeviceInputEnvelope
    set?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    disconnect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    delete?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    update?: SensorReadingUpdateWithWhereUniqueWithoutDeviceInput | SensorReadingUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: SensorReadingUpdateManyWithWhereWithoutDeviceInput | SensorReadingUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: SensorReadingScalarWhereInput | SensorReadingScalarWhereInput[]
  }

  export type ActuatorUncheckedUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<ActuatorCreateWithoutDeviceInput, ActuatorUncheckedCreateWithoutDeviceInput> | ActuatorCreateWithoutDeviceInput[] | ActuatorUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: ActuatorCreateOrConnectWithoutDeviceInput | ActuatorCreateOrConnectWithoutDeviceInput[]
    upsert?: ActuatorUpsertWithWhereUniqueWithoutDeviceInput | ActuatorUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: ActuatorCreateManyDeviceInputEnvelope
    set?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    disconnect?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    delete?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    connect?: ActuatorWhereUniqueInput | ActuatorWhereUniqueInput[]
    update?: ActuatorUpdateWithWhereUniqueWithoutDeviceInput | ActuatorUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: ActuatorUpdateManyWithWhereWithoutDeviceInput | ActuatorUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: ActuatorScalarWhereInput | ActuatorScalarWhereInput[]
  }

  export type DeviceAlertUncheckedUpdateManyWithoutDeviceNestedInput = {
    create?: XOR<DeviceAlertCreateWithoutDeviceInput, DeviceAlertUncheckedCreateWithoutDeviceInput> | DeviceAlertCreateWithoutDeviceInput[] | DeviceAlertUncheckedCreateWithoutDeviceInput[]
    connectOrCreate?: DeviceAlertCreateOrConnectWithoutDeviceInput | DeviceAlertCreateOrConnectWithoutDeviceInput[]
    upsert?: DeviceAlertUpsertWithWhereUniqueWithoutDeviceInput | DeviceAlertUpsertWithWhereUniqueWithoutDeviceInput[]
    createMany?: DeviceAlertCreateManyDeviceInputEnvelope
    set?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    disconnect?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    delete?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    connect?: DeviceAlertWhereUniqueInput | DeviceAlertWhereUniqueInput[]
    update?: DeviceAlertUpdateWithWhereUniqueWithoutDeviceInput | DeviceAlertUpdateWithWhereUniqueWithoutDeviceInput[]
    updateMany?: DeviceAlertUpdateManyWithWhereWithoutDeviceInput | DeviceAlertUpdateManyWithWhereWithoutDeviceInput[]
    deleteMany?: DeviceAlertScalarWhereInput | DeviceAlertScalarWhereInput[]
  }

  export type DeviceCreateNestedOneWithoutSensorsInput = {
    create?: XOR<DeviceCreateWithoutSensorsInput, DeviceUncheckedCreateWithoutSensorsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutSensorsInput
    connect?: DeviceWhereUniqueInput
  }

  export type SensorReadingCreateNestedManyWithoutSensorInput = {
    create?: XOR<SensorReadingCreateWithoutSensorInput, SensorReadingUncheckedCreateWithoutSensorInput> | SensorReadingCreateWithoutSensorInput[] | SensorReadingUncheckedCreateWithoutSensorInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutSensorInput | SensorReadingCreateOrConnectWithoutSensorInput[]
    createMany?: SensorReadingCreateManySensorInputEnvelope
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
  }

  export type SensorReadingUncheckedCreateNestedManyWithoutSensorInput = {
    create?: XOR<SensorReadingCreateWithoutSensorInput, SensorReadingUncheckedCreateWithoutSensorInput> | SensorReadingCreateWithoutSensorInput[] | SensorReadingUncheckedCreateWithoutSensorInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutSensorInput | SensorReadingCreateOrConnectWithoutSensorInput[]
    createMany?: SensorReadingCreateManySensorInputEnvelope
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
  }

  export type EnumSensorTypeFieldUpdateOperationsInput = {
    set?: $Enums.SensorType
  }

  export type NullableFloatFieldUpdateOperationsInput = {
    set?: number | null
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type DeviceUpdateOneRequiredWithoutSensorsNestedInput = {
    create?: XOR<DeviceCreateWithoutSensorsInput, DeviceUncheckedCreateWithoutSensorsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutSensorsInput
    upsert?: DeviceUpsertWithoutSensorsInput
    connect?: DeviceWhereUniqueInput
    update?: XOR<XOR<DeviceUpdateToOneWithWhereWithoutSensorsInput, DeviceUpdateWithoutSensorsInput>, DeviceUncheckedUpdateWithoutSensorsInput>
  }

  export type SensorReadingUpdateManyWithoutSensorNestedInput = {
    create?: XOR<SensorReadingCreateWithoutSensorInput, SensorReadingUncheckedCreateWithoutSensorInput> | SensorReadingCreateWithoutSensorInput[] | SensorReadingUncheckedCreateWithoutSensorInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutSensorInput | SensorReadingCreateOrConnectWithoutSensorInput[]
    upsert?: SensorReadingUpsertWithWhereUniqueWithoutSensorInput | SensorReadingUpsertWithWhereUniqueWithoutSensorInput[]
    createMany?: SensorReadingCreateManySensorInputEnvelope
    set?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    disconnect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    delete?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    update?: SensorReadingUpdateWithWhereUniqueWithoutSensorInput | SensorReadingUpdateWithWhereUniqueWithoutSensorInput[]
    updateMany?: SensorReadingUpdateManyWithWhereWithoutSensorInput | SensorReadingUpdateManyWithWhereWithoutSensorInput[]
    deleteMany?: SensorReadingScalarWhereInput | SensorReadingScalarWhereInput[]
  }

  export type SensorReadingUncheckedUpdateManyWithoutSensorNestedInput = {
    create?: XOR<SensorReadingCreateWithoutSensorInput, SensorReadingUncheckedCreateWithoutSensorInput> | SensorReadingCreateWithoutSensorInput[] | SensorReadingUncheckedCreateWithoutSensorInput[]
    connectOrCreate?: SensorReadingCreateOrConnectWithoutSensorInput | SensorReadingCreateOrConnectWithoutSensorInput[]
    upsert?: SensorReadingUpsertWithWhereUniqueWithoutSensorInput | SensorReadingUpsertWithWhereUniqueWithoutSensorInput[]
    createMany?: SensorReadingCreateManySensorInputEnvelope
    set?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    disconnect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    delete?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    connect?: SensorReadingWhereUniqueInput | SensorReadingWhereUniqueInput[]
    update?: SensorReadingUpdateWithWhereUniqueWithoutSensorInput | SensorReadingUpdateWithWhereUniqueWithoutSensorInput[]
    updateMany?: SensorReadingUpdateManyWithWhereWithoutSensorInput | SensorReadingUpdateManyWithWhereWithoutSensorInput[]
    deleteMany?: SensorReadingScalarWhereInput | SensorReadingScalarWhereInput[]
  }

  export type SensorCreateNestedOneWithoutReadingsInput = {
    create?: XOR<SensorCreateWithoutReadingsInput, SensorUncheckedCreateWithoutReadingsInput>
    connectOrCreate?: SensorCreateOrConnectWithoutReadingsInput
    connect?: SensorWhereUniqueInput
  }

  export type DeviceCreateNestedOneWithoutSensorReadingsInput = {
    create?: XOR<DeviceCreateWithoutSensorReadingsInput, DeviceUncheckedCreateWithoutSensorReadingsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutSensorReadingsInput
    connect?: DeviceWhereUniqueInput
  }

  export type FloatFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type SensorUpdateOneRequiredWithoutReadingsNestedInput = {
    create?: XOR<SensorCreateWithoutReadingsInput, SensorUncheckedCreateWithoutReadingsInput>
    connectOrCreate?: SensorCreateOrConnectWithoutReadingsInput
    upsert?: SensorUpsertWithoutReadingsInput
    connect?: SensorWhereUniqueInput
    update?: XOR<XOR<SensorUpdateToOneWithWhereWithoutReadingsInput, SensorUpdateWithoutReadingsInput>, SensorUncheckedUpdateWithoutReadingsInput>
  }

  export type DeviceUpdateOneRequiredWithoutSensorReadingsNestedInput = {
    create?: XOR<DeviceCreateWithoutSensorReadingsInput, DeviceUncheckedCreateWithoutSensorReadingsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutSensorReadingsInput
    upsert?: DeviceUpsertWithoutSensorReadingsInput
    connect?: DeviceWhereUniqueInput
    update?: XOR<XOR<DeviceUpdateToOneWithWhereWithoutSensorReadingsInput, DeviceUpdateWithoutSensorReadingsInput>, DeviceUncheckedUpdateWithoutSensorReadingsInput>
  }

  export type DeviceCreateNestedOneWithoutActuatorsInput = {
    create?: XOR<DeviceCreateWithoutActuatorsInput, DeviceUncheckedCreateWithoutActuatorsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutActuatorsInput
    connect?: DeviceWhereUniqueInput
  }

  export type ActuatorCommandCreateNestedManyWithoutActuatorInput = {
    create?: XOR<ActuatorCommandCreateWithoutActuatorInput, ActuatorCommandUncheckedCreateWithoutActuatorInput> | ActuatorCommandCreateWithoutActuatorInput[] | ActuatorCommandUncheckedCreateWithoutActuatorInput[]
    connectOrCreate?: ActuatorCommandCreateOrConnectWithoutActuatorInput | ActuatorCommandCreateOrConnectWithoutActuatorInput[]
    createMany?: ActuatorCommandCreateManyActuatorInputEnvelope
    connect?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
  }

  export type ActuatorCommandUncheckedCreateNestedManyWithoutActuatorInput = {
    create?: XOR<ActuatorCommandCreateWithoutActuatorInput, ActuatorCommandUncheckedCreateWithoutActuatorInput> | ActuatorCommandCreateWithoutActuatorInput[] | ActuatorCommandUncheckedCreateWithoutActuatorInput[]
    connectOrCreate?: ActuatorCommandCreateOrConnectWithoutActuatorInput | ActuatorCommandCreateOrConnectWithoutActuatorInput[]
    createMany?: ActuatorCommandCreateManyActuatorInputEnvelope
    connect?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
  }

  export type EnumActuatorTypeFieldUpdateOperationsInput = {
    set?: $Enums.ActuatorType
  }

  export type DeviceUpdateOneRequiredWithoutActuatorsNestedInput = {
    create?: XOR<DeviceCreateWithoutActuatorsInput, DeviceUncheckedCreateWithoutActuatorsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutActuatorsInput
    upsert?: DeviceUpsertWithoutActuatorsInput
    connect?: DeviceWhereUniqueInput
    update?: XOR<XOR<DeviceUpdateToOneWithWhereWithoutActuatorsInput, DeviceUpdateWithoutActuatorsInput>, DeviceUncheckedUpdateWithoutActuatorsInput>
  }

  export type ActuatorCommandUpdateManyWithoutActuatorNestedInput = {
    create?: XOR<ActuatorCommandCreateWithoutActuatorInput, ActuatorCommandUncheckedCreateWithoutActuatorInput> | ActuatorCommandCreateWithoutActuatorInput[] | ActuatorCommandUncheckedCreateWithoutActuatorInput[]
    connectOrCreate?: ActuatorCommandCreateOrConnectWithoutActuatorInput | ActuatorCommandCreateOrConnectWithoutActuatorInput[]
    upsert?: ActuatorCommandUpsertWithWhereUniqueWithoutActuatorInput | ActuatorCommandUpsertWithWhereUniqueWithoutActuatorInput[]
    createMany?: ActuatorCommandCreateManyActuatorInputEnvelope
    set?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    disconnect?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    delete?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    connect?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    update?: ActuatorCommandUpdateWithWhereUniqueWithoutActuatorInput | ActuatorCommandUpdateWithWhereUniqueWithoutActuatorInput[]
    updateMany?: ActuatorCommandUpdateManyWithWhereWithoutActuatorInput | ActuatorCommandUpdateManyWithWhereWithoutActuatorInput[]
    deleteMany?: ActuatorCommandScalarWhereInput | ActuatorCommandScalarWhereInput[]
  }

  export type ActuatorCommandUncheckedUpdateManyWithoutActuatorNestedInput = {
    create?: XOR<ActuatorCommandCreateWithoutActuatorInput, ActuatorCommandUncheckedCreateWithoutActuatorInput> | ActuatorCommandCreateWithoutActuatorInput[] | ActuatorCommandUncheckedCreateWithoutActuatorInput[]
    connectOrCreate?: ActuatorCommandCreateOrConnectWithoutActuatorInput | ActuatorCommandCreateOrConnectWithoutActuatorInput[]
    upsert?: ActuatorCommandUpsertWithWhereUniqueWithoutActuatorInput | ActuatorCommandUpsertWithWhereUniqueWithoutActuatorInput[]
    createMany?: ActuatorCommandCreateManyActuatorInputEnvelope
    set?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    disconnect?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    delete?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    connect?: ActuatorCommandWhereUniqueInput | ActuatorCommandWhereUniqueInput[]
    update?: ActuatorCommandUpdateWithWhereUniqueWithoutActuatorInput | ActuatorCommandUpdateWithWhereUniqueWithoutActuatorInput[]
    updateMany?: ActuatorCommandUpdateManyWithWhereWithoutActuatorInput | ActuatorCommandUpdateManyWithWhereWithoutActuatorInput[]
    deleteMany?: ActuatorCommandScalarWhereInput | ActuatorCommandScalarWhereInput[]
  }

  export type ActuatorCreateNestedOneWithoutCommandsInput = {
    create?: XOR<ActuatorCreateWithoutCommandsInput, ActuatorUncheckedCreateWithoutCommandsInput>
    connectOrCreate?: ActuatorCreateOrConnectWithoutCommandsInput
    connect?: ActuatorWhereUniqueInput
  }

  export type EnumCommandStatusFieldUpdateOperationsInput = {
    set?: $Enums.CommandStatus
  }

  export type ActuatorUpdateOneRequiredWithoutCommandsNestedInput = {
    create?: XOR<ActuatorCreateWithoutCommandsInput, ActuatorUncheckedCreateWithoutCommandsInput>
    connectOrCreate?: ActuatorCreateOrConnectWithoutCommandsInput
    upsert?: ActuatorUpsertWithoutCommandsInput
    connect?: ActuatorWhereUniqueInput
    update?: XOR<XOR<ActuatorUpdateToOneWithWhereWithoutCommandsInput, ActuatorUpdateWithoutCommandsInput>, ActuatorUncheckedUpdateWithoutCommandsInput>
  }

  export type DeviceCreateNestedOneWithoutAlertsInput = {
    create?: XOR<DeviceCreateWithoutAlertsInput, DeviceUncheckedCreateWithoutAlertsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutAlertsInput
    connect?: DeviceWhereUniqueInput
  }

  export type EnumAlertSeverityFieldUpdateOperationsInput = {
    set?: $Enums.AlertSeverity
  }

  export type BoolFieldUpdateOperationsInput = {
    set?: boolean
  }

  export type DeviceUpdateOneRequiredWithoutAlertsNestedInput = {
    create?: XOR<DeviceCreateWithoutAlertsInput, DeviceUncheckedCreateWithoutAlertsInput>
    connectOrCreate?: DeviceCreateOrConnectWithoutAlertsInput
    upsert?: DeviceUpsertWithoutAlertsInput
    connect?: DeviceWhereUniqueInput
    update?: XOR<XOR<DeviceUpdateToOneWithWhereWithoutAlertsInput, DeviceUpdateWithoutAlertsInput>, DeviceUncheckedUpdateWithoutAlertsInput>
  }

  export type NestedStringFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedStringFilter<$PrismaModel> | string
  }

  export type NestedEnumDeviceTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceType | EnumDeviceTypeFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceTypeFilter<$PrismaModel> | $Enums.DeviceType
  }

  export type NestedEnumDeviceStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceStatus | EnumDeviceStatusFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceStatusFilter<$PrismaModel> | $Enums.DeviceStatus
  }

  export type NestedDateTimeNullableFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel> | null
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeNullableFilter<$PrismaModel> | Date | string | null
  }

  export type NestedStringNullableFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedStringNullableFilter<$PrismaModel> | string | null
  }

  export type NestedDateTimeFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeFilter<$PrismaModel> | Date | string
  }

  export type NestedStringWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedStringWithAggregatesFilter<$PrismaModel> | string
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedStringFilter<$PrismaModel>
    _max?: NestedStringFilter<$PrismaModel>
  }

  export type NestedIntFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel>
    in?: number[] | ListIntFieldRefInput<$PrismaModel>
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel>
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntFilter<$PrismaModel> | number
  }

  export type NestedEnumDeviceTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceType | EnumDeviceTypeFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceType[] | ListEnumDeviceTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceTypeWithAggregatesFilter<$PrismaModel> | $Enums.DeviceType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumDeviceTypeFilter<$PrismaModel>
    _max?: NestedEnumDeviceTypeFilter<$PrismaModel>
  }

  export type NestedEnumDeviceStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.DeviceStatus | EnumDeviceStatusFieldRefInput<$PrismaModel>
    in?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.DeviceStatus[] | ListEnumDeviceStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumDeviceStatusWithAggregatesFilter<$PrismaModel> | $Enums.DeviceStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumDeviceStatusFilter<$PrismaModel>
    _max?: NestedEnumDeviceStatusFilter<$PrismaModel>
  }

  export type NestedDateTimeNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel> | null
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel> | null
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeNullableWithAggregatesFilter<$PrismaModel> | Date | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedDateTimeNullableFilter<$PrismaModel>
    _max?: NestedDateTimeNullableFilter<$PrismaModel>
  }

  export type NestedIntNullableFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel> | null
    in?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntNullableFilter<$PrismaModel> | number | null
  }
  export type NestedJsonNullableFilter<$PrismaModel = never> = 
    | PatchUndefined<
        Either<Required<NestedJsonNullableFilterBase<$PrismaModel>>, Exclude<keyof Required<NestedJsonNullableFilterBase<$PrismaModel>>, 'path'>>,
        Required<NestedJsonNullableFilterBase<$PrismaModel>>
      >
    | OptionalFlat<Omit<Required<NestedJsonNullableFilterBase<$PrismaModel>>, 'path'>>

  export type NestedJsonNullableFilterBase<$PrismaModel = never> = {
    equals?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | JsonNullValueFilter
    path?: string[]
    string_contains?: string | StringFieldRefInput<$PrismaModel>
    string_starts_with?: string | StringFieldRefInput<$PrismaModel>
    string_ends_with?: string | StringFieldRefInput<$PrismaModel>
    array_contains?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    array_starts_with?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    array_ends_with?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | null
    lt?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    lte?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    gt?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    gte?: InputJsonValue | JsonFieldRefInput<$PrismaModel>
    not?: InputJsonValue | JsonFieldRefInput<$PrismaModel> | JsonNullValueFilter
  }

  export type NestedStringNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    contains?: string | StringFieldRefInput<$PrismaModel>
    startsWith?: string | StringFieldRefInput<$PrismaModel>
    endsWith?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedStringNullableWithAggregatesFilter<$PrismaModel> | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedStringNullableFilter<$PrismaModel>
    _max?: NestedStringNullableFilter<$PrismaModel>
  }

  export type NestedDateTimeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    in?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    notIn?: Date[] | string[] | ListDateTimeFieldRefInput<$PrismaModel>
    lt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    lte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gt?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    gte?: Date | string | DateTimeFieldRefInput<$PrismaModel>
    not?: NestedDateTimeWithAggregatesFilter<$PrismaModel> | Date | string
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedDateTimeFilter<$PrismaModel>
    _max?: NestedDateTimeFilter<$PrismaModel>
  }

  export type NestedEnumSensorTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.SensorType | EnumSensorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumSensorTypeFilter<$PrismaModel> | $Enums.SensorType
  }

  export type NestedFloatNullableFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel> | null
    in?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatNullableFilter<$PrismaModel> | number | null
  }

  export type NestedEnumSensorTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.SensorType | EnumSensorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.SensorType[] | ListEnumSensorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumSensorTypeWithAggregatesFilter<$PrismaModel> | $Enums.SensorType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumSensorTypeFilter<$PrismaModel>
    _max?: NestedEnumSensorTypeFilter<$PrismaModel>
  }

  export type NestedFloatNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel> | null
    in?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel> | null
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatNullableWithAggregatesFilter<$PrismaModel> | number | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _avg?: NestedFloatNullableFilter<$PrismaModel>
    _sum?: NestedFloatNullableFilter<$PrismaModel>
    _min?: NestedFloatNullableFilter<$PrismaModel>
    _max?: NestedFloatNullableFilter<$PrismaModel>
  }

  export type NestedFloatFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel>
    in?: number[] | ListFloatFieldRefInput<$PrismaModel>
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel>
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatFilter<$PrismaModel> | number
  }

  export type NestedFloatWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | FloatFieldRefInput<$PrismaModel>
    in?: number[] | ListFloatFieldRefInput<$PrismaModel>
    notIn?: number[] | ListFloatFieldRefInput<$PrismaModel>
    lt?: number | FloatFieldRefInput<$PrismaModel>
    lte?: number | FloatFieldRefInput<$PrismaModel>
    gt?: number | FloatFieldRefInput<$PrismaModel>
    gte?: number | FloatFieldRefInput<$PrismaModel>
    not?: NestedFloatWithAggregatesFilter<$PrismaModel> | number
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedFloatFilter<$PrismaModel>
    _sum?: NestedFloatFilter<$PrismaModel>
    _min?: NestedFloatFilter<$PrismaModel>
    _max?: NestedFloatFilter<$PrismaModel>
  }

  export type NestedEnumActuatorTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.ActuatorType | EnumActuatorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumActuatorTypeFilter<$PrismaModel> | $Enums.ActuatorType
  }

  export type NestedEnumActuatorTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.ActuatorType | EnumActuatorTypeFieldRefInput<$PrismaModel>
    in?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.ActuatorType[] | ListEnumActuatorTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumActuatorTypeWithAggregatesFilter<$PrismaModel> | $Enums.ActuatorType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumActuatorTypeFilter<$PrismaModel>
    _max?: NestedEnumActuatorTypeFilter<$PrismaModel>
  }

  export type NestedEnumCommandStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.CommandStatus | EnumCommandStatusFieldRefInput<$PrismaModel>
    in?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumCommandStatusFilter<$PrismaModel> | $Enums.CommandStatus
  }

  export type NestedEnumCommandStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.CommandStatus | EnumCommandStatusFieldRefInput<$PrismaModel>
    in?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.CommandStatus[] | ListEnumCommandStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumCommandStatusWithAggregatesFilter<$PrismaModel> | $Enums.CommandStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumCommandStatusFilter<$PrismaModel>
    _max?: NestedEnumCommandStatusFilter<$PrismaModel>
  }

  export type NestedEnumAlertSeverityFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertSeverity | EnumAlertSeverityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertSeverityFilter<$PrismaModel> | $Enums.AlertSeverity
  }

  export type NestedBoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
  }

  export type NestedEnumAlertSeverityWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertSeverity | EnumAlertSeverityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertSeverityWithAggregatesFilter<$PrismaModel> | $Enums.AlertSeverity
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertSeverityFilter<$PrismaModel>
    _max?: NestedEnumAlertSeverityFilter<$PrismaModel>
  }

  export type NestedBoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
  }

  export type SensorCreateWithoutDeviceInput = {
    id?: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    readings?: SensorReadingCreateNestedManyWithoutSensorInput
  }

  export type SensorUncheckedCreateWithoutDeviceInput = {
    id?: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    readings?: SensorReadingUncheckedCreateNestedManyWithoutSensorInput
  }

  export type SensorCreateOrConnectWithoutDeviceInput = {
    where: SensorWhereUniqueInput
    create: XOR<SensorCreateWithoutDeviceInput, SensorUncheckedCreateWithoutDeviceInput>
  }

  export type SensorCreateManyDeviceInputEnvelope = {
    data: SensorCreateManyDeviceInput | SensorCreateManyDeviceInput[]
    skipDuplicates?: boolean
  }

  export type SensorReadingCreateWithoutDeviceInput = {
    id?: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    sensor: SensorCreateNestedOneWithoutReadingsInput
  }

  export type SensorReadingUncheckedCreateWithoutDeviceInput = {
    id?: string
    sensorId: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingCreateOrConnectWithoutDeviceInput = {
    where: SensorReadingWhereUniqueInput
    create: XOR<SensorReadingCreateWithoutDeviceInput, SensorReadingUncheckedCreateWithoutDeviceInput>
  }

  export type SensorReadingCreateManyDeviceInputEnvelope = {
    data: SensorReadingCreateManyDeviceInput | SensorReadingCreateManyDeviceInput[]
    skipDuplicates?: boolean
  }

  export type ActuatorCreateWithoutDeviceInput = {
    id?: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    commands?: ActuatorCommandCreateNestedManyWithoutActuatorInput
  }

  export type ActuatorUncheckedCreateWithoutDeviceInput = {
    id?: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    commands?: ActuatorCommandUncheckedCreateNestedManyWithoutActuatorInput
  }

  export type ActuatorCreateOrConnectWithoutDeviceInput = {
    where: ActuatorWhereUniqueInput
    create: XOR<ActuatorCreateWithoutDeviceInput, ActuatorUncheckedCreateWithoutDeviceInput>
  }

  export type ActuatorCreateManyDeviceInputEnvelope = {
    data: ActuatorCreateManyDeviceInput | ActuatorCreateManyDeviceInput[]
    skipDuplicates?: boolean
  }

  export type DeviceAlertCreateWithoutDeviceInput = {
    id?: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged?: boolean
    acknowledgedBy?: string | null
    acknowledgedAt?: Date | string | null
    resolvedAt?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type DeviceAlertUncheckedCreateWithoutDeviceInput = {
    id?: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged?: boolean
    acknowledgedBy?: string | null
    acknowledgedAt?: Date | string | null
    resolvedAt?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type DeviceAlertCreateOrConnectWithoutDeviceInput = {
    where: DeviceAlertWhereUniqueInput
    create: XOR<DeviceAlertCreateWithoutDeviceInput, DeviceAlertUncheckedCreateWithoutDeviceInput>
  }

  export type DeviceAlertCreateManyDeviceInputEnvelope = {
    data: DeviceAlertCreateManyDeviceInput | DeviceAlertCreateManyDeviceInput[]
    skipDuplicates?: boolean
  }

  export type SensorUpsertWithWhereUniqueWithoutDeviceInput = {
    where: SensorWhereUniqueInput
    update: XOR<SensorUpdateWithoutDeviceInput, SensorUncheckedUpdateWithoutDeviceInput>
    create: XOR<SensorCreateWithoutDeviceInput, SensorUncheckedCreateWithoutDeviceInput>
  }

  export type SensorUpdateWithWhereUniqueWithoutDeviceInput = {
    where: SensorWhereUniqueInput
    data: XOR<SensorUpdateWithoutDeviceInput, SensorUncheckedUpdateWithoutDeviceInput>
  }

  export type SensorUpdateManyWithWhereWithoutDeviceInput = {
    where: SensorScalarWhereInput
    data: XOR<SensorUpdateManyMutationInput, SensorUncheckedUpdateManyWithoutDeviceInput>
  }

  export type SensorScalarWhereInput = {
    AND?: SensorScalarWhereInput | SensorScalarWhereInput[]
    OR?: SensorScalarWhereInput[]
    NOT?: SensorScalarWhereInput | SensorScalarWhereInput[]
    id?: StringFilter<"Sensor"> | string
    deviceId?: StringFilter<"Sensor"> | string
    sensorType?: EnumSensorTypeFilter<"Sensor"> | $Enums.SensorType
    unit?: StringFilter<"Sensor"> | string
    calibrationData?: JsonNullableFilter<"Sensor">
    lastReading?: FloatNullableFilter<"Sensor"> | number | null
    lastReadingAt?: DateTimeNullableFilter<"Sensor"> | Date | string | null
    createdAt?: DateTimeFilter<"Sensor"> | Date | string
    updatedAt?: DateTimeFilter<"Sensor"> | Date | string
  }

  export type SensorReadingUpsertWithWhereUniqueWithoutDeviceInput = {
    where: SensorReadingWhereUniqueInput
    update: XOR<SensorReadingUpdateWithoutDeviceInput, SensorReadingUncheckedUpdateWithoutDeviceInput>
    create: XOR<SensorReadingCreateWithoutDeviceInput, SensorReadingUncheckedCreateWithoutDeviceInput>
  }

  export type SensorReadingUpdateWithWhereUniqueWithoutDeviceInput = {
    where: SensorReadingWhereUniqueInput
    data: XOR<SensorReadingUpdateWithoutDeviceInput, SensorReadingUncheckedUpdateWithoutDeviceInput>
  }

  export type SensorReadingUpdateManyWithWhereWithoutDeviceInput = {
    where: SensorReadingScalarWhereInput
    data: XOR<SensorReadingUpdateManyMutationInput, SensorReadingUncheckedUpdateManyWithoutDeviceInput>
  }

  export type SensorReadingScalarWhereInput = {
    AND?: SensorReadingScalarWhereInput | SensorReadingScalarWhereInput[]
    OR?: SensorReadingScalarWhereInput[]
    NOT?: SensorReadingScalarWhereInput | SensorReadingScalarWhereInput[]
    id?: StringFilter<"SensorReading"> | string
    sensorId?: StringFilter<"SensorReading"> | string
    deviceId?: StringFilter<"SensorReading"> | string
    value?: FloatFilter<"SensorReading"> | number
    unit?: StringFilter<"SensorReading"> | string
    timestamp?: DateTimeFilter<"SensorReading"> | Date | string
    quality?: FloatNullableFilter<"SensorReading"> | number | null
    metadata?: JsonNullableFilter<"SensorReading">
  }

  export type ActuatorUpsertWithWhereUniqueWithoutDeviceInput = {
    where: ActuatorWhereUniqueInput
    update: XOR<ActuatorUpdateWithoutDeviceInput, ActuatorUncheckedUpdateWithoutDeviceInput>
    create: XOR<ActuatorCreateWithoutDeviceInput, ActuatorUncheckedCreateWithoutDeviceInput>
  }

  export type ActuatorUpdateWithWhereUniqueWithoutDeviceInput = {
    where: ActuatorWhereUniqueInput
    data: XOR<ActuatorUpdateWithoutDeviceInput, ActuatorUncheckedUpdateWithoutDeviceInput>
  }

  export type ActuatorUpdateManyWithWhereWithoutDeviceInput = {
    where: ActuatorScalarWhereInput
    data: XOR<ActuatorUpdateManyMutationInput, ActuatorUncheckedUpdateManyWithoutDeviceInput>
  }

  export type ActuatorScalarWhereInput = {
    AND?: ActuatorScalarWhereInput | ActuatorScalarWhereInput[]
    OR?: ActuatorScalarWhereInput[]
    NOT?: ActuatorScalarWhereInput | ActuatorScalarWhereInput[]
    id?: StringFilter<"Actuator"> | string
    deviceId?: StringFilter<"Actuator"> | string
    actuatorType?: EnumActuatorTypeFilter<"Actuator"> | $Enums.ActuatorType
    name?: StringNullableFilter<"Actuator"> | string | null
    currentState?: JsonNullableFilter<"Actuator">
    lastCommand?: StringNullableFilter<"Actuator"> | string | null
    lastCommandAt?: DateTimeNullableFilter<"Actuator"> | Date | string | null
    createdAt?: DateTimeFilter<"Actuator"> | Date | string
    updatedAt?: DateTimeFilter<"Actuator"> | Date | string
  }

  export type DeviceAlertUpsertWithWhereUniqueWithoutDeviceInput = {
    where: DeviceAlertWhereUniqueInput
    update: XOR<DeviceAlertUpdateWithoutDeviceInput, DeviceAlertUncheckedUpdateWithoutDeviceInput>
    create: XOR<DeviceAlertCreateWithoutDeviceInput, DeviceAlertUncheckedCreateWithoutDeviceInput>
  }

  export type DeviceAlertUpdateWithWhereUniqueWithoutDeviceInput = {
    where: DeviceAlertWhereUniqueInput
    data: XOR<DeviceAlertUpdateWithoutDeviceInput, DeviceAlertUncheckedUpdateWithoutDeviceInput>
  }

  export type DeviceAlertUpdateManyWithWhereWithoutDeviceInput = {
    where: DeviceAlertScalarWhereInput
    data: XOR<DeviceAlertUpdateManyMutationInput, DeviceAlertUncheckedUpdateManyWithoutDeviceInput>
  }

  export type DeviceAlertScalarWhereInput = {
    AND?: DeviceAlertScalarWhereInput | DeviceAlertScalarWhereInput[]
    OR?: DeviceAlertScalarWhereInput[]
    NOT?: DeviceAlertScalarWhereInput | DeviceAlertScalarWhereInput[]
    id?: StringFilter<"DeviceAlert"> | string
    deviceId?: StringFilter<"DeviceAlert"> | string
    tenantId?: StringFilter<"DeviceAlert"> | string
    alertType?: StringFilter<"DeviceAlert"> | string
    severity?: EnumAlertSeverityFilter<"DeviceAlert"> | $Enums.AlertSeverity
    message?: StringFilter<"DeviceAlert"> | string
    acknowledged?: BoolFilter<"DeviceAlert"> | boolean
    acknowledgedBy?: StringNullableFilter<"DeviceAlert"> | string | null
    acknowledgedAt?: DateTimeNullableFilter<"DeviceAlert"> | Date | string | null
    resolvedAt?: DateTimeNullableFilter<"DeviceAlert"> | Date | string | null
    metadata?: JsonNullableFilter<"DeviceAlert">
    createdAt?: DateTimeFilter<"DeviceAlert"> | Date | string
    updatedAt?: DateTimeFilter<"DeviceAlert"> | Date | string
  }

  export type DeviceCreateWithoutSensorsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensorReadings?: SensorReadingCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertCreateNestedManyWithoutDeviceInput
  }

  export type DeviceUncheckedCreateWithoutSensorsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensorReadings?: SensorReadingUncheckedCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorUncheckedCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertUncheckedCreateNestedManyWithoutDeviceInput
  }

  export type DeviceCreateOrConnectWithoutSensorsInput = {
    where: DeviceWhereUniqueInput
    create: XOR<DeviceCreateWithoutSensorsInput, DeviceUncheckedCreateWithoutSensorsInput>
  }

  export type SensorReadingCreateWithoutSensorInput = {
    id?: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    device: DeviceCreateNestedOneWithoutSensorReadingsInput
  }

  export type SensorReadingUncheckedCreateWithoutSensorInput = {
    id?: string
    deviceId: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingCreateOrConnectWithoutSensorInput = {
    where: SensorReadingWhereUniqueInput
    create: XOR<SensorReadingCreateWithoutSensorInput, SensorReadingUncheckedCreateWithoutSensorInput>
  }

  export type SensorReadingCreateManySensorInputEnvelope = {
    data: SensorReadingCreateManySensorInput | SensorReadingCreateManySensorInput[]
    skipDuplicates?: boolean
  }

  export type DeviceUpsertWithoutSensorsInput = {
    update: XOR<DeviceUpdateWithoutSensorsInput, DeviceUncheckedUpdateWithoutSensorsInput>
    create: XOR<DeviceCreateWithoutSensorsInput, DeviceUncheckedCreateWithoutSensorsInput>
    where?: DeviceWhereInput
  }

  export type DeviceUpdateToOneWithWhereWithoutSensorsInput = {
    where?: DeviceWhereInput
    data: XOR<DeviceUpdateWithoutSensorsInput, DeviceUncheckedUpdateWithoutSensorsInput>
  }

  export type DeviceUpdateWithoutSensorsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensorReadings?: SensorReadingUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceUncheckedUpdateWithoutSensorsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensorReadings?: SensorReadingUncheckedUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUncheckedUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUncheckedUpdateManyWithoutDeviceNestedInput
  }

  export type SensorReadingUpsertWithWhereUniqueWithoutSensorInput = {
    where: SensorReadingWhereUniqueInput
    update: XOR<SensorReadingUpdateWithoutSensorInput, SensorReadingUncheckedUpdateWithoutSensorInput>
    create: XOR<SensorReadingCreateWithoutSensorInput, SensorReadingUncheckedCreateWithoutSensorInput>
  }

  export type SensorReadingUpdateWithWhereUniqueWithoutSensorInput = {
    where: SensorReadingWhereUniqueInput
    data: XOR<SensorReadingUpdateWithoutSensorInput, SensorReadingUncheckedUpdateWithoutSensorInput>
  }

  export type SensorReadingUpdateManyWithWhereWithoutSensorInput = {
    where: SensorReadingScalarWhereInput
    data: XOR<SensorReadingUpdateManyMutationInput, SensorReadingUncheckedUpdateManyWithoutSensorInput>
  }

  export type SensorCreateWithoutReadingsInput = {
    id?: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    device: DeviceCreateNestedOneWithoutSensorsInput
  }

  export type SensorUncheckedCreateWithoutReadingsInput = {
    id?: string
    deviceId: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SensorCreateOrConnectWithoutReadingsInput = {
    where: SensorWhereUniqueInput
    create: XOR<SensorCreateWithoutReadingsInput, SensorUncheckedCreateWithoutReadingsInput>
  }

  export type DeviceCreateWithoutSensorReadingsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertCreateNestedManyWithoutDeviceInput
  }

  export type DeviceUncheckedCreateWithoutSensorReadingsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorUncheckedCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorUncheckedCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertUncheckedCreateNestedManyWithoutDeviceInput
  }

  export type DeviceCreateOrConnectWithoutSensorReadingsInput = {
    where: DeviceWhereUniqueInput
    create: XOR<DeviceCreateWithoutSensorReadingsInput, DeviceUncheckedCreateWithoutSensorReadingsInput>
  }

  export type SensorUpsertWithoutReadingsInput = {
    update: XOR<SensorUpdateWithoutReadingsInput, SensorUncheckedUpdateWithoutReadingsInput>
    create: XOR<SensorCreateWithoutReadingsInput, SensorUncheckedCreateWithoutReadingsInput>
    where?: SensorWhereInput
  }

  export type SensorUpdateToOneWithWhereWithoutReadingsInput = {
    where?: SensorWhereInput
    data: XOR<SensorUpdateWithoutReadingsInput, SensorUncheckedUpdateWithoutReadingsInput>
  }

  export type SensorUpdateWithoutReadingsInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    device?: DeviceUpdateOneRequiredWithoutSensorsNestedInput
  }

  export type SensorUncheckedUpdateWithoutReadingsInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceUpsertWithoutSensorReadingsInput = {
    update: XOR<DeviceUpdateWithoutSensorReadingsInput, DeviceUncheckedUpdateWithoutSensorReadingsInput>
    create: XOR<DeviceCreateWithoutSensorReadingsInput, DeviceUncheckedCreateWithoutSensorReadingsInput>
    where?: DeviceWhereInput
  }

  export type DeviceUpdateToOneWithWhereWithoutSensorReadingsInput = {
    where?: DeviceWhereInput
    data: XOR<DeviceUpdateWithoutSensorReadingsInput, DeviceUncheckedUpdateWithoutSensorReadingsInput>
  }

  export type DeviceUpdateWithoutSensorReadingsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceUncheckedUpdateWithoutSensorReadingsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUncheckedUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUncheckedUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUncheckedUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceCreateWithoutActuatorsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorCreateNestedManyWithoutDeviceInput
    sensorReadings?: SensorReadingCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertCreateNestedManyWithoutDeviceInput
  }

  export type DeviceUncheckedCreateWithoutActuatorsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorUncheckedCreateNestedManyWithoutDeviceInput
    sensorReadings?: SensorReadingUncheckedCreateNestedManyWithoutDeviceInput
    alerts?: DeviceAlertUncheckedCreateNestedManyWithoutDeviceInput
  }

  export type DeviceCreateOrConnectWithoutActuatorsInput = {
    where: DeviceWhereUniqueInput
    create: XOR<DeviceCreateWithoutActuatorsInput, DeviceUncheckedCreateWithoutActuatorsInput>
  }

  export type ActuatorCommandCreateWithoutActuatorInput = {
    id?: string
    command: string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: $Enums.CommandStatus
    requestedAt?: Date | string
    executedAt?: Date | string | null
    completedAt?: Date | string | null
    errorMessage?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorCommandUncheckedCreateWithoutActuatorInput = {
    id?: string
    command: string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: $Enums.CommandStatus
    requestedAt?: Date | string
    executedAt?: Date | string | null
    completedAt?: Date | string | null
    errorMessage?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorCommandCreateOrConnectWithoutActuatorInput = {
    where: ActuatorCommandWhereUniqueInput
    create: XOR<ActuatorCommandCreateWithoutActuatorInput, ActuatorCommandUncheckedCreateWithoutActuatorInput>
  }

  export type ActuatorCommandCreateManyActuatorInputEnvelope = {
    data: ActuatorCommandCreateManyActuatorInput | ActuatorCommandCreateManyActuatorInput[]
    skipDuplicates?: boolean
  }

  export type DeviceUpsertWithoutActuatorsInput = {
    update: XOR<DeviceUpdateWithoutActuatorsInput, DeviceUncheckedUpdateWithoutActuatorsInput>
    create: XOR<DeviceCreateWithoutActuatorsInput, DeviceUncheckedCreateWithoutActuatorsInput>
    where?: DeviceWhereInput
  }

  export type DeviceUpdateToOneWithWhereWithoutActuatorsInput = {
    where?: DeviceWhereInput
    data: XOR<DeviceUpdateWithoutActuatorsInput, DeviceUncheckedUpdateWithoutActuatorsInput>
  }

  export type DeviceUpdateWithoutActuatorsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUpdateManyWithoutDeviceNestedInput
    sensorReadings?: SensorReadingUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceUncheckedUpdateWithoutActuatorsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUncheckedUpdateManyWithoutDeviceNestedInput
    sensorReadings?: SensorReadingUncheckedUpdateManyWithoutDeviceNestedInput
    alerts?: DeviceAlertUncheckedUpdateManyWithoutDeviceNestedInput
  }

  export type ActuatorCommandUpsertWithWhereUniqueWithoutActuatorInput = {
    where: ActuatorCommandWhereUniqueInput
    update: XOR<ActuatorCommandUpdateWithoutActuatorInput, ActuatorCommandUncheckedUpdateWithoutActuatorInput>
    create: XOR<ActuatorCommandCreateWithoutActuatorInput, ActuatorCommandUncheckedCreateWithoutActuatorInput>
  }

  export type ActuatorCommandUpdateWithWhereUniqueWithoutActuatorInput = {
    where: ActuatorCommandWhereUniqueInput
    data: XOR<ActuatorCommandUpdateWithoutActuatorInput, ActuatorCommandUncheckedUpdateWithoutActuatorInput>
  }

  export type ActuatorCommandUpdateManyWithWhereWithoutActuatorInput = {
    where: ActuatorCommandScalarWhereInput
    data: XOR<ActuatorCommandUpdateManyMutationInput, ActuatorCommandUncheckedUpdateManyWithoutActuatorInput>
  }

  export type ActuatorCommandScalarWhereInput = {
    AND?: ActuatorCommandScalarWhereInput | ActuatorCommandScalarWhereInput[]
    OR?: ActuatorCommandScalarWhereInput[]
    NOT?: ActuatorCommandScalarWhereInput | ActuatorCommandScalarWhereInput[]
    id?: StringFilter<"ActuatorCommand"> | string
    actuatorId?: StringFilter<"ActuatorCommand"> | string
    command?: StringFilter<"ActuatorCommand"> | string
    parameters?: JsonNullableFilter<"ActuatorCommand">
    status?: EnumCommandStatusFilter<"ActuatorCommand"> | $Enums.CommandStatus
    requestedAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    executedAt?: DateTimeNullableFilter<"ActuatorCommand"> | Date | string | null
    completedAt?: DateTimeNullableFilter<"ActuatorCommand"> | Date | string | null
    errorMessage?: StringNullableFilter<"ActuatorCommand"> | string | null
    createdAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
    updatedAt?: DateTimeFilter<"ActuatorCommand"> | Date | string
  }

  export type ActuatorCreateWithoutCommandsInput = {
    id?: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    device: DeviceCreateNestedOneWithoutActuatorsInput
  }

  export type ActuatorUncheckedCreateWithoutCommandsInput = {
    id?: string
    deviceId: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorCreateOrConnectWithoutCommandsInput = {
    where: ActuatorWhereUniqueInput
    create: XOR<ActuatorCreateWithoutCommandsInput, ActuatorUncheckedCreateWithoutCommandsInput>
  }

  export type ActuatorUpsertWithoutCommandsInput = {
    update: XOR<ActuatorUpdateWithoutCommandsInput, ActuatorUncheckedUpdateWithoutCommandsInput>
    create: XOR<ActuatorCreateWithoutCommandsInput, ActuatorUncheckedCreateWithoutCommandsInput>
    where?: ActuatorWhereInput
  }

  export type ActuatorUpdateToOneWithWhereWithoutCommandsInput = {
    where?: ActuatorWhereInput
    data: XOR<ActuatorUpdateWithoutCommandsInput, ActuatorUncheckedUpdateWithoutCommandsInput>
  }

  export type ActuatorUpdateWithoutCommandsInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    device?: DeviceUpdateOneRequiredWithoutActuatorsNestedInput
  }

  export type ActuatorUncheckedUpdateWithoutCommandsInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceCreateWithoutAlertsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorCreateNestedManyWithoutDeviceInput
    sensorReadings?: SensorReadingCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorCreateNestedManyWithoutDeviceInput
  }

  export type DeviceUncheckedCreateWithoutAlertsInput = {
    id?: string
    tenantId: string
    deviceId: string
    name: string
    type: $Enums.DeviceType
    status?: $Enums.DeviceStatus
    lastSeen?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    sensors?: SensorUncheckedCreateNestedManyWithoutDeviceInput
    sensorReadings?: SensorReadingUncheckedCreateNestedManyWithoutDeviceInput
    actuators?: ActuatorUncheckedCreateNestedManyWithoutDeviceInput
  }

  export type DeviceCreateOrConnectWithoutAlertsInput = {
    where: DeviceWhereUniqueInput
    create: XOR<DeviceCreateWithoutAlertsInput, DeviceUncheckedCreateWithoutAlertsInput>
  }

  export type DeviceUpsertWithoutAlertsInput = {
    update: XOR<DeviceUpdateWithoutAlertsInput, DeviceUncheckedUpdateWithoutAlertsInput>
    create: XOR<DeviceCreateWithoutAlertsInput, DeviceUncheckedCreateWithoutAlertsInput>
    where?: DeviceWhereInput
  }

  export type DeviceUpdateToOneWithWhereWithoutAlertsInput = {
    where?: DeviceWhereInput
    data: XOR<DeviceUpdateWithoutAlertsInput, DeviceUncheckedUpdateWithoutAlertsInput>
  }

  export type DeviceUpdateWithoutAlertsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUpdateManyWithoutDeviceNestedInput
    sensorReadings?: SensorReadingUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUpdateManyWithoutDeviceNestedInput
  }

  export type DeviceUncheckedUpdateWithoutAlertsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    type?: EnumDeviceTypeFieldUpdateOperationsInput | $Enums.DeviceType
    status?: EnumDeviceStatusFieldUpdateOperationsInput | $Enums.DeviceStatus
    lastSeen?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    sensors?: SensorUncheckedUpdateManyWithoutDeviceNestedInput
    sensorReadings?: SensorReadingUncheckedUpdateManyWithoutDeviceNestedInput
    actuators?: ActuatorUncheckedUpdateManyWithoutDeviceNestedInput
  }

  export type SensorCreateManyDeviceInput = {
    id?: string
    sensorType: $Enums.SensorType
    unit: string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: number | null
    lastReadingAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SensorReadingCreateManyDeviceInput = {
    id?: string
    sensorId: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type ActuatorCreateManyDeviceInput = {
    id?: string
    actuatorType: $Enums.ActuatorType
    name?: string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: string | null
    lastCommandAt?: Date | string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type DeviceAlertCreateManyDeviceInput = {
    id?: string
    tenantId: string
    alertType: string
    severity: $Enums.AlertSeverity
    message: string
    acknowledged?: boolean
    acknowledgedBy?: string | null
    acknowledgedAt?: Date | string | null
    resolvedAt?: Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SensorUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    readings?: SensorReadingUpdateManyWithoutSensorNestedInput
  }

  export type SensorUncheckedUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    readings?: SensorReadingUncheckedUpdateManyWithoutSensorNestedInput
  }

  export type SensorUncheckedUpdateManyWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorType?: EnumSensorTypeFieldUpdateOperationsInput | $Enums.SensorType
    unit?: StringFieldUpdateOperationsInput | string
    calibrationData?: NullableJsonNullValueInput | InputJsonValue
    lastReading?: NullableFloatFieldUpdateOperationsInput | number | null
    lastReadingAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SensorReadingUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    sensor?: SensorUpdateOneRequiredWithoutReadingsNestedInput
  }

  export type SensorReadingUncheckedUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorId?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingUncheckedUpdateManyWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    sensorId?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type ActuatorUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    commands?: ActuatorCommandUpdateManyWithoutActuatorNestedInput
  }

  export type ActuatorUncheckedUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    commands?: ActuatorCommandUncheckedUpdateManyWithoutActuatorNestedInput
  }

  export type ActuatorUncheckedUpdateManyWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    actuatorType?: EnumActuatorTypeFieldUpdateOperationsInput | $Enums.ActuatorType
    name?: NullableStringFieldUpdateOperationsInput | string | null
    currentState?: NullableJsonNullValueInput | InputJsonValue
    lastCommand?: NullableStringFieldUpdateOperationsInput | string | null
    lastCommandAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceAlertUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceAlertUncheckedUpdateWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type DeviceAlertUncheckedUpdateManyWithoutDeviceInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    alertType?: StringFieldUpdateOperationsInput | string
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    message?: StringFieldUpdateOperationsInput | string
    acknowledged?: BoolFieldUpdateOperationsInput | boolean
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SensorReadingCreateManySensorInput = {
    id?: string
    deviceId: string
    value: number
    unit: string
    timestamp?: Date | string
    quality?: number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingUpdateWithoutSensorInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    device?: DeviceUpdateOneRequiredWithoutSensorReadingsNestedInput
  }

  export type SensorReadingUncheckedUpdateWithoutSensorInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type SensorReadingUncheckedUpdateManyWithoutSensorInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    value?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    quality?: NullableFloatFieldUpdateOperationsInput | number | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
  }

  export type ActuatorCommandCreateManyActuatorInput = {
    id?: string
    command: string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: $Enums.CommandStatus
    requestedAt?: Date | string
    executedAt?: Date | string | null
    completedAt?: Date | string | null
    errorMessage?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ActuatorCommandUpdateWithoutActuatorInput = {
    id?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ActuatorCommandUncheckedUpdateWithoutActuatorInput = {
    id?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ActuatorCommandUncheckedUpdateManyWithoutActuatorInput = {
    id?: StringFieldUpdateOperationsInput | string
    command?: StringFieldUpdateOperationsInput | string
    parameters?: NullableJsonNullValueInput | InputJsonValue
    status?: EnumCommandStatusFieldUpdateOperationsInput | $Enums.CommandStatus
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    executedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    errorMessage?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }



  /**
   * Aliases for legacy arg types
   */
    /**
     * @deprecated Use DeviceCountOutputTypeDefaultArgs instead
     */
    export type DeviceCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = DeviceCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use SensorCountOutputTypeDefaultArgs instead
     */
    export type SensorCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = SensorCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use ActuatorCountOutputTypeDefaultArgs instead
     */
    export type ActuatorCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = ActuatorCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use DeviceDefaultArgs instead
     */
    export type DeviceArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = DeviceDefaultArgs<ExtArgs>
    /**
     * @deprecated Use SensorDefaultArgs instead
     */
    export type SensorArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = SensorDefaultArgs<ExtArgs>
    /**
     * @deprecated Use SensorReadingDefaultArgs instead
     */
    export type SensorReadingArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = SensorReadingDefaultArgs<ExtArgs>
    /**
     * @deprecated Use ActuatorDefaultArgs instead
     */
    export type ActuatorArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = ActuatorDefaultArgs<ExtArgs>
    /**
     * @deprecated Use ActuatorCommandDefaultArgs instead
     */
    export type ActuatorCommandArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = ActuatorCommandDefaultArgs<ExtArgs>
    /**
     * @deprecated Use DeviceAlertDefaultArgs instead
     */
    export type DeviceAlertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = DeviceAlertDefaultArgs<ExtArgs>

  /**
   * Batch Payload for updateMany & deleteMany & createMany
   */

  export type BatchPayload = {
    count: number
  }

  /**
   * DMMF
   */
  export const dmmf: runtime.BaseDMMF
}