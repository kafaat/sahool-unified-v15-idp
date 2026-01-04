
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
 * Model WeatherObservation
 * 
 */
export type WeatherObservation = $Result.DefaultSelection<Prisma.$WeatherObservationPayload>
/**
 * Model WeatherForecast
 * 
 */
export type WeatherForecast = $Result.DefaultSelection<Prisma.$WeatherForecastPayload>
/**
 * Model WeatherAlert
 * 
 */
export type WeatherAlert = $Result.DefaultSelection<Prisma.$WeatherAlertPayload>
/**
 * Model LocationConfig
 * 
 */
export type LocationConfig = $Result.DefaultSelection<Prisma.$LocationConfigPayload>

/**
 * Enums
 */
export namespace $Enums {
  export const AlertType: {
  HEAT_STRESS: 'HEAT_STRESS',
  FROST: 'FROST',
  HEAVY_RAIN: 'HEAVY_RAIN',
  DROUGHT: 'DROUGHT',
  STRONG_WIND: 'STRONG_WIND',
  STORM: 'STORM',
  DISEASE_RISK: 'DISEASE_RISK',
  OTHER: 'OTHER'
};

export type AlertType = (typeof AlertType)[keyof typeof AlertType]


export const AlertSeverity: {
  INFO: 'INFO',
  MINOR: 'MINOR',
  MODERATE: 'MODERATE',
  SEVERE: 'SEVERE',
  EXTREME: 'EXTREME'
};

export type AlertSeverity = (typeof AlertSeverity)[keyof typeof AlertSeverity]

}

export type AlertType = $Enums.AlertType

export const AlertType: typeof $Enums.AlertType

export type AlertSeverity = $Enums.AlertSeverity

export const AlertSeverity: typeof $Enums.AlertSeverity

/**
 * ##  Prisma Client ʲˢ
 * 
 * Type-safe database client for TypeScript & Node.js
 * @example
 * ```
 * const prisma = new PrismaClient()
 * // Fetch zero or more WeatherObservations
 * const weatherObservations = await prisma.weatherObservation.findMany()
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
   * // Fetch zero or more WeatherObservations
   * const weatherObservations = await prisma.weatherObservation.findMany()
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
   * `prisma.weatherObservation`: Exposes CRUD operations for the **WeatherObservation** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more WeatherObservations
    * const weatherObservations = await prisma.weatherObservation.findMany()
    * ```
    */
  get weatherObservation(): Prisma.WeatherObservationDelegate<ExtArgs>;

  /**
   * `prisma.weatherForecast`: Exposes CRUD operations for the **WeatherForecast** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more WeatherForecasts
    * const weatherForecasts = await prisma.weatherForecast.findMany()
    * ```
    */
  get weatherForecast(): Prisma.WeatherForecastDelegate<ExtArgs>;

  /**
   * `prisma.weatherAlert`: Exposes CRUD operations for the **WeatherAlert** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more WeatherAlerts
    * const weatherAlerts = await prisma.weatherAlert.findMany()
    * ```
    */
  get weatherAlert(): Prisma.WeatherAlertDelegate<ExtArgs>;

  /**
   * `prisma.locationConfig`: Exposes CRUD operations for the **LocationConfig** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more LocationConfigs
    * const locationConfigs = await prisma.locationConfig.findMany()
    * ```
    */
  get locationConfig(): Prisma.LocationConfigDelegate<ExtArgs>;
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
    WeatherObservation: 'WeatherObservation',
    WeatherForecast: 'WeatherForecast',
    WeatherAlert: 'WeatherAlert',
    LocationConfig: 'LocationConfig'
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
      modelProps: "weatherObservation" | "weatherForecast" | "weatherAlert" | "locationConfig"
      txIsolationLevel: Prisma.TransactionIsolationLevel
    }
    model: {
      WeatherObservation: {
        payload: Prisma.$WeatherObservationPayload<ExtArgs>
        fields: Prisma.WeatherObservationFieldRefs
        operations: {
          findUnique: {
            args: Prisma.WeatherObservationFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.WeatherObservationFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>
          }
          findFirst: {
            args: Prisma.WeatherObservationFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.WeatherObservationFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>
          }
          findMany: {
            args: Prisma.WeatherObservationFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>[]
          }
          create: {
            args: Prisma.WeatherObservationCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>
          }
          createMany: {
            args: Prisma.WeatherObservationCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.WeatherObservationCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>[]
          }
          delete: {
            args: Prisma.WeatherObservationDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>
          }
          update: {
            args: Prisma.WeatherObservationUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>
          }
          deleteMany: {
            args: Prisma.WeatherObservationDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.WeatherObservationUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.WeatherObservationUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherObservationPayload>
          }
          aggregate: {
            args: Prisma.WeatherObservationAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateWeatherObservation>
          }
          groupBy: {
            args: Prisma.WeatherObservationGroupByArgs<ExtArgs>
            result: $Utils.Optional<WeatherObservationGroupByOutputType>[]
          }
          count: {
            args: Prisma.WeatherObservationCountArgs<ExtArgs>
            result: $Utils.Optional<WeatherObservationCountAggregateOutputType> | number
          }
        }
      }
      WeatherForecast: {
        payload: Prisma.$WeatherForecastPayload<ExtArgs>
        fields: Prisma.WeatherForecastFieldRefs
        operations: {
          findUnique: {
            args: Prisma.WeatherForecastFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.WeatherForecastFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>
          }
          findFirst: {
            args: Prisma.WeatherForecastFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.WeatherForecastFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>
          }
          findMany: {
            args: Prisma.WeatherForecastFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>[]
          }
          create: {
            args: Prisma.WeatherForecastCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>
          }
          createMany: {
            args: Prisma.WeatherForecastCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.WeatherForecastCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>[]
          }
          delete: {
            args: Prisma.WeatherForecastDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>
          }
          update: {
            args: Prisma.WeatherForecastUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>
          }
          deleteMany: {
            args: Prisma.WeatherForecastDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.WeatherForecastUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.WeatherForecastUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherForecastPayload>
          }
          aggregate: {
            args: Prisma.WeatherForecastAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateWeatherForecast>
          }
          groupBy: {
            args: Prisma.WeatherForecastGroupByArgs<ExtArgs>
            result: $Utils.Optional<WeatherForecastGroupByOutputType>[]
          }
          count: {
            args: Prisma.WeatherForecastCountArgs<ExtArgs>
            result: $Utils.Optional<WeatherForecastCountAggregateOutputType> | number
          }
        }
      }
      WeatherAlert: {
        payload: Prisma.$WeatherAlertPayload<ExtArgs>
        fields: Prisma.WeatherAlertFieldRefs
        operations: {
          findUnique: {
            args: Prisma.WeatherAlertFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.WeatherAlertFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>
          }
          findFirst: {
            args: Prisma.WeatherAlertFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.WeatherAlertFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>
          }
          findMany: {
            args: Prisma.WeatherAlertFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>[]
          }
          create: {
            args: Prisma.WeatherAlertCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>
          }
          createMany: {
            args: Prisma.WeatherAlertCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.WeatherAlertCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>[]
          }
          delete: {
            args: Prisma.WeatherAlertDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>
          }
          update: {
            args: Prisma.WeatherAlertUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>
          }
          deleteMany: {
            args: Prisma.WeatherAlertDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.WeatherAlertUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.WeatherAlertUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WeatherAlertPayload>
          }
          aggregate: {
            args: Prisma.WeatherAlertAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateWeatherAlert>
          }
          groupBy: {
            args: Prisma.WeatherAlertGroupByArgs<ExtArgs>
            result: $Utils.Optional<WeatherAlertGroupByOutputType>[]
          }
          count: {
            args: Prisma.WeatherAlertCountArgs<ExtArgs>
            result: $Utils.Optional<WeatherAlertCountAggregateOutputType> | number
          }
        }
      }
      LocationConfig: {
        payload: Prisma.$LocationConfigPayload<ExtArgs>
        fields: Prisma.LocationConfigFieldRefs
        operations: {
          findUnique: {
            args: Prisma.LocationConfigFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.LocationConfigFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>
          }
          findFirst: {
            args: Prisma.LocationConfigFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.LocationConfigFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>
          }
          findMany: {
            args: Prisma.LocationConfigFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>[]
          }
          create: {
            args: Prisma.LocationConfigCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>
          }
          createMany: {
            args: Prisma.LocationConfigCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.LocationConfigCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>[]
          }
          delete: {
            args: Prisma.LocationConfigDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>
          }
          update: {
            args: Prisma.LocationConfigUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>
          }
          deleteMany: {
            args: Prisma.LocationConfigDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.LocationConfigUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.LocationConfigUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$LocationConfigPayload>
          }
          aggregate: {
            args: Prisma.LocationConfigAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateLocationConfig>
          }
          groupBy: {
            args: Prisma.LocationConfigGroupByArgs<ExtArgs>
            result: $Utils.Optional<LocationConfigGroupByOutputType>[]
          }
          count: {
            args: Prisma.LocationConfigCountArgs<ExtArgs>
            result: $Utils.Optional<LocationConfigCountAggregateOutputType> | number
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
   * Models
   */

  /**
   * Model WeatherObservation
   */

  export type AggregateWeatherObservation = {
    _count: WeatherObservationCountAggregateOutputType | null
    _avg: WeatherObservationAvgAggregateOutputType | null
    _sum: WeatherObservationSumAggregateOutputType | null
    _min: WeatherObservationMinAggregateOutputType | null
    _max: WeatherObservationMaxAggregateOutputType | null
  }

  export type WeatherObservationAvgAggregateOutputType = {
    latitude: number | null
    longitude: number | null
    temperature: number | null
    humidity: number | null
    pressure: number | null
    windSpeed: number | null
    windDirection: number | null
    rainfall: number | null
    uvIndex: number | null
    cloudCover: number | null
    visibility: number | null
  }

  export type WeatherObservationSumAggregateOutputType = {
    latitude: number | null
    longitude: number | null
    temperature: number | null
    humidity: number | null
    pressure: number | null
    windSpeed: number | null
    windDirection: number | null
    rainfall: number | null
    uvIndex: number | null
    cloudCover: number | null
    visibility: number | null
  }

  export type WeatherObservationMinAggregateOutputType = {
    id: string | null
    locationId: string | null
    tenantId: string | null
    latitude: number | null
    longitude: number | null
    timestamp: Date | null
    temperature: number | null
    humidity: number | null
    pressure: number | null
    windSpeed: number | null
    windDirection: number | null
    rainfall: number | null
    uvIndex: number | null
    cloudCover: number | null
    visibility: number | null
    source: string | null
    createdAt: Date | null
  }

  export type WeatherObservationMaxAggregateOutputType = {
    id: string | null
    locationId: string | null
    tenantId: string | null
    latitude: number | null
    longitude: number | null
    timestamp: Date | null
    temperature: number | null
    humidity: number | null
    pressure: number | null
    windSpeed: number | null
    windDirection: number | null
    rainfall: number | null
    uvIndex: number | null
    cloudCover: number | null
    visibility: number | null
    source: string | null
    createdAt: Date | null
  }

  export type WeatherObservationCountAggregateOutputType = {
    id: number
    locationId: number
    tenantId: number
    latitude: number
    longitude: number
    timestamp: number
    temperature: number
    humidity: number
    pressure: number
    windSpeed: number
    windDirection: number
    rainfall: number
    uvIndex: number
    cloudCover: number
    visibility: number
    source: number
    rawData: number
    createdAt: number
    _all: number
  }


  export type WeatherObservationAvgAggregateInputType = {
    latitude?: true
    longitude?: true
    temperature?: true
    humidity?: true
    pressure?: true
    windSpeed?: true
    windDirection?: true
    rainfall?: true
    uvIndex?: true
    cloudCover?: true
    visibility?: true
  }

  export type WeatherObservationSumAggregateInputType = {
    latitude?: true
    longitude?: true
    temperature?: true
    humidity?: true
    pressure?: true
    windSpeed?: true
    windDirection?: true
    rainfall?: true
    uvIndex?: true
    cloudCover?: true
    visibility?: true
  }

  export type WeatherObservationMinAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    latitude?: true
    longitude?: true
    timestamp?: true
    temperature?: true
    humidity?: true
    pressure?: true
    windSpeed?: true
    windDirection?: true
    rainfall?: true
    uvIndex?: true
    cloudCover?: true
    visibility?: true
    source?: true
    createdAt?: true
  }

  export type WeatherObservationMaxAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    latitude?: true
    longitude?: true
    timestamp?: true
    temperature?: true
    humidity?: true
    pressure?: true
    windSpeed?: true
    windDirection?: true
    rainfall?: true
    uvIndex?: true
    cloudCover?: true
    visibility?: true
    source?: true
    createdAt?: true
  }

  export type WeatherObservationCountAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    latitude?: true
    longitude?: true
    timestamp?: true
    temperature?: true
    humidity?: true
    pressure?: true
    windSpeed?: true
    windDirection?: true
    rainfall?: true
    uvIndex?: true
    cloudCover?: true
    visibility?: true
    source?: true
    rawData?: true
    createdAt?: true
    _all?: true
  }

  export type WeatherObservationAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which WeatherObservation to aggregate.
     */
    where?: WeatherObservationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherObservations to fetch.
     */
    orderBy?: WeatherObservationOrderByWithRelationInput | WeatherObservationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: WeatherObservationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherObservations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherObservations.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned WeatherObservations
    **/
    _count?: true | WeatherObservationCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: WeatherObservationAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: WeatherObservationSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: WeatherObservationMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: WeatherObservationMaxAggregateInputType
  }

  export type GetWeatherObservationAggregateType<T extends WeatherObservationAggregateArgs> = {
        [P in keyof T & keyof AggregateWeatherObservation]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateWeatherObservation[P]>
      : GetScalarType<T[P], AggregateWeatherObservation[P]>
  }




  export type WeatherObservationGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: WeatherObservationWhereInput
    orderBy?: WeatherObservationOrderByWithAggregationInput | WeatherObservationOrderByWithAggregationInput[]
    by: WeatherObservationScalarFieldEnum[] | WeatherObservationScalarFieldEnum
    having?: WeatherObservationScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: WeatherObservationCountAggregateInputType | true
    _avg?: WeatherObservationAvgAggregateInputType
    _sum?: WeatherObservationSumAggregateInputType
    _min?: WeatherObservationMinAggregateInputType
    _max?: WeatherObservationMaxAggregateInputType
  }

  export type WeatherObservationGroupByOutputType = {
    id: string
    locationId: string
    tenantId: string | null
    latitude: number
    longitude: number
    timestamp: Date
    temperature: number
    humidity: number
    pressure: number
    windSpeed: number
    windDirection: number
    rainfall: number | null
    uvIndex: number | null
    cloudCover: number | null
    visibility: number | null
    source: string
    rawData: JsonValue | null
    createdAt: Date
    _count: WeatherObservationCountAggregateOutputType | null
    _avg: WeatherObservationAvgAggregateOutputType | null
    _sum: WeatherObservationSumAggregateOutputType | null
    _min: WeatherObservationMinAggregateOutputType | null
    _max: WeatherObservationMaxAggregateOutputType | null
  }

  type GetWeatherObservationGroupByPayload<T extends WeatherObservationGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<WeatherObservationGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof WeatherObservationGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], WeatherObservationGroupByOutputType[P]>
            : GetScalarType<T[P], WeatherObservationGroupByOutputType[P]>
        }
      >
    >


  export type WeatherObservationSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    latitude?: boolean
    longitude?: boolean
    timestamp?: boolean
    temperature?: boolean
    humidity?: boolean
    pressure?: boolean
    windSpeed?: boolean
    windDirection?: boolean
    rainfall?: boolean
    uvIndex?: boolean
    cloudCover?: boolean
    visibility?: boolean
    source?: boolean
    rawData?: boolean
    createdAt?: boolean
  }, ExtArgs["result"]["weatherObservation"]>

  export type WeatherObservationSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    latitude?: boolean
    longitude?: boolean
    timestamp?: boolean
    temperature?: boolean
    humidity?: boolean
    pressure?: boolean
    windSpeed?: boolean
    windDirection?: boolean
    rainfall?: boolean
    uvIndex?: boolean
    cloudCover?: boolean
    visibility?: boolean
    source?: boolean
    rawData?: boolean
    createdAt?: boolean
  }, ExtArgs["result"]["weatherObservation"]>

  export type WeatherObservationSelectScalar = {
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    latitude?: boolean
    longitude?: boolean
    timestamp?: boolean
    temperature?: boolean
    humidity?: boolean
    pressure?: boolean
    windSpeed?: boolean
    windDirection?: boolean
    rainfall?: boolean
    uvIndex?: boolean
    cloudCover?: boolean
    visibility?: boolean
    source?: boolean
    rawData?: boolean
    createdAt?: boolean
  }


  export type $WeatherObservationPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "WeatherObservation"
    objects: {}
    scalars: $Extensions.GetPayloadResult<{
      id: string
      locationId: string
      tenantId: string | null
      latitude: number
      longitude: number
      timestamp: Date
      temperature: number
      humidity: number
      pressure: number
      windSpeed: number
      windDirection: number
      rainfall: number | null
      uvIndex: number | null
      cloudCover: number | null
      visibility: number | null
      source: string
      rawData: Prisma.JsonValue | null
      createdAt: Date
    }, ExtArgs["result"]["weatherObservation"]>
    composites: {}
  }

  type WeatherObservationGetPayload<S extends boolean | null | undefined | WeatherObservationDefaultArgs> = $Result.GetResult<Prisma.$WeatherObservationPayload, S>

  type WeatherObservationCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<WeatherObservationFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: WeatherObservationCountAggregateInputType | true
    }

  export interface WeatherObservationDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['WeatherObservation'], meta: { name: 'WeatherObservation' } }
    /**
     * Find zero or one WeatherObservation that matches the filter.
     * @param {WeatherObservationFindUniqueArgs} args - Arguments to find a WeatherObservation
     * @example
     * // Get one WeatherObservation
     * const weatherObservation = await prisma.weatherObservation.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends WeatherObservationFindUniqueArgs>(args: SelectSubset<T, WeatherObservationFindUniqueArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one WeatherObservation that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {WeatherObservationFindUniqueOrThrowArgs} args - Arguments to find a WeatherObservation
     * @example
     * // Get one WeatherObservation
     * const weatherObservation = await prisma.weatherObservation.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends WeatherObservationFindUniqueOrThrowArgs>(args: SelectSubset<T, WeatherObservationFindUniqueOrThrowArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first WeatherObservation that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationFindFirstArgs} args - Arguments to find a WeatherObservation
     * @example
     * // Get one WeatherObservation
     * const weatherObservation = await prisma.weatherObservation.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends WeatherObservationFindFirstArgs>(args?: SelectSubset<T, WeatherObservationFindFirstArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first WeatherObservation that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationFindFirstOrThrowArgs} args - Arguments to find a WeatherObservation
     * @example
     * // Get one WeatherObservation
     * const weatherObservation = await prisma.weatherObservation.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends WeatherObservationFindFirstOrThrowArgs>(args?: SelectSubset<T, WeatherObservationFindFirstOrThrowArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more WeatherObservations that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all WeatherObservations
     * const weatherObservations = await prisma.weatherObservation.findMany()
     * 
     * // Get first 10 WeatherObservations
     * const weatherObservations = await prisma.weatherObservation.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const weatherObservationWithIdOnly = await prisma.weatherObservation.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends WeatherObservationFindManyArgs>(args?: SelectSubset<T, WeatherObservationFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a WeatherObservation.
     * @param {WeatherObservationCreateArgs} args - Arguments to create a WeatherObservation.
     * @example
     * // Create one WeatherObservation
     * const WeatherObservation = await prisma.weatherObservation.create({
     *   data: {
     *     // ... data to create a WeatherObservation
     *   }
     * })
     * 
     */
    create<T extends WeatherObservationCreateArgs>(args: SelectSubset<T, WeatherObservationCreateArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many WeatherObservations.
     * @param {WeatherObservationCreateManyArgs} args - Arguments to create many WeatherObservations.
     * @example
     * // Create many WeatherObservations
     * const weatherObservation = await prisma.weatherObservation.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends WeatherObservationCreateManyArgs>(args?: SelectSubset<T, WeatherObservationCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many WeatherObservations and returns the data saved in the database.
     * @param {WeatherObservationCreateManyAndReturnArgs} args - Arguments to create many WeatherObservations.
     * @example
     * // Create many WeatherObservations
     * const weatherObservation = await prisma.weatherObservation.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many WeatherObservations and only return the `id`
     * const weatherObservationWithIdOnly = await prisma.weatherObservation.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends WeatherObservationCreateManyAndReturnArgs>(args?: SelectSubset<T, WeatherObservationCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a WeatherObservation.
     * @param {WeatherObservationDeleteArgs} args - Arguments to delete one WeatherObservation.
     * @example
     * // Delete one WeatherObservation
     * const WeatherObservation = await prisma.weatherObservation.delete({
     *   where: {
     *     // ... filter to delete one WeatherObservation
     *   }
     * })
     * 
     */
    delete<T extends WeatherObservationDeleteArgs>(args: SelectSubset<T, WeatherObservationDeleteArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one WeatherObservation.
     * @param {WeatherObservationUpdateArgs} args - Arguments to update one WeatherObservation.
     * @example
     * // Update one WeatherObservation
     * const weatherObservation = await prisma.weatherObservation.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends WeatherObservationUpdateArgs>(args: SelectSubset<T, WeatherObservationUpdateArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more WeatherObservations.
     * @param {WeatherObservationDeleteManyArgs} args - Arguments to filter WeatherObservations to delete.
     * @example
     * // Delete a few WeatherObservations
     * const { count } = await prisma.weatherObservation.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends WeatherObservationDeleteManyArgs>(args?: SelectSubset<T, WeatherObservationDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more WeatherObservations.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many WeatherObservations
     * const weatherObservation = await prisma.weatherObservation.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends WeatherObservationUpdateManyArgs>(args: SelectSubset<T, WeatherObservationUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one WeatherObservation.
     * @param {WeatherObservationUpsertArgs} args - Arguments to update or create a WeatherObservation.
     * @example
     * // Update or create a WeatherObservation
     * const weatherObservation = await prisma.weatherObservation.upsert({
     *   create: {
     *     // ... data to create a WeatherObservation
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the WeatherObservation we want to update
     *   }
     * })
     */
    upsert<T extends WeatherObservationUpsertArgs>(args: SelectSubset<T, WeatherObservationUpsertArgs<ExtArgs>>): Prisma__WeatherObservationClient<$Result.GetResult<Prisma.$WeatherObservationPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of WeatherObservations.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationCountArgs} args - Arguments to filter WeatherObservations to count.
     * @example
     * // Count the number of WeatherObservations
     * const count = await prisma.weatherObservation.count({
     *   where: {
     *     // ... the filter for the WeatherObservations we want to count
     *   }
     * })
    **/
    count<T extends WeatherObservationCountArgs>(
      args?: Subset<T, WeatherObservationCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], WeatherObservationCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a WeatherObservation.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends WeatherObservationAggregateArgs>(args: Subset<T, WeatherObservationAggregateArgs>): Prisma.PrismaPromise<GetWeatherObservationAggregateType<T>>

    /**
     * Group by WeatherObservation.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherObservationGroupByArgs} args - Group by arguments.
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
      T extends WeatherObservationGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: WeatherObservationGroupByArgs['orderBy'] }
        : { orderBy?: WeatherObservationGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, WeatherObservationGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetWeatherObservationGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the WeatherObservation model
   */
  readonly fields: WeatherObservationFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for WeatherObservation.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__WeatherObservationClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
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
   * Fields of the WeatherObservation model
   */ 
  interface WeatherObservationFieldRefs {
    readonly id: FieldRef<"WeatherObservation", 'String'>
    readonly locationId: FieldRef<"WeatherObservation", 'String'>
    readonly tenantId: FieldRef<"WeatherObservation", 'String'>
    readonly latitude: FieldRef<"WeatherObservation", 'Float'>
    readonly longitude: FieldRef<"WeatherObservation", 'Float'>
    readonly timestamp: FieldRef<"WeatherObservation", 'DateTime'>
    readonly temperature: FieldRef<"WeatherObservation", 'Float'>
    readonly humidity: FieldRef<"WeatherObservation", 'Float'>
    readonly pressure: FieldRef<"WeatherObservation", 'Float'>
    readonly windSpeed: FieldRef<"WeatherObservation", 'Float'>
    readonly windDirection: FieldRef<"WeatherObservation", 'Float'>
    readonly rainfall: FieldRef<"WeatherObservation", 'Float'>
    readonly uvIndex: FieldRef<"WeatherObservation", 'Float'>
    readonly cloudCover: FieldRef<"WeatherObservation", 'Float'>
    readonly visibility: FieldRef<"WeatherObservation", 'Float'>
    readonly source: FieldRef<"WeatherObservation", 'String'>
    readonly rawData: FieldRef<"WeatherObservation", 'Json'>
    readonly createdAt: FieldRef<"WeatherObservation", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * WeatherObservation findUnique
   */
  export type WeatherObservationFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * Filter, which WeatherObservation to fetch.
     */
    where: WeatherObservationWhereUniqueInput
  }

  /**
   * WeatherObservation findUniqueOrThrow
   */
  export type WeatherObservationFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * Filter, which WeatherObservation to fetch.
     */
    where: WeatherObservationWhereUniqueInput
  }

  /**
   * WeatherObservation findFirst
   */
  export type WeatherObservationFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * Filter, which WeatherObservation to fetch.
     */
    where?: WeatherObservationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherObservations to fetch.
     */
    orderBy?: WeatherObservationOrderByWithRelationInput | WeatherObservationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for WeatherObservations.
     */
    cursor?: WeatherObservationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherObservations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherObservations.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of WeatherObservations.
     */
    distinct?: WeatherObservationScalarFieldEnum | WeatherObservationScalarFieldEnum[]
  }

  /**
   * WeatherObservation findFirstOrThrow
   */
  export type WeatherObservationFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * Filter, which WeatherObservation to fetch.
     */
    where?: WeatherObservationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherObservations to fetch.
     */
    orderBy?: WeatherObservationOrderByWithRelationInput | WeatherObservationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for WeatherObservations.
     */
    cursor?: WeatherObservationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherObservations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherObservations.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of WeatherObservations.
     */
    distinct?: WeatherObservationScalarFieldEnum | WeatherObservationScalarFieldEnum[]
  }

  /**
   * WeatherObservation findMany
   */
  export type WeatherObservationFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * Filter, which WeatherObservations to fetch.
     */
    where?: WeatherObservationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherObservations to fetch.
     */
    orderBy?: WeatherObservationOrderByWithRelationInput | WeatherObservationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing WeatherObservations.
     */
    cursor?: WeatherObservationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherObservations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherObservations.
     */
    skip?: number
    distinct?: WeatherObservationScalarFieldEnum | WeatherObservationScalarFieldEnum[]
  }

  /**
   * WeatherObservation create
   */
  export type WeatherObservationCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * The data needed to create a WeatherObservation.
     */
    data: XOR<WeatherObservationCreateInput, WeatherObservationUncheckedCreateInput>
  }

  /**
   * WeatherObservation createMany
   */
  export type WeatherObservationCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many WeatherObservations.
     */
    data: WeatherObservationCreateManyInput | WeatherObservationCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * WeatherObservation createManyAndReturn
   */
  export type WeatherObservationCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many WeatherObservations.
     */
    data: WeatherObservationCreateManyInput | WeatherObservationCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * WeatherObservation update
   */
  export type WeatherObservationUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * The data needed to update a WeatherObservation.
     */
    data: XOR<WeatherObservationUpdateInput, WeatherObservationUncheckedUpdateInput>
    /**
     * Choose, which WeatherObservation to update.
     */
    where: WeatherObservationWhereUniqueInput
  }

  /**
   * WeatherObservation updateMany
   */
  export type WeatherObservationUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update WeatherObservations.
     */
    data: XOR<WeatherObservationUpdateManyMutationInput, WeatherObservationUncheckedUpdateManyInput>
    /**
     * Filter which WeatherObservations to update
     */
    where?: WeatherObservationWhereInput
  }

  /**
   * WeatherObservation upsert
   */
  export type WeatherObservationUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * The filter to search for the WeatherObservation to update in case it exists.
     */
    where: WeatherObservationWhereUniqueInput
    /**
     * In case the WeatherObservation found by the `where` argument doesn't exist, create a new WeatherObservation with this data.
     */
    create: XOR<WeatherObservationCreateInput, WeatherObservationUncheckedCreateInput>
    /**
     * In case the WeatherObservation was found with the provided `where` argument, update it with this data.
     */
    update: XOR<WeatherObservationUpdateInput, WeatherObservationUncheckedUpdateInput>
  }

  /**
   * WeatherObservation delete
   */
  export type WeatherObservationDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
    /**
     * Filter which WeatherObservation to delete.
     */
    where: WeatherObservationWhereUniqueInput
  }

  /**
   * WeatherObservation deleteMany
   */
  export type WeatherObservationDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which WeatherObservations to delete
     */
    where?: WeatherObservationWhereInput
  }

  /**
   * WeatherObservation without action
   */
  export type WeatherObservationDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherObservation
     */
    select?: WeatherObservationSelect<ExtArgs> | null
  }


  /**
   * Model WeatherForecast
   */

  export type AggregateWeatherForecast = {
    _count: WeatherForecastCountAggregateOutputType | null
    _min: WeatherForecastMinAggregateOutputType | null
    _max: WeatherForecastMaxAggregateOutputType | null
  }

  export type WeatherForecastMinAggregateOutputType = {
    id: string | null
    locationId: string | null
    tenantId: string | null
    forecastFor: Date | null
    fetchedAt: Date | null
    provider: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type WeatherForecastMaxAggregateOutputType = {
    id: string | null
    locationId: string | null
    tenantId: string | null
    forecastFor: Date | null
    fetchedAt: Date | null
    provider: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type WeatherForecastCountAggregateOutputType = {
    id: number
    locationId: number
    tenantId: number
    forecastFor: number
    fetchedAt: number
    provider: number
    hourlyData: number
    dailyData: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type WeatherForecastMinAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    forecastFor?: true
    fetchedAt?: true
    provider?: true
    createdAt?: true
    updatedAt?: true
  }

  export type WeatherForecastMaxAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    forecastFor?: true
    fetchedAt?: true
    provider?: true
    createdAt?: true
    updatedAt?: true
  }

  export type WeatherForecastCountAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    forecastFor?: true
    fetchedAt?: true
    provider?: true
    hourlyData?: true
    dailyData?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type WeatherForecastAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which WeatherForecast to aggregate.
     */
    where?: WeatherForecastWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherForecasts to fetch.
     */
    orderBy?: WeatherForecastOrderByWithRelationInput | WeatherForecastOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: WeatherForecastWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherForecasts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherForecasts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned WeatherForecasts
    **/
    _count?: true | WeatherForecastCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: WeatherForecastMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: WeatherForecastMaxAggregateInputType
  }

  export type GetWeatherForecastAggregateType<T extends WeatherForecastAggregateArgs> = {
        [P in keyof T & keyof AggregateWeatherForecast]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateWeatherForecast[P]>
      : GetScalarType<T[P], AggregateWeatherForecast[P]>
  }




  export type WeatherForecastGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: WeatherForecastWhereInput
    orderBy?: WeatherForecastOrderByWithAggregationInput | WeatherForecastOrderByWithAggregationInput[]
    by: WeatherForecastScalarFieldEnum[] | WeatherForecastScalarFieldEnum
    having?: WeatherForecastScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: WeatherForecastCountAggregateInputType | true
    _min?: WeatherForecastMinAggregateInputType
    _max?: WeatherForecastMaxAggregateInputType
  }

  export type WeatherForecastGroupByOutputType = {
    id: string
    locationId: string
    tenantId: string | null
    forecastFor: Date
    fetchedAt: Date
    provider: string
    hourlyData: JsonValue
    dailyData: JsonValue
    createdAt: Date
    updatedAt: Date
    _count: WeatherForecastCountAggregateOutputType | null
    _min: WeatherForecastMinAggregateOutputType | null
    _max: WeatherForecastMaxAggregateOutputType | null
  }

  type GetWeatherForecastGroupByPayload<T extends WeatherForecastGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<WeatherForecastGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof WeatherForecastGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], WeatherForecastGroupByOutputType[P]>
            : GetScalarType<T[P], WeatherForecastGroupByOutputType[P]>
        }
      >
    >


  export type WeatherForecastSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    forecastFor?: boolean
    fetchedAt?: boolean
    provider?: boolean
    hourlyData?: boolean
    dailyData?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["weatherForecast"]>

  export type WeatherForecastSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    forecastFor?: boolean
    fetchedAt?: boolean
    provider?: boolean
    hourlyData?: boolean
    dailyData?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["weatherForecast"]>

  export type WeatherForecastSelectScalar = {
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    forecastFor?: boolean
    fetchedAt?: boolean
    provider?: boolean
    hourlyData?: boolean
    dailyData?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }


  export type $WeatherForecastPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "WeatherForecast"
    objects: {}
    scalars: $Extensions.GetPayloadResult<{
      id: string
      locationId: string
      tenantId: string | null
      forecastFor: Date
      fetchedAt: Date
      provider: string
      hourlyData: Prisma.JsonValue
      dailyData: Prisma.JsonValue
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["weatherForecast"]>
    composites: {}
  }

  type WeatherForecastGetPayload<S extends boolean | null | undefined | WeatherForecastDefaultArgs> = $Result.GetResult<Prisma.$WeatherForecastPayload, S>

  type WeatherForecastCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<WeatherForecastFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: WeatherForecastCountAggregateInputType | true
    }

  export interface WeatherForecastDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['WeatherForecast'], meta: { name: 'WeatherForecast' } }
    /**
     * Find zero or one WeatherForecast that matches the filter.
     * @param {WeatherForecastFindUniqueArgs} args - Arguments to find a WeatherForecast
     * @example
     * // Get one WeatherForecast
     * const weatherForecast = await prisma.weatherForecast.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends WeatherForecastFindUniqueArgs>(args: SelectSubset<T, WeatherForecastFindUniqueArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one WeatherForecast that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {WeatherForecastFindUniqueOrThrowArgs} args - Arguments to find a WeatherForecast
     * @example
     * // Get one WeatherForecast
     * const weatherForecast = await prisma.weatherForecast.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends WeatherForecastFindUniqueOrThrowArgs>(args: SelectSubset<T, WeatherForecastFindUniqueOrThrowArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first WeatherForecast that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastFindFirstArgs} args - Arguments to find a WeatherForecast
     * @example
     * // Get one WeatherForecast
     * const weatherForecast = await prisma.weatherForecast.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends WeatherForecastFindFirstArgs>(args?: SelectSubset<T, WeatherForecastFindFirstArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first WeatherForecast that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastFindFirstOrThrowArgs} args - Arguments to find a WeatherForecast
     * @example
     * // Get one WeatherForecast
     * const weatherForecast = await prisma.weatherForecast.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends WeatherForecastFindFirstOrThrowArgs>(args?: SelectSubset<T, WeatherForecastFindFirstOrThrowArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more WeatherForecasts that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all WeatherForecasts
     * const weatherForecasts = await prisma.weatherForecast.findMany()
     * 
     * // Get first 10 WeatherForecasts
     * const weatherForecasts = await prisma.weatherForecast.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const weatherForecastWithIdOnly = await prisma.weatherForecast.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends WeatherForecastFindManyArgs>(args?: SelectSubset<T, WeatherForecastFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a WeatherForecast.
     * @param {WeatherForecastCreateArgs} args - Arguments to create a WeatherForecast.
     * @example
     * // Create one WeatherForecast
     * const WeatherForecast = await prisma.weatherForecast.create({
     *   data: {
     *     // ... data to create a WeatherForecast
     *   }
     * })
     * 
     */
    create<T extends WeatherForecastCreateArgs>(args: SelectSubset<T, WeatherForecastCreateArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many WeatherForecasts.
     * @param {WeatherForecastCreateManyArgs} args - Arguments to create many WeatherForecasts.
     * @example
     * // Create many WeatherForecasts
     * const weatherForecast = await prisma.weatherForecast.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends WeatherForecastCreateManyArgs>(args?: SelectSubset<T, WeatherForecastCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many WeatherForecasts and returns the data saved in the database.
     * @param {WeatherForecastCreateManyAndReturnArgs} args - Arguments to create many WeatherForecasts.
     * @example
     * // Create many WeatherForecasts
     * const weatherForecast = await prisma.weatherForecast.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many WeatherForecasts and only return the `id`
     * const weatherForecastWithIdOnly = await prisma.weatherForecast.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends WeatherForecastCreateManyAndReturnArgs>(args?: SelectSubset<T, WeatherForecastCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a WeatherForecast.
     * @param {WeatherForecastDeleteArgs} args - Arguments to delete one WeatherForecast.
     * @example
     * // Delete one WeatherForecast
     * const WeatherForecast = await prisma.weatherForecast.delete({
     *   where: {
     *     // ... filter to delete one WeatherForecast
     *   }
     * })
     * 
     */
    delete<T extends WeatherForecastDeleteArgs>(args: SelectSubset<T, WeatherForecastDeleteArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one WeatherForecast.
     * @param {WeatherForecastUpdateArgs} args - Arguments to update one WeatherForecast.
     * @example
     * // Update one WeatherForecast
     * const weatherForecast = await prisma.weatherForecast.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends WeatherForecastUpdateArgs>(args: SelectSubset<T, WeatherForecastUpdateArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more WeatherForecasts.
     * @param {WeatherForecastDeleteManyArgs} args - Arguments to filter WeatherForecasts to delete.
     * @example
     * // Delete a few WeatherForecasts
     * const { count } = await prisma.weatherForecast.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends WeatherForecastDeleteManyArgs>(args?: SelectSubset<T, WeatherForecastDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more WeatherForecasts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many WeatherForecasts
     * const weatherForecast = await prisma.weatherForecast.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends WeatherForecastUpdateManyArgs>(args: SelectSubset<T, WeatherForecastUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one WeatherForecast.
     * @param {WeatherForecastUpsertArgs} args - Arguments to update or create a WeatherForecast.
     * @example
     * // Update or create a WeatherForecast
     * const weatherForecast = await prisma.weatherForecast.upsert({
     *   create: {
     *     // ... data to create a WeatherForecast
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the WeatherForecast we want to update
     *   }
     * })
     */
    upsert<T extends WeatherForecastUpsertArgs>(args: SelectSubset<T, WeatherForecastUpsertArgs<ExtArgs>>): Prisma__WeatherForecastClient<$Result.GetResult<Prisma.$WeatherForecastPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of WeatherForecasts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastCountArgs} args - Arguments to filter WeatherForecasts to count.
     * @example
     * // Count the number of WeatherForecasts
     * const count = await prisma.weatherForecast.count({
     *   where: {
     *     // ... the filter for the WeatherForecasts we want to count
     *   }
     * })
    **/
    count<T extends WeatherForecastCountArgs>(
      args?: Subset<T, WeatherForecastCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], WeatherForecastCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a WeatherForecast.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends WeatherForecastAggregateArgs>(args: Subset<T, WeatherForecastAggregateArgs>): Prisma.PrismaPromise<GetWeatherForecastAggregateType<T>>

    /**
     * Group by WeatherForecast.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherForecastGroupByArgs} args - Group by arguments.
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
      T extends WeatherForecastGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: WeatherForecastGroupByArgs['orderBy'] }
        : { orderBy?: WeatherForecastGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, WeatherForecastGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetWeatherForecastGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the WeatherForecast model
   */
  readonly fields: WeatherForecastFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for WeatherForecast.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__WeatherForecastClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
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
   * Fields of the WeatherForecast model
   */ 
  interface WeatherForecastFieldRefs {
    readonly id: FieldRef<"WeatherForecast", 'String'>
    readonly locationId: FieldRef<"WeatherForecast", 'String'>
    readonly tenantId: FieldRef<"WeatherForecast", 'String'>
    readonly forecastFor: FieldRef<"WeatherForecast", 'DateTime'>
    readonly fetchedAt: FieldRef<"WeatherForecast", 'DateTime'>
    readonly provider: FieldRef<"WeatherForecast", 'String'>
    readonly hourlyData: FieldRef<"WeatherForecast", 'Json'>
    readonly dailyData: FieldRef<"WeatherForecast", 'Json'>
    readonly createdAt: FieldRef<"WeatherForecast", 'DateTime'>
    readonly updatedAt: FieldRef<"WeatherForecast", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * WeatherForecast findUnique
   */
  export type WeatherForecastFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * Filter, which WeatherForecast to fetch.
     */
    where: WeatherForecastWhereUniqueInput
  }

  /**
   * WeatherForecast findUniqueOrThrow
   */
  export type WeatherForecastFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * Filter, which WeatherForecast to fetch.
     */
    where: WeatherForecastWhereUniqueInput
  }

  /**
   * WeatherForecast findFirst
   */
  export type WeatherForecastFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * Filter, which WeatherForecast to fetch.
     */
    where?: WeatherForecastWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherForecasts to fetch.
     */
    orderBy?: WeatherForecastOrderByWithRelationInput | WeatherForecastOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for WeatherForecasts.
     */
    cursor?: WeatherForecastWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherForecasts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherForecasts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of WeatherForecasts.
     */
    distinct?: WeatherForecastScalarFieldEnum | WeatherForecastScalarFieldEnum[]
  }

  /**
   * WeatherForecast findFirstOrThrow
   */
  export type WeatherForecastFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * Filter, which WeatherForecast to fetch.
     */
    where?: WeatherForecastWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherForecasts to fetch.
     */
    orderBy?: WeatherForecastOrderByWithRelationInput | WeatherForecastOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for WeatherForecasts.
     */
    cursor?: WeatherForecastWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherForecasts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherForecasts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of WeatherForecasts.
     */
    distinct?: WeatherForecastScalarFieldEnum | WeatherForecastScalarFieldEnum[]
  }

  /**
   * WeatherForecast findMany
   */
  export type WeatherForecastFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * Filter, which WeatherForecasts to fetch.
     */
    where?: WeatherForecastWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherForecasts to fetch.
     */
    orderBy?: WeatherForecastOrderByWithRelationInput | WeatherForecastOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing WeatherForecasts.
     */
    cursor?: WeatherForecastWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherForecasts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherForecasts.
     */
    skip?: number
    distinct?: WeatherForecastScalarFieldEnum | WeatherForecastScalarFieldEnum[]
  }

  /**
   * WeatherForecast create
   */
  export type WeatherForecastCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * The data needed to create a WeatherForecast.
     */
    data: XOR<WeatherForecastCreateInput, WeatherForecastUncheckedCreateInput>
  }

  /**
   * WeatherForecast createMany
   */
  export type WeatherForecastCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many WeatherForecasts.
     */
    data: WeatherForecastCreateManyInput | WeatherForecastCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * WeatherForecast createManyAndReturn
   */
  export type WeatherForecastCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many WeatherForecasts.
     */
    data: WeatherForecastCreateManyInput | WeatherForecastCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * WeatherForecast update
   */
  export type WeatherForecastUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * The data needed to update a WeatherForecast.
     */
    data: XOR<WeatherForecastUpdateInput, WeatherForecastUncheckedUpdateInput>
    /**
     * Choose, which WeatherForecast to update.
     */
    where: WeatherForecastWhereUniqueInput
  }

  /**
   * WeatherForecast updateMany
   */
  export type WeatherForecastUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update WeatherForecasts.
     */
    data: XOR<WeatherForecastUpdateManyMutationInput, WeatherForecastUncheckedUpdateManyInput>
    /**
     * Filter which WeatherForecasts to update
     */
    where?: WeatherForecastWhereInput
  }

  /**
   * WeatherForecast upsert
   */
  export type WeatherForecastUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * The filter to search for the WeatherForecast to update in case it exists.
     */
    where: WeatherForecastWhereUniqueInput
    /**
     * In case the WeatherForecast found by the `where` argument doesn't exist, create a new WeatherForecast with this data.
     */
    create: XOR<WeatherForecastCreateInput, WeatherForecastUncheckedCreateInput>
    /**
     * In case the WeatherForecast was found with the provided `where` argument, update it with this data.
     */
    update: XOR<WeatherForecastUpdateInput, WeatherForecastUncheckedUpdateInput>
  }

  /**
   * WeatherForecast delete
   */
  export type WeatherForecastDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
    /**
     * Filter which WeatherForecast to delete.
     */
    where: WeatherForecastWhereUniqueInput
  }

  /**
   * WeatherForecast deleteMany
   */
  export type WeatherForecastDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which WeatherForecasts to delete
     */
    where?: WeatherForecastWhereInput
  }

  /**
   * WeatherForecast without action
   */
  export type WeatherForecastDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherForecast
     */
    select?: WeatherForecastSelect<ExtArgs> | null
  }


  /**
   * Model WeatherAlert
   */

  export type AggregateWeatherAlert = {
    _count: WeatherAlertCountAggregateOutputType | null
    _min: WeatherAlertMinAggregateOutputType | null
    _max: WeatherAlertMaxAggregateOutputType | null
  }

  export type WeatherAlertMinAggregateOutputType = {
    id: string | null
    locationId: string | null
    tenantId: string | null
    alertType: $Enums.AlertType | null
    severity: $Enums.AlertSeverity | null
    headline: string | null
    description: string | null
    startTime: Date | null
    endTime: Date | null
    source: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type WeatherAlertMaxAggregateOutputType = {
    id: string | null
    locationId: string | null
    tenantId: string | null
    alertType: $Enums.AlertType | null
    severity: $Enums.AlertSeverity | null
    headline: string | null
    description: string | null
    startTime: Date | null
    endTime: Date | null
    source: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type WeatherAlertCountAggregateOutputType = {
    id: number
    locationId: number
    tenantId: number
    alertType: number
    severity: number
    headline: number
    description: number
    startTime: number
    endTime: number
    source: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type WeatherAlertMinAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    alertType?: true
    severity?: true
    headline?: true
    description?: true
    startTime?: true
    endTime?: true
    source?: true
    createdAt?: true
    updatedAt?: true
  }

  export type WeatherAlertMaxAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    alertType?: true
    severity?: true
    headline?: true
    description?: true
    startTime?: true
    endTime?: true
    source?: true
    createdAt?: true
    updatedAt?: true
  }

  export type WeatherAlertCountAggregateInputType = {
    id?: true
    locationId?: true
    tenantId?: true
    alertType?: true
    severity?: true
    headline?: true
    description?: true
    startTime?: true
    endTime?: true
    source?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type WeatherAlertAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which WeatherAlert to aggregate.
     */
    where?: WeatherAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherAlerts to fetch.
     */
    orderBy?: WeatherAlertOrderByWithRelationInput | WeatherAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: WeatherAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned WeatherAlerts
    **/
    _count?: true | WeatherAlertCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: WeatherAlertMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: WeatherAlertMaxAggregateInputType
  }

  export type GetWeatherAlertAggregateType<T extends WeatherAlertAggregateArgs> = {
        [P in keyof T & keyof AggregateWeatherAlert]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateWeatherAlert[P]>
      : GetScalarType<T[P], AggregateWeatherAlert[P]>
  }




  export type WeatherAlertGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: WeatherAlertWhereInput
    orderBy?: WeatherAlertOrderByWithAggregationInput | WeatherAlertOrderByWithAggregationInput[]
    by: WeatherAlertScalarFieldEnum[] | WeatherAlertScalarFieldEnum
    having?: WeatherAlertScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: WeatherAlertCountAggregateInputType | true
    _min?: WeatherAlertMinAggregateInputType
    _max?: WeatherAlertMaxAggregateInputType
  }

  export type WeatherAlertGroupByOutputType = {
    id: string
    locationId: string
    tenantId: string | null
    alertType: $Enums.AlertType
    severity: $Enums.AlertSeverity
    headline: string
    description: string
    startTime: Date
    endTime: Date
    source: string
    createdAt: Date
    updatedAt: Date
    _count: WeatherAlertCountAggregateOutputType | null
    _min: WeatherAlertMinAggregateOutputType | null
    _max: WeatherAlertMaxAggregateOutputType | null
  }

  type GetWeatherAlertGroupByPayload<T extends WeatherAlertGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<WeatherAlertGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof WeatherAlertGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], WeatherAlertGroupByOutputType[P]>
            : GetScalarType<T[P], WeatherAlertGroupByOutputType[P]>
        }
      >
    >


  export type WeatherAlertSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    alertType?: boolean
    severity?: boolean
    headline?: boolean
    description?: boolean
    startTime?: boolean
    endTime?: boolean
    source?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["weatherAlert"]>

  export type WeatherAlertSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    alertType?: boolean
    severity?: boolean
    headline?: boolean
    description?: boolean
    startTime?: boolean
    endTime?: boolean
    source?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["weatherAlert"]>

  export type WeatherAlertSelectScalar = {
    id?: boolean
    locationId?: boolean
    tenantId?: boolean
    alertType?: boolean
    severity?: boolean
    headline?: boolean
    description?: boolean
    startTime?: boolean
    endTime?: boolean
    source?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }


  export type $WeatherAlertPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "WeatherAlert"
    objects: {}
    scalars: $Extensions.GetPayloadResult<{
      id: string
      locationId: string
      tenantId: string | null
      alertType: $Enums.AlertType
      severity: $Enums.AlertSeverity
      headline: string
      description: string
      startTime: Date
      endTime: Date
      source: string
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["weatherAlert"]>
    composites: {}
  }

  type WeatherAlertGetPayload<S extends boolean | null | undefined | WeatherAlertDefaultArgs> = $Result.GetResult<Prisma.$WeatherAlertPayload, S>

  type WeatherAlertCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<WeatherAlertFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: WeatherAlertCountAggregateInputType | true
    }

  export interface WeatherAlertDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['WeatherAlert'], meta: { name: 'WeatherAlert' } }
    /**
     * Find zero or one WeatherAlert that matches the filter.
     * @param {WeatherAlertFindUniqueArgs} args - Arguments to find a WeatherAlert
     * @example
     * // Get one WeatherAlert
     * const weatherAlert = await prisma.weatherAlert.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends WeatherAlertFindUniqueArgs>(args: SelectSubset<T, WeatherAlertFindUniqueArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one WeatherAlert that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {WeatherAlertFindUniqueOrThrowArgs} args - Arguments to find a WeatherAlert
     * @example
     * // Get one WeatherAlert
     * const weatherAlert = await prisma.weatherAlert.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends WeatherAlertFindUniqueOrThrowArgs>(args: SelectSubset<T, WeatherAlertFindUniqueOrThrowArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first WeatherAlert that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertFindFirstArgs} args - Arguments to find a WeatherAlert
     * @example
     * // Get one WeatherAlert
     * const weatherAlert = await prisma.weatherAlert.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends WeatherAlertFindFirstArgs>(args?: SelectSubset<T, WeatherAlertFindFirstArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first WeatherAlert that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertFindFirstOrThrowArgs} args - Arguments to find a WeatherAlert
     * @example
     * // Get one WeatherAlert
     * const weatherAlert = await prisma.weatherAlert.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends WeatherAlertFindFirstOrThrowArgs>(args?: SelectSubset<T, WeatherAlertFindFirstOrThrowArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more WeatherAlerts that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all WeatherAlerts
     * const weatherAlerts = await prisma.weatherAlert.findMany()
     * 
     * // Get first 10 WeatherAlerts
     * const weatherAlerts = await prisma.weatherAlert.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const weatherAlertWithIdOnly = await prisma.weatherAlert.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends WeatherAlertFindManyArgs>(args?: SelectSubset<T, WeatherAlertFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a WeatherAlert.
     * @param {WeatherAlertCreateArgs} args - Arguments to create a WeatherAlert.
     * @example
     * // Create one WeatherAlert
     * const WeatherAlert = await prisma.weatherAlert.create({
     *   data: {
     *     // ... data to create a WeatherAlert
     *   }
     * })
     * 
     */
    create<T extends WeatherAlertCreateArgs>(args: SelectSubset<T, WeatherAlertCreateArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many WeatherAlerts.
     * @param {WeatherAlertCreateManyArgs} args - Arguments to create many WeatherAlerts.
     * @example
     * // Create many WeatherAlerts
     * const weatherAlert = await prisma.weatherAlert.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends WeatherAlertCreateManyArgs>(args?: SelectSubset<T, WeatherAlertCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many WeatherAlerts and returns the data saved in the database.
     * @param {WeatherAlertCreateManyAndReturnArgs} args - Arguments to create many WeatherAlerts.
     * @example
     * // Create many WeatherAlerts
     * const weatherAlert = await prisma.weatherAlert.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many WeatherAlerts and only return the `id`
     * const weatherAlertWithIdOnly = await prisma.weatherAlert.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends WeatherAlertCreateManyAndReturnArgs>(args?: SelectSubset<T, WeatherAlertCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a WeatherAlert.
     * @param {WeatherAlertDeleteArgs} args - Arguments to delete one WeatherAlert.
     * @example
     * // Delete one WeatherAlert
     * const WeatherAlert = await prisma.weatherAlert.delete({
     *   where: {
     *     // ... filter to delete one WeatherAlert
     *   }
     * })
     * 
     */
    delete<T extends WeatherAlertDeleteArgs>(args: SelectSubset<T, WeatherAlertDeleteArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one WeatherAlert.
     * @param {WeatherAlertUpdateArgs} args - Arguments to update one WeatherAlert.
     * @example
     * // Update one WeatherAlert
     * const weatherAlert = await prisma.weatherAlert.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends WeatherAlertUpdateArgs>(args: SelectSubset<T, WeatherAlertUpdateArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more WeatherAlerts.
     * @param {WeatherAlertDeleteManyArgs} args - Arguments to filter WeatherAlerts to delete.
     * @example
     * // Delete a few WeatherAlerts
     * const { count } = await prisma.weatherAlert.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends WeatherAlertDeleteManyArgs>(args?: SelectSubset<T, WeatherAlertDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more WeatherAlerts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many WeatherAlerts
     * const weatherAlert = await prisma.weatherAlert.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends WeatherAlertUpdateManyArgs>(args: SelectSubset<T, WeatherAlertUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one WeatherAlert.
     * @param {WeatherAlertUpsertArgs} args - Arguments to update or create a WeatherAlert.
     * @example
     * // Update or create a WeatherAlert
     * const weatherAlert = await prisma.weatherAlert.upsert({
     *   create: {
     *     // ... data to create a WeatherAlert
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the WeatherAlert we want to update
     *   }
     * })
     */
    upsert<T extends WeatherAlertUpsertArgs>(args: SelectSubset<T, WeatherAlertUpsertArgs<ExtArgs>>): Prisma__WeatherAlertClient<$Result.GetResult<Prisma.$WeatherAlertPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of WeatherAlerts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertCountArgs} args - Arguments to filter WeatherAlerts to count.
     * @example
     * // Count the number of WeatherAlerts
     * const count = await prisma.weatherAlert.count({
     *   where: {
     *     // ... the filter for the WeatherAlerts we want to count
     *   }
     * })
    **/
    count<T extends WeatherAlertCountArgs>(
      args?: Subset<T, WeatherAlertCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], WeatherAlertCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a WeatherAlert.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends WeatherAlertAggregateArgs>(args: Subset<T, WeatherAlertAggregateArgs>): Prisma.PrismaPromise<GetWeatherAlertAggregateType<T>>

    /**
     * Group by WeatherAlert.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WeatherAlertGroupByArgs} args - Group by arguments.
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
      T extends WeatherAlertGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: WeatherAlertGroupByArgs['orderBy'] }
        : { orderBy?: WeatherAlertGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, WeatherAlertGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetWeatherAlertGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the WeatherAlert model
   */
  readonly fields: WeatherAlertFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for WeatherAlert.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__WeatherAlertClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
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
   * Fields of the WeatherAlert model
   */ 
  interface WeatherAlertFieldRefs {
    readonly id: FieldRef<"WeatherAlert", 'String'>
    readonly locationId: FieldRef<"WeatherAlert", 'String'>
    readonly tenantId: FieldRef<"WeatherAlert", 'String'>
    readonly alertType: FieldRef<"WeatherAlert", 'AlertType'>
    readonly severity: FieldRef<"WeatherAlert", 'AlertSeverity'>
    readonly headline: FieldRef<"WeatherAlert", 'String'>
    readonly description: FieldRef<"WeatherAlert", 'String'>
    readonly startTime: FieldRef<"WeatherAlert", 'DateTime'>
    readonly endTime: FieldRef<"WeatherAlert", 'DateTime'>
    readonly source: FieldRef<"WeatherAlert", 'String'>
    readonly createdAt: FieldRef<"WeatherAlert", 'DateTime'>
    readonly updatedAt: FieldRef<"WeatherAlert", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * WeatherAlert findUnique
   */
  export type WeatherAlertFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * Filter, which WeatherAlert to fetch.
     */
    where: WeatherAlertWhereUniqueInput
  }

  /**
   * WeatherAlert findUniqueOrThrow
   */
  export type WeatherAlertFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * Filter, which WeatherAlert to fetch.
     */
    where: WeatherAlertWhereUniqueInput
  }

  /**
   * WeatherAlert findFirst
   */
  export type WeatherAlertFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * Filter, which WeatherAlert to fetch.
     */
    where?: WeatherAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherAlerts to fetch.
     */
    orderBy?: WeatherAlertOrderByWithRelationInput | WeatherAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for WeatherAlerts.
     */
    cursor?: WeatherAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of WeatherAlerts.
     */
    distinct?: WeatherAlertScalarFieldEnum | WeatherAlertScalarFieldEnum[]
  }

  /**
   * WeatherAlert findFirstOrThrow
   */
  export type WeatherAlertFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * Filter, which WeatherAlert to fetch.
     */
    where?: WeatherAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherAlerts to fetch.
     */
    orderBy?: WeatherAlertOrderByWithRelationInput | WeatherAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for WeatherAlerts.
     */
    cursor?: WeatherAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of WeatherAlerts.
     */
    distinct?: WeatherAlertScalarFieldEnum | WeatherAlertScalarFieldEnum[]
  }

  /**
   * WeatherAlert findMany
   */
  export type WeatherAlertFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * Filter, which WeatherAlerts to fetch.
     */
    where?: WeatherAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of WeatherAlerts to fetch.
     */
    orderBy?: WeatherAlertOrderByWithRelationInput | WeatherAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing WeatherAlerts.
     */
    cursor?: WeatherAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` WeatherAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` WeatherAlerts.
     */
    skip?: number
    distinct?: WeatherAlertScalarFieldEnum | WeatherAlertScalarFieldEnum[]
  }

  /**
   * WeatherAlert create
   */
  export type WeatherAlertCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * The data needed to create a WeatherAlert.
     */
    data: XOR<WeatherAlertCreateInput, WeatherAlertUncheckedCreateInput>
  }

  /**
   * WeatherAlert createMany
   */
  export type WeatherAlertCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many WeatherAlerts.
     */
    data: WeatherAlertCreateManyInput | WeatherAlertCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * WeatherAlert createManyAndReturn
   */
  export type WeatherAlertCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many WeatherAlerts.
     */
    data: WeatherAlertCreateManyInput | WeatherAlertCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * WeatherAlert update
   */
  export type WeatherAlertUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * The data needed to update a WeatherAlert.
     */
    data: XOR<WeatherAlertUpdateInput, WeatherAlertUncheckedUpdateInput>
    /**
     * Choose, which WeatherAlert to update.
     */
    where: WeatherAlertWhereUniqueInput
  }

  /**
   * WeatherAlert updateMany
   */
  export type WeatherAlertUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update WeatherAlerts.
     */
    data: XOR<WeatherAlertUpdateManyMutationInput, WeatherAlertUncheckedUpdateManyInput>
    /**
     * Filter which WeatherAlerts to update
     */
    where?: WeatherAlertWhereInput
  }

  /**
   * WeatherAlert upsert
   */
  export type WeatherAlertUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * The filter to search for the WeatherAlert to update in case it exists.
     */
    where: WeatherAlertWhereUniqueInput
    /**
     * In case the WeatherAlert found by the `where` argument doesn't exist, create a new WeatherAlert with this data.
     */
    create: XOR<WeatherAlertCreateInput, WeatherAlertUncheckedCreateInput>
    /**
     * In case the WeatherAlert was found with the provided `where` argument, update it with this data.
     */
    update: XOR<WeatherAlertUpdateInput, WeatherAlertUncheckedUpdateInput>
  }

  /**
   * WeatherAlert delete
   */
  export type WeatherAlertDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
    /**
     * Filter which WeatherAlert to delete.
     */
    where: WeatherAlertWhereUniqueInput
  }

  /**
   * WeatherAlert deleteMany
   */
  export type WeatherAlertDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which WeatherAlerts to delete
     */
    where?: WeatherAlertWhereInput
  }

  /**
   * WeatherAlert without action
   */
  export type WeatherAlertDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WeatherAlert
     */
    select?: WeatherAlertSelect<ExtArgs> | null
  }


  /**
   * Model LocationConfig
   */

  export type AggregateLocationConfig = {
    _count: LocationConfigCountAggregateOutputType | null
    _avg: LocationConfigAvgAggregateOutputType | null
    _sum: LocationConfigSumAggregateOutputType | null
    _min: LocationConfigMinAggregateOutputType | null
    _max: LocationConfigMaxAggregateOutputType | null
  }

  export type LocationConfigAvgAggregateOutputType = {
    latitude: number | null
    longitude: number | null
    fetchInterval: number | null
  }

  export type LocationConfigSumAggregateOutputType = {
    latitude: number | null
    longitude: number | null
    fetchInterval: number | null
  }

  export type LocationConfigMinAggregateOutputType = {
    id: string | null
    tenantId: string | null
    name: string | null
    latitude: number | null
    longitude: number | null
    timezone: string | null
    isActive: boolean | null
    fetchInterval: number | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type LocationConfigMaxAggregateOutputType = {
    id: string | null
    tenantId: string | null
    name: string | null
    latitude: number | null
    longitude: number | null
    timezone: string | null
    isActive: boolean | null
    fetchInterval: number | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type LocationConfigCountAggregateOutputType = {
    id: number
    tenantId: number
    name: number
    latitude: number
    longitude: number
    timezone: number
    isActive: number
    fetchInterval: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type LocationConfigAvgAggregateInputType = {
    latitude?: true
    longitude?: true
    fetchInterval?: true
  }

  export type LocationConfigSumAggregateInputType = {
    latitude?: true
    longitude?: true
    fetchInterval?: true
  }

  export type LocationConfigMinAggregateInputType = {
    id?: true
    tenantId?: true
    name?: true
    latitude?: true
    longitude?: true
    timezone?: true
    isActive?: true
    fetchInterval?: true
    createdAt?: true
    updatedAt?: true
  }

  export type LocationConfigMaxAggregateInputType = {
    id?: true
    tenantId?: true
    name?: true
    latitude?: true
    longitude?: true
    timezone?: true
    isActive?: true
    fetchInterval?: true
    createdAt?: true
    updatedAt?: true
  }

  export type LocationConfigCountAggregateInputType = {
    id?: true
    tenantId?: true
    name?: true
    latitude?: true
    longitude?: true
    timezone?: true
    isActive?: true
    fetchInterval?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type LocationConfigAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which LocationConfig to aggregate.
     */
    where?: LocationConfigWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of LocationConfigs to fetch.
     */
    orderBy?: LocationConfigOrderByWithRelationInput | LocationConfigOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: LocationConfigWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` LocationConfigs from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` LocationConfigs.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned LocationConfigs
    **/
    _count?: true | LocationConfigCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: LocationConfigAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: LocationConfigSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: LocationConfigMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: LocationConfigMaxAggregateInputType
  }

  export type GetLocationConfigAggregateType<T extends LocationConfigAggregateArgs> = {
        [P in keyof T & keyof AggregateLocationConfig]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateLocationConfig[P]>
      : GetScalarType<T[P], AggregateLocationConfig[P]>
  }




  export type LocationConfigGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: LocationConfigWhereInput
    orderBy?: LocationConfigOrderByWithAggregationInput | LocationConfigOrderByWithAggregationInput[]
    by: LocationConfigScalarFieldEnum[] | LocationConfigScalarFieldEnum
    having?: LocationConfigScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: LocationConfigCountAggregateInputType | true
    _avg?: LocationConfigAvgAggregateInputType
    _sum?: LocationConfigSumAggregateInputType
    _min?: LocationConfigMinAggregateInputType
    _max?: LocationConfigMaxAggregateInputType
  }

  export type LocationConfigGroupByOutputType = {
    id: string
    tenantId: string
    name: string
    latitude: number
    longitude: number
    timezone: string
    isActive: boolean
    fetchInterval: number
    createdAt: Date
    updatedAt: Date
    _count: LocationConfigCountAggregateOutputType | null
    _avg: LocationConfigAvgAggregateOutputType | null
    _sum: LocationConfigSumAggregateOutputType | null
    _min: LocationConfigMinAggregateOutputType | null
    _max: LocationConfigMaxAggregateOutputType | null
  }

  type GetLocationConfigGroupByPayload<T extends LocationConfigGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<LocationConfigGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof LocationConfigGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], LocationConfigGroupByOutputType[P]>
            : GetScalarType<T[P], LocationConfigGroupByOutputType[P]>
        }
      >
    >


  export type LocationConfigSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    name?: boolean
    latitude?: boolean
    longitude?: boolean
    timezone?: boolean
    isActive?: boolean
    fetchInterval?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["locationConfig"]>

  export type LocationConfigSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    name?: boolean
    latitude?: boolean
    longitude?: boolean
    timezone?: boolean
    isActive?: boolean
    fetchInterval?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["locationConfig"]>

  export type LocationConfigSelectScalar = {
    id?: boolean
    tenantId?: boolean
    name?: boolean
    latitude?: boolean
    longitude?: boolean
    timezone?: boolean
    isActive?: boolean
    fetchInterval?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }


  export type $LocationConfigPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "LocationConfig"
    objects: {}
    scalars: $Extensions.GetPayloadResult<{
      id: string
      tenantId: string
      name: string
      latitude: number
      longitude: number
      timezone: string
      isActive: boolean
      fetchInterval: number
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["locationConfig"]>
    composites: {}
  }

  type LocationConfigGetPayload<S extends boolean | null | undefined | LocationConfigDefaultArgs> = $Result.GetResult<Prisma.$LocationConfigPayload, S>

  type LocationConfigCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<LocationConfigFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: LocationConfigCountAggregateInputType | true
    }

  export interface LocationConfigDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['LocationConfig'], meta: { name: 'LocationConfig' } }
    /**
     * Find zero or one LocationConfig that matches the filter.
     * @param {LocationConfigFindUniqueArgs} args - Arguments to find a LocationConfig
     * @example
     * // Get one LocationConfig
     * const locationConfig = await prisma.locationConfig.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends LocationConfigFindUniqueArgs>(args: SelectSubset<T, LocationConfigFindUniqueArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one LocationConfig that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {LocationConfigFindUniqueOrThrowArgs} args - Arguments to find a LocationConfig
     * @example
     * // Get one LocationConfig
     * const locationConfig = await prisma.locationConfig.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends LocationConfigFindUniqueOrThrowArgs>(args: SelectSubset<T, LocationConfigFindUniqueOrThrowArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first LocationConfig that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigFindFirstArgs} args - Arguments to find a LocationConfig
     * @example
     * // Get one LocationConfig
     * const locationConfig = await prisma.locationConfig.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends LocationConfigFindFirstArgs>(args?: SelectSubset<T, LocationConfigFindFirstArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first LocationConfig that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigFindFirstOrThrowArgs} args - Arguments to find a LocationConfig
     * @example
     * // Get one LocationConfig
     * const locationConfig = await prisma.locationConfig.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends LocationConfigFindFirstOrThrowArgs>(args?: SelectSubset<T, LocationConfigFindFirstOrThrowArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more LocationConfigs that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all LocationConfigs
     * const locationConfigs = await prisma.locationConfig.findMany()
     * 
     * // Get first 10 LocationConfigs
     * const locationConfigs = await prisma.locationConfig.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const locationConfigWithIdOnly = await prisma.locationConfig.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends LocationConfigFindManyArgs>(args?: SelectSubset<T, LocationConfigFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a LocationConfig.
     * @param {LocationConfigCreateArgs} args - Arguments to create a LocationConfig.
     * @example
     * // Create one LocationConfig
     * const LocationConfig = await prisma.locationConfig.create({
     *   data: {
     *     // ... data to create a LocationConfig
     *   }
     * })
     * 
     */
    create<T extends LocationConfigCreateArgs>(args: SelectSubset<T, LocationConfigCreateArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many LocationConfigs.
     * @param {LocationConfigCreateManyArgs} args - Arguments to create many LocationConfigs.
     * @example
     * // Create many LocationConfigs
     * const locationConfig = await prisma.locationConfig.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends LocationConfigCreateManyArgs>(args?: SelectSubset<T, LocationConfigCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many LocationConfigs and returns the data saved in the database.
     * @param {LocationConfigCreateManyAndReturnArgs} args - Arguments to create many LocationConfigs.
     * @example
     * // Create many LocationConfigs
     * const locationConfig = await prisma.locationConfig.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many LocationConfigs and only return the `id`
     * const locationConfigWithIdOnly = await prisma.locationConfig.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends LocationConfigCreateManyAndReturnArgs>(args?: SelectSubset<T, LocationConfigCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a LocationConfig.
     * @param {LocationConfigDeleteArgs} args - Arguments to delete one LocationConfig.
     * @example
     * // Delete one LocationConfig
     * const LocationConfig = await prisma.locationConfig.delete({
     *   where: {
     *     // ... filter to delete one LocationConfig
     *   }
     * })
     * 
     */
    delete<T extends LocationConfigDeleteArgs>(args: SelectSubset<T, LocationConfigDeleteArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one LocationConfig.
     * @param {LocationConfigUpdateArgs} args - Arguments to update one LocationConfig.
     * @example
     * // Update one LocationConfig
     * const locationConfig = await prisma.locationConfig.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends LocationConfigUpdateArgs>(args: SelectSubset<T, LocationConfigUpdateArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more LocationConfigs.
     * @param {LocationConfigDeleteManyArgs} args - Arguments to filter LocationConfigs to delete.
     * @example
     * // Delete a few LocationConfigs
     * const { count } = await prisma.locationConfig.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends LocationConfigDeleteManyArgs>(args?: SelectSubset<T, LocationConfigDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more LocationConfigs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many LocationConfigs
     * const locationConfig = await prisma.locationConfig.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends LocationConfigUpdateManyArgs>(args: SelectSubset<T, LocationConfigUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one LocationConfig.
     * @param {LocationConfigUpsertArgs} args - Arguments to update or create a LocationConfig.
     * @example
     * // Update or create a LocationConfig
     * const locationConfig = await prisma.locationConfig.upsert({
     *   create: {
     *     // ... data to create a LocationConfig
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the LocationConfig we want to update
     *   }
     * })
     */
    upsert<T extends LocationConfigUpsertArgs>(args: SelectSubset<T, LocationConfigUpsertArgs<ExtArgs>>): Prisma__LocationConfigClient<$Result.GetResult<Prisma.$LocationConfigPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of LocationConfigs.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigCountArgs} args - Arguments to filter LocationConfigs to count.
     * @example
     * // Count the number of LocationConfigs
     * const count = await prisma.locationConfig.count({
     *   where: {
     *     // ... the filter for the LocationConfigs we want to count
     *   }
     * })
    **/
    count<T extends LocationConfigCountArgs>(
      args?: Subset<T, LocationConfigCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], LocationConfigCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a LocationConfig.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends LocationConfigAggregateArgs>(args: Subset<T, LocationConfigAggregateArgs>): Prisma.PrismaPromise<GetLocationConfigAggregateType<T>>

    /**
     * Group by LocationConfig.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {LocationConfigGroupByArgs} args - Group by arguments.
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
      T extends LocationConfigGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: LocationConfigGroupByArgs['orderBy'] }
        : { orderBy?: LocationConfigGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, LocationConfigGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetLocationConfigGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the LocationConfig model
   */
  readonly fields: LocationConfigFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for LocationConfig.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__LocationConfigClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
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
   * Fields of the LocationConfig model
   */ 
  interface LocationConfigFieldRefs {
    readonly id: FieldRef<"LocationConfig", 'String'>
    readonly tenantId: FieldRef<"LocationConfig", 'String'>
    readonly name: FieldRef<"LocationConfig", 'String'>
    readonly latitude: FieldRef<"LocationConfig", 'Float'>
    readonly longitude: FieldRef<"LocationConfig", 'Float'>
    readonly timezone: FieldRef<"LocationConfig", 'String'>
    readonly isActive: FieldRef<"LocationConfig", 'Boolean'>
    readonly fetchInterval: FieldRef<"LocationConfig", 'Int'>
    readonly createdAt: FieldRef<"LocationConfig", 'DateTime'>
    readonly updatedAt: FieldRef<"LocationConfig", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * LocationConfig findUnique
   */
  export type LocationConfigFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * Filter, which LocationConfig to fetch.
     */
    where: LocationConfigWhereUniqueInput
  }

  /**
   * LocationConfig findUniqueOrThrow
   */
  export type LocationConfigFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * Filter, which LocationConfig to fetch.
     */
    where: LocationConfigWhereUniqueInput
  }

  /**
   * LocationConfig findFirst
   */
  export type LocationConfigFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * Filter, which LocationConfig to fetch.
     */
    where?: LocationConfigWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of LocationConfigs to fetch.
     */
    orderBy?: LocationConfigOrderByWithRelationInput | LocationConfigOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for LocationConfigs.
     */
    cursor?: LocationConfigWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` LocationConfigs from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` LocationConfigs.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of LocationConfigs.
     */
    distinct?: LocationConfigScalarFieldEnum | LocationConfigScalarFieldEnum[]
  }

  /**
   * LocationConfig findFirstOrThrow
   */
  export type LocationConfigFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * Filter, which LocationConfig to fetch.
     */
    where?: LocationConfigWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of LocationConfigs to fetch.
     */
    orderBy?: LocationConfigOrderByWithRelationInput | LocationConfigOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for LocationConfigs.
     */
    cursor?: LocationConfigWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` LocationConfigs from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` LocationConfigs.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of LocationConfigs.
     */
    distinct?: LocationConfigScalarFieldEnum | LocationConfigScalarFieldEnum[]
  }

  /**
   * LocationConfig findMany
   */
  export type LocationConfigFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * Filter, which LocationConfigs to fetch.
     */
    where?: LocationConfigWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of LocationConfigs to fetch.
     */
    orderBy?: LocationConfigOrderByWithRelationInput | LocationConfigOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing LocationConfigs.
     */
    cursor?: LocationConfigWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` LocationConfigs from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` LocationConfigs.
     */
    skip?: number
    distinct?: LocationConfigScalarFieldEnum | LocationConfigScalarFieldEnum[]
  }

  /**
   * LocationConfig create
   */
  export type LocationConfigCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * The data needed to create a LocationConfig.
     */
    data: XOR<LocationConfigCreateInput, LocationConfigUncheckedCreateInput>
  }

  /**
   * LocationConfig createMany
   */
  export type LocationConfigCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many LocationConfigs.
     */
    data: LocationConfigCreateManyInput | LocationConfigCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * LocationConfig createManyAndReturn
   */
  export type LocationConfigCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many LocationConfigs.
     */
    data: LocationConfigCreateManyInput | LocationConfigCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * LocationConfig update
   */
  export type LocationConfigUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * The data needed to update a LocationConfig.
     */
    data: XOR<LocationConfigUpdateInput, LocationConfigUncheckedUpdateInput>
    /**
     * Choose, which LocationConfig to update.
     */
    where: LocationConfigWhereUniqueInput
  }

  /**
   * LocationConfig updateMany
   */
  export type LocationConfigUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update LocationConfigs.
     */
    data: XOR<LocationConfigUpdateManyMutationInput, LocationConfigUncheckedUpdateManyInput>
    /**
     * Filter which LocationConfigs to update
     */
    where?: LocationConfigWhereInput
  }

  /**
   * LocationConfig upsert
   */
  export type LocationConfigUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * The filter to search for the LocationConfig to update in case it exists.
     */
    where: LocationConfigWhereUniqueInput
    /**
     * In case the LocationConfig found by the `where` argument doesn't exist, create a new LocationConfig with this data.
     */
    create: XOR<LocationConfigCreateInput, LocationConfigUncheckedCreateInput>
    /**
     * In case the LocationConfig was found with the provided `where` argument, update it with this data.
     */
    update: XOR<LocationConfigUpdateInput, LocationConfigUncheckedUpdateInput>
  }

  /**
   * LocationConfig delete
   */
  export type LocationConfigDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
    /**
     * Filter which LocationConfig to delete.
     */
    where: LocationConfigWhereUniqueInput
  }

  /**
   * LocationConfig deleteMany
   */
  export type LocationConfigDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which LocationConfigs to delete
     */
    where?: LocationConfigWhereInput
  }

  /**
   * LocationConfig without action
   */
  export type LocationConfigDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the LocationConfig
     */
    select?: LocationConfigSelect<ExtArgs> | null
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


  export const WeatherObservationScalarFieldEnum: {
    id: 'id',
    locationId: 'locationId',
    tenantId: 'tenantId',
    latitude: 'latitude',
    longitude: 'longitude',
    timestamp: 'timestamp',
    temperature: 'temperature',
    humidity: 'humidity',
    pressure: 'pressure',
    windSpeed: 'windSpeed',
    windDirection: 'windDirection',
    rainfall: 'rainfall',
    uvIndex: 'uvIndex',
    cloudCover: 'cloudCover',
    visibility: 'visibility',
    source: 'source',
    rawData: 'rawData',
    createdAt: 'createdAt'
  };

  export type WeatherObservationScalarFieldEnum = (typeof WeatherObservationScalarFieldEnum)[keyof typeof WeatherObservationScalarFieldEnum]


  export const WeatherForecastScalarFieldEnum: {
    id: 'id',
    locationId: 'locationId',
    tenantId: 'tenantId',
    forecastFor: 'forecastFor',
    fetchedAt: 'fetchedAt',
    provider: 'provider',
    hourlyData: 'hourlyData',
    dailyData: 'dailyData',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type WeatherForecastScalarFieldEnum = (typeof WeatherForecastScalarFieldEnum)[keyof typeof WeatherForecastScalarFieldEnum]


  export const WeatherAlertScalarFieldEnum: {
    id: 'id',
    locationId: 'locationId',
    tenantId: 'tenantId',
    alertType: 'alertType',
    severity: 'severity',
    headline: 'headline',
    description: 'description',
    startTime: 'startTime',
    endTime: 'endTime',
    source: 'source',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type WeatherAlertScalarFieldEnum = (typeof WeatherAlertScalarFieldEnum)[keyof typeof WeatherAlertScalarFieldEnum]


  export const LocationConfigScalarFieldEnum: {
    id: 'id',
    tenantId: 'tenantId',
    name: 'name',
    latitude: 'latitude',
    longitude: 'longitude',
    timezone: 'timezone',
    isActive: 'isActive',
    fetchInterval: 'fetchInterval',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type LocationConfigScalarFieldEnum = (typeof LocationConfigScalarFieldEnum)[keyof typeof LocationConfigScalarFieldEnum]


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


  export const JsonNullValueInput: {
    JsonNull: typeof JsonNull
  };

  export type JsonNullValueInput = (typeof JsonNullValueInput)[keyof typeof JsonNullValueInput]


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
   * Reference to a field of type 'Float'
   */
  export type FloatFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Float'>
    


  /**
   * Reference to a field of type 'Float[]'
   */
  export type ListFloatFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Float[]'>
    


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
   * Reference to a field of type 'AlertType'
   */
  export type EnumAlertTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertType'>
    


  /**
   * Reference to a field of type 'AlertType[]'
   */
  export type ListEnumAlertTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertType[]'>
    


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


  export type WeatherObservationWhereInput = {
    AND?: WeatherObservationWhereInput | WeatherObservationWhereInput[]
    OR?: WeatherObservationWhereInput[]
    NOT?: WeatherObservationWhereInput | WeatherObservationWhereInput[]
    id?: StringFilter<"WeatherObservation"> | string
    locationId?: StringFilter<"WeatherObservation"> | string
    tenantId?: StringNullableFilter<"WeatherObservation"> | string | null
    latitude?: FloatFilter<"WeatherObservation"> | number
    longitude?: FloatFilter<"WeatherObservation"> | number
    timestamp?: DateTimeFilter<"WeatherObservation"> | Date | string
    temperature?: FloatFilter<"WeatherObservation"> | number
    humidity?: FloatFilter<"WeatherObservation"> | number
    pressure?: FloatFilter<"WeatherObservation"> | number
    windSpeed?: FloatFilter<"WeatherObservation"> | number
    windDirection?: FloatFilter<"WeatherObservation"> | number
    rainfall?: FloatNullableFilter<"WeatherObservation"> | number | null
    uvIndex?: FloatNullableFilter<"WeatherObservation"> | number | null
    cloudCover?: FloatNullableFilter<"WeatherObservation"> | number | null
    visibility?: FloatNullableFilter<"WeatherObservation"> | number | null
    source?: StringFilter<"WeatherObservation"> | string
    rawData?: JsonNullableFilter<"WeatherObservation">
    createdAt?: DateTimeFilter<"WeatherObservation"> | Date | string
  }

  export type WeatherObservationOrderByWithRelationInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrderInput | SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timestamp?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrderInput | SortOrder
    uvIndex?: SortOrderInput | SortOrder
    cloudCover?: SortOrderInput | SortOrder
    visibility?: SortOrderInput | SortOrder
    source?: SortOrder
    rawData?: SortOrderInput | SortOrder
    createdAt?: SortOrder
  }

  export type WeatherObservationWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: WeatherObservationWhereInput | WeatherObservationWhereInput[]
    OR?: WeatherObservationWhereInput[]
    NOT?: WeatherObservationWhereInput | WeatherObservationWhereInput[]
    locationId?: StringFilter<"WeatherObservation"> | string
    tenantId?: StringNullableFilter<"WeatherObservation"> | string | null
    latitude?: FloatFilter<"WeatherObservation"> | number
    longitude?: FloatFilter<"WeatherObservation"> | number
    timestamp?: DateTimeFilter<"WeatherObservation"> | Date | string
    temperature?: FloatFilter<"WeatherObservation"> | number
    humidity?: FloatFilter<"WeatherObservation"> | number
    pressure?: FloatFilter<"WeatherObservation"> | number
    windSpeed?: FloatFilter<"WeatherObservation"> | number
    windDirection?: FloatFilter<"WeatherObservation"> | number
    rainfall?: FloatNullableFilter<"WeatherObservation"> | number | null
    uvIndex?: FloatNullableFilter<"WeatherObservation"> | number | null
    cloudCover?: FloatNullableFilter<"WeatherObservation"> | number | null
    visibility?: FloatNullableFilter<"WeatherObservation"> | number | null
    source?: StringFilter<"WeatherObservation"> | string
    rawData?: JsonNullableFilter<"WeatherObservation">
    createdAt?: DateTimeFilter<"WeatherObservation"> | Date | string
  }, "id">

  export type WeatherObservationOrderByWithAggregationInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrderInput | SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timestamp?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrderInput | SortOrder
    uvIndex?: SortOrderInput | SortOrder
    cloudCover?: SortOrderInput | SortOrder
    visibility?: SortOrderInput | SortOrder
    source?: SortOrder
    rawData?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    _count?: WeatherObservationCountOrderByAggregateInput
    _avg?: WeatherObservationAvgOrderByAggregateInput
    _max?: WeatherObservationMaxOrderByAggregateInput
    _min?: WeatherObservationMinOrderByAggregateInput
    _sum?: WeatherObservationSumOrderByAggregateInput
  }

  export type WeatherObservationScalarWhereWithAggregatesInput = {
    AND?: WeatherObservationScalarWhereWithAggregatesInput | WeatherObservationScalarWhereWithAggregatesInput[]
    OR?: WeatherObservationScalarWhereWithAggregatesInput[]
    NOT?: WeatherObservationScalarWhereWithAggregatesInput | WeatherObservationScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"WeatherObservation"> | string
    locationId?: StringWithAggregatesFilter<"WeatherObservation"> | string
    tenantId?: StringNullableWithAggregatesFilter<"WeatherObservation"> | string | null
    latitude?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    longitude?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    timestamp?: DateTimeWithAggregatesFilter<"WeatherObservation"> | Date | string
    temperature?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    humidity?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    pressure?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    windSpeed?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    windDirection?: FloatWithAggregatesFilter<"WeatherObservation"> | number
    rainfall?: FloatNullableWithAggregatesFilter<"WeatherObservation"> | number | null
    uvIndex?: FloatNullableWithAggregatesFilter<"WeatherObservation"> | number | null
    cloudCover?: FloatNullableWithAggregatesFilter<"WeatherObservation"> | number | null
    visibility?: FloatNullableWithAggregatesFilter<"WeatherObservation"> | number | null
    source?: StringWithAggregatesFilter<"WeatherObservation"> | string
    rawData?: JsonNullableWithAggregatesFilter<"WeatherObservation">
    createdAt?: DateTimeWithAggregatesFilter<"WeatherObservation"> | Date | string
  }

  export type WeatherForecastWhereInput = {
    AND?: WeatherForecastWhereInput | WeatherForecastWhereInput[]
    OR?: WeatherForecastWhereInput[]
    NOT?: WeatherForecastWhereInput | WeatherForecastWhereInput[]
    id?: StringFilter<"WeatherForecast"> | string
    locationId?: StringFilter<"WeatherForecast"> | string
    tenantId?: StringNullableFilter<"WeatherForecast"> | string | null
    forecastFor?: DateTimeFilter<"WeatherForecast"> | Date | string
    fetchedAt?: DateTimeFilter<"WeatherForecast"> | Date | string
    provider?: StringFilter<"WeatherForecast"> | string
    hourlyData?: JsonFilter<"WeatherForecast">
    dailyData?: JsonFilter<"WeatherForecast">
    createdAt?: DateTimeFilter<"WeatherForecast"> | Date | string
    updatedAt?: DateTimeFilter<"WeatherForecast"> | Date | string
  }

  export type WeatherForecastOrderByWithRelationInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrderInput | SortOrder
    forecastFor?: SortOrder
    fetchedAt?: SortOrder
    provider?: SortOrder
    hourlyData?: SortOrder
    dailyData?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WeatherForecastWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    locationId_forecastFor_provider?: WeatherForecastLocationIdForecastForProviderCompoundUniqueInput
    AND?: WeatherForecastWhereInput | WeatherForecastWhereInput[]
    OR?: WeatherForecastWhereInput[]
    NOT?: WeatherForecastWhereInput | WeatherForecastWhereInput[]
    locationId?: StringFilter<"WeatherForecast"> | string
    tenantId?: StringNullableFilter<"WeatherForecast"> | string | null
    forecastFor?: DateTimeFilter<"WeatherForecast"> | Date | string
    fetchedAt?: DateTimeFilter<"WeatherForecast"> | Date | string
    provider?: StringFilter<"WeatherForecast"> | string
    hourlyData?: JsonFilter<"WeatherForecast">
    dailyData?: JsonFilter<"WeatherForecast">
    createdAt?: DateTimeFilter<"WeatherForecast"> | Date | string
    updatedAt?: DateTimeFilter<"WeatherForecast"> | Date | string
  }, "id" | "locationId_forecastFor_provider">

  export type WeatherForecastOrderByWithAggregationInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrderInput | SortOrder
    forecastFor?: SortOrder
    fetchedAt?: SortOrder
    provider?: SortOrder
    hourlyData?: SortOrder
    dailyData?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: WeatherForecastCountOrderByAggregateInput
    _max?: WeatherForecastMaxOrderByAggregateInput
    _min?: WeatherForecastMinOrderByAggregateInput
  }

  export type WeatherForecastScalarWhereWithAggregatesInput = {
    AND?: WeatherForecastScalarWhereWithAggregatesInput | WeatherForecastScalarWhereWithAggregatesInput[]
    OR?: WeatherForecastScalarWhereWithAggregatesInput[]
    NOT?: WeatherForecastScalarWhereWithAggregatesInput | WeatherForecastScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"WeatherForecast"> | string
    locationId?: StringWithAggregatesFilter<"WeatherForecast"> | string
    tenantId?: StringNullableWithAggregatesFilter<"WeatherForecast"> | string | null
    forecastFor?: DateTimeWithAggregatesFilter<"WeatherForecast"> | Date | string
    fetchedAt?: DateTimeWithAggregatesFilter<"WeatherForecast"> | Date | string
    provider?: StringWithAggregatesFilter<"WeatherForecast"> | string
    hourlyData?: JsonWithAggregatesFilter<"WeatherForecast">
    dailyData?: JsonWithAggregatesFilter<"WeatherForecast">
    createdAt?: DateTimeWithAggregatesFilter<"WeatherForecast"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"WeatherForecast"> | Date | string
  }

  export type WeatherAlertWhereInput = {
    AND?: WeatherAlertWhereInput | WeatherAlertWhereInput[]
    OR?: WeatherAlertWhereInput[]
    NOT?: WeatherAlertWhereInput | WeatherAlertWhereInput[]
    id?: StringFilter<"WeatherAlert"> | string
    locationId?: StringFilter<"WeatherAlert"> | string
    tenantId?: StringNullableFilter<"WeatherAlert"> | string | null
    alertType?: EnumAlertTypeFilter<"WeatherAlert"> | $Enums.AlertType
    severity?: EnumAlertSeverityFilter<"WeatherAlert"> | $Enums.AlertSeverity
    headline?: StringFilter<"WeatherAlert"> | string
    description?: StringFilter<"WeatherAlert"> | string
    startTime?: DateTimeFilter<"WeatherAlert"> | Date | string
    endTime?: DateTimeFilter<"WeatherAlert"> | Date | string
    source?: StringFilter<"WeatherAlert"> | string
    createdAt?: DateTimeFilter<"WeatherAlert"> | Date | string
    updatedAt?: DateTimeFilter<"WeatherAlert"> | Date | string
  }

  export type WeatherAlertOrderByWithRelationInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrderInput | SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    headline?: SortOrder
    description?: SortOrder
    startTime?: SortOrder
    endTime?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WeatherAlertWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: WeatherAlertWhereInput | WeatherAlertWhereInput[]
    OR?: WeatherAlertWhereInput[]
    NOT?: WeatherAlertWhereInput | WeatherAlertWhereInput[]
    locationId?: StringFilter<"WeatherAlert"> | string
    tenantId?: StringNullableFilter<"WeatherAlert"> | string | null
    alertType?: EnumAlertTypeFilter<"WeatherAlert"> | $Enums.AlertType
    severity?: EnumAlertSeverityFilter<"WeatherAlert"> | $Enums.AlertSeverity
    headline?: StringFilter<"WeatherAlert"> | string
    description?: StringFilter<"WeatherAlert"> | string
    startTime?: DateTimeFilter<"WeatherAlert"> | Date | string
    endTime?: DateTimeFilter<"WeatherAlert"> | Date | string
    source?: StringFilter<"WeatherAlert"> | string
    createdAt?: DateTimeFilter<"WeatherAlert"> | Date | string
    updatedAt?: DateTimeFilter<"WeatherAlert"> | Date | string
  }, "id">

  export type WeatherAlertOrderByWithAggregationInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrderInput | SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    headline?: SortOrder
    description?: SortOrder
    startTime?: SortOrder
    endTime?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: WeatherAlertCountOrderByAggregateInput
    _max?: WeatherAlertMaxOrderByAggregateInput
    _min?: WeatherAlertMinOrderByAggregateInput
  }

  export type WeatherAlertScalarWhereWithAggregatesInput = {
    AND?: WeatherAlertScalarWhereWithAggregatesInput | WeatherAlertScalarWhereWithAggregatesInput[]
    OR?: WeatherAlertScalarWhereWithAggregatesInput[]
    NOT?: WeatherAlertScalarWhereWithAggregatesInput | WeatherAlertScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"WeatherAlert"> | string
    locationId?: StringWithAggregatesFilter<"WeatherAlert"> | string
    tenantId?: StringNullableWithAggregatesFilter<"WeatherAlert"> | string | null
    alertType?: EnumAlertTypeWithAggregatesFilter<"WeatherAlert"> | $Enums.AlertType
    severity?: EnumAlertSeverityWithAggregatesFilter<"WeatherAlert"> | $Enums.AlertSeverity
    headline?: StringWithAggregatesFilter<"WeatherAlert"> | string
    description?: StringWithAggregatesFilter<"WeatherAlert"> | string
    startTime?: DateTimeWithAggregatesFilter<"WeatherAlert"> | Date | string
    endTime?: DateTimeWithAggregatesFilter<"WeatherAlert"> | Date | string
    source?: StringWithAggregatesFilter<"WeatherAlert"> | string
    createdAt?: DateTimeWithAggregatesFilter<"WeatherAlert"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"WeatherAlert"> | Date | string
  }

  export type LocationConfigWhereInput = {
    AND?: LocationConfigWhereInput | LocationConfigWhereInput[]
    OR?: LocationConfigWhereInput[]
    NOT?: LocationConfigWhereInput | LocationConfigWhereInput[]
    id?: StringFilter<"LocationConfig"> | string
    tenantId?: StringFilter<"LocationConfig"> | string
    name?: StringFilter<"LocationConfig"> | string
    latitude?: FloatFilter<"LocationConfig"> | number
    longitude?: FloatFilter<"LocationConfig"> | number
    timezone?: StringFilter<"LocationConfig"> | string
    isActive?: BoolFilter<"LocationConfig"> | boolean
    fetchInterval?: IntFilter<"LocationConfig"> | number
    createdAt?: DateTimeFilter<"LocationConfig"> | Date | string
    updatedAt?: DateTimeFilter<"LocationConfig"> | Date | string
  }

  export type LocationConfigOrderByWithRelationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timezone?: SortOrder
    isActive?: SortOrder
    fetchInterval?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type LocationConfigWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    tenantId_latitude_longitude?: LocationConfigTenantIdLatitudeLongitudeCompoundUniqueInput
    AND?: LocationConfigWhereInput | LocationConfigWhereInput[]
    OR?: LocationConfigWhereInput[]
    NOT?: LocationConfigWhereInput | LocationConfigWhereInput[]
    tenantId?: StringFilter<"LocationConfig"> | string
    name?: StringFilter<"LocationConfig"> | string
    latitude?: FloatFilter<"LocationConfig"> | number
    longitude?: FloatFilter<"LocationConfig"> | number
    timezone?: StringFilter<"LocationConfig"> | string
    isActive?: BoolFilter<"LocationConfig"> | boolean
    fetchInterval?: IntFilter<"LocationConfig"> | number
    createdAt?: DateTimeFilter<"LocationConfig"> | Date | string
    updatedAt?: DateTimeFilter<"LocationConfig"> | Date | string
  }, "id" | "tenantId_latitude_longitude">

  export type LocationConfigOrderByWithAggregationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timezone?: SortOrder
    isActive?: SortOrder
    fetchInterval?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: LocationConfigCountOrderByAggregateInput
    _avg?: LocationConfigAvgOrderByAggregateInput
    _max?: LocationConfigMaxOrderByAggregateInput
    _min?: LocationConfigMinOrderByAggregateInput
    _sum?: LocationConfigSumOrderByAggregateInput
  }

  export type LocationConfigScalarWhereWithAggregatesInput = {
    AND?: LocationConfigScalarWhereWithAggregatesInput | LocationConfigScalarWhereWithAggregatesInput[]
    OR?: LocationConfigScalarWhereWithAggregatesInput[]
    NOT?: LocationConfigScalarWhereWithAggregatesInput | LocationConfigScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"LocationConfig"> | string
    tenantId?: StringWithAggregatesFilter<"LocationConfig"> | string
    name?: StringWithAggregatesFilter<"LocationConfig"> | string
    latitude?: FloatWithAggregatesFilter<"LocationConfig"> | number
    longitude?: FloatWithAggregatesFilter<"LocationConfig"> | number
    timezone?: StringWithAggregatesFilter<"LocationConfig"> | string
    isActive?: BoolWithAggregatesFilter<"LocationConfig"> | boolean
    fetchInterval?: IntWithAggregatesFilter<"LocationConfig"> | number
    createdAt?: DateTimeWithAggregatesFilter<"LocationConfig"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"LocationConfig"> | Date | string
  }

  export type WeatherObservationCreateInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    latitude: number
    longitude: number
    timestamp: Date | string
    temperature: number
    humidity: number
    pressure: number
    windSpeed: number
    windDirection: number
    rainfall?: number | null
    uvIndex?: number | null
    cloudCover?: number | null
    visibility?: number | null
    source: string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type WeatherObservationUncheckedCreateInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    latitude: number
    longitude: number
    timestamp: Date | string
    temperature: number
    humidity: number
    pressure: number
    windSpeed: number
    windDirection: number
    rainfall?: number | null
    uvIndex?: number | null
    cloudCover?: number | null
    visibility?: number | null
    source: string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type WeatherObservationUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    temperature?: FloatFieldUpdateOperationsInput | number
    humidity?: FloatFieldUpdateOperationsInput | number
    pressure?: FloatFieldUpdateOperationsInput | number
    windSpeed?: FloatFieldUpdateOperationsInput | number
    windDirection?: FloatFieldUpdateOperationsInput | number
    rainfall?: NullableFloatFieldUpdateOperationsInput | number | null
    uvIndex?: NullableFloatFieldUpdateOperationsInput | number | null
    cloudCover?: NullableFloatFieldUpdateOperationsInput | number | null
    visibility?: NullableFloatFieldUpdateOperationsInput | number | null
    source?: StringFieldUpdateOperationsInput | string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherObservationUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    temperature?: FloatFieldUpdateOperationsInput | number
    humidity?: FloatFieldUpdateOperationsInput | number
    pressure?: FloatFieldUpdateOperationsInput | number
    windSpeed?: FloatFieldUpdateOperationsInput | number
    windDirection?: FloatFieldUpdateOperationsInput | number
    rainfall?: NullableFloatFieldUpdateOperationsInput | number | null
    uvIndex?: NullableFloatFieldUpdateOperationsInput | number | null
    cloudCover?: NullableFloatFieldUpdateOperationsInput | number | null
    visibility?: NullableFloatFieldUpdateOperationsInput | number | null
    source?: StringFieldUpdateOperationsInput | string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherObservationCreateManyInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    latitude: number
    longitude: number
    timestamp: Date | string
    temperature: number
    humidity: number
    pressure: number
    windSpeed: number
    windDirection: number
    rainfall?: number | null
    uvIndex?: number | null
    cloudCover?: number | null
    visibility?: number | null
    source: string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type WeatherObservationUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    temperature?: FloatFieldUpdateOperationsInput | number
    humidity?: FloatFieldUpdateOperationsInput | number
    pressure?: FloatFieldUpdateOperationsInput | number
    windSpeed?: FloatFieldUpdateOperationsInput | number
    windDirection?: FloatFieldUpdateOperationsInput | number
    rainfall?: NullableFloatFieldUpdateOperationsInput | number | null
    uvIndex?: NullableFloatFieldUpdateOperationsInput | number | null
    cloudCover?: NullableFloatFieldUpdateOperationsInput | number | null
    visibility?: NullableFloatFieldUpdateOperationsInput | number | null
    source?: StringFieldUpdateOperationsInput | string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherObservationUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timestamp?: DateTimeFieldUpdateOperationsInput | Date | string
    temperature?: FloatFieldUpdateOperationsInput | number
    humidity?: FloatFieldUpdateOperationsInput | number
    pressure?: FloatFieldUpdateOperationsInput | number
    windSpeed?: FloatFieldUpdateOperationsInput | number
    windDirection?: FloatFieldUpdateOperationsInput | number
    rainfall?: NullableFloatFieldUpdateOperationsInput | number | null
    uvIndex?: NullableFloatFieldUpdateOperationsInput | number | null
    cloudCover?: NullableFloatFieldUpdateOperationsInput | number | null
    visibility?: NullableFloatFieldUpdateOperationsInput | number | null
    source?: StringFieldUpdateOperationsInput | string
    rawData?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherForecastCreateInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    forecastFor: Date | string
    fetchedAt: Date | string
    provider: string
    hourlyData: JsonNullValueInput | InputJsonValue
    dailyData: JsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WeatherForecastUncheckedCreateInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    forecastFor: Date | string
    fetchedAt: Date | string
    provider: string
    hourlyData: JsonNullValueInput | InputJsonValue
    dailyData: JsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WeatherForecastUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    forecastFor?: DateTimeFieldUpdateOperationsInput | Date | string
    fetchedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    provider?: StringFieldUpdateOperationsInput | string
    hourlyData?: JsonNullValueInput | InputJsonValue
    dailyData?: JsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherForecastUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    forecastFor?: DateTimeFieldUpdateOperationsInput | Date | string
    fetchedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    provider?: StringFieldUpdateOperationsInput | string
    hourlyData?: JsonNullValueInput | InputJsonValue
    dailyData?: JsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherForecastCreateManyInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    forecastFor: Date | string
    fetchedAt: Date | string
    provider: string
    hourlyData: JsonNullValueInput | InputJsonValue
    dailyData: JsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WeatherForecastUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    forecastFor?: DateTimeFieldUpdateOperationsInput | Date | string
    fetchedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    provider?: StringFieldUpdateOperationsInput | string
    hourlyData?: JsonNullValueInput | InputJsonValue
    dailyData?: JsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherForecastUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    forecastFor?: DateTimeFieldUpdateOperationsInput | Date | string
    fetchedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    provider?: StringFieldUpdateOperationsInput | string
    hourlyData?: JsonNullValueInput | InputJsonValue
    dailyData?: JsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherAlertCreateInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    alertType: $Enums.AlertType
    severity: $Enums.AlertSeverity
    headline: string
    description: string
    startTime: Date | string
    endTime: Date | string
    source: string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WeatherAlertUncheckedCreateInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    alertType: $Enums.AlertType
    severity: $Enums.AlertSeverity
    headline: string
    description: string
    startTime: Date | string
    endTime: Date | string
    source: string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WeatherAlertUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    headline?: StringFieldUpdateOperationsInput | string
    description?: StringFieldUpdateOperationsInput | string
    startTime?: DateTimeFieldUpdateOperationsInput | Date | string
    endTime?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherAlertUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    headline?: StringFieldUpdateOperationsInput | string
    description?: StringFieldUpdateOperationsInput | string
    startTime?: DateTimeFieldUpdateOperationsInput | Date | string
    endTime?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherAlertCreateManyInput = {
    id?: string
    locationId: string
    tenantId?: string | null
    alertType: $Enums.AlertType
    severity: $Enums.AlertSeverity
    headline: string
    description: string
    startTime: Date | string
    endTime: Date | string
    source: string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WeatherAlertUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    headline?: StringFieldUpdateOperationsInput | string
    description?: StringFieldUpdateOperationsInput | string
    startTime?: DateTimeFieldUpdateOperationsInput | Date | string
    endTime?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WeatherAlertUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    locationId?: StringFieldUpdateOperationsInput | string
    tenantId?: NullableStringFieldUpdateOperationsInput | string | null
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    severity?: EnumAlertSeverityFieldUpdateOperationsInput | $Enums.AlertSeverity
    headline?: StringFieldUpdateOperationsInput | string
    description?: StringFieldUpdateOperationsInput | string
    startTime?: DateTimeFieldUpdateOperationsInput | Date | string
    endTime?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type LocationConfigCreateInput = {
    id?: string
    tenantId: string
    name: string
    latitude: number
    longitude: number
    timezone?: string
    isActive?: boolean
    fetchInterval?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type LocationConfigUncheckedCreateInput = {
    id?: string
    tenantId: string
    name: string
    latitude: number
    longitude: number
    timezone?: string
    isActive?: boolean
    fetchInterval?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type LocationConfigUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timezone?: StringFieldUpdateOperationsInput | string
    isActive?: BoolFieldUpdateOperationsInput | boolean
    fetchInterval?: IntFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type LocationConfigUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timezone?: StringFieldUpdateOperationsInput | string
    isActive?: BoolFieldUpdateOperationsInput | boolean
    fetchInterval?: IntFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type LocationConfigCreateManyInput = {
    id?: string
    tenantId: string
    name: string
    latitude: number
    longitude: number
    timezone?: string
    isActive?: boolean
    fetchInterval?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type LocationConfigUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timezone?: StringFieldUpdateOperationsInput | string
    isActive?: BoolFieldUpdateOperationsInput | boolean
    fetchInterval?: IntFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type LocationConfigUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    latitude?: FloatFieldUpdateOperationsInput | number
    longitude?: FloatFieldUpdateOperationsInput | number
    timezone?: StringFieldUpdateOperationsInput | string
    isActive?: BoolFieldUpdateOperationsInput | boolean
    fetchInterval?: IntFieldUpdateOperationsInput | number
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

  export type SortOrderInput = {
    sort: SortOrder
    nulls?: NullsOrder
  }

  export type WeatherObservationCountOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timestamp?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrder
    uvIndex?: SortOrder
    cloudCover?: SortOrder
    visibility?: SortOrder
    source?: SortOrder
    rawData?: SortOrder
    createdAt?: SortOrder
  }

  export type WeatherObservationAvgOrderByAggregateInput = {
    latitude?: SortOrder
    longitude?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrder
    uvIndex?: SortOrder
    cloudCover?: SortOrder
    visibility?: SortOrder
  }

  export type WeatherObservationMaxOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timestamp?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrder
    uvIndex?: SortOrder
    cloudCover?: SortOrder
    visibility?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
  }

  export type WeatherObservationMinOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timestamp?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrder
    uvIndex?: SortOrder
    cloudCover?: SortOrder
    visibility?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
  }

  export type WeatherObservationSumOrderByAggregateInput = {
    latitude?: SortOrder
    longitude?: SortOrder
    temperature?: SortOrder
    humidity?: SortOrder
    pressure?: SortOrder
    windSpeed?: SortOrder
    windDirection?: SortOrder
    rainfall?: SortOrder
    uvIndex?: SortOrder
    cloudCover?: SortOrder
    visibility?: SortOrder
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
  export type JsonFilter<$PrismaModel = never> = 
    | PatchUndefined<
        Either<Required<JsonFilterBase<$PrismaModel>>, Exclude<keyof Required<JsonFilterBase<$PrismaModel>>, 'path'>>,
        Required<JsonFilterBase<$PrismaModel>>
      >
    | OptionalFlat<Omit<Required<JsonFilterBase<$PrismaModel>>, 'path'>>

  export type JsonFilterBase<$PrismaModel = never> = {
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

  export type WeatherForecastLocationIdForecastForProviderCompoundUniqueInput = {
    locationId: string
    forecastFor: Date | string
    provider: string
  }

  export type WeatherForecastCountOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    forecastFor?: SortOrder
    fetchedAt?: SortOrder
    provider?: SortOrder
    hourlyData?: SortOrder
    dailyData?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WeatherForecastMaxOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    forecastFor?: SortOrder
    fetchedAt?: SortOrder
    provider?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WeatherForecastMinOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    forecastFor?: SortOrder
    fetchedAt?: SortOrder
    provider?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }
  export type JsonWithAggregatesFilter<$PrismaModel = never> = 
    | PatchUndefined<
        Either<Required<JsonWithAggregatesFilterBase<$PrismaModel>>, Exclude<keyof Required<JsonWithAggregatesFilterBase<$PrismaModel>>, 'path'>>,
        Required<JsonWithAggregatesFilterBase<$PrismaModel>>
      >
    | OptionalFlat<Omit<Required<JsonWithAggregatesFilterBase<$PrismaModel>>, 'path'>>

  export type JsonWithAggregatesFilterBase<$PrismaModel = never> = {
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
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedJsonFilter<$PrismaModel>
    _max?: NestedJsonFilter<$PrismaModel>
  }

  export type EnumAlertTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertType | EnumAlertTypeFieldRefInput<$PrismaModel>
    in?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertTypeFilter<$PrismaModel> | $Enums.AlertType
  }

  export type EnumAlertSeverityFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertSeverity | EnumAlertSeverityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertSeverityFilter<$PrismaModel> | $Enums.AlertSeverity
  }

  export type WeatherAlertCountOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    headline?: SortOrder
    description?: SortOrder
    startTime?: SortOrder
    endTime?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WeatherAlertMaxOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    headline?: SortOrder
    description?: SortOrder
    startTime?: SortOrder
    endTime?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WeatherAlertMinOrderByAggregateInput = {
    id?: SortOrder
    locationId?: SortOrder
    tenantId?: SortOrder
    alertType?: SortOrder
    severity?: SortOrder
    headline?: SortOrder
    description?: SortOrder
    startTime?: SortOrder
    endTime?: SortOrder
    source?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type EnumAlertTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertType | EnumAlertTypeFieldRefInput<$PrismaModel>
    in?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertTypeWithAggregatesFilter<$PrismaModel> | $Enums.AlertType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertTypeFilter<$PrismaModel>
    _max?: NestedEnumAlertTypeFilter<$PrismaModel>
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

  export type BoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
  }

  export type IntFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel>
    in?: number[] | ListIntFieldRefInput<$PrismaModel>
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel>
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntFilter<$PrismaModel> | number
  }

  export type LocationConfigTenantIdLatitudeLongitudeCompoundUniqueInput = {
    tenantId: string
    latitude: number
    longitude: number
  }

  export type LocationConfigCountOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timezone?: SortOrder
    isActive?: SortOrder
    fetchInterval?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type LocationConfigAvgOrderByAggregateInput = {
    latitude?: SortOrder
    longitude?: SortOrder
    fetchInterval?: SortOrder
  }

  export type LocationConfigMaxOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timezone?: SortOrder
    isActive?: SortOrder
    fetchInterval?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type LocationConfigMinOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    timezone?: SortOrder
    isActive?: SortOrder
    fetchInterval?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type LocationConfigSumOrderByAggregateInput = {
    latitude?: SortOrder
    longitude?: SortOrder
    fetchInterval?: SortOrder
  }

  export type BoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
  }

  export type IntWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel>
    in?: number[] | ListIntFieldRefInput<$PrismaModel>
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel>
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntWithAggregatesFilter<$PrismaModel> | number
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedFloatFilter<$PrismaModel>
    _sum?: NestedIntFilter<$PrismaModel>
    _min?: NestedIntFilter<$PrismaModel>
    _max?: NestedIntFilter<$PrismaModel>
  }

  export type StringFieldUpdateOperationsInput = {
    set?: string
  }

  export type NullableStringFieldUpdateOperationsInput = {
    set?: string | null
  }

  export type FloatFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type DateTimeFieldUpdateOperationsInput = {
    set?: Date | string
  }

  export type NullableFloatFieldUpdateOperationsInput = {
    set?: number | null
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type EnumAlertTypeFieldUpdateOperationsInput = {
    set?: $Enums.AlertType
  }

  export type EnumAlertSeverityFieldUpdateOperationsInput = {
    set?: $Enums.AlertSeverity
  }

  export type BoolFieldUpdateOperationsInput = {
    set?: boolean
  }

  export type IntFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
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
  export type NestedJsonFilter<$PrismaModel = never> = 
    | PatchUndefined<
        Either<Required<NestedJsonFilterBase<$PrismaModel>>, Exclude<keyof Required<NestedJsonFilterBase<$PrismaModel>>, 'path'>>,
        Required<NestedJsonFilterBase<$PrismaModel>>
      >
    | OptionalFlat<Omit<Required<NestedJsonFilterBase<$PrismaModel>>, 'path'>>

  export type NestedJsonFilterBase<$PrismaModel = never> = {
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

  export type NestedEnumAlertTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertType | EnumAlertTypeFieldRefInput<$PrismaModel>
    in?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertTypeFilter<$PrismaModel> | $Enums.AlertType
  }

  export type NestedEnumAlertSeverityFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertSeverity | EnumAlertSeverityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertSeverity[] | ListEnumAlertSeverityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertSeverityFilter<$PrismaModel> | $Enums.AlertSeverity
  }

  export type NestedEnumAlertTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertType | EnumAlertTypeFieldRefInput<$PrismaModel>
    in?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertTypeWithAggregatesFilter<$PrismaModel> | $Enums.AlertType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertTypeFilter<$PrismaModel>
    _max?: NestedEnumAlertTypeFilter<$PrismaModel>
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

  export type NestedBoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
  }

  export type NestedBoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
  }

  export type NestedIntWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel>
    in?: number[] | ListIntFieldRefInput<$PrismaModel>
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel>
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntWithAggregatesFilter<$PrismaModel> | number
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedFloatFilter<$PrismaModel>
    _sum?: NestedIntFilter<$PrismaModel>
    _min?: NestedIntFilter<$PrismaModel>
    _max?: NestedIntFilter<$PrismaModel>
  }



  /**
   * Aliases for legacy arg types
   */
    /**
     * @deprecated Use WeatherObservationDefaultArgs instead
     */
    export type WeatherObservationArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = WeatherObservationDefaultArgs<ExtArgs>
    /**
     * @deprecated Use WeatherForecastDefaultArgs instead
     */
    export type WeatherForecastArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = WeatherForecastDefaultArgs<ExtArgs>
    /**
     * @deprecated Use WeatherAlertDefaultArgs instead
     */
    export type WeatherAlertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = WeatherAlertDefaultArgs<ExtArgs>
    /**
     * @deprecated Use LocationConfigDefaultArgs instead
     */
    export type LocationConfigArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = LocationConfigDefaultArgs<ExtArgs>

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