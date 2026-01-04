
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
} = require('./runtime/library.js')


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




  const path = require('path')

/**
 * Enums
 */
exports.Prisma.TransactionIsolationLevel = makeStrictEnum({
  ReadUncommitted: 'ReadUncommitted',
  ReadCommitted: 'ReadCommitted',
  RepeatableRead: 'RepeatableRead',
  Serializable: 'Serializable'
});

exports.Prisma.WeatherObservationScalarFieldEnum = {
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

exports.Prisma.WeatherForecastScalarFieldEnum = {
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

exports.Prisma.WeatherAlertScalarFieldEnum = {
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

exports.Prisma.LocationConfigScalarFieldEnum = {
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

exports.Prisma.SortOrder = {
  asc: 'asc',
  desc: 'desc'
};

exports.Prisma.NullableJsonNullValueInput = {
  DbNull: Prisma.DbNull,
  JsonNull: Prisma.JsonNull
};

exports.Prisma.JsonNullValueInput = {
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
exports.AlertType = exports.$Enums.AlertType = {
  HEAT_STRESS: 'HEAT_STRESS',
  FROST: 'FROST',
  HEAVY_RAIN: 'HEAVY_RAIN',
  DROUGHT: 'DROUGHT',
  STRONG_WIND: 'STRONG_WIND',
  STORM: 'STORM',
  DISEASE_RISK: 'DISEASE_RISK',
  OTHER: 'OTHER'
};

exports.AlertSeverity = exports.$Enums.AlertSeverity = {
  INFO: 'INFO',
  MINOR: 'MINOR',
  MODERATE: 'MODERATE',
  SEVERE: 'SEVERE',
  EXTREME: 'EXTREME'
};

exports.Prisma.ModelName = {
  WeatherObservation: 'WeatherObservation',
  WeatherForecast: 'WeatherForecast',
  WeatherAlert: 'WeatherAlert',
  LocationConfig: 'LocationConfig'
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
      "value": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/weather-service/prisma/.prisma/client",
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
    "sourceFilePath": "/home/runner/work/sahool-unified-v15-idp/sahool-unified-v15-idp/apps/services/weather-service/prisma/schema.prisma",
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
  "inlineSchema": "// SAHOOL Weather Service Schema\n// مخطط قاعدة بيانات خدمة الطقس الموحدة\n\ndatasource db {\n  url      = env(\"DATABASE_URL\")\n  provider = \"postgresql\"\n}\n\ngenerator client {\n  provider      = \"prisma-client-js\"\n  output        = \".prisma/client\"\n  binaryTargets = [\"native\", \"linux-musl-openssl-3.0.x\", \"debian-openssl-3.0.x\"]\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 1. الأرصاد الجوية - Weather Observations\n// البيانات الفعلية المرصودة للطقس\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel WeatherObservation {\n  id String @id @default(uuid())\n\n  // الموقع\n  locationId String  @map(\"location_id\")\n  tenantId   String? @map(\"tenant_id\")\n  latitude   Float\n  longitude  Float\n\n  // التوقيت\n  timestamp DateTime\n\n  // بيانات الطقس الأساسية\n  temperature Float // درجة الحرارة (Celsius)\n  humidity    Float // الرطوبة النسبية (%)\n  pressure    Float // الضغط الجوي (hPa)\n\n  // الرياح\n  windSpeed     Float // سرعة الرياح (m/s)\n  windDirection Float // اتجاه الرياح (degrees)\n\n  // الهطول\n  rainfall Float? // كمية الأمطار (mm)\n\n  // بيانات إضافية\n  uvIndex    Float? // مؤشر الأشعة فوق البنفسجية\n  cloudCover Float? // الغطاء السحابي (%)\n  visibility Float? // مدى الرؤية (meters)\n\n  // المصدر\n  source  String // المصدر (open-meteo, openweathermap, weatherapi)\n  rawData Json?  @map(\"raw_data\") // البيانات الخام من المزود\n\n  // التوقيت\n  createdAt DateTime @default(now()) @map(\"created_at\")\n\n  @@index([locationId, timestamp(sort: Desc)]) // للاستعلام عن آخر الأرصاد لموقع معين\n  @@index([tenantId, timestamp(sort: Desc)]) // للاستعلام عن بيانات مستأجر معين\n  @@index([timestamp(sort: Desc)]) // للاستعلامات الزمنية\n  @@index([latitude, longitude, timestamp]) // للاستعلام المكاني\n  @@map(\"weather_observations\")\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 2. التنبؤات الجوية - Weather Forecasts\n// التنبؤات المستقبلية للطقس\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel WeatherForecast {\n  id String @id @default(uuid())\n\n  // الموقع\n  locationId String  @map(\"location_id\")\n  tenantId   String? @map(\"tenant_id\")\n\n  // التوقيت\n  forecastFor DateTime @map(\"forecast_for\") // التاريخ المتنبأ له\n  fetchedAt   DateTime @map(\"fetched_at\") // وقت جلب التنبؤ\n\n  // المزود\n  provider String // المزود (open-meteo, openweathermap, weatherapi)\n\n  // البيانات\n  hourlyData Json @map(\"hourly_data\") // بيانات التنبؤ الساعي (48 ساعة)\n  dailyData  Json @map(\"daily_data\") // بيانات التنبؤ اليومي (7-14 يوم)\n\n  // التوقيت\n  createdAt DateTime @default(now()) @map(\"created_at\")\n  updatedAt DateTime @updatedAt @map(\"updated_at\")\n\n  @@unique([locationId, forecastFor, provider]) // تنبؤ واحد لكل موقع وتاريخ ومزود\n  @@index([locationId, forecastFor(sort: Desc)]) // للاستعلام عن التنبؤات لموقع معين\n  @@index([tenantId, forecastFor(sort: Desc)]) // للاستعلام عن تنبؤات مستأجر معين\n  @@index([forecastFor(sort: Desc)]) // للاستعلامات الزمنية\n  @@index([fetchedAt(sort: Desc)]) // لحذف التنبؤات القديمة\n  @@map(\"weather_forecasts\")\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 3. التنبيهات الجوية - Weather Alerts\n// التنبيهات والتحذيرات الجوية\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel WeatherAlert {\n  id String @id @default(uuid())\n\n  // الموقع\n  locationId String  @map(\"location_id\")\n  tenantId   String? @map(\"tenant_id\")\n\n  // نوع التنبيه\n  alertType AlertType     @map(\"alert_type\")\n  severity  AlertSeverity\n\n  // المحتوى\n  headline    String\n  description String @db.Text\n\n  // التوقيت\n  startTime DateTime @map(\"start_time\")\n  endTime   DateTime @map(\"end_time\")\n\n  // المصدر\n  source String\n\n  // التوقيت\n  createdAt DateTime @default(now()) @map(\"created_at\")\n  updatedAt DateTime @updatedAt @map(\"updated_at\")\n\n  @@index([locationId, startTime(sort: Desc)]) // للاستعلام عن تنبيهات موقع معين\n  @@index([tenantId, startTime(sort: Desc)]) // للاستعلام عن تنبيهات مستأجر معين\n  @@index([alertType, severity]) // للتصفية حسب النوع والخطورة\n  @@index([startTime, endTime]) // للتنبيهات النشطة\n  @@index([endTime(sort: Desc)]) // لحذف التنبيهات المنتهية\n  @@map(\"weather_alerts\")\n}\n\nenum AlertType {\n  HEAT_STRESS // إجهاد حراري\n  FROST // صقيع\n  HEAVY_RAIN // أمطار غزيرة\n  DROUGHT // جفاف\n  STRONG_WIND // رياح قوية\n  STORM // عاصفة\n  DISEASE_RISK // خطر الأمراض\n  OTHER // أخرى\n}\n\nenum AlertSeverity {\n  INFO // معلومة\n  MINOR // طفيف\n  MODERATE // متوسط\n  SEVERE // شديد\n  EXTREME // خطير جداً\n}\n\n// ═══════════════════════════════════════════════════════════════════════════════\n// 4. إعدادات المواقع - Location Configuration\n// إعدادات المواقع المراقبة\n// ═══════════════════════════════════════════════════════════════════════════════\n\nmodel LocationConfig {\n  id String @id @default(uuid())\n\n  // المستأجر\n  tenantId String @map(\"tenant_id\")\n\n  // المعلومات الأساسية\n  name      String\n  latitude  Float\n  longitude Float\n  timezone  String @default(\"Asia/Aden\")\n\n  // الإعدادات\n  isActive      Boolean @default(true) @map(\"is_active\")\n  fetchInterval Int     @default(3600) @map(\"fetch_interval\") // بالثواني (الافتراضي: ساعة واحدة)\n\n  // التوقيت\n  createdAt DateTime @default(now()) @map(\"created_at\")\n  updatedAt DateTime @updatedAt @map(\"updated_at\")\n\n  @@unique([tenantId, latitude, longitude]) // موقع واحد لكل مستأجر وإحداثيات\n  @@index([tenantId, isActive]) // للاستعلام عن المواقع النشطة لمستأجر\n  @@index([isActive]) // للمواقع النشطة\n  @@map(\"location_configs\")\n}\n",
  "inlineSchemaHash": "7ad427799da99c3d673603ae351407bb5c9cf5f14ad108516a8363e8669fb5d3",
  "copyEngine": true
}

const fs = require('fs')

config.dirname = __dirname
if (!fs.existsSync(path.join(__dirname, 'schema.prisma'))) {
  const alternativePaths = [
    "prisma/.prisma/client",
    ".prisma/client",
  ]
  
  const alternativePath = alternativePaths.find((altPath) => {
    return fs.existsSync(path.join(process.cwd(), altPath, 'schema.prisma'))
  }) ?? alternativePaths[0]

  config.dirname = path.join(process.cwd(), alternativePath)
  config.isBundled = true
}

config.runtimeDataModel = JSON.parse("{\"models\":{\"WeatherObservation\":{\"dbName\":\"weather_observations\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"locationId\",\"dbName\":\"location_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"latitude\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"longitude\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"timestamp\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"temperature\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"humidity\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"pressure\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"windSpeed\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"windDirection\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"rainfall\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"uvIndex\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"cloudCover\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"visibility\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"source\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"rawData\",\"dbName\":\"raw_data\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"WeatherForecast\":{\"dbName\":\"weather_forecasts\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"locationId\",\"dbName\":\"location_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"forecastFor\",\"dbName\":\"forecast_for\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fetchedAt\",\"dbName\":\"fetched_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"provider\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"hourlyData\",\"dbName\":\"hourly_data\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"dailyData\",\"dbName\":\"daily_data\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Json\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[[\"locationId\",\"forecastFor\",\"provider\"]],\"uniqueIndexes\":[{\"name\":null,\"fields\":[\"locationId\",\"forecastFor\",\"provider\"]}],\"isGenerated\":false},\"WeatherAlert\":{\"dbName\":\"weather_alerts\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"locationId\",\"dbName\":\"location_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":false,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"alertType\",\"dbName\":\"alert_type\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"AlertType\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"severity\",\"kind\":\"enum\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"AlertSeverity\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"headline\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"description\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"startTime\",\"dbName\":\"start_time\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"endTime\",\"dbName\":\"end_time\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"source\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[],\"uniqueIndexes\":[],\"isGenerated\":false},\"LocationConfig\":{\"dbName\":\"location_configs\",\"fields\":[{\"name\":\"id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":true,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":{\"name\":\"uuid(4)\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"tenantId\",\"dbName\":\"tenant_id\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"name\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"String\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"latitude\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"longitude\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"Float\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"timezone\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"String\",\"default\":\"Asia/Aden\",\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"isActive\",\"dbName\":\"is_active\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Boolean\",\"default\":true,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"fetchInterval\",\"dbName\":\"fetch_interval\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"Int\",\"default\":3600,\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"createdAt\",\"dbName\":\"created_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":true,\"type\":\"DateTime\",\"default\":{\"name\":\"now\",\"args\":[]},\"isGenerated\":false,\"isUpdatedAt\":false},{\"name\":\"updatedAt\",\"dbName\":\"updated_at\",\"kind\":\"scalar\",\"isList\":false,\"isRequired\":true,\"isUnique\":false,\"isId\":false,\"isReadOnly\":false,\"hasDefaultValue\":false,\"type\":\"DateTime\",\"isGenerated\":false,\"isUpdatedAt\":true}],\"primaryKey\":null,\"uniqueFields\":[[\"tenantId\",\"latitude\",\"longitude\"]],\"uniqueIndexes\":[{\"name\":null,\"fields\":[\"tenantId\",\"latitude\",\"longitude\"]}],\"isGenerated\":false}},\"enums\":{\"AlertType\":{\"values\":[{\"name\":\"HEAT_STRESS\",\"dbName\":null},{\"name\":\"FROST\",\"dbName\":null},{\"name\":\"HEAVY_RAIN\",\"dbName\":null},{\"name\":\"DROUGHT\",\"dbName\":null},{\"name\":\"STRONG_WIND\",\"dbName\":null},{\"name\":\"STORM\",\"dbName\":null},{\"name\":\"DISEASE_RISK\",\"dbName\":null},{\"name\":\"OTHER\",\"dbName\":null}],\"dbName\":null},\"AlertSeverity\":{\"values\":[{\"name\":\"INFO\",\"dbName\":null},{\"name\":\"MINOR\",\"dbName\":null},{\"name\":\"MODERATE\",\"dbName\":null},{\"name\":\"SEVERE\",\"dbName\":null},{\"name\":\"EXTREME\",\"dbName\":null}],\"dbName\":null}},\"types\":{}}")
defineDmmfProperty(exports.Prisma, config.runtimeDataModel)
config.engineWasm = undefined


const { warnEnvConflicts } = require('./runtime/library.js')

warnEnvConflicts({
    rootEnvPath: config.relativeEnvPaths.rootEnvPath && path.resolve(config.dirname, config.relativeEnvPaths.rootEnvPath),
    schemaEnvPath: config.relativeEnvPaths.schemaEnvPath && path.resolve(config.dirname, config.relativeEnvPaths.schemaEnvPath)
})

const PrismaClient = getPrismaClient(config)
exports.PrismaClient = PrismaClient
Object.assign(exports, Prisma)

// file annotations for bundling tools to include these files
path.join(__dirname, "libquery_engine-debian-openssl-3.0.x.so.node");
path.join(process.cwd(), "prisma/.prisma/client/libquery_engine-debian-openssl-3.0.x.so.node")

// file annotations for bundling tools to include these files
path.join(__dirname, "libquery_engine-linux-musl-openssl-3.0.x.so.node");
path.join(process.cwd(), "prisma/.prisma/client/libquery_engine-linux-musl-openssl-3.0.x.so.node")
// file annotations for bundling tools to include these files
path.join(__dirname, "schema.prisma");
path.join(process.cwd(), "prisma/.prisma/client/schema.prisma")
