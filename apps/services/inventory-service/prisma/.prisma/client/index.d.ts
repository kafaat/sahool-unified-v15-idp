
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
 * Model InventoryItem
 * 
 */
export type InventoryItem = $Result.DefaultSelection<Prisma.$InventoryItemPayload>
/**
 * Model InventoryMovement
 * 
 */
export type InventoryMovement = $Result.DefaultSelection<Prisma.$InventoryMovementPayload>
/**
 * Model InventoryAlert
 * 
 */
export type InventoryAlert = $Result.DefaultSelection<Prisma.$InventoryAlertPayload>
/**
 * Model AlertSettings
 * 
 */
export type AlertSettings = $Result.DefaultSelection<Prisma.$AlertSettingsPayload>
/**
 * Model Warehouse
 * 
 */
export type Warehouse = $Result.DefaultSelection<Prisma.$WarehousePayload>
/**
 * Model Zone
 * 
 */
export type Zone = $Result.DefaultSelection<Prisma.$ZonePayload>
/**
 * Model StorageLocation
 * 
 */
export type StorageLocation = $Result.DefaultSelection<Prisma.$StorageLocationPayload>
/**
 * Model StockTransfer
 * 
 */
export type StockTransfer = $Result.DefaultSelection<Prisma.$StockTransferPayload>

/**
 * Enums
 */
export namespace $Enums {
  export const ItemCategory: {
  SEEDS: 'SEEDS',
  FERTILIZER: 'FERTILIZER',
  PESTICIDE: 'PESTICIDE',
  HERBICIDE: 'HERBICIDE',
  FUNGICIDE: 'FUNGICIDE',
  INSECTICIDE: 'INSECTICIDE',
  EQUIPMENT: 'EQUIPMENT',
  TOOLS: 'TOOLS',
  IRRIGATION: 'IRRIGATION',
  PACKAGING: 'PACKAGING',
  FUEL: 'FUEL',
  OTHER: 'OTHER'
};

export type ItemCategory = (typeof ItemCategory)[keyof typeof ItemCategory]


export const MovementType: {
  PURCHASE: 'PURCHASE',
  SALE: 'SALE',
  RETURN: 'RETURN',
  ADJUSTMENT: 'ADJUSTMENT',
  TRANSFER: 'TRANSFER',
  WASTE: 'WASTE',
  USAGE: 'USAGE',
  PRODUCTION: 'PRODUCTION',
  RESTOCK: 'RESTOCK'
};

export type MovementType = (typeof MovementType)[keyof typeof MovementType]


export const AlertType: {
  LOW_STOCK: 'LOW_STOCK',
  OUT_OF_STOCK: 'OUT_OF_STOCK',
  EXPIRING_SOON: 'EXPIRING_SOON',
  EXPIRED: 'EXPIRED',
  REORDER_POINT: 'REORDER_POINT',
  OVERSTOCK: 'OVERSTOCK',
  STORAGE_CONDITION: 'STORAGE_CONDITION'
};

export type AlertType = (typeof AlertType)[keyof typeof AlertType]


export const AlertPriority: {
  LOW: 'LOW',
  MEDIUM: 'MEDIUM',
  HIGH: 'HIGH',
  CRITICAL: 'CRITICAL'
};

export type AlertPriority = (typeof AlertPriority)[keyof typeof AlertPriority]


export const AlertStatus: {
  ACTIVE: 'ACTIVE',
  ACKNOWLEDGED: 'ACKNOWLEDGED',
  RESOLVED: 'RESOLVED',
  SNOOZED: 'SNOOZED'
};

export type AlertStatus = (typeof AlertStatus)[keyof typeof AlertStatus]


export const WarehouseType: {
  MAIN: 'MAIN',
  FIELD: 'FIELD',
  COLD: 'COLD',
  CHEMICAL: 'CHEMICAL',
  SEED: 'SEED',
  FUEL: 'FUEL'
};

export type WarehouseType = (typeof WarehouseType)[keyof typeof WarehouseType]


export const StorageCondition: {
  AMBIENT: 'AMBIENT',
  COOL: 'COOL',
  COLD: 'COLD',
  FROZEN: 'FROZEN',
  DRY: 'DRY',
  CONTROLLED: 'CONTROLLED'
};

export type StorageCondition = (typeof StorageCondition)[keyof typeof StorageCondition]


export const TransferType: {
  INTER_WAREHOUSE: 'INTER_WAREHOUSE',
  RECEIVING: 'RECEIVING',
  DISPATCH: 'DISPATCH'
};

export type TransferType = (typeof TransferType)[keyof typeof TransferType]


export const TransferStatus: {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  IN_TRANSIT: 'IN_TRANSIT',
  COMPLETED: 'COMPLETED',
  CANCELLED: 'CANCELLED'
};

export type TransferStatus = (typeof TransferStatus)[keyof typeof TransferStatus]

}

export type ItemCategory = $Enums.ItemCategory

export const ItemCategory: typeof $Enums.ItemCategory

export type MovementType = $Enums.MovementType

export const MovementType: typeof $Enums.MovementType

export type AlertType = $Enums.AlertType

export const AlertType: typeof $Enums.AlertType

export type AlertPriority = $Enums.AlertPriority

export const AlertPriority: typeof $Enums.AlertPriority

export type AlertStatus = $Enums.AlertStatus

export const AlertStatus: typeof $Enums.AlertStatus

export type WarehouseType = $Enums.WarehouseType

export const WarehouseType: typeof $Enums.WarehouseType

export type StorageCondition = $Enums.StorageCondition

export const StorageCondition: typeof $Enums.StorageCondition

export type TransferType = $Enums.TransferType

export const TransferType: typeof $Enums.TransferType

export type TransferStatus = $Enums.TransferStatus

export const TransferStatus: typeof $Enums.TransferStatus

/**
 * ##  Prisma Client ʲˢ
 * 
 * Type-safe database client for TypeScript & Node.js
 * @example
 * ```
 * const prisma = new PrismaClient()
 * // Fetch zero or more InventoryItems
 * const inventoryItems = await prisma.inventoryItem.findMany()
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
   * // Fetch zero or more InventoryItems
   * const inventoryItems = await prisma.inventoryItem.findMany()
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
   * `prisma.inventoryItem`: Exposes CRUD operations for the **InventoryItem** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more InventoryItems
    * const inventoryItems = await prisma.inventoryItem.findMany()
    * ```
    */
  get inventoryItem(): Prisma.InventoryItemDelegate<ExtArgs>;

  /**
   * `prisma.inventoryMovement`: Exposes CRUD operations for the **InventoryMovement** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more InventoryMovements
    * const inventoryMovements = await prisma.inventoryMovement.findMany()
    * ```
    */
  get inventoryMovement(): Prisma.InventoryMovementDelegate<ExtArgs>;

  /**
   * `prisma.inventoryAlert`: Exposes CRUD operations for the **InventoryAlert** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more InventoryAlerts
    * const inventoryAlerts = await prisma.inventoryAlert.findMany()
    * ```
    */
  get inventoryAlert(): Prisma.InventoryAlertDelegate<ExtArgs>;

  /**
   * `prisma.alertSettings`: Exposes CRUD operations for the **AlertSettings** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more AlertSettings
    * const alertSettings = await prisma.alertSettings.findMany()
    * ```
    */
  get alertSettings(): Prisma.AlertSettingsDelegate<ExtArgs>;

  /**
   * `prisma.warehouse`: Exposes CRUD operations for the **Warehouse** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Warehouses
    * const warehouses = await prisma.warehouse.findMany()
    * ```
    */
  get warehouse(): Prisma.WarehouseDelegate<ExtArgs>;

  /**
   * `prisma.zone`: Exposes CRUD operations for the **Zone** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more Zones
    * const zones = await prisma.zone.findMany()
    * ```
    */
  get zone(): Prisma.ZoneDelegate<ExtArgs>;

  /**
   * `prisma.storageLocation`: Exposes CRUD operations for the **StorageLocation** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more StorageLocations
    * const storageLocations = await prisma.storageLocation.findMany()
    * ```
    */
  get storageLocation(): Prisma.StorageLocationDelegate<ExtArgs>;

  /**
   * `prisma.stockTransfer`: Exposes CRUD operations for the **StockTransfer** model.
    * Example usage:
    * ```ts
    * // Fetch zero or more StockTransfers
    * const stockTransfers = await prisma.stockTransfer.findMany()
    * ```
    */
  get stockTransfer(): Prisma.StockTransferDelegate<ExtArgs>;
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
    InventoryItem: 'InventoryItem',
    InventoryMovement: 'InventoryMovement',
    InventoryAlert: 'InventoryAlert',
    AlertSettings: 'AlertSettings',
    Warehouse: 'Warehouse',
    Zone: 'Zone',
    StorageLocation: 'StorageLocation',
    StockTransfer: 'StockTransfer'
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
      modelProps: "inventoryItem" | "inventoryMovement" | "inventoryAlert" | "alertSettings" | "warehouse" | "zone" | "storageLocation" | "stockTransfer"
      txIsolationLevel: Prisma.TransactionIsolationLevel
    }
    model: {
      InventoryItem: {
        payload: Prisma.$InventoryItemPayload<ExtArgs>
        fields: Prisma.InventoryItemFieldRefs
        operations: {
          findUnique: {
            args: Prisma.InventoryItemFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.InventoryItemFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>
          }
          findFirst: {
            args: Prisma.InventoryItemFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.InventoryItemFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>
          }
          findMany: {
            args: Prisma.InventoryItemFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>[]
          }
          create: {
            args: Prisma.InventoryItemCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>
          }
          createMany: {
            args: Prisma.InventoryItemCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.InventoryItemCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>[]
          }
          delete: {
            args: Prisma.InventoryItemDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>
          }
          update: {
            args: Prisma.InventoryItemUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>
          }
          deleteMany: {
            args: Prisma.InventoryItemDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.InventoryItemUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.InventoryItemUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryItemPayload>
          }
          aggregate: {
            args: Prisma.InventoryItemAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateInventoryItem>
          }
          groupBy: {
            args: Prisma.InventoryItemGroupByArgs<ExtArgs>
            result: $Utils.Optional<InventoryItemGroupByOutputType>[]
          }
          count: {
            args: Prisma.InventoryItemCountArgs<ExtArgs>
            result: $Utils.Optional<InventoryItemCountAggregateOutputType> | number
          }
        }
      }
      InventoryMovement: {
        payload: Prisma.$InventoryMovementPayload<ExtArgs>
        fields: Prisma.InventoryMovementFieldRefs
        operations: {
          findUnique: {
            args: Prisma.InventoryMovementFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.InventoryMovementFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>
          }
          findFirst: {
            args: Prisma.InventoryMovementFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.InventoryMovementFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>
          }
          findMany: {
            args: Prisma.InventoryMovementFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>[]
          }
          create: {
            args: Prisma.InventoryMovementCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>
          }
          createMany: {
            args: Prisma.InventoryMovementCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.InventoryMovementCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>[]
          }
          delete: {
            args: Prisma.InventoryMovementDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>
          }
          update: {
            args: Prisma.InventoryMovementUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>
          }
          deleteMany: {
            args: Prisma.InventoryMovementDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.InventoryMovementUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.InventoryMovementUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryMovementPayload>
          }
          aggregate: {
            args: Prisma.InventoryMovementAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateInventoryMovement>
          }
          groupBy: {
            args: Prisma.InventoryMovementGroupByArgs<ExtArgs>
            result: $Utils.Optional<InventoryMovementGroupByOutputType>[]
          }
          count: {
            args: Prisma.InventoryMovementCountArgs<ExtArgs>
            result: $Utils.Optional<InventoryMovementCountAggregateOutputType> | number
          }
        }
      }
      InventoryAlert: {
        payload: Prisma.$InventoryAlertPayload<ExtArgs>
        fields: Prisma.InventoryAlertFieldRefs
        operations: {
          findUnique: {
            args: Prisma.InventoryAlertFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.InventoryAlertFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>
          }
          findFirst: {
            args: Prisma.InventoryAlertFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.InventoryAlertFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>
          }
          findMany: {
            args: Prisma.InventoryAlertFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>[]
          }
          create: {
            args: Prisma.InventoryAlertCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>
          }
          createMany: {
            args: Prisma.InventoryAlertCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.InventoryAlertCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>[]
          }
          delete: {
            args: Prisma.InventoryAlertDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>
          }
          update: {
            args: Prisma.InventoryAlertUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>
          }
          deleteMany: {
            args: Prisma.InventoryAlertDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.InventoryAlertUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.InventoryAlertUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$InventoryAlertPayload>
          }
          aggregate: {
            args: Prisma.InventoryAlertAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateInventoryAlert>
          }
          groupBy: {
            args: Prisma.InventoryAlertGroupByArgs<ExtArgs>
            result: $Utils.Optional<InventoryAlertGroupByOutputType>[]
          }
          count: {
            args: Prisma.InventoryAlertCountArgs<ExtArgs>
            result: $Utils.Optional<InventoryAlertCountAggregateOutputType> | number
          }
        }
      }
      AlertSettings: {
        payload: Prisma.$AlertSettingsPayload<ExtArgs>
        fields: Prisma.AlertSettingsFieldRefs
        operations: {
          findUnique: {
            args: Prisma.AlertSettingsFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.AlertSettingsFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>
          }
          findFirst: {
            args: Prisma.AlertSettingsFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.AlertSettingsFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>
          }
          findMany: {
            args: Prisma.AlertSettingsFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>[]
          }
          create: {
            args: Prisma.AlertSettingsCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>
          }
          createMany: {
            args: Prisma.AlertSettingsCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.AlertSettingsCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>[]
          }
          delete: {
            args: Prisma.AlertSettingsDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>
          }
          update: {
            args: Prisma.AlertSettingsUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>
          }
          deleteMany: {
            args: Prisma.AlertSettingsDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.AlertSettingsUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.AlertSettingsUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$AlertSettingsPayload>
          }
          aggregate: {
            args: Prisma.AlertSettingsAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateAlertSettings>
          }
          groupBy: {
            args: Prisma.AlertSettingsGroupByArgs<ExtArgs>
            result: $Utils.Optional<AlertSettingsGroupByOutputType>[]
          }
          count: {
            args: Prisma.AlertSettingsCountArgs<ExtArgs>
            result: $Utils.Optional<AlertSettingsCountAggregateOutputType> | number
          }
        }
      }
      Warehouse: {
        payload: Prisma.$WarehousePayload<ExtArgs>
        fields: Prisma.WarehouseFieldRefs
        operations: {
          findUnique: {
            args: Prisma.WarehouseFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.WarehouseFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>
          }
          findFirst: {
            args: Prisma.WarehouseFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.WarehouseFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>
          }
          findMany: {
            args: Prisma.WarehouseFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>[]
          }
          create: {
            args: Prisma.WarehouseCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>
          }
          createMany: {
            args: Prisma.WarehouseCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.WarehouseCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>[]
          }
          delete: {
            args: Prisma.WarehouseDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>
          }
          update: {
            args: Prisma.WarehouseUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>
          }
          deleteMany: {
            args: Prisma.WarehouseDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.WarehouseUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.WarehouseUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$WarehousePayload>
          }
          aggregate: {
            args: Prisma.WarehouseAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateWarehouse>
          }
          groupBy: {
            args: Prisma.WarehouseGroupByArgs<ExtArgs>
            result: $Utils.Optional<WarehouseGroupByOutputType>[]
          }
          count: {
            args: Prisma.WarehouseCountArgs<ExtArgs>
            result: $Utils.Optional<WarehouseCountAggregateOutputType> | number
          }
        }
      }
      Zone: {
        payload: Prisma.$ZonePayload<ExtArgs>
        fields: Prisma.ZoneFieldRefs
        operations: {
          findUnique: {
            args: Prisma.ZoneFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.ZoneFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>
          }
          findFirst: {
            args: Prisma.ZoneFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.ZoneFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>
          }
          findMany: {
            args: Prisma.ZoneFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>[]
          }
          create: {
            args: Prisma.ZoneCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>
          }
          createMany: {
            args: Prisma.ZoneCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.ZoneCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>[]
          }
          delete: {
            args: Prisma.ZoneDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>
          }
          update: {
            args: Prisma.ZoneUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>
          }
          deleteMany: {
            args: Prisma.ZoneDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.ZoneUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.ZoneUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$ZonePayload>
          }
          aggregate: {
            args: Prisma.ZoneAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateZone>
          }
          groupBy: {
            args: Prisma.ZoneGroupByArgs<ExtArgs>
            result: $Utils.Optional<ZoneGroupByOutputType>[]
          }
          count: {
            args: Prisma.ZoneCountArgs<ExtArgs>
            result: $Utils.Optional<ZoneCountAggregateOutputType> | number
          }
        }
      }
      StorageLocation: {
        payload: Prisma.$StorageLocationPayload<ExtArgs>
        fields: Prisma.StorageLocationFieldRefs
        operations: {
          findUnique: {
            args: Prisma.StorageLocationFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.StorageLocationFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>
          }
          findFirst: {
            args: Prisma.StorageLocationFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.StorageLocationFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>
          }
          findMany: {
            args: Prisma.StorageLocationFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>[]
          }
          create: {
            args: Prisma.StorageLocationCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>
          }
          createMany: {
            args: Prisma.StorageLocationCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.StorageLocationCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>[]
          }
          delete: {
            args: Prisma.StorageLocationDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>
          }
          update: {
            args: Prisma.StorageLocationUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>
          }
          deleteMany: {
            args: Prisma.StorageLocationDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.StorageLocationUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.StorageLocationUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StorageLocationPayload>
          }
          aggregate: {
            args: Prisma.StorageLocationAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateStorageLocation>
          }
          groupBy: {
            args: Prisma.StorageLocationGroupByArgs<ExtArgs>
            result: $Utils.Optional<StorageLocationGroupByOutputType>[]
          }
          count: {
            args: Prisma.StorageLocationCountArgs<ExtArgs>
            result: $Utils.Optional<StorageLocationCountAggregateOutputType> | number
          }
        }
      }
      StockTransfer: {
        payload: Prisma.$StockTransferPayload<ExtArgs>
        fields: Prisma.StockTransferFieldRefs
        operations: {
          findUnique: {
            args: Prisma.StockTransferFindUniqueArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload> | null
          }
          findUniqueOrThrow: {
            args: Prisma.StockTransferFindUniqueOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>
          }
          findFirst: {
            args: Prisma.StockTransferFindFirstArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload> | null
          }
          findFirstOrThrow: {
            args: Prisma.StockTransferFindFirstOrThrowArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>
          }
          findMany: {
            args: Prisma.StockTransferFindManyArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>[]
          }
          create: {
            args: Prisma.StockTransferCreateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>
          }
          createMany: {
            args: Prisma.StockTransferCreateManyArgs<ExtArgs>
            result: BatchPayload
          }
          createManyAndReturn: {
            args: Prisma.StockTransferCreateManyAndReturnArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>[]
          }
          delete: {
            args: Prisma.StockTransferDeleteArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>
          }
          update: {
            args: Prisma.StockTransferUpdateArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>
          }
          deleteMany: {
            args: Prisma.StockTransferDeleteManyArgs<ExtArgs>
            result: BatchPayload
          }
          updateMany: {
            args: Prisma.StockTransferUpdateManyArgs<ExtArgs>
            result: BatchPayload
          }
          upsert: {
            args: Prisma.StockTransferUpsertArgs<ExtArgs>
            result: $Utils.PayloadToResult<Prisma.$StockTransferPayload>
          }
          aggregate: {
            args: Prisma.StockTransferAggregateArgs<ExtArgs>
            result: $Utils.Optional<AggregateStockTransfer>
          }
          groupBy: {
            args: Prisma.StockTransferGroupByArgs<ExtArgs>
            result: $Utils.Optional<StockTransferGroupByOutputType>[]
          }
          count: {
            args: Prisma.StockTransferCountArgs<ExtArgs>
            result: $Utils.Optional<StockTransferCountAggregateOutputType> | number
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
   * Count Type InventoryItemCountOutputType
   */

  export type InventoryItemCountOutputType = {
    movements: number
    alerts: number
  }

  export type InventoryItemCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    movements?: boolean | InventoryItemCountOutputTypeCountMovementsArgs
    alerts?: boolean | InventoryItemCountOutputTypeCountAlertsArgs
  }

  // Custom InputTypes
  /**
   * InventoryItemCountOutputType without action
   */
  export type InventoryItemCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItemCountOutputType
     */
    select?: InventoryItemCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * InventoryItemCountOutputType without action
   */
  export type InventoryItemCountOutputTypeCountMovementsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: InventoryMovementWhereInput
  }

  /**
   * InventoryItemCountOutputType without action
   */
  export type InventoryItemCountOutputTypeCountAlertsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: InventoryAlertWhereInput
  }


  /**
   * Count Type WarehouseCountOutputType
   */

  export type WarehouseCountOutputType = {
    zones: number
    transfersFrom: number
    transfersTo: number
  }

  export type WarehouseCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    zones?: boolean | WarehouseCountOutputTypeCountZonesArgs
    transfersFrom?: boolean | WarehouseCountOutputTypeCountTransfersFromArgs
    transfersTo?: boolean | WarehouseCountOutputTypeCountTransfersToArgs
  }

  // Custom InputTypes
  /**
   * WarehouseCountOutputType without action
   */
  export type WarehouseCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the WarehouseCountOutputType
     */
    select?: WarehouseCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * WarehouseCountOutputType without action
   */
  export type WarehouseCountOutputTypeCountZonesArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: ZoneWhereInput
  }

  /**
   * WarehouseCountOutputType without action
   */
  export type WarehouseCountOutputTypeCountTransfersFromArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: StockTransferWhereInput
  }

  /**
   * WarehouseCountOutputType without action
   */
  export type WarehouseCountOutputTypeCountTransfersToArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: StockTransferWhereInput
  }


  /**
   * Count Type ZoneCountOutputType
   */

  export type ZoneCountOutputType = {
    locations: number
  }

  export type ZoneCountOutputTypeSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    locations?: boolean | ZoneCountOutputTypeCountLocationsArgs
  }

  // Custom InputTypes
  /**
   * ZoneCountOutputType without action
   */
  export type ZoneCountOutputTypeDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the ZoneCountOutputType
     */
    select?: ZoneCountOutputTypeSelect<ExtArgs> | null
  }

  /**
   * ZoneCountOutputType without action
   */
  export type ZoneCountOutputTypeCountLocationsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: StorageLocationWhereInput
  }


  /**
   * Models
   */

  /**
   * Model InventoryItem
   */

  export type AggregateInventoryItem = {
    _count: InventoryItemCountAggregateOutputType | null
    _avg: InventoryItemAvgAggregateOutputType | null
    _sum: InventoryItemSumAggregateOutputType | null
    _min: InventoryItemMinAggregateOutputType | null
    _max: InventoryItemMaxAggregateOutputType | null
  }

  export type InventoryItemAvgAggregateOutputType = {
    quantity: number | null
    reorderLevel: number | null
    reorderPoint: number | null
    maxStock: number | null
    unitCost: number | null
    sellingPrice: number | null
    minTemperature: number | null
    maxTemperature: number | null
    minHumidity: number | null
    maxHumidity: number | null
  }

  export type InventoryItemSumAggregateOutputType = {
    quantity: number | null
    reorderLevel: number | null
    reorderPoint: number | null
    maxStock: number | null
    unitCost: number | null
    sellingPrice: number | null
    minTemperature: number | null
    maxTemperature: number | null
    minHumidity: number | null
    maxHumidity: number | null
  }

  export type InventoryItemMinAggregateOutputType = {
    id: string | null
    tenantId: string | null
    name: string | null
    nameAr: string | null
    sku: string | null
    category: $Enums.ItemCategory | null
    description: string | null
    descriptionAr: string | null
    quantity: number | null
    unit: string | null
    reorderLevel: number | null
    reorderPoint: number | null
    maxStock: number | null
    unitCost: number | null
    sellingPrice: number | null
    location: string | null
    batchNumber: string | null
    expiryDate: Date | null
    minTemperature: number | null
    maxTemperature: number | null
    minHumidity: number | null
    maxHumidity: number | null
    supplier: string | null
    barcode: string | null
    imageUrl: string | null
    notes: string | null
    createdAt: Date | null
    updatedAt: Date | null
    lastRestocked: Date | null
  }

  export type InventoryItemMaxAggregateOutputType = {
    id: string | null
    tenantId: string | null
    name: string | null
    nameAr: string | null
    sku: string | null
    category: $Enums.ItemCategory | null
    description: string | null
    descriptionAr: string | null
    quantity: number | null
    unit: string | null
    reorderLevel: number | null
    reorderPoint: number | null
    maxStock: number | null
    unitCost: number | null
    sellingPrice: number | null
    location: string | null
    batchNumber: string | null
    expiryDate: Date | null
    minTemperature: number | null
    maxTemperature: number | null
    minHumidity: number | null
    maxHumidity: number | null
    supplier: string | null
    barcode: string | null
    imageUrl: string | null
    notes: string | null
    createdAt: Date | null
    updatedAt: Date | null
    lastRestocked: Date | null
  }

  export type InventoryItemCountAggregateOutputType = {
    id: number
    tenantId: number
    name: number
    nameAr: number
    sku: number
    category: number
    description: number
    descriptionAr: number
    quantity: number
    unit: number
    reorderLevel: number
    reorderPoint: number
    maxStock: number
    unitCost: number
    sellingPrice: number
    location: number
    batchNumber: number
    expiryDate: number
    minTemperature: number
    maxTemperature: number
    minHumidity: number
    maxHumidity: number
    supplier: number
    barcode: number
    imageUrl: number
    notes: number
    createdAt: number
    updatedAt: number
    lastRestocked: number
    _all: number
  }


  export type InventoryItemAvgAggregateInputType = {
    quantity?: true
    reorderLevel?: true
    reorderPoint?: true
    maxStock?: true
    unitCost?: true
    sellingPrice?: true
    minTemperature?: true
    maxTemperature?: true
    minHumidity?: true
    maxHumidity?: true
  }

  export type InventoryItemSumAggregateInputType = {
    quantity?: true
    reorderLevel?: true
    reorderPoint?: true
    maxStock?: true
    unitCost?: true
    sellingPrice?: true
    minTemperature?: true
    maxTemperature?: true
    minHumidity?: true
    maxHumidity?: true
  }

  export type InventoryItemMinAggregateInputType = {
    id?: true
    tenantId?: true
    name?: true
    nameAr?: true
    sku?: true
    category?: true
    description?: true
    descriptionAr?: true
    quantity?: true
    unit?: true
    reorderLevel?: true
    reorderPoint?: true
    maxStock?: true
    unitCost?: true
    sellingPrice?: true
    location?: true
    batchNumber?: true
    expiryDate?: true
    minTemperature?: true
    maxTemperature?: true
    minHumidity?: true
    maxHumidity?: true
    supplier?: true
    barcode?: true
    imageUrl?: true
    notes?: true
    createdAt?: true
    updatedAt?: true
    lastRestocked?: true
  }

  export type InventoryItemMaxAggregateInputType = {
    id?: true
    tenantId?: true
    name?: true
    nameAr?: true
    sku?: true
    category?: true
    description?: true
    descriptionAr?: true
    quantity?: true
    unit?: true
    reorderLevel?: true
    reorderPoint?: true
    maxStock?: true
    unitCost?: true
    sellingPrice?: true
    location?: true
    batchNumber?: true
    expiryDate?: true
    minTemperature?: true
    maxTemperature?: true
    minHumidity?: true
    maxHumidity?: true
    supplier?: true
    barcode?: true
    imageUrl?: true
    notes?: true
    createdAt?: true
    updatedAt?: true
    lastRestocked?: true
  }

  export type InventoryItemCountAggregateInputType = {
    id?: true
    tenantId?: true
    name?: true
    nameAr?: true
    sku?: true
    category?: true
    description?: true
    descriptionAr?: true
    quantity?: true
    unit?: true
    reorderLevel?: true
    reorderPoint?: true
    maxStock?: true
    unitCost?: true
    sellingPrice?: true
    location?: true
    batchNumber?: true
    expiryDate?: true
    minTemperature?: true
    maxTemperature?: true
    minHumidity?: true
    maxHumidity?: true
    supplier?: true
    barcode?: true
    imageUrl?: true
    notes?: true
    createdAt?: true
    updatedAt?: true
    lastRestocked?: true
    _all?: true
  }

  export type InventoryItemAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which InventoryItem to aggregate.
     */
    where?: InventoryItemWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryItems to fetch.
     */
    orderBy?: InventoryItemOrderByWithRelationInput | InventoryItemOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: InventoryItemWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryItems from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryItems.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned InventoryItems
    **/
    _count?: true | InventoryItemCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: InventoryItemAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: InventoryItemSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: InventoryItemMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: InventoryItemMaxAggregateInputType
  }

  export type GetInventoryItemAggregateType<T extends InventoryItemAggregateArgs> = {
        [P in keyof T & keyof AggregateInventoryItem]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateInventoryItem[P]>
      : GetScalarType<T[P], AggregateInventoryItem[P]>
  }




  export type InventoryItemGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: InventoryItemWhereInput
    orderBy?: InventoryItemOrderByWithAggregationInput | InventoryItemOrderByWithAggregationInput[]
    by: InventoryItemScalarFieldEnum[] | InventoryItemScalarFieldEnum
    having?: InventoryItemScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: InventoryItemCountAggregateInputType | true
    _avg?: InventoryItemAvgAggregateInputType
    _sum?: InventoryItemSumAggregateInputType
    _min?: InventoryItemMinAggregateInputType
    _max?: InventoryItemMaxAggregateInputType
  }

  export type InventoryItemGroupByOutputType = {
    id: string
    tenantId: string
    name: string
    nameAr: string
    sku: string | null
    category: $Enums.ItemCategory
    description: string | null
    descriptionAr: string | null
    quantity: number
    unit: string
    reorderLevel: number
    reorderPoint: number | null
    maxStock: number | null
    unitCost: number | null
    sellingPrice: number | null
    location: string | null
    batchNumber: string | null
    expiryDate: Date | null
    minTemperature: number | null
    maxTemperature: number | null
    minHumidity: number | null
    maxHumidity: number | null
    supplier: string | null
    barcode: string | null
    imageUrl: string | null
    notes: string | null
    createdAt: Date
    updatedAt: Date
    lastRestocked: Date | null
    _count: InventoryItemCountAggregateOutputType | null
    _avg: InventoryItemAvgAggregateOutputType | null
    _sum: InventoryItemSumAggregateOutputType | null
    _min: InventoryItemMinAggregateOutputType | null
    _max: InventoryItemMaxAggregateOutputType | null
  }

  type GetInventoryItemGroupByPayload<T extends InventoryItemGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<InventoryItemGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof InventoryItemGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], InventoryItemGroupByOutputType[P]>
            : GetScalarType<T[P], InventoryItemGroupByOutputType[P]>
        }
      >
    >


  export type InventoryItemSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    name?: boolean
    nameAr?: boolean
    sku?: boolean
    category?: boolean
    description?: boolean
    descriptionAr?: boolean
    quantity?: boolean
    unit?: boolean
    reorderLevel?: boolean
    reorderPoint?: boolean
    maxStock?: boolean
    unitCost?: boolean
    sellingPrice?: boolean
    location?: boolean
    batchNumber?: boolean
    expiryDate?: boolean
    minTemperature?: boolean
    maxTemperature?: boolean
    minHumidity?: boolean
    maxHumidity?: boolean
    supplier?: boolean
    barcode?: boolean
    imageUrl?: boolean
    notes?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    lastRestocked?: boolean
    movements?: boolean | InventoryItem$movementsArgs<ExtArgs>
    alerts?: boolean | InventoryItem$alertsArgs<ExtArgs>
    _count?: boolean | InventoryItemCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["inventoryItem"]>

  export type InventoryItemSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    name?: boolean
    nameAr?: boolean
    sku?: boolean
    category?: boolean
    description?: boolean
    descriptionAr?: boolean
    quantity?: boolean
    unit?: boolean
    reorderLevel?: boolean
    reorderPoint?: boolean
    maxStock?: boolean
    unitCost?: boolean
    sellingPrice?: boolean
    location?: boolean
    batchNumber?: boolean
    expiryDate?: boolean
    minTemperature?: boolean
    maxTemperature?: boolean
    minHumidity?: boolean
    maxHumidity?: boolean
    supplier?: boolean
    barcode?: boolean
    imageUrl?: boolean
    notes?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    lastRestocked?: boolean
  }, ExtArgs["result"]["inventoryItem"]>

  export type InventoryItemSelectScalar = {
    id?: boolean
    tenantId?: boolean
    name?: boolean
    nameAr?: boolean
    sku?: boolean
    category?: boolean
    description?: boolean
    descriptionAr?: boolean
    quantity?: boolean
    unit?: boolean
    reorderLevel?: boolean
    reorderPoint?: boolean
    maxStock?: boolean
    unitCost?: boolean
    sellingPrice?: boolean
    location?: boolean
    batchNumber?: boolean
    expiryDate?: boolean
    minTemperature?: boolean
    maxTemperature?: boolean
    minHumidity?: boolean
    maxHumidity?: boolean
    supplier?: boolean
    barcode?: boolean
    imageUrl?: boolean
    notes?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    lastRestocked?: boolean
  }

  export type InventoryItemInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    movements?: boolean | InventoryItem$movementsArgs<ExtArgs>
    alerts?: boolean | InventoryItem$alertsArgs<ExtArgs>
    _count?: boolean | InventoryItemCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type InventoryItemIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {}

  export type $InventoryItemPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "InventoryItem"
    objects: {
      movements: Prisma.$InventoryMovementPayload<ExtArgs>[]
      alerts: Prisma.$InventoryAlertPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      tenantId: string
      name: string
      nameAr: string
      sku: string | null
      category: $Enums.ItemCategory
      description: string | null
      descriptionAr: string | null
      quantity: number
      unit: string
      reorderLevel: number
      reorderPoint: number | null
      maxStock: number | null
      unitCost: number | null
      sellingPrice: number | null
      location: string | null
      batchNumber: string | null
      expiryDate: Date | null
      minTemperature: number | null
      maxTemperature: number | null
      minHumidity: number | null
      maxHumidity: number | null
      supplier: string | null
      barcode: string | null
      imageUrl: string | null
      notes: string | null
      createdAt: Date
      updatedAt: Date
      lastRestocked: Date | null
    }, ExtArgs["result"]["inventoryItem"]>
    composites: {}
  }

  type InventoryItemGetPayload<S extends boolean | null | undefined | InventoryItemDefaultArgs> = $Result.GetResult<Prisma.$InventoryItemPayload, S>

  type InventoryItemCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<InventoryItemFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: InventoryItemCountAggregateInputType | true
    }

  export interface InventoryItemDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['InventoryItem'], meta: { name: 'InventoryItem' } }
    /**
     * Find zero or one InventoryItem that matches the filter.
     * @param {InventoryItemFindUniqueArgs} args - Arguments to find a InventoryItem
     * @example
     * // Get one InventoryItem
     * const inventoryItem = await prisma.inventoryItem.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends InventoryItemFindUniqueArgs>(args: SelectSubset<T, InventoryItemFindUniqueArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one InventoryItem that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {InventoryItemFindUniqueOrThrowArgs} args - Arguments to find a InventoryItem
     * @example
     * // Get one InventoryItem
     * const inventoryItem = await prisma.inventoryItem.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends InventoryItemFindUniqueOrThrowArgs>(args: SelectSubset<T, InventoryItemFindUniqueOrThrowArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first InventoryItem that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemFindFirstArgs} args - Arguments to find a InventoryItem
     * @example
     * // Get one InventoryItem
     * const inventoryItem = await prisma.inventoryItem.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends InventoryItemFindFirstArgs>(args?: SelectSubset<T, InventoryItemFindFirstArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first InventoryItem that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemFindFirstOrThrowArgs} args - Arguments to find a InventoryItem
     * @example
     * // Get one InventoryItem
     * const inventoryItem = await prisma.inventoryItem.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends InventoryItemFindFirstOrThrowArgs>(args?: SelectSubset<T, InventoryItemFindFirstOrThrowArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more InventoryItems that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all InventoryItems
     * const inventoryItems = await prisma.inventoryItem.findMany()
     * 
     * // Get first 10 InventoryItems
     * const inventoryItems = await prisma.inventoryItem.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const inventoryItemWithIdOnly = await prisma.inventoryItem.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends InventoryItemFindManyArgs>(args?: SelectSubset<T, InventoryItemFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a InventoryItem.
     * @param {InventoryItemCreateArgs} args - Arguments to create a InventoryItem.
     * @example
     * // Create one InventoryItem
     * const InventoryItem = await prisma.inventoryItem.create({
     *   data: {
     *     // ... data to create a InventoryItem
     *   }
     * })
     * 
     */
    create<T extends InventoryItemCreateArgs>(args: SelectSubset<T, InventoryItemCreateArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many InventoryItems.
     * @param {InventoryItemCreateManyArgs} args - Arguments to create many InventoryItems.
     * @example
     * // Create many InventoryItems
     * const inventoryItem = await prisma.inventoryItem.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends InventoryItemCreateManyArgs>(args?: SelectSubset<T, InventoryItemCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many InventoryItems and returns the data saved in the database.
     * @param {InventoryItemCreateManyAndReturnArgs} args - Arguments to create many InventoryItems.
     * @example
     * // Create many InventoryItems
     * const inventoryItem = await prisma.inventoryItem.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many InventoryItems and only return the `id`
     * const inventoryItemWithIdOnly = await prisma.inventoryItem.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends InventoryItemCreateManyAndReturnArgs>(args?: SelectSubset<T, InventoryItemCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a InventoryItem.
     * @param {InventoryItemDeleteArgs} args - Arguments to delete one InventoryItem.
     * @example
     * // Delete one InventoryItem
     * const InventoryItem = await prisma.inventoryItem.delete({
     *   where: {
     *     // ... filter to delete one InventoryItem
     *   }
     * })
     * 
     */
    delete<T extends InventoryItemDeleteArgs>(args: SelectSubset<T, InventoryItemDeleteArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one InventoryItem.
     * @param {InventoryItemUpdateArgs} args - Arguments to update one InventoryItem.
     * @example
     * // Update one InventoryItem
     * const inventoryItem = await prisma.inventoryItem.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends InventoryItemUpdateArgs>(args: SelectSubset<T, InventoryItemUpdateArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more InventoryItems.
     * @param {InventoryItemDeleteManyArgs} args - Arguments to filter InventoryItems to delete.
     * @example
     * // Delete a few InventoryItems
     * const { count } = await prisma.inventoryItem.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends InventoryItemDeleteManyArgs>(args?: SelectSubset<T, InventoryItemDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more InventoryItems.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many InventoryItems
     * const inventoryItem = await prisma.inventoryItem.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends InventoryItemUpdateManyArgs>(args: SelectSubset<T, InventoryItemUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one InventoryItem.
     * @param {InventoryItemUpsertArgs} args - Arguments to update or create a InventoryItem.
     * @example
     * // Update or create a InventoryItem
     * const inventoryItem = await prisma.inventoryItem.upsert({
     *   create: {
     *     // ... data to create a InventoryItem
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the InventoryItem we want to update
     *   }
     * })
     */
    upsert<T extends InventoryItemUpsertArgs>(args: SelectSubset<T, InventoryItemUpsertArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of InventoryItems.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemCountArgs} args - Arguments to filter InventoryItems to count.
     * @example
     * // Count the number of InventoryItems
     * const count = await prisma.inventoryItem.count({
     *   where: {
     *     // ... the filter for the InventoryItems we want to count
     *   }
     * })
    **/
    count<T extends InventoryItemCountArgs>(
      args?: Subset<T, InventoryItemCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], InventoryItemCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a InventoryItem.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends InventoryItemAggregateArgs>(args: Subset<T, InventoryItemAggregateArgs>): Prisma.PrismaPromise<GetInventoryItemAggregateType<T>>

    /**
     * Group by InventoryItem.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryItemGroupByArgs} args - Group by arguments.
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
      T extends InventoryItemGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: InventoryItemGroupByArgs['orderBy'] }
        : { orderBy?: InventoryItemGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, InventoryItemGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetInventoryItemGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the InventoryItem model
   */
  readonly fields: InventoryItemFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for InventoryItem.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__InventoryItemClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    movements<T extends InventoryItem$movementsArgs<ExtArgs> = {}>(args?: Subset<T, InventoryItem$movementsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "findMany"> | Null>
    alerts<T extends InventoryItem$alertsArgs<ExtArgs> = {}>(args?: Subset<T, InventoryItem$alertsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "findMany"> | Null>
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
   * Fields of the InventoryItem model
   */ 
  interface InventoryItemFieldRefs {
    readonly id: FieldRef<"InventoryItem", 'String'>
    readonly tenantId: FieldRef<"InventoryItem", 'String'>
    readonly name: FieldRef<"InventoryItem", 'String'>
    readonly nameAr: FieldRef<"InventoryItem", 'String'>
    readonly sku: FieldRef<"InventoryItem", 'String'>
    readonly category: FieldRef<"InventoryItem", 'ItemCategory'>
    readonly description: FieldRef<"InventoryItem", 'String'>
    readonly descriptionAr: FieldRef<"InventoryItem", 'String'>
    readonly quantity: FieldRef<"InventoryItem", 'Float'>
    readonly unit: FieldRef<"InventoryItem", 'String'>
    readonly reorderLevel: FieldRef<"InventoryItem", 'Float'>
    readonly reorderPoint: FieldRef<"InventoryItem", 'Float'>
    readonly maxStock: FieldRef<"InventoryItem", 'Float'>
    readonly unitCost: FieldRef<"InventoryItem", 'Float'>
    readonly sellingPrice: FieldRef<"InventoryItem", 'Float'>
    readonly location: FieldRef<"InventoryItem", 'String'>
    readonly batchNumber: FieldRef<"InventoryItem", 'String'>
    readonly expiryDate: FieldRef<"InventoryItem", 'DateTime'>
    readonly minTemperature: FieldRef<"InventoryItem", 'Float'>
    readonly maxTemperature: FieldRef<"InventoryItem", 'Float'>
    readonly minHumidity: FieldRef<"InventoryItem", 'Float'>
    readonly maxHumidity: FieldRef<"InventoryItem", 'Float'>
    readonly supplier: FieldRef<"InventoryItem", 'String'>
    readonly barcode: FieldRef<"InventoryItem", 'String'>
    readonly imageUrl: FieldRef<"InventoryItem", 'String'>
    readonly notes: FieldRef<"InventoryItem", 'String'>
    readonly createdAt: FieldRef<"InventoryItem", 'DateTime'>
    readonly updatedAt: FieldRef<"InventoryItem", 'DateTime'>
    readonly lastRestocked: FieldRef<"InventoryItem", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * InventoryItem findUnique
   */
  export type InventoryItemFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * Filter, which InventoryItem to fetch.
     */
    where: InventoryItemWhereUniqueInput
  }

  /**
   * InventoryItem findUniqueOrThrow
   */
  export type InventoryItemFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * Filter, which InventoryItem to fetch.
     */
    where: InventoryItemWhereUniqueInput
  }

  /**
   * InventoryItem findFirst
   */
  export type InventoryItemFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * Filter, which InventoryItem to fetch.
     */
    where?: InventoryItemWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryItems to fetch.
     */
    orderBy?: InventoryItemOrderByWithRelationInput | InventoryItemOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for InventoryItems.
     */
    cursor?: InventoryItemWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryItems from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryItems.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of InventoryItems.
     */
    distinct?: InventoryItemScalarFieldEnum | InventoryItemScalarFieldEnum[]
  }

  /**
   * InventoryItem findFirstOrThrow
   */
  export type InventoryItemFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * Filter, which InventoryItem to fetch.
     */
    where?: InventoryItemWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryItems to fetch.
     */
    orderBy?: InventoryItemOrderByWithRelationInput | InventoryItemOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for InventoryItems.
     */
    cursor?: InventoryItemWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryItems from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryItems.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of InventoryItems.
     */
    distinct?: InventoryItemScalarFieldEnum | InventoryItemScalarFieldEnum[]
  }

  /**
   * InventoryItem findMany
   */
  export type InventoryItemFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * Filter, which InventoryItems to fetch.
     */
    where?: InventoryItemWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryItems to fetch.
     */
    orderBy?: InventoryItemOrderByWithRelationInput | InventoryItemOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing InventoryItems.
     */
    cursor?: InventoryItemWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryItems from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryItems.
     */
    skip?: number
    distinct?: InventoryItemScalarFieldEnum | InventoryItemScalarFieldEnum[]
  }

  /**
   * InventoryItem create
   */
  export type InventoryItemCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * The data needed to create a InventoryItem.
     */
    data: XOR<InventoryItemCreateInput, InventoryItemUncheckedCreateInput>
  }

  /**
   * InventoryItem createMany
   */
  export type InventoryItemCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many InventoryItems.
     */
    data: InventoryItemCreateManyInput | InventoryItemCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * InventoryItem createManyAndReturn
   */
  export type InventoryItemCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many InventoryItems.
     */
    data: InventoryItemCreateManyInput | InventoryItemCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * InventoryItem update
   */
  export type InventoryItemUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * The data needed to update a InventoryItem.
     */
    data: XOR<InventoryItemUpdateInput, InventoryItemUncheckedUpdateInput>
    /**
     * Choose, which InventoryItem to update.
     */
    where: InventoryItemWhereUniqueInput
  }

  /**
   * InventoryItem updateMany
   */
  export type InventoryItemUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update InventoryItems.
     */
    data: XOR<InventoryItemUpdateManyMutationInput, InventoryItemUncheckedUpdateManyInput>
    /**
     * Filter which InventoryItems to update
     */
    where?: InventoryItemWhereInput
  }

  /**
   * InventoryItem upsert
   */
  export type InventoryItemUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * The filter to search for the InventoryItem to update in case it exists.
     */
    where: InventoryItemWhereUniqueInput
    /**
     * In case the InventoryItem found by the `where` argument doesn't exist, create a new InventoryItem with this data.
     */
    create: XOR<InventoryItemCreateInput, InventoryItemUncheckedCreateInput>
    /**
     * In case the InventoryItem was found with the provided `where` argument, update it with this data.
     */
    update: XOR<InventoryItemUpdateInput, InventoryItemUncheckedUpdateInput>
  }

  /**
   * InventoryItem delete
   */
  export type InventoryItemDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
    /**
     * Filter which InventoryItem to delete.
     */
    where: InventoryItemWhereUniqueInput
  }

  /**
   * InventoryItem deleteMany
   */
  export type InventoryItemDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which InventoryItems to delete
     */
    where?: InventoryItemWhereInput
  }

  /**
   * InventoryItem.movements
   */
  export type InventoryItem$movementsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    where?: InventoryMovementWhereInput
    orderBy?: InventoryMovementOrderByWithRelationInput | InventoryMovementOrderByWithRelationInput[]
    cursor?: InventoryMovementWhereUniqueInput
    take?: number
    skip?: number
    distinct?: InventoryMovementScalarFieldEnum | InventoryMovementScalarFieldEnum[]
  }

  /**
   * InventoryItem.alerts
   */
  export type InventoryItem$alertsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    where?: InventoryAlertWhereInput
    orderBy?: InventoryAlertOrderByWithRelationInput | InventoryAlertOrderByWithRelationInput[]
    cursor?: InventoryAlertWhereUniqueInput
    take?: number
    skip?: number
    distinct?: InventoryAlertScalarFieldEnum | InventoryAlertScalarFieldEnum[]
  }

  /**
   * InventoryItem without action
   */
  export type InventoryItemDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryItem
     */
    select?: InventoryItemSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryItemInclude<ExtArgs> | null
  }


  /**
   * Model InventoryMovement
   */

  export type AggregateInventoryMovement = {
    _count: InventoryMovementCountAggregateOutputType | null
    _avg: InventoryMovementAvgAggregateOutputType | null
    _sum: InventoryMovementSumAggregateOutputType | null
    _min: InventoryMovementMinAggregateOutputType | null
    _max: InventoryMovementMaxAggregateOutputType | null
  }

  export type InventoryMovementAvgAggregateOutputType = {
    quantity: number | null
    unitCost: number | null
  }

  export type InventoryMovementSumAggregateOutputType = {
    quantity: number | null
    unitCost: number | null
  }

  export type InventoryMovementMinAggregateOutputType = {
    id: string | null
    itemId: string | null
    tenantId: string | null
    type: $Enums.MovementType | null
    quantity: number | null
    unitCost: number | null
    referenceId: string | null
    referenceType: string | null
    fromLocation: string | null
    toLocation: string | null
    notes: string | null
    notesAr: string | null
    performedBy: string | null
    createdAt: Date | null
  }

  export type InventoryMovementMaxAggregateOutputType = {
    id: string | null
    itemId: string | null
    tenantId: string | null
    type: $Enums.MovementType | null
    quantity: number | null
    unitCost: number | null
    referenceId: string | null
    referenceType: string | null
    fromLocation: string | null
    toLocation: string | null
    notes: string | null
    notesAr: string | null
    performedBy: string | null
    createdAt: Date | null
  }

  export type InventoryMovementCountAggregateOutputType = {
    id: number
    itemId: number
    tenantId: number
    type: number
    quantity: number
    unitCost: number
    referenceId: number
    referenceType: number
    fromLocation: number
    toLocation: number
    notes: number
    notesAr: number
    performedBy: number
    createdAt: number
    _all: number
  }


  export type InventoryMovementAvgAggregateInputType = {
    quantity?: true
    unitCost?: true
  }

  export type InventoryMovementSumAggregateInputType = {
    quantity?: true
    unitCost?: true
  }

  export type InventoryMovementMinAggregateInputType = {
    id?: true
    itemId?: true
    tenantId?: true
    type?: true
    quantity?: true
    unitCost?: true
    referenceId?: true
    referenceType?: true
    fromLocation?: true
    toLocation?: true
    notes?: true
    notesAr?: true
    performedBy?: true
    createdAt?: true
  }

  export type InventoryMovementMaxAggregateInputType = {
    id?: true
    itemId?: true
    tenantId?: true
    type?: true
    quantity?: true
    unitCost?: true
    referenceId?: true
    referenceType?: true
    fromLocation?: true
    toLocation?: true
    notes?: true
    notesAr?: true
    performedBy?: true
    createdAt?: true
  }

  export type InventoryMovementCountAggregateInputType = {
    id?: true
    itemId?: true
    tenantId?: true
    type?: true
    quantity?: true
    unitCost?: true
    referenceId?: true
    referenceType?: true
    fromLocation?: true
    toLocation?: true
    notes?: true
    notesAr?: true
    performedBy?: true
    createdAt?: true
    _all?: true
  }

  export type InventoryMovementAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which InventoryMovement to aggregate.
     */
    where?: InventoryMovementWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryMovements to fetch.
     */
    orderBy?: InventoryMovementOrderByWithRelationInput | InventoryMovementOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: InventoryMovementWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryMovements from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryMovements.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned InventoryMovements
    **/
    _count?: true | InventoryMovementCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: InventoryMovementAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: InventoryMovementSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: InventoryMovementMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: InventoryMovementMaxAggregateInputType
  }

  export type GetInventoryMovementAggregateType<T extends InventoryMovementAggregateArgs> = {
        [P in keyof T & keyof AggregateInventoryMovement]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateInventoryMovement[P]>
      : GetScalarType<T[P], AggregateInventoryMovement[P]>
  }




  export type InventoryMovementGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: InventoryMovementWhereInput
    orderBy?: InventoryMovementOrderByWithAggregationInput | InventoryMovementOrderByWithAggregationInput[]
    by: InventoryMovementScalarFieldEnum[] | InventoryMovementScalarFieldEnum
    having?: InventoryMovementScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: InventoryMovementCountAggregateInputType | true
    _avg?: InventoryMovementAvgAggregateInputType
    _sum?: InventoryMovementSumAggregateInputType
    _min?: InventoryMovementMinAggregateInputType
    _max?: InventoryMovementMaxAggregateInputType
  }

  export type InventoryMovementGroupByOutputType = {
    id: string
    itemId: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost: number | null
    referenceId: string | null
    referenceType: string | null
    fromLocation: string | null
    toLocation: string | null
    notes: string | null
    notesAr: string | null
    performedBy: string
    createdAt: Date
    _count: InventoryMovementCountAggregateOutputType | null
    _avg: InventoryMovementAvgAggregateOutputType | null
    _sum: InventoryMovementSumAggregateOutputType | null
    _min: InventoryMovementMinAggregateOutputType | null
    _max: InventoryMovementMaxAggregateOutputType | null
  }

  type GetInventoryMovementGroupByPayload<T extends InventoryMovementGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<InventoryMovementGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof InventoryMovementGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], InventoryMovementGroupByOutputType[P]>
            : GetScalarType<T[P], InventoryMovementGroupByOutputType[P]>
        }
      >
    >


  export type InventoryMovementSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    itemId?: boolean
    tenantId?: boolean
    type?: boolean
    quantity?: boolean
    unitCost?: boolean
    referenceId?: boolean
    referenceType?: boolean
    fromLocation?: boolean
    toLocation?: boolean
    notes?: boolean
    notesAr?: boolean
    performedBy?: boolean
    createdAt?: boolean
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["inventoryMovement"]>

  export type InventoryMovementSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    itemId?: boolean
    tenantId?: boolean
    type?: boolean
    quantity?: boolean
    unitCost?: boolean
    referenceId?: boolean
    referenceType?: boolean
    fromLocation?: boolean
    toLocation?: boolean
    notes?: boolean
    notesAr?: boolean
    performedBy?: boolean
    createdAt?: boolean
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["inventoryMovement"]>

  export type InventoryMovementSelectScalar = {
    id?: boolean
    itemId?: boolean
    tenantId?: boolean
    type?: boolean
    quantity?: boolean
    unitCost?: boolean
    referenceId?: boolean
    referenceType?: boolean
    fromLocation?: boolean
    toLocation?: boolean
    notes?: boolean
    notesAr?: boolean
    performedBy?: boolean
    createdAt?: boolean
  }

  export type InventoryMovementInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }
  export type InventoryMovementIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }

  export type $InventoryMovementPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "InventoryMovement"
    objects: {
      item: Prisma.$InventoryItemPayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      itemId: string
      tenantId: string
      type: $Enums.MovementType
      quantity: number
      unitCost: number | null
      referenceId: string | null
      referenceType: string | null
      fromLocation: string | null
      toLocation: string | null
      notes: string | null
      notesAr: string | null
      performedBy: string
      createdAt: Date
    }, ExtArgs["result"]["inventoryMovement"]>
    composites: {}
  }

  type InventoryMovementGetPayload<S extends boolean | null | undefined | InventoryMovementDefaultArgs> = $Result.GetResult<Prisma.$InventoryMovementPayload, S>

  type InventoryMovementCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<InventoryMovementFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: InventoryMovementCountAggregateInputType | true
    }

  export interface InventoryMovementDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['InventoryMovement'], meta: { name: 'InventoryMovement' } }
    /**
     * Find zero or one InventoryMovement that matches the filter.
     * @param {InventoryMovementFindUniqueArgs} args - Arguments to find a InventoryMovement
     * @example
     * // Get one InventoryMovement
     * const inventoryMovement = await prisma.inventoryMovement.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends InventoryMovementFindUniqueArgs>(args: SelectSubset<T, InventoryMovementFindUniqueArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one InventoryMovement that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {InventoryMovementFindUniqueOrThrowArgs} args - Arguments to find a InventoryMovement
     * @example
     * // Get one InventoryMovement
     * const inventoryMovement = await prisma.inventoryMovement.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends InventoryMovementFindUniqueOrThrowArgs>(args: SelectSubset<T, InventoryMovementFindUniqueOrThrowArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first InventoryMovement that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementFindFirstArgs} args - Arguments to find a InventoryMovement
     * @example
     * // Get one InventoryMovement
     * const inventoryMovement = await prisma.inventoryMovement.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends InventoryMovementFindFirstArgs>(args?: SelectSubset<T, InventoryMovementFindFirstArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first InventoryMovement that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementFindFirstOrThrowArgs} args - Arguments to find a InventoryMovement
     * @example
     * // Get one InventoryMovement
     * const inventoryMovement = await prisma.inventoryMovement.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends InventoryMovementFindFirstOrThrowArgs>(args?: SelectSubset<T, InventoryMovementFindFirstOrThrowArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more InventoryMovements that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all InventoryMovements
     * const inventoryMovements = await prisma.inventoryMovement.findMany()
     * 
     * // Get first 10 InventoryMovements
     * const inventoryMovements = await prisma.inventoryMovement.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const inventoryMovementWithIdOnly = await prisma.inventoryMovement.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends InventoryMovementFindManyArgs>(args?: SelectSubset<T, InventoryMovementFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a InventoryMovement.
     * @param {InventoryMovementCreateArgs} args - Arguments to create a InventoryMovement.
     * @example
     * // Create one InventoryMovement
     * const InventoryMovement = await prisma.inventoryMovement.create({
     *   data: {
     *     // ... data to create a InventoryMovement
     *   }
     * })
     * 
     */
    create<T extends InventoryMovementCreateArgs>(args: SelectSubset<T, InventoryMovementCreateArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many InventoryMovements.
     * @param {InventoryMovementCreateManyArgs} args - Arguments to create many InventoryMovements.
     * @example
     * // Create many InventoryMovements
     * const inventoryMovement = await prisma.inventoryMovement.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends InventoryMovementCreateManyArgs>(args?: SelectSubset<T, InventoryMovementCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many InventoryMovements and returns the data saved in the database.
     * @param {InventoryMovementCreateManyAndReturnArgs} args - Arguments to create many InventoryMovements.
     * @example
     * // Create many InventoryMovements
     * const inventoryMovement = await prisma.inventoryMovement.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many InventoryMovements and only return the `id`
     * const inventoryMovementWithIdOnly = await prisma.inventoryMovement.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends InventoryMovementCreateManyAndReturnArgs>(args?: SelectSubset<T, InventoryMovementCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a InventoryMovement.
     * @param {InventoryMovementDeleteArgs} args - Arguments to delete one InventoryMovement.
     * @example
     * // Delete one InventoryMovement
     * const InventoryMovement = await prisma.inventoryMovement.delete({
     *   where: {
     *     // ... filter to delete one InventoryMovement
     *   }
     * })
     * 
     */
    delete<T extends InventoryMovementDeleteArgs>(args: SelectSubset<T, InventoryMovementDeleteArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one InventoryMovement.
     * @param {InventoryMovementUpdateArgs} args - Arguments to update one InventoryMovement.
     * @example
     * // Update one InventoryMovement
     * const inventoryMovement = await prisma.inventoryMovement.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends InventoryMovementUpdateArgs>(args: SelectSubset<T, InventoryMovementUpdateArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more InventoryMovements.
     * @param {InventoryMovementDeleteManyArgs} args - Arguments to filter InventoryMovements to delete.
     * @example
     * // Delete a few InventoryMovements
     * const { count } = await prisma.inventoryMovement.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends InventoryMovementDeleteManyArgs>(args?: SelectSubset<T, InventoryMovementDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more InventoryMovements.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many InventoryMovements
     * const inventoryMovement = await prisma.inventoryMovement.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends InventoryMovementUpdateManyArgs>(args: SelectSubset<T, InventoryMovementUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one InventoryMovement.
     * @param {InventoryMovementUpsertArgs} args - Arguments to update or create a InventoryMovement.
     * @example
     * // Update or create a InventoryMovement
     * const inventoryMovement = await prisma.inventoryMovement.upsert({
     *   create: {
     *     // ... data to create a InventoryMovement
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the InventoryMovement we want to update
     *   }
     * })
     */
    upsert<T extends InventoryMovementUpsertArgs>(args: SelectSubset<T, InventoryMovementUpsertArgs<ExtArgs>>): Prisma__InventoryMovementClient<$Result.GetResult<Prisma.$InventoryMovementPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of InventoryMovements.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementCountArgs} args - Arguments to filter InventoryMovements to count.
     * @example
     * // Count the number of InventoryMovements
     * const count = await prisma.inventoryMovement.count({
     *   where: {
     *     // ... the filter for the InventoryMovements we want to count
     *   }
     * })
    **/
    count<T extends InventoryMovementCountArgs>(
      args?: Subset<T, InventoryMovementCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], InventoryMovementCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a InventoryMovement.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends InventoryMovementAggregateArgs>(args: Subset<T, InventoryMovementAggregateArgs>): Prisma.PrismaPromise<GetInventoryMovementAggregateType<T>>

    /**
     * Group by InventoryMovement.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryMovementGroupByArgs} args - Group by arguments.
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
      T extends InventoryMovementGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: InventoryMovementGroupByArgs['orderBy'] }
        : { orderBy?: InventoryMovementGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, InventoryMovementGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetInventoryMovementGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the InventoryMovement model
   */
  readonly fields: InventoryMovementFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for InventoryMovement.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__InventoryMovementClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    item<T extends InventoryItemDefaultArgs<ExtArgs> = {}>(args?: Subset<T, InventoryItemDefaultArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
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
   * Fields of the InventoryMovement model
   */ 
  interface InventoryMovementFieldRefs {
    readonly id: FieldRef<"InventoryMovement", 'String'>
    readonly itemId: FieldRef<"InventoryMovement", 'String'>
    readonly tenantId: FieldRef<"InventoryMovement", 'String'>
    readonly type: FieldRef<"InventoryMovement", 'MovementType'>
    readonly quantity: FieldRef<"InventoryMovement", 'Float'>
    readonly unitCost: FieldRef<"InventoryMovement", 'Float'>
    readonly referenceId: FieldRef<"InventoryMovement", 'String'>
    readonly referenceType: FieldRef<"InventoryMovement", 'String'>
    readonly fromLocation: FieldRef<"InventoryMovement", 'String'>
    readonly toLocation: FieldRef<"InventoryMovement", 'String'>
    readonly notes: FieldRef<"InventoryMovement", 'String'>
    readonly notesAr: FieldRef<"InventoryMovement", 'String'>
    readonly performedBy: FieldRef<"InventoryMovement", 'String'>
    readonly createdAt: FieldRef<"InventoryMovement", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * InventoryMovement findUnique
   */
  export type InventoryMovementFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * Filter, which InventoryMovement to fetch.
     */
    where: InventoryMovementWhereUniqueInput
  }

  /**
   * InventoryMovement findUniqueOrThrow
   */
  export type InventoryMovementFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * Filter, which InventoryMovement to fetch.
     */
    where: InventoryMovementWhereUniqueInput
  }

  /**
   * InventoryMovement findFirst
   */
  export type InventoryMovementFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * Filter, which InventoryMovement to fetch.
     */
    where?: InventoryMovementWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryMovements to fetch.
     */
    orderBy?: InventoryMovementOrderByWithRelationInput | InventoryMovementOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for InventoryMovements.
     */
    cursor?: InventoryMovementWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryMovements from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryMovements.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of InventoryMovements.
     */
    distinct?: InventoryMovementScalarFieldEnum | InventoryMovementScalarFieldEnum[]
  }

  /**
   * InventoryMovement findFirstOrThrow
   */
  export type InventoryMovementFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * Filter, which InventoryMovement to fetch.
     */
    where?: InventoryMovementWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryMovements to fetch.
     */
    orderBy?: InventoryMovementOrderByWithRelationInput | InventoryMovementOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for InventoryMovements.
     */
    cursor?: InventoryMovementWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryMovements from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryMovements.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of InventoryMovements.
     */
    distinct?: InventoryMovementScalarFieldEnum | InventoryMovementScalarFieldEnum[]
  }

  /**
   * InventoryMovement findMany
   */
  export type InventoryMovementFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * Filter, which InventoryMovements to fetch.
     */
    where?: InventoryMovementWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryMovements to fetch.
     */
    orderBy?: InventoryMovementOrderByWithRelationInput | InventoryMovementOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing InventoryMovements.
     */
    cursor?: InventoryMovementWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryMovements from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryMovements.
     */
    skip?: number
    distinct?: InventoryMovementScalarFieldEnum | InventoryMovementScalarFieldEnum[]
  }

  /**
   * InventoryMovement create
   */
  export type InventoryMovementCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * The data needed to create a InventoryMovement.
     */
    data: XOR<InventoryMovementCreateInput, InventoryMovementUncheckedCreateInput>
  }

  /**
   * InventoryMovement createMany
   */
  export type InventoryMovementCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many InventoryMovements.
     */
    data: InventoryMovementCreateManyInput | InventoryMovementCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * InventoryMovement createManyAndReturn
   */
  export type InventoryMovementCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many InventoryMovements.
     */
    data: InventoryMovementCreateManyInput | InventoryMovementCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * InventoryMovement update
   */
  export type InventoryMovementUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * The data needed to update a InventoryMovement.
     */
    data: XOR<InventoryMovementUpdateInput, InventoryMovementUncheckedUpdateInput>
    /**
     * Choose, which InventoryMovement to update.
     */
    where: InventoryMovementWhereUniqueInput
  }

  /**
   * InventoryMovement updateMany
   */
  export type InventoryMovementUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update InventoryMovements.
     */
    data: XOR<InventoryMovementUpdateManyMutationInput, InventoryMovementUncheckedUpdateManyInput>
    /**
     * Filter which InventoryMovements to update
     */
    where?: InventoryMovementWhereInput
  }

  /**
   * InventoryMovement upsert
   */
  export type InventoryMovementUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * The filter to search for the InventoryMovement to update in case it exists.
     */
    where: InventoryMovementWhereUniqueInput
    /**
     * In case the InventoryMovement found by the `where` argument doesn't exist, create a new InventoryMovement with this data.
     */
    create: XOR<InventoryMovementCreateInput, InventoryMovementUncheckedCreateInput>
    /**
     * In case the InventoryMovement was found with the provided `where` argument, update it with this data.
     */
    update: XOR<InventoryMovementUpdateInput, InventoryMovementUncheckedUpdateInput>
  }

  /**
   * InventoryMovement delete
   */
  export type InventoryMovementDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
    /**
     * Filter which InventoryMovement to delete.
     */
    where: InventoryMovementWhereUniqueInput
  }

  /**
   * InventoryMovement deleteMany
   */
  export type InventoryMovementDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which InventoryMovements to delete
     */
    where?: InventoryMovementWhereInput
  }

  /**
   * InventoryMovement without action
   */
  export type InventoryMovementDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryMovement
     */
    select?: InventoryMovementSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryMovementInclude<ExtArgs> | null
  }


  /**
   * Model InventoryAlert
   */

  export type AggregateInventoryAlert = {
    _count: InventoryAlertCountAggregateOutputType | null
    _avg: InventoryAlertAvgAggregateOutputType | null
    _sum: InventoryAlertSumAggregateOutputType | null
    _min: InventoryAlertMinAggregateOutputType | null
    _max: InventoryAlertMaxAggregateOutputType | null
  }

  export type InventoryAlertAvgAggregateOutputType = {
    currentValue: number | null
    thresholdValue: number | null
  }

  export type InventoryAlertSumAggregateOutputType = {
    currentValue: number | null
    thresholdValue: number | null
  }

  export type InventoryAlertMinAggregateOutputType = {
    id: string | null
    alertType: $Enums.AlertType | null
    priority: $Enums.AlertPriority | null
    status: $Enums.AlertStatus | null
    itemId: string | null
    itemName: string | null
    itemNameAr: string | null
    titleEn: string | null
    titleAr: string | null
    messageEn: string | null
    messageAr: string | null
    currentValue: number | null
    thresholdValue: number | null
    recommendedActionEn: string | null
    recommendedActionAr: string | null
    actionUrl: string | null
    createdAt: Date | null
    acknowledgedAt: Date | null
    acknowledgedBy: string | null
    resolvedAt: Date | null
    resolvedBy: string | null
    resolutionNotes: string | null
    snoozeUntil: Date | null
  }

  export type InventoryAlertMaxAggregateOutputType = {
    id: string | null
    alertType: $Enums.AlertType | null
    priority: $Enums.AlertPriority | null
    status: $Enums.AlertStatus | null
    itemId: string | null
    itemName: string | null
    itemNameAr: string | null
    titleEn: string | null
    titleAr: string | null
    messageEn: string | null
    messageAr: string | null
    currentValue: number | null
    thresholdValue: number | null
    recommendedActionEn: string | null
    recommendedActionAr: string | null
    actionUrl: string | null
    createdAt: Date | null
    acknowledgedAt: Date | null
    acknowledgedBy: string | null
    resolvedAt: Date | null
    resolvedBy: string | null
    resolutionNotes: string | null
    snoozeUntil: Date | null
  }

  export type InventoryAlertCountAggregateOutputType = {
    id: number
    alertType: number
    priority: number
    status: number
    itemId: number
    itemName: number
    itemNameAr: number
    titleEn: number
    titleAr: number
    messageEn: number
    messageAr: number
    currentValue: number
    thresholdValue: number
    recommendedActionEn: number
    recommendedActionAr: number
    actionUrl: number
    createdAt: number
    acknowledgedAt: number
    acknowledgedBy: number
    resolvedAt: number
    resolvedBy: number
    resolutionNotes: number
    snoozeUntil: number
    _all: number
  }


  export type InventoryAlertAvgAggregateInputType = {
    currentValue?: true
    thresholdValue?: true
  }

  export type InventoryAlertSumAggregateInputType = {
    currentValue?: true
    thresholdValue?: true
  }

  export type InventoryAlertMinAggregateInputType = {
    id?: true
    alertType?: true
    priority?: true
    status?: true
    itemId?: true
    itemName?: true
    itemNameAr?: true
    titleEn?: true
    titleAr?: true
    messageEn?: true
    messageAr?: true
    currentValue?: true
    thresholdValue?: true
    recommendedActionEn?: true
    recommendedActionAr?: true
    actionUrl?: true
    createdAt?: true
    acknowledgedAt?: true
    acknowledgedBy?: true
    resolvedAt?: true
    resolvedBy?: true
    resolutionNotes?: true
    snoozeUntil?: true
  }

  export type InventoryAlertMaxAggregateInputType = {
    id?: true
    alertType?: true
    priority?: true
    status?: true
    itemId?: true
    itemName?: true
    itemNameAr?: true
    titleEn?: true
    titleAr?: true
    messageEn?: true
    messageAr?: true
    currentValue?: true
    thresholdValue?: true
    recommendedActionEn?: true
    recommendedActionAr?: true
    actionUrl?: true
    createdAt?: true
    acknowledgedAt?: true
    acknowledgedBy?: true
    resolvedAt?: true
    resolvedBy?: true
    resolutionNotes?: true
    snoozeUntil?: true
  }

  export type InventoryAlertCountAggregateInputType = {
    id?: true
    alertType?: true
    priority?: true
    status?: true
    itemId?: true
    itemName?: true
    itemNameAr?: true
    titleEn?: true
    titleAr?: true
    messageEn?: true
    messageAr?: true
    currentValue?: true
    thresholdValue?: true
    recommendedActionEn?: true
    recommendedActionAr?: true
    actionUrl?: true
    createdAt?: true
    acknowledgedAt?: true
    acknowledgedBy?: true
    resolvedAt?: true
    resolvedBy?: true
    resolutionNotes?: true
    snoozeUntil?: true
    _all?: true
  }

  export type InventoryAlertAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which InventoryAlert to aggregate.
     */
    where?: InventoryAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryAlerts to fetch.
     */
    orderBy?: InventoryAlertOrderByWithRelationInput | InventoryAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: InventoryAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned InventoryAlerts
    **/
    _count?: true | InventoryAlertCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: InventoryAlertAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: InventoryAlertSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: InventoryAlertMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: InventoryAlertMaxAggregateInputType
  }

  export type GetInventoryAlertAggregateType<T extends InventoryAlertAggregateArgs> = {
        [P in keyof T & keyof AggregateInventoryAlert]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateInventoryAlert[P]>
      : GetScalarType<T[P], AggregateInventoryAlert[P]>
  }




  export type InventoryAlertGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: InventoryAlertWhereInput
    orderBy?: InventoryAlertOrderByWithAggregationInput | InventoryAlertOrderByWithAggregationInput[]
    by: InventoryAlertScalarFieldEnum[] | InventoryAlertScalarFieldEnum
    having?: InventoryAlertScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: InventoryAlertCountAggregateInputType | true
    _avg?: InventoryAlertAvgAggregateInputType
    _sum?: InventoryAlertSumAggregateInputType
    _min?: InventoryAlertMinAggregateInputType
    _max?: InventoryAlertMaxAggregateInputType
  }

  export type InventoryAlertGroupByOutputType = {
    id: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status: $Enums.AlertStatus
    itemId: string
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl: string | null
    createdAt: Date
    acknowledgedAt: Date | null
    acknowledgedBy: string | null
    resolvedAt: Date | null
    resolvedBy: string | null
    resolutionNotes: string | null
    snoozeUntil: Date | null
    _count: InventoryAlertCountAggregateOutputType | null
    _avg: InventoryAlertAvgAggregateOutputType | null
    _sum: InventoryAlertSumAggregateOutputType | null
    _min: InventoryAlertMinAggregateOutputType | null
    _max: InventoryAlertMaxAggregateOutputType | null
  }

  type GetInventoryAlertGroupByPayload<T extends InventoryAlertGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<InventoryAlertGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof InventoryAlertGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], InventoryAlertGroupByOutputType[P]>
            : GetScalarType<T[P], InventoryAlertGroupByOutputType[P]>
        }
      >
    >


  export type InventoryAlertSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    alertType?: boolean
    priority?: boolean
    status?: boolean
    itemId?: boolean
    itemName?: boolean
    itemNameAr?: boolean
    titleEn?: boolean
    titleAr?: boolean
    messageEn?: boolean
    messageAr?: boolean
    currentValue?: boolean
    thresholdValue?: boolean
    recommendedActionEn?: boolean
    recommendedActionAr?: boolean
    actionUrl?: boolean
    createdAt?: boolean
    acknowledgedAt?: boolean
    acknowledgedBy?: boolean
    resolvedAt?: boolean
    resolvedBy?: boolean
    resolutionNotes?: boolean
    snoozeUntil?: boolean
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["inventoryAlert"]>

  export type InventoryAlertSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    alertType?: boolean
    priority?: boolean
    status?: boolean
    itemId?: boolean
    itemName?: boolean
    itemNameAr?: boolean
    titleEn?: boolean
    titleAr?: boolean
    messageEn?: boolean
    messageAr?: boolean
    currentValue?: boolean
    thresholdValue?: boolean
    recommendedActionEn?: boolean
    recommendedActionAr?: boolean
    actionUrl?: boolean
    createdAt?: boolean
    acknowledgedAt?: boolean
    acknowledgedBy?: boolean
    resolvedAt?: boolean
    resolvedBy?: boolean
    resolutionNotes?: boolean
    snoozeUntil?: boolean
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["inventoryAlert"]>

  export type InventoryAlertSelectScalar = {
    id?: boolean
    alertType?: boolean
    priority?: boolean
    status?: boolean
    itemId?: boolean
    itemName?: boolean
    itemNameAr?: boolean
    titleEn?: boolean
    titleAr?: boolean
    messageEn?: boolean
    messageAr?: boolean
    currentValue?: boolean
    thresholdValue?: boolean
    recommendedActionEn?: boolean
    recommendedActionAr?: boolean
    actionUrl?: boolean
    createdAt?: boolean
    acknowledgedAt?: boolean
    acknowledgedBy?: boolean
    resolvedAt?: boolean
    resolvedBy?: boolean
    resolutionNotes?: boolean
    snoozeUntil?: boolean
  }

  export type InventoryAlertInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }
  export type InventoryAlertIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    item?: boolean | InventoryItemDefaultArgs<ExtArgs>
  }

  export type $InventoryAlertPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "InventoryAlert"
    objects: {
      item: Prisma.$InventoryItemPayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      alertType: $Enums.AlertType
      priority: $Enums.AlertPriority
      status: $Enums.AlertStatus
      itemId: string
      itemName: string
      itemNameAr: string
      titleEn: string
      titleAr: string
      messageEn: string
      messageAr: string
      currentValue: number
      thresholdValue: number
      recommendedActionEn: string
      recommendedActionAr: string
      actionUrl: string | null
      createdAt: Date
      acknowledgedAt: Date | null
      acknowledgedBy: string | null
      resolvedAt: Date | null
      resolvedBy: string | null
      resolutionNotes: string | null
      snoozeUntil: Date | null
    }, ExtArgs["result"]["inventoryAlert"]>
    composites: {}
  }

  type InventoryAlertGetPayload<S extends boolean | null | undefined | InventoryAlertDefaultArgs> = $Result.GetResult<Prisma.$InventoryAlertPayload, S>

  type InventoryAlertCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<InventoryAlertFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: InventoryAlertCountAggregateInputType | true
    }

  export interface InventoryAlertDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['InventoryAlert'], meta: { name: 'InventoryAlert' } }
    /**
     * Find zero or one InventoryAlert that matches the filter.
     * @param {InventoryAlertFindUniqueArgs} args - Arguments to find a InventoryAlert
     * @example
     * // Get one InventoryAlert
     * const inventoryAlert = await prisma.inventoryAlert.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends InventoryAlertFindUniqueArgs>(args: SelectSubset<T, InventoryAlertFindUniqueArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one InventoryAlert that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {InventoryAlertFindUniqueOrThrowArgs} args - Arguments to find a InventoryAlert
     * @example
     * // Get one InventoryAlert
     * const inventoryAlert = await prisma.inventoryAlert.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends InventoryAlertFindUniqueOrThrowArgs>(args: SelectSubset<T, InventoryAlertFindUniqueOrThrowArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first InventoryAlert that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertFindFirstArgs} args - Arguments to find a InventoryAlert
     * @example
     * // Get one InventoryAlert
     * const inventoryAlert = await prisma.inventoryAlert.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends InventoryAlertFindFirstArgs>(args?: SelectSubset<T, InventoryAlertFindFirstArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first InventoryAlert that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertFindFirstOrThrowArgs} args - Arguments to find a InventoryAlert
     * @example
     * // Get one InventoryAlert
     * const inventoryAlert = await prisma.inventoryAlert.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends InventoryAlertFindFirstOrThrowArgs>(args?: SelectSubset<T, InventoryAlertFindFirstOrThrowArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more InventoryAlerts that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all InventoryAlerts
     * const inventoryAlerts = await prisma.inventoryAlert.findMany()
     * 
     * // Get first 10 InventoryAlerts
     * const inventoryAlerts = await prisma.inventoryAlert.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const inventoryAlertWithIdOnly = await prisma.inventoryAlert.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends InventoryAlertFindManyArgs>(args?: SelectSubset<T, InventoryAlertFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a InventoryAlert.
     * @param {InventoryAlertCreateArgs} args - Arguments to create a InventoryAlert.
     * @example
     * // Create one InventoryAlert
     * const InventoryAlert = await prisma.inventoryAlert.create({
     *   data: {
     *     // ... data to create a InventoryAlert
     *   }
     * })
     * 
     */
    create<T extends InventoryAlertCreateArgs>(args: SelectSubset<T, InventoryAlertCreateArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many InventoryAlerts.
     * @param {InventoryAlertCreateManyArgs} args - Arguments to create many InventoryAlerts.
     * @example
     * // Create many InventoryAlerts
     * const inventoryAlert = await prisma.inventoryAlert.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends InventoryAlertCreateManyArgs>(args?: SelectSubset<T, InventoryAlertCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many InventoryAlerts and returns the data saved in the database.
     * @param {InventoryAlertCreateManyAndReturnArgs} args - Arguments to create many InventoryAlerts.
     * @example
     * // Create many InventoryAlerts
     * const inventoryAlert = await prisma.inventoryAlert.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many InventoryAlerts and only return the `id`
     * const inventoryAlertWithIdOnly = await prisma.inventoryAlert.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends InventoryAlertCreateManyAndReturnArgs>(args?: SelectSubset<T, InventoryAlertCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a InventoryAlert.
     * @param {InventoryAlertDeleteArgs} args - Arguments to delete one InventoryAlert.
     * @example
     * // Delete one InventoryAlert
     * const InventoryAlert = await prisma.inventoryAlert.delete({
     *   where: {
     *     // ... filter to delete one InventoryAlert
     *   }
     * })
     * 
     */
    delete<T extends InventoryAlertDeleteArgs>(args: SelectSubset<T, InventoryAlertDeleteArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one InventoryAlert.
     * @param {InventoryAlertUpdateArgs} args - Arguments to update one InventoryAlert.
     * @example
     * // Update one InventoryAlert
     * const inventoryAlert = await prisma.inventoryAlert.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends InventoryAlertUpdateArgs>(args: SelectSubset<T, InventoryAlertUpdateArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more InventoryAlerts.
     * @param {InventoryAlertDeleteManyArgs} args - Arguments to filter InventoryAlerts to delete.
     * @example
     * // Delete a few InventoryAlerts
     * const { count } = await prisma.inventoryAlert.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends InventoryAlertDeleteManyArgs>(args?: SelectSubset<T, InventoryAlertDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more InventoryAlerts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many InventoryAlerts
     * const inventoryAlert = await prisma.inventoryAlert.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends InventoryAlertUpdateManyArgs>(args: SelectSubset<T, InventoryAlertUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one InventoryAlert.
     * @param {InventoryAlertUpsertArgs} args - Arguments to update or create a InventoryAlert.
     * @example
     * // Update or create a InventoryAlert
     * const inventoryAlert = await prisma.inventoryAlert.upsert({
     *   create: {
     *     // ... data to create a InventoryAlert
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the InventoryAlert we want to update
     *   }
     * })
     */
    upsert<T extends InventoryAlertUpsertArgs>(args: SelectSubset<T, InventoryAlertUpsertArgs<ExtArgs>>): Prisma__InventoryAlertClient<$Result.GetResult<Prisma.$InventoryAlertPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of InventoryAlerts.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertCountArgs} args - Arguments to filter InventoryAlerts to count.
     * @example
     * // Count the number of InventoryAlerts
     * const count = await prisma.inventoryAlert.count({
     *   where: {
     *     // ... the filter for the InventoryAlerts we want to count
     *   }
     * })
    **/
    count<T extends InventoryAlertCountArgs>(
      args?: Subset<T, InventoryAlertCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], InventoryAlertCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a InventoryAlert.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends InventoryAlertAggregateArgs>(args: Subset<T, InventoryAlertAggregateArgs>): Prisma.PrismaPromise<GetInventoryAlertAggregateType<T>>

    /**
     * Group by InventoryAlert.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {InventoryAlertGroupByArgs} args - Group by arguments.
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
      T extends InventoryAlertGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: InventoryAlertGroupByArgs['orderBy'] }
        : { orderBy?: InventoryAlertGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, InventoryAlertGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetInventoryAlertGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the InventoryAlert model
   */
  readonly fields: InventoryAlertFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for InventoryAlert.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__InventoryAlertClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    item<T extends InventoryItemDefaultArgs<ExtArgs> = {}>(args?: Subset<T, InventoryItemDefaultArgs<ExtArgs>>): Prisma__InventoryItemClient<$Result.GetResult<Prisma.$InventoryItemPayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
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
   * Fields of the InventoryAlert model
   */ 
  interface InventoryAlertFieldRefs {
    readonly id: FieldRef<"InventoryAlert", 'String'>
    readonly alertType: FieldRef<"InventoryAlert", 'AlertType'>
    readonly priority: FieldRef<"InventoryAlert", 'AlertPriority'>
    readonly status: FieldRef<"InventoryAlert", 'AlertStatus'>
    readonly itemId: FieldRef<"InventoryAlert", 'String'>
    readonly itemName: FieldRef<"InventoryAlert", 'String'>
    readonly itemNameAr: FieldRef<"InventoryAlert", 'String'>
    readonly titleEn: FieldRef<"InventoryAlert", 'String'>
    readonly titleAr: FieldRef<"InventoryAlert", 'String'>
    readonly messageEn: FieldRef<"InventoryAlert", 'String'>
    readonly messageAr: FieldRef<"InventoryAlert", 'String'>
    readonly currentValue: FieldRef<"InventoryAlert", 'Float'>
    readonly thresholdValue: FieldRef<"InventoryAlert", 'Float'>
    readonly recommendedActionEn: FieldRef<"InventoryAlert", 'String'>
    readonly recommendedActionAr: FieldRef<"InventoryAlert", 'String'>
    readonly actionUrl: FieldRef<"InventoryAlert", 'String'>
    readonly createdAt: FieldRef<"InventoryAlert", 'DateTime'>
    readonly acknowledgedAt: FieldRef<"InventoryAlert", 'DateTime'>
    readonly acknowledgedBy: FieldRef<"InventoryAlert", 'String'>
    readonly resolvedAt: FieldRef<"InventoryAlert", 'DateTime'>
    readonly resolvedBy: FieldRef<"InventoryAlert", 'String'>
    readonly resolutionNotes: FieldRef<"InventoryAlert", 'String'>
    readonly snoozeUntil: FieldRef<"InventoryAlert", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * InventoryAlert findUnique
   */
  export type InventoryAlertFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * Filter, which InventoryAlert to fetch.
     */
    where: InventoryAlertWhereUniqueInput
  }

  /**
   * InventoryAlert findUniqueOrThrow
   */
  export type InventoryAlertFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * Filter, which InventoryAlert to fetch.
     */
    where: InventoryAlertWhereUniqueInput
  }

  /**
   * InventoryAlert findFirst
   */
  export type InventoryAlertFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * Filter, which InventoryAlert to fetch.
     */
    where?: InventoryAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryAlerts to fetch.
     */
    orderBy?: InventoryAlertOrderByWithRelationInput | InventoryAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for InventoryAlerts.
     */
    cursor?: InventoryAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of InventoryAlerts.
     */
    distinct?: InventoryAlertScalarFieldEnum | InventoryAlertScalarFieldEnum[]
  }

  /**
   * InventoryAlert findFirstOrThrow
   */
  export type InventoryAlertFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * Filter, which InventoryAlert to fetch.
     */
    where?: InventoryAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryAlerts to fetch.
     */
    orderBy?: InventoryAlertOrderByWithRelationInput | InventoryAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for InventoryAlerts.
     */
    cursor?: InventoryAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryAlerts.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of InventoryAlerts.
     */
    distinct?: InventoryAlertScalarFieldEnum | InventoryAlertScalarFieldEnum[]
  }

  /**
   * InventoryAlert findMany
   */
  export type InventoryAlertFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * Filter, which InventoryAlerts to fetch.
     */
    where?: InventoryAlertWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of InventoryAlerts to fetch.
     */
    orderBy?: InventoryAlertOrderByWithRelationInput | InventoryAlertOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing InventoryAlerts.
     */
    cursor?: InventoryAlertWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` InventoryAlerts from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` InventoryAlerts.
     */
    skip?: number
    distinct?: InventoryAlertScalarFieldEnum | InventoryAlertScalarFieldEnum[]
  }

  /**
   * InventoryAlert create
   */
  export type InventoryAlertCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * The data needed to create a InventoryAlert.
     */
    data: XOR<InventoryAlertCreateInput, InventoryAlertUncheckedCreateInput>
  }

  /**
   * InventoryAlert createMany
   */
  export type InventoryAlertCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many InventoryAlerts.
     */
    data: InventoryAlertCreateManyInput | InventoryAlertCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * InventoryAlert createManyAndReturn
   */
  export type InventoryAlertCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many InventoryAlerts.
     */
    data: InventoryAlertCreateManyInput | InventoryAlertCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * InventoryAlert update
   */
  export type InventoryAlertUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * The data needed to update a InventoryAlert.
     */
    data: XOR<InventoryAlertUpdateInput, InventoryAlertUncheckedUpdateInput>
    /**
     * Choose, which InventoryAlert to update.
     */
    where: InventoryAlertWhereUniqueInput
  }

  /**
   * InventoryAlert updateMany
   */
  export type InventoryAlertUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update InventoryAlerts.
     */
    data: XOR<InventoryAlertUpdateManyMutationInput, InventoryAlertUncheckedUpdateManyInput>
    /**
     * Filter which InventoryAlerts to update
     */
    where?: InventoryAlertWhereInput
  }

  /**
   * InventoryAlert upsert
   */
  export type InventoryAlertUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * The filter to search for the InventoryAlert to update in case it exists.
     */
    where: InventoryAlertWhereUniqueInput
    /**
     * In case the InventoryAlert found by the `where` argument doesn't exist, create a new InventoryAlert with this data.
     */
    create: XOR<InventoryAlertCreateInput, InventoryAlertUncheckedCreateInput>
    /**
     * In case the InventoryAlert was found with the provided `where` argument, update it with this data.
     */
    update: XOR<InventoryAlertUpdateInput, InventoryAlertUncheckedUpdateInput>
  }

  /**
   * InventoryAlert delete
   */
  export type InventoryAlertDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
    /**
     * Filter which InventoryAlert to delete.
     */
    where: InventoryAlertWhereUniqueInput
  }

  /**
   * InventoryAlert deleteMany
   */
  export type InventoryAlertDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which InventoryAlerts to delete
     */
    where?: InventoryAlertWhereInput
  }

  /**
   * InventoryAlert without action
   */
  export type InventoryAlertDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the InventoryAlert
     */
    select?: InventoryAlertSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: InventoryAlertInclude<ExtArgs> | null
  }


  /**
   * Model AlertSettings
   */

  export type AggregateAlertSettings = {
    _count: AlertSettingsCountAggregateOutputType | null
    _avg: AlertSettingsAvgAggregateOutputType | null
    _sum: AlertSettingsSumAggregateOutputType | null
    _min: AlertSettingsMinAggregateOutputType | null
    _max: AlertSettingsMaxAggregateOutputType | null
  }

  export type AlertSettingsAvgAggregateOutputType = {
    expiryWarningDays: number | null
    expiryCriticalDays: number | null
    defaultReorderLevel: number | null
    alertCheckInterval: number | null
    maxAlertsPerDay: number | null
  }

  export type AlertSettingsSumAggregateOutputType = {
    expiryWarningDays: number | null
    expiryCriticalDays: number | null
    defaultReorderLevel: number | null
    alertCheckInterval: number | null
    maxAlertsPerDay: number | null
  }

  export type AlertSettingsMinAggregateOutputType = {
    id: string | null
    tenantId: string | null
    expiryWarningDays: number | null
    expiryCriticalDays: number | null
    defaultReorderLevel: number | null
    enableEmailAlerts: boolean | null
    enablePushAlerts: boolean | null
    enableSmsAlerts: boolean | null
    alertCheckInterval: number | null
    maxAlertsPerDay: number | null
    autoResolveOnRestock: boolean | null
    autoResolveExpired: boolean | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type AlertSettingsMaxAggregateOutputType = {
    id: string | null
    tenantId: string | null
    expiryWarningDays: number | null
    expiryCriticalDays: number | null
    defaultReorderLevel: number | null
    enableEmailAlerts: boolean | null
    enablePushAlerts: boolean | null
    enableSmsAlerts: boolean | null
    alertCheckInterval: number | null
    maxAlertsPerDay: number | null
    autoResolveOnRestock: boolean | null
    autoResolveExpired: boolean | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type AlertSettingsCountAggregateOutputType = {
    id: number
    tenantId: number
    expiryWarningDays: number
    expiryCriticalDays: number
    defaultReorderLevel: number
    enableEmailAlerts: number
    enablePushAlerts: number
    enableSmsAlerts: number
    alertCheckInterval: number
    maxAlertsPerDay: number
    autoResolveOnRestock: number
    autoResolveExpired: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type AlertSettingsAvgAggregateInputType = {
    expiryWarningDays?: true
    expiryCriticalDays?: true
    defaultReorderLevel?: true
    alertCheckInterval?: true
    maxAlertsPerDay?: true
  }

  export type AlertSettingsSumAggregateInputType = {
    expiryWarningDays?: true
    expiryCriticalDays?: true
    defaultReorderLevel?: true
    alertCheckInterval?: true
    maxAlertsPerDay?: true
  }

  export type AlertSettingsMinAggregateInputType = {
    id?: true
    tenantId?: true
    expiryWarningDays?: true
    expiryCriticalDays?: true
    defaultReorderLevel?: true
    enableEmailAlerts?: true
    enablePushAlerts?: true
    enableSmsAlerts?: true
    alertCheckInterval?: true
    maxAlertsPerDay?: true
    autoResolveOnRestock?: true
    autoResolveExpired?: true
    createdAt?: true
    updatedAt?: true
  }

  export type AlertSettingsMaxAggregateInputType = {
    id?: true
    tenantId?: true
    expiryWarningDays?: true
    expiryCriticalDays?: true
    defaultReorderLevel?: true
    enableEmailAlerts?: true
    enablePushAlerts?: true
    enableSmsAlerts?: true
    alertCheckInterval?: true
    maxAlertsPerDay?: true
    autoResolveOnRestock?: true
    autoResolveExpired?: true
    createdAt?: true
    updatedAt?: true
  }

  export type AlertSettingsCountAggregateInputType = {
    id?: true
    tenantId?: true
    expiryWarningDays?: true
    expiryCriticalDays?: true
    defaultReorderLevel?: true
    enableEmailAlerts?: true
    enablePushAlerts?: true
    enableSmsAlerts?: true
    alertCheckInterval?: true
    maxAlertsPerDay?: true
    autoResolveOnRestock?: true
    autoResolveExpired?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type AlertSettingsAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which AlertSettings to aggregate.
     */
    where?: AlertSettingsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of AlertSettings to fetch.
     */
    orderBy?: AlertSettingsOrderByWithRelationInput | AlertSettingsOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: AlertSettingsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` AlertSettings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` AlertSettings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned AlertSettings
    **/
    _count?: true | AlertSettingsCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: AlertSettingsAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: AlertSettingsSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: AlertSettingsMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: AlertSettingsMaxAggregateInputType
  }

  export type GetAlertSettingsAggregateType<T extends AlertSettingsAggregateArgs> = {
        [P in keyof T & keyof AggregateAlertSettings]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateAlertSettings[P]>
      : GetScalarType<T[P], AggregateAlertSettings[P]>
  }




  export type AlertSettingsGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: AlertSettingsWhereInput
    orderBy?: AlertSettingsOrderByWithAggregationInput | AlertSettingsOrderByWithAggregationInput[]
    by: AlertSettingsScalarFieldEnum[] | AlertSettingsScalarFieldEnum
    having?: AlertSettingsScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: AlertSettingsCountAggregateInputType | true
    _avg?: AlertSettingsAvgAggregateInputType
    _sum?: AlertSettingsSumAggregateInputType
    _min?: AlertSettingsMinAggregateInputType
    _max?: AlertSettingsMaxAggregateInputType
  }

  export type AlertSettingsGroupByOutputType = {
    id: string
    tenantId: string
    expiryWarningDays: number
    expiryCriticalDays: number
    defaultReorderLevel: number
    enableEmailAlerts: boolean
    enablePushAlerts: boolean
    enableSmsAlerts: boolean
    alertCheckInterval: number
    maxAlertsPerDay: number
    autoResolveOnRestock: boolean
    autoResolveExpired: boolean
    createdAt: Date
    updatedAt: Date
    _count: AlertSettingsCountAggregateOutputType | null
    _avg: AlertSettingsAvgAggregateOutputType | null
    _sum: AlertSettingsSumAggregateOutputType | null
    _min: AlertSettingsMinAggregateOutputType | null
    _max: AlertSettingsMaxAggregateOutputType | null
  }

  type GetAlertSettingsGroupByPayload<T extends AlertSettingsGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<AlertSettingsGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof AlertSettingsGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], AlertSettingsGroupByOutputType[P]>
            : GetScalarType<T[P], AlertSettingsGroupByOutputType[P]>
        }
      >
    >


  export type AlertSettingsSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    expiryWarningDays?: boolean
    expiryCriticalDays?: boolean
    defaultReorderLevel?: boolean
    enableEmailAlerts?: boolean
    enablePushAlerts?: boolean
    enableSmsAlerts?: boolean
    alertCheckInterval?: boolean
    maxAlertsPerDay?: boolean
    autoResolveOnRestock?: boolean
    autoResolveExpired?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["alertSettings"]>

  export type AlertSettingsSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    tenantId?: boolean
    expiryWarningDays?: boolean
    expiryCriticalDays?: boolean
    defaultReorderLevel?: boolean
    enableEmailAlerts?: boolean
    enablePushAlerts?: boolean
    enableSmsAlerts?: boolean
    alertCheckInterval?: boolean
    maxAlertsPerDay?: boolean
    autoResolveOnRestock?: boolean
    autoResolveExpired?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["alertSettings"]>

  export type AlertSettingsSelectScalar = {
    id?: boolean
    tenantId?: boolean
    expiryWarningDays?: boolean
    expiryCriticalDays?: boolean
    defaultReorderLevel?: boolean
    enableEmailAlerts?: boolean
    enablePushAlerts?: boolean
    enableSmsAlerts?: boolean
    alertCheckInterval?: boolean
    maxAlertsPerDay?: boolean
    autoResolveOnRestock?: boolean
    autoResolveExpired?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }


  export type $AlertSettingsPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "AlertSettings"
    objects: {}
    scalars: $Extensions.GetPayloadResult<{
      id: string
      tenantId: string
      expiryWarningDays: number
      expiryCriticalDays: number
      defaultReorderLevel: number
      enableEmailAlerts: boolean
      enablePushAlerts: boolean
      enableSmsAlerts: boolean
      alertCheckInterval: number
      maxAlertsPerDay: number
      autoResolveOnRestock: boolean
      autoResolveExpired: boolean
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["alertSettings"]>
    composites: {}
  }

  type AlertSettingsGetPayload<S extends boolean | null | undefined | AlertSettingsDefaultArgs> = $Result.GetResult<Prisma.$AlertSettingsPayload, S>

  type AlertSettingsCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<AlertSettingsFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: AlertSettingsCountAggregateInputType | true
    }

  export interface AlertSettingsDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['AlertSettings'], meta: { name: 'AlertSettings' } }
    /**
     * Find zero or one AlertSettings that matches the filter.
     * @param {AlertSettingsFindUniqueArgs} args - Arguments to find a AlertSettings
     * @example
     * // Get one AlertSettings
     * const alertSettings = await prisma.alertSettings.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends AlertSettingsFindUniqueArgs>(args: SelectSubset<T, AlertSettingsFindUniqueArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one AlertSettings that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {AlertSettingsFindUniqueOrThrowArgs} args - Arguments to find a AlertSettings
     * @example
     * // Get one AlertSettings
     * const alertSettings = await prisma.alertSettings.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends AlertSettingsFindUniqueOrThrowArgs>(args: SelectSubset<T, AlertSettingsFindUniqueOrThrowArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first AlertSettings that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsFindFirstArgs} args - Arguments to find a AlertSettings
     * @example
     * // Get one AlertSettings
     * const alertSettings = await prisma.alertSettings.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends AlertSettingsFindFirstArgs>(args?: SelectSubset<T, AlertSettingsFindFirstArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first AlertSettings that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsFindFirstOrThrowArgs} args - Arguments to find a AlertSettings
     * @example
     * // Get one AlertSettings
     * const alertSettings = await prisma.alertSettings.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends AlertSettingsFindFirstOrThrowArgs>(args?: SelectSubset<T, AlertSettingsFindFirstOrThrowArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more AlertSettings that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all AlertSettings
     * const alertSettings = await prisma.alertSettings.findMany()
     * 
     * // Get first 10 AlertSettings
     * const alertSettings = await prisma.alertSettings.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const alertSettingsWithIdOnly = await prisma.alertSettings.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends AlertSettingsFindManyArgs>(args?: SelectSubset<T, AlertSettingsFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a AlertSettings.
     * @param {AlertSettingsCreateArgs} args - Arguments to create a AlertSettings.
     * @example
     * // Create one AlertSettings
     * const AlertSettings = await prisma.alertSettings.create({
     *   data: {
     *     // ... data to create a AlertSettings
     *   }
     * })
     * 
     */
    create<T extends AlertSettingsCreateArgs>(args: SelectSubset<T, AlertSettingsCreateArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many AlertSettings.
     * @param {AlertSettingsCreateManyArgs} args - Arguments to create many AlertSettings.
     * @example
     * // Create many AlertSettings
     * const alertSettings = await prisma.alertSettings.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends AlertSettingsCreateManyArgs>(args?: SelectSubset<T, AlertSettingsCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many AlertSettings and returns the data saved in the database.
     * @param {AlertSettingsCreateManyAndReturnArgs} args - Arguments to create many AlertSettings.
     * @example
     * // Create many AlertSettings
     * const alertSettings = await prisma.alertSettings.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many AlertSettings and only return the `id`
     * const alertSettingsWithIdOnly = await prisma.alertSettings.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends AlertSettingsCreateManyAndReturnArgs>(args?: SelectSubset<T, AlertSettingsCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a AlertSettings.
     * @param {AlertSettingsDeleteArgs} args - Arguments to delete one AlertSettings.
     * @example
     * // Delete one AlertSettings
     * const AlertSettings = await prisma.alertSettings.delete({
     *   where: {
     *     // ... filter to delete one AlertSettings
     *   }
     * })
     * 
     */
    delete<T extends AlertSettingsDeleteArgs>(args: SelectSubset<T, AlertSettingsDeleteArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one AlertSettings.
     * @param {AlertSettingsUpdateArgs} args - Arguments to update one AlertSettings.
     * @example
     * // Update one AlertSettings
     * const alertSettings = await prisma.alertSettings.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends AlertSettingsUpdateArgs>(args: SelectSubset<T, AlertSettingsUpdateArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more AlertSettings.
     * @param {AlertSettingsDeleteManyArgs} args - Arguments to filter AlertSettings to delete.
     * @example
     * // Delete a few AlertSettings
     * const { count } = await prisma.alertSettings.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends AlertSettingsDeleteManyArgs>(args?: SelectSubset<T, AlertSettingsDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more AlertSettings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many AlertSettings
     * const alertSettings = await prisma.alertSettings.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends AlertSettingsUpdateManyArgs>(args: SelectSubset<T, AlertSettingsUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one AlertSettings.
     * @param {AlertSettingsUpsertArgs} args - Arguments to update or create a AlertSettings.
     * @example
     * // Update or create a AlertSettings
     * const alertSettings = await prisma.alertSettings.upsert({
     *   create: {
     *     // ... data to create a AlertSettings
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the AlertSettings we want to update
     *   }
     * })
     */
    upsert<T extends AlertSettingsUpsertArgs>(args: SelectSubset<T, AlertSettingsUpsertArgs<ExtArgs>>): Prisma__AlertSettingsClient<$Result.GetResult<Prisma.$AlertSettingsPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of AlertSettings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsCountArgs} args - Arguments to filter AlertSettings to count.
     * @example
     * // Count the number of AlertSettings
     * const count = await prisma.alertSettings.count({
     *   where: {
     *     // ... the filter for the AlertSettings we want to count
     *   }
     * })
    **/
    count<T extends AlertSettingsCountArgs>(
      args?: Subset<T, AlertSettingsCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], AlertSettingsCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a AlertSettings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends AlertSettingsAggregateArgs>(args: Subset<T, AlertSettingsAggregateArgs>): Prisma.PrismaPromise<GetAlertSettingsAggregateType<T>>

    /**
     * Group by AlertSettings.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {AlertSettingsGroupByArgs} args - Group by arguments.
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
      T extends AlertSettingsGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: AlertSettingsGroupByArgs['orderBy'] }
        : { orderBy?: AlertSettingsGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, AlertSettingsGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetAlertSettingsGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the AlertSettings model
   */
  readonly fields: AlertSettingsFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for AlertSettings.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__AlertSettingsClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
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
   * Fields of the AlertSettings model
   */ 
  interface AlertSettingsFieldRefs {
    readonly id: FieldRef<"AlertSettings", 'String'>
    readonly tenantId: FieldRef<"AlertSettings", 'String'>
    readonly expiryWarningDays: FieldRef<"AlertSettings", 'Int'>
    readonly expiryCriticalDays: FieldRef<"AlertSettings", 'Int'>
    readonly defaultReorderLevel: FieldRef<"AlertSettings", 'Float'>
    readonly enableEmailAlerts: FieldRef<"AlertSettings", 'Boolean'>
    readonly enablePushAlerts: FieldRef<"AlertSettings", 'Boolean'>
    readonly enableSmsAlerts: FieldRef<"AlertSettings", 'Boolean'>
    readonly alertCheckInterval: FieldRef<"AlertSettings", 'Int'>
    readonly maxAlertsPerDay: FieldRef<"AlertSettings", 'Int'>
    readonly autoResolveOnRestock: FieldRef<"AlertSettings", 'Boolean'>
    readonly autoResolveExpired: FieldRef<"AlertSettings", 'Boolean'>
    readonly createdAt: FieldRef<"AlertSettings", 'DateTime'>
    readonly updatedAt: FieldRef<"AlertSettings", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * AlertSettings findUnique
   */
  export type AlertSettingsFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * Filter, which AlertSettings to fetch.
     */
    where: AlertSettingsWhereUniqueInput
  }

  /**
   * AlertSettings findUniqueOrThrow
   */
  export type AlertSettingsFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * Filter, which AlertSettings to fetch.
     */
    where: AlertSettingsWhereUniqueInput
  }

  /**
   * AlertSettings findFirst
   */
  export type AlertSettingsFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * Filter, which AlertSettings to fetch.
     */
    where?: AlertSettingsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of AlertSettings to fetch.
     */
    orderBy?: AlertSettingsOrderByWithRelationInput | AlertSettingsOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for AlertSettings.
     */
    cursor?: AlertSettingsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` AlertSettings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` AlertSettings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of AlertSettings.
     */
    distinct?: AlertSettingsScalarFieldEnum | AlertSettingsScalarFieldEnum[]
  }

  /**
   * AlertSettings findFirstOrThrow
   */
  export type AlertSettingsFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * Filter, which AlertSettings to fetch.
     */
    where?: AlertSettingsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of AlertSettings to fetch.
     */
    orderBy?: AlertSettingsOrderByWithRelationInput | AlertSettingsOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for AlertSettings.
     */
    cursor?: AlertSettingsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` AlertSettings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` AlertSettings.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of AlertSettings.
     */
    distinct?: AlertSettingsScalarFieldEnum | AlertSettingsScalarFieldEnum[]
  }

  /**
   * AlertSettings findMany
   */
  export type AlertSettingsFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * Filter, which AlertSettings to fetch.
     */
    where?: AlertSettingsWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of AlertSettings to fetch.
     */
    orderBy?: AlertSettingsOrderByWithRelationInput | AlertSettingsOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing AlertSettings.
     */
    cursor?: AlertSettingsWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` AlertSettings from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` AlertSettings.
     */
    skip?: number
    distinct?: AlertSettingsScalarFieldEnum | AlertSettingsScalarFieldEnum[]
  }

  /**
   * AlertSettings create
   */
  export type AlertSettingsCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * The data needed to create a AlertSettings.
     */
    data: XOR<AlertSettingsCreateInput, AlertSettingsUncheckedCreateInput>
  }

  /**
   * AlertSettings createMany
   */
  export type AlertSettingsCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many AlertSettings.
     */
    data: AlertSettingsCreateManyInput | AlertSettingsCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * AlertSettings createManyAndReturn
   */
  export type AlertSettingsCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many AlertSettings.
     */
    data: AlertSettingsCreateManyInput | AlertSettingsCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * AlertSettings update
   */
  export type AlertSettingsUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * The data needed to update a AlertSettings.
     */
    data: XOR<AlertSettingsUpdateInput, AlertSettingsUncheckedUpdateInput>
    /**
     * Choose, which AlertSettings to update.
     */
    where: AlertSettingsWhereUniqueInput
  }

  /**
   * AlertSettings updateMany
   */
  export type AlertSettingsUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update AlertSettings.
     */
    data: XOR<AlertSettingsUpdateManyMutationInput, AlertSettingsUncheckedUpdateManyInput>
    /**
     * Filter which AlertSettings to update
     */
    where?: AlertSettingsWhereInput
  }

  /**
   * AlertSettings upsert
   */
  export type AlertSettingsUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * The filter to search for the AlertSettings to update in case it exists.
     */
    where: AlertSettingsWhereUniqueInput
    /**
     * In case the AlertSettings found by the `where` argument doesn't exist, create a new AlertSettings with this data.
     */
    create: XOR<AlertSettingsCreateInput, AlertSettingsUncheckedCreateInput>
    /**
     * In case the AlertSettings was found with the provided `where` argument, update it with this data.
     */
    update: XOR<AlertSettingsUpdateInput, AlertSettingsUncheckedUpdateInput>
  }

  /**
   * AlertSettings delete
   */
  export type AlertSettingsDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
    /**
     * Filter which AlertSettings to delete.
     */
    where: AlertSettingsWhereUniqueInput
  }

  /**
   * AlertSettings deleteMany
   */
  export type AlertSettingsDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which AlertSettings to delete
     */
    where?: AlertSettingsWhereInput
  }

  /**
   * AlertSettings without action
   */
  export type AlertSettingsDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the AlertSettings
     */
    select?: AlertSettingsSelect<ExtArgs> | null
  }


  /**
   * Model Warehouse
   */

  export type AggregateWarehouse = {
    _count: WarehouseCountAggregateOutputType | null
    _avg: WarehouseAvgAggregateOutputType | null
    _sum: WarehouseSumAggregateOutputType | null
    _min: WarehouseMinAggregateOutputType | null
    _max: WarehouseMaxAggregateOutputType | null
  }

  export type WarehouseAvgAggregateOutputType = {
    latitude: number | null
    longitude: number | null
    capacityValue: number | null
    currentUsage: number | null
    tempMin: number | null
    tempMax: number | null
    humidityMin: number | null
    humidityMax: number | null
  }

  export type WarehouseSumAggregateOutputType = {
    latitude: number | null
    longitude: number | null
    capacityValue: number | null
    currentUsage: number | null
    tempMin: number | null
    tempMax: number | null
    humidityMin: number | null
    humidityMax: number | null
  }

  export type WarehouseMinAggregateOutputType = {
    id: string | null
    name: string | null
    nameAr: string | null
    warehouseType: $Enums.WarehouseType | null
    latitude: number | null
    longitude: number | null
    address: string | null
    governorate: string | null
    capacityValue: number | null
    capacityUnit: string | null
    currentUsage: number | null
    storageCondition: $Enums.StorageCondition | null
    tempMin: number | null
    tempMax: number | null
    humidityMin: number | null
    humidityMax: number | null
    isActive: boolean | null
    managerId: string | null
    managerName: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type WarehouseMaxAggregateOutputType = {
    id: string | null
    name: string | null
    nameAr: string | null
    warehouseType: $Enums.WarehouseType | null
    latitude: number | null
    longitude: number | null
    address: string | null
    governorate: string | null
    capacityValue: number | null
    capacityUnit: string | null
    currentUsage: number | null
    storageCondition: $Enums.StorageCondition | null
    tempMin: number | null
    tempMax: number | null
    humidityMin: number | null
    humidityMax: number | null
    isActive: boolean | null
    managerId: string | null
    managerName: string | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type WarehouseCountAggregateOutputType = {
    id: number
    name: number
    nameAr: number
    warehouseType: number
    latitude: number
    longitude: number
    address: number
    governorate: number
    capacityValue: number
    capacityUnit: number
    currentUsage: number
    storageCondition: number
    tempMin: number
    tempMax: number
    humidityMin: number
    humidityMax: number
    isActive: number
    managerId: number
    managerName: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type WarehouseAvgAggregateInputType = {
    latitude?: true
    longitude?: true
    capacityValue?: true
    currentUsage?: true
    tempMin?: true
    tempMax?: true
    humidityMin?: true
    humidityMax?: true
  }

  export type WarehouseSumAggregateInputType = {
    latitude?: true
    longitude?: true
    capacityValue?: true
    currentUsage?: true
    tempMin?: true
    tempMax?: true
    humidityMin?: true
    humidityMax?: true
  }

  export type WarehouseMinAggregateInputType = {
    id?: true
    name?: true
    nameAr?: true
    warehouseType?: true
    latitude?: true
    longitude?: true
    address?: true
    governorate?: true
    capacityValue?: true
    capacityUnit?: true
    currentUsage?: true
    storageCondition?: true
    tempMin?: true
    tempMax?: true
    humidityMin?: true
    humidityMax?: true
    isActive?: true
    managerId?: true
    managerName?: true
    createdAt?: true
    updatedAt?: true
  }

  export type WarehouseMaxAggregateInputType = {
    id?: true
    name?: true
    nameAr?: true
    warehouseType?: true
    latitude?: true
    longitude?: true
    address?: true
    governorate?: true
    capacityValue?: true
    capacityUnit?: true
    currentUsage?: true
    storageCondition?: true
    tempMin?: true
    tempMax?: true
    humidityMin?: true
    humidityMax?: true
    isActive?: true
    managerId?: true
    managerName?: true
    createdAt?: true
    updatedAt?: true
  }

  export type WarehouseCountAggregateInputType = {
    id?: true
    name?: true
    nameAr?: true
    warehouseType?: true
    latitude?: true
    longitude?: true
    address?: true
    governorate?: true
    capacityValue?: true
    capacityUnit?: true
    currentUsage?: true
    storageCondition?: true
    tempMin?: true
    tempMax?: true
    humidityMin?: true
    humidityMax?: true
    isActive?: true
    managerId?: true
    managerName?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type WarehouseAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Warehouse to aggregate.
     */
    where?: WarehouseWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Warehouses to fetch.
     */
    orderBy?: WarehouseOrderByWithRelationInput | WarehouseOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: WarehouseWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Warehouses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Warehouses.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Warehouses
    **/
    _count?: true | WarehouseCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: WarehouseAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: WarehouseSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: WarehouseMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: WarehouseMaxAggregateInputType
  }

  export type GetWarehouseAggregateType<T extends WarehouseAggregateArgs> = {
        [P in keyof T & keyof AggregateWarehouse]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateWarehouse[P]>
      : GetScalarType<T[P], AggregateWarehouse[P]>
  }




  export type WarehouseGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: WarehouseWhereInput
    orderBy?: WarehouseOrderByWithAggregationInput | WarehouseOrderByWithAggregationInput[]
    by: WarehouseScalarFieldEnum[] | WarehouseScalarFieldEnum
    having?: WarehouseScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: WarehouseCountAggregateInputType | true
    _avg?: WarehouseAvgAggregateInputType
    _sum?: WarehouseSumAggregateInputType
    _min?: WarehouseMinAggregateInputType
    _max?: WarehouseMaxAggregateInputType
  }

  export type WarehouseGroupByOutputType = {
    id: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude: number | null
    longitude: number | null
    address: string | null
    governorate: string | null
    capacityValue: number
    capacityUnit: string
    currentUsage: number
    storageCondition: $Enums.StorageCondition
    tempMin: number | null
    tempMax: number | null
    humidityMin: number | null
    humidityMax: number | null
    isActive: boolean
    managerId: string | null
    managerName: string | null
    createdAt: Date
    updatedAt: Date
    _count: WarehouseCountAggregateOutputType | null
    _avg: WarehouseAvgAggregateOutputType | null
    _sum: WarehouseSumAggregateOutputType | null
    _min: WarehouseMinAggregateOutputType | null
    _max: WarehouseMaxAggregateOutputType | null
  }

  type GetWarehouseGroupByPayload<T extends WarehouseGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<WarehouseGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof WarehouseGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], WarehouseGroupByOutputType[P]>
            : GetScalarType<T[P], WarehouseGroupByOutputType[P]>
        }
      >
    >


  export type WarehouseSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    name?: boolean
    nameAr?: boolean
    warehouseType?: boolean
    latitude?: boolean
    longitude?: boolean
    address?: boolean
    governorate?: boolean
    capacityValue?: boolean
    capacityUnit?: boolean
    currentUsage?: boolean
    storageCondition?: boolean
    tempMin?: boolean
    tempMax?: boolean
    humidityMin?: boolean
    humidityMax?: boolean
    isActive?: boolean
    managerId?: boolean
    managerName?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    zones?: boolean | Warehouse$zonesArgs<ExtArgs>
    transfersFrom?: boolean | Warehouse$transfersFromArgs<ExtArgs>
    transfersTo?: boolean | Warehouse$transfersToArgs<ExtArgs>
    _count?: boolean | WarehouseCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["warehouse"]>

  export type WarehouseSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    name?: boolean
    nameAr?: boolean
    warehouseType?: boolean
    latitude?: boolean
    longitude?: boolean
    address?: boolean
    governorate?: boolean
    capacityValue?: boolean
    capacityUnit?: boolean
    currentUsage?: boolean
    storageCondition?: boolean
    tempMin?: boolean
    tempMax?: boolean
    humidityMin?: boolean
    humidityMax?: boolean
    isActive?: boolean
    managerId?: boolean
    managerName?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }, ExtArgs["result"]["warehouse"]>

  export type WarehouseSelectScalar = {
    id?: boolean
    name?: boolean
    nameAr?: boolean
    warehouseType?: boolean
    latitude?: boolean
    longitude?: boolean
    address?: boolean
    governorate?: boolean
    capacityValue?: boolean
    capacityUnit?: boolean
    currentUsage?: boolean
    storageCondition?: boolean
    tempMin?: boolean
    tempMax?: boolean
    humidityMin?: boolean
    humidityMax?: boolean
    isActive?: boolean
    managerId?: boolean
    managerName?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type WarehouseInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    zones?: boolean | Warehouse$zonesArgs<ExtArgs>
    transfersFrom?: boolean | Warehouse$transfersFromArgs<ExtArgs>
    transfersTo?: boolean | Warehouse$transfersToArgs<ExtArgs>
    _count?: boolean | WarehouseCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type WarehouseIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {}

  export type $WarehousePayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Warehouse"
    objects: {
      zones: Prisma.$ZonePayload<ExtArgs>[]
      transfersFrom: Prisma.$StockTransferPayload<ExtArgs>[]
      transfersTo: Prisma.$StockTransferPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      name: string
      nameAr: string
      warehouseType: $Enums.WarehouseType
      latitude: number | null
      longitude: number | null
      address: string | null
      governorate: string | null
      capacityValue: number
      capacityUnit: string
      currentUsage: number
      storageCondition: $Enums.StorageCondition
      tempMin: number | null
      tempMax: number | null
      humidityMin: number | null
      humidityMax: number | null
      isActive: boolean
      managerId: string | null
      managerName: string | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["warehouse"]>
    composites: {}
  }

  type WarehouseGetPayload<S extends boolean | null | undefined | WarehouseDefaultArgs> = $Result.GetResult<Prisma.$WarehousePayload, S>

  type WarehouseCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<WarehouseFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: WarehouseCountAggregateInputType | true
    }

  export interface WarehouseDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Warehouse'], meta: { name: 'Warehouse' } }
    /**
     * Find zero or one Warehouse that matches the filter.
     * @param {WarehouseFindUniqueArgs} args - Arguments to find a Warehouse
     * @example
     * // Get one Warehouse
     * const warehouse = await prisma.warehouse.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends WarehouseFindUniqueArgs>(args: SelectSubset<T, WarehouseFindUniqueArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Warehouse that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {WarehouseFindUniqueOrThrowArgs} args - Arguments to find a Warehouse
     * @example
     * // Get one Warehouse
     * const warehouse = await prisma.warehouse.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends WarehouseFindUniqueOrThrowArgs>(args: SelectSubset<T, WarehouseFindUniqueOrThrowArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Warehouse that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseFindFirstArgs} args - Arguments to find a Warehouse
     * @example
     * // Get one Warehouse
     * const warehouse = await prisma.warehouse.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends WarehouseFindFirstArgs>(args?: SelectSubset<T, WarehouseFindFirstArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Warehouse that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseFindFirstOrThrowArgs} args - Arguments to find a Warehouse
     * @example
     * // Get one Warehouse
     * const warehouse = await prisma.warehouse.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends WarehouseFindFirstOrThrowArgs>(args?: SelectSubset<T, WarehouseFindFirstOrThrowArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Warehouses that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Warehouses
     * const warehouses = await prisma.warehouse.findMany()
     * 
     * // Get first 10 Warehouses
     * const warehouses = await prisma.warehouse.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const warehouseWithIdOnly = await prisma.warehouse.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends WarehouseFindManyArgs>(args?: SelectSubset<T, WarehouseFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Warehouse.
     * @param {WarehouseCreateArgs} args - Arguments to create a Warehouse.
     * @example
     * // Create one Warehouse
     * const Warehouse = await prisma.warehouse.create({
     *   data: {
     *     // ... data to create a Warehouse
     *   }
     * })
     * 
     */
    create<T extends WarehouseCreateArgs>(args: SelectSubset<T, WarehouseCreateArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Warehouses.
     * @param {WarehouseCreateManyArgs} args - Arguments to create many Warehouses.
     * @example
     * // Create many Warehouses
     * const warehouse = await prisma.warehouse.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends WarehouseCreateManyArgs>(args?: SelectSubset<T, WarehouseCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Warehouses and returns the data saved in the database.
     * @param {WarehouseCreateManyAndReturnArgs} args - Arguments to create many Warehouses.
     * @example
     * // Create many Warehouses
     * const warehouse = await prisma.warehouse.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Warehouses and only return the `id`
     * const warehouseWithIdOnly = await prisma.warehouse.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends WarehouseCreateManyAndReturnArgs>(args?: SelectSubset<T, WarehouseCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Warehouse.
     * @param {WarehouseDeleteArgs} args - Arguments to delete one Warehouse.
     * @example
     * // Delete one Warehouse
     * const Warehouse = await prisma.warehouse.delete({
     *   where: {
     *     // ... filter to delete one Warehouse
     *   }
     * })
     * 
     */
    delete<T extends WarehouseDeleteArgs>(args: SelectSubset<T, WarehouseDeleteArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Warehouse.
     * @param {WarehouseUpdateArgs} args - Arguments to update one Warehouse.
     * @example
     * // Update one Warehouse
     * const warehouse = await prisma.warehouse.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends WarehouseUpdateArgs>(args: SelectSubset<T, WarehouseUpdateArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Warehouses.
     * @param {WarehouseDeleteManyArgs} args - Arguments to filter Warehouses to delete.
     * @example
     * // Delete a few Warehouses
     * const { count } = await prisma.warehouse.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends WarehouseDeleteManyArgs>(args?: SelectSubset<T, WarehouseDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Warehouses.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Warehouses
     * const warehouse = await prisma.warehouse.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends WarehouseUpdateManyArgs>(args: SelectSubset<T, WarehouseUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Warehouse.
     * @param {WarehouseUpsertArgs} args - Arguments to update or create a Warehouse.
     * @example
     * // Update or create a Warehouse
     * const warehouse = await prisma.warehouse.upsert({
     *   create: {
     *     // ... data to create a Warehouse
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Warehouse we want to update
     *   }
     * })
     */
    upsert<T extends WarehouseUpsertArgs>(args: SelectSubset<T, WarehouseUpsertArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Warehouses.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseCountArgs} args - Arguments to filter Warehouses to count.
     * @example
     * // Count the number of Warehouses
     * const count = await prisma.warehouse.count({
     *   where: {
     *     // ... the filter for the Warehouses we want to count
     *   }
     * })
    **/
    count<T extends WarehouseCountArgs>(
      args?: Subset<T, WarehouseCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], WarehouseCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Warehouse.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends WarehouseAggregateArgs>(args: Subset<T, WarehouseAggregateArgs>): Prisma.PrismaPromise<GetWarehouseAggregateType<T>>

    /**
     * Group by Warehouse.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {WarehouseGroupByArgs} args - Group by arguments.
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
      T extends WarehouseGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: WarehouseGroupByArgs['orderBy'] }
        : { orderBy?: WarehouseGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, WarehouseGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetWarehouseGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Warehouse model
   */
  readonly fields: WarehouseFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Warehouse.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__WarehouseClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    zones<T extends Warehouse$zonesArgs<ExtArgs> = {}>(args?: Subset<T, Warehouse$zonesArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findMany"> | Null>
    transfersFrom<T extends Warehouse$transfersFromArgs<ExtArgs> = {}>(args?: Subset<T, Warehouse$transfersFromArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findMany"> | Null>
    transfersTo<T extends Warehouse$transfersToArgs<ExtArgs> = {}>(args?: Subset<T, Warehouse$transfersToArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findMany"> | Null>
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
   * Fields of the Warehouse model
   */ 
  interface WarehouseFieldRefs {
    readonly id: FieldRef<"Warehouse", 'String'>
    readonly name: FieldRef<"Warehouse", 'String'>
    readonly nameAr: FieldRef<"Warehouse", 'String'>
    readonly warehouseType: FieldRef<"Warehouse", 'WarehouseType'>
    readonly latitude: FieldRef<"Warehouse", 'Float'>
    readonly longitude: FieldRef<"Warehouse", 'Float'>
    readonly address: FieldRef<"Warehouse", 'String'>
    readonly governorate: FieldRef<"Warehouse", 'String'>
    readonly capacityValue: FieldRef<"Warehouse", 'Float'>
    readonly capacityUnit: FieldRef<"Warehouse", 'String'>
    readonly currentUsage: FieldRef<"Warehouse", 'Float'>
    readonly storageCondition: FieldRef<"Warehouse", 'StorageCondition'>
    readonly tempMin: FieldRef<"Warehouse", 'Float'>
    readonly tempMax: FieldRef<"Warehouse", 'Float'>
    readonly humidityMin: FieldRef<"Warehouse", 'Float'>
    readonly humidityMax: FieldRef<"Warehouse", 'Float'>
    readonly isActive: FieldRef<"Warehouse", 'Boolean'>
    readonly managerId: FieldRef<"Warehouse", 'String'>
    readonly managerName: FieldRef<"Warehouse", 'String'>
    readonly createdAt: FieldRef<"Warehouse", 'DateTime'>
    readonly updatedAt: FieldRef<"Warehouse", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Warehouse findUnique
   */
  export type WarehouseFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * Filter, which Warehouse to fetch.
     */
    where: WarehouseWhereUniqueInput
  }

  /**
   * Warehouse findUniqueOrThrow
   */
  export type WarehouseFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * Filter, which Warehouse to fetch.
     */
    where: WarehouseWhereUniqueInput
  }

  /**
   * Warehouse findFirst
   */
  export type WarehouseFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * Filter, which Warehouse to fetch.
     */
    where?: WarehouseWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Warehouses to fetch.
     */
    orderBy?: WarehouseOrderByWithRelationInput | WarehouseOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Warehouses.
     */
    cursor?: WarehouseWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Warehouses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Warehouses.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Warehouses.
     */
    distinct?: WarehouseScalarFieldEnum | WarehouseScalarFieldEnum[]
  }

  /**
   * Warehouse findFirstOrThrow
   */
  export type WarehouseFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * Filter, which Warehouse to fetch.
     */
    where?: WarehouseWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Warehouses to fetch.
     */
    orderBy?: WarehouseOrderByWithRelationInput | WarehouseOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Warehouses.
     */
    cursor?: WarehouseWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Warehouses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Warehouses.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Warehouses.
     */
    distinct?: WarehouseScalarFieldEnum | WarehouseScalarFieldEnum[]
  }

  /**
   * Warehouse findMany
   */
  export type WarehouseFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * Filter, which Warehouses to fetch.
     */
    where?: WarehouseWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Warehouses to fetch.
     */
    orderBy?: WarehouseOrderByWithRelationInput | WarehouseOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Warehouses.
     */
    cursor?: WarehouseWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Warehouses from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Warehouses.
     */
    skip?: number
    distinct?: WarehouseScalarFieldEnum | WarehouseScalarFieldEnum[]
  }

  /**
   * Warehouse create
   */
  export type WarehouseCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * The data needed to create a Warehouse.
     */
    data: XOR<WarehouseCreateInput, WarehouseUncheckedCreateInput>
  }

  /**
   * Warehouse createMany
   */
  export type WarehouseCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Warehouses.
     */
    data: WarehouseCreateManyInput | WarehouseCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Warehouse createManyAndReturn
   */
  export type WarehouseCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Warehouses.
     */
    data: WarehouseCreateManyInput | WarehouseCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Warehouse update
   */
  export type WarehouseUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * The data needed to update a Warehouse.
     */
    data: XOR<WarehouseUpdateInput, WarehouseUncheckedUpdateInput>
    /**
     * Choose, which Warehouse to update.
     */
    where: WarehouseWhereUniqueInput
  }

  /**
   * Warehouse updateMany
   */
  export type WarehouseUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Warehouses.
     */
    data: XOR<WarehouseUpdateManyMutationInput, WarehouseUncheckedUpdateManyInput>
    /**
     * Filter which Warehouses to update
     */
    where?: WarehouseWhereInput
  }

  /**
   * Warehouse upsert
   */
  export type WarehouseUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * The filter to search for the Warehouse to update in case it exists.
     */
    where: WarehouseWhereUniqueInput
    /**
     * In case the Warehouse found by the `where` argument doesn't exist, create a new Warehouse with this data.
     */
    create: XOR<WarehouseCreateInput, WarehouseUncheckedCreateInput>
    /**
     * In case the Warehouse was found with the provided `where` argument, update it with this data.
     */
    update: XOR<WarehouseUpdateInput, WarehouseUncheckedUpdateInput>
  }

  /**
   * Warehouse delete
   */
  export type WarehouseDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    /**
     * Filter which Warehouse to delete.
     */
    where: WarehouseWhereUniqueInput
  }

  /**
   * Warehouse deleteMany
   */
  export type WarehouseDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Warehouses to delete
     */
    where?: WarehouseWhereInput
  }

  /**
   * Warehouse.zones
   */
  export type Warehouse$zonesArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    where?: ZoneWhereInput
    orderBy?: ZoneOrderByWithRelationInput | ZoneOrderByWithRelationInput[]
    cursor?: ZoneWhereUniqueInput
    take?: number
    skip?: number
    distinct?: ZoneScalarFieldEnum | ZoneScalarFieldEnum[]
  }

  /**
   * Warehouse.transfersFrom
   */
  export type Warehouse$transfersFromArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    where?: StockTransferWhereInput
    orderBy?: StockTransferOrderByWithRelationInput | StockTransferOrderByWithRelationInput[]
    cursor?: StockTransferWhereUniqueInput
    take?: number
    skip?: number
    distinct?: StockTransferScalarFieldEnum | StockTransferScalarFieldEnum[]
  }

  /**
   * Warehouse.transfersTo
   */
  export type Warehouse$transfersToArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    where?: StockTransferWhereInput
    orderBy?: StockTransferOrderByWithRelationInput | StockTransferOrderByWithRelationInput[]
    cursor?: StockTransferWhereUniqueInput
    take?: number
    skip?: number
    distinct?: StockTransferScalarFieldEnum | StockTransferScalarFieldEnum[]
  }

  /**
   * Warehouse without action
   */
  export type WarehouseDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
  }


  /**
   * Model Zone
   */

  export type AggregateZone = {
    _count: ZoneCountAggregateOutputType | null
    _avg: ZoneAvgAggregateOutputType | null
    _sum: ZoneSumAggregateOutputType | null
    _min: ZoneMinAggregateOutputType | null
    _max: ZoneMaxAggregateOutputType | null
  }

  export type ZoneAvgAggregateOutputType = {
    capacity: number | null
    currentUsage: number | null
  }

  export type ZoneSumAggregateOutputType = {
    capacity: number | null
    currentUsage: number | null
  }

  export type ZoneMinAggregateOutputType = {
    id: string | null
    warehouseId: string | null
    name: string | null
    nameAr: string | null
    capacity: number | null
    currentUsage: number | null
    condition: $Enums.StorageCondition | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type ZoneMaxAggregateOutputType = {
    id: string | null
    warehouseId: string | null
    name: string | null
    nameAr: string | null
    capacity: number | null
    currentUsage: number | null
    condition: $Enums.StorageCondition | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type ZoneCountAggregateOutputType = {
    id: number
    warehouseId: number
    name: number
    nameAr: number
    capacity: number
    currentUsage: number
    condition: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type ZoneAvgAggregateInputType = {
    capacity?: true
    currentUsage?: true
  }

  export type ZoneSumAggregateInputType = {
    capacity?: true
    currentUsage?: true
  }

  export type ZoneMinAggregateInputType = {
    id?: true
    warehouseId?: true
    name?: true
    nameAr?: true
    capacity?: true
    currentUsage?: true
    condition?: true
    createdAt?: true
    updatedAt?: true
  }

  export type ZoneMaxAggregateInputType = {
    id?: true
    warehouseId?: true
    name?: true
    nameAr?: true
    capacity?: true
    currentUsage?: true
    condition?: true
    createdAt?: true
    updatedAt?: true
  }

  export type ZoneCountAggregateInputType = {
    id?: true
    warehouseId?: true
    name?: true
    nameAr?: true
    capacity?: true
    currentUsage?: true
    condition?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type ZoneAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Zone to aggregate.
     */
    where?: ZoneWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Zones to fetch.
     */
    orderBy?: ZoneOrderByWithRelationInput | ZoneOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: ZoneWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Zones from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Zones.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned Zones
    **/
    _count?: true | ZoneCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: ZoneAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: ZoneSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: ZoneMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: ZoneMaxAggregateInputType
  }

  export type GetZoneAggregateType<T extends ZoneAggregateArgs> = {
        [P in keyof T & keyof AggregateZone]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateZone[P]>
      : GetScalarType<T[P], AggregateZone[P]>
  }




  export type ZoneGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: ZoneWhereInput
    orderBy?: ZoneOrderByWithAggregationInput | ZoneOrderByWithAggregationInput[]
    by: ZoneScalarFieldEnum[] | ZoneScalarFieldEnum
    having?: ZoneScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: ZoneCountAggregateInputType | true
    _avg?: ZoneAvgAggregateInputType
    _sum?: ZoneSumAggregateInputType
    _min?: ZoneMinAggregateInputType
    _max?: ZoneMaxAggregateInputType
  }

  export type ZoneGroupByOutputType = {
    id: string
    warehouseId: string
    name: string
    nameAr: string | null
    capacity: number
    currentUsage: number
    condition: $Enums.StorageCondition | null
    createdAt: Date
    updatedAt: Date
    _count: ZoneCountAggregateOutputType | null
    _avg: ZoneAvgAggregateOutputType | null
    _sum: ZoneSumAggregateOutputType | null
    _min: ZoneMinAggregateOutputType | null
    _max: ZoneMaxAggregateOutputType | null
  }

  type GetZoneGroupByPayload<T extends ZoneGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<ZoneGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof ZoneGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], ZoneGroupByOutputType[P]>
            : GetScalarType<T[P], ZoneGroupByOutputType[P]>
        }
      >
    >


  export type ZoneSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    warehouseId?: boolean
    name?: boolean
    nameAr?: boolean
    capacity?: boolean
    currentUsage?: boolean
    condition?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    warehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
    locations?: boolean | Zone$locationsArgs<ExtArgs>
    _count?: boolean | ZoneCountOutputTypeDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["zone"]>

  export type ZoneSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    warehouseId?: boolean
    name?: boolean
    nameAr?: boolean
    capacity?: boolean
    currentUsage?: boolean
    condition?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    warehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["zone"]>

  export type ZoneSelectScalar = {
    id?: boolean
    warehouseId?: boolean
    name?: boolean
    nameAr?: boolean
    capacity?: boolean
    currentUsage?: boolean
    condition?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type ZoneInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    warehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
    locations?: boolean | Zone$locationsArgs<ExtArgs>
    _count?: boolean | ZoneCountOutputTypeDefaultArgs<ExtArgs>
  }
  export type ZoneIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    warehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
  }

  export type $ZonePayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "Zone"
    objects: {
      warehouse: Prisma.$WarehousePayload<ExtArgs>
      locations: Prisma.$StorageLocationPayload<ExtArgs>[]
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      warehouseId: string
      name: string
      nameAr: string | null
      capacity: number
      currentUsage: number
      condition: $Enums.StorageCondition | null
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["zone"]>
    composites: {}
  }

  type ZoneGetPayload<S extends boolean | null | undefined | ZoneDefaultArgs> = $Result.GetResult<Prisma.$ZonePayload, S>

  type ZoneCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<ZoneFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: ZoneCountAggregateInputType | true
    }

  export interface ZoneDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['Zone'], meta: { name: 'Zone' } }
    /**
     * Find zero or one Zone that matches the filter.
     * @param {ZoneFindUniqueArgs} args - Arguments to find a Zone
     * @example
     * // Get one Zone
     * const zone = await prisma.zone.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends ZoneFindUniqueArgs>(args: SelectSubset<T, ZoneFindUniqueArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one Zone that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {ZoneFindUniqueOrThrowArgs} args - Arguments to find a Zone
     * @example
     * // Get one Zone
     * const zone = await prisma.zone.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends ZoneFindUniqueOrThrowArgs>(args: SelectSubset<T, ZoneFindUniqueOrThrowArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first Zone that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneFindFirstArgs} args - Arguments to find a Zone
     * @example
     * // Get one Zone
     * const zone = await prisma.zone.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends ZoneFindFirstArgs>(args?: SelectSubset<T, ZoneFindFirstArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first Zone that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneFindFirstOrThrowArgs} args - Arguments to find a Zone
     * @example
     * // Get one Zone
     * const zone = await prisma.zone.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends ZoneFindFirstOrThrowArgs>(args?: SelectSubset<T, ZoneFindFirstOrThrowArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more Zones that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all Zones
     * const zones = await prisma.zone.findMany()
     * 
     * // Get first 10 Zones
     * const zones = await prisma.zone.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const zoneWithIdOnly = await prisma.zone.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends ZoneFindManyArgs>(args?: SelectSubset<T, ZoneFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findMany">>

    /**
     * Create a Zone.
     * @param {ZoneCreateArgs} args - Arguments to create a Zone.
     * @example
     * // Create one Zone
     * const Zone = await prisma.zone.create({
     *   data: {
     *     // ... data to create a Zone
     *   }
     * })
     * 
     */
    create<T extends ZoneCreateArgs>(args: SelectSubset<T, ZoneCreateArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many Zones.
     * @param {ZoneCreateManyArgs} args - Arguments to create many Zones.
     * @example
     * // Create many Zones
     * const zone = await prisma.zone.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends ZoneCreateManyArgs>(args?: SelectSubset<T, ZoneCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many Zones and returns the data saved in the database.
     * @param {ZoneCreateManyAndReturnArgs} args - Arguments to create many Zones.
     * @example
     * // Create many Zones
     * const zone = await prisma.zone.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many Zones and only return the `id`
     * const zoneWithIdOnly = await prisma.zone.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends ZoneCreateManyAndReturnArgs>(args?: SelectSubset<T, ZoneCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a Zone.
     * @param {ZoneDeleteArgs} args - Arguments to delete one Zone.
     * @example
     * // Delete one Zone
     * const Zone = await prisma.zone.delete({
     *   where: {
     *     // ... filter to delete one Zone
     *   }
     * })
     * 
     */
    delete<T extends ZoneDeleteArgs>(args: SelectSubset<T, ZoneDeleteArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one Zone.
     * @param {ZoneUpdateArgs} args - Arguments to update one Zone.
     * @example
     * // Update one Zone
     * const zone = await prisma.zone.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends ZoneUpdateArgs>(args: SelectSubset<T, ZoneUpdateArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more Zones.
     * @param {ZoneDeleteManyArgs} args - Arguments to filter Zones to delete.
     * @example
     * // Delete a few Zones
     * const { count } = await prisma.zone.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends ZoneDeleteManyArgs>(args?: SelectSubset<T, ZoneDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more Zones.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many Zones
     * const zone = await prisma.zone.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends ZoneUpdateManyArgs>(args: SelectSubset<T, ZoneUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one Zone.
     * @param {ZoneUpsertArgs} args - Arguments to update or create a Zone.
     * @example
     * // Update or create a Zone
     * const zone = await prisma.zone.upsert({
     *   create: {
     *     // ... data to create a Zone
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the Zone we want to update
     *   }
     * })
     */
    upsert<T extends ZoneUpsertArgs>(args: SelectSubset<T, ZoneUpsertArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of Zones.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneCountArgs} args - Arguments to filter Zones to count.
     * @example
     * // Count the number of Zones
     * const count = await prisma.zone.count({
     *   where: {
     *     // ... the filter for the Zones we want to count
     *   }
     * })
    **/
    count<T extends ZoneCountArgs>(
      args?: Subset<T, ZoneCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], ZoneCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a Zone.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends ZoneAggregateArgs>(args: Subset<T, ZoneAggregateArgs>): Prisma.PrismaPromise<GetZoneAggregateType<T>>

    /**
     * Group by Zone.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {ZoneGroupByArgs} args - Group by arguments.
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
      T extends ZoneGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: ZoneGroupByArgs['orderBy'] }
        : { orderBy?: ZoneGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, ZoneGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetZoneGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the Zone model
   */
  readonly fields: ZoneFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for Zone.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__ZoneClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    warehouse<T extends WarehouseDefaultArgs<ExtArgs> = {}>(args?: Subset<T, WarehouseDefaultArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
    locations<T extends Zone$locationsArgs<ExtArgs> = {}>(args?: Subset<T, Zone$locationsArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "findMany"> | Null>
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
   * Fields of the Zone model
   */ 
  interface ZoneFieldRefs {
    readonly id: FieldRef<"Zone", 'String'>
    readonly warehouseId: FieldRef<"Zone", 'String'>
    readonly name: FieldRef<"Zone", 'String'>
    readonly nameAr: FieldRef<"Zone", 'String'>
    readonly capacity: FieldRef<"Zone", 'Float'>
    readonly currentUsage: FieldRef<"Zone", 'Float'>
    readonly condition: FieldRef<"Zone", 'StorageCondition'>
    readonly createdAt: FieldRef<"Zone", 'DateTime'>
    readonly updatedAt: FieldRef<"Zone", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * Zone findUnique
   */
  export type ZoneFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * Filter, which Zone to fetch.
     */
    where: ZoneWhereUniqueInput
  }

  /**
   * Zone findUniqueOrThrow
   */
  export type ZoneFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * Filter, which Zone to fetch.
     */
    where: ZoneWhereUniqueInput
  }

  /**
   * Zone findFirst
   */
  export type ZoneFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * Filter, which Zone to fetch.
     */
    where?: ZoneWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Zones to fetch.
     */
    orderBy?: ZoneOrderByWithRelationInput | ZoneOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Zones.
     */
    cursor?: ZoneWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Zones from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Zones.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Zones.
     */
    distinct?: ZoneScalarFieldEnum | ZoneScalarFieldEnum[]
  }

  /**
   * Zone findFirstOrThrow
   */
  export type ZoneFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * Filter, which Zone to fetch.
     */
    where?: ZoneWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Zones to fetch.
     */
    orderBy?: ZoneOrderByWithRelationInput | ZoneOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for Zones.
     */
    cursor?: ZoneWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Zones from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Zones.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of Zones.
     */
    distinct?: ZoneScalarFieldEnum | ZoneScalarFieldEnum[]
  }

  /**
   * Zone findMany
   */
  export type ZoneFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * Filter, which Zones to fetch.
     */
    where?: ZoneWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of Zones to fetch.
     */
    orderBy?: ZoneOrderByWithRelationInput | ZoneOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing Zones.
     */
    cursor?: ZoneWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` Zones from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` Zones.
     */
    skip?: number
    distinct?: ZoneScalarFieldEnum | ZoneScalarFieldEnum[]
  }

  /**
   * Zone create
   */
  export type ZoneCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * The data needed to create a Zone.
     */
    data: XOR<ZoneCreateInput, ZoneUncheckedCreateInput>
  }

  /**
   * Zone createMany
   */
  export type ZoneCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many Zones.
     */
    data: ZoneCreateManyInput | ZoneCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * Zone createManyAndReturn
   */
  export type ZoneCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many Zones.
     */
    data: ZoneCreateManyInput | ZoneCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * Zone update
   */
  export type ZoneUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * The data needed to update a Zone.
     */
    data: XOR<ZoneUpdateInput, ZoneUncheckedUpdateInput>
    /**
     * Choose, which Zone to update.
     */
    where: ZoneWhereUniqueInput
  }

  /**
   * Zone updateMany
   */
  export type ZoneUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update Zones.
     */
    data: XOR<ZoneUpdateManyMutationInput, ZoneUncheckedUpdateManyInput>
    /**
     * Filter which Zones to update
     */
    where?: ZoneWhereInput
  }

  /**
   * Zone upsert
   */
  export type ZoneUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * The filter to search for the Zone to update in case it exists.
     */
    where: ZoneWhereUniqueInput
    /**
     * In case the Zone found by the `where` argument doesn't exist, create a new Zone with this data.
     */
    create: XOR<ZoneCreateInput, ZoneUncheckedCreateInput>
    /**
     * In case the Zone was found with the provided `where` argument, update it with this data.
     */
    update: XOR<ZoneUpdateInput, ZoneUncheckedUpdateInput>
  }

  /**
   * Zone delete
   */
  export type ZoneDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
    /**
     * Filter which Zone to delete.
     */
    where: ZoneWhereUniqueInput
  }

  /**
   * Zone deleteMany
   */
  export type ZoneDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which Zones to delete
     */
    where?: ZoneWhereInput
  }

  /**
   * Zone.locations
   */
  export type Zone$locationsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    where?: StorageLocationWhereInput
    orderBy?: StorageLocationOrderByWithRelationInput | StorageLocationOrderByWithRelationInput[]
    cursor?: StorageLocationWhereUniqueInput
    take?: number
    skip?: number
    distinct?: StorageLocationScalarFieldEnum | StorageLocationScalarFieldEnum[]
  }

  /**
   * Zone without action
   */
  export type ZoneDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Zone
     */
    select?: ZoneSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: ZoneInclude<ExtArgs> | null
  }


  /**
   * Model StorageLocation
   */

  export type AggregateStorageLocation = {
    _count: StorageLocationCountAggregateOutputType | null
    _avg: StorageLocationAvgAggregateOutputType | null
    _sum: StorageLocationSumAggregateOutputType | null
    _min: StorageLocationMinAggregateOutputType | null
    _max: StorageLocationMaxAggregateOutputType | null
  }

  export type StorageLocationAvgAggregateOutputType = {
    capacity: number | null
    currentQty: number | null
  }

  export type StorageLocationSumAggregateOutputType = {
    capacity: number | null
    currentQty: number | null
  }

  export type StorageLocationMinAggregateOutputType = {
    id: string | null
    zoneId: string | null
    aisle: string | null
    shelf: string | null
    bin: string | null
    locationCode: string | null
    capacity: number | null
    isOccupied: boolean | null
    currentItemId: string | null
    currentQty: number | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type StorageLocationMaxAggregateOutputType = {
    id: string | null
    zoneId: string | null
    aisle: string | null
    shelf: string | null
    bin: string | null
    locationCode: string | null
    capacity: number | null
    isOccupied: boolean | null
    currentItemId: string | null
    currentQty: number | null
    createdAt: Date | null
    updatedAt: Date | null
  }

  export type StorageLocationCountAggregateOutputType = {
    id: number
    zoneId: number
    aisle: number
    shelf: number
    bin: number
    locationCode: number
    capacity: number
    isOccupied: number
    currentItemId: number
    currentQty: number
    createdAt: number
    updatedAt: number
    _all: number
  }


  export type StorageLocationAvgAggregateInputType = {
    capacity?: true
    currentQty?: true
  }

  export type StorageLocationSumAggregateInputType = {
    capacity?: true
    currentQty?: true
  }

  export type StorageLocationMinAggregateInputType = {
    id?: true
    zoneId?: true
    aisle?: true
    shelf?: true
    bin?: true
    locationCode?: true
    capacity?: true
    isOccupied?: true
    currentItemId?: true
    currentQty?: true
    createdAt?: true
    updatedAt?: true
  }

  export type StorageLocationMaxAggregateInputType = {
    id?: true
    zoneId?: true
    aisle?: true
    shelf?: true
    bin?: true
    locationCode?: true
    capacity?: true
    isOccupied?: true
    currentItemId?: true
    currentQty?: true
    createdAt?: true
    updatedAt?: true
  }

  export type StorageLocationCountAggregateInputType = {
    id?: true
    zoneId?: true
    aisle?: true
    shelf?: true
    bin?: true
    locationCode?: true
    capacity?: true
    isOccupied?: true
    currentItemId?: true
    currentQty?: true
    createdAt?: true
    updatedAt?: true
    _all?: true
  }

  export type StorageLocationAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which StorageLocation to aggregate.
     */
    where?: StorageLocationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StorageLocations to fetch.
     */
    orderBy?: StorageLocationOrderByWithRelationInput | StorageLocationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: StorageLocationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StorageLocations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StorageLocations.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned StorageLocations
    **/
    _count?: true | StorageLocationCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: StorageLocationAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: StorageLocationSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: StorageLocationMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: StorageLocationMaxAggregateInputType
  }

  export type GetStorageLocationAggregateType<T extends StorageLocationAggregateArgs> = {
        [P in keyof T & keyof AggregateStorageLocation]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateStorageLocation[P]>
      : GetScalarType<T[P], AggregateStorageLocation[P]>
  }




  export type StorageLocationGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: StorageLocationWhereInput
    orderBy?: StorageLocationOrderByWithAggregationInput | StorageLocationOrderByWithAggregationInput[]
    by: StorageLocationScalarFieldEnum[] | StorageLocationScalarFieldEnum
    having?: StorageLocationScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: StorageLocationCountAggregateInputType | true
    _avg?: StorageLocationAvgAggregateInputType
    _sum?: StorageLocationSumAggregateInputType
    _min?: StorageLocationMinAggregateInputType
    _max?: StorageLocationMaxAggregateInputType
  }

  export type StorageLocationGroupByOutputType = {
    id: string
    zoneId: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied: boolean
    currentItemId: string | null
    currentQty: number
    createdAt: Date
    updatedAt: Date
    _count: StorageLocationCountAggregateOutputType | null
    _avg: StorageLocationAvgAggregateOutputType | null
    _sum: StorageLocationSumAggregateOutputType | null
    _min: StorageLocationMinAggregateOutputType | null
    _max: StorageLocationMaxAggregateOutputType | null
  }

  type GetStorageLocationGroupByPayload<T extends StorageLocationGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<StorageLocationGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof StorageLocationGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], StorageLocationGroupByOutputType[P]>
            : GetScalarType<T[P], StorageLocationGroupByOutputType[P]>
        }
      >
    >


  export type StorageLocationSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    zoneId?: boolean
    aisle?: boolean
    shelf?: boolean
    bin?: boolean
    locationCode?: boolean
    capacity?: boolean
    isOccupied?: boolean
    currentItemId?: boolean
    currentQty?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    zone?: boolean | ZoneDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["storageLocation"]>

  export type StorageLocationSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    zoneId?: boolean
    aisle?: boolean
    shelf?: boolean
    bin?: boolean
    locationCode?: boolean
    capacity?: boolean
    isOccupied?: boolean
    currentItemId?: boolean
    currentQty?: boolean
    createdAt?: boolean
    updatedAt?: boolean
    zone?: boolean | ZoneDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["storageLocation"]>

  export type StorageLocationSelectScalar = {
    id?: boolean
    zoneId?: boolean
    aisle?: boolean
    shelf?: boolean
    bin?: boolean
    locationCode?: boolean
    capacity?: boolean
    isOccupied?: boolean
    currentItemId?: boolean
    currentQty?: boolean
    createdAt?: boolean
    updatedAt?: boolean
  }

  export type StorageLocationInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    zone?: boolean | ZoneDefaultArgs<ExtArgs>
  }
  export type StorageLocationIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    zone?: boolean | ZoneDefaultArgs<ExtArgs>
  }

  export type $StorageLocationPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "StorageLocation"
    objects: {
      zone: Prisma.$ZonePayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      zoneId: string
      aisle: string
      shelf: string
      bin: string
      locationCode: string
      capacity: number
      isOccupied: boolean
      currentItemId: string | null
      currentQty: number
      createdAt: Date
      updatedAt: Date
    }, ExtArgs["result"]["storageLocation"]>
    composites: {}
  }

  type StorageLocationGetPayload<S extends boolean | null | undefined | StorageLocationDefaultArgs> = $Result.GetResult<Prisma.$StorageLocationPayload, S>

  type StorageLocationCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<StorageLocationFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: StorageLocationCountAggregateInputType | true
    }

  export interface StorageLocationDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['StorageLocation'], meta: { name: 'StorageLocation' } }
    /**
     * Find zero or one StorageLocation that matches the filter.
     * @param {StorageLocationFindUniqueArgs} args - Arguments to find a StorageLocation
     * @example
     * // Get one StorageLocation
     * const storageLocation = await prisma.storageLocation.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends StorageLocationFindUniqueArgs>(args: SelectSubset<T, StorageLocationFindUniqueArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one StorageLocation that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {StorageLocationFindUniqueOrThrowArgs} args - Arguments to find a StorageLocation
     * @example
     * // Get one StorageLocation
     * const storageLocation = await prisma.storageLocation.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends StorageLocationFindUniqueOrThrowArgs>(args: SelectSubset<T, StorageLocationFindUniqueOrThrowArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first StorageLocation that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationFindFirstArgs} args - Arguments to find a StorageLocation
     * @example
     * // Get one StorageLocation
     * const storageLocation = await prisma.storageLocation.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends StorageLocationFindFirstArgs>(args?: SelectSubset<T, StorageLocationFindFirstArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first StorageLocation that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationFindFirstOrThrowArgs} args - Arguments to find a StorageLocation
     * @example
     * // Get one StorageLocation
     * const storageLocation = await prisma.storageLocation.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends StorageLocationFindFirstOrThrowArgs>(args?: SelectSubset<T, StorageLocationFindFirstOrThrowArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more StorageLocations that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all StorageLocations
     * const storageLocations = await prisma.storageLocation.findMany()
     * 
     * // Get first 10 StorageLocations
     * const storageLocations = await prisma.storageLocation.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const storageLocationWithIdOnly = await prisma.storageLocation.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends StorageLocationFindManyArgs>(args?: SelectSubset<T, StorageLocationFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a StorageLocation.
     * @param {StorageLocationCreateArgs} args - Arguments to create a StorageLocation.
     * @example
     * // Create one StorageLocation
     * const StorageLocation = await prisma.storageLocation.create({
     *   data: {
     *     // ... data to create a StorageLocation
     *   }
     * })
     * 
     */
    create<T extends StorageLocationCreateArgs>(args: SelectSubset<T, StorageLocationCreateArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many StorageLocations.
     * @param {StorageLocationCreateManyArgs} args - Arguments to create many StorageLocations.
     * @example
     * // Create many StorageLocations
     * const storageLocation = await prisma.storageLocation.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends StorageLocationCreateManyArgs>(args?: SelectSubset<T, StorageLocationCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many StorageLocations and returns the data saved in the database.
     * @param {StorageLocationCreateManyAndReturnArgs} args - Arguments to create many StorageLocations.
     * @example
     * // Create many StorageLocations
     * const storageLocation = await prisma.storageLocation.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many StorageLocations and only return the `id`
     * const storageLocationWithIdOnly = await prisma.storageLocation.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends StorageLocationCreateManyAndReturnArgs>(args?: SelectSubset<T, StorageLocationCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a StorageLocation.
     * @param {StorageLocationDeleteArgs} args - Arguments to delete one StorageLocation.
     * @example
     * // Delete one StorageLocation
     * const StorageLocation = await prisma.storageLocation.delete({
     *   where: {
     *     // ... filter to delete one StorageLocation
     *   }
     * })
     * 
     */
    delete<T extends StorageLocationDeleteArgs>(args: SelectSubset<T, StorageLocationDeleteArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one StorageLocation.
     * @param {StorageLocationUpdateArgs} args - Arguments to update one StorageLocation.
     * @example
     * // Update one StorageLocation
     * const storageLocation = await prisma.storageLocation.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends StorageLocationUpdateArgs>(args: SelectSubset<T, StorageLocationUpdateArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more StorageLocations.
     * @param {StorageLocationDeleteManyArgs} args - Arguments to filter StorageLocations to delete.
     * @example
     * // Delete a few StorageLocations
     * const { count } = await prisma.storageLocation.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends StorageLocationDeleteManyArgs>(args?: SelectSubset<T, StorageLocationDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more StorageLocations.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many StorageLocations
     * const storageLocation = await prisma.storageLocation.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends StorageLocationUpdateManyArgs>(args: SelectSubset<T, StorageLocationUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one StorageLocation.
     * @param {StorageLocationUpsertArgs} args - Arguments to update or create a StorageLocation.
     * @example
     * // Update or create a StorageLocation
     * const storageLocation = await prisma.storageLocation.upsert({
     *   create: {
     *     // ... data to create a StorageLocation
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the StorageLocation we want to update
     *   }
     * })
     */
    upsert<T extends StorageLocationUpsertArgs>(args: SelectSubset<T, StorageLocationUpsertArgs<ExtArgs>>): Prisma__StorageLocationClient<$Result.GetResult<Prisma.$StorageLocationPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of StorageLocations.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationCountArgs} args - Arguments to filter StorageLocations to count.
     * @example
     * // Count the number of StorageLocations
     * const count = await prisma.storageLocation.count({
     *   where: {
     *     // ... the filter for the StorageLocations we want to count
     *   }
     * })
    **/
    count<T extends StorageLocationCountArgs>(
      args?: Subset<T, StorageLocationCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], StorageLocationCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a StorageLocation.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends StorageLocationAggregateArgs>(args: Subset<T, StorageLocationAggregateArgs>): Prisma.PrismaPromise<GetStorageLocationAggregateType<T>>

    /**
     * Group by StorageLocation.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StorageLocationGroupByArgs} args - Group by arguments.
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
      T extends StorageLocationGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: StorageLocationGroupByArgs['orderBy'] }
        : { orderBy?: StorageLocationGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, StorageLocationGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetStorageLocationGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the StorageLocation model
   */
  readonly fields: StorageLocationFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for StorageLocation.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__StorageLocationClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    zone<T extends ZoneDefaultArgs<ExtArgs> = {}>(args?: Subset<T, ZoneDefaultArgs<ExtArgs>>): Prisma__ZoneClient<$Result.GetResult<Prisma.$ZonePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
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
   * Fields of the StorageLocation model
   */ 
  interface StorageLocationFieldRefs {
    readonly id: FieldRef<"StorageLocation", 'String'>
    readonly zoneId: FieldRef<"StorageLocation", 'String'>
    readonly aisle: FieldRef<"StorageLocation", 'String'>
    readonly shelf: FieldRef<"StorageLocation", 'String'>
    readonly bin: FieldRef<"StorageLocation", 'String'>
    readonly locationCode: FieldRef<"StorageLocation", 'String'>
    readonly capacity: FieldRef<"StorageLocation", 'Float'>
    readonly isOccupied: FieldRef<"StorageLocation", 'Boolean'>
    readonly currentItemId: FieldRef<"StorageLocation", 'String'>
    readonly currentQty: FieldRef<"StorageLocation", 'Float'>
    readonly createdAt: FieldRef<"StorageLocation", 'DateTime'>
    readonly updatedAt: FieldRef<"StorageLocation", 'DateTime'>
  }
    

  // Custom InputTypes
  /**
   * StorageLocation findUnique
   */
  export type StorageLocationFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * Filter, which StorageLocation to fetch.
     */
    where: StorageLocationWhereUniqueInput
  }

  /**
   * StorageLocation findUniqueOrThrow
   */
  export type StorageLocationFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * Filter, which StorageLocation to fetch.
     */
    where: StorageLocationWhereUniqueInput
  }

  /**
   * StorageLocation findFirst
   */
  export type StorageLocationFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * Filter, which StorageLocation to fetch.
     */
    where?: StorageLocationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StorageLocations to fetch.
     */
    orderBy?: StorageLocationOrderByWithRelationInput | StorageLocationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for StorageLocations.
     */
    cursor?: StorageLocationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StorageLocations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StorageLocations.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of StorageLocations.
     */
    distinct?: StorageLocationScalarFieldEnum | StorageLocationScalarFieldEnum[]
  }

  /**
   * StorageLocation findFirstOrThrow
   */
  export type StorageLocationFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * Filter, which StorageLocation to fetch.
     */
    where?: StorageLocationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StorageLocations to fetch.
     */
    orderBy?: StorageLocationOrderByWithRelationInput | StorageLocationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for StorageLocations.
     */
    cursor?: StorageLocationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StorageLocations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StorageLocations.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of StorageLocations.
     */
    distinct?: StorageLocationScalarFieldEnum | StorageLocationScalarFieldEnum[]
  }

  /**
   * StorageLocation findMany
   */
  export type StorageLocationFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * Filter, which StorageLocations to fetch.
     */
    where?: StorageLocationWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StorageLocations to fetch.
     */
    orderBy?: StorageLocationOrderByWithRelationInput | StorageLocationOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing StorageLocations.
     */
    cursor?: StorageLocationWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StorageLocations from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StorageLocations.
     */
    skip?: number
    distinct?: StorageLocationScalarFieldEnum | StorageLocationScalarFieldEnum[]
  }

  /**
   * StorageLocation create
   */
  export type StorageLocationCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * The data needed to create a StorageLocation.
     */
    data: XOR<StorageLocationCreateInput, StorageLocationUncheckedCreateInput>
  }

  /**
   * StorageLocation createMany
   */
  export type StorageLocationCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many StorageLocations.
     */
    data: StorageLocationCreateManyInput | StorageLocationCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * StorageLocation createManyAndReturn
   */
  export type StorageLocationCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many StorageLocations.
     */
    data: StorageLocationCreateManyInput | StorageLocationCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * StorageLocation update
   */
  export type StorageLocationUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * The data needed to update a StorageLocation.
     */
    data: XOR<StorageLocationUpdateInput, StorageLocationUncheckedUpdateInput>
    /**
     * Choose, which StorageLocation to update.
     */
    where: StorageLocationWhereUniqueInput
  }

  /**
   * StorageLocation updateMany
   */
  export type StorageLocationUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update StorageLocations.
     */
    data: XOR<StorageLocationUpdateManyMutationInput, StorageLocationUncheckedUpdateManyInput>
    /**
     * Filter which StorageLocations to update
     */
    where?: StorageLocationWhereInput
  }

  /**
   * StorageLocation upsert
   */
  export type StorageLocationUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * The filter to search for the StorageLocation to update in case it exists.
     */
    where: StorageLocationWhereUniqueInput
    /**
     * In case the StorageLocation found by the `where` argument doesn't exist, create a new StorageLocation with this data.
     */
    create: XOR<StorageLocationCreateInput, StorageLocationUncheckedCreateInput>
    /**
     * In case the StorageLocation was found with the provided `where` argument, update it with this data.
     */
    update: XOR<StorageLocationUpdateInput, StorageLocationUncheckedUpdateInput>
  }

  /**
   * StorageLocation delete
   */
  export type StorageLocationDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
    /**
     * Filter which StorageLocation to delete.
     */
    where: StorageLocationWhereUniqueInput
  }

  /**
   * StorageLocation deleteMany
   */
  export type StorageLocationDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which StorageLocations to delete
     */
    where?: StorageLocationWhereInput
  }

  /**
   * StorageLocation without action
   */
  export type StorageLocationDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StorageLocation
     */
    select?: StorageLocationSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StorageLocationInclude<ExtArgs> | null
  }


  /**
   * Model StockTransfer
   */

  export type AggregateStockTransfer = {
    _count: StockTransferCountAggregateOutputType | null
    _avg: StockTransferAvgAggregateOutputType | null
    _sum: StockTransferSumAggregateOutputType | null
    _min: StockTransferMinAggregateOutputType | null
    _max: StockTransferMaxAggregateOutputType | null
  }

  export type StockTransferAvgAggregateOutputType = {
    quantity: number | null
    unitCost: number | null
    totalCost: number | null
  }

  export type StockTransferSumAggregateOutputType = {
    quantity: number | null
    unitCost: number | null
    totalCost: number | null
  }

  export type StockTransferMinAggregateOutputType = {
    id: string | null
    itemId: string | null
    fromWarehouseId: string | null
    toWarehouseId: string | null
    quantity: number | null
    unitCost: number | null
    totalCost: number | null
    transferType: $Enums.TransferType | null
    status: $Enums.TransferStatus | null
    requestedBy: string | null
    approvedBy: string | null
    performedBy: string | null
    requestedAt: Date | null
    approvedAt: Date | null
    completedAt: Date | null
    notes: string | null
  }

  export type StockTransferMaxAggregateOutputType = {
    id: string | null
    itemId: string | null
    fromWarehouseId: string | null
    toWarehouseId: string | null
    quantity: number | null
    unitCost: number | null
    totalCost: number | null
    transferType: $Enums.TransferType | null
    status: $Enums.TransferStatus | null
    requestedBy: string | null
    approvedBy: string | null
    performedBy: string | null
    requestedAt: Date | null
    approvedAt: Date | null
    completedAt: Date | null
    notes: string | null
  }

  export type StockTransferCountAggregateOutputType = {
    id: number
    itemId: number
    fromWarehouseId: number
    toWarehouseId: number
    quantity: number
    unitCost: number
    totalCost: number
    transferType: number
    status: number
    requestedBy: number
    approvedBy: number
    performedBy: number
    requestedAt: number
    approvedAt: number
    completedAt: number
    notes: number
    _all: number
  }


  export type StockTransferAvgAggregateInputType = {
    quantity?: true
    unitCost?: true
    totalCost?: true
  }

  export type StockTransferSumAggregateInputType = {
    quantity?: true
    unitCost?: true
    totalCost?: true
  }

  export type StockTransferMinAggregateInputType = {
    id?: true
    itemId?: true
    fromWarehouseId?: true
    toWarehouseId?: true
    quantity?: true
    unitCost?: true
    totalCost?: true
    transferType?: true
    status?: true
    requestedBy?: true
    approvedBy?: true
    performedBy?: true
    requestedAt?: true
    approvedAt?: true
    completedAt?: true
    notes?: true
  }

  export type StockTransferMaxAggregateInputType = {
    id?: true
    itemId?: true
    fromWarehouseId?: true
    toWarehouseId?: true
    quantity?: true
    unitCost?: true
    totalCost?: true
    transferType?: true
    status?: true
    requestedBy?: true
    approvedBy?: true
    performedBy?: true
    requestedAt?: true
    approvedAt?: true
    completedAt?: true
    notes?: true
  }

  export type StockTransferCountAggregateInputType = {
    id?: true
    itemId?: true
    fromWarehouseId?: true
    toWarehouseId?: true
    quantity?: true
    unitCost?: true
    totalCost?: true
    transferType?: true
    status?: true
    requestedBy?: true
    approvedBy?: true
    performedBy?: true
    requestedAt?: true
    approvedAt?: true
    completedAt?: true
    notes?: true
    _all?: true
  }

  export type StockTransferAggregateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which StockTransfer to aggregate.
     */
    where?: StockTransferWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StockTransfers to fetch.
     */
    orderBy?: StockTransferOrderByWithRelationInput | StockTransferOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the start position
     */
    cursor?: StockTransferWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StockTransfers from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StockTransfers.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Count returned StockTransfers
    **/
    _count?: true | StockTransferCountAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to average
    **/
    _avg?: StockTransferAvgAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to sum
    **/
    _sum?: StockTransferSumAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the minimum value
    **/
    _min?: StockTransferMinAggregateInputType
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/aggregations Aggregation Docs}
     * 
     * Select which fields to find the maximum value
    **/
    _max?: StockTransferMaxAggregateInputType
  }

  export type GetStockTransferAggregateType<T extends StockTransferAggregateArgs> = {
        [P in keyof T & keyof AggregateStockTransfer]: P extends '_count' | 'count'
      ? T[P] extends true
        ? number
        : GetScalarType<T[P], AggregateStockTransfer[P]>
      : GetScalarType<T[P], AggregateStockTransfer[P]>
  }




  export type StockTransferGroupByArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    where?: StockTransferWhereInput
    orderBy?: StockTransferOrderByWithAggregationInput | StockTransferOrderByWithAggregationInput[]
    by: StockTransferScalarFieldEnum[] | StockTransferScalarFieldEnum
    having?: StockTransferScalarWhereWithAggregatesInput
    take?: number
    skip?: number
    _count?: StockTransferCountAggregateInputType | true
    _avg?: StockTransferAvgAggregateInputType
    _sum?: StockTransferSumAggregateInputType
    _min?: StockTransferMinAggregateInputType
    _max?: StockTransferMaxAggregateInputType
  }

  export type StockTransferGroupByOutputType = {
    id: string
    itemId: string
    fromWarehouseId: string | null
    toWarehouseId: string
    quantity: number
    unitCost: number | null
    totalCost: number | null
    transferType: $Enums.TransferType
    status: $Enums.TransferStatus
    requestedBy: string
    approvedBy: string | null
    performedBy: string | null
    requestedAt: Date
    approvedAt: Date | null
    completedAt: Date | null
    notes: string | null
    _count: StockTransferCountAggregateOutputType | null
    _avg: StockTransferAvgAggregateOutputType | null
    _sum: StockTransferSumAggregateOutputType | null
    _min: StockTransferMinAggregateOutputType | null
    _max: StockTransferMaxAggregateOutputType | null
  }

  type GetStockTransferGroupByPayload<T extends StockTransferGroupByArgs> = Prisma.PrismaPromise<
    Array<
      PickEnumerable<StockTransferGroupByOutputType, T['by']> &
        {
          [P in ((keyof T) & (keyof StockTransferGroupByOutputType))]: P extends '_count'
            ? T[P] extends boolean
              ? number
              : GetScalarType<T[P], StockTransferGroupByOutputType[P]>
            : GetScalarType<T[P], StockTransferGroupByOutputType[P]>
        }
      >
    >


  export type StockTransferSelect<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    itemId?: boolean
    fromWarehouseId?: boolean
    toWarehouseId?: boolean
    quantity?: boolean
    unitCost?: boolean
    totalCost?: boolean
    transferType?: boolean
    status?: boolean
    requestedBy?: boolean
    approvedBy?: boolean
    performedBy?: boolean
    requestedAt?: boolean
    approvedAt?: boolean
    completedAt?: boolean
    notes?: boolean
    fromWarehouse?: boolean | StockTransfer$fromWarehouseArgs<ExtArgs>
    toWarehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["stockTransfer"]>

  export type StockTransferSelectCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = $Extensions.GetSelect<{
    id?: boolean
    itemId?: boolean
    fromWarehouseId?: boolean
    toWarehouseId?: boolean
    quantity?: boolean
    unitCost?: boolean
    totalCost?: boolean
    transferType?: boolean
    status?: boolean
    requestedBy?: boolean
    approvedBy?: boolean
    performedBy?: boolean
    requestedAt?: boolean
    approvedAt?: boolean
    completedAt?: boolean
    notes?: boolean
    fromWarehouse?: boolean | StockTransfer$fromWarehouseArgs<ExtArgs>
    toWarehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
  }, ExtArgs["result"]["stockTransfer"]>

  export type StockTransferSelectScalar = {
    id?: boolean
    itemId?: boolean
    fromWarehouseId?: boolean
    toWarehouseId?: boolean
    quantity?: boolean
    unitCost?: boolean
    totalCost?: boolean
    transferType?: boolean
    status?: boolean
    requestedBy?: boolean
    approvedBy?: boolean
    performedBy?: boolean
    requestedAt?: boolean
    approvedAt?: boolean
    completedAt?: boolean
    notes?: boolean
  }

  export type StockTransferInclude<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    fromWarehouse?: boolean | StockTransfer$fromWarehouseArgs<ExtArgs>
    toWarehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
  }
  export type StockTransferIncludeCreateManyAndReturn<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    fromWarehouse?: boolean | StockTransfer$fromWarehouseArgs<ExtArgs>
    toWarehouse?: boolean | WarehouseDefaultArgs<ExtArgs>
  }

  export type $StockTransferPayload<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    name: "StockTransfer"
    objects: {
      fromWarehouse: Prisma.$WarehousePayload<ExtArgs> | null
      toWarehouse: Prisma.$WarehousePayload<ExtArgs>
    }
    scalars: $Extensions.GetPayloadResult<{
      id: string
      itemId: string
      fromWarehouseId: string | null
      toWarehouseId: string
      quantity: number
      unitCost: number | null
      totalCost: number | null
      transferType: $Enums.TransferType
      status: $Enums.TransferStatus
      requestedBy: string
      approvedBy: string | null
      performedBy: string | null
      requestedAt: Date
      approvedAt: Date | null
      completedAt: Date | null
      notes: string | null
    }, ExtArgs["result"]["stockTransfer"]>
    composites: {}
  }

  type StockTransferGetPayload<S extends boolean | null | undefined | StockTransferDefaultArgs> = $Result.GetResult<Prisma.$StockTransferPayload, S>

  type StockTransferCountArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = 
    Omit<StockTransferFindManyArgs, 'select' | 'include' | 'distinct'> & {
      select?: StockTransferCountAggregateInputType | true
    }

  export interface StockTransferDelegate<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> {
    [K: symbol]: { types: Prisma.TypeMap<ExtArgs>['model']['StockTransfer'], meta: { name: 'StockTransfer' } }
    /**
     * Find zero or one StockTransfer that matches the filter.
     * @param {StockTransferFindUniqueArgs} args - Arguments to find a StockTransfer
     * @example
     * // Get one StockTransfer
     * const stockTransfer = await prisma.stockTransfer.findUnique({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUnique<T extends StockTransferFindUniqueArgs>(args: SelectSubset<T, StockTransferFindUniqueArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findUnique"> | null, null, ExtArgs>

    /**
     * Find one StockTransfer that matches the filter or throw an error with `error.code='P2025'` 
     * if no matches were found.
     * @param {StockTransferFindUniqueOrThrowArgs} args - Arguments to find a StockTransfer
     * @example
     * // Get one StockTransfer
     * const stockTransfer = await prisma.stockTransfer.findUniqueOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findUniqueOrThrow<T extends StockTransferFindUniqueOrThrowArgs>(args: SelectSubset<T, StockTransferFindUniqueOrThrowArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findUniqueOrThrow">, never, ExtArgs>

    /**
     * Find the first StockTransfer that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferFindFirstArgs} args - Arguments to find a StockTransfer
     * @example
     * // Get one StockTransfer
     * const stockTransfer = await prisma.stockTransfer.findFirst({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirst<T extends StockTransferFindFirstArgs>(args?: SelectSubset<T, StockTransferFindFirstArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findFirst"> | null, null, ExtArgs>

    /**
     * Find the first StockTransfer that matches the filter or
     * throw `PrismaKnownClientError` with `P2025` code if no matches were found.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferFindFirstOrThrowArgs} args - Arguments to find a StockTransfer
     * @example
     * // Get one StockTransfer
     * const stockTransfer = await prisma.stockTransfer.findFirstOrThrow({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     */
    findFirstOrThrow<T extends StockTransferFindFirstOrThrowArgs>(args?: SelectSubset<T, StockTransferFindFirstOrThrowArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findFirstOrThrow">, never, ExtArgs>

    /**
     * Find zero or more StockTransfers that matches the filter.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferFindManyArgs} args - Arguments to filter and select certain fields only.
     * @example
     * // Get all StockTransfers
     * const stockTransfers = await prisma.stockTransfer.findMany()
     * 
     * // Get first 10 StockTransfers
     * const stockTransfers = await prisma.stockTransfer.findMany({ take: 10 })
     * 
     * // Only select the `id`
     * const stockTransferWithIdOnly = await prisma.stockTransfer.findMany({ select: { id: true } })
     * 
     */
    findMany<T extends StockTransferFindManyArgs>(args?: SelectSubset<T, StockTransferFindManyArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "findMany">>

    /**
     * Create a StockTransfer.
     * @param {StockTransferCreateArgs} args - Arguments to create a StockTransfer.
     * @example
     * // Create one StockTransfer
     * const StockTransfer = await prisma.stockTransfer.create({
     *   data: {
     *     // ... data to create a StockTransfer
     *   }
     * })
     * 
     */
    create<T extends StockTransferCreateArgs>(args: SelectSubset<T, StockTransferCreateArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "create">, never, ExtArgs>

    /**
     * Create many StockTransfers.
     * @param {StockTransferCreateManyArgs} args - Arguments to create many StockTransfers.
     * @example
     * // Create many StockTransfers
     * const stockTransfer = await prisma.stockTransfer.createMany({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     *     
     */
    createMany<T extends StockTransferCreateManyArgs>(args?: SelectSubset<T, StockTransferCreateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create many StockTransfers and returns the data saved in the database.
     * @param {StockTransferCreateManyAndReturnArgs} args - Arguments to create many StockTransfers.
     * @example
     * // Create many StockTransfers
     * const stockTransfer = await prisma.stockTransfer.createManyAndReturn({
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * 
     * // Create many StockTransfers and only return the `id`
     * const stockTransferWithIdOnly = await prisma.stockTransfer.createManyAndReturn({ 
     *   select: { id: true },
     *   data: [
     *     // ... provide data here
     *   ]
     * })
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * 
     */
    createManyAndReturn<T extends StockTransferCreateManyAndReturnArgs>(args?: SelectSubset<T, StockTransferCreateManyAndReturnArgs<ExtArgs>>): Prisma.PrismaPromise<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "createManyAndReturn">>

    /**
     * Delete a StockTransfer.
     * @param {StockTransferDeleteArgs} args - Arguments to delete one StockTransfer.
     * @example
     * // Delete one StockTransfer
     * const StockTransfer = await prisma.stockTransfer.delete({
     *   where: {
     *     // ... filter to delete one StockTransfer
     *   }
     * })
     * 
     */
    delete<T extends StockTransferDeleteArgs>(args: SelectSubset<T, StockTransferDeleteArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "delete">, never, ExtArgs>

    /**
     * Update one StockTransfer.
     * @param {StockTransferUpdateArgs} args - Arguments to update one StockTransfer.
     * @example
     * // Update one StockTransfer
     * const stockTransfer = await prisma.stockTransfer.update({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    update<T extends StockTransferUpdateArgs>(args: SelectSubset<T, StockTransferUpdateArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "update">, never, ExtArgs>

    /**
     * Delete zero or more StockTransfers.
     * @param {StockTransferDeleteManyArgs} args - Arguments to filter StockTransfers to delete.
     * @example
     * // Delete a few StockTransfers
     * const { count } = await prisma.stockTransfer.deleteMany({
     *   where: {
     *     // ... provide filter here
     *   }
     * })
     * 
     */
    deleteMany<T extends StockTransferDeleteManyArgs>(args?: SelectSubset<T, StockTransferDeleteManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Update zero or more StockTransfers.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferUpdateManyArgs} args - Arguments to update one or more rows.
     * @example
     * // Update many StockTransfers
     * const stockTransfer = await prisma.stockTransfer.updateMany({
     *   where: {
     *     // ... provide filter here
     *   },
     *   data: {
     *     // ... provide data here
     *   }
     * })
     * 
     */
    updateMany<T extends StockTransferUpdateManyArgs>(args: SelectSubset<T, StockTransferUpdateManyArgs<ExtArgs>>): Prisma.PrismaPromise<BatchPayload>

    /**
     * Create or update one StockTransfer.
     * @param {StockTransferUpsertArgs} args - Arguments to update or create a StockTransfer.
     * @example
     * // Update or create a StockTransfer
     * const stockTransfer = await prisma.stockTransfer.upsert({
     *   create: {
     *     // ... data to create a StockTransfer
     *   },
     *   update: {
     *     // ... in case it already exists, update
     *   },
     *   where: {
     *     // ... the filter for the StockTransfer we want to update
     *   }
     * })
     */
    upsert<T extends StockTransferUpsertArgs>(args: SelectSubset<T, StockTransferUpsertArgs<ExtArgs>>): Prisma__StockTransferClient<$Result.GetResult<Prisma.$StockTransferPayload<ExtArgs>, T, "upsert">, never, ExtArgs>


    /**
     * Count the number of StockTransfers.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferCountArgs} args - Arguments to filter StockTransfers to count.
     * @example
     * // Count the number of StockTransfers
     * const count = await prisma.stockTransfer.count({
     *   where: {
     *     // ... the filter for the StockTransfers we want to count
     *   }
     * })
    **/
    count<T extends StockTransferCountArgs>(
      args?: Subset<T, StockTransferCountArgs>,
    ): Prisma.PrismaPromise<
      T extends $Utils.Record<'select', any>
        ? T['select'] extends true
          ? number
          : GetScalarType<T['select'], StockTransferCountAggregateOutputType>
        : number
    >

    /**
     * Allows you to perform aggregations operations on a StockTransfer.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferAggregateArgs} args - Select which aggregations you would like to apply and on what fields.
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
    aggregate<T extends StockTransferAggregateArgs>(args: Subset<T, StockTransferAggregateArgs>): Prisma.PrismaPromise<GetStockTransferAggregateType<T>>

    /**
     * Group by StockTransfer.
     * Note, that providing `undefined` is treated as the value not being there.
     * Read more here: https://pris.ly/d/null-undefined
     * @param {StockTransferGroupByArgs} args - Group by arguments.
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
      T extends StockTransferGroupByArgs,
      HasSelectOrTake extends Or<
        Extends<'skip', Keys<T>>,
        Extends<'take', Keys<T>>
      >,
      OrderByArg extends True extends HasSelectOrTake
        ? { orderBy: StockTransferGroupByArgs['orderBy'] }
        : { orderBy?: StockTransferGroupByArgs['orderBy'] },
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
    >(args: SubsetIntersection<T, StockTransferGroupByArgs, OrderByArg> & InputErrors): {} extends InputErrors ? GetStockTransferGroupByPayload<T> : Prisma.PrismaPromise<InputErrors>
  /**
   * Fields of the StockTransfer model
   */
  readonly fields: StockTransferFieldRefs;
  }

  /**
   * The delegate class that acts as a "Promise-like" for StockTransfer.
   * Why is this prefixed with `Prisma__`?
   * Because we want to prevent naming conflicts as mentioned in
   * https://github.com/prisma/prisma-client-js/issues/707
   */
  export interface Prisma__StockTransferClient<T, Null = never, ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> extends Prisma.PrismaPromise<T> {
    readonly [Symbol.toStringTag]: "PrismaPromise"
    fromWarehouse<T extends StockTransfer$fromWarehouseArgs<ExtArgs> = {}>(args?: Subset<T, StockTransfer$fromWarehouseArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findUniqueOrThrow"> | null, null, ExtArgs>
    toWarehouse<T extends WarehouseDefaultArgs<ExtArgs> = {}>(args?: Subset<T, WarehouseDefaultArgs<ExtArgs>>): Prisma__WarehouseClient<$Result.GetResult<Prisma.$WarehousePayload<ExtArgs>, T, "findUniqueOrThrow"> | Null, Null, ExtArgs>
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
   * Fields of the StockTransfer model
   */ 
  interface StockTransferFieldRefs {
    readonly id: FieldRef<"StockTransfer", 'String'>
    readonly itemId: FieldRef<"StockTransfer", 'String'>
    readonly fromWarehouseId: FieldRef<"StockTransfer", 'String'>
    readonly toWarehouseId: FieldRef<"StockTransfer", 'String'>
    readonly quantity: FieldRef<"StockTransfer", 'Float'>
    readonly unitCost: FieldRef<"StockTransfer", 'Float'>
    readonly totalCost: FieldRef<"StockTransfer", 'Float'>
    readonly transferType: FieldRef<"StockTransfer", 'TransferType'>
    readonly status: FieldRef<"StockTransfer", 'TransferStatus'>
    readonly requestedBy: FieldRef<"StockTransfer", 'String'>
    readonly approvedBy: FieldRef<"StockTransfer", 'String'>
    readonly performedBy: FieldRef<"StockTransfer", 'String'>
    readonly requestedAt: FieldRef<"StockTransfer", 'DateTime'>
    readonly approvedAt: FieldRef<"StockTransfer", 'DateTime'>
    readonly completedAt: FieldRef<"StockTransfer", 'DateTime'>
    readonly notes: FieldRef<"StockTransfer", 'String'>
  }
    

  // Custom InputTypes
  /**
   * StockTransfer findUnique
   */
  export type StockTransferFindUniqueArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * Filter, which StockTransfer to fetch.
     */
    where: StockTransferWhereUniqueInput
  }

  /**
   * StockTransfer findUniqueOrThrow
   */
  export type StockTransferFindUniqueOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * Filter, which StockTransfer to fetch.
     */
    where: StockTransferWhereUniqueInput
  }

  /**
   * StockTransfer findFirst
   */
  export type StockTransferFindFirstArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * Filter, which StockTransfer to fetch.
     */
    where?: StockTransferWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StockTransfers to fetch.
     */
    orderBy?: StockTransferOrderByWithRelationInput | StockTransferOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for StockTransfers.
     */
    cursor?: StockTransferWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StockTransfers from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StockTransfers.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of StockTransfers.
     */
    distinct?: StockTransferScalarFieldEnum | StockTransferScalarFieldEnum[]
  }

  /**
   * StockTransfer findFirstOrThrow
   */
  export type StockTransferFindFirstOrThrowArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * Filter, which StockTransfer to fetch.
     */
    where?: StockTransferWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StockTransfers to fetch.
     */
    orderBy?: StockTransferOrderByWithRelationInput | StockTransferOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for searching for StockTransfers.
     */
    cursor?: StockTransferWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StockTransfers from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StockTransfers.
     */
    skip?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/distinct Distinct Docs}
     * 
     * Filter by unique combinations of StockTransfers.
     */
    distinct?: StockTransferScalarFieldEnum | StockTransferScalarFieldEnum[]
  }

  /**
   * StockTransfer findMany
   */
  export type StockTransferFindManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * Filter, which StockTransfers to fetch.
     */
    where?: StockTransferWhereInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/sorting Sorting Docs}
     * 
     * Determine the order of StockTransfers to fetch.
     */
    orderBy?: StockTransferOrderByWithRelationInput | StockTransferOrderByWithRelationInput[]
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination#cursor-based-pagination Cursor Docs}
     * 
     * Sets the position for listing StockTransfers.
     */
    cursor?: StockTransferWhereUniqueInput
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Take `±n` StockTransfers from the position of the cursor.
     */
    take?: number
    /**
     * {@link https://www.prisma.io/docs/concepts/components/prisma-client/pagination Pagination Docs}
     * 
     * Skip the first `n` StockTransfers.
     */
    skip?: number
    distinct?: StockTransferScalarFieldEnum | StockTransferScalarFieldEnum[]
  }

  /**
   * StockTransfer create
   */
  export type StockTransferCreateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * The data needed to create a StockTransfer.
     */
    data: XOR<StockTransferCreateInput, StockTransferUncheckedCreateInput>
  }

  /**
   * StockTransfer createMany
   */
  export type StockTransferCreateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to create many StockTransfers.
     */
    data: StockTransferCreateManyInput | StockTransferCreateManyInput[]
    skipDuplicates?: boolean
  }

  /**
   * StockTransfer createManyAndReturn
   */
  export type StockTransferCreateManyAndReturnArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelectCreateManyAndReturn<ExtArgs> | null
    /**
     * The data used to create many StockTransfers.
     */
    data: StockTransferCreateManyInput | StockTransferCreateManyInput[]
    skipDuplicates?: boolean
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferIncludeCreateManyAndReturn<ExtArgs> | null
  }

  /**
   * StockTransfer update
   */
  export type StockTransferUpdateArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * The data needed to update a StockTransfer.
     */
    data: XOR<StockTransferUpdateInput, StockTransferUncheckedUpdateInput>
    /**
     * Choose, which StockTransfer to update.
     */
    where: StockTransferWhereUniqueInput
  }

  /**
   * StockTransfer updateMany
   */
  export type StockTransferUpdateManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * The data used to update StockTransfers.
     */
    data: XOR<StockTransferUpdateManyMutationInput, StockTransferUncheckedUpdateManyInput>
    /**
     * Filter which StockTransfers to update
     */
    where?: StockTransferWhereInput
  }

  /**
   * StockTransfer upsert
   */
  export type StockTransferUpsertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * The filter to search for the StockTransfer to update in case it exists.
     */
    where: StockTransferWhereUniqueInput
    /**
     * In case the StockTransfer found by the `where` argument doesn't exist, create a new StockTransfer with this data.
     */
    create: XOR<StockTransferCreateInput, StockTransferUncheckedCreateInput>
    /**
     * In case the StockTransfer was found with the provided `where` argument, update it with this data.
     */
    update: XOR<StockTransferUpdateInput, StockTransferUncheckedUpdateInput>
  }

  /**
   * StockTransfer delete
   */
  export type StockTransferDeleteArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
    /**
     * Filter which StockTransfer to delete.
     */
    where: StockTransferWhereUniqueInput
  }

  /**
   * StockTransfer deleteMany
   */
  export type StockTransferDeleteManyArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Filter which StockTransfers to delete
     */
    where?: StockTransferWhereInput
  }

  /**
   * StockTransfer.fromWarehouse
   */
  export type StockTransfer$fromWarehouseArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the Warehouse
     */
    select?: WarehouseSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: WarehouseInclude<ExtArgs> | null
    where?: WarehouseWhereInput
  }

  /**
   * StockTransfer without action
   */
  export type StockTransferDefaultArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = {
    /**
     * Select specific fields to fetch from the StockTransfer
     */
    select?: StockTransferSelect<ExtArgs> | null
    /**
     * Choose, which related nodes to fetch as well
     */
    include?: StockTransferInclude<ExtArgs> | null
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


  export const InventoryItemScalarFieldEnum: {
    id: 'id',
    tenantId: 'tenantId',
    name: 'name',
    nameAr: 'nameAr',
    sku: 'sku',
    category: 'category',
    description: 'description',
    descriptionAr: 'descriptionAr',
    quantity: 'quantity',
    unit: 'unit',
    reorderLevel: 'reorderLevel',
    reorderPoint: 'reorderPoint',
    maxStock: 'maxStock',
    unitCost: 'unitCost',
    sellingPrice: 'sellingPrice',
    location: 'location',
    batchNumber: 'batchNumber',
    expiryDate: 'expiryDate',
    minTemperature: 'minTemperature',
    maxTemperature: 'maxTemperature',
    minHumidity: 'minHumidity',
    maxHumidity: 'maxHumidity',
    supplier: 'supplier',
    barcode: 'barcode',
    imageUrl: 'imageUrl',
    notes: 'notes',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt',
    lastRestocked: 'lastRestocked'
  };

  export type InventoryItemScalarFieldEnum = (typeof InventoryItemScalarFieldEnum)[keyof typeof InventoryItemScalarFieldEnum]


  export const InventoryMovementScalarFieldEnum: {
    id: 'id',
    itemId: 'itemId',
    tenantId: 'tenantId',
    type: 'type',
    quantity: 'quantity',
    unitCost: 'unitCost',
    referenceId: 'referenceId',
    referenceType: 'referenceType',
    fromLocation: 'fromLocation',
    toLocation: 'toLocation',
    notes: 'notes',
    notesAr: 'notesAr',
    performedBy: 'performedBy',
    createdAt: 'createdAt'
  };

  export type InventoryMovementScalarFieldEnum = (typeof InventoryMovementScalarFieldEnum)[keyof typeof InventoryMovementScalarFieldEnum]


  export const InventoryAlertScalarFieldEnum: {
    id: 'id',
    alertType: 'alertType',
    priority: 'priority',
    status: 'status',
    itemId: 'itemId',
    itemName: 'itemName',
    itemNameAr: 'itemNameAr',
    titleEn: 'titleEn',
    titleAr: 'titleAr',
    messageEn: 'messageEn',
    messageAr: 'messageAr',
    currentValue: 'currentValue',
    thresholdValue: 'thresholdValue',
    recommendedActionEn: 'recommendedActionEn',
    recommendedActionAr: 'recommendedActionAr',
    actionUrl: 'actionUrl',
    createdAt: 'createdAt',
    acknowledgedAt: 'acknowledgedAt',
    acknowledgedBy: 'acknowledgedBy',
    resolvedAt: 'resolvedAt',
    resolvedBy: 'resolvedBy',
    resolutionNotes: 'resolutionNotes',
    snoozeUntil: 'snoozeUntil'
  };

  export type InventoryAlertScalarFieldEnum = (typeof InventoryAlertScalarFieldEnum)[keyof typeof InventoryAlertScalarFieldEnum]


  export const AlertSettingsScalarFieldEnum: {
    id: 'id',
    tenantId: 'tenantId',
    expiryWarningDays: 'expiryWarningDays',
    expiryCriticalDays: 'expiryCriticalDays',
    defaultReorderLevel: 'defaultReorderLevel',
    enableEmailAlerts: 'enableEmailAlerts',
    enablePushAlerts: 'enablePushAlerts',
    enableSmsAlerts: 'enableSmsAlerts',
    alertCheckInterval: 'alertCheckInterval',
    maxAlertsPerDay: 'maxAlertsPerDay',
    autoResolveOnRestock: 'autoResolveOnRestock',
    autoResolveExpired: 'autoResolveExpired',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type AlertSettingsScalarFieldEnum = (typeof AlertSettingsScalarFieldEnum)[keyof typeof AlertSettingsScalarFieldEnum]


  export const WarehouseScalarFieldEnum: {
    id: 'id',
    name: 'name',
    nameAr: 'nameAr',
    warehouseType: 'warehouseType',
    latitude: 'latitude',
    longitude: 'longitude',
    address: 'address',
    governorate: 'governorate',
    capacityValue: 'capacityValue',
    capacityUnit: 'capacityUnit',
    currentUsage: 'currentUsage',
    storageCondition: 'storageCondition',
    tempMin: 'tempMin',
    tempMax: 'tempMax',
    humidityMin: 'humidityMin',
    humidityMax: 'humidityMax',
    isActive: 'isActive',
    managerId: 'managerId',
    managerName: 'managerName',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type WarehouseScalarFieldEnum = (typeof WarehouseScalarFieldEnum)[keyof typeof WarehouseScalarFieldEnum]


  export const ZoneScalarFieldEnum: {
    id: 'id',
    warehouseId: 'warehouseId',
    name: 'name',
    nameAr: 'nameAr',
    capacity: 'capacity',
    currentUsage: 'currentUsage',
    condition: 'condition',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type ZoneScalarFieldEnum = (typeof ZoneScalarFieldEnum)[keyof typeof ZoneScalarFieldEnum]


  export const StorageLocationScalarFieldEnum: {
    id: 'id',
    zoneId: 'zoneId',
    aisle: 'aisle',
    shelf: 'shelf',
    bin: 'bin',
    locationCode: 'locationCode',
    capacity: 'capacity',
    isOccupied: 'isOccupied',
    currentItemId: 'currentItemId',
    currentQty: 'currentQty',
    createdAt: 'createdAt',
    updatedAt: 'updatedAt'
  };

  export type StorageLocationScalarFieldEnum = (typeof StorageLocationScalarFieldEnum)[keyof typeof StorageLocationScalarFieldEnum]


  export const StockTransferScalarFieldEnum: {
    id: 'id',
    itemId: 'itemId',
    fromWarehouseId: 'fromWarehouseId',
    toWarehouseId: 'toWarehouseId',
    quantity: 'quantity',
    unitCost: 'unitCost',
    totalCost: 'totalCost',
    transferType: 'transferType',
    status: 'status',
    requestedBy: 'requestedBy',
    approvedBy: 'approvedBy',
    performedBy: 'performedBy',
    requestedAt: 'requestedAt',
    approvedAt: 'approvedAt',
    completedAt: 'completedAt',
    notes: 'notes'
  };

  export type StockTransferScalarFieldEnum = (typeof StockTransferScalarFieldEnum)[keyof typeof StockTransferScalarFieldEnum]


  export const SortOrder: {
    asc: 'asc',
    desc: 'desc'
  };

  export type SortOrder = (typeof SortOrder)[keyof typeof SortOrder]


  export const QueryMode: {
    default: 'default',
    insensitive: 'insensitive'
  };

  export type QueryMode = (typeof QueryMode)[keyof typeof QueryMode]


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
   * Reference to a field of type 'ItemCategory'
   */
  export type EnumItemCategoryFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'ItemCategory'>
    


  /**
   * Reference to a field of type 'ItemCategory[]'
   */
  export type ListEnumItemCategoryFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'ItemCategory[]'>
    


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
   * Reference to a field of type 'MovementType'
   */
  export type EnumMovementTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'MovementType'>
    


  /**
   * Reference to a field of type 'MovementType[]'
   */
  export type ListEnumMovementTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'MovementType[]'>
    


  /**
   * Reference to a field of type 'AlertType'
   */
  export type EnumAlertTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertType'>
    


  /**
   * Reference to a field of type 'AlertType[]'
   */
  export type ListEnumAlertTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertType[]'>
    


  /**
   * Reference to a field of type 'AlertPriority'
   */
  export type EnumAlertPriorityFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertPriority'>
    


  /**
   * Reference to a field of type 'AlertPriority[]'
   */
  export type ListEnumAlertPriorityFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertPriority[]'>
    


  /**
   * Reference to a field of type 'AlertStatus'
   */
  export type EnumAlertStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertStatus'>
    


  /**
   * Reference to a field of type 'AlertStatus[]'
   */
  export type ListEnumAlertStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'AlertStatus[]'>
    


  /**
   * Reference to a field of type 'Int'
   */
  export type IntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Int'>
    


  /**
   * Reference to a field of type 'Int[]'
   */
  export type ListIntFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Int[]'>
    


  /**
   * Reference to a field of type 'Boolean'
   */
  export type BooleanFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'Boolean'>
    


  /**
   * Reference to a field of type 'WarehouseType'
   */
  export type EnumWarehouseTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'WarehouseType'>
    


  /**
   * Reference to a field of type 'WarehouseType[]'
   */
  export type ListEnumWarehouseTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'WarehouseType[]'>
    


  /**
   * Reference to a field of type 'StorageCondition'
   */
  export type EnumStorageConditionFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'StorageCondition'>
    


  /**
   * Reference to a field of type 'StorageCondition[]'
   */
  export type ListEnumStorageConditionFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'StorageCondition[]'>
    


  /**
   * Reference to a field of type 'TransferType'
   */
  export type EnumTransferTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TransferType'>
    


  /**
   * Reference to a field of type 'TransferType[]'
   */
  export type ListEnumTransferTypeFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TransferType[]'>
    


  /**
   * Reference to a field of type 'TransferStatus'
   */
  export type EnumTransferStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TransferStatus'>
    


  /**
   * Reference to a field of type 'TransferStatus[]'
   */
  export type ListEnumTransferStatusFieldRefInput<$PrismaModel> = FieldRefInputType<$PrismaModel, 'TransferStatus[]'>
    
  /**
   * Deep Input Types
   */


  export type InventoryItemWhereInput = {
    AND?: InventoryItemWhereInput | InventoryItemWhereInput[]
    OR?: InventoryItemWhereInput[]
    NOT?: InventoryItemWhereInput | InventoryItemWhereInput[]
    id?: StringFilter<"InventoryItem"> | string
    tenantId?: StringFilter<"InventoryItem"> | string
    name?: StringFilter<"InventoryItem"> | string
    nameAr?: StringFilter<"InventoryItem"> | string
    sku?: StringNullableFilter<"InventoryItem"> | string | null
    category?: EnumItemCategoryFilter<"InventoryItem"> | $Enums.ItemCategory
    description?: StringNullableFilter<"InventoryItem"> | string | null
    descriptionAr?: StringNullableFilter<"InventoryItem"> | string | null
    quantity?: FloatFilter<"InventoryItem"> | number
    unit?: StringFilter<"InventoryItem"> | string
    reorderLevel?: FloatFilter<"InventoryItem"> | number
    reorderPoint?: FloatNullableFilter<"InventoryItem"> | number | null
    maxStock?: FloatNullableFilter<"InventoryItem"> | number | null
    unitCost?: FloatNullableFilter<"InventoryItem"> | number | null
    sellingPrice?: FloatNullableFilter<"InventoryItem"> | number | null
    location?: StringNullableFilter<"InventoryItem"> | string | null
    batchNumber?: StringNullableFilter<"InventoryItem"> | string | null
    expiryDate?: DateTimeNullableFilter<"InventoryItem"> | Date | string | null
    minTemperature?: FloatNullableFilter<"InventoryItem"> | number | null
    maxTemperature?: FloatNullableFilter<"InventoryItem"> | number | null
    minHumidity?: FloatNullableFilter<"InventoryItem"> | number | null
    maxHumidity?: FloatNullableFilter<"InventoryItem"> | number | null
    supplier?: StringNullableFilter<"InventoryItem"> | string | null
    barcode?: StringNullableFilter<"InventoryItem"> | string | null
    imageUrl?: StringNullableFilter<"InventoryItem"> | string | null
    notes?: StringNullableFilter<"InventoryItem"> | string | null
    createdAt?: DateTimeFilter<"InventoryItem"> | Date | string
    updatedAt?: DateTimeFilter<"InventoryItem"> | Date | string
    lastRestocked?: DateTimeNullableFilter<"InventoryItem"> | Date | string | null
    movements?: InventoryMovementListRelationFilter
    alerts?: InventoryAlertListRelationFilter
  }

  export type InventoryItemOrderByWithRelationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    sku?: SortOrderInput | SortOrder
    category?: SortOrder
    description?: SortOrderInput | SortOrder
    descriptionAr?: SortOrderInput | SortOrder
    quantity?: SortOrder
    unit?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrderInput | SortOrder
    maxStock?: SortOrderInput | SortOrder
    unitCost?: SortOrderInput | SortOrder
    sellingPrice?: SortOrderInput | SortOrder
    location?: SortOrderInput | SortOrder
    batchNumber?: SortOrderInput | SortOrder
    expiryDate?: SortOrderInput | SortOrder
    minTemperature?: SortOrderInput | SortOrder
    maxTemperature?: SortOrderInput | SortOrder
    minHumidity?: SortOrderInput | SortOrder
    maxHumidity?: SortOrderInput | SortOrder
    supplier?: SortOrderInput | SortOrder
    barcode?: SortOrderInput | SortOrder
    imageUrl?: SortOrderInput | SortOrder
    notes?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    lastRestocked?: SortOrderInput | SortOrder
    movements?: InventoryMovementOrderByRelationAggregateInput
    alerts?: InventoryAlertOrderByRelationAggregateInput
  }

  export type InventoryItemWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    sku?: string
    AND?: InventoryItemWhereInput | InventoryItemWhereInput[]
    OR?: InventoryItemWhereInput[]
    NOT?: InventoryItemWhereInput | InventoryItemWhereInput[]
    tenantId?: StringFilter<"InventoryItem"> | string
    name?: StringFilter<"InventoryItem"> | string
    nameAr?: StringFilter<"InventoryItem"> | string
    category?: EnumItemCategoryFilter<"InventoryItem"> | $Enums.ItemCategory
    description?: StringNullableFilter<"InventoryItem"> | string | null
    descriptionAr?: StringNullableFilter<"InventoryItem"> | string | null
    quantity?: FloatFilter<"InventoryItem"> | number
    unit?: StringFilter<"InventoryItem"> | string
    reorderLevel?: FloatFilter<"InventoryItem"> | number
    reorderPoint?: FloatNullableFilter<"InventoryItem"> | number | null
    maxStock?: FloatNullableFilter<"InventoryItem"> | number | null
    unitCost?: FloatNullableFilter<"InventoryItem"> | number | null
    sellingPrice?: FloatNullableFilter<"InventoryItem"> | number | null
    location?: StringNullableFilter<"InventoryItem"> | string | null
    batchNumber?: StringNullableFilter<"InventoryItem"> | string | null
    expiryDate?: DateTimeNullableFilter<"InventoryItem"> | Date | string | null
    minTemperature?: FloatNullableFilter<"InventoryItem"> | number | null
    maxTemperature?: FloatNullableFilter<"InventoryItem"> | number | null
    minHumidity?: FloatNullableFilter<"InventoryItem"> | number | null
    maxHumidity?: FloatNullableFilter<"InventoryItem"> | number | null
    supplier?: StringNullableFilter<"InventoryItem"> | string | null
    barcode?: StringNullableFilter<"InventoryItem"> | string | null
    imageUrl?: StringNullableFilter<"InventoryItem"> | string | null
    notes?: StringNullableFilter<"InventoryItem"> | string | null
    createdAt?: DateTimeFilter<"InventoryItem"> | Date | string
    updatedAt?: DateTimeFilter<"InventoryItem"> | Date | string
    lastRestocked?: DateTimeNullableFilter<"InventoryItem"> | Date | string | null
    movements?: InventoryMovementListRelationFilter
    alerts?: InventoryAlertListRelationFilter
  }, "id" | "sku">

  export type InventoryItemOrderByWithAggregationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    sku?: SortOrderInput | SortOrder
    category?: SortOrder
    description?: SortOrderInput | SortOrder
    descriptionAr?: SortOrderInput | SortOrder
    quantity?: SortOrder
    unit?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrderInput | SortOrder
    maxStock?: SortOrderInput | SortOrder
    unitCost?: SortOrderInput | SortOrder
    sellingPrice?: SortOrderInput | SortOrder
    location?: SortOrderInput | SortOrder
    batchNumber?: SortOrderInput | SortOrder
    expiryDate?: SortOrderInput | SortOrder
    minTemperature?: SortOrderInput | SortOrder
    maxTemperature?: SortOrderInput | SortOrder
    minHumidity?: SortOrderInput | SortOrder
    maxHumidity?: SortOrderInput | SortOrder
    supplier?: SortOrderInput | SortOrder
    barcode?: SortOrderInput | SortOrder
    imageUrl?: SortOrderInput | SortOrder
    notes?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    lastRestocked?: SortOrderInput | SortOrder
    _count?: InventoryItemCountOrderByAggregateInput
    _avg?: InventoryItemAvgOrderByAggregateInput
    _max?: InventoryItemMaxOrderByAggregateInput
    _min?: InventoryItemMinOrderByAggregateInput
    _sum?: InventoryItemSumOrderByAggregateInput
  }

  export type InventoryItemScalarWhereWithAggregatesInput = {
    AND?: InventoryItemScalarWhereWithAggregatesInput | InventoryItemScalarWhereWithAggregatesInput[]
    OR?: InventoryItemScalarWhereWithAggregatesInput[]
    NOT?: InventoryItemScalarWhereWithAggregatesInput | InventoryItemScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"InventoryItem"> | string
    tenantId?: StringWithAggregatesFilter<"InventoryItem"> | string
    name?: StringWithAggregatesFilter<"InventoryItem"> | string
    nameAr?: StringWithAggregatesFilter<"InventoryItem"> | string
    sku?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    category?: EnumItemCategoryWithAggregatesFilter<"InventoryItem"> | $Enums.ItemCategory
    description?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    descriptionAr?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    quantity?: FloatWithAggregatesFilter<"InventoryItem"> | number
    unit?: StringWithAggregatesFilter<"InventoryItem"> | string
    reorderLevel?: FloatWithAggregatesFilter<"InventoryItem"> | number
    reorderPoint?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    maxStock?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    unitCost?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    sellingPrice?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    location?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    batchNumber?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    expiryDate?: DateTimeNullableWithAggregatesFilter<"InventoryItem"> | Date | string | null
    minTemperature?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    maxTemperature?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    minHumidity?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    maxHumidity?: FloatNullableWithAggregatesFilter<"InventoryItem"> | number | null
    supplier?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    barcode?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    imageUrl?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    notes?: StringNullableWithAggregatesFilter<"InventoryItem"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"InventoryItem"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"InventoryItem"> | Date | string
    lastRestocked?: DateTimeNullableWithAggregatesFilter<"InventoryItem"> | Date | string | null
  }

  export type InventoryMovementWhereInput = {
    AND?: InventoryMovementWhereInput | InventoryMovementWhereInput[]
    OR?: InventoryMovementWhereInput[]
    NOT?: InventoryMovementWhereInput | InventoryMovementWhereInput[]
    id?: StringFilter<"InventoryMovement"> | string
    itemId?: StringFilter<"InventoryMovement"> | string
    tenantId?: StringFilter<"InventoryMovement"> | string
    type?: EnumMovementTypeFilter<"InventoryMovement"> | $Enums.MovementType
    quantity?: FloatFilter<"InventoryMovement"> | number
    unitCost?: FloatNullableFilter<"InventoryMovement"> | number | null
    referenceId?: StringNullableFilter<"InventoryMovement"> | string | null
    referenceType?: StringNullableFilter<"InventoryMovement"> | string | null
    fromLocation?: StringNullableFilter<"InventoryMovement"> | string | null
    toLocation?: StringNullableFilter<"InventoryMovement"> | string | null
    notes?: StringNullableFilter<"InventoryMovement"> | string | null
    notesAr?: StringNullableFilter<"InventoryMovement"> | string | null
    performedBy?: StringFilter<"InventoryMovement"> | string
    createdAt?: DateTimeFilter<"InventoryMovement"> | Date | string
    item?: XOR<InventoryItemRelationFilter, InventoryItemWhereInput>
  }

  export type InventoryMovementOrderByWithRelationInput = {
    id?: SortOrder
    itemId?: SortOrder
    tenantId?: SortOrder
    type?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrderInput | SortOrder
    referenceId?: SortOrderInput | SortOrder
    referenceType?: SortOrderInput | SortOrder
    fromLocation?: SortOrderInput | SortOrder
    toLocation?: SortOrderInput | SortOrder
    notes?: SortOrderInput | SortOrder
    notesAr?: SortOrderInput | SortOrder
    performedBy?: SortOrder
    createdAt?: SortOrder
    item?: InventoryItemOrderByWithRelationInput
  }

  export type InventoryMovementWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: InventoryMovementWhereInput | InventoryMovementWhereInput[]
    OR?: InventoryMovementWhereInput[]
    NOT?: InventoryMovementWhereInput | InventoryMovementWhereInput[]
    itemId?: StringFilter<"InventoryMovement"> | string
    tenantId?: StringFilter<"InventoryMovement"> | string
    type?: EnumMovementTypeFilter<"InventoryMovement"> | $Enums.MovementType
    quantity?: FloatFilter<"InventoryMovement"> | number
    unitCost?: FloatNullableFilter<"InventoryMovement"> | number | null
    referenceId?: StringNullableFilter<"InventoryMovement"> | string | null
    referenceType?: StringNullableFilter<"InventoryMovement"> | string | null
    fromLocation?: StringNullableFilter<"InventoryMovement"> | string | null
    toLocation?: StringNullableFilter<"InventoryMovement"> | string | null
    notes?: StringNullableFilter<"InventoryMovement"> | string | null
    notesAr?: StringNullableFilter<"InventoryMovement"> | string | null
    performedBy?: StringFilter<"InventoryMovement"> | string
    createdAt?: DateTimeFilter<"InventoryMovement"> | Date | string
    item?: XOR<InventoryItemRelationFilter, InventoryItemWhereInput>
  }, "id">

  export type InventoryMovementOrderByWithAggregationInput = {
    id?: SortOrder
    itemId?: SortOrder
    tenantId?: SortOrder
    type?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrderInput | SortOrder
    referenceId?: SortOrderInput | SortOrder
    referenceType?: SortOrderInput | SortOrder
    fromLocation?: SortOrderInput | SortOrder
    toLocation?: SortOrderInput | SortOrder
    notes?: SortOrderInput | SortOrder
    notesAr?: SortOrderInput | SortOrder
    performedBy?: SortOrder
    createdAt?: SortOrder
    _count?: InventoryMovementCountOrderByAggregateInput
    _avg?: InventoryMovementAvgOrderByAggregateInput
    _max?: InventoryMovementMaxOrderByAggregateInput
    _min?: InventoryMovementMinOrderByAggregateInput
    _sum?: InventoryMovementSumOrderByAggregateInput
  }

  export type InventoryMovementScalarWhereWithAggregatesInput = {
    AND?: InventoryMovementScalarWhereWithAggregatesInput | InventoryMovementScalarWhereWithAggregatesInput[]
    OR?: InventoryMovementScalarWhereWithAggregatesInput[]
    NOT?: InventoryMovementScalarWhereWithAggregatesInput | InventoryMovementScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"InventoryMovement"> | string
    itemId?: StringWithAggregatesFilter<"InventoryMovement"> | string
    tenantId?: StringWithAggregatesFilter<"InventoryMovement"> | string
    type?: EnumMovementTypeWithAggregatesFilter<"InventoryMovement"> | $Enums.MovementType
    quantity?: FloatWithAggregatesFilter<"InventoryMovement"> | number
    unitCost?: FloatNullableWithAggregatesFilter<"InventoryMovement"> | number | null
    referenceId?: StringNullableWithAggregatesFilter<"InventoryMovement"> | string | null
    referenceType?: StringNullableWithAggregatesFilter<"InventoryMovement"> | string | null
    fromLocation?: StringNullableWithAggregatesFilter<"InventoryMovement"> | string | null
    toLocation?: StringNullableWithAggregatesFilter<"InventoryMovement"> | string | null
    notes?: StringNullableWithAggregatesFilter<"InventoryMovement"> | string | null
    notesAr?: StringNullableWithAggregatesFilter<"InventoryMovement"> | string | null
    performedBy?: StringWithAggregatesFilter<"InventoryMovement"> | string
    createdAt?: DateTimeWithAggregatesFilter<"InventoryMovement"> | Date | string
  }

  export type InventoryAlertWhereInput = {
    AND?: InventoryAlertWhereInput | InventoryAlertWhereInput[]
    OR?: InventoryAlertWhereInput[]
    NOT?: InventoryAlertWhereInput | InventoryAlertWhereInput[]
    id?: StringFilter<"InventoryAlert"> | string
    alertType?: EnumAlertTypeFilter<"InventoryAlert"> | $Enums.AlertType
    priority?: EnumAlertPriorityFilter<"InventoryAlert"> | $Enums.AlertPriority
    status?: EnumAlertStatusFilter<"InventoryAlert"> | $Enums.AlertStatus
    itemId?: StringFilter<"InventoryAlert"> | string
    itemName?: StringFilter<"InventoryAlert"> | string
    itemNameAr?: StringFilter<"InventoryAlert"> | string
    titleEn?: StringFilter<"InventoryAlert"> | string
    titleAr?: StringFilter<"InventoryAlert"> | string
    messageEn?: StringFilter<"InventoryAlert"> | string
    messageAr?: StringFilter<"InventoryAlert"> | string
    currentValue?: FloatFilter<"InventoryAlert"> | number
    thresholdValue?: FloatFilter<"InventoryAlert"> | number
    recommendedActionEn?: StringFilter<"InventoryAlert"> | string
    recommendedActionAr?: StringFilter<"InventoryAlert"> | string
    actionUrl?: StringNullableFilter<"InventoryAlert"> | string | null
    createdAt?: DateTimeFilter<"InventoryAlert"> | Date | string
    acknowledgedAt?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    acknowledgedBy?: StringNullableFilter<"InventoryAlert"> | string | null
    resolvedAt?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    resolvedBy?: StringNullableFilter<"InventoryAlert"> | string | null
    resolutionNotes?: StringNullableFilter<"InventoryAlert"> | string | null
    snoozeUntil?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    item?: XOR<InventoryItemRelationFilter, InventoryItemWhereInput>
  }

  export type InventoryAlertOrderByWithRelationInput = {
    id?: SortOrder
    alertType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    itemId?: SortOrder
    itemName?: SortOrder
    itemNameAr?: SortOrder
    titleEn?: SortOrder
    titleAr?: SortOrder
    messageEn?: SortOrder
    messageAr?: SortOrder
    currentValue?: SortOrder
    thresholdValue?: SortOrder
    recommendedActionEn?: SortOrder
    recommendedActionAr?: SortOrder
    actionUrl?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    acknowledgedAt?: SortOrderInput | SortOrder
    acknowledgedBy?: SortOrderInput | SortOrder
    resolvedAt?: SortOrderInput | SortOrder
    resolvedBy?: SortOrderInput | SortOrder
    resolutionNotes?: SortOrderInput | SortOrder
    snoozeUntil?: SortOrderInput | SortOrder
    item?: InventoryItemOrderByWithRelationInput
  }

  export type InventoryAlertWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: InventoryAlertWhereInput | InventoryAlertWhereInput[]
    OR?: InventoryAlertWhereInput[]
    NOT?: InventoryAlertWhereInput | InventoryAlertWhereInput[]
    alertType?: EnumAlertTypeFilter<"InventoryAlert"> | $Enums.AlertType
    priority?: EnumAlertPriorityFilter<"InventoryAlert"> | $Enums.AlertPriority
    status?: EnumAlertStatusFilter<"InventoryAlert"> | $Enums.AlertStatus
    itemId?: StringFilter<"InventoryAlert"> | string
    itemName?: StringFilter<"InventoryAlert"> | string
    itemNameAr?: StringFilter<"InventoryAlert"> | string
    titleEn?: StringFilter<"InventoryAlert"> | string
    titleAr?: StringFilter<"InventoryAlert"> | string
    messageEn?: StringFilter<"InventoryAlert"> | string
    messageAr?: StringFilter<"InventoryAlert"> | string
    currentValue?: FloatFilter<"InventoryAlert"> | number
    thresholdValue?: FloatFilter<"InventoryAlert"> | number
    recommendedActionEn?: StringFilter<"InventoryAlert"> | string
    recommendedActionAr?: StringFilter<"InventoryAlert"> | string
    actionUrl?: StringNullableFilter<"InventoryAlert"> | string | null
    createdAt?: DateTimeFilter<"InventoryAlert"> | Date | string
    acknowledgedAt?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    acknowledgedBy?: StringNullableFilter<"InventoryAlert"> | string | null
    resolvedAt?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    resolvedBy?: StringNullableFilter<"InventoryAlert"> | string | null
    resolutionNotes?: StringNullableFilter<"InventoryAlert"> | string | null
    snoozeUntil?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    item?: XOR<InventoryItemRelationFilter, InventoryItemWhereInput>
  }, "id">

  export type InventoryAlertOrderByWithAggregationInput = {
    id?: SortOrder
    alertType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    itemId?: SortOrder
    itemName?: SortOrder
    itemNameAr?: SortOrder
    titleEn?: SortOrder
    titleAr?: SortOrder
    messageEn?: SortOrder
    messageAr?: SortOrder
    currentValue?: SortOrder
    thresholdValue?: SortOrder
    recommendedActionEn?: SortOrder
    recommendedActionAr?: SortOrder
    actionUrl?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    acknowledgedAt?: SortOrderInput | SortOrder
    acknowledgedBy?: SortOrderInput | SortOrder
    resolvedAt?: SortOrderInput | SortOrder
    resolvedBy?: SortOrderInput | SortOrder
    resolutionNotes?: SortOrderInput | SortOrder
    snoozeUntil?: SortOrderInput | SortOrder
    _count?: InventoryAlertCountOrderByAggregateInput
    _avg?: InventoryAlertAvgOrderByAggregateInput
    _max?: InventoryAlertMaxOrderByAggregateInput
    _min?: InventoryAlertMinOrderByAggregateInput
    _sum?: InventoryAlertSumOrderByAggregateInput
  }

  export type InventoryAlertScalarWhereWithAggregatesInput = {
    AND?: InventoryAlertScalarWhereWithAggregatesInput | InventoryAlertScalarWhereWithAggregatesInput[]
    OR?: InventoryAlertScalarWhereWithAggregatesInput[]
    NOT?: InventoryAlertScalarWhereWithAggregatesInput | InventoryAlertScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"InventoryAlert"> | string
    alertType?: EnumAlertTypeWithAggregatesFilter<"InventoryAlert"> | $Enums.AlertType
    priority?: EnumAlertPriorityWithAggregatesFilter<"InventoryAlert"> | $Enums.AlertPriority
    status?: EnumAlertStatusWithAggregatesFilter<"InventoryAlert"> | $Enums.AlertStatus
    itemId?: StringWithAggregatesFilter<"InventoryAlert"> | string
    itemName?: StringWithAggregatesFilter<"InventoryAlert"> | string
    itemNameAr?: StringWithAggregatesFilter<"InventoryAlert"> | string
    titleEn?: StringWithAggregatesFilter<"InventoryAlert"> | string
    titleAr?: StringWithAggregatesFilter<"InventoryAlert"> | string
    messageEn?: StringWithAggregatesFilter<"InventoryAlert"> | string
    messageAr?: StringWithAggregatesFilter<"InventoryAlert"> | string
    currentValue?: FloatWithAggregatesFilter<"InventoryAlert"> | number
    thresholdValue?: FloatWithAggregatesFilter<"InventoryAlert"> | number
    recommendedActionEn?: StringWithAggregatesFilter<"InventoryAlert"> | string
    recommendedActionAr?: StringWithAggregatesFilter<"InventoryAlert"> | string
    actionUrl?: StringNullableWithAggregatesFilter<"InventoryAlert"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"InventoryAlert"> | Date | string
    acknowledgedAt?: DateTimeNullableWithAggregatesFilter<"InventoryAlert"> | Date | string | null
    acknowledgedBy?: StringNullableWithAggregatesFilter<"InventoryAlert"> | string | null
    resolvedAt?: DateTimeNullableWithAggregatesFilter<"InventoryAlert"> | Date | string | null
    resolvedBy?: StringNullableWithAggregatesFilter<"InventoryAlert"> | string | null
    resolutionNotes?: StringNullableWithAggregatesFilter<"InventoryAlert"> | string | null
    snoozeUntil?: DateTimeNullableWithAggregatesFilter<"InventoryAlert"> | Date | string | null
  }

  export type AlertSettingsWhereInput = {
    AND?: AlertSettingsWhereInput | AlertSettingsWhereInput[]
    OR?: AlertSettingsWhereInput[]
    NOT?: AlertSettingsWhereInput | AlertSettingsWhereInput[]
    id?: StringFilter<"AlertSettings"> | string
    tenantId?: StringFilter<"AlertSettings"> | string
    expiryWarningDays?: IntFilter<"AlertSettings"> | number
    expiryCriticalDays?: IntFilter<"AlertSettings"> | number
    defaultReorderLevel?: FloatFilter<"AlertSettings"> | number
    enableEmailAlerts?: BoolFilter<"AlertSettings"> | boolean
    enablePushAlerts?: BoolFilter<"AlertSettings"> | boolean
    enableSmsAlerts?: BoolFilter<"AlertSettings"> | boolean
    alertCheckInterval?: IntFilter<"AlertSettings"> | number
    maxAlertsPerDay?: IntFilter<"AlertSettings"> | number
    autoResolveOnRestock?: BoolFilter<"AlertSettings"> | boolean
    autoResolveExpired?: BoolFilter<"AlertSettings"> | boolean
    createdAt?: DateTimeFilter<"AlertSettings"> | Date | string
    updatedAt?: DateTimeFilter<"AlertSettings"> | Date | string
  }

  export type AlertSettingsOrderByWithRelationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    enableEmailAlerts?: SortOrder
    enablePushAlerts?: SortOrder
    enableSmsAlerts?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
    autoResolveOnRestock?: SortOrder
    autoResolveExpired?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type AlertSettingsWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    tenantId?: string
    AND?: AlertSettingsWhereInput | AlertSettingsWhereInput[]
    OR?: AlertSettingsWhereInput[]
    NOT?: AlertSettingsWhereInput | AlertSettingsWhereInput[]
    expiryWarningDays?: IntFilter<"AlertSettings"> | number
    expiryCriticalDays?: IntFilter<"AlertSettings"> | number
    defaultReorderLevel?: FloatFilter<"AlertSettings"> | number
    enableEmailAlerts?: BoolFilter<"AlertSettings"> | boolean
    enablePushAlerts?: BoolFilter<"AlertSettings"> | boolean
    enableSmsAlerts?: BoolFilter<"AlertSettings"> | boolean
    alertCheckInterval?: IntFilter<"AlertSettings"> | number
    maxAlertsPerDay?: IntFilter<"AlertSettings"> | number
    autoResolveOnRestock?: BoolFilter<"AlertSettings"> | boolean
    autoResolveExpired?: BoolFilter<"AlertSettings"> | boolean
    createdAt?: DateTimeFilter<"AlertSettings"> | Date | string
    updatedAt?: DateTimeFilter<"AlertSettings"> | Date | string
  }, "id" | "tenantId">

  export type AlertSettingsOrderByWithAggregationInput = {
    id?: SortOrder
    tenantId?: SortOrder
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    enableEmailAlerts?: SortOrder
    enablePushAlerts?: SortOrder
    enableSmsAlerts?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
    autoResolveOnRestock?: SortOrder
    autoResolveExpired?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: AlertSettingsCountOrderByAggregateInput
    _avg?: AlertSettingsAvgOrderByAggregateInput
    _max?: AlertSettingsMaxOrderByAggregateInput
    _min?: AlertSettingsMinOrderByAggregateInput
    _sum?: AlertSettingsSumOrderByAggregateInput
  }

  export type AlertSettingsScalarWhereWithAggregatesInput = {
    AND?: AlertSettingsScalarWhereWithAggregatesInput | AlertSettingsScalarWhereWithAggregatesInput[]
    OR?: AlertSettingsScalarWhereWithAggregatesInput[]
    NOT?: AlertSettingsScalarWhereWithAggregatesInput | AlertSettingsScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"AlertSettings"> | string
    tenantId?: StringWithAggregatesFilter<"AlertSettings"> | string
    expiryWarningDays?: IntWithAggregatesFilter<"AlertSettings"> | number
    expiryCriticalDays?: IntWithAggregatesFilter<"AlertSettings"> | number
    defaultReorderLevel?: FloatWithAggregatesFilter<"AlertSettings"> | number
    enableEmailAlerts?: BoolWithAggregatesFilter<"AlertSettings"> | boolean
    enablePushAlerts?: BoolWithAggregatesFilter<"AlertSettings"> | boolean
    enableSmsAlerts?: BoolWithAggregatesFilter<"AlertSettings"> | boolean
    alertCheckInterval?: IntWithAggregatesFilter<"AlertSettings"> | number
    maxAlertsPerDay?: IntWithAggregatesFilter<"AlertSettings"> | number
    autoResolveOnRestock?: BoolWithAggregatesFilter<"AlertSettings"> | boolean
    autoResolveExpired?: BoolWithAggregatesFilter<"AlertSettings"> | boolean
    createdAt?: DateTimeWithAggregatesFilter<"AlertSettings"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"AlertSettings"> | Date | string
  }

  export type WarehouseWhereInput = {
    AND?: WarehouseWhereInput | WarehouseWhereInput[]
    OR?: WarehouseWhereInput[]
    NOT?: WarehouseWhereInput | WarehouseWhereInput[]
    id?: StringFilter<"Warehouse"> | string
    name?: StringFilter<"Warehouse"> | string
    nameAr?: StringFilter<"Warehouse"> | string
    warehouseType?: EnumWarehouseTypeFilter<"Warehouse"> | $Enums.WarehouseType
    latitude?: FloatNullableFilter<"Warehouse"> | number | null
    longitude?: FloatNullableFilter<"Warehouse"> | number | null
    address?: StringNullableFilter<"Warehouse"> | string | null
    governorate?: StringNullableFilter<"Warehouse"> | string | null
    capacityValue?: FloatFilter<"Warehouse"> | number
    capacityUnit?: StringFilter<"Warehouse"> | string
    currentUsage?: FloatFilter<"Warehouse"> | number
    storageCondition?: EnumStorageConditionFilter<"Warehouse"> | $Enums.StorageCondition
    tempMin?: FloatNullableFilter<"Warehouse"> | number | null
    tempMax?: FloatNullableFilter<"Warehouse"> | number | null
    humidityMin?: FloatNullableFilter<"Warehouse"> | number | null
    humidityMax?: FloatNullableFilter<"Warehouse"> | number | null
    isActive?: BoolFilter<"Warehouse"> | boolean
    managerId?: StringNullableFilter<"Warehouse"> | string | null
    managerName?: StringNullableFilter<"Warehouse"> | string | null
    createdAt?: DateTimeFilter<"Warehouse"> | Date | string
    updatedAt?: DateTimeFilter<"Warehouse"> | Date | string
    zones?: ZoneListRelationFilter
    transfersFrom?: StockTransferListRelationFilter
    transfersTo?: StockTransferListRelationFilter
  }

  export type WarehouseOrderByWithRelationInput = {
    id?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    warehouseType?: SortOrder
    latitude?: SortOrderInput | SortOrder
    longitude?: SortOrderInput | SortOrder
    address?: SortOrderInput | SortOrder
    governorate?: SortOrderInput | SortOrder
    capacityValue?: SortOrder
    capacityUnit?: SortOrder
    currentUsage?: SortOrder
    storageCondition?: SortOrder
    tempMin?: SortOrderInput | SortOrder
    tempMax?: SortOrderInput | SortOrder
    humidityMin?: SortOrderInput | SortOrder
    humidityMax?: SortOrderInput | SortOrder
    isActive?: SortOrder
    managerId?: SortOrderInput | SortOrder
    managerName?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    zones?: ZoneOrderByRelationAggregateInput
    transfersFrom?: StockTransferOrderByRelationAggregateInput
    transfersTo?: StockTransferOrderByRelationAggregateInput
  }

  export type WarehouseWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: WarehouseWhereInput | WarehouseWhereInput[]
    OR?: WarehouseWhereInput[]
    NOT?: WarehouseWhereInput | WarehouseWhereInput[]
    name?: StringFilter<"Warehouse"> | string
    nameAr?: StringFilter<"Warehouse"> | string
    warehouseType?: EnumWarehouseTypeFilter<"Warehouse"> | $Enums.WarehouseType
    latitude?: FloatNullableFilter<"Warehouse"> | number | null
    longitude?: FloatNullableFilter<"Warehouse"> | number | null
    address?: StringNullableFilter<"Warehouse"> | string | null
    governorate?: StringNullableFilter<"Warehouse"> | string | null
    capacityValue?: FloatFilter<"Warehouse"> | number
    capacityUnit?: StringFilter<"Warehouse"> | string
    currentUsage?: FloatFilter<"Warehouse"> | number
    storageCondition?: EnumStorageConditionFilter<"Warehouse"> | $Enums.StorageCondition
    tempMin?: FloatNullableFilter<"Warehouse"> | number | null
    tempMax?: FloatNullableFilter<"Warehouse"> | number | null
    humidityMin?: FloatNullableFilter<"Warehouse"> | number | null
    humidityMax?: FloatNullableFilter<"Warehouse"> | number | null
    isActive?: BoolFilter<"Warehouse"> | boolean
    managerId?: StringNullableFilter<"Warehouse"> | string | null
    managerName?: StringNullableFilter<"Warehouse"> | string | null
    createdAt?: DateTimeFilter<"Warehouse"> | Date | string
    updatedAt?: DateTimeFilter<"Warehouse"> | Date | string
    zones?: ZoneListRelationFilter
    transfersFrom?: StockTransferListRelationFilter
    transfersTo?: StockTransferListRelationFilter
  }, "id">

  export type WarehouseOrderByWithAggregationInput = {
    id?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    warehouseType?: SortOrder
    latitude?: SortOrderInput | SortOrder
    longitude?: SortOrderInput | SortOrder
    address?: SortOrderInput | SortOrder
    governorate?: SortOrderInput | SortOrder
    capacityValue?: SortOrder
    capacityUnit?: SortOrder
    currentUsage?: SortOrder
    storageCondition?: SortOrder
    tempMin?: SortOrderInput | SortOrder
    tempMax?: SortOrderInput | SortOrder
    humidityMin?: SortOrderInput | SortOrder
    humidityMax?: SortOrderInput | SortOrder
    isActive?: SortOrder
    managerId?: SortOrderInput | SortOrder
    managerName?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: WarehouseCountOrderByAggregateInput
    _avg?: WarehouseAvgOrderByAggregateInput
    _max?: WarehouseMaxOrderByAggregateInput
    _min?: WarehouseMinOrderByAggregateInput
    _sum?: WarehouseSumOrderByAggregateInput
  }

  export type WarehouseScalarWhereWithAggregatesInput = {
    AND?: WarehouseScalarWhereWithAggregatesInput | WarehouseScalarWhereWithAggregatesInput[]
    OR?: WarehouseScalarWhereWithAggregatesInput[]
    NOT?: WarehouseScalarWhereWithAggregatesInput | WarehouseScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"Warehouse"> | string
    name?: StringWithAggregatesFilter<"Warehouse"> | string
    nameAr?: StringWithAggregatesFilter<"Warehouse"> | string
    warehouseType?: EnumWarehouseTypeWithAggregatesFilter<"Warehouse"> | $Enums.WarehouseType
    latitude?: FloatNullableWithAggregatesFilter<"Warehouse"> | number | null
    longitude?: FloatNullableWithAggregatesFilter<"Warehouse"> | number | null
    address?: StringNullableWithAggregatesFilter<"Warehouse"> | string | null
    governorate?: StringNullableWithAggregatesFilter<"Warehouse"> | string | null
    capacityValue?: FloatWithAggregatesFilter<"Warehouse"> | number
    capacityUnit?: StringWithAggregatesFilter<"Warehouse"> | string
    currentUsage?: FloatWithAggregatesFilter<"Warehouse"> | number
    storageCondition?: EnumStorageConditionWithAggregatesFilter<"Warehouse"> | $Enums.StorageCondition
    tempMin?: FloatNullableWithAggregatesFilter<"Warehouse"> | number | null
    tempMax?: FloatNullableWithAggregatesFilter<"Warehouse"> | number | null
    humidityMin?: FloatNullableWithAggregatesFilter<"Warehouse"> | number | null
    humidityMax?: FloatNullableWithAggregatesFilter<"Warehouse"> | number | null
    isActive?: BoolWithAggregatesFilter<"Warehouse"> | boolean
    managerId?: StringNullableWithAggregatesFilter<"Warehouse"> | string | null
    managerName?: StringNullableWithAggregatesFilter<"Warehouse"> | string | null
    createdAt?: DateTimeWithAggregatesFilter<"Warehouse"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Warehouse"> | Date | string
  }

  export type ZoneWhereInput = {
    AND?: ZoneWhereInput | ZoneWhereInput[]
    OR?: ZoneWhereInput[]
    NOT?: ZoneWhereInput | ZoneWhereInput[]
    id?: StringFilter<"Zone"> | string
    warehouseId?: StringFilter<"Zone"> | string
    name?: StringFilter<"Zone"> | string
    nameAr?: StringNullableFilter<"Zone"> | string | null
    capacity?: FloatFilter<"Zone"> | number
    currentUsage?: FloatFilter<"Zone"> | number
    condition?: EnumStorageConditionNullableFilter<"Zone"> | $Enums.StorageCondition | null
    createdAt?: DateTimeFilter<"Zone"> | Date | string
    updatedAt?: DateTimeFilter<"Zone"> | Date | string
    warehouse?: XOR<WarehouseRelationFilter, WarehouseWhereInput>
    locations?: StorageLocationListRelationFilter
  }

  export type ZoneOrderByWithRelationInput = {
    id?: SortOrder
    warehouseId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrderInput | SortOrder
    capacity?: SortOrder
    currentUsage?: SortOrder
    condition?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    warehouse?: WarehouseOrderByWithRelationInput
    locations?: StorageLocationOrderByRelationAggregateInput
  }

  export type ZoneWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: ZoneWhereInput | ZoneWhereInput[]
    OR?: ZoneWhereInput[]
    NOT?: ZoneWhereInput | ZoneWhereInput[]
    warehouseId?: StringFilter<"Zone"> | string
    name?: StringFilter<"Zone"> | string
    nameAr?: StringNullableFilter<"Zone"> | string | null
    capacity?: FloatFilter<"Zone"> | number
    currentUsage?: FloatFilter<"Zone"> | number
    condition?: EnumStorageConditionNullableFilter<"Zone"> | $Enums.StorageCondition | null
    createdAt?: DateTimeFilter<"Zone"> | Date | string
    updatedAt?: DateTimeFilter<"Zone"> | Date | string
    warehouse?: XOR<WarehouseRelationFilter, WarehouseWhereInput>
    locations?: StorageLocationListRelationFilter
  }, "id">

  export type ZoneOrderByWithAggregationInput = {
    id?: SortOrder
    warehouseId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrderInput | SortOrder
    capacity?: SortOrder
    currentUsage?: SortOrder
    condition?: SortOrderInput | SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: ZoneCountOrderByAggregateInput
    _avg?: ZoneAvgOrderByAggregateInput
    _max?: ZoneMaxOrderByAggregateInput
    _min?: ZoneMinOrderByAggregateInput
    _sum?: ZoneSumOrderByAggregateInput
  }

  export type ZoneScalarWhereWithAggregatesInput = {
    AND?: ZoneScalarWhereWithAggregatesInput | ZoneScalarWhereWithAggregatesInput[]
    OR?: ZoneScalarWhereWithAggregatesInput[]
    NOT?: ZoneScalarWhereWithAggregatesInput | ZoneScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"Zone"> | string
    warehouseId?: StringWithAggregatesFilter<"Zone"> | string
    name?: StringWithAggregatesFilter<"Zone"> | string
    nameAr?: StringNullableWithAggregatesFilter<"Zone"> | string | null
    capacity?: FloatWithAggregatesFilter<"Zone"> | number
    currentUsage?: FloatWithAggregatesFilter<"Zone"> | number
    condition?: EnumStorageConditionNullableWithAggregatesFilter<"Zone"> | $Enums.StorageCondition | null
    createdAt?: DateTimeWithAggregatesFilter<"Zone"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"Zone"> | Date | string
  }

  export type StorageLocationWhereInput = {
    AND?: StorageLocationWhereInput | StorageLocationWhereInput[]
    OR?: StorageLocationWhereInput[]
    NOT?: StorageLocationWhereInput | StorageLocationWhereInput[]
    id?: StringFilter<"StorageLocation"> | string
    zoneId?: StringFilter<"StorageLocation"> | string
    aisle?: StringFilter<"StorageLocation"> | string
    shelf?: StringFilter<"StorageLocation"> | string
    bin?: StringFilter<"StorageLocation"> | string
    locationCode?: StringFilter<"StorageLocation"> | string
    capacity?: FloatFilter<"StorageLocation"> | number
    isOccupied?: BoolFilter<"StorageLocation"> | boolean
    currentItemId?: StringNullableFilter<"StorageLocation"> | string | null
    currentQty?: FloatFilter<"StorageLocation"> | number
    createdAt?: DateTimeFilter<"StorageLocation"> | Date | string
    updatedAt?: DateTimeFilter<"StorageLocation"> | Date | string
    zone?: XOR<ZoneRelationFilter, ZoneWhereInput>
  }

  export type StorageLocationOrderByWithRelationInput = {
    id?: SortOrder
    zoneId?: SortOrder
    aisle?: SortOrder
    shelf?: SortOrder
    bin?: SortOrder
    locationCode?: SortOrder
    capacity?: SortOrder
    isOccupied?: SortOrder
    currentItemId?: SortOrderInput | SortOrder
    currentQty?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    zone?: ZoneOrderByWithRelationInput
  }

  export type StorageLocationWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    locationCode?: string
    AND?: StorageLocationWhereInput | StorageLocationWhereInput[]
    OR?: StorageLocationWhereInput[]
    NOT?: StorageLocationWhereInput | StorageLocationWhereInput[]
    zoneId?: StringFilter<"StorageLocation"> | string
    aisle?: StringFilter<"StorageLocation"> | string
    shelf?: StringFilter<"StorageLocation"> | string
    bin?: StringFilter<"StorageLocation"> | string
    capacity?: FloatFilter<"StorageLocation"> | number
    isOccupied?: BoolFilter<"StorageLocation"> | boolean
    currentItemId?: StringNullableFilter<"StorageLocation"> | string | null
    currentQty?: FloatFilter<"StorageLocation"> | number
    createdAt?: DateTimeFilter<"StorageLocation"> | Date | string
    updatedAt?: DateTimeFilter<"StorageLocation"> | Date | string
    zone?: XOR<ZoneRelationFilter, ZoneWhereInput>
  }, "id" | "locationCode">

  export type StorageLocationOrderByWithAggregationInput = {
    id?: SortOrder
    zoneId?: SortOrder
    aisle?: SortOrder
    shelf?: SortOrder
    bin?: SortOrder
    locationCode?: SortOrder
    capacity?: SortOrder
    isOccupied?: SortOrder
    currentItemId?: SortOrderInput | SortOrder
    currentQty?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    _count?: StorageLocationCountOrderByAggregateInput
    _avg?: StorageLocationAvgOrderByAggregateInput
    _max?: StorageLocationMaxOrderByAggregateInput
    _min?: StorageLocationMinOrderByAggregateInput
    _sum?: StorageLocationSumOrderByAggregateInput
  }

  export type StorageLocationScalarWhereWithAggregatesInput = {
    AND?: StorageLocationScalarWhereWithAggregatesInput | StorageLocationScalarWhereWithAggregatesInput[]
    OR?: StorageLocationScalarWhereWithAggregatesInput[]
    NOT?: StorageLocationScalarWhereWithAggregatesInput | StorageLocationScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"StorageLocation"> | string
    zoneId?: StringWithAggregatesFilter<"StorageLocation"> | string
    aisle?: StringWithAggregatesFilter<"StorageLocation"> | string
    shelf?: StringWithAggregatesFilter<"StorageLocation"> | string
    bin?: StringWithAggregatesFilter<"StorageLocation"> | string
    locationCode?: StringWithAggregatesFilter<"StorageLocation"> | string
    capacity?: FloatWithAggregatesFilter<"StorageLocation"> | number
    isOccupied?: BoolWithAggregatesFilter<"StorageLocation"> | boolean
    currentItemId?: StringNullableWithAggregatesFilter<"StorageLocation"> | string | null
    currentQty?: FloatWithAggregatesFilter<"StorageLocation"> | number
    createdAt?: DateTimeWithAggregatesFilter<"StorageLocation"> | Date | string
    updatedAt?: DateTimeWithAggregatesFilter<"StorageLocation"> | Date | string
  }

  export type StockTransferWhereInput = {
    AND?: StockTransferWhereInput | StockTransferWhereInput[]
    OR?: StockTransferWhereInput[]
    NOT?: StockTransferWhereInput | StockTransferWhereInput[]
    id?: StringFilter<"StockTransfer"> | string
    itemId?: StringFilter<"StockTransfer"> | string
    fromWarehouseId?: StringNullableFilter<"StockTransfer"> | string | null
    toWarehouseId?: StringFilter<"StockTransfer"> | string
    quantity?: FloatFilter<"StockTransfer"> | number
    unitCost?: FloatNullableFilter<"StockTransfer"> | number | null
    totalCost?: FloatNullableFilter<"StockTransfer"> | number | null
    transferType?: EnumTransferTypeFilter<"StockTransfer"> | $Enums.TransferType
    status?: EnumTransferStatusFilter<"StockTransfer"> | $Enums.TransferStatus
    requestedBy?: StringFilter<"StockTransfer"> | string
    approvedBy?: StringNullableFilter<"StockTransfer"> | string | null
    performedBy?: StringNullableFilter<"StockTransfer"> | string | null
    requestedAt?: DateTimeFilter<"StockTransfer"> | Date | string
    approvedAt?: DateTimeNullableFilter<"StockTransfer"> | Date | string | null
    completedAt?: DateTimeNullableFilter<"StockTransfer"> | Date | string | null
    notes?: StringNullableFilter<"StockTransfer"> | string | null
    fromWarehouse?: XOR<WarehouseNullableRelationFilter, WarehouseWhereInput> | null
    toWarehouse?: XOR<WarehouseRelationFilter, WarehouseWhereInput>
  }

  export type StockTransferOrderByWithRelationInput = {
    id?: SortOrder
    itemId?: SortOrder
    fromWarehouseId?: SortOrderInput | SortOrder
    toWarehouseId?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrderInput | SortOrder
    totalCost?: SortOrderInput | SortOrder
    transferType?: SortOrder
    status?: SortOrder
    requestedBy?: SortOrder
    approvedBy?: SortOrderInput | SortOrder
    performedBy?: SortOrderInput | SortOrder
    requestedAt?: SortOrder
    approvedAt?: SortOrderInput | SortOrder
    completedAt?: SortOrderInput | SortOrder
    notes?: SortOrderInput | SortOrder
    fromWarehouse?: WarehouseOrderByWithRelationInput
    toWarehouse?: WarehouseOrderByWithRelationInput
  }

  export type StockTransferWhereUniqueInput = Prisma.AtLeast<{
    id?: string
    AND?: StockTransferWhereInput | StockTransferWhereInput[]
    OR?: StockTransferWhereInput[]
    NOT?: StockTransferWhereInput | StockTransferWhereInput[]
    itemId?: StringFilter<"StockTransfer"> | string
    fromWarehouseId?: StringNullableFilter<"StockTransfer"> | string | null
    toWarehouseId?: StringFilter<"StockTransfer"> | string
    quantity?: FloatFilter<"StockTransfer"> | number
    unitCost?: FloatNullableFilter<"StockTransfer"> | number | null
    totalCost?: FloatNullableFilter<"StockTransfer"> | number | null
    transferType?: EnumTransferTypeFilter<"StockTransfer"> | $Enums.TransferType
    status?: EnumTransferStatusFilter<"StockTransfer"> | $Enums.TransferStatus
    requestedBy?: StringFilter<"StockTransfer"> | string
    approvedBy?: StringNullableFilter<"StockTransfer"> | string | null
    performedBy?: StringNullableFilter<"StockTransfer"> | string | null
    requestedAt?: DateTimeFilter<"StockTransfer"> | Date | string
    approvedAt?: DateTimeNullableFilter<"StockTransfer"> | Date | string | null
    completedAt?: DateTimeNullableFilter<"StockTransfer"> | Date | string | null
    notes?: StringNullableFilter<"StockTransfer"> | string | null
    fromWarehouse?: XOR<WarehouseNullableRelationFilter, WarehouseWhereInput> | null
    toWarehouse?: XOR<WarehouseRelationFilter, WarehouseWhereInput>
  }, "id">

  export type StockTransferOrderByWithAggregationInput = {
    id?: SortOrder
    itemId?: SortOrder
    fromWarehouseId?: SortOrderInput | SortOrder
    toWarehouseId?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrderInput | SortOrder
    totalCost?: SortOrderInput | SortOrder
    transferType?: SortOrder
    status?: SortOrder
    requestedBy?: SortOrder
    approvedBy?: SortOrderInput | SortOrder
    performedBy?: SortOrderInput | SortOrder
    requestedAt?: SortOrder
    approvedAt?: SortOrderInput | SortOrder
    completedAt?: SortOrderInput | SortOrder
    notes?: SortOrderInput | SortOrder
    _count?: StockTransferCountOrderByAggregateInput
    _avg?: StockTransferAvgOrderByAggregateInput
    _max?: StockTransferMaxOrderByAggregateInput
    _min?: StockTransferMinOrderByAggregateInput
    _sum?: StockTransferSumOrderByAggregateInput
  }

  export type StockTransferScalarWhereWithAggregatesInput = {
    AND?: StockTransferScalarWhereWithAggregatesInput | StockTransferScalarWhereWithAggregatesInput[]
    OR?: StockTransferScalarWhereWithAggregatesInput[]
    NOT?: StockTransferScalarWhereWithAggregatesInput | StockTransferScalarWhereWithAggregatesInput[]
    id?: StringWithAggregatesFilter<"StockTransfer"> | string
    itemId?: StringWithAggregatesFilter<"StockTransfer"> | string
    fromWarehouseId?: StringNullableWithAggregatesFilter<"StockTransfer"> | string | null
    toWarehouseId?: StringWithAggregatesFilter<"StockTransfer"> | string
    quantity?: FloatWithAggregatesFilter<"StockTransfer"> | number
    unitCost?: FloatNullableWithAggregatesFilter<"StockTransfer"> | number | null
    totalCost?: FloatNullableWithAggregatesFilter<"StockTransfer"> | number | null
    transferType?: EnumTransferTypeWithAggregatesFilter<"StockTransfer"> | $Enums.TransferType
    status?: EnumTransferStatusWithAggregatesFilter<"StockTransfer"> | $Enums.TransferStatus
    requestedBy?: StringWithAggregatesFilter<"StockTransfer"> | string
    approvedBy?: StringNullableWithAggregatesFilter<"StockTransfer"> | string | null
    performedBy?: StringNullableWithAggregatesFilter<"StockTransfer"> | string | null
    requestedAt?: DateTimeWithAggregatesFilter<"StockTransfer"> | Date | string
    approvedAt?: DateTimeNullableWithAggregatesFilter<"StockTransfer"> | Date | string | null
    completedAt?: DateTimeNullableWithAggregatesFilter<"StockTransfer"> | Date | string | null
    notes?: StringNullableWithAggregatesFilter<"StockTransfer"> | string | null
  }

  export type InventoryItemCreateInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
    movements?: InventoryMovementCreateNestedManyWithoutItemInput
    alerts?: InventoryAlertCreateNestedManyWithoutItemInput
  }

  export type InventoryItemUncheckedCreateInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
    movements?: InventoryMovementUncheckedCreateNestedManyWithoutItemInput
    alerts?: InventoryAlertUncheckedCreateNestedManyWithoutItemInput
  }

  export type InventoryItemUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    movements?: InventoryMovementUpdateManyWithoutItemNestedInput
    alerts?: InventoryAlertUpdateManyWithoutItemNestedInput
  }

  export type InventoryItemUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    movements?: InventoryMovementUncheckedUpdateManyWithoutItemNestedInput
    alerts?: InventoryAlertUncheckedUpdateManyWithoutItemNestedInput
  }

  export type InventoryItemCreateManyInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
  }

  export type InventoryItemUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type InventoryItemUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type InventoryMovementCreateInput = {
    id?: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost?: number | null
    referenceId?: string | null
    referenceType?: string | null
    fromLocation?: string | null
    toLocation?: string | null
    notes?: string | null
    notesAr?: string | null
    performedBy: string
    createdAt?: Date | string
    item: InventoryItemCreateNestedOneWithoutMovementsInput
  }

  export type InventoryMovementUncheckedCreateInput = {
    id?: string
    itemId: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost?: number | null
    referenceId?: string | null
    referenceType?: string | null
    fromLocation?: string | null
    toLocation?: string | null
    notes?: string | null
    notesAr?: string | null
    performedBy: string
    createdAt?: Date | string
  }

  export type InventoryMovementUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    item?: InventoryItemUpdateOneRequiredWithoutMovementsNestedInput
  }

  export type InventoryMovementUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type InventoryMovementCreateManyInput = {
    id?: string
    itemId: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost?: number | null
    referenceId?: string | null
    referenceType?: string | null
    fromLocation?: string | null
    toLocation?: string | null
    notes?: string | null
    notesAr?: string | null
    performedBy: string
    createdAt?: Date | string
  }

  export type InventoryMovementUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type InventoryMovementUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type InventoryAlertCreateInput = {
    id?: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status?: $Enums.AlertStatus
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl?: string | null
    createdAt?: Date | string
    acknowledgedAt?: Date | string | null
    acknowledgedBy?: string | null
    resolvedAt?: Date | string | null
    resolvedBy?: string | null
    resolutionNotes?: string | null
    snoozeUntil?: Date | string | null
    item: InventoryItemCreateNestedOneWithoutAlertsInput
  }

  export type InventoryAlertUncheckedCreateInput = {
    id?: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status?: $Enums.AlertStatus
    itemId: string
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl?: string | null
    createdAt?: Date | string
    acknowledgedAt?: Date | string | null
    acknowledgedBy?: string | null
    resolvedAt?: Date | string | null
    resolvedBy?: string | null
    resolutionNotes?: string | null
    snoozeUntil?: Date | string | null
  }

  export type InventoryAlertUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    item?: InventoryItemUpdateOneRequiredWithoutAlertsNestedInput
  }

  export type InventoryAlertUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemId?: StringFieldUpdateOperationsInput | string
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type InventoryAlertCreateManyInput = {
    id?: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status?: $Enums.AlertStatus
    itemId: string
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl?: string | null
    createdAt?: Date | string
    acknowledgedAt?: Date | string | null
    acknowledgedBy?: string | null
    resolvedAt?: Date | string | null
    resolvedBy?: string | null
    resolutionNotes?: string | null
    snoozeUntil?: Date | string | null
  }

  export type InventoryAlertUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type InventoryAlertUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemId?: StringFieldUpdateOperationsInput | string
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type AlertSettingsCreateInput = {
    id?: string
    tenantId: string
    expiryWarningDays?: number
    expiryCriticalDays?: number
    defaultReorderLevel?: number
    enableEmailAlerts?: boolean
    enablePushAlerts?: boolean
    enableSmsAlerts?: boolean
    alertCheckInterval?: number
    maxAlertsPerDay?: number
    autoResolveOnRestock?: boolean
    autoResolveExpired?: boolean
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type AlertSettingsUncheckedCreateInput = {
    id?: string
    tenantId: string
    expiryWarningDays?: number
    expiryCriticalDays?: number
    defaultReorderLevel?: number
    enableEmailAlerts?: boolean
    enablePushAlerts?: boolean
    enableSmsAlerts?: boolean
    alertCheckInterval?: number
    maxAlertsPerDay?: number
    autoResolveOnRestock?: boolean
    autoResolveExpired?: boolean
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type AlertSettingsUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    expiryWarningDays?: IntFieldUpdateOperationsInput | number
    expiryCriticalDays?: IntFieldUpdateOperationsInput | number
    defaultReorderLevel?: FloatFieldUpdateOperationsInput | number
    enableEmailAlerts?: BoolFieldUpdateOperationsInput | boolean
    enablePushAlerts?: BoolFieldUpdateOperationsInput | boolean
    enableSmsAlerts?: BoolFieldUpdateOperationsInput | boolean
    alertCheckInterval?: IntFieldUpdateOperationsInput | number
    maxAlertsPerDay?: IntFieldUpdateOperationsInput | number
    autoResolveOnRestock?: BoolFieldUpdateOperationsInput | boolean
    autoResolveExpired?: BoolFieldUpdateOperationsInput | boolean
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type AlertSettingsUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    expiryWarningDays?: IntFieldUpdateOperationsInput | number
    expiryCriticalDays?: IntFieldUpdateOperationsInput | number
    defaultReorderLevel?: FloatFieldUpdateOperationsInput | number
    enableEmailAlerts?: BoolFieldUpdateOperationsInput | boolean
    enablePushAlerts?: BoolFieldUpdateOperationsInput | boolean
    enableSmsAlerts?: BoolFieldUpdateOperationsInput | boolean
    alertCheckInterval?: IntFieldUpdateOperationsInput | number
    maxAlertsPerDay?: IntFieldUpdateOperationsInput | number
    autoResolveOnRestock?: BoolFieldUpdateOperationsInput | boolean
    autoResolveExpired?: BoolFieldUpdateOperationsInput | boolean
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type AlertSettingsCreateManyInput = {
    id?: string
    tenantId: string
    expiryWarningDays?: number
    expiryCriticalDays?: number
    defaultReorderLevel?: number
    enableEmailAlerts?: boolean
    enablePushAlerts?: boolean
    enableSmsAlerts?: boolean
    alertCheckInterval?: number
    maxAlertsPerDay?: number
    autoResolveOnRestock?: boolean
    autoResolveExpired?: boolean
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type AlertSettingsUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    expiryWarningDays?: IntFieldUpdateOperationsInput | number
    expiryCriticalDays?: IntFieldUpdateOperationsInput | number
    defaultReorderLevel?: FloatFieldUpdateOperationsInput | number
    enableEmailAlerts?: BoolFieldUpdateOperationsInput | boolean
    enablePushAlerts?: BoolFieldUpdateOperationsInput | boolean
    enableSmsAlerts?: BoolFieldUpdateOperationsInput | boolean
    alertCheckInterval?: IntFieldUpdateOperationsInput | number
    maxAlertsPerDay?: IntFieldUpdateOperationsInput | number
    autoResolveOnRestock?: BoolFieldUpdateOperationsInput | boolean
    autoResolveExpired?: BoolFieldUpdateOperationsInput | boolean
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type AlertSettingsUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    expiryWarningDays?: IntFieldUpdateOperationsInput | number
    expiryCriticalDays?: IntFieldUpdateOperationsInput | number
    defaultReorderLevel?: FloatFieldUpdateOperationsInput | number
    enableEmailAlerts?: BoolFieldUpdateOperationsInput | boolean
    enablePushAlerts?: BoolFieldUpdateOperationsInput | boolean
    enableSmsAlerts?: BoolFieldUpdateOperationsInput | boolean
    alertCheckInterval?: IntFieldUpdateOperationsInput | number
    maxAlertsPerDay?: IntFieldUpdateOperationsInput | number
    autoResolveOnRestock?: BoolFieldUpdateOperationsInput | boolean
    autoResolveExpired?: BoolFieldUpdateOperationsInput | boolean
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WarehouseCreateInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    zones?: ZoneCreateNestedManyWithoutWarehouseInput
    transfersFrom?: StockTransferCreateNestedManyWithoutFromWarehouseInput
    transfersTo?: StockTransferCreateNestedManyWithoutToWarehouseInput
  }

  export type WarehouseUncheckedCreateInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    zones?: ZoneUncheckedCreateNestedManyWithoutWarehouseInput
    transfersFrom?: StockTransferUncheckedCreateNestedManyWithoutFromWarehouseInput
    transfersTo?: StockTransferUncheckedCreateNestedManyWithoutToWarehouseInput
  }

  export type WarehouseUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zones?: ZoneUpdateManyWithoutWarehouseNestedInput
    transfersFrom?: StockTransferUpdateManyWithoutFromWarehouseNestedInput
    transfersTo?: StockTransferUpdateManyWithoutToWarehouseNestedInput
  }

  export type WarehouseUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zones?: ZoneUncheckedUpdateManyWithoutWarehouseNestedInput
    transfersFrom?: StockTransferUncheckedUpdateManyWithoutFromWarehouseNestedInput
    transfersTo?: StockTransferUncheckedUpdateManyWithoutToWarehouseNestedInput
  }

  export type WarehouseCreateManyInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type WarehouseUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WarehouseUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ZoneCreateInput = {
    id?: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
    warehouse: WarehouseCreateNestedOneWithoutZonesInput
    locations?: StorageLocationCreateNestedManyWithoutZoneInput
  }

  export type ZoneUncheckedCreateInput = {
    id?: string
    warehouseId: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
    locations?: StorageLocationUncheckedCreateNestedManyWithoutZoneInput
  }

  export type ZoneUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    warehouse?: WarehouseUpdateOneRequiredWithoutZonesNestedInput
    locations?: StorageLocationUpdateManyWithoutZoneNestedInput
  }

  export type ZoneUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    warehouseId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    locations?: StorageLocationUncheckedUpdateManyWithoutZoneNestedInput
  }

  export type ZoneCreateManyInput = {
    id?: string
    warehouseId: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ZoneUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type ZoneUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    warehouseId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StorageLocationCreateInput = {
    id?: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied?: boolean
    currentItemId?: string | null
    currentQty?: number
    createdAt?: Date | string
    updatedAt?: Date | string
    zone: ZoneCreateNestedOneWithoutLocationsInput
  }

  export type StorageLocationUncheckedCreateInput = {
    id?: string
    zoneId: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied?: boolean
    currentItemId?: string | null
    currentQty?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type StorageLocationUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zone?: ZoneUpdateOneRequiredWithoutLocationsNestedInput
  }

  export type StorageLocationUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    zoneId?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StorageLocationCreateManyInput = {
    id?: string
    zoneId: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied?: boolean
    currentItemId?: string | null
    currentQty?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type StorageLocationUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StorageLocationUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    zoneId?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StockTransferCreateInput = {
    id?: string
    itemId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
    fromWarehouse?: WarehouseCreateNestedOneWithoutTransfersFromInput
    toWarehouse: WarehouseCreateNestedOneWithoutTransfersToInput
  }

  export type StockTransferUncheckedCreateInput = {
    id?: string
    itemId: string
    fromWarehouseId?: string | null
    toWarehouseId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
  }

  export type StockTransferUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    fromWarehouse?: WarehouseUpdateOneWithoutTransfersFromNestedInput
    toWarehouse?: WarehouseUpdateOneRequiredWithoutTransfersToNestedInput
  }

  export type StockTransferUncheckedUpdateInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    fromWarehouseId?: NullableStringFieldUpdateOperationsInput | string | null
    toWarehouseId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
  }

  export type StockTransferCreateManyInput = {
    id?: string
    itemId: string
    fromWarehouseId?: string | null
    toWarehouseId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
  }

  export type StockTransferUpdateManyMutationInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
  }

  export type StockTransferUncheckedUpdateManyInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    fromWarehouseId?: NullableStringFieldUpdateOperationsInput | string | null
    toWarehouseId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
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

  export type EnumItemCategoryFilter<$PrismaModel = never> = {
    equals?: $Enums.ItemCategory | EnumItemCategoryFieldRefInput<$PrismaModel>
    in?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    notIn?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    not?: NestedEnumItemCategoryFilter<$PrismaModel> | $Enums.ItemCategory
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

  export type InventoryMovementListRelationFilter = {
    every?: InventoryMovementWhereInput
    some?: InventoryMovementWhereInput
    none?: InventoryMovementWhereInput
  }

  export type InventoryAlertListRelationFilter = {
    every?: InventoryAlertWhereInput
    some?: InventoryAlertWhereInput
    none?: InventoryAlertWhereInput
  }

  export type SortOrderInput = {
    sort: SortOrder
    nulls?: NullsOrder
  }

  export type InventoryMovementOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type InventoryAlertOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type InventoryItemCountOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    sku?: SortOrder
    category?: SortOrder
    description?: SortOrder
    descriptionAr?: SortOrder
    quantity?: SortOrder
    unit?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrder
    maxStock?: SortOrder
    unitCost?: SortOrder
    sellingPrice?: SortOrder
    location?: SortOrder
    batchNumber?: SortOrder
    expiryDate?: SortOrder
    minTemperature?: SortOrder
    maxTemperature?: SortOrder
    minHumidity?: SortOrder
    maxHumidity?: SortOrder
    supplier?: SortOrder
    barcode?: SortOrder
    imageUrl?: SortOrder
    notes?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    lastRestocked?: SortOrder
  }

  export type InventoryItemAvgOrderByAggregateInput = {
    quantity?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrder
    maxStock?: SortOrder
    unitCost?: SortOrder
    sellingPrice?: SortOrder
    minTemperature?: SortOrder
    maxTemperature?: SortOrder
    minHumidity?: SortOrder
    maxHumidity?: SortOrder
  }

  export type InventoryItemMaxOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    sku?: SortOrder
    category?: SortOrder
    description?: SortOrder
    descriptionAr?: SortOrder
    quantity?: SortOrder
    unit?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrder
    maxStock?: SortOrder
    unitCost?: SortOrder
    sellingPrice?: SortOrder
    location?: SortOrder
    batchNumber?: SortOrder
    expiryDate?: SortOrder
    minTemperature?: SortOrder
    maxTemperature?: SortOrder
    minHumidity?: SortOrder
    maxHumidity?: SortOrder
    supplier?: SortOrder
    barcode?: SortOrder
    imageUrl?: SortOrder
    notes?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    lastRestocked?: SortOrder
  }

  export type InventoryItemMinOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    sku?: SortOrder
    category?: SortOrder
    description?: SortOrder
    descriptionAr?: SortOrder
    quantity?: SortOrder
    unit?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrder
    maxStock?: SortOrder
    unitCost?: SortOrder
    sellingPrice?: SortOrder
    location?: SortOrder
    batchNumber?: SortOrder
    expiryDate?: SortOrder
    minTemperature?: SortOrder
    maxTemperature?: SortOrder
    minHumidity?: SortOrder
    maxHumidity?: SortOrder
    supplier?: SortOrder
    barcode?: SortOrder
    imageUrl?: SortOrder
    notes?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
    lastRestocked?: SortOrder
  }

  export type InventoryItemSumOrderByAggregateInput = {
    quantity?: SortOrder
    reorderLevel?: SortOrder
    reorderPoint?: SortOrder
    maxStock?: SortOrder
    unitCost?: SortOrder
    sellingPrice?: SortOrder
    minTemperature?: SortOrder
    maxTemperature?: SortOrder
    minHumidity?: SortOrder
    maxHumidity?: SortOrder
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

  export type EnumItemCategoryWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.ItemCategory | EnumItemCategoryFieldRefInput<$PrismaModel>
    in?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    notIn?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    not?: NestedEnumItemCategoryWithAggregatesFilter<$PrismaModel> | $Enums.ItemCategory
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumItemCategoryFilter<$PrismaModel>
    _max?: NestedEnumItemCategoryFilter<$PrismaModel>
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

  export type EnumMovementTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.MovementType | EnumMovementTypeFieldRefInput<$PrismaModel>
    in?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumMovementTypeFilter<$PrismaModel> | $Enums.MovementType
  }

  export type InventoryItemRelationFilter = {
    is?: InventoryItemWhereInput
    isNot?: InventoryItemWhereInput
  }

  export type InventoryMovementCountOrderByAggregateInput = {
    id?: SortOrder
    itemId?: SortOrder
    tenantId?: SortOrder
    type?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrder
    referenceId?: SortOrder
    referenceType?: SortOrder
    fromLocation?: SortOrder
    toLocation?: SortOrder
    notes?: SortOrder
    notesAr?: SortOrder
    performedBy?: SortOrder
    createdAt?: SortOrder
  }

  export type InventoryMovementAvgOrderByAggregateInput = {
    quantity?: SortOrder
    unitCost?: SortOrder
  }

  export type InventoryMovementMaxOrderByAggregateInput = {
    id?: SortOrder
    itemId?: SortOrder
    tenantId?: SortOrder
    type?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrder
    referenceId?: SortOrder
    referenceType?: SortOrder
    fromLocation?: SortOrder
    toLocation?: SortOrder
    notes?: SortOrder
    notesAr?: SortOrder
    performedBy?: SortOrder
    createdAt?: SortOrder
  }

  export type InventoryMovementMinOrderByAggregateInput = {
    id?: SortOrder
    itemId?: SortOrder
    tenantId?: SortOrder
    type?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrder
    referenceId?: SortOrder
    referenceType?: SortOrder
    fromLocation?: SortOrder
    toLocation?: SortOrder
    notes?: SortOrder
    notesAr?: SortOrder
    performedBy?: SortOrder
    createdAt?: SortOrder
  }

  export type InventoryMovementSumOrderByAggregateInput = {
    quantity?: SortOrder
    unitCost?: SortOrder
  }

  export type EnumMovementTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.MovementType | EnumMovementTypeFieldRefInput<$PrismaModel>
    in?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumMovementTypeWithAggregatesFilter<$PrismaModel> | $Enums.MovementType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumMovementTypeFilter<$PrismaModel>
    _max?: NestedEnumMovementTypeFilter<$PrismaModel>
  }

  export type EnumAlertTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertType | EnumAlertTypeFieldRefInput<$PrismaModel>
    in?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertTypeFilter<$PrismaModel> | $Enums.AlertType
  }

  export type EnumAlertPriorityFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertPriority | EnumAlertPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertPriorityFilter<$PrismaModel> | $Enums.AlertPriority
  }

  export type EnumAlertStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertStatus | EnumAlertStatusFieldRefInput<$PrismaModel>
    in?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertStatusFilter<$PrismaModel> | $Enums.AlertStatus
  }

  export type InventoryAlertCountOrderByAggregateInput = {
    id?: SortOrder
    alertType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    itemId?: SortOrder
    itemName?: SortOrder
    itemNameAr?: SortOrder
    titleEn?: SortOrder
    titleAr?: SortOrder
    messageEn?: SortOrder
    messageAr?: SortOrder
    currentValue?: SortOrder
    thresholdValue?: SortOrder
    recommendedActionEn?: SortOrder
    recommendedActionAr?: SortOrder
    actionUrl?: SortOrder
    createdAt?: SortOrder
    acknowledgedAt?: SortOrder
    acknowledgedBy?: SortOrder
    resolvedAt?: SortOrder
    resolvedBy?: SortOrder
    resolutionNotes?: SortOrder
    snoozeUntil?: SortOrder
  }

  export type InventoryAlertAvgOrderByAggregateInput = {
    currentValue?: SortOrder
    thresholdValue?: SortOrder
  }

  export type InventoryAlertMaxOrderByAggregateInput = {
    id?: SortOrder
    alertType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    itemId?: SortOrder
    itemName?: SortOrder
    itemNameAr?: SortOrder
    titleEn?: SortOrder
    titleAr?: SortOrder
    messageEn?: SortOrder
    messageAr?: SortOrder
    currentValue?: SortOrder
    thresholdValue?: SortOrder
    recommendedActionEn?: SortOrder
    recommendedActionAr?: SortOrder
    actionUrl?: SortOrder
    createdAt?: SortOrder
    acknowledgedAt?: SortOrder
    acknowledgedBy?: SortOrder
    resolvedAt?: SortOrder
    resolvedBy?: SortOrder
    resolutionNotes?: SortOrder
    snoozeUntil?: SortOrder
  }

  export type InventoryAlertMinOrderByAggregateInput = {
    id?: SortOrder
    alertType?: SortOrder
    priority?: SortOrder
    status?: SortOrder
    itemId?: SortOrder
    itemName?: SortOrder
    itemNameAr?: SortOrder
    titleEn?: SortOrder
    titleAr?: SortOrder
    messageEn?: SortOrder
    messageAr?: SortOrder
    currentValue?: SortOrder
    thresholdValue?: SortOrder
    recommendedActionEn?: SortOrder
    recommendedActionAr?: SortOrder
    actionUrl?: SortOrder
    createdAt?: SortOrder
    acknowledgedAt?: SortOrder
    acknowledgedBy?: SortOrder
    resolvedAt?: SortOrder
    resolvedBy?: SortOrder
    resolutionNotes?: SortOrder
    snoozeUntil?: SortOrder
  }

  export type InventoryAlertSumOrderByAggregateInput = {
    currentValue?: SortOrder
    thresholdValue?: SortOrder
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

  export type EnumAlertPriorityWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertPriority | EnumAlertPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertPriorityWithAggregatesFilter<$PrismaModel> | $Enums.AlertPriority
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertPriorityFilter<$PrismaModel>
    _max?: NestedEnumAlertPriorityFilter<$PrismaModel>
  }

  export type EnumAlertStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertStatus | EnumAlertStatusFieldRefInput<$PrismaModel>
    in?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertStatusWithAggregatesFilter<$PrismaModel> | $Enums.AlertStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertStatusFilter<$PrismaModel>
    _max?: NestedEnumAlertStatusFilter<$PrismaModel>
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

  export type BoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
  }

  export type AlertSettingsCountOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    enableEmailAlerts?: SortOrder
    enablePushAlerts?: SortOrder
    enableSmsAlerts?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
    autoResolveOnRestock?: SortOrder
    autoResolveExpired?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type AlertSettingsAvgOrderByAggregateInput = {
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
  }

  export type AlertSettingsMaxOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    enableEmailAlerts?: SortOrder
    enablePushAlerts?: SortOrder
    enableSmsAlerts?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
    autoResolveOnRestock?: SortOrder
    autoResolveExpired?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type AlertSettingsMinOrderByAggregateInput = {
    id?: SortOrder
    tenantId?: SortOrder
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    enableEmailAlerts?: SortOrder
    enablePushAlerts?: SortOrder
    enableSmsAlerts?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
    autoResolveOnRestock?: SortOrder
    autoResolveExpired?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type AlertSettingsSumOrderByAggregateInput = {
    expiryWarningDays?: SortOrder
    expiryCriticalDays?: SortOrder
    defaultReorderLevel?: SortOrder
    alertCheckInterval?: SortOrder
    maxAlertsPerDay?: SortOrder
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

  export type BoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
  }

  export type EnumWarehouseTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.WarehouseType | EnumWarehouseTypeFieldRefInput<$PrismaModel>
    in?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumWarehouseTypeFilter<$PrismaModel> | $Enums.WarehouseType
  }

  export type EnumStorageConditionFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel>
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    not?: NestedEnumStorageConditionFilter<$PrismaModel> | $Enums.StorageCondition
  }

  export type ZoneListRelationFilter = {
    every?: ZoneWhereInput
    some?: ZoneWhereInput
    none?: ZoneWhereInput
  }

  export type StockTransferListRelationFilter = {
    every?: StockTransferWhereInput
    some?: StockTransferWhereInput
    none?: StockTransferWhereInput
  }

  export type ZoneOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type StockTransferOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type WarehouseCountOrderByAggregateInput = {
    id?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    warehouseType?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    address?: SortOrder
    governorate?: SortOrder
    capacityValue?: SortOrder
    capacityUnit?: SortOrder
    currentUsage?: SortOrder
    storageCondition?: SortOrder
    tempMin?: SortOrder
    tempMax?: SortOrder
    humidityMin?: SortOrder
    humidityMax?: SortOrder
    isActive?: SortOrder
    managerId?: SortOrder
    managerName?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WarehouseAvgOrderByAggregateInput = {
    latitude?: SortOrder
    longitude?: SortOrder
    capacityValue?: SortOrder
    currentUsage?: SortOrder
    tempMin?: SortOrder
    tempMax?: SortOrder
    humidityMin?: SortOrder
    humidityMax?: SortOrder
  }

  export type WarehouseMaxOrderByAggregateInput = {
    id?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    warehouseType?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    address?: SortOrder
    governorate?: SortOrder
    capacityValue?: SortOrder
    capacityUnit?: SortOrder
    currentUsage?: SortOrder
    storageCondition?: SortOrder
    tempMin?: SortOrder
    tempMax?: SortOrder
    humidityMin?: SortOrder
    humidityMax?: SortOrder
    isActive?: SortOrder
    managerId?: SortOrder
    managerName?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WarehouseMinOrderByAggregateInput = {
    id?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    warehouseType?: SortOrder
    latitude?: SortOrder
    longitude?: SortOrder
    address?: SortOrder
    governorate?: SortOrder
    capacityValue?: SortOrder
    capacityUnit?: SortOrder
    currentUsage?: SortOrder
    storageCondition?: SortOrder
    tempMin?: SortOrder
    tempMax?: SortOrder
    humidityMin?: SortOrder
    humidityMax?: SortOrder
    isActive?: SortOrder
    managerId?: SortOrder
    managerName?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type WarehouseSumOrderByAggregateInput = {
    latitude?: SortOrder
    longitude?: SortOrder
    capacityValue?: SortOrder
    currentUsage?: SortOrder
    tempMin?: SortOrder
    tempMax?: SortOrder
    humidityMin?: SortOrder
    humidityMax?: SortOrder
  }

  export type EnumWarehouseTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.WarehouseType | EnumWarehouseTypeFieldRefInput<$PrismaModel>
    in?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumWarehouseTypeWithAggregatesFilter<$PrismaModel> | $Enums.WarehouseType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumWarehouseTypeFilter<$PrismaModel>
    _max?: NestedEnumWarehouseTypeFilter<$PrismaModel>
  }

  export type EnumStorageConditionWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel>
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    not?: NestedEnumStorageConditionWithAggregatesFilter<$PrismaModel> | $Enums.StorageCondition
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumStorageConditionFilter<$PrismaModel>
    _max?: NestedEnumStorageConditionFilter<$PrismaModel>
  }

  export type EnumStorageConditionNullableFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel> | null
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    not?: NestedEnumStorageConditionNullableFilter<$PrismaModel> | $Enums.StorageCondition | null
  }

  export type WarehouseRelationFilter = {
    is?: WarehouseWhereInput
    isNot?: WarehouseWhereInput
  }

  export type StorageLocationListRelationFilter = {
    every?: StorageLocationWhereInput
    some?: StorageLocationWhereInput
    none?: StorageLocationWhereInput
  }

  export type StorageLocationOrderByRelationAggregateInput = {
    _count?: SortOrder
  }

  export type ZoneCountOrderByAggregateInput = {
    id?: SortOrder
    warehouseId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    capacity?: SortOrder
    currentUsage?: SortOrder
    condition?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ZoneAvgOrderByAggregateInput = {
    capacity?: SortOrder
    currentUsage?: SortOrder
  }

  export type ZoneMaxOrderByAggregateInput = {
    id?: SortOrder
    warehouseId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    capacity?: SortOrder
    currentUsage?: SortOrder
    condition?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ZoneMinOrderByAggregateInput = {
    id?: SortOrder
    warehouseId?: SortOrder
    name?: SortOrder
    nameAr?: SortOrder
    capacity?: SortOrder
    currentUsage?: SortOrder
    condition?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type ZoneSumOrderByAggregateInput = {
    capacity?: SortOrder
    currentUsage?: SortOrder
  }

  export type EnumStorageConditionNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel> | null
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    not?: NestedEnumStorageConditionNullableWithAggregatesFilter<$PrismaModel> | $Enums.StorageCondition | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedEnumStorageConditionNullableFilter<$PrismaModel>
    _max?: NestedEnumStorageConditionNullableFilter<$PrismaModel>
  }

  export type ZoneRelationFilter = {
    is?: ZoneWhereInput
    isNot?: ZoneWhereInput
  }

  export type StorageLocationCountOrderByAggregateInput = {
    id?: SortOrder
    zoneId?: SortOrder
    aisle?: SortOrder
    shelf?: SortOrder
    bin?: SortOrder
    locationCode?: SortOrder
    capacity?: SortOrder
    isOccupied?: SortOrder
    currentItemId?: SortOrder
    currentQty?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type StorageLocationAvgOrderByAggregateInput = {
    capacity?: SortOrder
    currentQty?: SortOrder
  }

  export type StorageLocationMaxOrderByAggregateInput = {
    id?: SortOrder
    zoneId?: SortOrder
    aisle?: SortOrder
    shelf?: SortOrder
    bin?: SortOrder
    locationCode?: SortOrder
    capacity?: SortOrder
    isOccupied?: SortOrder
    currentItemId?: SortOrder
    currentQty?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type StorageLocationMinOrderByAggregateInput = {
    id?: SortOrder
    zoneId?: SortOrder
    aisle?: SortOrder
    shelf?: SortOrder
    bin?: SortOrder
    locationCode?: SortOrder
    capacity?: SortOrder
    isOccupied?: SortOrder
    currentItemId?: SortOrder
    currentQty?: SortOrder
    createdAt?: SortOrder
    updatedAt?: SortOrder
  }

  export type StorageLocationSumOrderByAggregateInput = {
    capacity?: SortOrder
    currentQty?: SortOrder
  }

  export type EnumTransferTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferType | EnumTransferTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferTypeFilter<$PrismaModel> | $Enums.TransferType
  }

  export type EnumTransferStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferStatus | EnumTransferStatusFieldRefInput<$PrismaModel>
    in?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferStatusFilter<$PrismaModel> | $Enums.TransferStatus
  }

  export type WarehouseNullableRelationFilter = {
    is?: WarehouseWhereInput | null
    isNot?: WarehouseWhereInput | null
  }

  export type StockTransferCountOrderByAggregateInput = {
    id?: SortOrder
    itemId?: SortOrder
    fromWarehouseId?: SortOrder
    toWarehouseId?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrder
    totalCost?: SortOrder
    transferType?: SortOrder
    status?: SortOrder
    requestedBy?: SortOrder
    approvedBy?: SortOrder
    performedBy?: SortOrder
    requestedAt?: SortOrder
    approvedAt?: SortOrder
    completedAt?: SortOrder
    notes?: SortOrder
  }

  export type StockTransferAvgOrderByAggregateInput = {
    quantity?: SortOrder
    unitCost?: SortOrder
    totalCost?: SortOrder
  }

  export type StockTransferMaxOrderByAggregateInput = {
    id?: SortOrder
    itemId?: SortOrder
    fromWarehouseId?: SortOrder
    toWarehouseId?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrder
    totalCost?: SortOrder
    transferType?: SortOrder
    status?: SortOrder
    requestedBy?: SortOrder
    approvedBy?: SortOrder
    performedBy?: SortOrder
    requestedAt?: SortOrder
    approvedAt?: SortOrder
    completedAt?: SortOrder
    notes?: SortOrder
  }

  export type StockTransferMinOrderByAggregateInput = {
    id?: SortOrder
    itemId?: SortOrder
    fromWarehouseId?: SortOrder
    toWarehouseId?: SortOrder
    quantity?: SortOrder
    unitCost?: SortOrder
    totalCost?: SortOrder
    transferType?: SortOrder
    status?: SortOrder
    requestedBy?: SortOrder
    approvedBy?: SortOrder
    performedBy?: SortOrder
    requestedAt?: SortOrder
    approvedAt?: SortOrder
    completedAt?: SortOrder
    notes?: SortOrder
  }

  export type StockTransferSumOrderByAggregateInput = {
    quantity?: SortOrder
    unitCost?: SortOrder
    totalCost?: SortOrder
  }

  export type EnumTransferTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferType | EnumTransferTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferTypeWithAggregatesFilter<$PrismaModel> | $Enums.TransferType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTransferTypeFilter<$PrismaModel>
    _max?: NestedEnumTransferTypeFilter<$PrismaModel>
  }

  export type EnumTransferStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferStatus | EnumTransferStatusFieldRefInput<$PrismaModel>
    in?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferStatusWithAggregatesFilter<$PrismaModel> | $Enums.TransferStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTransferStatusFilter<$PrismaModel>
    _max?: NestedEnumTransferStatusFilter<$PrismaModel>
  }

  export type InventoryMovementCreateNestedManyWithoutItemInput = {
    create?: XOR<InventoryMovementCreateWithoutItemInput, InventoryMovementUncheckedCreateWithoutItemInput> | InventoryMovementCreateWithoutItemInput[] | InventoryMovementUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryMovementCreateOrConnectWithoutItemInput | InventoryMovementCreateOrConnectWithoutItemInput[]
    createMany?: InventoryMovementCreateManyItemInputEnvelope
    connect?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
  }

  export type InventoryAlertCreateNestedManyWithoutItemInput = {
    create?: XOR<InventoryAlertCreateWithoutItemInput, InventoryAlertUncheckedCreateWithoutItemInput> | InventoryAlertCreateWithoutItemInput[] | InventoryAlertUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryAlertCreateOrConnectWithoutItemInput | InventoryAlertCreateOrConnectWithoutItemInput[]
    createMany?: InventoryAlertCreateManyItemInputEnvelope
    connect?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
  }

  export type InventoryMovementUncheckedCreateNestedManyWithoutItemInput = {
    create?: XOR<InventoryMovementCreateWithoutItemInput, InventoryMovementUncheckedCreateWithoutItemInput> | InventoryMovementCreateWithoutItemInput[] | InventoryMovementUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryMovementCreateOrConnectWithoutItemInput | InventoryMovementCreateOrConnectWithoutItemInput[]
    createMany?: InventoryMovementCreateManyItemInputEnvelope
    connect?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
  }

  export type InventoryAlertUncheckedCreateNestedManyWithoutItemInput = {
    create?: XOR<InventoryAlertCreateWithoutItemInput, InventoryAlertUncheckedCreateWithoutItemInput> | InventoryAlertCreateWithoutItemInput[] | InventoryAlertUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryAlertCreateOrConnectWithoutItemInput | InventoryAlertCreateOrConnectWithoutItemInput[]
    createMany?: InventoryAlertCreateManyItemInputEnvelope
    connect?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
  }

  export type StringFieldUpdateOperationsInput = {
    set?: string
  }

  export type NullableStringFieldUpdateOperationsInput = {
    set?: string | null
  }

  export type EnumItemCategoryFieldUpdateOperationsInput = {
    set?: $Enums.ItemCategory
  }

  export type FloatFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type NullableFloatFieldUpdateOperationsInput = {
    set?: number | null
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type NullableDateTimeFieldUpdateOperationsInput = {
    set?: Date | string | null
  }

  export type DateTimeFieldUpdateOperationsInput = {
    set?: Date | string
  }

  export type InventoryMovementUpdateManyWithoutItemNestedInput = {
    create?: XOR<InventoryMovementCreateWithoutItemInput, InventoryMovementUncheckedCreateWithoutItemInput> | InventoryMovementCreateWithoutItemInput[] | InventoryMovementUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryMovementCreateOrConnectWithoutItemInput | InventoryMovementCreateOrConnectWithoutItemInput[]
    upsert?: InventoryMovementUpsertWithWhereUniqueWithoutItemInput | InventoryMovementUpsertWithWhereUniqueWithoutItemInput[]
    createMany?: InventoryMovementCreateManyItemInputEnvelope
    set?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    disconnect?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    delete?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    connect?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    update?: InventoryMovementUpdateWithWhereUniqueWithoutItemInput | InventoryMovementUpdateWithWhereUniqueWithoutItemInput[]
    updateMany?: InventoryMovementUpdateManyWithWhereWithoutItemInput | InventoryMovementUpdateManyWithWhereWithoutItemInput[]
    deleteMany?: InventoryMovementScalarWhereInput | InventoryMovementScalarWhereInput[]
  }

  export type InventoryAlertUpdateManyWithoutItemNestedInput = {
    create?: XOR<InventoryAlertCreateWithoutItemInput, InventoryAlertUncheckedCreateWithoutItemInput> | InventoryAlertCreateWithoutItemInput[] | InventoryAlertUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryAlertCreateOrConnectWithoutItemInput | InventoryAlertCreateOrConnectWithoutItemInput[]
    upsert?: InventoryAlertUpsertWithWhereUniqueWithoutItemInput | InventoryAlertUpsertWithWhereUniqueWithoutItemInput[]
    createMany?: InventoryAlertCreateManyItemInputEnvelope
    set?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    disconnect?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    delete?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    connect?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    update?: InventoryAlertUpdateWithWhereUniqueWithoutItemInput | InventoryAlertUpdateWithWhereUniqueWithoutItemInput[]
    updateMany?: InventoryAlertUpdateManyWithWhereWithoutItemInput | InventoryAlertUpdateManyWithWhereWithoutItemInput[]
    deleteMany?: InventoryAlertScalarWhereInput | InventoryAlertScalarWhereInput[]
  }

  export type InventoryMovementUncheckedUpdateManyWithoutItemNestedInput = {
    create?: XOR<InventoryMovementCreateWithoutItemInput, InventoryMovementUncheckedCreateWithoutItemInput> | InventoryMovementCreateWithoutItemInput[] | InventoryMovementUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryMovementCreateOrConnectWithoutItemInput | InventoryMovementCreateOrConnectWithoutItemInput[]
    upsert?: InventoryMovementUpsertWithWhereUniqueWithoutItemInput | InventoryMovementUpsertWithWhereUniqueWithoutItemInput[]
    createMany?: InventoryMovementCreateManyItemInputEnvelope
    set?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    disconnect?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    delete?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    connect?: InventoryMovementWhereUniqueInput | InventoryMovementWhereUniqueInput[]
    update?: InventoryMovementUpdateWithWhereUniqueWithoutItemInput | InventoryMovementUpdateWithWhereUniqueWithoutItemInput[]
    updateMany?: InventoryMovementUpdateManyWithWhereWithoutItemInput | InventoryMovementUpdateManyWithWhereWithoutItemInput[]
    deleteMany?: InventoryMovementScalarWhereInput | InventoryMovementScalarWhereInput[]
  }

  export type InventoryAlertUncheckedUpdateManyWithoutItemNestedInput = {
    create?: XOR<InventoryAlertCreateWithoutItemInput, InventoryAlertUncheckedCreateWithoutItemInput> | InventoryAlertCreateWithoutItemInput[] | InventoryAlertUncheckedCreateWithoutItemInput[]
    connectOrCreate?: InventoryAlertCreateOrConnectWithoutItemInput | InventoryAlertCreateOrConnectWithoutItemInput[]
    upsert?: InventoryAlertUpsertWithWhereUniqueWithoutItemInput | InventoryAlertUpsertWithWhereUniqueWithoutItemInput[]
    createMany?: InventoryAlertCreateManyItemInputEnvelope
    set?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    disconnect?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    delete?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    connect?: InventoryAlertWhereUniqueInput | InventoryAlertWhereUniqueInput[]
    update?: InventoryAlertUpdateWithWhereUniqueWithoutItemInput | InventoryAlertUpdateWithWhereUniqueWithoutItemInput[]
    updateMany?: InventoryAlertUpdateManyWithWhereWithoutItemInput | InventoryAlertUpdateManyWithWhereWithoutItemInput[]
    deleteMany?: InventoryAlertScalarWhereInput | InventoryAlertScalarWhereInput[]
  }

  export type InventoryItemCreateNestedOneWithoutMovementsInput = {
    create?: XOR<InventoryItemCreateWithoutMovementsInput, InventoryItemUncheckedCreateWithoutMovementsInput>
    connectOrCreate?: InventoryItemCreateOrConnectWithoutMovementsInput
    connect?: InventoryItemWhereUniqueInput
  }

  export type EnumMovementTypeFieldUpdateOperationsInput = {
    set?: $Enums.MovementType
  }

  export type InventoryItemUpdateOneRequiredWithoutMovementsNestedInput = {
    create?: XOR<InventoryItemCreateWithoutMovementsInput, InventoryItemUncheckedCreateWithoutMovementsInput>
    connectOrCreate?: InventoryItemCreateOrConnectWithoutMovementsInput
    upsert?: InventoryItemUpsertWithoutMovementsInput
    connect?: InventoryItemWhereUniqueInput
    update?: XOR<XOR<InventoryItemUpdateToOneWithWhereWithoutMovementsInput, InventoryItemUpdateWithoutMovementsInput>, InventoryItemUncheckedUpdateWithoutMovementsInput>
  }

  export type InventoryItemCreateNestedOneWithoutAlertsInput = {
    create?: XOR<InventoryItemCreateWithoutAlertsInput, InventoryItemUncheckedCreateWithoutAlertsInput>
    connectOrCreate?: InventoryItemCreateOrConnectWithoutAlertsInput
    connect?: InventoryItemWhereUniqueInput
  }

  export type EnumAlertTypeFieldUpdateOperationsInput = {
    set?: $Enums.AlertType
  }

  export type EnumAlertPriorityFieldUpdateOperationsInput = {
    set?: $Enums.AlertPriority
  }

  export type EnumAlertStatusFieldUpdateOperationsInput = {
    set?: $Enums.AlertStatus
  }

  export type InventoryItemUpdateOneRequiredWithoutAlertsNestedInput = {
    create?: XOR<InventoryItemCreateWithoutAlertsInput, InventoryItemUncheckedCreateWithoutAlertsInput>
    connectOrCreate?: InventoryItemCreateOrConnectWithoutAlertsInput
    upsert?: InventoryItemUpsertWithoutAlertsInput
    connect?: InventoryItemWhereUniqueInput
    update?: XOR<XOR<InventoryItemUpdateToOneWithWhereWithoutAlertsInput, InventoryItemUpdateWithoutAlertsInput>, InventoryItemUncheckedUpdateWithoutAlertsInput>
  }

  export type IntFieldUpdateOperationsInput = {
    set?: number
    increment?: number
    decrement?: number
    multiply?: number
    divide?: number
  }

  export type BoolFieldUpdateOperationsInput = {
    set?: boolean
  }

  export type ZoneCreateNestedManyWithoutWarehouseInput = {
    create?: XOR<ZoneCreateWithoutWarehouseInput, ZoneUncheckedCreateWithoutWarehouseInput> | ZoneCreateWithoutWarehouseInput[] | ZoneUncheckedCreateWithoutWarehouseInput[]
    connectOrCreate?: ZoneCreateOrConnectWithoutWarehouseInput | ZoneCreateOrConnectWithoutWarehouseInput[]
    createMany?: ZoneCreateManyWarehouseInputEnvelope
    connect?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
  }

  export type StockTransferCreateNestedManyWithoutFromWarehouseInput = {
    create?: XOR<StockTransferCreateWithoutFromWarehouseInput, StockTransferUncheckedCreateWithoutFromWarehouseInput> | StockTransferCreateWithoutFromWarehouseInput[] | StockTransferUncheckedCreateWithoutFromWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutFromWarehouseInput | StockTransferCreateOrConnectWithoutFromWarehouseInput[]
    createMany?: StockTransferCreateManyFromWarehouseInputEnvelope
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
  }

  export type StockTransferCreateNestedManyWithoutToWarehouseInput = {
    create?: XOR<StockTransferCreateWithoutToWarehouseInput, StockTransferUncheckedCreateWithoutToWarehouseInput> | StockTransferCreateWithoutToWarehouseInput[] | StockTransferUncheckedCreateWithoutToWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutToWarehouseInput | StockTransferCreateOrConnectWithoutToWarehouseInput[]
    createMany?: StockTransferCreateManyToWarehouseInputEnvelope
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
  }

  export type ZoneUncheckedCreateNestedManyWithoutWarehouseInput = {
    create?: XOR<ZoneCreateWithoutWarehouseInput, ZoneUncheckedCreateWithoutWarehouseInput> | ZoneCreateWithoutWarehouseInput[] | ZoneUncheckedCreateWithoutWarehouseInput[]
    connectOrCreate?: ZoneCreateOrConnectWithoutWarehouseInput | ZoneCreateOrConnectWithoutWarehouseInput[]
    createMany?: ZoneCreateManyWarehouseInputEnvelope
    connect?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
  }

  export type StockTransferUncheckedCreateNestedManyWithoutFromWarehouseInput = {
    create?: XOR<StockTransferCreateWithoutFromWarehouseInput, StockTransferUncheckedCreateWithoutFromWarehouseInput> | StockTransferCreateWithoutFromWarehouseInput[] | StockTransferUncheckedCreateWithoutFromWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutFromWarehouseInput | StockTransferCreateOrConnectWithoutFromWarehouseInput[]
    createMany?: StockTransferCreateManyFromWarehouseInputEnvelope
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
  }

  export type StockTransferUncheckedCreateNestedManyWithoutToWarehouseInput = {
    create?: XOR<StockTransferCreateWithoutToWarehouseInput, StockTransferUncheckedCreateWithoutToWarehouseInput> | StockTransferCreateWithoutToWarehouseInput[] | StockTransferUncheckedCreateWithoutToWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutToWarehouseInput | StockTransferCreateOrConnectWithoutToWarehouseInput[]
    createMany?: StockTransferCreateManyToWarehouseInputEnvelope
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
  }

  export type EnumWarehouseTypeFieldUpdateOperationsInput = {
    set?: $Enums.WarehouseType
  }

  export type EnumStorageConditionFieldUpdateOperationsInput = {
    set?: $Enums.StorageCondition
  }

  export type ZoneUpdateManyWithoutWarehouseNestedInput = {
    create?: XOR<ZoneCreateWithoutWarehouseInput, ZoneUncheckedCreateWithoutWarehouseInput> | ZoneCreateWithoutWarehouseInput[] | ZoneUncheckedCreateWithoutWarehouseInput[]
    connectOrCreate?: ZoneCreateOrConnectWithoutWarehouseInput | ZoneCreateOrConnectWithoutWarehouseInput[]
    upsert?: ZoneUpsertWithWhereUniqueWithoutWarehouseInput | ZoneUpsertWithWhereUniqueWithoutWarehouseInput[]
    createMany?: ZoneCreateManyWarehouseInputEnvelope
    set?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    disconnect?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    delete?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    connect?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    update?: ZoneUpdateWithWhereUniqueWithoutWarehouseInput | ZoneUpdateWithWhereUniqueWithoutWarehouseInput[]
    updateMany?: ZoneUpdateManyWithWhereWithoutWarehouseInput | ZoneUpdateManyWithWhereWithoutWarehouseInput[]
    deleteMany?: ZoneScalarWhereInput | ZoneScalarWhereInput[]
  }

  export type StockTransferUpdateManyWithoutFromWarehouseNestedInput = {
    create?: XOR<StockTransferCreateWithoutFromWarehouseInput, StockTransferUncheckedCreateWithoutFromWarehouseInput> | StockTransferCreateWithoutFromWarehouseInput[] | StockTransferUncheckedCreateWithoutFromWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutFromWarehouseInput | StockTransferCreateOrConnectWithoutFromWarehouseInput[]
    upsert?: StockTransferUpsertWithWhereUniqueWithoutFromWarehouseInput | StockTransferUpsertWithWhereUniqueWithoutFromWarehouseInput[]
    createMany?: StockTransferCreateManyFromWarehouseInputEnvelope
    set?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    disconnect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    delete?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    update?: StockTransferUpdateWithWhereUniqueWithoutFromWarehouseInput | StockTransferUpdateWithWhereUniqueWithoutFromWarehouseInput[]
    updateMany?: StockTransferUpdateManyWithWhereWithoutFromWarehouseInput | StockTransferUpdateManyWithWhereWithoutFromWarehouseInput[]
    deleteMany?: StockTransferScalarWhereInput | StockTransferScalarWhereInput[]
  }

  export type StockTransferUpdateManyWithoutToWarehouseNestedInput = {
    create?: XOR<StockTransferCreateWithoutToWarehouseInput, StockTransferUncheckedCreateWithoutToWarehouseInput> | StockTransferCreateWithoutToWarehouseInput[] | StockTransferUncheckedCreateWithoutToWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutToWarehouseInput | StockTransferCreateOrConnectWithoutToWarehouseInput[]
    upsert?: StockTransferUpsertWithWhereUniqueWithoutToWarehouseInput | StockTransferUpsertWithWhereUniqueWithoutToWarehouseInput[]
    createMany?: StockTransferCreateManyToWarehouseInputEnvelope
    set?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    disconnect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    delete?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    update?: StockTransferUpdateWithWhereUniqueWithoutToWarehouseInput | StockTransferUpdateWithWhereUniqueWithoutToWarehouseInput[]
    updateMany?: StockTransferUpdateManyWithWhereWithoutToWarehouseInput | StockTransferUpdateManyWithWhereWithoutToWarehouseInput[]
    deleteMany?: StockTransferScalarWhereInput | StockTransferScalarWhereInput[]
  }

  export type ZoneUncheckedUpdateManyWithoutWarehouseNestedInput = {
    create?: XOR<ZoneCreateWithoutWarehouseInput, ZoneUncheckedCreateWithoutWarehouseInput> | ZoneCreateWithoutWarehouseInput[] | ZoneUncheckedCreateWithoutWarehouseInput[]
    connectOrCreate?: ZoneCreateOrConnectWithoutWarehouseInput | ZoneCreateOrConnectWithoutWarehouseInput[]
    upsert?: ZoneUpsertWithWhereUniqueWithoutWarehouseInput | ZoneUpsertWithWhereUniqueWithoutWarehouseInput[]
    createMany?: ZoneCreateManyWarehouseInputEnvelope
    set?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    disconnect?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    delete?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    connect?: ZoneWhereUniqueInput | ZoneWhereUniqueInput[]
    update?: ZoneUpdateWithWhereUniqueWithoutWarehouseInput | ZoneUpdateWithWhereUniqueWithoutWarehouseInput[]
    updateMany?: ZoneUpdateManyWithWhereWithoutWarehouseInput | ZoneUpdateManyWithWhereWithoutWarehouseInput[]
    deleteMany?: ZoneScalarWhereInput | ZoneScalarWhereInput[]
  }

  export type StockTransferUncheckedUpdateManyWithoutFromWarehouseNestedInput = {
    create?: XOR<StockTransferCreateWithoutFromWarehouseInput, StockTransferUncheckedCreateWithoutFromWarehouseInput> | StockTransferCreateWithoutFromWarehouseInput[] | StockTransferUncheckedCreateWithoutFromWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutFromWarehouseInput | StockTransferCreateOrConnectWithoutFromWarehouseInput[]
    upsert?: StockTransferUpsertWithWhereUniqueWithoutFromWarehouseInput | StockTransferUpsertWithWhereUniqueWithoutFromWarehouseInput[]
    createMany?: StockTransferCreateManyFromWarehouseInputEnvelope
    set?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    disconnect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    delete?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    update?: StockTransferUpdateWithWhereUniqueWithoutFromWarehouseInput | StockTransferUpdateWithWhereUniqueWithoutFromWarehouseInput[]
    updateMany?: StockTransferUpdateManyWithWhereWithoutFromWarehouseInput | StockTransferUpdateManyWithWhereWithoutFromWarehouseInput[]
    deleteMany?: StockTransferScalarWhereInput | StockTransferScalarWhereInput[]
  }

  export type StockTransferUncheckedUpdateManyWithoutToWarehouseNestedInput = {
    create?: XOR<StockTransferCreateWithoutToWarehouseInput, StockTransferUncheckedCreateWithoutToWarehouseInput> | StockTransferCreateWithoutToWarehouseInput[] | StockTransferUncheckedCreateWithoutToWarehouseInput[]
    connectOrCreate?: StockTransferCreateOrConnectWithoutToWarehouseInput | StockTransferCreateOrConnectWithoutToWarehouseInput[]
    upsert?: StockTransferUpsertWithWhereUniqueWithoutToWarehouseInput | StockTransferUpsertWithWhereUniqueWithoutToWarehouseInput[]
    createMany?: StockTransferCreateManyToWarehouseInputEnvelope
    set?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    disconnect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    delete?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    connect?: StockTransferWhereUniqueInput | StockTransferWhereUniqueInput[]
    update?: StockTransferUpdateWithWhereUniqueWithoutToWarehouseInput | StockTransferUpdateWithWhereUniqueWithoutToWarehouseInput[]
    updateMany?: StockTransferUpdateManyWithWhereWithoutToWarehouseInput | StockTransferUpdateManyWithWhereWithoutToWarehouseInput[]
    deleteMany?: StockTransferScalarWhereInput | StockTransferScalarWhereInput[]
  }

  export type WarehouseCreateNestedOneWithoutZonesInput = {
    create?: XOR<WarehouseCreateWithoutZonesInput, WarehouseUncheckedCreateWithoutZonesInput>
    connectOrCreate?: WarehouseCreateOrConnectWithoutZonesInput
    connect?: WarehouseWhereUniqueInput
  }

  export type StorageLocationCreateNestedManyWithoutZoneInput = {
    create?: XOR<StorageLocationCreateWithoutZoneInput, StorageLocationUncheckedCreateWithoutZoneInput> | StorageLocationCreateWithoutZoneInput[] | StorageLocationUncheckedCreateWithoutZoneInput[]
    connectOrCreate?: StorageLocationCreateOrConnectWithoutZoneInput | StorageLocationCreateOrConnectWithoutZoneInput[]
    createMany?: StorageLocationCreateManyZoneInputEnvelope
    connect?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
  }

  export type StorageLocationUncheckedCreateNestedManyWithoutZoneInput = {
    create?: XOR<StorageLocationCreateWithoutZoneInput, StorageLocationUncheckedCreateWithoutZoneInput> | StorageLocationCreateWithoutZoneInput[] | StorageLocationUncheckedCreateWithoutZoneInput[]
    connectOrCreate?: StorageLocationCreateOrConnectWithoutZoneInput | StorageLocationCreateOrConnectWithoutZoneInput[]
    createMany?: StorageLocationCreateManyZoneInputEnvelope
    connect?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
  }

  export type NullableEnumStorageConditionFieldUpdateOperationsInput = {
    set?: $Enums.StorageCondition | null
  }

  export type WarehouseUpdateOneRequiredWithoutZonesNestedInput = {
    create?: XOR<WarehouseCreateWithoutZonesInput, WarehouseUncheckedCreateWithoutZonesInput>
    connectOrCreate?: WarehouseCreateOrConnectWithoutZonesInput
    upsert?: WarehouseUpsertWithoutZonesInput
    connect?: WarehouseWhereUniqueInput
    update?: XOR<XOR<WarehouseUpdateToOneWithWhereWithoutZonesInput, WarehouseUpdateWithoutZonesInput>, WarehouseUncheckedUpdateWithoutZonesInput>
  }

  export type StorageLocationUpdateManyWithoutZoneNestedInput = {
    create?: XOR<StorageLocationCreateWithoutZoneInput, StorageLocationUncheckedCreateWithoutZoneInput> | StorageLocationCreateWithoutZoneInput[] | StorageLocationUncheckedCreateWithoutZoneInput[]
    connectOrCreate?: StorageLocationCreateOrConnectWithoutZoneInput | StorageLocationCreateOrConnectWithoutZoneInput[]
    upsert?: StorageLocationUpsertWithWhereUniqueWithoutZoneInput | StorageLocationUpsertWithWhereUniqueWithoutZoneInput[]
    createMany?: StorageLocationCreateManyZoneInputEnvelope
    set?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    disconnect?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    delete?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    connect?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    update?: StorageLocationUpdateWithWhereUniqueWithoutZoneInput | StorageLocationUpdateWithWhereUniqueWithoutZoneInput[]
    updateMany?: StorageLocationUpdateManyWithWhereWithoutZoneInput | StorageLocationUpdateManyWithWhereWithoutZoneInput[]
    deleteMany?: StorageLocationScalarWhereInput | StorageLocationScalarWhereInput[]
  }

  export type StorageLocationUncheckedUpdateManyWithoutZoneNestedInput = {
    create?: XOR<StorageLocationCreateWithoutZoneInput, StorageLocationUncheckedCreateWithoutZoneInput> | StorageLocationCreateWithoutZoneInput[] | StorageLocationUncheckedCreateWithoutZoneInput[]
    connectOrCreate?: StorageLocationCreateOrConnectWithoutZoneInput | StorageLocationCreateOrConnectWithoutZoneInput[]
    upsert?: StorageLocationUpsertWithWhereUniqueWithoutZoneInput | StorageLocationUpsertWithWhereUniqueWithoutZoneInput[]
    createMany?: StorageLocationCreateManyZoneInputEnvelope
    set?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    disconnect?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    delete?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    connect?: StorageLocationWhereUniqueInput | StorageLocationWhereUniqueInput[]
    update?: StorageLocationUpdateWithWhereUniqueWithoutZoneInput | StorageLocationUpdateWithWhereUniqueWithoutZoneInput[]
    updateMany?: StorageLocationUpdateManyWithWhereWithoutZoneInput | StorageLocationUpdateManyWithWhereWithoutZoneInput[]
    deleteMany?: StorageLocationScalarWhereInput | StorageLocationScalarWhereInput[]
  }

  export type ZoneCreateNestedOneWithoutLocationsInput = {
    create?: XOR<ZoneCreateWithoutLocationsInput, ZoneUncheckedCreateWithoutLocationsInput>
    connectOrCreate?: ZoneCreateOrConnectWithoutLocationsInput
    connect?: ZoneWhereUniqueInput
  }

  export type ZoneUpdateOneRequiredWithoutLocationsNestedInput = {
    create?: XOR<ZoneCreateWithoutLocationsInput, ZoneUncheckedCreateWithoutLocationsInput>
    connectOrCreate?: ZoneCreateOrConnectWithoutLocationsInput
    upsert?: ZoneUpsertWithoutLocationsInput
    connect?: ZoneWhereUniqueInput
    update?: XOR<XOR<ZoneUpdateToOneWithWhereWithoutLocationsInput, ZoneUpdateWithoutLocationsInput>, ZoneUncheckedUpdateWithoutLocationsInput>
  }

  export type WarehouseCreateNestedOneWithoutTransfersFromInput = {
    create?: XOR<WarehouseCreateWithoutTransfersFromInput, WarehouseUncheckedCreateWithoutTransfersFromInput>
    connectOrCreate?: WarehouseCreateOrConnectWithoutTransfersFromInput
    connect?: WarehouseWhereUniqueInput
  }

  export type WarehouseCreateNestedOneWithoutTransfersToInput = {
    create?: XOR<WarehouseCreateWithoutTransfersToInput, WarehouseUncheckedCreateWithoutTransfersToInput>
    connectOrCreate?: WarehouseCreateOrConnectWithoutTransfersToInput
    connect?: WarehouseWhereUniqueInput
  }

  export type EnumTransferTypeFieldUpdateOperationsInput = {
    set?: $Enums.TransferType
  }

  export type EnumTransferStatusFieldUpdateOperationsInput = {
    set?: $Enums.TransferStatus
  }

  export type WarehouseUpdateOneWithoutTransfersFromNestedInput = {
    create?: XOR<WarehouseCreateWithoutTransfersFromInput, WarehouseUncheckedCreateWithoutTransfersFromInput>
    connectOrCreate?: WarehouseCreateOrConnectWithoutTransfersFromInput
    upsert?: WarehouseUpsertWithoutTransfersFromInput
    disconnect?: WarehouseWhereInput | boolean
    delete?: WarehouseWhereInput | boolean
    connect?: WarehouseWhereUniqueInput
    update?: XOR<XOR<WarehouseUpdateToOneWithWhereWithoutTransfersFromInput, WarehouseUpdateWithoutTransfersFromInput>, WarehouseUncheckedUpdateWithoutTransfersFromInput>
  }

  export type WarehouseUpdateOneRequiredWithoutTransfersToNestedInput = {
    create?: XOR<WarehouseCreateWithoutTransfersToInput, WarehouseUncheckedCreateWithoutTransfersToInput>
    connectOrCreate?: WarehouseCreateOrConnectWithoutTransfersToInput
    upsert?: WarehouseUpsertWithoutTransfersToInput
    connect?: WarehouseWhereUniqueInput
    update?: XOR<XOR<WarehouseUpdateToOneWithWhereWithoutTransfersToInput, WarehouseUpdateWithoutTransfersToInput>, WarehouseUncheckedUpdateWithoutTransfersToInput>
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

  export type NestedEnumItemCategoryFilter<$PrismaModel = never> = {
    equals?: $Enums.ItemCategory | EnumItemCategoryFieldRefInput<$PrismaModel>
    in?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    notIn?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    not?: NestedEnumItemCategoryFilter<$PrismaModel> | $Enums.ItemCategory
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

  export type NestedEnumItemCategoryWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.ItemCategory | EnumItemCategoryFieldRefInput<$PrismaModel>
    in?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    notIn?: $Enums.ItemCategory[] | ListEnumItemCategoryFieldRefInput<$PrismaModel>
    not?: NestedEnumItemCategoryWithAggregatesFilter<$PrismaModel> | $Enums.ItemCategory
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumItemCategoryFilter<$PrismaModel>
    _max?: NestedEnumItemCategoryFilter<$PrismaModel>
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

  export type NestedEnumMovementTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.MovementType | EnumMovementTypeFieldRefInput<$PrismaModel>
    in?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumMovementTypeFilter<$PrismaModel> | $Enums.MovementType
  }

  export type NestedEnumMovementTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.MovementType | EnumMovementTypeFieldRefInput<$PrismaModel>
    in?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.MovementType[] | ListEnumMovementTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumMovementTypeWithAggregatesFilter<$PrismaModel> | $Enums.MovementType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumMovementTypeFilter<$PrismaModel>
    _max?: NestedEnumMovementTypeFilter<$PrismaModel>
  }

  export type NestedEnumAlertTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertType | EnumAlertTypeFieldRefInput<$PrismaModel>
    in?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertType[] | ListEnumAlertTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertTypeFilter<$PrismaModel> | $Enums.AlertType
  }

  export type NestedEnumAlertPriorityFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertPriority | EnumAlertPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertPriorityFilter<$PrismaModel> | $Enums.AlertPriority
  }

  export type NestedEnumAlertStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertStatus | EnumAlertStatusFieldRefInput<$PrismaModel>
    in?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertStatusFilter<$PrismaModel> | $Enums.AlertStatus
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

  export type NestedEnumAlertPriorityWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertPriority | EnumAlertPriorityFieldRefInput<$PrismaModel>
    in?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertPriority[] | ListEnumAlertPriorityFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertPriorityWithAggregatesFilter<$PrismaModel> | $Enums.AlertPriority
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertPriorityFilter<$PrismaModel>
    _max?: NestedEnumAlertPriorityFilter<$PrismaModel>
  }

  export type NestedEnumAlertStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.AlertStatus | EnumAlertStatusFieldRefInput<$PrismaModel>
    in?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.AlertStatus[] | ListEnumAlertStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumAlertStatusWithAggregatesFilter<$PrismaModel> | $Enums.AlertStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumAlertStatusFilter<$PrismaModel>
    _max?: NestedEnumAlertStatusFilter<$PrismaModel>
  }

  export type NestedBoolFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolFilter<$PrismaModel> | boolean
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

  export type NestedBoolWithAggregatesFilter<$PrismaModel = never> = {
    equals?: boolean | BooleanFieldRefInput<$PrismaModel>
    not?: NestedBoolWithAggregatesFilter<$PrismaModel> | boolean
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedBoolFilter<$PrismaModel>
    _max?: NestedBoolFilter<$PrismaModel>
  }

  export type NestedEnumWarehouseTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.WarehouseType | EnumWarehouseTypeFieldRefInput<$PrismaModel>
    in?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumWarehouseTypeFilter<$PrismaModel> | $Enums.WarehouseType
  }

  export type NestedEnumStorageConditionFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel>
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    not?: NestedEnumStorageConditionFilter<$PrismaModel> | $Enums.StorageCondition
  }

  export type NestedEnumWarehouseTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.WarehouseType | EnumWarehouseTypeFieldRefInput<$PrismaModel>
    in?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.WarehouseType[] | ListEnumWarehouseTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumWarehouseTypeWithAggregatesFilter<$PrismaModel> | $Enums.WarehouseType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumWarehouseTypeFilter<$PrismaModel>
    _max?: NestedEnumWarehouseTypeFilter<$PrismaModel>
  }

  export type NestedEnumStorageConditionWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel>
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel>
    not?: NestedEnumStorageConditionWithAggregatesFilter<$PrismaModel> | $Enums.StorageCondition
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumStorageConditionFilter<$PrismaModel>
    _max?: NestedEnumStorageConditionFilter<$PrismaModel>
  }

  export type NestedEnumStorageConditionNullableFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel> | null
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    not?: NestedEnumStorageConditionNullableFilter<$PrismaModel> | $Enums.StorageCondition | null
  }

  export type NestedEnumStorageConditionNullableWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.StorageCondition | EnumStorageConditionFieldRefInput<$PrismaModel> | null
    in?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    notIn?: $Enums.StorageCondition[] | ListEnumStorageConditionFieldRefInput<$PrismaModel> | null
    not?: NestedEnumStorageConditionNullableWithAggregatesFilter<$PrismaModel> | $Enums.StorageCondition | null
    _count?: NestedIntNullableFilter<$PrismaModel>
    _min?: NestedEnumStorageConditionNullableFilter<$PrismaModel>
    _max?: NestedEnumStorageConditionNullableFilter<$PrismaModel>
  }

  export type NestedEnumTransferTypeFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferType | EnumTransferTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferTypeFilter<$PrismaModel> | $Enums.TransferType
  }

  export type NestedEnumTransferStatusFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferStatus | EnumTransferStatusFieldRefInput<$PrismaModel>
    in?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferStatusFilter<$PrismaModel> | $Enums.TransferStatus
  }

  export type NestedEnumTransferTypeWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferType | EnumTransferTypeFieldRefInput<$PrismaModel>
    in?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferType[] | ListEnumTransferTypeFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferTypeWithAggregatesFilter<$PrismaModel> | $Enums.TransferType
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTransferTypeFilter<$PrismaModel>
    _max?: NestedEnumTransferTypeFilter<$PrismaModel>
  }

  export type NestedEnumTransferStatusWithAggregatesFilter<$PrismaModel = never> = {
    equals?: $Enums.TransferStatus | EnumTransferStatusFieldRefInput<$PrismaModel>
    in?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    notIn?: $Enums.TransferStatus[] | ListEnumTransferStatusFieldRefInput<$PrismaModel>
    not?: NestedEnumTransferStatusWithAggregatesFilter<$PrismaModel> | $Enums.TransferStatus
    _count?: NestedIntFilter<$PrismaModel>
    _min?: NestedEnumTransferStatusFilter<$PrismaModel>
    _max?: NestedEnumTransferStatusFilter<$PrismaModel>
  }

  export type InventoryMovementCreateWithoutItemInput = {
    id?: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost?: number | null
    referenceId?: string | null
    referenceType?: string | null
    fromLocation?: string | null
    toLocation?: string | null
    notes?: string | null
    notesAr?: string | null
    performedBy: string
    createdAt?: Date | string
  }

  export type InventoryMovementUncheckedCreateWithoutItemInput = {
    id?: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost?: number | null
    referenceId?: string | null
    referenceType?: string | null
    fromLocation?: string | null
    toLocation?: string | null
    notes?: string | null
    notesAr?: string | null
    performedBy: string
    createdAt?: Date | string
  }

  export type InventoryMovementCreateOrConnectWithoutItemInput = {
    where: InventoryMovementWhereUniqueInput
    create: XOR<InventoryMovementCreateWithoutItemInput, InventoryMovementUncheckedCreateWithoutItemInput>
  }

  export type InventoryMovementCreateManyItemInputEnvelope = {
    data: InventoryMovementCreateManyItemInput | InventoryMovementCreateManyItemInput[]
    skipDuplicates?: boolean
  }

  export type InventoryAlertCreateWithoutItemInput = {
    id?: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status?: $Enums.AlertStatus
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl?: string | null
    createdAt?: Date | string
    acknowledgedAt?: Date | string | null
    acknowledgedBy?: string | null
    resolvedAt?: Date | string | null
    resolvedBy?: string | null
    resolutionNotes?: string | null
    snoozeUntil?: Date | string | null
  }

  export type InventoryAlertUncheckedCreateWithoutItemInput = {
    id?: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status?: $Enums.AlertStatus
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl?: string | null
    createdAt?: Date | string
    acknowledgedAt?: Date | string | null
    acknowledgedBy?: string | null
    resolvedAt?: Date | string | null
    resolvedBy?: string | null
    resolutionNotes?: string | null
    snoozeUntil?: Date | string | null
  }

  export type InventoryAlertCreateOrConnectWithoutItemInput = {
    where: InventoryAlertWhereUniqueInput
    create: XOR<InventoryAlertCreateWithoutItemInput, InventoryAlertUncheckedCreateWithoutItemInput>
  }

  export type InventoryAlertCreateManyItemInputEnvelope = {
    data: InventoryAlertCreateManyItemInput | InventoryAlertCreateManyItemInput[]
    skipDuplicates?: boolean
  }

  export type InventoryMovementUpsertWithWhereUniqueWithoutItemInput = {
    where: InventoryMovementWhereUniqueInput
    update: XOR<InventoryMovementUpdateWithoutItemInput, InventoryMovementUncheckedUpdateWithoutItemInput>
    create: XOR<InventoryMovementCreateWithoutItemInput, InventoryMovementUncheckedCreateWithoutItemInput>
  }

  export type InventoryMovementUpdateWithWhereUniqueWithoutItemInput = {
    where: InventoryMovementWhereUniqueInput
    data: XOR<InventoryMovementUpdateWithoutItemInput, InventoryMovementUncheckedUpdateWithoutItemInput>
  }

  export type InventoryMovementUpdateManyWithWhereWithoutItemInput = {
    where: InventoryMovementScalarWhereInput
    data: XOR<InventoryMovementUpdateManyMutationInput, InventoryMovementUncheckedUpdateManyWithoutItemInput>
  }

  export type InventoryMovementScalarWhereInput = {
    AND?: InventoryMovementScalarWhereInput | InventoryMovementScalarWhereInput[]
    OR?: InventoryMovementScalarWhereInput[]
    NOT?: InventoryMovementScalarWhereInput | InventoryMovementScalarWhereInput[]
    id?: StringFilter<"InventoryMovement"> | string
    itemId?: StringFilter<"InventoryMovement"> | string
    tenantId?: StringFilter<"InventoryMovement"> | string
    type?: EnumMovementTypeFilter<"InventoryMovement"> | $Enums.MovementType
    quantity?: FloatFilter<"InventoryMovement"> | number
    unitCost?: FloatNullableFilter<"InventoryMovement"> | number | null
    referenceId?: StringNullableFilter<"InventoryMovement"> | string | null
    referenceType?: StringNullableFilter<"InventoryMovement"> | string | null
    fromLocation?: StringNullableFilter<"InventoryMovement"> | string | null
    toLocation?: StringNullableFilter<"InventoryMovement"> | string | null
    notes?: StringNullableFilter<"InventoryMovement"> | string | null
    notesAr?: StringNullableFilter<"InventoryMovement"> | string | null
    performedBy?: StringFilter<"InventoryMovement"> | string
    createdAt?: DateTimeFilter<"InventoryMovement"> | Date | string
  }

  export type InventoryAlertUpsertWithWhereUniqueWithoutItemInput = {
    where: InventoryAlertWhereUniqueInput
    update: XOR<InventoryAlertUpdateWithoutItemInput, InventoryAlertUncheckedUpdateWithoutItemInput>
    create: XOR<InventoryAlertCreateWithoutItemInput, InventoryAlertUncheckedCreateWithoutItemInput>
  }

  export type InventoryAlertUpdateWithWhereUniqueWithoutItemInput = {
    where: InventoryAlertWhereUniqueInput
    data: XOR<InventoryAlertUpdateWithoutItemInput, InventoryAlertUncheckedUpdateWithoutItemInput>
  }

  export type InventoryAlertUpdateManyWithWhereWithoutItemInput = {
    where: InventoryAlertScalarWhereInput
    data: XOR<InventoryAlertUpdateManyMutationInput, InventoryAlertUncheckedUpdateManyWithoutItemInput>
  }

  export type InventoryAlertScalarWhereInput = {
    AND?: InventoryAlertScalarWhereInput | InventoryAlertScalarWhereInput[]
    OR?: InventoryAlertScalarWhereInput[]
    NOT?: InventoryAlertScalarWhereInput | InventoryAlertScalarWhereInput[]
    id?: StringFilter<"InventoryAlert"> | string
    alertType?: EnumAlertTypeFilter<"InventoryAlert"> | $Enums.AlertType
    priority?: EnumAlertPriorityFilter<"InventoryAlert"> | $Enums.AlertPriority
    status?: EnumAlertStatusFilter<"InventoryAlert"> | $Enums.AlertStatus
    itemId?: StringFilter<"InventoryAlert"> | string
    itemName?: StringFilter<"InventoryAlert"> | string
    itemNameAr?: StringFilter<"InventoryAlert"> | string
    titleEn?: StringFilter<"InventoryAlert"> | string
    titleAr?: StringFilter<"InventoryAlert"> | string
    messageEn?: StringFilter<"InventoryAlert"> | string
    messageAr?: StringFilter<"InventoryAlert"> | string
    currentValue?: FloatFilter<"InventoryAlert"> | number
    thresholdValue?: FloatFilter<"InventoryAlert"> | number
    recommendedActionEn?: StringFilter<"InventoryAlert"> | string
    recommendedActionAr?: StringFilter<"InventoryAlert"> | string
    actionUrl?: StringNullableFilter<"InventoryAlert"> | string | null
    createdAt?: DateTimeFilter<"InventoryAlert"> | Date | string
    acknowledgedAt?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    acknowledgedBy?: StringNullableFilter<"InventoryAlert"> | string | null
    resolvedAt?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
    resolvedBy?: StringNullableFilter<"InventoryAlert"> | string | null
    resolutionNotes?: StringNullableFilter<"InventoryAlert"> | string | null
    snoozeUntil?: DateTimeNullableFilter<"InventoryAlert"> | Date | string | null
  }

  export type InventoryItemCreateWithoutMovementsInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
    alerts?: InventoryAlertCreateNestedManyWithoutItemInput
  }

  export type InventoryItemUncheckedCreateWithoutMovementsInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
    alerts?: InventoryAlertUncheckedCreateNestedManyWithoutItemInput
  }

  export type InventoryItemCreateOrConnectWithoutMovementsInput = {
    where: InventoryItemWhereUniqueInput
    create: XOR<InventoryItemCreateWithoutMovementsInput, InventoryItemUncheckedCreateWithoutMovementsInput>
  }

  export type InventoryItemUpsertWithoutMovementsInput = {
    update: XOR<InventoryItemUpdateWithoutMovementsInput, InventoryItemUncheckedUpdateWithoutMovementsInput>
    create: XOR<InventoryItemCreateWithoutMovementsInput, InventoryItemUncheckedCreateWithoutMovementsInput>
    where?: InventoryItemWhereInput
  }

  export type InventoryItemUpdateToOneWithWhereWithoutMovementsInput = {
    where?: InventoryItemWhereInput
    data: XOR<InventoryItemUpdateWithoutMovementsInput, InventoryItemUncheckedUpdateWithoutMovementsInput>
  }

  export type InventoryItemUpdateWithoutMovementsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    alerts?: InventoryAlertUpdateManyWithoutItemNestedInput
  }

  export type InventoryItemUncheckedUpdateWithoutMovementsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    alerts?: InventoryAlertUncheckedUpdateManyWithoutItemNestedInput
  }

  export type InventoryItemCreateWithoutAlertsInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
    movements?: InventoryMovementCreateNestedManyWithoutItemInput
  }

  export type InventoryItemUncheckedCreateWithoutAlertsInput = {
    id?: string
    tenantId: string
    name: string
    nameAr: string
    sku?: string | null
    category: $Enums.ItemCategory
    description?: string | null
    descriptionAr?: string | null
    quantity?: number
    unit: string
    reorderLevel?: number
    reorderPoint?: number | null
    maxStock?: number | null
    unitCost?: number | null
    sellingPrice?: number | null
    location?: string | null
    batchNumber?: string | null
    expiryDate?: Date | string | null
    minTemperature?: number | null
    maxTemperature?: number | null
    minHumidity?: number | null
    maxHumidity?: number | null
    supplier?: string | null
    barcode?: string | null
    imageUrl?: string | null
    notes?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    lastRestocked?: Date | string | null
    movements?: InventoryMovementUncheckedCreateNestedManyWithoutItemInput
  }

  export type InventoryItemCreateOrConnectWithoutAlertsInput = {
    where: InventoryItemWhereUniqueInput
    create: XOR<InventoryItemCreateWithoutAlertsInput, InventoryItemUncheckedCreateWithoutAlertsInput>
  }

  export type InventoryItemUpsertWithoutAlertsInput = {
    update: XOR<InventoryItemUpdateWithoutAlertsInput, InventoryItemUncheckedUpdateWithoutAlertsInput>
    create: XOR<InventoryItemCreateWithoutAlertsInput, InventoryItemUncheckedCreateWithoutAlertsInput>
    where?: InventoryItemWhereInput
  }

  export type InventoryItemUpdateToOneWithWhereWithoutAlertsInput = {
    where?: InventoryItemWhereInput
    data: XOR<InventoryItemUpdateWithoutAlertsInput, InventoryItemUncheckedUpdateWithoutAlertsInput>
  }

  export type InventoryItemUpdateWithoutAlertsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    movements?: InventoryMovementUpdateManyWithoutItemNestedInput
  }

  export type InventoryItemUncheckedUpdateWithoutAlertsInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    sku?: NullableStringFieldUpdateOperationsInput | string | null
    category?: EnumItemCategoryFieldUpdateOperationsInput | $Enums.ItemCategory
    description?: NullableStringFieldUpdateOperationsInput | string | null
    descriptionAr?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unit?: StringFieldUpdateOperationsInput | string
    reorderLevel?: FloatFieldUpdateOperationsInput | number
    reorderPoint?: NullableFloatFieldUpdateOperationsInput | number | null
    maxStock?: NullableFloatFieldUpdateOperationsInput | number | null
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    sellingPrice?: NullableFloatFieldUpdateOperationsInput | number | null
    location?: NullableStringFieldUpdateOperationsInput | string | null
    batchNumber?: NullableStringFieldUpdateOperationsInput | string | null
    expiryDate?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    minTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    maxTemperature?: NullableFloatFieldUpdateOperationsInput | number | null
    minHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    maxHumidity?: NullableFloatFieldUpdateOperationsInput | number | null
    supplier?: NullableStringFieldUpdateOperationsInput | string | null
    barcode?: NullableStringFieldUpdateOperationsInput | string | null
    imageUrl?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    lastRestocked?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    movements?: InventoryMovementUncheckedUpdateManyWithoutItemNestedInput
  }

  export type ZoneCreateWithoutWarehouseInput = {
    id?: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
    locations?: StorageLocationCreateNestedManyWithoutZoneInput
  }

  export type ZoneUncheckedCreateWithoutWarehouseInput = {
    id?: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
    locations?: StorageLocationUncheckedCreateNestedManyWithoutZoneInput
  }

  export type ZoneCreateOrConnectWithoutWarehouseInput = {
    where: ZoneWhereUniqueInput
    create: XOR<ZoneCreateWithoutWarehouseInput, ZoneUncheckedCreateWithoutWarehouseInput>
  }

  export type ZoneCreateManyWarehouseInputEnvelope = {
    data: ZoneCreateManyWarehouseInput | ZoneCreateManyWarehouseInput[]
    skipDuplicates?: boolean
  }

  export type StockTransferCreateWithoutFromWarehouseInput = {
    id?: string
    itemId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
    toWarehouse: WarehouseCreateNestedOneWithoutTransfersToInput
  }

  export type StockTransferUncheckedCreateWithoutFromWarehouseInput = {
    id?: string
    itemId: string
    toWarehouseId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
  }

  export type StockTransferCreateOrConnectWithoutFromWarehouseInput = {
    where: StockTransferWhereUniqueInput
    create: XOR<StockTransferCreateWithoutFromWarehouseInput, StockTransferUncheckedCreateWithoutFromWarehouseInput>
  }

  export type StockTransferCreateManyFromWarehouseInputEnvelope = {
    data: StockTransferCreateManyFromWarehouseInput | StockTransferCreateManyFromWarehouseInput[]
    skipDuplicates?: boolean
  }

  export type StockTransferCreateWithoutToWarehouseInput = {
    id?: string
    itemId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
    fromWarehouse?: WarehouseCreateNestedOneWithoutTransfersFromInput
  }

  export type StockTransferUncheckedCreateWithoutToWarehouseInput = {
    id?: string
    itemId: string
    fromWarehouseId?: string | null
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
  }

  export type StockTransferCreateOrConnectWithoutToWarehouseInput = {
    where: StockTransferWhereUniqueInput
    create: XOR<StockTransferCreateWithoutToWarehouseInput, StockTransferUncheckedCreateWithoutToWarehouseInput>
  }

  export type StockTransferCreateManyToWarehouseInputEnvelope = {
    data: StockTransferCreateManyToWarehouseInput | StockTransferCreateManyToWarehouseInput[]
    skipDuplicates?: boolean
  }

  export type ZoneUpsertWithWhereUniqueWithoutWarehouseInput = {
    where: ZoneWhereUniqueInput
    update: XOR<ZoneUpdateWithoutWarehouseInput, ZoneUncheckedUpdateWithoutWarehouseInput>
    create: XOR<ZoneCreateWithoutWarehouseInput, ZoneUncheckedCreateWithoutWarehouseInput>
  }

  export type ZoneUpdateWithWhereUniqueWithoutWarehouseInput = {
    where: ZoneWhereUniqueInput
    data: XOR<ZoneUpdateWithoutWarehouseInput, ZoneUncheckedUpdateWithoutWarehouseInput>
  }

  export type ZoneUpdateManyWithWhereWithoutWarehouseInput = {
    where: ZoneScalarWhereInput
    data: XOR<ZoneUpdateManyMutationInput, ZoneUncheckedUpdateManyWithoutWarehouseInput>
  }

  export type ZoneScalarWhereInput = {
    AND?: ZoneScalarWhereInput | ZoneScalarWhereInput[]
    OR?: ZoneScalarWhereInput[]
    NOT?: ZoneScalarWhereInput | ZoneScalarWhereInput[]
    id?: StringFilter<"Zone"> | string
    warehouseId?: StringFilter<"Zone"> | string
    name?: StringFilter<"Zone"> | string
    nameAr?: StringNullableFilter<"Zone"> | string | null
    capacity?: FloatFilter<"Zone"> | number
    currentUsage?: FloatFilter<"Zone"> | number
    condition?: EnumStorageConditionNullableFilter<"Zone"> | $Enums.StorageCondition | null
    createdAt?: DateTimeFilter<"Zone"> | Date | string
    updatedAt?: DateTimeFilter<"Zone"> | Date | string
  }

  export type StockTransferUpsertWithWhereUniqueWithoutFromWarehouseInput = {
    where: StockTransferWhereUniqueInput
    update: XOR<StockTransferUpdateWithoutFromWarehouseInput, StockTransferUncheckedUpdateWithoutFromWarehouseInput>
    create: XOR<StockTransferCreateWithoutFromWarehouseInput, StockTransferUncheckedCreateWithoutFromWarehouseInput>
  }

  export type StockTransferUpdateWithWhereUniqueWithoutFromWarehouseInput = {
    where: StockTransferWhereUniqueInput
    data: XOR<StockTransferUpdateWithoutFromWarehouseInput, StockTransferUncheckedUpdateWithoutFromWarehouseInput>
  }

  export type StockTransferUpdateManyWithWhereWithoutFromWarehouseInput = {
    where: StockTransferScalarWhereInput
    data: XOR<StockTransferUpdateManyMutationInput, StockTransferUncheckedUpdateManyWithoutFromWarehouseInput>
  }

  export type StockTransferScalarWhereInput = {
    AND?: StockTransferScalarWhereInput | StockTransferScalarWhereInput[]
    OR?: StockTransferScalarWhereInput[]
    NOT?: StockTransferScalarWhereInput | StockTransferScalarWhereInput[]
    id?: StringFilter<"StockTransfer"> | string
    itemId?: StringFilter<"StockTransfer"> | string
    fromWarehouseId?: StringNullableFilter<"StockTransfer"> | string | null
    toWarehouseId?: StringFilter<"StockTransfer"> | string
    quantity?: FloatFilter<"StockTransfer"> | number
    unitCost?: FloatNullableFilter<"StockTransfer"> | number | null
    totalCost?: FloatNullableFilter<"StockTransfer"> | number | null
    transferType?: EnumTransferTypeFilter<"StockTransfer"> | $Enums.TransferType
    status?: EnumTransferStatusFilter<"StockTransfer"> | $Enums.TransferStatus
    requestedBy?: StringFilter<"StockTransfer"> | string
    approvedBy?: StringNullableFilter<"StockTransfer"> | string | null
    performedBy?: StringNullableFilter<"StockTransfer"> | string | null
    requestedAt?: DateTimeFilter<"StockTransfer"> | Date | string
    approvedAt?: DateTimeNullableFilter<"StockTransfer"> | Date | string | null
    completedAt?: DateTimeNullableFilter<"StockTransfer"> | Date | string | null
    notes?: StringNullableFilter<"StockTransfer"> | string | null
  }

  export type StockTransferUpsertWithWhereUniqueWithoutToWarehouseInput = {
    where: StockTransferWhereUniqueInput
    update: XOR<StockTransferUpdateWithoutToWarehouseInput, StockTransferUncheckedUpdateWithoutToWarehouseInput>
    create: XOR<StockTransferCreateWithoutToWarehouseInput, StockTransferUncheckedCreateWithoutToWarehouseInput>
  }

  export type StockTransferUpdateWithWhereUniqueWithoutToWarehouseInput = {
    where: StockTransferWhereUniqueInput
    data: XOR<StockTransferUpdateWithoutToWarehouseInput, StockTransferUncheckedUpdateWithoutToWarehouseInput>
  }

  export type StockTransferUpdateManyWithWhereWithoutToWarehouseInput = {
    where: StockTransferScalarWhereInput
    data: XOR<StockTransferUpdateManyMutationInput, StockTransferUncheckedUpdateManyWithoutToWarehouseInput>
  }

  export type WarehouseCreateWithoutZonesInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    transfersFrom?: StockTransferCreateNestedManyWithoutFromWarehouseInput
    transfersTo?: StockTransferCreateNestedManyWithoutToWarehouseInput
  }

  export type WarehouseUncheckedCreateWithoutZonesInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    transfersFrom?: StockTransferUncheckedCreateNestedManyWithoutFromWarehouseInput
    transfersTo?: StockTransferUncheckedCreateNestedManyWithoutToWarehouseInput
  }

  export type WarehouseCreateOrConnectWithoutZonesInput = {
    where: WarehouseWhereUniqueInput
    create: XOR<WarehouseCreateWithoutZonesInput, WarehouseUncheckedCreateWithoutZonesInput>
  }

  export type StorageLocationCreateWithoutZoneInput = {
    id?: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied?: boolean
    currentItemId?: string | null
    currentQty?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type StorageLocationUncheckedCreateWithoutZoneInput = {
    id?: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied?: boolean
    currentItemId?: string | null
    currentQty?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type StorageLocationCreateOrConnectWithoutZoneInput = {
    where: StorageLocationWhereUniqueInput
    create: XOR<StorageLocationCreateWithoutZoneInput, StorageLocationUncheckedCreateWithoutZoneInput>
  }

  export type StorageLocationCreateManyZoneInputEnvelope = {
    data: StorageLocationCreateManyZoneInput | StorageLocationCreateManyZoneInput[]
    skipDuplicates?: boolean
  }

  export type WarehouseUpsertWithoutZonesInput = {
    update: XOR<WarehouseUpdateWithoutZonesInput, WarehouseUncheckedUpdateWithoutZonesInput>
    create: XOR<WarehouseCreateWithoutZonesInput, WarehouseUncheckedCreateWithoutZonesInput>
    where?: WarehouseWhereInput
  }

  export type WarehouseUpdateToOneWithWhereWithoutZonesInput = {
    where?: WarehouseWhereInput
    data: XOR<WarehouseUpdateWithoutZonesInput, WarehouseUncheckedUpdateWithoutZonesInput>
  }

  export type WarehouseUpdateWithoutZonesInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    transfersFrom?: StockTransferUpdateManyWithoutFromWarehouseNestedInput
    transfersTo?: StockTransferUpdateManyWithoutToWarehouseNestedInput
  }

  export type WarehouseUncheckedUpdateWithoutZonesInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    transfersFrom?: StockTransferUncheckedUpdateManyWithoutFromWarehouseNestedInput
    transfersTo?: StockTransferUncheckedUpdateManyWithoutToWarehouseNestedInput
  }

  export type StorageLocationUpsertWithWhereUniqueWithoutZoneInput = {
    where: StorageLocationWhereUniqueInput
    update: XOR<StorageLocationUpdateWithoutZoneInput, StorageLocationUncheckedUpdateWithoutZoneInput>
    create: XOR<StorageLocationCreateWithoutZoneInput, StorageLocationUncheckedCreateWithoutZoneInput>
  }

  export type StorageLocationUpdateWithWhereUniqueWithoutZoneInput = {
    where: StorageLocationWhereUniqueInput
    data: XOR<StorageLocationUpdateWithoutZoneInput, StorageLocationUncheckedUpdateWithoutZoneInput>
  }

  export type StorageLocationUpdateManyWithWhereWithoutZoneInput = {
    where: StorageLocationScalarWhereInput
    data: XOR<StorageLocationUpdateManyMutationInput, StorageLocationUncheckedUpdateManyWithoutZoneInput>
  }

  export type StorageLocationScalarWhereInput = {
    AND?: StorageLocationScalarWhereInput | StorageLocationScalarWhereInput[]
    OR?: StorageLocationScalarWhereInput[]
    NOT?: StorageLocationScalarWhereInput | StorageLocationScalarWhereInput[]
    id?: StringFilter<"StorageLocation"> | string
    zoneId?: StringFilter<"StorageLocation"> | string
    aisle?: StringFilter<"StorageLocation"> | string
    shelf?: StringFilter<"StorageLocation"> | string
    bin?: StringFilter<"StorageLocation"> | string
    locationCode?: StringFilter<"StorageLocation"> | string
    capacity?: FloatFilter<"StorageLocation"> | number
    isOccupied?: BoolFilter<"StorageLocation"> | boolean
    currentItemId?: StringNullableFilter<"StorageLocation"> | string | null
    currentQty?: FloatFilter<"StorageLocation"> | number
    createdAt?: DateTimeFilter<"StorageLocation"> | Date | string
    updatedAt?: DateTimeFilter<"StorageLocation"> | Date | string
  }

  export type ZoneCreateWithoutLocationsInput = {
    id?: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
    warehouse: WarehouseCreateNestedOneWithoutZonesInput
  }

  export type ZoneUncheckedCreateWithoutLocationsInput = {
    id?: string
    warehouseId: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type ZoneCreateOrConnectWithoutLocationsInput = {
    where: ZoneWhereUniqueInput
    create: XOR<ZoneCreateWithoutLocationsInput, ZoneUncheckedCreateWithoutLocationsInput>
  }

  export type ZoneUpsertWithoutLocationsInput = {
    update: XOR<ZoneUpdateWithoutLocationsInput, ZoneUncheckedUpdateWithoutLocationsInput>
    create: XOR<ZoneCreateWithoutLocationsInput, ZoneUncheckedCreateWithoutLocationsInput>
    where?: ZoneWhereInput
  }

  export type ZoneUpdateToOneWithWhereWithoutLocationsInput = {
    where?: ZoneWhereInput
    data: XOR<ZoneUpdateWithoutLocationsInput, ZoneUncheckedUpdateWithoutLocationsInput>
  }

  export type ZoneUpdateWithoutLocationsInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    warehouse?: WarehouseUpdateOneRequiredWithoutZonesNestedInput
  }

  export type ZoneUncheckedUpdateWithoutLocationsInput = {
    id?: StringFieldUpdateOperationsInput | string
    warehouseId?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type WarehouseCreateWithoutTransfersFromInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    zones?: ZoneCreateNestedManyWithoutWarehouseInput
    transfersTo?: StockTransferCreateNestedManyWithoutToWarehouseInput
  }

  export type WarehouseUncheckedCreateWithoutTransfersFromInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    zones?: ZoneUncheckedCreateNestedManyWithoutWarehouseInput
    transfersTo?: StockTransferUncheckedCreateNestedManyWithoutToWarehouseInput
  }

  export type WarehouseCreateOrConnectWithoutTransfersFromInput = {
    where: WarehouseWhereUniqueInput
    create: XOR<WarehouseCreateWithoutTransfersFromInput, WarehouseUncheckedCreateWithoutTransfersFromInput>
  }

  export type WarehouseCreateWithoutTransfersToInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    zones?: ZoneCreateNestedManyWithoutWarehouseInput
    transfersFrom?: StockTransferCreateNestedManyWithoutFromWarehouseInput
  }

  export type WarehouseUncheckedCreateWithoutTransfersToInput = {
    id?: string
    name: string
    nameAr: string
    warehouseType: $Enums.WarehouseType
    latitude?: number | null
    longitude?: number | null
    address?: string | null
    governorate?: string | null
    capacityValue: number
    capacityUnit?: string
    currentUsage?: number
    storageCondition?: $Enums.StorageCondition
    tempMin?: number | null
    tempMax?: number | null
    humidityMin?: number | null
    humidityMax?: number | null
    isActive?: boolean
    managerId?: string | null
    managerName?: string | null
    createdAt?: Date | string
    updatedAt?: Date | string
    zones?: ZoneUncheckedCreateNestedManyWithoutWarehouseInput
    transfersFrom?: StockTransferUncheckedCreateNestedManyWithoutFromWarehouseInput
  }

  export type WarehouseCreateOrConnectWithoutTransfersToInput = {
    where: WarehouseWhereUniqueInput
    create: XOR<WarehouseCreateWithoutTransfersToInput, WarehouseUncheckedCreateWithoutTransfersToInput>
  }

  export type WarehouseUpsertWithoutTransfersFromInput = {
    update: XOR<WarehouseUpdateWithoutTransfersFromInput, WarehouseUncheckedUpdateWithoutTransfersFromInput>
    create: XOR<WarehouseCreateWithoutTransfersFromInput, WarehouseUncheckedCreateWithoutTransfersFromInput>
    where?: WarehouseWhereInput
  }

  export type WarehouseUpdateToOneWithWhereWithoutTransfersFromInput = {
    where?: WarehouseWhereInput
    data: XOR<WarehouseUpdateWithoutTransfersFromInput, WarehouseUncheckedUpdateWithoutTransfersFromInput>
  }

  export type WarehouseUpdateWithoutTransfersFromInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zones?: ZoneUpdateManyWithoutWarehouseNestedInput
    transfersTo?: StockTransferUpdateManyWithoutToWarehouseNestedInput
  }

  export type WarehouseUncheckedUpdateWithoutTransfersFromInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zones?: ZoneUncheckedUpdateManyWithoutWarehouseNestedInput
    transfersTo?: StockTransferUncheckedUpdateManyWithoutToWarehouseNestedInput
  }

  export type WarehouseUpsertWithoutTransfersToInput = {
    update: XOR<WarehouseUpdateWithoutTransfersToInput, WarehouseUncheckedUpdateWithoutTransfersToInput>
    create: XOR<WarehouseCreateWithoutTransfersToInput, WarehouseUncheckedCreateWithoutTransfersToInput>
    where?: WarehouseWhereInput
  }

  export type WarehouseUpdateToOneWithWhereWithoutTransfersToInput = {
    where?: WarehouseWhereInput
    data: XOR<WarehouseUpdateWithoutTransfersToInput, WarehouseUncheckedUpdateWithoutTransfersToInput>
  }

  export type WarehouseUpdateWithoutTransfersToInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zones?: ZoneUpdateManyWithoutWarehouseNestedInput
    transfersFrom?: StockTransferUpdateManyWithoutFromWarehouseNestedInput
  }

  export type WarehouseUncheckedUpdateWithoutTransfersToInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: StringFieldUpdateOperationsInput | string
    warehouseType?: EnumWarehouseTypeFieldUpdateOperationsInput | $Enums.WarehouseType
    latitude?: NullableFloatFieldUpdateOperationsInput | number | null
    longitude?: NullableFloatFieldUpdateOperationsInput | number | null
    address?: NullableStringFieldUpdateOperationsInput | string | null
    governorate?: NullableStringFieldUpdateOperationsInput | string | null
    capacityValue?: FloatFieldUpdateOperationsInput | number
    capacityUnit?: StringFieldUpdateOperationsInput | string
    currentUsage?: FloatFieldUpdateOperationsInput | number
    storageCondition?: EnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition
    tempMin?: NullableFloatFieldUpdateOperationsInput | number | null
    tempMax?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMin?: NullableFloatFieldUpdateOperationsInput | number | null
    humidityMax?: NullableFloatFieldUpdateOperationsInput | number | null
    isActive?: BoolFieldUpdateOperationsInput | boolean
    managerId?: NullableStringFieldUpdateOperationsInput | string | null
    managerName?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    zones?: ZoneUncheckedUpdateManyWithoutWarehouseNestedInput
    transfersFrom?: StockTransferUncheckedUpdateManyWithoutFromWarehouseNestedInput
  }

  export type InventoryMovementCreateManyItemInput = {
    id?: string
    tenantId: string
    type: $Enums.MovementType
    quantity: number
    unitCost?: number | null
    referenceId?: string | null
    referenceType?: string | null
    fromLocation?: string | null
    toLocation?: string | null
    notes?: string | null
    notesAr?: string | null
    performedBy: string
    createdAt?: Date | string
  }

  export type InventoryAlertCreateManyItemInput = {
    id?: string
    alertType: $Enums.AlertType
    priority: $Enums.AlertPriority
    status?: $Enums.AlertStatus
    itemName: string
    itemNameAr: string
    titleEn: string
    titleAr: string
    messageEn: string
    messageAr: string
    currentValue: number
    thresholdValue: number
    recommendedActionEn: string
    recommendedActionAr: string
    actionUrl?: string | null
    createdAt?: Date | string
    acknowledgedAt?: Date | string | null
    acknowledgedBy?: string | null
    resolvedAt?: Date | string | null
    resolvedBy?: string | null
    resolutionNotes?: string | null
    snoozeUntil?: Date | string | null
  }

  export type InventoryMovementUpdateWithoutItemInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type InventoryMovementUncheckedUpdateWithoutItemInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type InventoryMovementUncheckedUpdateManyWithoutItemInput = {
    id?: StringFieldUpdateOperationsInput | string
    tenantId?: StringFieldUpdateOperationsInput | string
    type?: EnumMovementTypeFieldUpdateOperationsInput | $Enums.MovementType
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    referenceId?: NullableStringFieldUpdateOperationsInput | string | null
    referenceType?: NullableStringFieldUpdateOperationsInput | string | null
    fromLocation?: NullableStringFieldUpdateOperationsInput | string | null
    toLocation?: NullableStringFieldUpdateOperationsInput | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    notesAr?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: StringFieldUpdateOperationsInput | string
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type InventoryAlertUpdateWithoutItemInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type InventoryAlertUncheckedUpdateWithoutItemInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type InventoryAlertUncheckedUpdateManyWithoutItemInput = {
    id?: StringFieldUpdateOperationsInput | string
    alertType?: EnumAlertTypeFieldUpdateOperationsInput | $Enums.AlertType
    priority?: EnumAlertPriorityFieldUpdateOperationsInput | $Enums.AlertPriority
    status?: EnumAlertStatusFieldUpdateOperationsInput | $Enums.AlertStatus
    itemName?: StringFieldUpdateOperationsInput | string
    itemNameAr?: StringFieldUpdateOperationsInput | string
    titleEn?: StringFieldUpdateOperationsInput | string
    titleAr?: StringFieldUpdateOperationsInput | string
    messageEn?: StringFieldUpdateOperationsInput | string
    messageAr?: StringFieldUpdateOperationsInput | string
    currentValue?: FloatFieldUpdateOperationsInput | number
    thresholdValue?: FloatFieldUpdateOperationsInput | number
    recommendedActionEn?: StringFieldUpdateOperationsInput | string
    recommendedActionAr?: StringFieldUpdateOperationsInput | string
    actionUrl?: NullableStringFieldUpdateOperationsInput | string | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    acknowledgedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    acknowledgedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    resolvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    resolutionNotes?: NullableStringFieldUpdateOperationsInput | string | null
    snoozeUntil?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
  }

  export type ZoneCreateManyWarehouseInput = {
    id?: string
    name: string
    nameAr?: string | null
    capacity: number
    currentUsage?: number
    condition?: $Enums.StorageCondition | null
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type StockTransferCreateManyFromWarehouseInput = {
    id?: string
    itemId: string
    toWarehouseId: string
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
  }

  export type StockTransferCreateManyToWarehouseInput = {
    id?: string
    itemId: string
    fromWarehouseId?: string | null
    quantity: number
    unitCost?: number | null
    totalCost?: number | null
    transferType: $Enums.TransferType
    status?: $Enums.TransferStatus
    requestedBy: string
    approvedBy?: string | null
    performedBy?: string | null
    requestedAt?: Date | string
    approvedAt?: Date | string | null
    completedAt?: Date | string | null
    notes?: string | null
  }

  export type ZoneUpdateWithoutWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    locations?: StorageLocationUpdateManyWithoutZoneNestedInput
  }

  export type ZoneUncheckedUpdateWithoutWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    locations?: StorageLocationUncheckedUpdateManyWithoutZoneNestedInput
  }

  export type ZoneUncheckedUpdateManyWithoutWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    name?: StringFieldUpdateOperationsInput | string
    nameAr?: NullableStringFieldUpdateOperationsInput | string | null
    capacity?: FloatFieldUpdateOperationsInput | number
    currentUsage?: FloatFieldUpdateOperationsInput | number
    condition?: NullableEnumStorageConditionFieldUpdateOperationsInput | $Enums.StorageCondition | null
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StockTransferUpdateWithoutFromWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    toWarehouse?: WarehouseUpdateOneRequiredWithoutTransfersToNestedInput
  }

  export type StockTransferUncheckedUpdateWithoutFromWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    toWarehouseId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
  }

  export type StockTransferUncheckedUpdateManyWithoutFromWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    toWarehouseId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
  }

  export type StockTransferUpdateWithoutToWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
    fromWarehouse?: WarehouseUpdateOneWithoutTransfersFromNestedInput
  }

  export type StockTransferUncheckedUpdateWithoutToWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    fromWarehouseId?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
  }

  export type StockTransferUncheckedUpdateManyWithoutToWarehouseInput = {
    id?: StringFieldUpdateOperationsInput | string
    itemId?: StringFieldUpdateOperationsInput | string
    fromWarehouseId?: NullableStringFieldUpdateOperationsInput | string | null
    quantity?: FloatFieldUpdateOperationsInput | number
    unitCost?: NullableFloatFieldUpdateOperationsInput | number | null
    totalCost?: NullableFloatFieldUpdateOperationsInput | number | null
    transferType?: EnumTransferTypeFieldUpdateOperationsInput | $Enums.TransferType
    status?: EnumTransferStatusFieldUpdateOperationsInput | $Enums.TransferStatus
    requestedBy?: StringFieldUpdateOperationsInput | string
    approvedBy?: NullableStringFieldUpdateOperationsInput | string | null
    performedBy?: NullableStringFieldUpdateOperationsInput | string | null
    requestedAt?: DateTimeFieldUpdateOperationsInput | Date | string
    approvedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    completedAt?: NullableDateTimeFieldUpdateOperationsInput | Date | string | null
    notes?: NullableStringFieldUpdateOperationsInput | string | null
  }

  export type StorageLocationCreateManyZoneInput = {
    id?: string
    aisle: string
    shelf: string
    bin: string
    locationCode: string
    capacity: number
    isOccupied?: boolean
    currentItemId?: string | null
    currentQty?: number
    createdAt?: Date | string
    updatedAt?: Date | string
  }

  export type StorageLocationUpdateWithoutZoneInput = {
    id?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StorageLocationUncheckedUpdateWithoutZoneInput = {
    id?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }

  export type StorageLocationUncheckedUpdateManyWithoutZoneInput = {
    id?: StringFieldUpdateOperationsInput | string
    aisle?: StringFieldUpdateOperationsInput | string
    shelf?: StringFieldUpdateOperationsInput | string
    bin?: StringFieldUpdateOperationsInput | string
    locationCode?: StringFieldUpdateOperationsInput | string
    capacity?: FloatFieldUpdateOperationsInput | number
    isOccupied?: BoolFieldUpdateOperationsInput | boolean
    currentItemId?: NullableStringFieldUpdateOperationsInput | string | null
    currentQty?: FloatFieldUpdateOperationsInput | number
    createdAt?: DateTimeFieldUpdateOperationsInput | Date | string
    updatedAt?: DateTimeFieldUpdateOperationsInput | Date | string
  }



  /**
   * Aliases for legacy arg types
   */
    /**
     * @deprecated Use InventoryItemCountOutputTypeDefaultArgs instead
     */
    export type InventoryItemCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = InventoryItemCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use WarehouseCountOutputTypeDefaultArgs instead
     */
    export type WarehouseCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = WarehouseCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use ZoneCountOutputTypeDefaultArgs instead
     */
    export type ZoneCountOutputTypeArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = ZoneCountOutputTypeDefaultArgs<ExtArgs>
    /**
     * @deprecated Use InventoryItemDefaultArgs instead
     */
    export type InventoryItemArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = InventoryItemDefaultArgs<ExtArgs>
    /**
     * @deprecated Use InventoryMovementDefaultArgs instead
     */
    export type InventoryMovementArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = InventoryMovementDefaultArgs<ExtArgs>
    /**
     * @deprecated Use InventoryAlertDefaultArgs instead
     */
    export type InventoryAlertArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = InventoryAlertDefaultArgs<ExtArgs>
    /**
     * @deprecated Use AlertSettingsDefaultArgs instead
     */
    export type AlertSettingsArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = AlertSettingsDefaultArgs<ExtArgs>
    /**
     * @deprecated Use WarehouseDefaultArgs instead
     */
    export type WarehouseArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = WarehouseDefaultArgs<ExtArgs>
    /**
     * @deprecated Use ZoneDefaultArgs instead
     */
    export type ZoneArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = ZoneDefaultArgs<ExtArgs>
    /**
     * @deprecated Use StorageLocationDefaultArgs instead
     */
    export type StorageLocationArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = StorageLocationDefaultArgs<ExtArgs>
    /**
     * @deprecated Use StockTransferDefaultArgs instead
     */
    export type StockTransferArgs<ExtArgs extends $Extensions.InternalArgs = $Extensions.DefaultArgs> = StockTransferDefaultArgs<ExtArgs>

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