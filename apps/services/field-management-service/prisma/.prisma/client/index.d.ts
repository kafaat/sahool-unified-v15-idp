
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
 * Model Field
 * 
 */
export type Field = $Result.DefaultSelection<Prisma.$FieldPayload>
/**
 * Model FieldBoundaryHistory
 * 
 */
export type FieldBoundaryHistory = $Result.DefaultSelection<Prisma.$FieldBoundaryHistoryPayload>
/**
 * Model SyncStatus
 * 
 */
export type SyncStatus = $Result.DefaultSelection<Prisma.$SyncStatusPayload>
/**
 * Model Task
 * 
 */
export type Task = $Result.DefaultSelection<Prisma.$TaskPayload>
/**
 * Model NdviReading
 * 
 */
export type NdviReading = $Result.DefaultSelection<Prisma.$NdviReadingPayload>

/**
 * Enums
 */
export namespace $Enums {
  export const FieldStatus: {
  active: 'active',
  fallow: 'fallow',
  harvested: 'harvested',
  preparing: 'preparing',
  inactive: 'inactive'
};

export type FieldStatus = (typeof FieldStatus)[keyof typeof FieldStatus]


export const ChangeSource: {
  mobile: 'mobile',
  web: 'web',
  api: 'api',
  system: 'system'
};

export type ChangeSource = (typeof ChangeSource)[keyof typeof ChangeSource]


export const SyncState: {
  idle: 'idle',
  syncing: 'syncing',
  error: 'error',
  conflict: 'conflict'
};

export type SyncState = (typeof SyncState)[keyof typeof SyncState]


export const TaskType: {
  irrigation: 'irrigation',
  fertilization: 'fertilization',
  spraying: 'spraying',
  scouting: 'scouting',
  maintenance: 'maintenance',
  sampling: 'sampling',
  harvest: 'harvest',
  planting: 'planting',
  other: 'other'
};

export type TaskType = (typeof TaskType)[keyof typeof TaskType]


export const Priority: {
  low: 'low',
  medium: 'medium',
  high: 'high',
  urgent: 'urgent'
};

export type Priority = (typeof Priority)[keyof typeof Priority]


export const TaskState: {
  pending: 'pending',
  in_progress: 'in_progress',
  completed: 'completed',
  cancelled: 'cancelled',
  overdue: 'overdue'
};

export type TaskState = (typeof TaskState)[keyof typeof TaskState]

}

export type FieldStatus = $Enums.FieldStatus

export const FieldStatus: typeof $Enums.FieldStatus

export type ChangeSource = $Enums.ChangeSource

export const ChangeSource: typeof $Enums.ChangeSource

export type SyncState = $Enums.SyncState

export const SyncState: typeof $Enums.SyncState

export type TaskType = $Enums.TaskType

export const TaskType: typeof $Enums.TaskType

export type Priority = $Enums.Priority

export const Priority: typeof $Enums.Priority

export type TaskState = $Enums.TaskState

export const TaskState: typeof $Enums.TaskState

/**
 * ##  Prisma Client ʲˢ
 * 
 * Type-safe database client for TypeScript & Node.js
 * @example
 * ```
 * const prisma = new PrismaClient()
 * // Fetch zero or more Fields
 * const fields = await prisma.field.findMany()
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
   * // Fetch zero or more Fields
   * const fields = await prisma.field.findMany()
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
   * `prisma.field`: Exposes CRUD operations for the **Field** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Fields
    * const fields = await prisma.field.findMany()
    * ```
    */
  get field(): Prisma.FieldDelegate<ExtArgs>;

  /**
   * `prisma.fieldBoundaryHistory`: Exposes CRUD operations for the **FieldBoundaryHistory** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more FieldBoundaryHistories
    * const fieldBoundaryHistories = await prisma.fieldBoundaryHistory.findMany()
    * ```
    */
  get fieldBoundaryHistory(): Prisma.FieldBoundaryHistoryDelegate<ExtArgs>;

  /**
   * `prisma.syncStatus`: Exposes CRUD operations for the **SyncStatus** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more SyncStatuses
    * const syncStatuses = await prisma.syncStatus.findMany()
    * ```
    */
  get syncStatus(): Prisma.SyncStatusDelegate<ExtArgs>;

  /**
   * `prisma.task`: Exposes CRUD operations for the **Task** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Tasks
    * const tasks = await prisma.task.findMany()
    * ```
    */
  get task(): Prisma.TaskDelegate<ExtArgs>;

  /**
   * `prisma.ndviReading`: Exposes CRUD operations for the **NdviReading** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more NdviReadings
    * const ndviReadings = await prisma.ndviReading.findMany()
    * ```
    */
  get ndviReading(): Prisma.NdviReadingDelegate<ExtArgs>;
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
    Field: 'Field',
    FieldBoundaryHistory: 'FieldBoundaryHistory',
    SyncStatus: 'SyncStatus',
    Task: 'Task',
    NdviReading: 'NdviReading'
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
      modelProps: "field" | "fieldBoundaryHistory" | "syncStatus" | "task" | "ndviReading"
      txIsolationLevel: Prisma.TransactionIsolationLevel
    }
    model: {
      Field: {
        payload: Prisma.$FieldPayload<ExtArgs>
        fields: Prisma.FieldFieldRefs
        operations: {
          findUnique: {
            args: Prisma.FieldFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.FieldFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>
          }
          findFirst: {
            args: Prisma.FieldFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.FieldFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>
          }
          findMany: {
            args: Prisma.FieldFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>[]
          }
          create: {
            args: Prisma.FieldCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>
          }
          createMany: {
            args: Prisma.FieldCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.FieldCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>[]
          }
          delete: {
            args: Prisma.FieldDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>
          }
          update: {
            args: Prisma.FieldUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>
          }
          deleteMany: {
            args: Prisma.FieldDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.FieldUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.FieldUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldPayload>
          }
          aggregate: {
            args: Prisma.FieldAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateField>
          }
          groupBy: {
            args: Prisma.FieldGroupByArgs<ExtArgs>
            result: $Utils.Optional<FieldGroupByOutputType>[]
          }
          count: {
            args: Prisma.FieldCountArgs<ExtArgs>
            result: $Utils.Optional<FieldCountAggregateOutputType> | number
          }
        }
      }
      FieldBoundaryHistory: {
        payload: Prisma.$FieldBoundaryHistoryPayload<ExtArgs>
        fields: Prisma.FieldBoundaryHistoryFieldRefs
        operations: {
          findUnique: {
            args: Prisma.FieldBoundaryHistoryFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.FieldBoundaryHistoryFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>
          }
          findFirst: {
            args: Prisma.FieldBoundaryHistoryFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.FieldBoundaryHistoryFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>
          }
          findMany: {
            args: Prisma.FieldBoundaryHistoryFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>[]
          }
          create: {
            args: Prisma.FieldBoundaryHistoryCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>
          }
          createMany: {
            args: Prisma.FieldBoundaryHistoryCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.FieldBoundaryHistoryCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>[]
          }
          delete: {
            args: Prisma.FieldBoundaryHistoryDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>
          }
          update: {
            args: Prisma.FieldBoundaryHistoryUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>
          }
          deleteMany: {
            args: Prisma.FieldBoundaryHistoryDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.FieldBoundaryHistoryUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.FieldBoundaryHistoryUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$FieldBoundaryHistoryPayload>
          }
          aggregate: {
            args: Prisma.FieldBoundaryHistoryAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateFieldBoundaryHistory>
          }
          groupBy: {
            args: Prisma.FieldBoundaryHistoryGroupByArgs<ExtArgs>
            result: $Utils.Optional<FieldBoundaryHistoryGroupByOutputType>[]
          }
          count: {
            args: Prisma.FieldBoundaryHistoryCountArgs<ExtArgs>
            result: $Utils.Optional<FieldBoundaryHistoryCountAggregateOutputType> | number
          }
        }
      }
      SyncStatus: {
        payload: Prisma.$SyncStatusPayload<ExtArgs>
        fields: Prisma.SyncStatusFieldRefs
        operations: {
          findUnique: {
            args: Prisma.SyncStatusFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.SyncStatusFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>
          }
          findFirst: {
            args: Prisma.SyncStatusFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.SyncStatusFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>
          }
          findMany: {
            args: Prisma.SyncStatusFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>[]
          }
          create: {
            args: Prisma.SyncStatusCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>
          }
          createMany: {
            args: Prisma.SyncStatusCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.SyncStatusCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>[]
          }
          delete: {
            args: Prisma.SyncStatusDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>
          }
          update: {
            args: Prisma.SyncStatusUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>
          }
          deleteMany: {
            args: Prisma.SyncStatusDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.SyncStatusUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.SyncStatusUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$SyncStatusPayload>
          }
          aggregate: {
            args: Prisma.SyncStatusAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateSyncStatus>
          }
          groupBy: {
            args: Prisma.SyncStatusGroupByArgs<ExtArgs>
            result: $Utils.Optional<SyncStatusGroupByOutputType>[]
          }
          count: {
            args: Prisma.SyncStatusCountArgs<ExtArgs>
            result: $Utils.Optional<SyncStatusCountAggregateOutputType> | number
          }
        }
      }
      Task: {
        payload: Prisma.$TaskPayload<ExtArgs>
        fields: Prisma.TaskFieldRefs
        operations: {
          findUnique: {
            args: Prisma.TaskFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.TaskFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>
          }
          findFirst: {
            args: Prisma.TaskFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.TaskFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>
          }
          findMany: {
            args: Prisma.TaskFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>[]
          }
          create: {
            args: Prisma.TaskCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>
          }
          createMany: {
            args: Prisma.TaskCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.TaskCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>[]
          }
          delete: {
            args: Prisma.TaskDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>
          }
          update: {
            args: Prisma.TaskUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>
          }
          deleteMany: {
            args: Prisma.TaskDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.TaskUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.TaskUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$TaskPayload>
          }
          aggregate: {
            args: Prisma.TaskAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateTask>
          }
          groupBy: {
            args: Prisma.TaskGroupByArgs<ExtArgs>
            result: $Utils.Optional<TaskGroupByOutputType>[]
          }
          count: {
            args: Prisma.TaskCountArgs<ExtArgs>
            result: $Utils.Optional<TaskCountAggregateOutputType> | number
          }
        }
      }
      NdviReading: {
        payload: Prisma.$NdviReadingPayload<ExtArgs>
        fields: Prisma.NdviReadingFieldRefs
        operations: {
          findUnique: {
            args: Prisma.NdviReadingFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.NdviReadingFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>
          }
          findFirst: {
            args: Prisma.NdviReadingFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.NdviReadingFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>
          }
          findMany: {
            args: Prisma.NdviReadingFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>[]
          }
          create: {
            args: Prisma.NdviReadingCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>
          }
          createMany: {
            args: Prisma.NdviReadingCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.NdviReadingCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>[]
          }
          delete: {
            args: Prisma.NdviReadingDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>
          }
          update: {
            args: Prisma.NdviReadingUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>
          }
          deleteMany: {
            args: Prisma.NdviReadingDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.NdviReadingUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.NdviReadingUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$NdviReadingPayload>
          }
          aggregate: {
            args: Prisma.NdviReadingAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateNdviReading>
          }
          groupBy: {
            args: Prisma.NdviReadingGroupByArgs<ExtArgs>
            result: $Utils.Optional<NdviReadingGroupByOutputType>[]
          }
          count: {
            args: Prisma.NdviReadingCountArgs<ExtArgs>
            result: $Utils.Optional<NdviReadingCountAggregateOutputType> | number
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
   * Count Type FieldCountOutputType
   */

  export type FieldCountOutputType = {
    boundaryHistory: number
    tasks: number
    ndviReadings: number
  }

  export type FieldCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    boundaryHistory?: boolean | FieldCountOutputTypeCountBoundaryHistoryArgs
    tasks?: boolean | FieldCountOutputTypeCountTasksArgs
    ndviReadings?: boolean | FieldCountOutputTypeCountNdviReadingsArgs
  }

  // Custom InputTypes
  /**
   * FieldCountOutputType without action
   */
  export type FieldCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldCountOutputType
     */
    select?: FieldCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * FieldCountOutputType without action
   */
  export type FieldCountOutputTypeCountBoundaryHistoryArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: FieldBoundaryHistoryWhereInput
  }

  /**
   * FieldCountOutputType without action
   */
  export type FieldCountOutputTypeCountTasksArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: TaskWhereInput
  }

  /**
   * FieldCountOutputType without action
   */
  export type FieldCountOutputTypeCountNdviReadingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: NdviReadingWhereInput
  }


  /**
   * Models
   */

  /**
   * Model Field
   */

  export type AggregateField = {
    _count: FieldCountAggregateOutputType | null
    _avg: FieldAvgAggregateOutputType | null
    _sum: FieldSumAggregateOutputType | null
    _min: FieldMinAggregateOutputType | null
    _max: FieldMaxAggregateOutputType | null
  }

  export type FieldAvgAggregateOutputType = {
    version: number | null
    areaHectares: Decimal | null
    healthScore: Decimal | null
    ndviValue: Decimal | null
  }

  export type FieldSumAggregateOutputType = {
    version: number | null
    areaHectares: Decimal | null
    healthScore: Decimal | null
    ndviValue: Decimal | null
  }

  export type FieldMinAggregateOutputType = {
    id: string | null
    version: number | null
    name: string | null
    tenantId: string | null
    cropType: string | null
    ownerId: string | null
    areaHectares: Decimal | null
    healthScore: Decimal | null
    ndviValue: Decimal | null
    status: $Enums.FieldStatus | null
    plantingDate: Date | null
    expectedHarvest: Date | null
    irrigationType: string | null
    soilType: string | null
    isDeleted: boolean | null
    serverUpdatedAt: Date | null
    etag: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type FieldMaxAggregateOutputType = {
    id: string | null
    version: number | null
    name: string | null
    tenantId: string | null
    cropType: string | null
    ownerId: string | null
    areaHectares: Decimal | null
    healthScore: Decimal | null
    ndviValue: Decimal | null
    status: $Enums.FieldStatus | null
    plantingDate: Date | null
    expectedHarvest: Date | null
    irrigationType: string | null
    soilType: string | null
    isDeleted: boolean | null
    serverUpdatedAt: Date | null
    etag: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type FieldCountAggregateOutputType = {
    id: number
    version: number
    name: number
    tenantId: number
    cropType: number
    ownerId: number
    areaHectares: number
    healthScore: number
    ndviValue: number
    status: number
    plantingDate: number
    expectedHarvest: number
    irrigationType: number
    soilType: number
    metadata: number
    isDeleted: number
    serverUpdatedAt: number
    etag: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type FieldAvgAggregateInputType = {
    version?: true
    areaHectares?: true
    healthScore?: true
    ndviValue?: true
  }

  export type FieldSumAggregateInputType = {
    version?: true
    areaHectares?: true
    healthScore?: true
    ndviValue?: true
  }

  export type FieldMinAggregateInputType = {
    id?: true
    version?: true
    name?: true
    tenantId?: true
    cropType?: true
    ownerId?: true
    areaHectares?: true
    healthScore?: true
    ndviValue?: true
    status?: true
    plantingDate?: true
    expectedHarvest?: true
    irrigationType?: true
    soilType?: true
    isDeleted?: true
    serverUpdatedAt?: true
    etag?: true
    createdAt?: true
    updatedAt?: true
  }

  export type FieldMaxAggregateInputType = {
    id?: true
    version?: true
    name?: true
    tenantId?: true
    cropType?: true
    ownerId?: true
    areaHectares?: true
    healthScore?: true
    ndviValue?: true
    status?: true
    plantingDate?: true
    expectedHarvest?: true
    irrigationType?: true
    soilType?: true
    isDeleted?: true
    serverUpdatedAt?: true
    etag?: true
    createdAt?: true
    updatedAt?: true
  }

  export type FieldCountAggregateInputType = {
    id?: true
    version?: true
    name?: true
    tenantId?: true
    cropType?: true
    ownerId?: true
    areaHectares?: true
    healthScore?: true
    ndviValue?: true
    status?: true
    plantingDate?: true
    expectedHarvest?: true
    irrigationType?: true
    soilType?: true
    metadata?: true
    isDeleted?: true
    serverUpdatedAt?: true
    etag?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type FieldAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Field to aggregate.
     */
    where?: FieldWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Fields to fetch.
     */
    orderBy?: FieldOrderByWithRelationInput | FieldOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: FieldWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Fields from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Fields.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Fields
    **/
    _count?: true | FieldCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: FieldAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: FieldSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: FieldMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: FieldMaxAggregateInputType
  }

  export type GetFieldAggregateType<T extends FieldAggregateArgs> = {
        [P in keyof T & keyof AggregateField]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateField[P]>
      : GetScalarType<T[P], AggregateField[P]>
  }




  export type FieldGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: FieldWhereInput
    orderBy?: FieldOrderByWithAggregationInput | FieldOrderByWithAggregationInput[]
    by: FieldScalarFieldEnum[] | FieldScalarFieldEnum
    having?: FieldScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: FieldCountAggregateInputType | true
    _avg?: FieldAvgAggregateInputType
    _sum?: FieldSumAggregateInputType
    _min?: FieldMinAggregateInputType
    _max?: FieldMaxAggregateInputType
  }

  export type FieldGroupByOutputType = {
    id: string
    version: number
    name: string
    tenantId: string
    cropType: string
    ownerId: string | null
    areaHectares: Decimal | null
    healthScore: Decimal | null
    ndviValue: Decimal | null
    status: $Enums.FieldStatus
    plantingDate: Date | null
    expectedHarvest: Date | null
    irrigationType: string | null
    soilType: string | null
    metadata: JsonValue | null
    isDeleted: boolean
    serverUpdatedAt: Date
    etag: string | null
    createdAt: Date
    updatedAt: Date
    _count: FieldCountAggregateOutputType | null
    _avg: FieldAvgAggregateOutputType | null
    _sum: FieldSumAggregateOutputType | null
    _min: FieldMinAggregateOutputType | null
    _max: FieldMaxAggregateOutputType | null
  }

  type GetFieldGroupByPayload<T extends FieldGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<FieldGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof FieldGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], FieldGroupByOutputType[P]>
            : GetScalarType<T[P], FieldGroupByOutputType[P]>
        }
      >
    >


  export type FieldSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    version?: boolean
    name?: boolean
    tenantId?: boolean
    cropType?: boolean
    ownerId?: boolean
    areaHectares?: boolean
    healthScore?: boolean
    ndviValue?: boolean
    status?: boolean
    plantingDate?: boolean
    expectedHarvest?: boolean
    irrigationType?: boolean
    soilType?: boolean
    metadata?: boolean
    isDeleted?: boolean
    serverUpdatedAt?: boolean
    etag?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    boundaryHistory?: boolean | Field$boundaryHistoryArgs<ExtArgs>
    tasks?: boolean | Field$tasksArgs<ExtArgs>
    ndviReadings?: boolean | Field$ndviReadingsArgs<ExtArgs>
    _count?: boolean | FieldCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["field"]>

  export type FieldSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    version?: boolean
    name?: boolean
    tenantId?: boolean
    cropType?: boolean
    ownerId?: boolean
    areaHectares?: boolean
    healthScore?: boolean
    ndviValue?: boolean
    status?: boolean
    plantingDate?: boolean
    expectedHarvest?: boolean
    irrigationType?: boolean
    soilType?: boolean
    metadata?: boolean
    isDeleted?: boolean
    serverUpdatedAt?: boolean
    etag?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["field"]>

  export type FieldSelectScalar = {
    id?: boolean
    version?: boolean
    name?: boolean
    tenantId?: boolean
    cropType?: boolean
    ownerId?: boolean
    areaHectares?: boolean
    healthScore?: boolean
    ndviValue?: boolean
    status?: boolean
    plantingDate?: boolean
    expectedHarvest?: boolean
    irrigationType?: boolean
    soilType?: boolean
    metadata?: boolean
    isDeleted?: boolean
    serverUpdatedAt?: boolean
    etag?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type FieldInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    boundaryHistory?: boolean | Field$boundaryHistoryArgs<ExtArgs>
    tasks?: boolean | Field$tasksArgs<ExtArgs>
    ndviReadings?: boolean | Field$ndviReadingsArgs<ExtArgs>
    _count?: boolean | FieldCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type FieldIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {}

  export type $FieldPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Field"
    objects: {
      boundaryHistory: Prisma.$FieldBoundaryHistoryPayload<ExtArgs>[]
      tasks: Prisma.$TaskPayload<ExtArgs>[]
      ndviReadings: Prisma.$NdviReadingPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      version: number
      name: string
      tenantId: string
      cropType: string
      ownerId: string | null
      areaHectares: Prisma.Decimal | null
      healthScore: Prisma.Decimal | null
      ndviValue: Prisma.Decimal | null
      status: $Enums.FieldStatus
      plantingDate: Date | null
      expectedHarvest: Date | null
      irrigationType: string | null
      soilType: string | null
      metadata: Prisma.JsonValue | null
      isDeleted: boolean
      serverUpdatedAt: Date
      etag: string | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["field"]>
    composites: {}
  }

  type FieldGetPayload<S extends boolean | null | undefined | FieldDefaultArgs> = $Result.GetResult<Prisma.$FieldPayload, S>

  type FieldCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<FieldFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: FieldCountAggregateInputType | true
    }

  export interface FieldDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Field'], meta: { name: 'Field' } }
    /**
     * Find zero or one Field that matches the filter.
     * @param {FieldFindUniqueArgs} args - Arguments to find a Field
     * @example
     * // Get one Field
     * const field = await prisma.field.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends FieldFindUniqueArgs>(args: SelectSubset<T, FieldFindUniqueArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Field that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {FieldFindUniqueOrThrowArgs} args - Arguments to find a Field
     * @example
     * // Get one Field
     * const field = await prisma.field.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends FieldFindUniqueOrThrowArgs>(args: SelectSubset<T, FieldFindUniqueOrThrowArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Field that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldFindFirstArgs} args - Arguments to find a Field
     * @example
     * // Get one Field
     * const field = await prisma.field.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends FieldFindFirstArgs>(args?: SelectSubset<T, FieldFindFirstArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Field that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldFindFirstOrThrowArgs} args - Arguments to find a Field
     * @example
     * // Get one Field
     * const field = await prisma.field.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends FieldFindFirstOrThrowArgs>(args?: SelectSubset<T, FieldFindFirstOrThrowArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Fields that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Fields
     * const fields = await prisma.field.findMany()
     * 
     * // Get first 10 Fields
     * const fields = await prisma.field.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const fieldWithIdOnly = await prisma.field.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends FieldFindManyArgs>(args?: SelectSubset<T, FieldFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Field.
     * @param {FieldCreateArgs} args - Arguments to create a Field.
     * @example
     * // Create one Field
     * const Field = await prisma.field.create({
     *   data: {
     *     // ... data to create a Field
     *   }
     * })
     * 
     */
    create<T extends FieldCreateArgs>(args: SelectSubset<T, FieldCreateArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Fields.
     * @param {FieldCreateManyArgs} args - Arguments to create many Fields.
     * @example
     * // Create many Fields
     * const field = await prisma.field.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends FieldCreateManyArgs>(args?: SelectSubset<T, FieldCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Fields and returns the data saved in the database.
     * @param {FieldCreateManyAndReturnArgs} args - Arguments to create many Fields.
     * @example
     * // Create many Fields
     * const field = await prisma.field.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Fields and only return the `id`
     * const fieldWithIdOnly = await prisma.field.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends FieldCreateManyAndReturnArgs>(args?: SelectSubset<T, FieldCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Field.
     * @param {FieldDeleteArgs} args - Arguments to delete one Field.
     * @example
     * // Delete one Field
     * const Field = await prisma.field.delete({
     *   where: {
     *     // ... filter to delete one Field
     *   }
     * })
     * 
     */
    delete<T extends FieldDeleteArgs>(args: SelectSubset<T, FieldDeleteArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Field.
     * @param {FieldUpdateArgs} args - Arguments to update one Field.
     * @example
     * // Update one Field
     * const field = await prisma.field.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends FieldUpdateArgs>(args: SelectSubset<T, FieldUpdateArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Fields.
     * @param {FieldDeleteManyArgs} args - Arguments to filter Fields to delete.
     * @example
     * // Delete a few Fields
     * const { count } = await prisma.field.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends FieldDeleteManyArgs>(args?: SelectSubset<T, FieldDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Fields.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Fields
     * const field = await prisma.field.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends FieldUpdateManyArgs>(args: SelectSubset<T, FieldUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Field.
     * @param {FieldUpsertArgs} args - Arguments to update or create a Field.
     * @example
     * // Update or create a Field
     * const field = await prisma.field.upsert({
     *   create: {
     *     // ... data to create a Field
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Field we want to update
     *   }
     * })
     */
    upsert<T extends FieldUpsertArgs>(args: SelectSubset<T, FieldUpsertArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Fields.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldCountArgs} args - Arguments to filter Fields to count.
     * @example
     * // Count the number of Fields
     * const count = await prisma.field.count({
     *   where: {
     *     // ... the filter for the Fields we want to count
     *   }
     * })
    **/
    count<T extends FieldCountArgs>(
      args?: Subset<T, FieldCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], FieldCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Field.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends FieldAggregateArgs>(args: Subset<T, FieldAggregateArgs>): Prisma.PrismaPromise<GetFieldAggregateType<T>>

    /**
     * Group by Field.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldGroupByArgs} args - Group by arguments.
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
      T extends FieldGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: FieldGroupByArgs['orderBy'] }
        : { orderBy?: FieldGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, FieldGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetFieldGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Field model
   */
  readonly fields: FieldFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Field.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__FieldClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    boundaryHistory<T extends Field$boundaryHistoryArgs<ExtArgs> = {}>(args?: Subset<T, Field$boundaryHistoryArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "findMany"> | Null>
    tasks<T extends Field$tasksArgs<ExtArgs> = {}>(args?: Subset<T, Field$tasksArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "findMany"> | Null>
    ndviReadings<T extends Field$ndviReadingsArgs<ExtArgs> = {}>(args?: Subset<T, Field$ndviReadingsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "findMany"> | Null>
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
   * Fields of the Field model
   */ 
  interface FieldFieldRefs {
    readonly id: FieldRef<"Field", 'String'>
    readonly version: FieldRef<"Field", 'Int'>
    readonly name: FieldRef<"Field", 'String'>
    readonly tenantId: FieldRef<"Field", 'String'>
    readonly cropType: FieldRef<"Field", 'String'>
    readonly ownerId: FieldRef<"Field", 'String'>
    readonly areaHectares: FieldRef<"Field", 'Decimal'>
    readonly healthScore: FieldRef<"Field", 'Decimal'>
    readonly ndviValue: FieldRef<"Field", 'Decimal'>
    readonly status: FieldRef<"Field", 'FieldStatus'>
    readonly plantingDate: FieldRef<"Field", 'DateTime'>
    readonly expectedHarvest: FieldRef<"Field", 'DateTime'>
    readonly irrigationType: FieldRef<"Field", 'String'>
    readonly soilType: FieldRef<"Field", 'String'>
    readonly metadata: FieldRef<"Field", 'Json'>
    readonly isDeleted: FieldRef<"Field", 'Boolean'>
    readonly serverUpdatedAt: FieldRef<"Field", 'DateTime'>
    readonly etag: FieldRef<"Field", 'String'>
    readonly createdAt: FieldRef<"Field", 'DateTime'>
    readonly updatedAt: FieldRef<"Field", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Field findUnique
   */
  export type FieldFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * Filter, which Field to fetch.
     */
    where: FieldWhereUniqueInput
  }

  /**
   * Field findUniqueOrThrow
   */
  export type FieldFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * Filter, which Field to fetch.
     */
    where: FieldWhereUniqueInput
  }

  /**
   * Field findFirst
   */
  export type FieldFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * Filter, which Field to fetch.
     */
    where?: FieldWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Fields to fetch.
     */
    orderBy?: FieldOrderByWithRelationInput | FieldOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Fields.
     */
    cursor?: FieldWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Fields from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Fields.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Fields.
     */
    distinct?: FieldScalarFieldEnum | FieldScalarFieldEnum[]
  }

  /**
   * Field findFirstOrThrow
   */
  export type FieldFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * Filter, which Field to fetch.
     */
    where?: FieldWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Fields to fetch.
     */
    orderBy?: FieldOrderByWithRelationInput | FieldOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Fields.
     */
    cursor?: FieldWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Fields from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Fields.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Fields.
     */
    distinct?: FieldScalarFieldEnum | FieldScalarFieldEnum[]
  }

  /**
   * Field findMany
   */
  export type FieldFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * Filter, which Fields to fetch.
     */
    where?: FieldWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Fields to fetch.
     */
    orderBy?: FieldOrderByWithRelationInput | FieldOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Fields.
     */
    cursor?: FieldWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Fields from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Fields.
     */
    skip?: number
    distinct?: FieldScalarFieldEnum | FieldScalarFieldEnum[]
  }

  /**
   * Field create
   */
  export type FieldCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * The data needed to create a Field.
     */
    data: XOR<FieldCreateInput, FieldUncheckedCreateInput>
  }

  /**
   * Field createMany
   */
  export type FieldCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Fields.
     */
    data: FieldCreateManyInput | FieldCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Field createManyAndReturn
   */
  export type FieldCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Fields.
     */
    data: FieldCreateManyInput | FieldCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Field update
   */
  export type FieldUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * The data needed to update a Field.
     */
    data: XOR<FieldUpdateInput, FieldUncheckedUpdateInput>
    /**
     * Choose, which Field to update.
     */
    where: FieldWhereUniqueInput
  }

  /**
   * Field updateMany
   */
  export type FieldUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Fields.
     */
    data: XOR<FieldUpdateManyMutationInput, FieldUncheckedUpdateManyInput>
    /**
     * Filter which Fields to update
     */
    where?: FieldWhereInput
  }

  /**
   * Field upsert
   */
  export type FieldUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * The filter to search for the Field to update in case it exists.
     */
    where: FieldWhereUniqueInput
    /**
     * In case the Field found by the `where` argument doesn't exist, create a new Field with this data.
     */
    create: XOR<FieldCreateInput, FieldUncheckedCreateInput>
    /**
     * In case the Field was found with the provided `where` argument, update it with this data.
     */
    update: XOR<FieldUpdateInput, FieldUncheckedUpdateInput>
  }

  /**
   * Field delete
   */
  export type FieldDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    /**
     * Filter which Field to delete.
     */
    where: FieldWhereUniqueInput
  }

  /**
   * Field deleteMany
   */
  export type FieldDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Fields to delete
     */
    where?: FieldWhereInput
  }

  /**
   * Field.boundaryHistory
   */
  export type Field$boundaryHistoryArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    where?: FieldBoundaryHistoryWhereInput
    orderBy?: FieldBoundaryHistoryOrderByWithRelationInput | FieldBoundaryHistoryOrderByWithRelationInput[]
    cursor?: FieldBoundaryHistoryWhereUniqueInput
    take?: number
    skip?: number
    distinct?: FieldBoundaryHistoryScalarFieldEnum | FieldBoundaryHistoryScalarFieldEnum[]
  }

  /**
   * Field.tasks
   */
  export type Field$tasksArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    where?: TaskWhereInput
    orderBy?: TaskOrderByWithRelationInput | TaskOrderByWithRelationInput[]
    cursor?: TaskWhereUniqueInput
    take?: number
    skip?: number
    distinct?: TaskScalarFieldEnum | TaskScalarFieldEnum[]
  }

  /**
   * Field.ndviReadings
   */
  export type Field$ndviReadingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    where?: NdviReadingWhereInput
    orderBy?: NdviReadingOrderByWithRelationInput | NdviReadingOrderByWithRelationInput[]
    cursor?: NdviReadingWhereUniqueInput
    take?: number
    skip?: number
    distinct?: NdviReadingScalarFieldEnum | NdviReadingScalarFieldEnum[]
  }

  /**
   * Field without action
   */
  export type FieldDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
  }


  /**
   * Model FieldBoundaryHistory
   */

  export type AggregateFieldBoundaryHistory = {
    _count: FieldBoundaryHistoryCountAggregateOutputType | null
    _avg: FieldBoundaryHistoryAvgAggregateOutputType | null
    _sum: FieldBoundaryHistorySumAggregateOutputType | null
    _min: FieldBoundaryHistoryMinAggregateOutputType | null
    _max: FieldBoundaryHistoryMaxAggregateOutputType | null
  }

  export type FieldBoundaryHistoryAvgAggregateOutputType = {
    versionAtChange: number | null
    areaChangeHectares: Decimal | null
  }

  export type FieldBoundaryHistorySumAggregateOutputType = {
    versionAtChange: number | null
    areaChangeHectares: Decimal | null
  }

  export type FieldBoundaryHistoryMinAggregateOutputType = {
    id: string | null
    fieldId: string | null
    versionAtChange: number | null
    areaChangeHectares: Decimal | null
    changedBy: string | null
    changeReason: string | null
    changeSource: $Enums.ChangeSource | null
    deviceId: string | null
    createdAt: Date | null
  }

  export type FieldBoundaryHistoryMaxAggregateOutputType = {
    id: string | null
    fieldId: string | null
    versionAtChange: number | null
    areaChangeHectares: Decimal | null
    changedBy: string | null
    changeReason: string | null
    changeSource: $Enums.ChangeSource | null
    deviceId: string | null
    createdAt: Date | null
  }

  export type FieldBoundaryHistoryCountAggregateOutputType = {
    id: number
    fieldId: number
    versionAtChange: number
    areaChangeHectares: number
    changedBy: number
    changeReason: number
    changeSource: number
    deviceId: number
    createdAt: number
    _all: number
  }


  export type FieldBoundaryHistoryAvgAggregateInputType = {
    versionAtChange?: true
    areaChangeHectares?: true
  }

  export type FieldBoundaryHistorySumAggregateInputType = {
    versionAtChange?: true
    areaChangeHectares?: true
  }

  export type FieldBoundaryHistoryMinAggregateInputType = {
    id?: true
    fieldId?: true
    versionAtChange?: true
    areaChangeHectares?: true
    changedBy?: true
    changeReason?: true
    changeSource?: true
    deviceId?: true
    createdAt?: true
  }

  export type FieldBoundaryHistoryMaxAggregateInputType = {
    id?: true
    fieldId?: true
    versionAtChange?: true
    areaChangeHectares?: true
    changedBy?: true
    changeReason?: true
    changeSource?: true
    deviceId?: true
    createdAt?: true
  }

  export type FieldBoundaryHistoryCountAggregateInputType = {
    id?: true
    fieldId?: true
    versionAtChange?: true
    areaChangeHectares?: true
    changedBy?: true
    changeReason?: true
    changeSource?: true
    deviceId?: true
    createdAt?: true
    _all?: true
  }

  export type FieldBoundaryHistoryAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which FieldBoundaryHistory to aggregate.
     */
    where?: FieldBoundaryHistoryWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of FieldBoundaryHistories to fetch.
     */
    orderBy?: FieldBoundaryHistoryOrderByWithRelationInput | FieldBoundaryHistoryOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: FieldBoundaryHistoryWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` FieldBoundaryHistories from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` FieldBoundaryHistories.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned FieldBoundaryHistories
    **/
    _count?: true | FieldBoundaryHistoryCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: FieldBoundaryHistoryAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: FieldBoundaryHistorySumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: FieldBoundaryHistoryMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: FieldBoundaryHistoryMaxAggregateInputType
  }

  export type GetFieldBoundaryHistoryAggregateType<T extends FieldBoundaryHistoryAggregateArgs> = {
        [P in keyof T & keyof AggregateFieldBoundaryHistory]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateFieldBoundaryHistory[P]>
      : GetScalarType<T[P], AggregateFieldBoundaryHistory[P]>
  }




  export type FieldBoundaryHistoryGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: FieldBoundaryHistoryWhereInput
    orderBy?: FieldBoundaryHistoryOrderByWithAggregationInput | FieldBoundaryHistoryOrderByWithAggregationInput[]
    by: FieldBoundaryHistoryScalarFieldEnum[] | FieldBoundaryHistoryScalarFieldEnum
    having?: FieldBoundaryHistoryScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: FieldBoundaryHistoryCountAggregateInputType | true
    _avg?: FieldBoundaryHistoryAvgAggregateInputType
    _sum?: FieldBoundaryHistorySumAggregateInputType
    _min?: FieldBoundaryHistoryMinAggregateInputType
    _max?: FieldBoundaryHistoryMaxAggregateInputType
  }

  export type FieldBoundaryHistoryGroupByOutputType = {
    id: string
    fieldId: string
    versionAtChange: number
    areaChangeHectares: Decimal | null
    changedBy: string | null
    changeReason: string | null
    changeSource: $Enums.ChangeSource
    deviceId: string | null
    createdAt: Date
    _count: FieldBoundaryHistoryCountAggregateOutputType | null
    _avg: FieldBoundaryHistoryAvgAggregateOutputType | null
    _sum: FieldBoundaryHistorySumAggregateOutputType | null
    _min: FieldBoundaryHistoryMinAggregateOutputType | null
    _max: FieldBoundaryHistoryMaxAggregateOutputType | null
  }

  type GetFieldBoundaryHistoryGroupByPayload<T extends FieldBoundaryHistoryGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<FieldBoundaryHistoryGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof FieldBoundaryHistoryGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], FieldBoundaryHistoryGroupByOutputType[P]>
            : GetScalarType<T[P], FieldBoundaryHistoryGroupByOutputType[P]>
        }
      >
    >


  export type FieldBoundaryHistorySelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    fieldId?: boolean
    versionAtChange?: boolean
    areaChangeHectares?: boolean
    changedBy?: boolean
    changeReason?: boolean
    changeSource?: boolean
    deviceId?: boolean
    createdAt?: boolean
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["fieldBoundaryHistory"]>

  export type FieldBoundaryHistorySelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    fieldId?: boolean
    versionAtChange?: boolean
    areaChangeHectares?: boolean
    changedBy?: boolean
    changeReason?: boolean
    changeSource?: boolean
    deviceId?: boolean
    createdAt?: boolean
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["fieldBoundaryHistory"]>

  export type FieldBoundaryHistorySelectScalar = {
    id?: boolean
    fieldId?: boolean
    versionAtChange?: boolean
    areaChangeHectares?: boolean
    changedBy?: boolean
    changeReason?: boolean
    changeSource?: boolean
    deviceId?: boolean
    createdAt?: boolean
  }

  export type FieldBoundaryHistoryInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }
  export type FieldBoundaryHistoryIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }

  export type $FieldBoundaryHistoryPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "FieldBoundaryHistory"
    objects: {
      field: Prisma.$FieldPayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      fieldId: string
      versionAtChange: number
      areaChangeHectares: Prisma.Decimal | null
      changedBy: string | null
      changeReason: string | null
      changeSource: $Enums.ChangeSource
      deviceId: string | null
      createdAt: Date
    }, ExtArgs["result"]["fieldBoundaryHistory"]>
    composites: {}
  }

  type FieldBoundaryHistoryGetPayload<S extends boolean | null | undefined | FieldBoundaryHistoryDefaultArgs> = $Result.GetResult<Prisma.$FieldBoundaryHistoryPayload, S>

  type FieldBoundaryHistoryCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<FieldBoundaryHistoryFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: FieldBoundaryHistoryCountAggregateInputType | true
    }

  export interface FieldBoundaryHistoryDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['FieldBoundaryHistory'], meta: { name: 'FieldBoundaryHistory' } }
    /**
     * Find zero or one FieldBoundaryHistory that matches the filter.
     * @param {FieldBoundaryHistoryFindUniqueArgs} args - Arguments to find a FieldBoundaryHistory
     * @example
     * // Get one FieldBoundaryHistory
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends FieldBoundaryHistoryFindUniqueArgs>(args: SelectSubset<T, FieldBoundaryHistoryFindUniqueArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one FieldBoundaryHistory that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {FieldBoundaryHistoryFindUniqueOrThrowArgs} args - Arguments to find a FieldBoundaryHistory
     * @example
     * // Get one FieldBoundaryHistory
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends FieldBoundaryHistoryFindUniqueOrThrowArgs>(args: SelectSubset<T, FieldBoundaryHistoryFindUniqueOrThrowArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first FieldBoundaryHistory that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryFindFirstArgs} args - Arguments to find a FieldBoundaryHistory
     * @example
     * // Get one FieldBoundaryHistory
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends FieldBoundaryHistoryFindFirstArgs>(args?: SelectSubset<T, FieldBoundaryHistoryFindFirstArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first FieldBoundaryHistory that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryFindFirstOrThrowArgs} args - Arguments to find a FieldBoundaryHistory
     * @example
     * // Get one FieldBoundaryHistory
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends FieldBoundaryHistoryFindFirstOrThrowArgs>(args?: SelectSubset<T, FieldBoundaryHistoryFindFirstOrThrowArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more FieldBoundaryHistories that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all FieldBoundaryHistories
     * const fieldBoundaryHistories = await prisma.fieldBoundaryHistory.findMany()
     * 
     * // Get first 10 FieldBoundaryHistories
     * const fieldBoundaryHistories = await prisma.fieldBoundaryHistory.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const fieldBoundaryHistoryWithIdOnly = await prisma.fieldBoundaryHistory.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends FieldBoundaryHistoryFindManyArgs>(args?: SelectSubset<T, FieldBoundaryHistoryFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a FieldBoundaryHistory.
     * @param {FieldBoundaryHistoryCreateArgs} args - Arguments to create a FieldBoundaryHistory.
     * @example
     * // Create one FieldBoundaryHistory
     * const FieldBoundaryHistory = await prisma.fieldBoundaryHistory.create({
     *   data: {
     *     // ... data to create a FieldBoundaryHistory
     *   }
     * })
     * 
     */
    create<T extends FieldBoundaryHistoryCreateArgs>(args: SelectSubset<T, FieldBoundaryHistoryCreateArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many FieldBoundaryHistories.
     * @param {FieldBoundaryHistoryCreateManyArgs} args - Arguments to create many FieldBoundaryHistories.
     * @example
     * // Create many FieldBoundaryHistories
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends FieldBoundaryHistoryCreateManyArgs>(args?: SelectSubset<T, FieldBoundaryHistoryCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many FieldBoundaryHistories and returns the data saved in the database.
     * @param {FieldBoundaryHistoryCreateManyAndReturnArgs} args - Arguments to create many FieldBoundaryHistories.
     * @example
     * // Create many FieldBoundaryHistories
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many FieldBoundaryHistories and only return the `id`
     * const fieldBoundaryHistoryWithIdOnly = await prisma.fieldBoundaryHistory.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends FieldBoundaryHistoryCreateManyAndReturnArgs>(args?: SelectSubset<T, FieldBoundaryHistoryCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a FieldBoundaryHistory.
     * @param {FieldBoundaryHistoryDeleteArgs} args - Arguments to delete one FieldBoundaryHistory.
     * @example
     * // Delete one FieldBoundaryHistory
     * const FieldBoundaryHistory = await prisma.fieldBoundaryHistory.delete({
     *   where: {
     *     // ... filter to delete one FieldBoundaryHistory
     *   }
     * })
     * 
     */
    delete<T extends FieldBoundaryHistoryDeleteArgs>(args: SelectSubset<T, FieldBoundaryHistoryDeleteArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one FieldBoundaryHistory.
     * @param {FieldBoundaryHistoryUpdateArgs} args - Arguments to update one FieldBoundaryHistory.
     * @example
     * // Update one FieldBoundaryHistory
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends FieldBoundaryHistoryUpdateArgs>(args: SelectSubset<T, FieldBoundaryHistoryUpdateArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more FieldBoundaryHistories.
     * @param {FieldBoundaryHistoryDeleteManyArgs} args - Arguments to filter FieldBoundaryHistories to delete.
     * @example
     * // Delete a few FieldBoundaryHistories
     * const { count } = await prisma.fieldBoundaryHistory.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends FieldBoundaryHistoryDeleteManyArgs>(args?: SelectSubset<T, FieldBoundaryHistoryDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more FieldBoundaryHistories.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many FieldBoundaryHistories
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends FieldBoundaryHistoryUpdateManyArgs>(args: SelectSubset<T, FieldBoundaryHistoryUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one FieldBoundaryHistory.
     * @param {FieldBoundaryHistoryUpsertArgs} args - Arguments to update or create a FieldBoundaryHistory.
     * @example
     * // Update or create a FieldBoundaryHistory
     * const fieldBoundaryHistory = await prisma.fieldBoundaryHistory.upsert({
     *   create: {
     *     // ... data to create a FieldBoundaryHistory
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the FieldBoundaryHistory we want to update
     *   }
     * })
     */
    upsert<T extends FieldBoundaryHistoryUpsertArgs>(args: SelectSubset<T, FieldBoundaryHistoryUpsertArgs<ExtArgs>>): Prisma__FieldBoundaryHistoryClient<$Result.GetResult<Prisma.$FieldBoundaryHistoryPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of FieldBoundaryHistories.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryCountArgs} args - Arguments to filter FieldBoundaryHistories to count.
     * @example
     * // Count the number of FieldBoundaryHistories
     * const count = await prisma.fieldBoundaryHistory.count({
     *   where: {
     *     // ... the filter for the FieldBoundaryHistories we want to count
     *   }
     * })
    **/
    count<T extends FieldBoundaryHistoryCountArgs>(
      args?: Subset<T, FieldBoundaryHistoryCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], FieldBoundaryHistoryCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a FieldBoundaryHistory.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends FieldBoundaryHistoryAggregateArgs>(args: Subset<T, FieldBoundaryHistoryAggregateArgs>): Prisma.PrismaPromise<GetFieldBoundaryHistoryAggregateType<T>>

    /**
     * Group by FieldBoundaryHistory.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {FieldBoundaryHistoryGroupByArgs} args - Group by arguments.
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
      T extends FieldBoundaryHistoryGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: FieldBoundaryHistoryGroupByArgs['orderBy'] }
        : { orderBy?: FieldBoundaryHistoryGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, FieldBoundaryHistoryGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetFieldBoundaryHistoryGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the FieldBoundaryHistory model
   */
  readonly fields: FieldBoundaryHistoryFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for FieldBoundaryHistory.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__FieldBoundaryHistoryClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    field<T extends FieldDefaultArgs<ExtArgs> = {}>(args?: Subset<T, FieldDefaultArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
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
   * Fields of the FieldBoundaryHistory model
   */ 
  interface FieldBoundaryHistoryFieldRefs {
    readonly id: FieldRef<"FieldBoundaryHistory", 'String'>
    readonly fieldId: FieldRef<"FieldBoundaryHistory", 'String'>
    readonly versionAtChange: FieldRef<"FieldBoundaryHistory", 'Int'>
    readonly areaChangeHectares: FieldRef<"FieldBoundaryHistory", 'Decimal'>
    readonly changedBy: FieldRef<"FieldBoundaryHistory", 'String'>
    readonly changeReason: FieldRef<"FieldBoundaryHistory", 'String'>
    readonly changeSource: FieldRef<"FieldBoundaryHistory", 'ChangeSource'>
    readonly deviceId: FieldRef<"FieldBoundaryHistory", 'String'>
    readonly createdAt: FieldRef<"FieldBoundaryHistory", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * FieldBoundaryHistory findUnique
   */
  export type FieldBoundaryHistoryFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * Filter, which FieldBoundaryHistory to fetch.
     */
    where: FieldBoundaryHistoryWhereUniqueInput
  }

  /**
   * FieldBoundaryHistory findUniqueOrThrow
   */
  export type FieldBoundaryHistoryFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * Filter, which FieldBoundaryHistory to fetch.
     */
    where: FieldBoundaryHistoryWhereUniqueInput
  }

  /**
   * FieldBoundaryHistory findFirst
   */
  export type FieldBoundaryHistoryFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * Filter, which FieldBoundaryHistory to fetch.
     */
    where?: FieldBoundaryHistoryWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of FieldBoundaryHistories to fetch.
     */
    orderBy?: FieldBoundaryHistoryOrderByWithRelationInput | FieldBoundaryHistoryOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for FieldBoundaryHistories.
     */
    cursor?: FieldBoundaryHistoryWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` FieldBoundaryHistories from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` FieldBoundaryHistories.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of FieldBoundaryHistories.
     */
    distinct?: FieldBoundaryHistoryScalarFieldEnum | FieldBoundaryHistoryScalarFieldEnum[]
  }

  /**
   * FieldBoundaryHistory findFirstOrThrow
   */
  export type FieldBoundaryHistoryFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * Filter, which FieldBoundaryHistory to fetch.
     */
    where?: FieldBoundaryHistoryWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of FieldBoundaryHistories to fetch.
     */
    orderBy?: FieldBoundaryHistoryOrderByWithRelationInput | FieldBoundaryHistoryOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for FieldBoundaryHistories.
     */
    cursor?: FieldBoundaryHistoryWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` FieldBoundaryHistories from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` FieldBoundaryHistories.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of FieldBoundaryHistories.
     */
    distinct?: FieldBoundaryHistoryScalarFieldEnum | FieldBoundaryHistoryScalarFieldEnum[]
  }

  /**
   * FieldBoundaryHistory findMany
   */
  export type FieldBoundaryHistoryFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * Filter, which FieldBoundaryHistories to fetch.
     */
    where?: FieldBoundaryHistoryWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of FieldBoundaryHistories to fetch.
     */
    orderBy?: FieldBoundaryHistoryOrderByWithRelationInput | FieldBoundaryHistoryOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing FieldBoundaryHistories.
     */
    cursor?: FieldBoundaryHistoryWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` FieldBoundaryHistories from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` FieldBoundaryHistories.
     */
    skip?: number
    distinct?: FieldBoundaryHistoryScalarFieldEnum | FieldBoundaryHistoryScalarFieldEnum[]
  }

  /**
   * FieldBoundaryHistory create
   */
  export type FieldBoundaryHistoryCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * The data needed to create a FieldBoundaryHistory.
     */
    data: XOR<FieldBoundaryHistoryCreateInput, FieldBoundaryHistoryUncheckedCreateInput>
  }

  /**
   * FieldBoundaryHistory createMany
   */
  export type FieldBoundaryHistoryCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many FieldBoundaryHistories.
     */
    data: FieldBoundaryHistoryCreateManyInput | FieldBoundaryHistoryCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * FieldBoundaryHistory createManyAndReturn
   */
  export type FieldBoundaryHistoryCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many FieldBoundaryHistories.
     */
    data: FieldBoundaryHistoryCreateManyInput | FieldBoundaryHistoryCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * FieldBoundaryHistory update
   */
  export type FieldBoundaryHistoryUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * The data needed to update a FieldBoundaryHistory.
     */
    data: XOR<FieldBoundaryHistoryUpdateInput, FieldBoundaryHistoryUncheckedUpdateInput>
    /**
     * Choose, which FieldBoundaryHistory to update.
     */
    where: FieldBoundaryHistoryWhereUniqueInput
  }

  /**
   * FieldBoundaryHistory updateMany
   */
  export type FieldBoundaryHistoryUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update FieldBoundaryHistories.
     */
    data: XOR<FieldBoundaryHistoryUpdateManyMutationInput, FieldBoundaryHistoryUncheckedUpdateManyInput>
    /**
     * Filter which FieldBoundaryHistories to update
     */
    where?: FieldBoundaryHistoryWhereInput
  }

  /**
   * FieldBoundaryHistory upsert
   */
  export type FieldBoundaryHistoryUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * The filter to search for the FieldBoundaryHistory to update in case it exists.
     */
    where: FieldBoundaryHistoryWhereUniqueInput
    /**
     * In case the FieldBoundaryHistory found by the `where` argument doesn't exist, create a new FieldBoundaryHistory with this data.
     */
    create: XOR<FieldBoundaryHistoryCreateInput, FieldBoundaryHistoryUncheckedCreateInput>
    /**
     * In case the FieldBoundaryHistory was found with the provided `where` argument, update it with this data.
     */
    update: XOR<FieldBoundaryHistoryUpdateInput, FieldBoundaryHistoryUncheckedUpdateInput>
  }

  /**
   * FieldBoundaryHistory delete
   */
  export type FieldBoundaryHistoryDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
    /**
     * Filter which FieldBoundaryHistory to delete.
     */
    where: FieldBoundaryHistoryWhereUniqueInput
  }

  /**
   * FieldBoundaryHistory deleteMany
   */
  export type FieldBoundaryHistoryDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which FieldBoundaryHistories to delete
     */
    where?: FieldBoundaryHistoryWhereInput
  }

  /**
   * FieldBoundaryHistory without action
   */
  export type FieldBoundaryHistoryDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the FieldBoundaryHistory
     */
    select?: FieldBoundaryHistorySelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldBoundaryHistoryInclude<ExtArgs> | null
  }


  /**
   * Model SyncStatus
   */

  export type AggregateSyncStatus = {
    _count: SyncStatusCountAggregateOutputType | null
    _avg: SyncStatusAvgAggregateOutputType | null
    _sum: SyncStatusSumAggregateOutputType | null
    _min: SyncStatusMinAggregateOutputType | null
    _max: SyncStatusMaxAggregateOutputType | null
  }

  export type SyncStatusAvgAggregateOutputType = {
    lastSyncVersion: number | null
    pendingUploads: number | null
    pendingDownloads: number | null
    conflictsCount: number | null
  }

  export type SyncStatusSumAggregateOutputType = {
    lastSyncVersion: bigint | null
    pendingUploads: number | null
    pendingDownloads: number | null
    conflictsCount: number | null
  }

  export type SyncStatusMinAggregateOutputType = {
    id: string | null
    deviceId: string | null
    userId: string | null
    tenantId: string | null
    lastSyncAt: Date | null
    lastSyncVersion: bigint | null
    status: $Enums.SyncState | null
    pendingUploads: number | null
    pendingDownloads: number | null
    conflictsCount: number | null
    lastError: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type SyncStatusMaxAggregateOutputType = {
    id: string | null
    deviceId: string | null
    userId: string | null
    tenantId: string | null
    lastSyncAt: Date | null
    lastSyncVersion: bigint | null
    status: $Enums.SyncState | null
    pendingUploads: number | null
    pendingDownloads: number | null
    conflictsCount: number | null
    lastError: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type SyncStatusCountAggregateOutputType = {
    id: number
    deviceId: number
    userId: number
    tenantId: number
    lastSyncAt: number
    lastSyncVersion: number
    status: number
    pendingUploads: number
    pendingDownloads: number
    conflictsCount: number
    lastError: number
    deviceInfo: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type SyncStatusAvgAggregateInputType = {
    lastSyncVersion?: true
    pendingUploads?: true
    pendingDownloads?: true
    conflictsCount?: true
  }

  export type SyncStatusSumAggregateInputType = {
    lastSyncVersion?: true
    pendingUploads?: true
    pendingDownloads?: true
    conflictsCount?: true
  }

  export type SyncStatusMinAggregateInputType = {
    id?: true
    deviceId?: true
    userId?: true
    tenantId?: true
    lastSyncAt?: true
    lastSyncVersion?: true
    status?: true
    pendingUploads?: true
    pendingDownloads?: true
    conflictsCount?: true
    lastError?: true
    createdAt?: true
    updatedAt?: true
  }

  export type SyncStatusMaxAggregateInputType = {
    id?: true
    deviceId?: true
    userId?: true
    tenantId?: true
    lastSyncAt?: true
    lastSyncVersion?: true
    status?: true
    pendingUploads?: true
    pendingDownloads?: true
    conflictsCount?: true
    lastError?: true
    createdAt?: true
    updatedAt?: true
  }

  export type SyncStatusCountAggregateInputType = {
    id?: true
    deviceId?: true
    userId?: true
    tenantId?: true
    lastSyncAt?: true
    lastSyncVersion?: true
    status?: true
    pendingUploads?: true
    pendingDownloads?: true
    conflictsCount?: true
    lastError?: true
    deviceInfo?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type SyncStatusAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which SyncStatus to aggregate.
     */
    where?: SyncStatusWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SyncStatuses to fetch.
     */
    orderBy?: SyncStatusOrderByWithRelationInput | SyncStatusOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: SyncStatusWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SyncStatuses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SyncStatuses.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned SyncStatuses
    **/
    _count?: true | SyncStatusCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: SyncStatusAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: SyncStatusSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: SyncStatusMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: SyncStatusMaxAggregateInputType
  }

  export type GetSyncStatusAggregateType<T extends SyncStatusAggregateArgs> = {
        [P in keyof T & keyof AggregateSyncStatus]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateSyncStatus[P]>
      : GetScalarType<T[P], AggregateSyncStatus[P]>
  }




  export type SyncStatusGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: SyncStatusWhereInput
    orderBy?: SyncStatusOrderByWithAggregationInput | SyncStatusOrderByWithAggregationInput[]
    by: SyncStatusScalarFieldEnum[] | SyncStatusScalarFieldEnum
    having?: SyncStatusScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: SyncStatusCountAggregateInputType | true
    _avg?: SyncStatusAvgAggregateInputType
    _sum?: SyncStatusSumAggregateInputType
    _min?: SyncStatusMinAggregateInputType
    _max?: SyncStatusMaxAggregateInputType
  }

  export type SyncStatusGroupByOutputType = {
    id: string
    deviceId: string
    userId: string
    tenantId: string
    lastSyncAt: Date | null
    lastSyncVersion: bigint
    status: $Enums.SyncState
    pendingUploads: number
    pendingDownloads: number
    conflictsCount: number
    lastError: string | null
    deviceInfo: JsonValue | null
    createdAt: Date
    updatedAt: Date
    _count: SyncStatusCountAggregateOutputType | null
    _avg: SyncStatusAvgAggregateOutputType | null
    _sum: SyncStatusSumAggregateOutputType | null
    _min: SyncStatusMinAggregateOutputType | null
    _max: SyncStatusMaxAggregateOutputType | null
  }

  type GetSyncStatusGroupByPayload<T extends SyncStatusGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<SyncStatusGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof SyncStatusGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], SyncStatusGroupByOutputType[P]>
            : GetScalarType<T[P], SyncStatusGroupByOutputType[P]>
        }
      >
    >


  export type SyncStatusSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    userId?: boolean
    tenantId?: boolean
    lastSyncAt?: boolean
    lastSyncVersion?: boolean
    status?: boolean
    pendingUploads?: boolean
    pendingDownloads?: boolean
    conflictsCount?: boolean
    lastError?: boolean
    deviceInfo?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["syncStatus"]>

  export type SyncStatusSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    deviceId?: boolean
    userId?: boolean
    tenantId?: boolean
    lastSyncAt?: boolean
    lastSyncVersion?: boolean
    status?: boolean
    pendingUploads?: boolean
    pendingDownloads?: boolean
    conflictsCount?: boolean
    lastError?: boolean
    deviceInfo?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["syncStatus"]>

  export type SyncStatusSelectScalar = {
    id?: boolean
    deviceId?: boolean
    userId?: boolean
    tenantId?: boolean
    lastSyncAt?: boolean
    lastSyncVersion?: boolean
    status?: boolean
    pendingUploads?: boolean
    pendingDownloads?: boolean
    conflictsCount?: boolean
    lastError?: boolean
    deviceInfo?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }


  export type $SyncStatusPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "SyncStatus"
    objects: {}
    scalars: $Extensions.GetPayloadResult<{
      id: string
      deviceId: string
      userId: string
      tenantId: string
      lastSyncAt: Date | null
      lastSyncVersion: bigint
      status: $Enums.SyncState
      pendingUploads: number
      pendingDownloads: number
      conflictsCount: number
      lastError: string | null
      deviceInfo: Prisma.JsonValue | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["syncStatus"]>
    composites: {}
  }

  type SyncStatusGetPayload<S extends boolean | null | undefined | SyncStatusDefaultArgs> = $Result.GetResult<Prisma.$SyncStatusPayload, S>

  type SyncStatusCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<SyncStatusFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: SyncStatusCountAggregateInputType | true
    }

  export interface SyncStatusDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['SyncStatus'], meta: { name: 'SyncStatus' } }
    /**
     * Find zero or one SyncStatus that matches the filter.
     * @param {SyncStatusFindUniqueArgs} args - Arguments to find a SyncStatus
     * @example
     * // Get one SyncStatus
     * const syncStatus = await prisma.syncStatus.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends SyncStatusFindUniqueArgs>(args: SelectSubset<T, SyncStatusFindUniqueArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one SyncStatus that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {SyncStatusFindUniqueOrThrowArgs} args - Arguments to find a SyncStatus
     * @example
     * // Get one SyncStatus
     * const syncStatus = await prisma.syncStatus.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends SyncStatusFindUniqueOrThrowArgs>(args: SelectSubset<T, SyncStatusFindUniqueOrThrowArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first SyncStatus that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusFindFirstArgs} args - Arguments to find a SyncStatus
     * @example
     * // Get one SyncStatus
     * const syncStatus = await prisma.syncStatus.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends SyncStatusFindFirstArgs>(args?: SelectSubset<T, SyncStatusFindFirstArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first SyncStatus that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusFindFirstOrThrowArgs} args - Arguments to find a SyncStatus
     * @example
     * // Get one SyncStatus
     * const syncStatus = await prisma.syncStatus.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends SyncStatusFindFirstOrThrowArgs>(args?: SelectSubset<T, SyncStatusFindFirstOrThrowArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more SyncStatuses that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all SyncStatuses
     * const syncStatuses = await prisma.syncStatus.findMany()
     * 
     * // Get first 10 SyncStatuses
     * const syncStatuses = await prisma.syncStatus.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const syncStatusWithIdOnly = await prisma.syncStatus.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends SyncStatusFindManyArgs>(args?: SelectSubset<T, SyncStatusFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a SyncStatus.
     * @param {SyncStatusCreateArgs} args - Arguments to create a SyncStatus.
     * @example
     * // Create one SyncStatus
     * const SyncStatus = await prisma.syncStatus.create({
     *   data: {
     *     // ... data to create a SyncStatus
     *   }
     * })
     * 
     */
    create<T extends SyncStatusCreateArgs>(args: SelectSubset<T, SyncStatusCreateArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many SyncStatuses.
     * @param {SyncStatusCreateManyArgs} args - Arguments to create many SyncStatuses.
     * @example
     * // Create many SyncStatuses
     * const syncStatus = await prisma.syncStatus.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends SyncStatusCreateManyArgs>(args?: SelectSubset<T, SyncStatusCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many SyncStatuses and returns the data saved in the database.
     * @param {SyncStatusCreateManyAndReturnArgs} args - Arguments to create many SyncStatuses.
     * @example
     * // Create many SyncStatuses
     * const syncStatus = await prisma.syncStatus.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many SyncStatuses and only return the `id`
     * const syncStatusWithIdOnly = await prisma.syncStatus.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends SyncStatusCreateManyAndReturnArgs>(args?: SelectSubset<T, SyncStatusCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a SyncStatus.
     * @param {SyncStatusDeleteArgs} args - Arguments to delete one SyncStatus.
     * @example
     * // Delete one SyncStatus
     * const SyncStatus = await prisma.syncStatus.delete({
     *   where: {
     *     // ... filter to delete one SyncStatus
     *   }
     * })
     * 
     */
    delete<T extends SyncStatusDeleteArgs>(args: SelectSubset<T, SyncStatusDeleteArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one SyncStatus.
     * @param {SyncStatusUpdateArgs} args - Arguments to update one SyncStatus.
     * @example
     * // Update one SyncStatus
     * const syncStatus = await prisma.syncStatus.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends SyncStatusUpdateArgs>(args: SelectSubset<T, SyncStatusUpdateArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more SyncStatuses.
     * @param {SyncStatusDeleteManyArgs} args - Arguments to filter SyncStatuses to delete.
     * @example
     * // Delete a few SyncStatuses
     * const { count } = await prisma.syncStatus.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends SyncStatusDeleteManyArgs>(args?: SelectSubset<T, SyncStatusDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more SyncStatuses.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many SyncStatuses
     * const syncStatus = await prisma.syncStatus.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends SyncStatusUpdateManyArgs>(args: SelectSubset<T, SyncStatusUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one SyncStatus.
     * @param {SyncStatusUpsertArgs} args - Arguments to update or create a SyncStatus.
     * @example
     * // Update or create a SyncStatus
     * const syncStatus = await prisma.syncStatus.upsert({
     *   create: {
     *     // ... data to create a SyncStatus
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the SyncStatus we want to update
     *   }
     * })
     */
    upsert<T extends SyncStatusUpsertArgs>(args: SelectSubset<T, SyncStatusUpsertArgs<ExtArgs>>): Prisma__SyncStatusClient<$Result.GetResult<Prisma.$SyncStatusPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of SyncStatuses.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusCountArgs} args - Arguments to filter SyncStatuses to count.
     * @example
     * // Count the number of SyncStatuses
     * const count = await prisma.syncStatus.count({
     *   where: {
     *     // ... the filter for the SyncStatuses we want to count
     *   }
     * })
    **/
    count<T extends SyncStatusCountArgs>(
      args?: Subset<T, SyncStatusCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], SyncStatusCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a SyncStatus.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends SyncStatusAggregateArgs>(args: Subset<T, SyncStatusAggregateArgs>): Prisma.PrismaPromise<GetSyncStatusAggregateType<T>>

    /**
     * Group by SyncStatus.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {SyncStatusGroupByArgs} args - Group by arguments.
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
      T extends SyncStatusGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: SyncStatusGroupByArgs['orderBy'] }
        : { orderBy?: SyncStatusGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, SyncStatusGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetSyncStatusGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the SyncStatus model
   */
  readonly fields: SyncStatusFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for SyncStatus.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__SyncStatusClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
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
   * Fields of the SyncStatus model
   */ 
  interface SyncStatusFieldRefs {
    readonly id: FieldRef<"SyncStatus", 'String'>
    readonly deviceId: FieldRef<"SyncStatus", 'String'>
    readonly userId: FieldRef<"SyncStatus", 'String'>
    readonly tenantId: FieldRef<"SyncStatus", 'String'>
    readonly lastSyncAt: FieldRef<"SyncStatus", 'DateTime'>
    readonly lastSyncVersion: FieldRef<"SyncStatus", 'BigInt'>
    readonly status: FieldRef<"SyncStatus", 'SyncState'>
    readonly pendingUploads: FieldRef<"SyncStatus", 'Int'>
    readonly pendingDownloads: FieldRef<"SyncStatus", 'Int'>
    readonly conflictsCount: FieldRef<"SyncStatus", 'Int'>
    readonly lastError: FieldRef<"SyncStatus", 'String'>
    readonly deviceInfo: FieldRef<"SyncStatus", 'Json'>
    readonly createdAt: FieldRef<"SyncStatus", 'DateTime'>
    readonly updatedAt: FieldRef<"SyncStatus", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * SyncStatus findUnique
   */
  export type SyncStatusFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * Filter, which SyncStatus to fetch.
     */
    where: SyncStatusWhereUniqueInput
  }

  /**
   * SyncStatus findUniqueOrThrow
   */
  export type SyncStatusFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * Filter, which SyncStatus to fetch.
     */
    where: SyncStatusWhereUniqueInput
  }

  /**
   * SyncStatus findFirst
   */
  export type SyncStatusFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * Filter, which SyncStatus to fetch.
     */
    where?: SyncStatusWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SyncStatuses to fetch.
     */
    orderBy?: SyncStatusOrderByWithRelationInput | SyncStatusOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for SyncStatuses.
     */
    cursor?: SyncStatusWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SyncStatuses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SyncStatuses.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of SyncStatuses.
     */
    distinct?: SyncStatusScalarFieldEnum | SyncStatusScalarFieldEnum[]
  }

  /**
   * SyncStatus findFirstOrThrow
   */
  export type SyncStatusFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * Filter, which SyncStatus to fetch.
     */
    where?: SyncStatusWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SyncStatuses to fetch.
     */
    orderBy?: SyncStatusOrderByWithRelationInput | SyncStatusOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for SyncStatuses.
     */
    cursor?: SyncStatusWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SyncStatuses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SyncStatuses.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of SyncStatuses.
     */
    distinct?: SyncStatusScalarFieldEnum | SyncStatusScalarFieldEnum[]
  }

  /**
   * SyncStatus findMany
   */
  export type SyncStatusFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * Filter, which SyncStatuses to fetch.
     */
    where?: SyncStatusWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of SyncStatuses to fetch.
     */
    orderBy?: SyncStatusOrderByWithRelationInput | SyncStatusOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing SyncStatuses.
     */
    cursor?: SyncStatusWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` SyncStatuses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` SyncStatuses.
     */
    skip?: number
    distinct?: SyncStatusScalarFieldEnum | SyncStatusScalarFieldEnum[]
  }

  /**
   * SyncStatus create
   */
  export type SyncStatusCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * The data needed to create a SyncStatus.
     */
    data: XOR<SyncStatusCreateInput, SyncStatusUncheckedCreateInput>
  }

  /**
   * SyncStatus createMany
   */
  export type SyncStatusCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many SyncStatuses.
     */
    data: SyncStatusCreateManyInput | SyncStatusCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * SyncStatus createManyAndReturn
   */
  export type SyncStatusCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many SyncStatuses.
     */
    data: SyncStatusCreateManyInput | SyncStatusCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * SyncStatus update
   */
  export type SyncStatusUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * The data needed to update a SyncStatus.
     */
    data: XOR<SyncStatusUpdateInput, SyncStatusUncheckedUpdateInput>
    /**
     * Choose, which SyncStatus to update.
     */
    where: SyncStatusWhereUniqueInput
  }

  /**
   * SyncStatus updateMany
   */
  export type SyncStatusUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update SyncStatuses.
     */
    data: XOR<SyncStatusUpdateManyMutationInput, SyncStatusUncheckedUpdateManyInput>
    /**
     * Filter which SyncStatuses to update
     */
    where?: SyncStatusWhereInput
  }

  /**
   * SyncStatus upsert
   */
  export type SyncStatusUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * The filter to search for the SyncStatus to update in case it exists.
     */
    where: SyncStatusWhereUniqueInput
    /**
     * In case the SyncStatus found by the `where` argument doesn't exist, create a new SyncStatus with this data.
     */
    create: XOR<SyncStatusCreateInput, SyncStatusUncheckedCreateInput>
    /**
     * In case the SyncStatus was found with the provided `where` argument, update it with this data.
     */
    update: XOR<SyncStatusUpdateInput, SyncStatusUncheckedUpdateInput>
  }

  /**
   * SyncStatus delete
   */
  export type SyncStatusDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
    /**
     * Filter which SyncStatus to delete.
     */
    where: SyncStatusWhereUniqueInput
  }

  /**
   * SyncStatus deleteMany
   */
  export type SyncStatusDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which SyncStatuses to delete
     */
    where?: SyncStatusWhereInput
  }

  /**
   * SyncStatus without action
   */
  export type SyncStatusDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the SyncStatus
     */
    select?: SyncStatusSelect<ExtArgs> | null
  }


  /**
   * Model Task
   */

  export type AggregateTask = {
    _count: TaskCountAggregateOutputType | null
    _avg: TaskAvgAggregateOutputType | null
    _sum: TaskSumAggregateOutputType | null
    _min: TaskMinAggregateOutputType | null
    _max: TaskMaxAggregateOutputType | null
  }

  export type TaskAvgAggregateOutputType = {
    estimatedMinutes: number | null
    actualMinutes: number | null
  }

  export type TaskSumAggregateOutputType = {
    estimatedMinutes: number | null
    actualMinutes: number | null
  }

  export type TaskMinAggregateOutputType = {
    id: string | null
    title: string | null
    titleAr: string | null
    description: string | null
    taskType: $Enums.TaskType | null
    priority: $Enums.Priority | null
    status: $Enums.TaskState | null
    dueDate: Date | null
    scheduledTime: string | null
    completedAt: Date | null
    assignedTo: string | null
    createdBy: string | null
    fieldId: string | null
    estimatedMinutes: number | null
    actualMinutes: number | null
    completionNotes: string | null
    serverUpdatedAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type TaskMaxAggregateOutputType = {
    id: string | null
    title: string | null
    titleAr: string | null
    description: string | null
    taskType: $Enums.TaskType | null
    priority: $Enums.Priority | null
    status: $Enums.TaskState | null
    dueDate: Date | null
    scheduledTime: string | null
    completedAt: Date | null
    assignedTo: string | null
    createdBy: string | null
    fieldId: string | null
    estimatedMinutes: number | null
    actualMinutes: number | null
    completionNotes: string | null
    serverUpdatedAt: Date | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type TaskCountAggregateOutputType = {
    id: number
    title: number
    titleAr: number
    description: number
    taskType: number
    priority: number
    status: number
    dueDate: number
    scheduledTime: number
    completedAt: number
    assignedTo: number
    createdBy: number
    fieldId: number
    estimatedMinutes: number
    actualMinutes: number
    completionNotes: number
    evidence: number
    serverUpdatedAt: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type TaskAvgAggregateInputType = {
    estimatedMinutes?: true
    actualMinutes?: true
  }

  export type TaskSumAggregateInputType = {
    estimatedMinutes?: true
    actualMinutes?: true
  }

  export type TaskMinAggregateInputType = {
    id?: true
    title?: true
    titleAr?: true
    description?: true
    taskType?: true
    priority?: true
    status?: true
    dueDate?: true
    scheduledTime?: true
    completedAt?: true
    assignedTo?: true
    createdBy?: true
    fieldId?: true
    estimatedMinutes?: true
    actualMinutes?: true
    completionNotes?: true
    serverUpdatedAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type TaskMaxAggregateInputType = {
    id?: true
    title?: true
    titleAr?: true
    description?: true
    taskType?: true
    priority?: true
    status?: true
    dueDate?: true
    scheduledTime?: true
    completedAt?: true
    assignedTo?: true
    createdBy?: true
    fieldId?: true
    estimatedMinutes?: true
    actualMinutes?: true
    completionNotes?: true
    serverUpdatedAt?: true
    createdAt?: true
    updatedAt?: true
  }

  export type TaskCountAggregateInputType = {
    id?: true
    title?: true
    titleAr?: true
    description?: true
    taskType?: true
    priority?: true
    status?: true
    dueDate?: true
    scheduledTime?: true
    completedAt?: true
    assignedTo?: true
    createdBy?: true
    fieldId?: true
    estimatedMinutes?: true
    actualMinutes?: true
    completionNotes?: true
    evidence?: true
    serverUpdatedAt?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type TaskAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Task to aggregate.
     */
    where?: TaskWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Tasks to fetch.
     */
    orderBy?: TaskOrderByWithRelationInput | TaskOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: TaskWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Tasks from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Tasks.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Tasks
    **/
    _count?: true | TaskCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: TaskAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: TaskSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: TaskMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: TaskMaxAggregateInputType
  }

  export type GetTaskAggregateType<T extends TaskAggregateArgs> = {
        [P in keyof T & keyof AggregateTask]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateTask[P]>
      : GetScalarType<T[P], AggregateTask[P]>
  }




  export type TaskGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: TaskWhereInput
    orderBy?: TaskOrderByWithAggregationInput | TaskOrderByWithAggregationInput[]
    by: TaskScalarFieldEnum[] | TaskScalarFieldEnum
    having?: TaskScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: TaskCountAggregateInputType | true
    _avg?: TaskAvgAggregateInputType
    _sum?: TaskSumAggregateInputType
    _min?: TaskMinAggregateInputType
    _max?: TaskMaxAggregateInputType
  }

  export type TaskGroupByOutputType = {
    id: string
    title: string
    titleAr: string | null
    description: string | null
    taskType: $Enums.TaskType
    priority: $Enums.Priority
    status: $Enums.TaskState
    dueDate: Date | null
    scheduledTime: string | null
    completedAt: Date | null
    assignedTo: string | null
    createdBy: string
    fieldId: string | null
    estimatedMinutes: number | null
    actualMinutes: number | null
    completionNotes: string | null
    evidence: JsonValue | null
    serverUpdatedAt: Date
    createdAt: Date
    updatedAt: Date
    _count: TaskCountAggregateOutputType | null
    _avg: TaskAvgAggregateOutputType | null
    _sum: TaskSumAggregateOutputType | null
    _min: TaskMinAggregateOutputType | null
    _max: TaskMaxAggregateOutputType | null
  }

  type GetTaskGroupByPayload<T extends TaskGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<TaskGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof TaskGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], TaskGroupByOutputType[P]>
            : GetScalarType<T[P], TaskGroupByOutputType[P]>
        }
      >
    >


  export type TaskSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    title?: boolean
    titleAr?: boolean
    description?: boolean
    taskType?: boolean
    priority?: boolean
    status?: boolean
    dueDate?: boolean
    scheduledTime?: boolean
    completedAt?: boolean
    assignedTo?: boolean
    createdBy?: boolean
    fieldId?: boolean
    estimatedMinutes?: boolean
    actualMinutes?: boolean
    completionNotes?: boolean
    evidence?: boolean
    serverUpdatedAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    field?: boolean | Task$fieldArgs<ExtArgs>
  }, ExtArgs["result"]["task"]>

  export type TaskSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    title?: boolean
    titleAr?: boolean
    description?: boolean
    taskType?: boolean
    priority?: boolean
    status?: boolean
    dueDate?: boolean
    scheduledTime?: boolean
    completedAt?: boolean
    assignedTo?: boolean
    createdBy?: boolean
    fieldId?: boolean
    estimatedMinutes?: boolean
    actualMinutes?: boolean
    completionNotes?: boolean
    evidence?: boolean
    serverUpdatedAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    field?: boolean | Task$fieldArgs<ExtArgs>
  }, ExtArgs["result"]["task"]>

  export type TaskSelectScalar = {
    id?: boolean
    title?: boolean
    titleAr?: boolean
    description?: boolean
    taskType?: boolean
    priority?: boolean
    status?: boolean
    dueDate?: boolean
    scheduledTime?: boolean
    completedAt?: boolean
    assignedTo?: boolean
    createdBy?: boolean
    fieldId?: boolean
    estimatedMinutes?: boolean
    actualMinutes?: boolean
    completionNotes?: boolean
    evidence?: boolean
    serverUpdatedAt?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type TaskInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    field?: boolean | Task$fieldArgs<ExtArgs>
  }
  export type TaskIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    field?: boolean | Task$fieldArgs<ExtArgs>
  }

  export type $TaskPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Task"
    objects: {
      field: Prisma.$FieldPayload<ExtArgs> | null
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      title: string
      titleAr: string | null
      description: string | null
      taskType: $Enums.TaskType
      priority: $Enums.Priority
      status: $Enums.TaskState
      dueDate: Date | null
      scheduledTime: string | null
      completedAt: Date | null
      assignedTo: string | null
      createdBy: string
      fieldId: string | null
      estimatedMinutes: number | null
      actualMinutes: number | null
      completionNotes: string | null
      evidence: Prisma.JsonValue | null
      serverUpdatedAt: Date
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["task"]>
    composites: {}
  }

  type TaskGetPayload<S extends boolean | null | undefined | TaskDefaultArgs> = $Result.GetResult<Prisma.$TaskPayload, S>

  type TaskCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<TaskFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: TaskCountAggregateInputType | true
    }

  export interface TaskDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Task'], meta: { name: 'Task' } }
    /**
     * Find zero or one Task that matches the filter.
     * @param {TaskFindUniqueArgs} args - Arguments to find a Task
     * @example
     * // Get one Task
     * const task = await prisma.task.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends TaskFindUniqueArgs>(args: SelectSubset<T, TaskFindUniqueArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Task that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {TaskFindUniqueOrThrowArgs} args - Arguments to find a Task
     * @example
     * // Get one Task
     * const task = await prisma.task.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends TaskFindUniqueOrThrowArgs>(args: SelectSubset<T, TaskFindUniqueOrThrowArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Task that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskFindFirstArgs} args - Arguments to find a Task
     * @example
     * // Get one Task
     * const task = await prisma.task.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends TaskFindFirstArgs>(args?: SelectSubset<T, TaskFindFirstArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Task that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskFindFirstOrThrowArgs} args - Arguments to find a Task
     * @example
     * // Get one Task
     * const task = await prisma.task.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends TaskFindFirstOrThrowArgs>(args?: SelectSubset<T, TaskFindFirstOrThrowArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Tasks that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Tasks
     * const tasks = await prisma.task.findMany()
     * 
     * // Get first 10 Tasks
     * const tasks = await prisma.task.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const taskWithIdOnly = await prisma.task.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends TaskFindManyArgs>(args?: SelectSubset<T, TaskFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Task.
     * @param {TaskCreateArgs} args - Arguments to create a Task.
     * @example
     * // Create one Task
     * const Task = await prisma.task.create({
     *   data: {
     *     // ... data to create a Task
     *   }
     * })
     * 
     */
    create<T extends TaskCreateArgs>(args: SelectSubset<T, TaskCreateArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Tasks.
     * @param {TaskCreateManyArgs} args - Arguments to create many Tasks.
     * @example
     * // Create many Tasks
     * const task = await prisma.task.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends TaskCreateManyArgs>(args?: SelectSubset<T, TaskCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Tasks and returns the data saved in the database.
     * @param {TaskCreateManyAndReturnArgs} args - Arguments to create many Tasks.
     * @example
     * // Create many Tasks
     * const task = await prisma.task.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Tasks and only return the `id`
     * const taskWithIdOnly = await prisma.task.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends TaskCreateManyAndReturnArgs>(args?: SelectSubset<T, TaskCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Task.
     * @param {TaskDeleteArgs} args - Arguments to delete one Task.
     * @example
     * // Delete one Task
     * const Task = await prisma.task.delete({
     *   where: {
     *     // ... filter to delete one Task
     *   }
     * })
     * 
     */
    delete<T extends TaskDeleteArgs>(args: SelectSubset<T, TaskDeleteArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Task.
     * @param {TaskUpdateArgs} args - Arguments to update one Task.
     * @example
     * // Update one Task
     * const task = await prisma.task.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends TaskUpdateArgs>(args: SelectSubset<T, TaskUpdateArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Tasks.
     * @param {TaskDeleteManyArgs} args - Arguments to filter Tasks to delete.
     * @example
     * // Delete a few Tasks
     * const { count } = await prisma.task.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends TaskDeleteManyArgs>(args?: SelectSubset<T, TaskDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Tasks.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Tasks
     * const task = await prisma.task.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends TaskUpdateManyArgs>(args: SelectSubset<T, TaskUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Task.
     * @param {TaskUpsertArgs} args - Arguments to update or create a Task.
     * @example
     * // Update or create a Task
     * const task = await prisma.task.upsert({
     *   create: {
     *     // ... data to create a Task
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Task we want to update
     *   }
     * })
     */
    upsert<T extends TaskUpsertArgs>(args: SelectSubset<T, TaskUpsertArgs<ExtArgs>>): Prisma__TaskClient<$Result.GetResult<Prisma.$TaskPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Tasks.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskCountArgs} args - Arguments to filter Tasks to count.
     * @example
     * // Count the number of Tasks
     * const count = await prisma.task.count({
     *   where: {
     *     // ... the filter for the Tasks we want to count
     *   }
     * })
    **/
    count<T extends TaskCountArgs>(
      args?: Subset<T, TaskCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], TaskCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Task.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends TaskAggregateArgs>(args: Subset<T, TaskAggregateArgs>): Prisma.PrismaPromise<GetTaskAggregateType<T>>

    /**
     * Group by Task.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {TaskGroupByArgs} args - Group by arguments.
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
      T extends TaskGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: TaskGroupByArgs['orderBy'] }
        : { orderBy?: TaskGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, TaskGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetTaskGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Task model
   */
  readonly fields: TaskFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Task.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__TaskClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    field<T extends Task$fieldArgs<ExtArgs> = {}>(args?: Subset<T, Task$fieldArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findUniqueOrThrow"> | null, null, ExtArgs>
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
   * Fields of the Task model
   */ 
  interface TaskFieldRefs {
    readonly id: FieldRef<"Task", 'String'>
    readonly title: FieldRef<"Task", 'String'>
    readonly titleAr: FieldRef<"Task", 'String'>
    readonly description: FieldRef<"Task", 'String'>
    readonly taskType: FieldRef<"Task", 'TaskType'>
    readonly priority: FieldRef<"Task", 'Priority'>
    readonly status: FieldRef<"Task", 'TaskState'>
    readonly dueDate: FieldRef<"Task", 'DateTime'>
    readonly scheduledTime: FieldRef<"Task", 'String'>
    readonly completedAt: FieldRef<"Task", 'DateTime'>
    readonly assignedTo: FieldRef<"Task", 'String'>
    readonly createdBy: FieldRef<"Task", 'String'>
    readonly fieldId: FieldRef<"Task", 'String'>
    readonly estimatedMinutes: FieldRef<"Task", 'Int'>
    readonly actualMinutes: FieldRef<"Task", 'Int'>
    readonly completionNotes: FieldRef<"Task", 'String'>
    readonly evidence: FieldRef<"Task", 'Json'>
    readonly serverUpdatedAt: FieldRef<"Task", 'DateTime'>
    readonly createdAt: FieldRef<"Task", 'DateTime'>
    readonly updatedAt: FieldRef<"Task", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Task findUnique
   */
  export type TaskFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * Filter, which Task to fetch.
     */
    where: TaskWhereUniqueInput
  }

  /**
   * Task findUniqueOrThrow
   */
  export type TaskFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * Filter, which Task to fetch.
     */
    where: TaskWhereUniqueInput
  }

  /**
   * Task findFirst
   */
  export type TaskFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * Filter, which Task to fetch.
     */
    where?: TaskWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Tasks to fetch.
     */
    orderBy?: TaskOrderByWithRelationInput | TaskOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Tasks.
     */
    cursor?: TaskWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Tasks from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Tasks.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Tasks.
     */
    distinct?: TaskScalarFieldEnum | TaskScalarFieldEnum[]
  }

  /**
   * Task findFirstOrThrow
   */
  export type TaskFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * Filter, which Task to fetch.
     */
    where?: TaskWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Tasks to fetch.
     */
    orderBy?: TaskOrderByWithRelationInput | TaskOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Tasks.
     */
    cursor?: TaskWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Tasks from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Tasks.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Tasks.
     */
    distinct?: TaskScalarFieldEnum | TaskScalarFieldEnum[]
  }

  /**
   * Task findMany
   */
  export type TaskFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * Filter, which Tasks to fetch.
     */
    where?: TaskWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Tasks to fetch.
     */
    orderBy?: TaskOrderByWithRelationInput | TaskOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Tasks.
     */
    cursor?: TaskWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Tasks from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Tasks.
     */
    skip?: number
    distinct?: TaskScalarFieldEnum | TaskScalarFieldEnum[]
  }

  /**
   * Task create
   */
  export type TaskCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * The data needed to create a Task.
     */
    data: XOR<TaskCreateInput, TaskUncheckedCreateInput>
  }

  /**
   * Task createMany
   */
  export type TaskCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Tasks.
     */
    data: TaskCreateManyInput | TaskCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Task createManyAndReturn
   */
  export type TaskCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Tasks.
     */
    data: TaskCreateManyInput | TaskCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * Task update
   */
  export type TaskUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * The data needed to update a Task.
     */
    data: XOR<TaskUpdateInput, TaskUncheckedUpdateInput>
    /**
     * Choose, which Task to update.
     */
    where: TaskWhereUniqueInput
  }

  /**
   * Task updateMany
   */
  export type TaskUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Tasks.
     */
    data: XOR<TaskUpdateManyMutationInput, TaskUncheckedUpdateManyInput>
    /**
     * Filter which Tasks to update
     */
    where?: TaskWhereInput
  }

  /**
   * Task upsert
   */
  export type TaskUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * The filter to search for the Task to update in case it exists.
     */
    where: TaskWhereUniqueInput
    /**
     * In case the Task found by the `where` argument doesn't exist, create a new Task with this data.
     */
    create: XOR<TaskCreateInput, TaskUncheckedCreateInput>
    /**
     * In case the Task was found with the provided `where` argument, update it with this data.
     */
    update: XOR<TaskUpdateInput, TaskUncheckedUpdateInput>
  }

  /**
   * Task delete
   */
  export type TaskDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
    /**
     * Filter which Task to delete.
     */
    where: TaskWhereUniqueInput
  }

  /**
   * Task deleteMany
   */
  export type TaskDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Tasks to delete
     */
    where?: TaskWhereInput
  }

  /**
   * Task.field
   */
  export type Task$fieldArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Field
     */
    select?: FieldSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: FieldInclude<ExtArgs> | null
    where?: FieldWhereInput
  }

  /**
   * Task without action
   */
  export type TaskDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Task
     */
    select?: TaskSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: TaskInclude<ExtArgs> | null
  }


  /**
   * Model NdviReading
   */

  export type AggregateNdviReading = {
    _count: NdviReadingCountAggregateOutputType | null
    _avg: NdviReadingAvgAggregateOutputType | null
    _sum: NdviReadingSumAggregateOutputType | null
    _min: NdviReadingMinAggregateOutputType | null
    _max: NdviReadingMaxAggregateOutputType | null
  }

  export type NdviReadingAvgAggregateOutputType = {
    value: Decimal | null
    cloudCover: Decimal | null
  }

  export type NdviReadingSumAggregateOutputType = {
    value: Decimal | null
    cloudCover: Decimal | null
  }

  export type NdviReadingMinAggregateOutputType = {
    id: string | null
    fieldId: string | null
    value: Decimal | null
    capturedAt: Date | null
    source: string | null
    cloudCover: Decimal | null
    quality: string | null
    satelliteName: string | null
    createdAt: Date | null
  }

  export type NdviReadingMaxAggregateOutputType = {
    id: string | null
    fieldId: string | null
    value: Decimal | null
    capturedAt: Date | null
    source: string | null
    cloudCover: Decimal | null
    quality: string | null
    satelliteName: string | null
    createdAt: Date | null
  }

  export type NdviReadingCountAggregateOutputType = {
    id: number
    fieldId: number
    value: number
    capturedAt: number
    source: number
    cloudCover: number
    quality: number
    satelliteName: number
    bandInfo: number
    createdAt: number
    _all: number
  }


  export type NdviReadingAvgAggregateInputType = {
    value?: true
    cloudCover?: true
  }

  export type NdviReadingSumAggregateInputType = {
    value?: true
    cloudCover?: true
  }

  export type NdviReadingMinAggregateInputType = {
    id?: true
    fieldId?: true
    value?: true
    capturedAt?: true
    source?: true
    cloudCover?: true
    quality?: true
    satelliteName?: true
    createdAt?: true
  }

  export type NdviReadingMaxAggregateInputType = {
    id?: true
    fieldId?: true
    value?: true
    capturedAt?: true
    source?: true
    cloudCover?: true
    quality?: true
    satelliteName?: true
    createdAt?: true
  }

  export type NdviReadingCountAggregateInputType = {
    id?: true
    fieldId?: true
    value?: true
    capturedAt?: true
    source?: true
    cloudCover?: true
    quality?: true
    satelliteName?: true
    bandInfo?: true
    createdAt?: true
    _all?: true
  }

  export type NdviReadingAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which NdviReading to aggregate.
     */
    where?: NdviReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of NdviReadings to fetch.
     */
    orderBy?: NdviReadingOrderByWithRelationInput | NdviReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: NdviReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` NdviReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` NdviReadings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned NdviReadings
    **/
    _count?: true | NdviReadingCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: NdviReadingAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: NdviReadingSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: NdviReadingMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: NdviReadingMaxAggregateInputType
  }

  export type GetNdviReadingAggregateType<T extends NdviReadingAggregateArgs> = {
        [P in keyof T & keyof AggregateNdviReading]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateNdviReading[P]>
      : GetScalarType<T[P], AggregateNdviReading[P]>
  }




  export type NdviReadingGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: NdviReadingWhereInput
    orderBy?: NdviReadingOrderByWithAggregationInput | NdviReadingOrderByWithAggregationInput[]
    by: NdviReadingScalarFieldEnum[] | NdviReadingScalarFieldEnum
    having?: NdviReadingScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: NdviReadingCountAggregateInputType | true
    _avg?: NdviReadingAvgAggregateInputType
    _sum?: NdviReadingSumAggregateInputType
    _min?: NdviReadingMinAggregateInputType
    _max?: NdviReadingMaxAggregateInputType
  }

  export type NdviReadingGroupByOutputType = {
    id: string
    fieldId: string
    value: Decimal
    capturedAt: Date
    source: string
    cloudCover: Decimal | null
    quality: string | null
    satelliteName: string | null
    bandInfo: JsonValue | null
    createdAt: Date
    _count: NdviReadingCountAggregateOutputType | null
    _avg: NdviReadingAvgAggregateOutputType | null
    _sum: NdviReadingSumAggregateOutputType | null
    _min: NdviReadingMinAggregateOutputType | null
    _max: NdviReadingMaxAggregateOutputType | null
  }

  type GetNdviReadingGroupByPayload<T extends NdviReadingGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<NdviReadingGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof NdviReadingGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], NdviReadingGroupByOutputType[P]>
            : GetScalarType<T[P], NdviReadingGroupByOutputType[P]>
        }
      >
    >


  export type NdviReadingSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    fieldId?: boolean
    value?: boolean
    capturedAt?: boolean
    source?: boolean
    cloudCover?: boolean
    quality?: boolean
    satelliteName?: boolean
    bandInfo?: boolean
    createdAt?: boolean
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["ndviReading"]>

  export type NdviReadingSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    fieldId?: boolean
    value?: boolean
    capturedAt?: boolean
    source?: boolean
    cloudCover?: boolean
    quality?: boolean
    satelliteName?: boolean
    bandInfo?: boolean
    createdAt?: boolean
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["ndviReading"]>

  export type NdviReadingSelectScalar = {
    id?: boolean
    fieldId?: boolean
    value?: boolean
    capturedAt?: boolean
    source?: boolean
    cloudCover?: boolean
    quality?: boolean
    satelliteName?: boolean
    bandInfo?: boolean
    createdAt?: boolean
  }

  export type NdviReadingInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }
  export type NdviReadingIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    field?: boolean | FieldDefaultArgs<ExtArgs>
  }

  export type $NdviReadingPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "NdviReading"
    objects: {
      field: Prisma.$FieldPayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      fieldId: string
      value: Prisma.Decimal
      capturedAt: Date
      source: string
      cloudCover: Prisma.Decimal | null
      quality: string | null
      satelliteName: string | null
      bandInfo: Prisma.JsonValue | null
      createdAt: Date
    }, ExtArgs["result"]["ndviReading"]>
    composites: {}
  }

  type NdviReadingGetPayload<S extends boolean | null | undefined | NdviReadingDefaultArgs> = $Result.GetResult<Prisma.$NdviReadingPayload, S>

  type NdviReadingCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<NdviReadingFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: NdviReadingCountAggregateInputType | true
    }

  export interface NdviReadingDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['NdviReading'], meta: { name: 'NdviReading' } }
    /**
     * Find zero or one NdviReading that matches the filter.
     * @param {NdviReadingFindUniqueArgs} args - Arguments to find a NdviReading
     * @example
     * // Get one NdviReading
     * const ndviReading = await prisma.ndviReading.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends NdviReadingFindUniqueArgs>(args: SelectSubset<T, NdviReadingFindUniqueArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one NdviReading that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {NdviReadingFindUniqueOrThrowArgs} args - Arguments to find a NdviReading
     * @example
     * // Get one NdviReading
     * const ndviReading = await prisma.ndviReading.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends NdviReadingFindUniqueOrThrowArgs>(args: SelectSubset<T, NdviReadingFindUniqueOrThrowArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first NdviReading that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingFindFirstArgs} args - Arguments to find a NdviReading
     * @example
     * // Get one NdviReading
     * const ndviReading = await prisma.ndviReading.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends NdviReadingFindFirstArgs>(args?: SelectSubset<T, NdviReadingFindFirstArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first NdviReading that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingFindFirstOrThrowArgs} args - Arguments to find a NdviReading
     * @example
     * // Get one NdviReading
     * const ndviReading = await prisma.ndviReading.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends NdviReadingFindFirstOrThrowArgs>(args?: SelectSubset<T, NdviReadingFindFirstOrThrowArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more NdviReadings that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all NdviReadings
     * const ndviReadings = await prisma.ndviReading.findMany()
     * 
     * // Get first 10 NdviReadings
     * const ndviReadings = await prisma.ndviReading.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const ndviReadingWithIdOnly = await prisma.ndviReading.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends NdviReadingFindManyArgs>(args?: SelectSubset<T, NdviReadingFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a NdviReading.
     * @param {NdviReadingCreateArgs} args - Arguments to create a NdviReading.
     * @example
     * // Create one NdviReading
     * const NdviReading = await prisma.ndviReading.create({
     *   data: {
     *     // ... data to create a NdviReading
     *   }
     * })
     * 
     */
    create<T extends NdviReadingCreateArgs>(args: SelectSubset<T, NdviReadingCreateArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many NdviReadings.
     * @param {NdviReadingCreateManyArgs} args - Arguments to create many NdviReadings.
     * @example
     * // Create many NdviReadings
     * const ndviReading = await prisma.ndviReading.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends NdviReadingCreateManyArgs>(args?: SelectSubset<T, NdviReadingCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many NdviReadings and returns the data saved in the database.
     * @param {NdviReadingCreateManyAndReturnArgs} args - Arguments to create many NdviReadings.
     * @example
     * // Create many NdviReadings
     * const ndviReading = await prisma.ndviReading.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many NdviReadings and only return the `id`
     * const ndviReadingWithIdOnly = await prisma.ndviReading.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends NdviReadingCreateManyAndReturnArgs>(args?: SelectSubset<T, NdviReadingCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a NdviReading.
     * @param {NdviReadingDeleteArgs} args - Arguments to delete one NdviReading.
     * @example
     * // Delete one NdviReading
     * const NdviReading = await prisma.ndviReading.delete({
     *   where: {
     *     // ... filter to delete one NdviReading
     *   }
     * })
     * 
     */
    delete<T extends NdviReadingDeleteArgs>(args: SelectSubset<T, NdviReadingDeleteArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one NdviReading.
     * @param {NdviReadingUpdateArgs} args - Arguments to update one NdviReading.
     * @example
     * // Update one NdviReading
     * const ndviReading = await prisma.ndviReading.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends NdviReadingUpdateArgs>(args: SelectSubset<T, NdviReadingUpdateArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more NdviReadings.
     * @param {NdviReadingDeleteManyArgs} args - Arguments to filter NdviReadings to delete.
     * @example
     * // Delete a few NdviReadings
     * const { count } = await prisma.ndviReading.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends NdviReadingDeleteManyArgs>(args?: SelectSubset<T, NdviReadingDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more NdviReadings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many NdviReadings
     * const ndviReading = await prisma.ndviReading.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends NdviReadingUpdateManyArgs>(args: SelectSubset<T, NdviReadingUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one NdviReading.
     * @param {NdviReadingUpsertArgs} args - Arguments to update or create a NdviReading.
     * @example
     * // Update or create a NdviReading
     * const ndviReading = await prisma.ndviReading.upsert({
     *   create: {
     *     // ... data to create a NdviReading
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the NdviReading we want to update
     *   }
     * })
     */
    upsert<T extends NdviReadingUpsertArgs>(args: SelectSubset<T, NdviReadingUpsertArgs<ExtArgs>>): Prisma__NdviReadingClient<$Result.GetResult<Prisma.$NdviReadingPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of NdviReadings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingCountArgs} args - Arguments to filter NdviReadings to count.
     * @example
     * // Count the number of NdviReadings
     * const count = await prisma.ndviReading.count({
     *   where: {
     *     // ... the filter for the NdviReadings we want to count
     *   }
     * })
    **/
    count<T extends NdviReadingCountArgs>(
      args?: Subset<T, NdviReadingCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], NdviReadingCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a NdviReading.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends NdviReadingAggregateArgs>(args: Subset<T, NdviReadingAggregateArgs>): Prisma.PrismaPromise<GetNdviReadingAggregateType<T>>

    /**
     * Group by NdviReading.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {NdviReadingGroupByArgs} args - Group by arguments.
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
      T extends NdviReadingGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: NdviReadingGroupByArgs['orderBy'] }
        : { orderBy?: NdviReadingGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, NdviReadingGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetNdviReadingGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the NdviReading model
   */
  readonly fields: NdviReadingFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for NdviReading.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__NdviReadingClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    field<T extends FieldDefaultArgs<ExtArgs> = {}>(args?: Subset<T, FieldDefaultArgs<ExtArgs>>): Prisma__FieldClient<$Result.GetResult<Prisma.$FieldPayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
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
   * Fields of the NdviReading model
   */ 
  interface NdviReadingFieldRefs {
    readonly id: FieldRef<"NdviReading", 'String'>
    readonly fieldId: FieldRef<"NdviReading", 'String'>
    readonly value: FieldRef<"NdviReading", 'Decimal'>
    readonly capturedAt: FieldRef<"NdviReading", 'DateTime'>
    readonly source: FieldRef<"NdviReading", 'String'>
    readonly cloudCover: FieldRef<"NdviReading", 'Decimal'>
    readonly quality: FieldRef<"NdviReading", 'String'>
    readonly satelliteName: FieldRef<"NdviReading", 'String'>
    readonly bandInfo: FieldRef<"NdviReading", 'Json'>
    readonly createdAt: FieldRef<"NdviReading", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * NdviReading findUnique
   */
  export type NdviReadingFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * Filter, which NdviReading to fetch.
     */
    where: NdviReadingWhereUniqueInput
  }

  /**
   * NdviReading findUniqueOrThrow
   */
  export type NdviReadingFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * Filter, which NdviReading to fetch.
     */
    where: NdviReadingWhereUniqueInput
  }

  /**
   * NdviReading findFirst
   */
  export type NdviReadingFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * Filter, which NdviReading to fetch.
     */
    where?: NdviReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of NdviReadings to fetch.
     */
    orderBy?: NdviReadingOrderByWithRelationInput | NdviReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for NdviReadings.
     */
    cursor?: NdviReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` NdviReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` NdviReadings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of NdviReadings.
     */
    distinct?: NdviReadingScalarFieldEnum | NdviReadingScalarFieldEnum[]
  }

  /**
   * NdviReading findFirstOrThrow
   */
  export type NdviReadingFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * Filter, which NdviReading to fetch.
     */
    where?: NdviReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of NdviReadings to fetch.
     */
    orderBy?: NdviReadingOrderByWithRelationInput | NdviReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for NdviReadings.
     */
    cursor?: NdviReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` NdviReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` NdviReadings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of NdviReadings.
     */
    distinct?: NdviReadingScalarFieldEnum | NdviReadingScalarFieldEnum[]
  }

  /**
   * NdviReading findMany
   */
  export type NdviReadingFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * Filter, which NdviReadings to fetch.
     */
    where?: NdviReadingWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of NdviReadings to fetch.
     */
    orderBy?: NdviReadingOrderByWithRelationInput | NdviReadingOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing NdviReadings.
     */
    cursor?: NdviReadingWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` NdviReadings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` NdviReadings.
     */
    skip?: number
    distinct?: NdviReadingScalarFieldEnum | NdviReadingScalarFieldEnum[]
  }

  /**
   * NdviReading create
   */
  export type NdviReadingCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * The data needed to create a NdviReading.
     */
    data: XOR<NdviReadingCreateInput, NdviReadingUncheckedCreateInput>
  }

  /**
   * NdviReading createMany
   */
  export type NdviReadingCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many NdviReadings.
     */
    data: NdviReadingCreateManyInput | NdviReadingCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * NdviReading createManyAndReturn
   */
  export type NdviReadingCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many NdviReadings.
     */
    data: NdviReadingCreateManyInput | NdviReadingCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * NdviReading update
   */
  export type NdviReadingUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * The data needed to update a NdviReading.
     */
    data: XOR<NdviReadingUpdateInput, NdviReadingUncheckedUpdateInput>
    /**
     * Choose, which NdviReading to update.
     */
    where: NdviReadingWhereUniqueInput
  }

  /**
   * NdviReading updateMany
   */
  export type NdviReadingUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update NdviReadings.
     */
    data: XOR<NdviReadingUpdateManyMutationInput, NdviReadingUncheckedUpdateManyInput>
    /**
     * Filter which NdviReadings to update
     */
    where?: NdviReadingWhereInput
  }

  /**
   * NdviReading upsert
   */
  export type NdviReadingUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * The filter to search for the NdviReading to update in case it exists.
     */
    where: NdviReadingWhereUniqueInput
    /**
     * In case the NdviReading found by the `where` argument doesn't exist, create a new NdviReading with this data.
     */
    create: XOR<NdviReadingCreateInput, NdviReadingUncheckedCreateInput>
    /**
     * In case the NdviReading was found with the provided `where` argument, update it with this data.
     */
    update: XOR<NdviReadingUpdateInput, NdviReadingUncheckedUpdateInput>
  }

  /**
   * NdviReading delete
   */
  export type NdviReadingDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
    /**
     * Filter which NdviReading to delete.
     */
    where: NdviReadingWhereUniqueInput
  }

  /**
   * NdviReading deleteMany
   */
  export type NdviReadingDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which NdviReadings to delete
     */
    where?: NdviReadingWhereInput
  }

  /**
   * NdviReading without action
   */
  export type NdviReadingDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the NdviReading
     */
    select?: NdviReadingSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: NdviReadingInclude<ExtArgs> | null
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


  export const FieldScalarFieldEnum: {
    id: 'id',
    version: 'version',
    name: 'name',
    tenantId: 'tenantId',
    cropType: 'cropType',
    ownerId: 'ownerId',
    areaHectares: 'areaHectares',
    healthScore: 'healthScore',
    ndviValue: 'ndviValue',
    status: 'status',
    plantingDate: 'plantingDate',
    expectedHarvest: 'expectedHarvest',
    irrigationType: 'irrigationType',
    soilType: 'soilType',
    metadata: 'metadata',
    isDeleted: 'isDeleted',
    serverUpdatedAt: 'serverUpdatedAt',
    etag: 'etag',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type FieldScalarFieldEnum = (typeof FieldScalarFieldEnum)[keyof typeof FieldScalarFieldEnum]


  export const FieldBoundaryHistoryScalarFieldEnum: {
    id: 'id',
    fieldId: 'fieldId',
    versionAtChange: 'versionAtChange',
    areaChangeHectares: 'areaChangeHectares',
    changedBy: 'changedBy',
    changeReason: 'changeReason',
    changeSource: 'changeSource',
    deviceId: 'deviceId',
    createdAt: 'createdAt'
  };

  export type FieldBoundaryHistoryScalarFieldEnum = (typeof FieldBoundaryHistoryScalarFieldEnum)[keyof typeof FieldBoundaryHistoryScalarFieldEnum]


  export const SyncStatusScalarFieldEnum: {
    id: 'id',
    deviceId: 'deviceId',
    userId: 'userId',
    tenantId: 'tenantId',
    lastSyncAt: 'lastSyncAt',
    lastSyncVersion: 'lastSyncVersion',
    status: 'status',
    pendingUploads: 'pendingUploads',
    pendingDownloads: 'pendingDownloads',
    conflictsCount: 'conflictsCount',
    lastError: 'lastError',
    deviceInfo: 'deviceInfo',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type SyncStatusScalarFieldEnum = (typeof SyncStatusScalarFieldEnum)[keyof typeof SyncStatusScalarFieldEnum]


  export const TaskScalarFieldEnum: {
    id: 'id',
    title: 'title',
    titleAr: 'titleAr',
    description: 'description',
    taskType: 'taskType',
    priority: 'priority',
    status: 'status',
    dueDate: 'dueDate',
    scheduledTime: 'scheduledTime',
    completedAt: 'completedAt',
    assignedTo: 'assignedTo',
    createdBy: 'createdBy',
    fieldId: 'fieldId',
    estimatedMinutes: 'estimatedMinutes',
    actualMinutes: 'actualMinutes',
    completionNotes: 'completionNotes',
    evidence: 'evidence',
    serverUpdatedAt: 'serverUpdatedAt',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type TaskScalarFieldEnum = (typeof TaskScalarFieldEnum)[keyof typeof TaskScalarFieldEnum]


  export const NdviReadingScalarFieldEnum: {
    id: 'id',
    fieldId: 'fieldId',
    value: 'value',
    capturedAt: 'capturedAt',
    source: 'source',
    cloudCover: 'cloudCover',
    quality: 'quality',
    satelliteName: 'satelliteName',
    bandInfo: 'bandInfo',
    createdAt: 'createdAt'
  };

  export type NdviReadingScalarFieldEnum = (typeof NdviReadingScalarFieldEnum)[keyof typeof NdviReadingScalarFieldEnum]


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
   * Reference to a field of type 'Int'
   */
  export type IntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Int'>
    


  /**
   * Reference to a field of type 'Int[]'
   */
  export type ListIntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Int[]'>
    


  /**
   * Reference to a field of type 'Decimal'
   */
  export type DecimalFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Decimal'>
    


  /**
   * Reference to a field of type 'Decimal[]'
   */
  export type ListDecimalFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Decimal[]'>
    


  /**
   * Reference to a field of type 'FieldStatus'
   */
  export type EnumFieldStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'FieldStatus'>
    


  /**
   * Reference to a field of type 'FieldStatus[]'
   */
  export type ListEnumFieldStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'FieldStatus[]'>
    


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
   * Reference to a field of type 'Boolean'
   */
  export type BooleanFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Boolean'>
    


  /**
   * Reference to a field of type 'ChangeSource'
   */
  export type EnumChangeSourceFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'ChangeSource'>
    


  /**
   * Reference to a field of type 'ChangeSource[]'
   */
  export type ListEnumChangeSourceFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'ChangeSource[]'>
    


  /**
   * Reference to a field of type 'BigInt'
   */
  export type BigIntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'BigInt'>
    


  /**
   * Reference to a field of type 'BigInt[]'
   */
  export type ListBigIntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'BigInt[]'>
    


  /**
   * Reference to a field of type 'SyncState'
   */
  export type EnumSyncStateFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'SyncState'>
    


  /**
   * Reference to a field of type 'SyncState[]'
   */
  export type ListEnumSyncStateFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'SyncState[]'>
    


  /**
   * Reference to a field of type 'TaskType'
   */
  export type EnumTaskTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TaskType'>
    


  /**
   * Reference to a field of type 'TaskType[]'
   */
  export type ListEnumTaskTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TaskType[]'>
    


  /**
   * Reference to a field of type 'Priority'
   */
  export type EnumPriorityFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Priority'>
    


  /**
   * Reference to a field of type 'Priority[]'
   */
  export type ListEnumPriorityFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Priority[]'>
    


  /**
   * Reference to a field of type 'TaskState'
   */
  export type EnumTaskStateFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TaskState'>
    


  /**
   * Reference to a field of type 'TaskState[]'
   */
  export type ListEnumTaskStateFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TaskState[]'>
    


  /**
   * Reference to a field of type 'Float'
   */
  export type FloatFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Float'>
    


  /**
   * Reference to a field of type 'Float[]'
   */
  export type ListFloatFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Float[]'>
    
  /**
   * Deep Input Types
   */


  export type FieldWhereInput = {
    AND?: FieldWhereInput | FieldWhereInput[]
    OR?: FieldWhereInput[]
    NOT?: FieldWhereInput | FieldWhereInput[]
    id?: UuidFilter<"Field"> | string
    version?: IntFilter<"Field"> | number
    name?: StringFilter<"Field"> | string
    tenantId?: StringFilter<"Field"> | string
    cropType?: StringFilter<"Field"> | string
    ownerId?: UuidNullableFilter<"Field"> | string | null
    areaHectares?: DecimalNullableFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    healthScore?: DecimalNullableFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    ndviValue?: DecimalNullableFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFilter<"Field"> | $Enums.FieldStatus
    plantingDate?: DateTimeNullableFilter<"Field"> | Date | string | null
    expectedHarvest?: DateTimeNullableFilter<"Field"> | Date | string | null
    irrigationType?: StringNullableFilter<"Field"> | string | null
    soilType?: StringNullableFilter<"Field"> | string | null
    metadata?: JsonNullableFilter<"Field">
    isDeleted?: BoolFilter<"Field"> | boolean
    serverUpdatedAt?: DateTimeFilter<"Field"> | Date | string
    etag?: StringNullableFilter<"Field"> | string | null
    createdAt?: DateTimeFilter<"Field"> | Date | string
    updatedAt?: DateTimeFilter<"Field"> | Date | string
    boundaryHistory?: FieldBoundaryHistoryListRelationFilter
    tasks?: TaskListRelationFilter
    ndviReadings?: NdviReadingListRelationFilter
  }

  export type FieldOrderByWithRelationInput = {
    id?: SortOrder
    version?: SortOrder
    name?: SortOrder
    tenantId?: SortOrder
    cropType?: SortOrder
    ownerId?: SortOrderInput | SortOrder
    areaHectares?: SortOrderInput | SortOrder
    healthScore?: SortOrderInput | SortOrder
    ndviValue?: SortOrderInput | SortOrder
    status?: SortOrder
    plantingDate?: SortOrderInput | SortOrder
    expectedHarvest?: SortOrderInput | SortOrder
    irrigationType?: SortOrderInput | SortOrder
    soilType?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    isDeleted?: SortOrder
    serverUpdatedAt?: SortOrder
    etag?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    boundaryHistory?: FieldBoundaryHistoryOrderByRelationAggregateInput
    tasks?: TaskOrderByRelationAggregateInput
    ndviReadings?: NdviReadingOrderByRelationAggregateInput
  }

  export type FieldWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: FieldWhereInput | FieldWhereInput[]
    OR?: FieldWhereInput[]
    NOT?: FieldWhereInput | FieldWhereInput[]
    version?: IntFilter<"Field"> | number
    name?: StringFilter<"Field"> | string
    tenantId?: StringFilter<"Field"> | string
    cropType?: StringFilter<"Field"> | string
    ownerId?: UuidNullableFilter<"Field"> | string | null
    areaHectares?: DecimalNullableFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    healthScore?: DecimalNullableFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    ndviValue?: DecimalNullableFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFilter<"Field"> | $Enums.FieldStatus
    plantingDate?: DateTimeNullableFilter<"Field"> | Date | string | null
    expectedHarvest?: DateTimeNullableFilter<"Field"> | Date | string | null
    irrigationType?: StringNullableFilter<"Field"> | string | null
    soilType?: StringNullableFilter<"Field"> | string | null
    metadata?: JsonNullableFilter<"Field">
    isDeleted?: BoolFilter<"Field"> | boolean
    serverUpdatedAt?: DateTimeFilter<"Field"> | Date | string
    etag?: StringNullableFilter<"Field"> | string | null
    createdAt?: DateTimeFilter<"Field"> | Date | string
    updatedAt?: DateTimeFilter<"Field"> | Date | string
    boundaryHistory?: FieldBoundaryHistoryListRelationFilter
    tasks?: TaskListRelationFilter
    ndviReadings?: NdviReadingListRelationFilter
  }, "id">

  export type FieldOrderByWithAggregationInput = {
    id?: SortOrder
    version?: SortOrder
    name?: SortOrder
    tenantId?: SortOrder
    cropType?: SortOrder
    ownerId?: SortOrderInput | SortOrder
    areaHectares?: SortOrderInput | SortOrder
    healthScore?: SortOrderInput | SortOrder
    ndviValue?: SortOrderInput | SortOrder
    status?: SortOrder
    plantingDate?: SortOrderInput | SortOrder
    expectedHarvest?: SortOrderInput | SortOrder
    irrigationType?: SortOrderInput | SortOrder
    soilType?: SortOrderInput | SortOrder
    metadata?: SortOrderInput | SortOrder
    isDeleted?: SortOrder
    serverUpdatedAt?: SortOrder
    etag?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: FieldCountOrderByAggregateInput
    _avg?: FieldAvgOrderByAggregateInput
    _max?: FieldMaxOrderByAggregateInput
    _min?: FieldMinOrderByAggregateInput
    _sum?: FieldSumOrderByAggregateInput
  }

  export type FieldScalarWhereWithAggregatesInput = {
    AND?: FieldScalarWhereWithAggregatesInput | FieldScalarWhereWithAggregatesInput[]
    OR?: FieldScalarWhereWithAggregatesInput[]
    NOT?: FieldScalarWhereWithAggregatesInput | FieldScalarWhereWithAggregatesInput[]
    id?: UuidWithAggregatesFilter<"Field"> | string
    version?: IntWithAggregatesFilter<"Field"> | number
    name?: StringWithAggregatesFilter<"Field"> | string
    tenantId?: StringWithAggregatesFilter<"Field"> | string
    cropType?: StringWithAggregatesFilter<"Field"> | string
    ownerId?: UuidNullableWithAggregatesFilter<"Field"> | string | null
    areaHectares?: DecimalNullableWithAggregatesFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    healthScore?: DecimalNullableWithAggregatesFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    ndviValue?: DecimalNullableWithAggregatesFilter<"Field"> | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusWithAggregatesFilter<"Field"> | $Enums.FieldStatus
    plantingDate?: DateTimeNullableWithAggregatesFilter<"Field"> | Date | string | null
    expectedHarvest?: DateTimeNullableWithAggregatesFilter<"Field"> | Date | string | null
    irrigationType?: StringNullableWithAggregatesFilter<"Field"> | string | null
    soilType?: StringNullableWithAggregatesFilter<"Field"> | string | null
    metadata?: JsonNullableWithAggregatesFilter<"Field">
    isDeleted?: BoolWithAggregatesFilter<"Field"> | boolean
    serverUpdatedAt?: DateTimeWithAggregatesFilter<"Field"> | Date | string
    etag?: StringNullableWithAggregatesFilter<"Field"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"Field"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Field"> | Date | string
  }

  export type FieldBoundaryHistoryWhereInput = {
    AND?: FieldBoundaryHistoryWhereInput | FieldBoundaryHistoryWhereInput[]
    OR?: FieldBoundaryHistoryWhereInput[]
    NOT?: FieldBoundaryHistoryWhereInput | FieldBoundaryHistoryWhereInput[]
    id?: UuidFilter<"FieldBoundaryHistory"> | string
    fieldId?: UuidFilter<"FieldBoundaryHistory"> | string
    versionAtChange?: IntFilter<"FieldBoundaryHistory"> | number
    areaChangeHectares?: DecimalNullableFilter<"FieldBoundaryHistory"> | Decimal | DecimalJsLike | number | string | null
    changedBy?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    changeReason?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    changeSource?: EnumChangeSourceFilter<"FieldBoundaryHistory"> | $Enums.ChangeSource
    deviceId?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    createdAt?: DateTimeFilter<"FieldBoundaryHistory"> | Date | string
    field?: XOR<FieldRelationFilter, FieldWhereInput>
  }

  export type FieldBoundaryHistoryOrderByWithRelationInput = {
    id?: SortOrder
    fieldId?: SortOrder
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrderInput | SortOrder
    changedBy?: SortOrderInput | SortOrder
    changeReason?: SortOrderInput | SortOrder
    changeSource?: SortOrder
    deviceId?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    field?: FieldOrderByWithRelationInput
  }

  export type FieldBoundaryHistoryWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: FieldBoundaryHistoryWhereInput | FieldBoundaryHistoryWhereInput[]
    OR?: FieldBoundaryHistoryWhereInput[]
    NOT?: FieldBoundaryHistoryWhereInput | FieldBoundaryHistoryWhereInput[]
    fieldId?: UuidFilter<"FieldBoundaryHistory"> | string
    versionAtChange?: IntFilter<"FieldBoundaryHistory"> | number
    areaChangeHectares?: DecimalNullableFilter<"FieldBoundaryHistory"> | Decimal | DecimalJsLike | number | string | null
    changedBy?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    changeReason?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    changeSource?: EnumChangeSourceFilter<"FieldBoundaryHistory"> | $Enums.ChangeSource
    deviceId?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    createdAt?: DateTimeFilter<"FieldBoundaryHistory"> | Date | string
    field?: XOR<FieldRelationFilter, FieldWhereInput>
  }, "id">

  export type FieldBoundaryHistoryOrderByWithAggregationInput = {
    id?: SortOrder
    fieldId?: SortOrder
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrderInput | SortOrder
    changedBy?: SortOrderInput | SortOrder
    changeReason?: SortOrderInput | SortOrder
    changeSource?: SortOrder
    deviceId?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    _count?: FieldBoundaryHistoryCountOrderByAggregateInput
    _avg?: FieldBoundaryHistoryAvgOrderByAggregateInput
    _max?: FieldBoundaryHistoryMaxOrderByAggregateInput
    _min?: FieldBoundaryHistoryMinOrderByAggregateInput
    _sum?: FieldBoundaryHistorySumOrderByAggregateInput
  }

  export type FieldBoundaryHistoryScalarWhereWithAggregatesInput = {
    AND?: FieldBoundaryHistoryScalarWhereWithAggregatesInput | FieldBoundaryHistoryScalarWhereWithAggregatesInput[]
    OR?: FieldBoundaryHistoryScalarWhereWithAggregatesInput[]
    NOT?: FieldBoundaryHistoryScalarWhereWithAggregatesInput | FieldBoundaryHistoryScalarWhereWithAggregatesInput[]
    id?: UuidWithAggregatesFilter<"FieldBoundaryHistory"> | string
    fieldId?: UuidWithAggregatesFilter<"FieldBoundaryHistory"> | string
    versionAtChange?: IntWithAggregatesFilter<"FieldBoundaryHistory"> | number
    areaChangeHectares?: DecimalNullableWithAggregatesFilter<"FieldBoundaryHistory"> | Decimal | DecimalJsLike | number | string | null
    changedBy?: StringNullableWithAggregatesFilter<"FieldBoundaryHistory"> | string | null
    changeReason?: StringNullableWithAggregatesFilter<"FieldBoundaryHistory"> | string | null
    changeSource?: EnumChangeSourceWithAggregatesFilter<"FieldBoundaryHistory"> | $Enums.ChangeSource
    deviceId?: StringNullableWithAggregatesFilter<"FieldBoundaryHistory"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"FieldBoundaryHistory"> | Date | string
  }

  export type SyncStatusWhereInput = {
    AND?: SyncStatusWhereInput | SyncStatusWhereInput[]
    OR?: SyncStatusWhereInput[]
    NOT?: SyncStatusWhereInput | SyncStatusWhereInput[]
    id?: UuidFilter<"SyncStatus"> | string
    deviceId?: StringFilter<"SyncStatus"> | string
    userId?: StringFilter<"SyncStatus"> | string
    tenantId?: StringFilter<"SyncStatus"> | string
    lastSyncAt?: DateTimeNullableFilter<"SyncStatus"> | Date | string | null
    lastSyncVersion?: BigIntFilter<"SyncStatus"> | bigint | number
    status?: EnumSyncStateFilter<"SyncStatus"> | $Enums.SyncState
    pendingUploads?: IntFilter<"SyncStatus"> | number
    pendingDownloads?: IntFilter<"SyncStatus"> | number
    conflictsCount?: IntFilter<"SyncStatus"> | number
    lastError?: StringNullableFilter<"SyncStatus"> | string | null
    deviceInfo?: JsonNullableFilter<"SyncStatus">
    createdAt?: DateTimeFilter<"SyncStatus"> | Date | string
    updatedAt?: DateTimeFilter<"SyncStatus"> | Date | string
  }

  export type SyncStatusOrderByWithRelationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    userId?: SortOrder
    tenantId?: SortOrder
    lastSyncAt?: SortOrderInput | SortOrder
    lastSyncVersion?: SortOrder
    status?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
    lastError?: SortOrderInput | SortOrder
    deviceInfo?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SyncStatusWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    idx_sync_device_user?: SyncStatusIdx_sync_device_userCompoundUniqueInput
    AND?: SyncStatusWhereInput | SyncStatusWhereInput[]
    OR?: SyncStatusWhereInput[]
    NOT?: SyncStatusWhereInput | SyncStatusWhereInput[]
    deviceId?: StringFilter<"SyncStatus"> | string
    userId?: StringFilter<"SyncStatus"> | string
    tenantId?: StringFilter<"SyncStatus"> | string
    lastSyncAt?: DateTimeNullableFilter<"SyncStatus"> | Date | string | null
    lastSyncVersion?: BigIntFilter<"SyncStatus"> | bigint | number
    status?: EnumSyncStateFilter<"SyncStatus"> | $Enums.SyncState
    pendingUploads?: IntFilter<"SyncStatus"> | number
    pendingDownloads?: IntFilter<"SyncStatus"> | number
    conflictsCount?: IntFilter<"SyncStatus"> | number
    lastError?: StringNullableFilter<"SyncStatus"> | string | null
    deviceInfo?: JsonNullableFilter<"SyncStatus">
    createdAt?: DateTimeFilter<"SyncStatus"> | Date | string
    updatedAt?: DateTimeFilter<"SyncStatus"> | Date | string
  }, "id" | "idx_sync_device_user">

  export type SyncStatusOrderByWithAggregationInput = {
    id?: SortOrder
    deviceId?: SortOrder
    userId?: SortOrder
    tenantId?: SortOrder
    lastSyncAt?: SortOrderInput | SortOrder
    lastSyncVersion?: SortOrder
    status?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
    lastError?: SortOrderInput | SortOrder
    deviceInfo?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: SyncStatusCountOrderByAggregateInput
    _avg?: SyncStatusAvgOrderByAggregateInput
    _max?: SyncStatusMaxOrderByAggregateInput
    _min?: SyncStatusMinOrderByAggregateInput
    _sum?: SyncStatusSumOrderByAggregateInput
  }

  export type SyncStatusScalarWhereWithAggregatesInput = {
    AND?: SyncStatusScalarWhereWithAggregatesInput | SyncStatusScalarWhereWithAggregatesInput[]
    OR?: SyncStatusScalarWhereWithAggregatesInput[]
    NOT?: SyncStatusScalarWhereWithAggregatesInput | SyncStatusScalarWhereWithAggregatesInput[]
    id?: UuidWithAggregatesFilter<"SyncStatus"> | string
    deviceId?: StringWithAggregatesFilter<"SyncStatus"> | string
    userId?: StringWithAggregatesFilter<"SyncStatus"> | string
    tenantId?: StringWithAggregatesFilter<"SyncStatus"> | string
    lastSyncAt?: DateTimeNullableWithAggregatesFilter<"SyncStatus"> | Date | string | null
    lastSyncVersion?: BigIntWithAggregatesFilter<"SyncStatus"> | bigint | number
    status?: EnumSyncStateWithAggregatesFilter<"SyncStatus"> | $Enums.SyncState
    pendingUploads?: IntWithAggregatesFilter<"SyncStatus"> | number
    pendingDownloads?: IntWithAggregatesFilter<"SyncStatus"> | number
    conflictsCount?: IntWithAggregatesFilter<"SyncStatus"> | number
    lastError?: StringNullableWithAggregatesFilter<"SyncStatus"> | string | null
    deviceInfo?: JsonNullableWithAggregatesFilter<"SyncStatus">
    createdAt?: DateTimeWithAggregatesFilter<"SyncStatus"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"SyncStatus"> | Date | string
  }

  export type TaskWhereInput = {
    AND?: TaskWhereInput | TaskWhereInput[]
    OR?: TaskWhereInput[]
    NOT?: TaskWhereInput | TaskWhereInput[]
    id?: UuidFilter<"Task"> | string
    title?: StringFilter<"Task"> | string
    titleAr?: StringNullableFilter<"Task"> | string | null
    description?: StringNullableFilter<"Task"> | string | null
    taskType?: EnumTaskTypeFilter<"Task"> | $Enums.TaskType
    priority?: EnumPriorityFilter<"Task"> | $Enums.Priority
    status?: EnumTaskStateFilter<"Task"> | $Enums.TaskState
    dueDate?: DateTimeNullableFilter<"Task"> | Date | string | null
    scheduledTime?: StringNullableFilter<"Task"> | string | null
    completedAt?: DateTimeNullableFilter<"Task"> | Date | string | null
    assignedTo?: StringNullableFilter<"Task"> | string | null
    createdBy?: StringFilter<"Task"> | string
    fieldId?: UuidNullableFilter<"Task"> | string | null
    estimatedMinutes?: IntNullableFilter<"Task"> | number | null
    actualMinutes?: IntNullableFilter<"Task"> | number | null
    completionNotes?: StringNullableFilter<"Task"> | string | null
    evidence?: JsonNullableFilter<"Task">
    serverUpdatedAt?: DateTimeFilter<"Task"> | Date | string
    createdAt?: DateTimeFilter<"Task"> | Date | string
    updatedAt?: DateTimeFilter<"Task"> | Date | string
    field?: XOR<FieldNullableRelationFilter, FieldWhereInput> | null
  }

  export type TaskOrderByWithRelationInput = {
    id?: SortOrder
    title?: SortOrder
    titleAr?: SortOrderInput | SortOrder
    description?: SortOrderInput | SortOrder
    taskType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    dueDate?: SortOrderInput | SortOrder
    scheduledTime?: SortOrderInput | SortOrder
    completedAt?: SortOrderInput | SortOrder
    assignedTo?: SortOrderInput | SortOrder
    createdBy?: SortOrder
    fieldId?: SortOrderInput | SortOrder
    estimatedMinutes?: SortOrderInput | SortOrder
    actualMinutes?: SortOrderInput | SortOrder
    completionNotes?: SortOrderInput | SortOrder
    evidence?: SortOrderInput | SortOrder
    serverUpdatedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    field?: FieldOrderByWithRelationInput
  }

  export type TaskWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: TaskWhereInput | TaskWhereInput[]
    OR?: TaskWhereInput[]
    NOT?: TaskWhereInput | TaskWhereInput[]
    title?: StringFilter<"Task"> | string
    titleAr?: StringNullableFilter<"Task"> | string | null
    description?: StringNullableFilter<"Task"> | string | null
    taskType?: EnumTaskTypeFilter<"Task"> | $Enums.TaskType
    priority?: EnumPriorityFilter<"Task"> | $Enums.Priority
    status?: EnumTaskStateFilter<"Task"> | $Enums.TaskState
    dueDate?: DateTimeNullableFilter<"Task"> | Date | string | null
    scheduledTime?: StringNullableFilter<"Task"> | string | null
    completedAt?: DateTimeNullableFilter<"Task"> | Date | string | null
    assignedTo?: StringNullableFilter<"Task"> | string | null
    createdBy?: StringFilter<"Task"> | string
    fieldId?: UuidNullableFilter<"Task"> | string | null
    estimatedMinutes?: IntNullableFilter<"Task"> | number | null
    actualMinutes?: IntNullableFilter<"Task"> | number | null
    completionNotes?: StringNullableFilter<"Task"> | string | null
    evidence?: JsonNullableFilter<"Task">
    serverUpdatedAt?: DateTimeFilter<"Task"> | Date | string
    createdAt?: DateTimeFilter<"Task"> | Date | string
    updatedAt?: DateTimeFilter<"Task"> | Date | string
    field?: XOR<FieldNullableRelationFilter, FieldWhereInput> | null
  }, "id">

  export type TaskOrderByWithAggregationInput = {
    id?: SortOrder
    title?: SortOrder
    titleAr?: SortOrderInput | SortOrder
    description?: SortOrderInput | SortOrder
    taskType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    dueDate?: SortOrderInput | SortOrder
    scheduledTime?: SortOrderInput | SortOrder
    completedAt?: SortOrderInput | SortOrder
    assignedTo?: SortOrderInput | SortOrder
    createdBy?: SortOrder
    fieldId?: SortOrderInput | SortOrder
    estimatedMinutes?: SortOrderInput | SortOrder
    actualMinutes?: SortOrderInput | SortOrder
    completionNotes?: SortOrderInput | SortOrder
    evidence?: SortOrderInput | SortOrder
    serverUpdatedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: TaskCountOrderByAggregateInput
    _avg?: TaskAvgOrderByAggregateInput
    _max?: TaskMaxOrderByAggregateInput
    _min?: TaskMinOrderByAggregateInput
    _sum?: TaskSumOrderByAggregateInput
  }

  export type TaskScalarWhereWithAggregatesInput = {
    AND?: TaskScalarWhereWithAggregatesInput | TaskScalarWhereWithAggregatesInput[]
    OR?: TaskScalarWhereWithAggregatesInput[]
    NOT?: TaskScalarWhereWithAggregatesInput | TaskScalarWhereWithAggregatesInput[]
    id?: UuidWithAggregatesFilter<"Task"> | string
    title?: StringWithAggregatesFilter<"Task"> | string
    titleAr?: StringNullableWithAggregatesFilter<"Task"> | string | null
    description?: StringNullableWithAggregatesFilter<"Task"> | string | null
    taskType?: EnumTaskTypeWithAggregatesFilter<"Task"> | $Enums.TaskType
    priority?: EnumPriorityWithAggregatesFilter<"Task"> | $Enums.Priority
    status?: EnumTaskStateWithAggregatesFilter<"Task"> | $Enums.TaskState
    dueDate?: DateTimeNullableWithAggregatesFilter<"Task"> | Date | string | null
    scheduledTime?: StringNullableWithAggregatesFilter<"Task"> | string | null
    completedAt?: DateTimeNullableWithAggregatesFilter<"Task"> | Date | string | null
    assignedTo?: StringNullableWithAggregatesFilter<"Task"> | string | null
    createdBy?: StringWithAggregatesFilter<"Task"> | string
    fieldId?: UuidNullableWithAggregatesFilter<"Task"> | string | null
    estimatedMinutes?: IntNullableWithAggregatesFilter<"Task"> | number | null
    actualMinutes?: IntNullableWithAggregatesFilter<"Task"> | number | null
    completionNotes?: StringNullableWithAggregatesFilter<"Task"> | string | null
    evidence?: JsonNullableWithAggregatesFilter<"Task">
    serverUpdatedAt?: DateTimeWithAggregatesFilter<"Task"> | Date | string
    createdAt?: DateTimeWithAggregatesFilter<"Task"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Task"> | Date | string
  }

  export type NdviReadingWhereInput = {
    AND?: NdviReadingWhereInput | NdviReadingWhereInput[]
    OR?: NdviReadingWhereInput[]
    NOT?: NdviReadingWhereInput | NdviReadingWhereInput[]
    id?: UuidFilter<"NdviReading"> | string
    fieldId?: UuidFilter<"NdviReading"> | string
    value?: DecimalFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFilter<"NdviReading"> | Date | string
    source?: StringFilter<"NdviReading"> | string
    cloudCover?: DecimalNullableFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string | null
    quality?: StringNullableFilter<"NdviReading"> | string | null
    satelliteName?: StringNullableFilter<"NdviReading"> | string | null
    bandInfo?: JsonNullableFilter<"NdviReading">
    createdAt?: DateTimeFilter<"NdviReading"> | Date | string
    field?: XOR<FieldRelationFilter, FieldWhereInput>
  }

  export type NdviReadingOrderByWithRelationInput = {
    id?: SortOrder
    fieldId?: SortOrder
    value?: SortOrder
    capturedAt?: SortOrder
    source?: SortOrder
    cloudCover?: SortOrderInput | SortOrder
    quality?: SortOrderInput | SortOrder
    satelliteName?: SortOrderInput | SortOrder
    bandInfo?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    field?: FieldOrderByWithRelationInput
  }

  export type NdviReadingWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: NdviReadingWhereInput | NdviReadingWhereInput[]
    OR?: NdviReadingWhereInput[]
    NOT?: NdviReadingWhereInput | NdviReadingWhereInput[]
    fieldId?: UuidFilter<"NdviReading"> | string
    value?: DecimalFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFilter<"NdviReading"> | Date | string
    source?: StringFilter<"NdviReading"> | string
    cloudCover?: DecimalNullableFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string | null
    quality?: StringNullableFilter<"NdviReading"> | string | null
    satelliteName?: StringNullableFilter<"NdviReading"> | string | null
    bandInfo?: JsonNullableFilter<"NdviReading">
    createdAt?: DateTimeFilter<"NdviReading"> | Date | string
    field?: XOR<FieldRelationFilter, FieldWhereInput>
  }, "id">

  export type NdviReadingOrderByWithAggregationInput = {
    id?: SortOrder
    fieldId?: SortOrder
    value?: SortOrder
    capturedAt?: SortOrder
    source?: SortOrder
    cloudCover?: SortOrderInput | SortOrder
    quality?: SortOrderInput | SortOrder
    satelliteName?: SortOrderInput | SortOrder
    bandInfo?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    _count?: NdviReadingCountOrderByAggregateInput
    _avg?: NdviReadingAvgOrderByAggregateInput
    _max?: NdviReadingMaxOrderByAggregateInput
    _min?: NdviReadingMinOrderByAggregateInput
    _sum?: NdviReadingSumOrderByAggregateInput
  }

  export type NdviReadingScalarWhereWithAggregatesInput = {
    AND?: NdviReadingScalarWhereWithAggregatesInput | NdviReadingScalarWhereWithAggregatesInput[]
    OR?: NdviReadingScalarWhereWithAggregatesInput[]
    NOT?: NdviReadingScalarWhereWithAggregatesInput | NdviReadingScalarWhereWithAggregatesInput[]
    id?: UuidWithAggregatesFilter<"NdviReading"> | string
    fieldId?: UuidWithAggregatesFilter<"NdviReading"> | string
    value?: DecimalWithAggregatesFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeWithAggregatesFilter<"NdviReading"> | Date | string
    source?: StringWithAggregatesFilter<"NdviReading"> | string
    cloudCover?: DecimalNullableWithAggregatesFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string | null
    quality?: StringNullableWithAggregatesFilter<"NdviReading"> | string | null
    satelliteName?: StringNullableWithAggregatesFilter<"NdviReading"> | string | null
    bandInfo?: JsonNullableWithAggregatesFilter<"NdviReading">
    createdAt?: DateTimeWithAggregatesFilter<"NdviReading"> | Date | string
  }

  export type FieldCreateInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    boundaryHistory?: FieldBoundaryHistoryCreateNestedManyWithoutFieldInput
    tasks?: TaskCreateNestedManyWithoutFieldInput
    ndviReadings?: NdviReadingCreateNestedManyWithoutFieldInput
  }

  export type FieldUncheckedCreateInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    boundaryHistory?: FieldBoundaryHistoryUncheckedCreateNestedManyWithoutFieldInput
    tasks?: TaskUncheckedCreateNestedManyWithoutFieldInput
    ndviReadings?: NdviReadingUncheckedCreateNestedManyWithoutFieldInput
  }

  export type FieldUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    boundaryHistory?: FieldBoundaryHistoryUpdateManyWithoutFieldNestedInput
    tasks?: TaskUpdateManyWithoutFieldNestedInput
    ndviReadings?: NdviReadingUpdateManyWithoutFieldNestedInput
  }

  export type FieldUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    boundaryHistory?: FieldBoundaryHistoryUncheckedUpdateManyWithoutFieldNestedInput
    tasks?: TaskUncheckedUpdateManyWithoutFieldNestedInput
    ndviReadings?: NdviReadingUncheckedUpdateManyWithoutFieldNestedInput
  }

  export type FieldCreateManyInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type FieldUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type FieldUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type FieldBoundaryHistoryCreateInput = {
    id?: string
    versionAtChange: number
    areaChangeHectares?: Decimal | DecimalJsLike | number | string | null
    changedBy?: string | null
    changeReason?: string | null
    changeSource?: $Enums.ChangeSource
    deviceId?: string | null
    createdAt?: Date | string
    field: FieldCreateNestedOneWithoutBoundaryHistoryInput
  }

  export type FieldBoundaryHistoryUncheckedCreateInput = {
    id?: string
    fieldId: string
    versionAtChange: number
    areaChangeHectares?: Decimal | DecimalJsLike | number | string | null
    changedBy?: string | null
    changeReason?: string | null
    changeSource?: $Enums.ChangeSource
    deviceId?: string | null
    createdAt?: Date | string
  }

  export type FieldBoundaryHistoryUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    field?: FieldUpdateOneRequiredWithoutBoundaryHistoryNestedInput
  }

  export type FieldBoundaryHistoryUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    fieldId?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type FieldBoundaryHistoryCreateManyInput = {
    id?: string
    fieldId: string
    versionAtChange: number
    areaChangeHectares?: Decimal | DecimalJsLike | number | string | null
    changedBy?: string | null
    changeReason?: string | null
    changeSource?: $Enums.ChangeSource
    deviceId?: string | null
    createdAt?: Date | string
  }

  export type FieldBoundaryHistoryUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type FieldBoundaryHistoryUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    fieldId?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SyncStatusCreateInput = {
    id?: string
    deviceId: string
    userId: string
    tenantId: string
    lastSyncAt?: Date | string | null
    lastSyncVersion?: bigint | number
    status?: $Enums.SyncState
    pendingUploads?: number
    pendingDownloads?: number
    conflictsCount?: number
    lastError?: string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SyncStatusUncheckedCreateInput = {
    id?: string
    deviceId: string
    userId: string
    tenantId: string
    lastSyncAt?: Date | string | null
    lastSyncVersion?: bigint | number
    status?: $Enums.SyncState
    pendingUploads?: number
    pendingDownloads?: number
    conflictsCount?: number
    lastError?: string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SyncStatusUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    userId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    lastSyncAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    lastSyncVersion?: BigIntFieldUpdateOperationsInput | bigint | number
    status?: EnumSyncStateFieldUpdateOperationsInput | $Enums.SyncState
    pendingUploads?: IntFieldUpdateOperationsInput | number
    pendingDownloads?: IntFieldUpdateOperationsInput | number
    conflictsCount?: IntFieldUpdateOperationsInput | number
    lastError?: NullableStringFieldUpdateOperationsInput | string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SyncStatusUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    userId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    lastSyncAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    lastSyncVersion?: BigIntFieldUpdateOperationsInput | bigint | number
    status?: EnumSyncStateFieldUpdateOperationsInput | $Enums.SyncState
    pendingUploads?: IntFieldUpdateOperationsInput | number
    pendingDownloads?: IntFieldUpdateOperationsInput | number
    conflictsCount?: IntFieldUpdateOperationsInput | number
    lastError?: NullableStringFieldUpdateOperationsInput | string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SyncStatusCreateManyInput = {
    id?: string
    deviceId: string
    userId: string
    tenantId: string
    lastSyncAt?: Date | string | null
    lastSyncVersion?: bigint | number
    status?: $Enums.SyncState
    pendingUploads?: number
    pendingDownloads?: number
    conflictsCount?: number
    lastError?: string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type SyncStatusUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    userId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    lastSyncAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    lastSyncVersion?: BigIntFieldUpdateOperationsInput | bigint | number
    status?: EnumSyncStateFieldUpdateOperationsInput | $Enums.SyncState
    pendingUploads?: IntFieldUpdateOperationsInput | number
    pendingDownloads?: IntFieldUpdateOperationsInput | number
    conflictsCount?: IntFieldUpdateOperationsInput | number
    lastError?: NullableStringFieldUpdateOperationsInput | string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type SyncStatusUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    deviceId?: StringFieldUpdateOperationsInput | string
    userId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    lastSyncAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    lastSyncVersion?: BigIntFieldUpdateOperationsInput | bigint | number
    status?: EnumSyncStateFieldUpdateOperationsInput | $Enums.SyncState
    pendingUploads?: IntFieldUpdateOperationsInput | number
    pendingDownloads?: IntFieldUpdateOperationsInput | number
    conflictsCount?: IntFieldUpdateOperationsInput | number
    lastError?: NullableStringFieldUpdateOperationsInput | string | null
    deviceInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type TaskCreateInput = {
    id?: string
    title: string
    titleAr?: string | null
    description?: string | null
    taskType?: $Enums.TaskType
    priority?: $Enums.Priority
    status?: $Enums.TaskState
    dueDate?: Date | string | null
    scheduledTime?: string | null
    completedAt?: Date | string | null
    assignedTo?: string | null
    createdBy: string
    estimatedMinutes?: number | null
    actualMinutes?: number | null
    completionNotes?: string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: Date | string
    createdAt?: Date | string
    updatedAt?: Date | string
    field?: FieldCreateNestedOneWithoutTasksInput
  }

  export type TaskUncheckedCreateInput = {
    id?: string
    title: string
    titleAr?: string | null
    description?: string | null
    taskType?: $Enums.TaskType
    priority?: $Enums.Priority
    status?: $Enums.TaskState
    dueDate?: Date | string | null
    scheduledTime?: string | null
    completedAt?: Date | string | null
    assignedTo?: string | null
    createdBy: string
    fieldId?: string | null
    estimatedMinutes?: number | null
    actualMinutes?: number | null
    completionNotes?: string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: Date | string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type TaskUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    field?: FieldUpdateOneWithoutTasksNestedInput
  }

  export type TaskUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type TaskCreateManyInput = {
    id?: string
    title: string
    titleAr?: string | null
    description?: string | null
    taskType?: $Enums.TaskType
    priority?: $Enums.Priority
    status?: $Enums.TaskState
    dueDate?: Date | string | null
    scheduledTime?: string | null
    completedAt?: Date | string | null
    assignedTo?: string | null
    createdBy: string
    fieldId?: string | null
    estimatedMinutes?: number | null
    actualMinutes?: number | null
    completionNotes?: string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: Date | string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type TaskUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type TaskUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    fieldId?: NullableStringFieldUpdateOperationsInput | string | null
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type NdviReadingCreateInput = {
    id?: string
    value: Decimal | DecimalJsLike | number | string
    capturedAt: Date | string
    source?: string
    cloudCover?: Decimal | DecimalJsLike | number | string | null
    quality?: string | null
    satelliteName?: string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
    field: FieldCreateNestedOneWithoutNdviReadingsInput
  }

  export type NdviReadingUncheckedCreateInput = {
    id?: string
    fieldId: string
    value: Decimal | DecimalJsLike | number | string
    capturedAt: Date | string
    source?: string
    cloudCover?: Decimal | DecimalJsLike | number | string | null
    quality?: string | null
    satelliteName?: string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type NdviReadingUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    field?: FieldUpdateOneRequiredWithoutNdviReadingsNestedInput
  }

  export type NdviReadingUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    fieldId?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type NdviReadingCreateManyInput = {
    id?: string
    fieldId: string
    value: Decimal | DecimalJsLike | number | string
    capturedAt: Date | string
    source?: string
    cloudCover?: Decimal | DecimalJsLike | number | string | null
    quality?: string | null
    satelliteName?: string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type NdviReadingUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type NdviReadingUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    fieldId?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type UuidFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedUuidFilter<$PrismaModel> | string
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

  export type UuidNullableFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedUuidNullableFilter<$PrismaModel> | string | null
  }

  export type DecimalNullableFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel> | null
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalNullableFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string | null
  }

  export type EnumFieldStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.FieldStatus | EnumFieldStatusFieldRefInput<$PrismaModel>
    in?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumFieldStatusFilter<$PrismaModel> | $Enums.FieldStatus
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

  export type BoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
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

  export type FieldBoundaryHistoryListRelationFilter = {
    every?: FieldBoundaryHistoryWhereInput
    some?: FieldBoundaryHistoryWhereInput
    none?: FieldBoundaryHistoryWhereInput
  }

  export type TaskListRelationFilter = {
    every?: TaskWhereInput
    some?: TaskWhereInput
    none?: TaskWhereInput
  }

  export type NdviReadingListRelationFilter = {
    every?: NdviReadingWhereInput
    some?: NdviReadingWhereInput
    none?: NdviReadingWhereInput
  }

  export type SortOrderInput = {
    sort: SortOrder
    nulls?: NullsOrder
  }

  export type FieldBoundaryHistoryOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type TaskOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type NdviReadingOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type FieldCountOrderByAggregateInput = {
    id?: SortOrder
    version?: SortOrder
    name?: SortOrder
    tenantId?: SortOrder
    cropType?: SortOrder
    ownerId?: SortOrder
    areaHectares?: SortOrder
    healthScore?: SortOrder
    ndviValue?: SortOrder
    status?: SortOrder
    plantingDate?: SortOrder
    expectedHarvest?: SortOrder
    irrigationType?: SortOrder
    soilType?: SortOrder
    metadata?: SortOrder
    isDeleted?: SortOrder
    serverUpdatedAt?: SortOrder
    etag?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type FieldAvgOrderByAggregateInput = {
    version?: SortOrder
    areaHectares?: SortOrder
    healthScore?: SortOrder
    ndviValue?: SortOrder
  }

  export type FieldMaxOrderByAggregateInput = {
    id?: SortOrder
    version?: SortOrder
    name?: SortOrder
    tenantId?: SortOrder
    cropType?: SortOrder
    ownerId?: SortOrder
    areaHectares?: SortOrder
    healthScore?: SortOrder
    ndviValue?: SortOrder
    status?: SortOrder
    plantingDate?: SortOrder
    expectedHarvest?: SortOrder
    irrigationType?: SortOrder
    soilType?: SortOrder
    isDeleted?: SortOrder
    serverUpdatedAt?: SortOrder
    etag?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type FieldMinOrderByAggregateInput = {
    id?: SortOrder
    version?: SortOrder
    name?: SortOrder
    tenantId?: SortOrder
    cropType?: SortOrder
    ownerId?: SortOrder
    areaHectares?: SortOrder
    healthScore?: SortOrder
    ndviValue?: SortOrder
    status?: SortOrder
    plantingDate?: SortOrder
    expectedHarvest?: SortOrder
    irrigationType?: SortOrder
    soilType?: SortOrder
    isDeleted?: SortOrder
    serverUpdatedAt?: SortOrder
    etag?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type FieldSumOrderByAggregateInput = {
    version?: SortOrder
    areaHectares?: SortOrder
    healthScore?: SortOrder
    ndviValue?: SortOrder
  }

  export type UuidWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedUuidWithAggregatesFilter<$PrismaModel> | string
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedStringFilter<$PrismaModel>
    _max?: NestedStringFilter<$PrismaModel>
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

  export type UuidNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    mode?: QueryMode
    not?: NestedUuidNullableWithAggregatesFilter<$PrismaModel> | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedStringNullableFilter<$PrismaModel>
    _max?: NestedStringNullableFilter<$PrismaModel>
  }

  export type DecimalNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel> | null
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalNullableWithAggregatesFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _avg?: NestedDecimalNullableFilter<$PrismaModel>
    _sum?: NestedDecimalNullableFilter<$PrismaModel>
    _min?: NestedDecimalNullableFilter<$PrismaModel>
    _max?: NestedDecimalNullableFilter<$PrismaModel>
  }

  export type EnumFieldStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.FieldStatus | EnumFieldStatusFieldRefInput<$PrismaModel>
    in?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumFieldStatusWithAggregatesFilter<$PrismaModel> | $Enums.FieldStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumFieldStatusFilter<$PrismaModel>
    _max?: NestedEnumFieldStatusFilter<$PrismaModel>
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

  export type BoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
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

  export type EnumChangeSourceFilter<$PrismaModel = never> = {
    equals?: $Enums.ChangeSource | EnumChangeSourceFieldRefInput<$PrismaModel>
    in?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    notIn?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    not?: NestedEnumChangeSourceFilter<$PrismaModel> | $Enums.ChangeSource
  }

  export type FieldRelationFilter = {
    is?: FieldWhereInput
    isNot?: FieldWhereInput
  }

  export type FieldBoundaryHistoryCountOrderByAggregateInput = {
    id?: SortOrder
    fieldId?: SortOrder
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrder
    changedBy?: SortOrder
    changeReason?: SortOrder
    changeSource?: SortOrder
    deviceId?: SortOrder
    createdAt?: SortOrder
  }

  export type FieldBoundaryHistoryAvgOrderByAggregateInput = {
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrder
  }

  export type FieldBoundaryHistoryMaxOrderByAggregateInput = {
    id?: SortOrder
    fieldId?: SortOrder
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrder
    changedBy?: SortOrder
    changeReason?: SortOrder
    changeSource?: SortOrder
    deviceId?: SortOrder
    createdAt?: SortOrder
  }

  export type FieldBoundaryHistoryMinOrderByAggregateInput = {
    id?: SortOrder
    fieldId?: SortOrder
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrder
    changedBy?: SortOrder
    changeReason?: SortOrder
    changeSource?: SortOrder
    deviceId?: SortOrder
    createdAt?: SortOrder
  }

  export type FieldBoundaryHistorySumOrderByAggregateInput = {
    versionAtChange?: SortOrder
    areaChangeHectares?: SortOrder
  }

  export type EnumChangeSourceWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.ChangeSource | EnumChangeSourceFieldRefInput<$PrismaModel>
    in?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    notIn?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    not?: NestedEnumChangeSourceWithAggregatesFilter<$PrismaModel> | $Enums.ChangeSource
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumChangeSourceFilter<$PrismaModel>
    _max?: NestedEnumChangeSourceFilter<$PrismaModel>
  }

  export type BigIntFilter<$PrismaModel = never> = {
    equals?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    in?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    notIn?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    lt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    lte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    not?: NestedBigIntFilter<$PrismaModel> | bigint | number
  }

  export type EnumSyncStateFilter<$PrismaModel = never> = {
    equals?: $Enums.SyncState | EnumSyncStateFieldRefInput<$PrismaModel>
    in?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    not?: NestedEnumSyncStateFilter<$PrismaModel> | $Enums.SyncState
  }

  export type SyncStatusIdx_sync_device_userCompoundUniqueInput = {
    deviceId: string
    userId: string
  }

  export type SyncStatusCountOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    userId?: SortOrder
    tenantId?: SortOrder
    lastSyncAt?: SortOrder
    lastSyncVersion?: SortOrder
    status?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
    lastError?: SortOrder
    deviceInfo?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SyncStatusAvgOrderByAggregateInput = {
    lastSyncVersion?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
  }

  export type SyncStatusMaxOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    userId?: SortOrder
    tenantId?: SortOrder
    lastSyncAt?: SortOrder
    lastSyncVersion?: SortOrder
    status?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
    lastError?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SyncStatusMinOrderByAggregateInput = {
    id?: SortOrder
    deviceId?: SortOrder
    userId?: SortOrder
    tenantId?: SortOrder
    lastSyncAt?: SortOrder
    lastSyncVersion?: SortOrder
    status?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
    lastError?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type SyncStatusSumOrderByAggregateInput = {
    lastSyncVersion?: SortOrder
    pendingUploads?: SortOrder
    pendingDownloads?: SortOrder
    conflictsCount?: SortOrder
  }

  export type BigIntWithAggregatesFilter<$PrismaModel = never> = {
    equals?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    in?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    notIn?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    lt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    lte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    not?: NestedBigIntWithAggregatesFilter<$PrismaModel> | bigint | number
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedFloatFilter<$PrismaModel>
    _sum?: NestedBigIntFilter<$PrismaModel>
    _min?: NestedBigIntFilter<$PrismaModel>
    _max?: NestedBigIntFilter<$PrismaModel>
  }

  export type EnumSyncStateWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.SyncState | EnumSyncStateFieldRefInput<$PrismaModel>
    in?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    not?: NestedEnumSyncStateWithAggregatesFilter<$PrismaModel> | $Enums.SyncState
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumSyncStateFilter<$PrismaModel>
    _max?: NestedEnumSyncStateFilter<$PrismaModel>
  }

  export type EnumTaskTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskType | EnumTaskTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskTypeFilter<$PrismaModel> | $Enums.TaskType
  }

  export type EnumPriorityFilter<$PrismaModel = never> = {
    equals?: $Enums.Priority | EnumPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumPriorityFilter<$PrismaModel> | $Enums.Priority
  }

  export type EnumTaskStateFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskState | EnumTaskStateFieldRefInput<$PrismaModel>
    in?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskStateFilter<$PrismaModel> | $Enums.TaskState
  }

  export type IntNullableFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel> | null
    in?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntNullableFilter<$PrismaModel> | number | null
  }

  export type FieldNullableRelationFilter = {
    is?: FieldWhereInput | null
    isNot?: FieldWhereInput | null
  }

  export type TaskCountOrderByAggregateInput = {
    id?: SortOrder
    title?: SortOrder
    titleAr?: SortOrder
    description?: SortOrder
    taskType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    dueDate?: SortOrder
    scheduledTime?: SortOrder
    completedAt?: SortOrder
    assignedTo?: SortOrder
    createdBy?: SortOrder
    fieldId?: SortOrder
    estimatedMinutes?: SortOrder
    actualMinutes?: SortOrder
    completionNotes?: SortOrder
    evidence?: SortOrder
    serverUpdatedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type TaskAvgOrderByAggregateInput = {
    estimatedMinutes?: SortOrder
    actualMinutes?: SortOrder
  }

  export type TaskMaxOrderByAggregateInput = {
    id?: SortOrder
    title?: SortOrder
    titleAr?: SortOrder
    description?: SortOrder
    taskType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    dueDate?: SortOrder
    scheduledTime?: SortOrder
    completedAt?: SortOrder
    assignedTo?: SortOrder
    createdBy?: SortOrder
    fieldId?: SortOrder
    estimatedMinutes?: SortOrder
    actualMinutes?: SortOrder
    completionNotes?: SortOrder
    serverUpdatedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type TaskMinOrderByAggregateInput = {
    id?: SortOrder
    title?: SortOrder
    titleAr?: SortOrder
    description?: SortOrder
    taskType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    dueDate?: SortOrder
    scheduledTime?: SortOrder
    completedAt?: SortOrder
    assignedTo?: SortOrder
    createdBy?: SortOrder
    fieldId?: SortOrder
    estimatedMinutes?: SortOrder
    actualMinutes?: SortOrder
    completionNotes?: SortOrder
    serverUpdatedAt?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type TaskSumOrderByAggregateInput = {
    estimatedMinutes?: SortOrder
    actualMinutes?: SortOrder
  }

  export type EnumTaskTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskType | EnumTaskTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskTypeWithAggregatesFilter<$PrismaModel> | $Enums.TaskType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTaskTypeFilter<$PrismaModel>
    _max?: NestedEnumTaskTypeFilter<$PrismaModel>
  }

  export type EnumPriorityWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.Priority | EnumPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumPriorityWithAggregatesFilter<$PrismaModel> | $Enums.Priority
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumPriorityFilter<$PrismaModel>
    _max?: NestedEnumPriorityFilter<$PrismaModel>
  }

  export type EnumTaskStateWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskState | EnumTaskStateFieldRefInput<$PrismaModel>
    in?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskStateWithAggregatesFilter<$PrismaModel> | $Enums.TaskState
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTaskStateFilter<$PrismaModel>
    _max?: NestedEnumTaskStateFilter<$PrismaModel>
  }

  export type IntNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel> | null
    in?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntNullableWithAggregatesFilter<$PrismaModel> | number | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _avg?: NestedFloatNullableFilter<$PrismaModel>
    _sum?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedIntNullableFilter<$PrismaModel>
    _max?: NestedIntNullableFilter<$PrismaModel>
  }

  export type DecimalFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string
  }

  export type NdviReadingCountOrderByAggregateInput = {
    id?: SortOrder
    fieldId?: SortOrder
    value?: SortOrder
    capturedAt?: SortOrder
    source?: SortOrder
    cloudCover?: SortOrder
    quality?: SortOrder
    satelliteName?: SortOrder
    bandInfo?: SortOrder
    createdAt?: SortOrder
  }

  export type NdviReadingAvgOrderByAggregateInput = {
    value?: SortOrder
    cloudCover?: SortOrder
  }

  export type NdviReadingMaxOrderByAggregateInput = {
    id?: SortOrder
    fieldId?: SortOrder
    value?: SortOrder
    capturedAt?: SortOrder
    source?: SortOrder
    cloudCover?: SortOrder
    quality?: SortOrder
    satelliteName?: SortOrder
    createdAt?: SortOrder
  }

  export type NdviReadingMinOrderByAggregateInput = {
    id?: SortOrder
    fieldId?: SortOrder
    value?: SortOrder
    capturedAt?: SortOrder
    source?: SortOrder
    cloudCover?: SortOrder
    quality?: SortOrder
    satelliteName?: SortOrder
    createdAt?: SortOrder
  }

  export type NdviReadingSumOrderByAggregateInput = {
    value?: SortOrder
    cloudCover?: SortOrder
  }

  export type DecimalWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalWithAggregatesFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedDecimalFilter<$PrismaModel>
    _sum?: NestedDecimalFilter<$PrismaModel>
    _min?: NestedDecimalFilter<$PrismaModel>
    _max?: NestedDecimalFilter<$PrismaModel>
  }

  export type FieldBoundaryHistoryCreateNestedManyWithoutFieldInput = {
    create?: XOR<FieldBoundaryHistoryCreateWithoutFieldInput, FieldBoundaryHistoryUncheckedCreateWithoutFieldInput> | FieldBoundaryHistoryCreateWithoutFieldInput[] | FieldBoundaryHistoryUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: FieldBoundaryHistoryCreateOrConnectWithoutFieldInput | FieldBoundaryHistoryCreateOrConnectWithoutFieldInput[]
    createMany?: FieldBoundaryHistoryCreateManyFieldInputEnvelope
    connect?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
  }

  export type TaskCreateNestedManyWithoutFieldInput = {
    create?: XOR<TaskCreateWithoutFieldInput, TaskUncheckedCreateWithoutFieldInput> | TaskCreateWithoutFieldInput[] | TaskUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: TaskCreateOrConnectWithoutFieldInput | TaskCreateOrConnectWithoutFieldInput[]
    createMany?: TaskCreateManyFieldInputEnvelope
    connect?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
  }

  export type NdviReadingCreateNestedManyWithoutFieldInput = {
    create?: XOR<NdviReadingCreateWithoutFieldInput, NdviReadingUncheckedCreateWithoutFieldInput> | NdviReadingCreateWithoutFieldInput[] | NdviReadingUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: NdviReadingCreateOrConnectWithoutFieldInput | NdviReadingCreateOrConnectWithoutFieldInput[]
    createMany?: NdviReadingCreateManyFieldInputEnvelope
    connect?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
  }

  export type FieldBoundaryHistoryUncheckedCreateNestedManyWithoutFieldInput = {
    create?: XOR<FieldBoundaryHistoryCreateWithoutFieldInput, FieldBoundaryHistoryUncheckedCreateWithoutFieldInput> | FieldBoundaryHistoryCreateWithoutFieldInput[] | FieldBoundaryHistoryUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: FieldBoundaryHistoryCreateOrConnectWithoutFieldInput | FieldBoundaryHistoryCreateOrConnectWithoutFieldInput[]
    createMany?: FieldBoundaryHistoryCreateManyFieldInputEnvelope
    connect?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
  }

  export type TaskUncheckedCreateNestedManyWithoutFieldInput = {
    create?: XOR<TaskCreateWithoutFieldInput, TaskUncheckedCreateWithoutFieldInput> | TaskCreateWithoutFieldInput[] | TaskUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: TaskCreateOrConnectWithoutFieldInput | TaskCreateOrConnectWithoutFieldInput[]
    createMany?: TaskCreateManyFieldInputEnvelope
    connect?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
  }

  export type NdviReadingUncheckedCreateNestedManyWithoutFieldInput = {
    create?: XOR<NdviReadingCreateWithoutFieldInput, NdviReadingUncheckedCreateWithoutFieldInput> | NdviReadingCreateWithoutFieldInput[] | NdviReadingUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: NdviReadingCreateOrConnectWithoutFieldInput | NdviReadingCreateOrConnectWithoutFieldInput[]
    createMany?: NdviReadingCreateManyFieldInputEnvelope
    connect?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
  }

  export type StringFieldUpdateOperationsInput = {
    set?: string
  }

  export type IntFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type NullableStringFieldUpdateOperationsInput = {
    set?: string | null
  }

  export type NullableDecimalFieldUpdateOperationsInput = {
    set?: Decimal | DecimalJsLike | number | string | null
    increment?: Decimal | DecimalJsLike | number | string
    decrement?: Decimal | DecimalJsLike | number | string
    multiply?: Decimal | DecimalJsLike | number | string
    divide?: Decimal | DecimalJsLike | number | string
  }

  export type EnumFieldStatusFieldUpdateOperationsInput = {
    set?: $Enums.FieldStatus
  }

  export type NullableDateTimeFieldUpdateOperationsInput = {
    set?: Date | string | null
  }

  export type BoolFieldUpdateOperationsInput = {
    set?: boolean
  }

  export type DateTimeFieldUpdateOperationsInput = {
    set?: Date | string
  }

  export type FieldBoundaryHistoryUpdateManyWithoutFieldNestedInput = {
    create?: XOR<FieldBoundaryHistoryCreateWithoutFieldInput, FieldBoundaryHistoryUncheckedCreateWithoutFieldInput> | FieldBoundaryHistoryCreateWithoutFieldInput[] | FieldBoundaryHistoryUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: FieldBoundaryHistoryCreateOrConnectWithoutFieldInput | FieldBoundaryHistoryCreateOrConnectWithoutFieldInput[]
    upsert?: FieldBoundaryHistoryUpsertWithWhereUniqueWithoutFieldInput | FieldBoundaryHistoryUpsertWithWhereUniqueWithoutFieldInput[]
    createMany?: FieldBoundaryHistoryCreateManyFieldInputEnvelope
    set?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    disconnect?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    delete?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    connect?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    update?: FieldBoundaryHistoryUpdateWithWhereUniqueWithoutFieldInput | FieldBoundaryHistoryUpdateWithWhereUniqueWithoutFieldInput[]
    updateMany?: FieldBoundaryHistoryUpdateManyWithWhereWithoutFieldInput | FieldBoundaryHistoryUpdateManyWithWhereWithoutFieldInput[]
    deleteMany?: FieldBoundaryHistoryScalarWhereInput | FieldBoundaryHistoryScalarWhereInput[]
  }

  export type TaskUpdateManyWithoutFieldNestedInput = {
    create?: XOR<TaskCreateWithoutFieldInput, TaskUncheckedCreateWithoutFieldInput> | TaskCreateWithoutFieldInput[] | TaskUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: TaskCreateOrConnectWithoutFieldInput | TaskCreateOrConnectWithoutFieldInput[]
    upsert?: TaskUpsertWithWhereUniqueWithoutFieldInput | TaskUpsertWithWhereUniqueWithoutFieldInput[]
    createMany?: TaskCreateManyFieldInputEnvelope
    set?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    disconnect?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    delete?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    connect?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    update?: TaskUpdateWithWhereUniqueWithoutFieldInput | TaskUpdateWithWhereUniqueWithoutFieldInput[]
    updateMany?: TaskUpdateManyWithWhereWithoutFieldInput | TaskUpdateManyWithWhereWithoutFieldInput[]
    deleteMany?: TaskScalarWhereInput | TaskScalarWhereInput[]
  }

  export type NdviReadingUpdateManyWithoutFieldNestedInput = {
    create?: XOR<NdviReadingCreateWithoutFieldInput, NdviReadingUncheckedCreateWithoutFieldInput> | NdviReadingCreateWithoutFieldInput[] | NdviReadingUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: NdviReadingCreateOrConnectWithoutFieldInput | NdviReadingCreateOrConnectWithoutFieldInput[]
    upsert?: NdviReadingUpsertWithWhereUniqueWithoutFieldInput | NdviReadingUpsertWithWhereUniqueWithoutFieldInput[]
    createMany?: NdviReadingCreateManyFieldInputEnvelope
    set?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    disconnect?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    delete?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    connect?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    update?: NdviReadingUpdateWithWhereUniqueWithoutFieldInput | NdviReadingUpdateWithWhereUniqueWithoutFieldInput[]
    updateMany?: NdviReadingUpdateManyWithWhereWithoutFieldInput | NdviReadingUpdateManyWithWhereWithoutFieldInput[]
    deleteMany?: NdviReadingScalarWhereInput | NdviReadingScalarWhereInput[]
  }

  export type FieldBoundaryHistoryUncheckedUpdateManyWithoutFieldNestedInput = {
    create?: XOR<FieldBoundaryHistoryCreateWithoutFieldInput, FieldBoundaryHistoryUncheckedCreateWithoutFieldInput> | FieldBoundaryHistoryCreateWithoutFieldInput[] | FieldBoundaryHistoryUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: FieldBoundaryHistoryCreateOrConnectWithoutFieldInput | FieldBoundaryHistoryCreateOrConnectWithoutFieldInput[]
    upsert?: FieldBoundaryHistoryUpsertWithWhereUniqueWithoutFieldInput | FieldBoundaryHistoryUpsertWithWhereUniqueWithoutFieldInput[]
    createMany?: FieldBoundaryHistoryCreateManyFieldInputEnvelope
    set?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    disconnect?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    delete?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    connect?: FieldBoundaryHistoryWhereUniqueInput | FieldBoundaryHistoryWhereUniqueInput[]
    update?: FieldBoundaryHistoryUpdateWithWhereUniqueWithoutFieldInput | FieldBoundaryHistoryUpdateWithWhereUniqueWithoutFieldInput[]
    updateMany?: FieldBoundaryHistoryUpdateManyWithWhereWithoutFieldInput | FieldBoundaryHistoryUpdateManyWithWhereWithoutFieldInput[]
    deleteMany?: FieldBoundaryHistoryScalarWhereInput | FieldBoundaryHistoryScalarWhereInput[]
  }

  export type TaskUncheckedUpdateManyWithoutFieldNestedInput = {
    create?: XOR<TaskCreateWithoutFieldInput, TaskUncheckedCreateWithoutFieldInput> | TaskCreateWithoutFieldInput[] | TaskUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: TaskCreateOrConnectWithoutFieldInput | TaskCreateOrConnectWithoutFieldInput[]
    upsert?: TaskUpsertWithWhereUniqueWithoutFieldInput | TaskUpsertWithWhereUniqueWithoutFieldInput[]
    createMany?: TaskCreateManyFieldInputEnvelope
    set?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    disconnect?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    delete?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    connect?: TaskWhereUniqueInput | TaskWhereUniqueInput[]
    update?: TaskUpdateWithWhereUniqueWithoutFieldInput | TaskUpdateWithWhereUniqueWithoutFieldInput[]
    updateMany?: TaskUpdateManyWithWhereWithoutFieldInput | TaskUpdateManyWithWhereWithoutFieldInput[]
    deleteMany?: TaskScalarWhereInput | TaskScalarWhereInput[]
  }

  export type NdviReadingUncheckedUpdateManyWithoutFieldNestedInput = {
    create?: XOR<NdviReadingCreateWithoutFieldInput, NdviReadingUncheckedCreateWithoutFieldInput> | NdviReadingCreateWithoutFieldInput[] | NdviReadingUncheckedCreateWithoutFieldInput[]
    connectOrCreate?: NdviReadingCreateOrConnectWithoutFieldInput | NdviReadingCreateOrConnectWithoutFieldInput[]
    upsert?: NdviReadingUpsertWithWhereUniqueWithoutFieldInput | NdviReadingUpsertWithWhereUniqueWithoutFieldInput[]
    createMany?: NdviReadingCreateManyFieldInputEnvelope
    set?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    disconnect?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    delete?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    connect?: NdviReadingWhereUniqueInput | NdviReadingWhereUniqueInput[]
    update?: NdviReadingUpdateWithWhereUniqueWithoutFieldInput | NdviReadingUpdateWithWhereUniqueWithoutFieldInput[]
    updateMany?: NdviReadingUpdateManyWithWhereWithoutFieldInput | NdviReadingUpdateManyWithWhereWithoutFieldInput[]
    deleteMany?: NdviReadingScalarWhereInput | NdviReadingScalarWhereInput[]
  }

  export type FieldCreateNestedOneWithoutBoundaryHistoryInput = {
    create?: XOR<FieldCreateWithoutBoundaryHistoryInput, FieldUncheckedCreateWithoutBoundaryHistoryInput>
    connectOrCreate?: FieldCreateOrConnectWithoutBoundaryHistoryInput
    connect?: FieldWhereUniqueInput
  }

  export type EnumChangeSourceFieldUpdateOperationsInput = {
    set?: $Enums.ChangeSource
  }

  export type FieldUpdateOneRequiredWithoutBoundaryHistoryNestedInput = {
    create?: XOR<FieldCreateWithoutBoundaryHistoryInput, FieldUncheckedCreateWithoutBoundaryHistoryInput>
    connectOrCreate?: FieldCreateOrConnectWithoutBoundaryHistoryInput
    upsert?: FieldUpsertWithoutBoundaryHistoryInput
    connect?: FieldWhereUniqueInput
    update?: XOR<XOR<FieldUpdateToOneWithWhereWithoutBoundaryHistoryInput, FieldUpdateWithoutBoundaryHistoryInput>, FieldUncheckedUpdateWithoutBoundaryHistoryInput>
  }

  export type BigIntFieldUpdateOperationsInput = {
    set?: bigint | number
    increment?: bigint | number
    decrement?: bigint | number
    multiply?: bigint | number
    divide?: bigint | number
  }

  export type EnumSyncStateFieldUpdateOperationsInput = {
    set?: $Enums.SyncState
  }

  export type FieldCreateNestedOneWithoutTasksInput = {
    create?: XOR<FieldCreateWithoutTasksInput, FieldUncheckedCreateWithoutTasksInput>
    connectOrCreate?: FieldCreateOrConnectWithoutTasksInput
    connect?: FieldWhereUniqueInput
  }

  export type EnumTaskTypeFieldUpdateOperationsInput = {
    set?: $Enums.TaskType
  }

  export type EnumPriorityFieldUpdateOperationsInput = {
    set?: $Enums.Priority
  }

  export type EnumTaskStateFieldUpdateOperationsInput = {
    set?: $Enums.TaskState
  }

  export type NullableIntFieldUpdateOperationsInput = {
    set?: number | null
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type FieldUpdateOneWithoutTasksNestedInput = {
    create?: XOR<FieldCreateWithoutTasksInput, FieldUncheckedCreateWithoutTasksInput>
    connectOrCreate?: FieldCreateOrConnectWithoutTasksInput
    upsert?: FieldUpsertWithoutTasksInput
    disconnect?: FieldWhereInput | boolean
    delete?: FieldWhereInput | boolean
    connect?: FieldWhereUniqueInput
    update?: XOR<XOR<FieldUpdateToOneWithWhereWithoutTasksInput, FieldUpdateWithoutTasksInput>, FieldUncheckedUpdateWithoutTasksInput>
  }

  export type FieldCreateNestedOneWithoutNdviReadingsInput = {
    create?: XOR<FieldCreateWithoutNdviReadingsInput, FieldUncheckedCreateWithoutNdviReadingsInput>
    connectOrCreate?: FieldCreateOrConnectWithoutNdviReadingsInput
    connect?: FieldWhereUniqueInput
  }

  export type DecimalFieldUpdateOperationsInput = {
    set?: Decimal | DecimalJsLike | number | string
    increment?: Decimal | DecimalJsLike | number | string
    decrement?: Decimal | DecimalJsLike | number | string
    multiply?: Decimal | DecimalJsLike | number | string
    divide?: Decimal | DecimalJsLike | number | string
  }

  export type FieldUpdateOneRequiredWithoutNdviReadingsNestedInput = {
    create?: XOR<FieldCreateWithoutNdviReadingsInput, FieldUncheckedCreateWithoutNdviReadingsInput>
    connectOrCreate?: FieldCreateOrConnectWithoutNdviReadingsInput
    upsert?: FieldUpsertWithoutNdviReadingsInput
    connect?: FieldWhereUniqueInput
    update?: XOR<XOR<FieldUpdateToOneWithWhereWithoutNdviReadingsInput, FieldUpdateWithoutNdviReadingsInput>, FieldUncheckedUpdateWithoutNdviReadingsInput>
  }

  export type NestedUuidFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedUuidFilter<$PrismaModel> | string
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

  export type NestedUuidNullableFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedUuidNullableFilter<$PrismaModel> | string | null
  }

  export type NestedDecimalNullableFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel> | null
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalNullableFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string | null
  }

  export type NestedEnumFieldStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.FieldStatus | EnumFieldStatusFieldRefInput<$PrismaModel>
    in?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumFieldStatusFilter<$PrismaModel> | $Enums.FieldStatus
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

  export type NestedBoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
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

  export type NestedUuidWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel>
    in?: string[] | ListStringFieldRefInput<$PrismaModel>
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel>
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedUuidWithAggregatesFilter<$PrismaModel> | string
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedStringFilter<$PrismaModel>
    _max?: NestedStringFilter<$PrismaModel>
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

  export type NestedUuidNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: string | StringFieldRefInput<$PrismaModel> | null
    in?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    notIn?: string[] | ListStringFieldRefInput<$PrismaModel> | null
    lt?: string | StringFieldRefInput<$PrismaModel>
    lte?: string | StringFieldRefInput<$PrismaModel>
    gt?: string | StringFieldRefInput<$PrismaModel>
    gte?: string | StringFieldRefInput<$PrismaModel>
    not?: NestedUuidNullableWithAggregatesFilter<$PrismaModel> | string | null
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

  export type NestedDecimalNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel> | null
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel> | null
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalNullableWithAggregatesFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _avg?: NestedDecimalNullableFilter<$PrismaModel>
    _sum?: NestedDecimalNullableFilter<$PrismaModel>
    _min?: NestedDecimalNullableFilter<$PrismaModel>
    _max?: NestedDecimalNullableFilter<$PrismaModel>
  }

  export type NestedEnumFieldStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.FieldStatus | EnumFieldStatusFieldRefInput<$PrismaModel>
    in?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.FieldStatus[] | ListEnumFieldStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumFieldStatusWithAggregatesFilter<$PrismaModel> | $Enums.FieldStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumFieldStatusFilter<$PrismaModel>
    _max?: NestedEnumFieldStatusFilter<$PrismaModel>
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

  export type NestedBoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
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

  export type NestedEnumChangeSourceFilter<$PrismaModel = never> = {
    equals?: $Enums.ChangeSource | EnumChangeSourceFieldRefInput<$PrismaModel>
    in?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    notIn?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    not?: NestedEnumChangeSourceFilter<$PrismaModel> | $Enums.ChangeSource
  }

  export type NestedEnumChangeSourceWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.ChangeSource | EnumChangeSourceFieldRefInput<$PrismaModel>
    in?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    notIn?: $Enums.ChangeSource[] | ListEnumChangeSourceFieldRefInput<$PrismaModel>
    not?: NestedEnumChangeSourceWithAggregatesFilter<$PrismaModel> | $Enums.ChangeSource
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumChangeSourceFilter<$PrismaModel>
    _max?: NestedEnumChangeSourceFilter<$PrismaModel>
  }

  export type NestedBigIntFilter<$PrismaModel = never> = {
    equals?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    in?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    notIn?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    lt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    lte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    not?: NestedBigIntFilter<$PrismaModel> | bigint | number
  }

  export type NestedEnumSyncStateFilter<$PrismaModel = never> = {
    equals?: $Enums.SyncState | EnumSyncStateFieldRefInput<$PrismaModel>
    in?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    not?: NestedEnumSyncStateFilter<$PrismaModel> | $Enums.SyncState
  }

  export type NestedBigIntWithAggregatesFilter<$PrismaModel = never> = {
    equals?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    in?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    notIn?: bigint[] | number[] | ListBigIntFieldRefInput<$PrismaModel>
    lt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    lte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gt?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    gte?: bigint | number | BigIntFieldRefInput<$PrismaModel>
    not?: NestedBigIntWithAggregatesFilter<$PrismaModel> | bigint | number
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedFloatFilter<$PrismaModel>
    _sum?: NestedBigIntFilter<$PrismaModel>
    _min?: NestedBigIntFilter<$PrismaModel>
    _max?: NestedBigIntFilter<$PrismaModel>
  }

  export type NestedEnumSyncStateWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.SyncState | EnumSyncStateFieldRefInput<$PrismaModel>
    in?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.SyncState[] | ListEnumSyncStateFieldRefInput<$PrismaModel>
    not?: NestedEnumSyncStateWithAggregatesFilter<$PrismaModel> | $Enums.SyncState
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumSyncStateFilter<$PrismaModel>
    _max?: NestedEnumSyncStateFilter<$PrismaModel>
  }

  export type NestedEnumTaskTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskType | EnumTaskTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskTypeFilter<$PrismaModel> | $Enums.TaskType
  }

  export type NestedEnumPriorityFilter<$PrismaModel = never> = {
    equals?: $Enums.Priority | EnumPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumPriorityFilter<$PrismaModel> | $Enums.Priority
  }

  export type NestedEnumTaskStateFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskState | EnumTaskStateFieldRefInput<$PrismaModel>
    in?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskStateFilter<$PrismaModel> | $Enums.TaskState
  }

  export type NestedEnumTaskTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskType | EnumTaskTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskType[] | ListEnumTaskTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskTypeWithAggregatesFilter<$PrismaModel> | $Enums.TaskType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTaskTypeFilter<$PrismaModel>
    _max?: NestedEnumTaskTypeFilter<$PrismaModel>
  }

  export type NestedEnumPriorityWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.Priority | EnumPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.Priority[] | ListEnumPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumPriorityWithAggregatesFilter<$PrismaModel> | $Enums.Priority
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumPriorityFilter<$PrismaModel>
    _max?: NestedEnumPriorityFilter<$PrismaModel>
  }

  export type NestedEnumTaskStateWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TaskState | EnumTaskStateFieldRefInput<$PrismaModel>
    in?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    notIn?: $Enums.TaskState[] | ListEnumTaskStateFieldRefInput<$PrismaModel>
    not?: NestedEnumTaskStateWithAggregatesFilter<$PrismaModel> | $Enums.TaskState
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTaskStateFilter<$PrismaModel>
    _max?: NestedEnumTaskStateFilter<$PrismaModel>
  }

  export type NestedIntNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: number | IntFieldRefInput<$PrismaModel> | null
    in?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    notIn?: number[] | ListIntFieldRefInput<$PrismaModel> | null
    lt?: number | IntFieldRefInput<$PrismaModel>
    lte?: number | IntFieldRefInput<$PrismaModel>
    gt?: number | IntFieldRefInput<$PrismaModel>
    gte?: number | IntFieldRefInput<$PrismaModel>
    not?: NestedIntNullableWithAggregatesFilter<$PrismaModel> | number | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _avg?: NestedFloatNullableFilter<$PrismaModel>
    _sum?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedIntNullableFilter<$PrismaModel>
    _max?: NestedIntNullableFilter<$PrismaModel>
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

  export type NestedDecimalFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string
  }

  export type NestedDecimalWithAggregatesFilter<$PrismaModel = never> = {
    equals?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    in?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    notIn?: Decimal[] | DecimalJsLike[] | number[] | string[] | ListDecimalFieldRefInput<$PrismaModel>
    lt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    lte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gt?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    gte?: Decimal | DecimalJsLike | number | string | DecimalFieldRefInput<$PrismaModel>
    not?: NestedDecimalWithAggregatesFilter<$PrismaModel> | Decimal | DecimalJsLike | number | string
    _count?: NestedIntFilter<$PrismaModel>
    _avg?: NestedDecimalFilter<$PrismaModel>
    _sum?: NestedDecimalFilter<$PrismaModel>
    _min?: NestedDecimalFilter<$PrismaModel>
    _max?: NestedDecimalFilter<$PrismaModel>
  }

  export type FieldBoundaryHistoryCreateWithoutFieldInput = {
    id?: string
    versionAtChange: number
    areaChangeHectares?: Decimal | DecimalJsLike | number | string | null
    changedBy?: string | null
    changeReason?: string | null
    changeSource?: $Enums.ChangeSource
    deviceId?: string | null
    createdAt?: Date | string
  }

  export type FieldBoundaryHistoryUncheckedCreateWithoutFieldInput = {
    id?: string
    versionAtChange: number
    areaChangeHectares?: Decimal | DecimalJsLike | number | string | null
    changedBy?: string | null
    changeReason?: string | null
    changeSource?: $Enums.ChangeSource
    deviceId?: string | null
    createdAt?: Date | string
  }

  export type FieldBoundaryHistoryCreateOrConnectWithoutFieldInput = {
    where: FieldBoundaryHistoryWhereUniqueInput
    create: XOR<FieldBoundaryHistoryCreateWithoutFieldInput, FieldBoundaryHistoryUncheckedCreateWithoutFieldInput>
  }

  export type FieldBoundaryHistoryCreateManyFieldInputEnvelope = {
    data: FieldBoundaryHistoryCreateManyFieldInput | FieldBoundaryHistoryCreateManyFieldInput[]
    skipDuplicates?: boolean
  }

  export type TaskCreateWithoutFieldInput = {
    id?: string
    title: string
    titleAr?: string | null
    description?: string | null
    taskType?: $Enums.TaskType
    priority?: $Enums.Priority
    status?: $Enums.TaskState
    dueDate?: Date | string | null
    scheduledTime?: string | null
    completedAt?: Date | string | null
    assignedTo?: string | null
    createdBy: string
    estimatedMinutes?: number | null
    actualMinutes?: number | null
    completionNotes?: string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: Date | string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type TaskUncheckedCreateWithoutFieldInput = {
    id?: string
    title: string
    titleAr?: string | null
    description?: string | null
    taskType?: $Enums.TaskType
    priority?: $Enums.Priority
    status?: $Enums.TaskState
    dueDate?: Date | string | null
    scheduledTime?: string | null
    completedAt?: Date | string | null
    assignedTo?: string | null
    createdBy: string
    estimatedMinutes?: number | null
    actualMinutes?: number | null
    completionNotes?: string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: Date | string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type TaskCreateOrConnectWithoutFieldInput = {
    where: TaskWhereUniqueInput
    create: XOR<TaskCreateWithoutFieldInput, TaskUncheckedCreateWithoutFieldInput>
  }

  export type TaskCreateManyFieldInputEnvelope = {
    data: TaskCreateManyFieldInput | TaskCreateManyFieldInput[]
    skipDuplicates?: boolean
  }

  export type NdviReadingCreateWithoutFieldInput = {
    id?: string
    value: Decimal | DecimalJsLike | number | string
    capturedAt: Date | string
    source?: string
    cloudCover?: Decimal | DecimalJsLike | number | string | null
    quality?: string | null
    satelliteName?: string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type NdviReadingUncheckedCreateWithoutFieldInput = {
    id?: string
    value: Decimal | DecimalJsLike | number | string
    capturedAt: Date | string
    source?: string
    cloudCover?: Decimal | DecimalJsLike | number | string | null
    quality?: string | null
    satelliteName?: string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type NdviReadingCreateOrConnectWithoutFieldInput = {
    where: NdviReadingWhereUniqueInput
    create: XOR<NdviReadingCreateWithoutFieldInput, NdviReadingUncheckedCreateWithoutFieldInput>
  }

  export type NdviReadingCreateManyFieldInputEnvelope = {
    data: NdviReadingCreateManyFieldInput | NdviReadingCreateManyFieldInput[]
    skipDuplicates?: boolean
  }

  export type FieldBoundaryHistoryUpsertWithWhereUniqueWithoutFieldInput = {
    where: FieldBoundaryHistoryWhereUniqueInput
    update: XOR<FieldBoundaryHistoryUpdateWithoutFieldInput, FieldBoundaryHistoryUncheckedUpdateWithoutFieldInput>
    create: XOR<FieldBoundaryHistoryCreateWithoutFieldInput, FieldBoundaryHistoryUncheckedCreateWithoutFieldInput>
  }

  export type FieldBoundaryHistoryUpdateWithWhereUniqueWithoutFieldInput = {
    where: FieldBoundaryHistoryWhereUniqueInput
    data: XOR<FieldBoundaryHistoryUpdateWithoutFieldInput, FieldBoundaryHistoryUncheckedUpdateWithoutFieldInput>
  }

  export type FieldBoundaryHistoryUpdateManyWithWhereWithoutFieldInput = {
    where: FieldBoundaryHistoryScalarWhereInput
    data: XOR<FieldBoundaryHistoryUpdateManyMutationInput, FieldBoundaryHistoryUncheckedUpdateManyWithoutFieldInput>
  }

  export type FieldBoundaryHistoryScalarWhereInput = {
    AND?: FieldBoundaryHistoryScalarWhereInput | FieldBoundaryHistoryScalarWhereInput[]
    OR?: FieldBoundaryHistoryScalarWhereInput[]
    NOT?: FieldBoundaryHistoryScalarWhereInput | FieldBoundaryHistoryScalarWhereInput[]
    id?: UuidFilter<"FieldBoundaryHistory"> | string
    fieldId?: UuidFilter<"FieldBoundaryHistory"> | string
    versionAtChange?: IntFilter<"FieldBoundaryHistory"> | number
    areaChangeHectares?: DecimalNullableFilter<"FieldBoundaryHistory"> | Decimal | DecimalJsLike | number | string | null
    changedBy?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    changeReason?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    changeSource?: EnumChangeSourceFilter<"FieldBoundaryHistory"> | $Enums.ChangeSource
    deviceId?: StringNullableFilter<"FieldBoundaryHistory"> | string | null
    createdAt?: DateTimeFilter<"FieldBoundaryHistory"> | Date | string
  }

  export type TaskUpsertWithWhereUniqueWithoutFieldInput = {
    where: TaskWhereUniqueInput
    update: XOR<TaskUpdateWithoutFieldInput, TaskUncheckedUpdateWithoutFieldInput>
    create: XOR<TaskCreateWithoutFieldInput, TaskUncheckedCreateWithoutFieldInput>
  }

  export type TaskUpdateWithWhereUniqueWithoutFieldInput = {
    where: TaskWhereUniqueInput
    data: XOR<TaskUpdateWithoutFieldInput, TaskUncheckedUpdateWithoutFieldInput>
  }

  export type TaskUpdateManyWithWhereWithoutFieldInput = {
    where: TaskScalarWhereInput
    data: XOR<TaskUpdateManyMutationInput, TaskUncheckedUpdateManyWithoutFieldInput>
  }

  export type TaskScalarWhereInput = {
    AND?: TaskScalarWhereInput | TaskScalarWhereInput[]
    OR?: TaskScalarWhereInput[]
    NOT?: TaskScalarWhereInput | TaskScalarWhereInput[]
    id?: UuidFilter<"Task"> | string
    title?: StringFilter<"Task"> | string
    titleAr?: StringNullableFilter<"Task"> | string | null
    description?: StringNullableFilter<"Task"> | string | null
    taskType?: EnumTaskTypeFilter<"Task"> | $Enums.TaskType
    priority?: EnumPriorityFilter<"Task"> | $Enums.Priority
    status?: EnumTaskStateFilter<"Task"> | $Enums.TaskState
    dueDate?: DateTimeNullableFilter<"Task"> | Date | string | null
    scheduledTime?: StringNullableFilter<"Task"> | string | null
    completedAt?: DateTimeNullableFilter<"Task"> | Date | string | null
    assignedTo?: StringNullableFilter<"Task"> | string | null
    createdBy?: StringFilter<"Task"> | string
    fieldId?: UuidNullableFilter<"Task"> | string | null
    estimatedMinutes?: IntNullableFilter<"Task"> | number | null
    actualMinutes?: IntNullableFilter<"Task"> | number | null
    completionNotes?: StringNullableFilter<"Task"> | string | null
    evidence?: JsonNullableFilter<"Task">
    serverUpdatedAt?: DateTimeFilter<"Task"> | Date | string
    createdAt?: DateTimeFilter<"Task"> | Date | string
    updatedAt?: DateTimeFilter<"Task"> | Date | string
  }

  export type NdviReadingUpsertWithWhereUniqueWithoutFieldInput = {
    where: NdviReadingWhereUniqueInput
    update: XOR<NdviReadingUpdateWithoutFieldInput, NdviReadingUncheckedUpdateWithoutFieldInput>
    create: XOR<NdviReadingCreateWithoutFieldInput, NdviReadingUncheckedCreateWithoutFieldInput>
  }

  export type NdviReadingUpdateWithWhereUniqueWithoutFieldInput = {
    where: NdviReadingWhereUniqueInput
    data: XOR<NdviReadingUpdateWithoutFieldInput, NdviReadingUncheckedUpdateWithoutFieldInput>
  }

  export type NdviReadingUpdateManyWithWhereWithoutFieldInput = {
    where: NdviReadingScalarWhereInput
    data: XOR<NdviReadingUpdateManyMutationInput, NdviReadingUncheckedUpdateManyWithoutFieldInput>
  }

  export type NdviReadingScalarWhereInput = {
    AND?: NdviReadingScalarWhereInput | NdviReadingScalarWhereInput[]
    OR?: NdviReadingScalarWhereInput[]
    NOT?: NdviReadingScalarWhereInput | NdviReadingScalarWhereInput[]
    id?: UuidFilter<"NdviReading"> | string
    fieldId?: UuidFilter<"NdviReading"> | string
    value?: DecimalFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFilter<"NdviReading"> | Date | string
    source?: StringFilter<"NdviReading"> | string
    cloudCover?: DecimalNullableFilter<"NdviReading"> | Decimal | DecimalJsLike | number | string | null
    quality?: StringNullableFilter<"NdviReading"> | string | null
    satelliteName?: StringNullableFilter<"NdviReading"> | string | null
    bandInfo?: JsonNullableFilter<"NdviReading">
    createdAt?: DateTimeFilter<"NdviReading"> | Date | string
  }

  export type FieldCreateWithoutBoundaryHistoryInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    tasks?: TaskCreateNestedManyWithoutFieldInput
    ndviReadings?: NdviReadingCreateNestedManyWithoutFieldInput
  }

  export type FieldUncheckedCreateWithoutBoundaryHistoryInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    tasks?: TaskUncheckedCreateNestedManyWithoutFieldInput
    ndviReadings?: NdviReadingUncheckedCreateNestedManyWithoutFieldInput
  }

  export type FieldCreateOrConnectWithoutBoundaryHistoryInput = {
    where: FieldWhereUniqueInput
    create: XOR<FieldCreateWithoutBoundaryHistoryInput, FieldUncheckedCreateWithoutBoundaryHistoryInput>
  }

  export type FieldUpsertWithoutBoundaryHistoryInput = {
    update: XOR<FieldUpdateWithoutBoundaryHistoryInput, FieldUncheckedUpdateWithoutBoundaryHistoryInput>
    create: XOR<FieldCreateWithoutBoundaryHistoryInput, FieldUncheckedCreateWithoutBoundaryHistoryInput>
    where?: FieldWhereInput
  }

  export type FieldUpdateToOneWithWhereWithoutBoundaryHistoryInput = {
    where?: FieldWhereInput
    data: XOR<FieldUpdateWithoutBoundaryHistoryInput, FieldUncheckedUpdateWithoutBoundaryHistoryInput>
  }

  export type FieldUpdateWithoutBoundaryHistoryInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    tasks?: TaskUpdateManyWithoutFieldNestedInput
    ndviReadings?: NdviReadingUpdateManyWithoutFieldNestedInput
  }

  export type FieldUncheckedUpdateWithoutBoundaryHistoryInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    tasks?: TaskUncheckedUpdateManyWithoutFieldNestedInput
    ndviReadings?: NdviReadingUncheckedUpdateManyWithoutFieldNestedInput
  }

  export type FieldCreateWithoutTasksInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    boundaryHistory?: FieldBoundaryHistoryCreateNestedManyWithoutFieldInput
    ndviReadings?: NdviReadingCreateNestedManyWithoutFieldInput
  }

  export type FieldUncheckedCreateWithoutTasksInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    boundaryHistory?: FieldBoundaryHistoryUncheckedCreateNestedManyWithoutFieldInput
    ndviReadings?: NdviReadingUncheckedCreateNestedManyWithoutFieldInput
  }

  export type FieldCreateOrConnectWithoutTasksInput = {
    where: FieldWhereUniqueInput
    create: XOR<FieldCreateWithoutTasksInput, FieldUncheckedCreateWithoutTasksInput>
  }

  export type FieldUpsertWithoutTasksInput = {
    update: XOR<FieldUpdateWithoutTasksInput, FieldUncheckedUpdateWithoutTasksInput>
    create: XOR<FieldCreateWithoutTasksInput, FieldUncheckedCreateWithoutTasksInput>
    where?: FieldWhereInput
  }

  export type FieldUpdateToOneWithWhereWithoutTasksInput = {
    where?: FieldWhereInput
    data: XOR<FieldUpdateWithoutTasksInput, FieldUncheckedUpdateWithoutTasksInput>
  }

  export type FieldUpdateWithoutTasksInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    boundaryHistory?: FieldBoundaryHistoryUpdateManyWithoutFieldNestedInput
    ndviReadings?: NdviReadingUpdateManyWithoutFieldNestedInput
  }

  export type FieldUncheckedUpdateWithoutTasksInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    boundaryHistory?: FieldBoundaryHistoryUncheckedUpdateManyWithoutFieldNestedInput
    ndviReadings?: NdviReadingUncheckedUpdateManyWithoutFieldNestedInput
  }

  export type FieldCreateWithoutNdviReadingsInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    boundaryHistory?: FieldBoundaryHistoryCreateNestedManyWithoutFieldInput
    tasks?: TaskCreateNestedManyWithoutFieldInput
  }

  export type FieldUncheckedCreateWithoutNdviReadingsInput = {
    id?: string
    version?: number
    name: string
    tenantId: string
    cropType: string
    ownerId?: string | null
    areaHectares?: Decimal | DecimalJsLike | number | string | null
    healthScore?: Decimal | DecimalJsLike | number | string | null
    ndviValue?: Decimal | DecimalJsLike | number | string | null
    status?: $Enums.FieldStatus
    plantingDate?: Date | string | null
    expectedHarvest?: Date | string | null
    irrigationType?: string | null
    soilType?: string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: boolean
    serverUpdatedAt?: Date | string
    etag?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    boundaryHistory?: FieldBoundaryHistoryUncheckedCreateNestedManyWithoutFieldInput
    tasks?: TaskUncheckedCreateNestedManyWithoutFieldInput
  }

  export type FieldCreateOrConnectWithoutNdviReadingsInput = {
    where: FieldWhereUniqueInput
    create: XOR<FieldCreateWithoutNdviReadingsInput, FieldUncheckedCreateWithoutNdviReadingsInput>
  }

  export type FieldUpsertWithoutNdviReadingsInput = {
    update: XOR<FieldUpdateWithoutNdviReadingsInput, FieldUncheckedUpdateWithoutNdviReadingsInput>
    create: XOR<FieldCreateWithoutNdviReadingsInput, FieldUncheckedCreateWithoutNdviReadingsInput>
    where?: FieldWhereInput
  }

  export type FieldUpdateToOneWithWhereWithoutNdviReadingsInput = {
    where?: FieldWhereInput
    data: XOR<FieldUpdateWithoutNdviReadingsInput, FieldUncheckedUpdateWithoutNdviReadingsInput>
  }

  export type FieldUpdateWithoutNdviReadingsInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    boundaryHistory?: FieldBoundaryHistoryUpdateManyWithoutFieldNestedInput
    tasks?: TaskUpdateManyWithoutFieldNestedInput
  }

  export type FieldUncheckedUpdateWithoutNdviReadingsInput = {
    id?: StringFieldUpdateOperationsInput | string
    version?: IntFieldUpdateOperationsInput | number
    name?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    cropType?: StringFieldUpdateOperationsInput | string
    ownerId?: NullableStringFieldUpdateOperationsInput | string | null
    areaHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    healthScore?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    ndviValue?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    status?: EnumFieldStatusFieldUpdateOperationsInput | $Enums.FieldStatus
    plantingDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    expectedHarvest?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    irrigationType?: NullableStringFieldUpdateOperationsInput | string | null
    soilType?: NullableStringFieldUpdateOperationsInput | string | null
    metadata?: NullableJsonNullValueInput | InputJsonValue
    isDeleted?: BoolFieldUpdateOperationsInput | boolean
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    etag?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    boundaryHistory?: FieldBoundaryHistoryUncheckedUpdateManyWithoutFieldNestedInput
    tasks?: TaskUncheckedUpdateManyWithoutFieldNestedInput
  }

  export type FieldBoundaryHistoryCreateManyFieldInput = {
    id?: string
    versionAtChange: number
    areaChangeHectares?: Decimal | DecimalJsLike | number | string | null
    changedBy?: string | null
    changeReason?: string | null
    changeSource?: $Enums.ChangeSource
    deviceId?: string | null
    createdAt?: Date | string
  }

  export type TaskCreateManyFieldInput = {
    id?: string
    title: string
    titleAr?: string | null
    description?: string | null
    taskType?: $Enums.TaskType
    priority?: $Enums.Priority
    status?: $Enums.TaskState
    dueDate?: Date | string | null
    scheduledTime?: string | null
    completedAt?: Date | string | null
    assignedTo?: string | null
    createdBy: string
    estimatedMinutes?: number | null
    actualMinutes?: number | null
    completionNotes?: string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: Date | string
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type NdviReadingCreateManyFieldInput = {
    id?: string
    value: Decimal | DecimalJsLike | number | string
    capturedAt: Date | string
    source?: string
    cloudCover?: Decimal | DecimalJsLike | number | string | null
    quality?: string | null
    satelliteName?: string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: Date | string
  }

  export type FieldBoundaryHistoryUpdateWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type FieldBoundaryHistoryUncheckedUpdateWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type FieldBoundaryHistoryUncheckedUpdateManyWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    versionAtChange?: IntFieldUpdateOperationsInput | number
    areaChangeHectares?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    changedBy?: NullableStringFieldUpdateOperationsInput | string | null
    changeReason?: NullableStringFieldUpdateOperationsInput | string | null
    changeSource?: EnumChangeSourceFieldUpdateOperationsInput | $Enums.ChangeSource
    deviceId?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type TaskUpdateWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type TaskUncheckedUpdateWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type TaskUncheckedUpdateManyWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    title?: StringFieldUpdateOperationsInput | string
    titleAr?: NullableStringFieldUpdateOperationsInput | string | null
    description?: NullableStringFieldUpdateOperationsInput | string | null
    taskType?: EnumTaskTypeFieldUpdateOperationsInput | $Enums.TaskType
    priority?: EnumPriorityFieldUpdateOperationsInput | $Enums.Priority
    status?: EnumTaskStateFieldUpdateOperationsInput | $Enums.TaskState
    dueDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    scheduledTime?: NullableStringFieldUpdateOperationsInput | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    assignedTo?: NullableStringFieldUpdateOperationsInput | string | null
    createdBy?: StringFieldUpdateOperationsInput | string
    estimatedMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    actualMinutes?: NullableIntFieldUpdateOperationsInput | number | null
    completionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    evidence?: NullableJsonNullValueInput | InputJsonValue
    serverUpdatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type NdviReadingUpdateWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type NdviReadingUncheckedUpdateWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type NdviReadingUncheckedUpdateManyWithoutFieldInput = {
    id?: StringFieldUpdateOperationsInput | string
    value?: DecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string
    capturedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    source?: StringFieldUpdateOperationsInput | string
    cloudCover?: NullableDecimalFieldUpdateOperationsInput | Decimal | DecimalJsLike | number | string | null
    quality?: NullableStringFieldUpdateOperationsInput | string | null
    satelliteName?: NullableStringFieldUpdateOperationsInput | string | null
    bandInfo?: NullableJsonNullValueInput | InputJsonValue
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }



  /**
   * Aliases for legacy arg types
   */
    /**
     * @deprecated Use FieldCountOutputTypeDefaultArgs instead
     */
    export type FieldCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = FieldCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use FieldDefaultArgs instead
     */
    export type FieldArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = FieldDefaultArgs<ExtArgs>
    /**
     * @deprecated Use FieldBoundaryHistoryDefaultArgs instead
     */
    export type FieldBoundaryHistoryArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = FieldBoundaryHistoryDefaultArgs<ExtArgs>
    /**
     * @deprecated Use SyncStatusDefaultArgs instead
     */
    export type SyncStatusArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = SyncStatusDefaultArgs<ExtArgs>
    /**
     * @deprecated Use TaskDefaultArgs instead
     */
    export type TaskArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = TaskDefaultArgs<ExtArgs>
    /**
     * @deprecated Use NdviReadingDefaultArgs instead
     */
    export type NdviReadingArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = NdviReadingDefaultArgs<ExtArgs>

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