
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

exports.Prisma.GermplasmScalarFieldEnum = {
  id: 'id',
  accessionNumber: 'accessionNumber',
  commonName: 'commonName',
  commonNameAr: 'commonNameAr',
  scientificName: 'scientificName',
  genus: 'genus',
  species: 'species',
  subspecies: 'subspecies',
  cultivar: 'cultivar',
  variety: 'variety',
  pedigree: 'pedigree',
  type: 'type',
  countryOfOrigin: 'countryOfOrigin',
  regionOfOrigin: 'regionOfOrigin',
  collectionSite: 'collectionSite',
  collectionDate: 'collectionDate',
  collectedBy: 'collectedBy',
  donorInstitution: 'donorInstitution',
  donorAccessionNumber: 'donorAccessionNumber',
  growthHabit: 'growthHabit',
  maturityDays: 'maturityDays',
  yieldPotential: 'yieldPotential',
  droughtTolerance: 'droughtTolerance',
  diseaseResistance: 'diseaseResistance',
  pestResistance: 'pestResistance',
  qualityTraits: 'qualityTraits',
  storageLocation: 'storageLocation',
  storageConditions: 'storageConditions',
  storageTemperature: 'storageTemperature',
  storageHumidity: 'storageHumidity',
  isAvailable: 'isAvailable',
  quantityAvailable: 'quantityAvailable',
  quantityUnit: 'quantityUnit',
  description: 'description',
  descriptionAr: 'descriptionAr',
  photos: 'photos',
  documents: 'documents',
  metadata: 'metadata',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.SeedLotScalarFieldEnum = {
  id: 'id',
  germplasmId: 'germplasmId',
  lotNumber: 'lotNumber',
  initialQuantity: 'initialQuantity',
  currentQuantity: 'currentQuantity',
  quantityUnit: 'quantityUnit',
  seedCount: 'seedCount',
  thousandSeedWeight: 'thousandSeedWeight',
  qualityGrade: 'qualityGrade',
  germinationRate: 'germinationRate',
  germinationTestDate: 'germinationTestDate',
  purityPercentage: 'purityPercentage',
  moistureContent: 'moistureContent',
  vigorIndex: 'vigorIndex',
  productionDate: 'productionDate',
  harvestDate: 'harvestDate',
  productionLocation: 'productionLocation',
  productionSeason: 'productionSeason',
  producedBy: 'producedBy',
  certificationNumber: 'certificationNumber',
  certifiedBy: 'certifiedBy',
  certificationDate: 'certificationDate',
  expiryDate: 'expiryDate',
  isTreated: 'isTreated',
  treatmentType: 'treatmentType',
  treatmentProduct: 'treatmentProduct',
  treatmentDate: 'treatmentDate',
  storageLocation: 'storageLocation',
  storageConditions: 'storageConditions',
  notes: 'notes',
  notesAr: 'notesAr',
  photos: 'photos',
  documents: 'documents',
  metadata: 'metadata',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.PlantingScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  plotId: 'plotId',
  germplasmId: 'germplasmId',
  seedLotId: 'seedLotId',
  plantingDate: 'plantingDate',
  plantingMethod: 'plantingMethod',
  seedingRate: 'seedingRate',
  seedingRateUnit: 'seedingRateUnit',
  seedsPerHill: 'seedsPerHill',
  seedDepth: 'seedDepth',
  seedDepthUnit: 'seedDepthUnit',
  rowSpacing: 'rowSpacing',
  plantSpacing: 'plantSpacing',
  spacingUnit: 'spacingUnit',
  plantedArea: 'plantedArea',
  plantedAreaUnit: 'plantedAreaUnit',
  numberOfRows: 'numberOfRows',
  plantsPerRow: 'plantsPerRow',
  totalPlantsExpected: 'totalPlantsExpected',
  germinationDate: 'germinationDate',
  emergenceDate: 'emergenceDate',
  germinationCount: 'germinationCount',
  germinationPercentage: 'germinationPercentage',
  thinningDate: 'thinningDate',
  finalPlantCount: 'finalPlantCount',
  plantedBy: 'plantedBy',
  notes: 'notes',
  notesAr: 'notesAr',
  photos: 'photos',
  metadata: 'metadata',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ExperimentScalarFieldEnum = {
  id: 'id',
  title: 'title',
  titleAr: 'titleAr',
  description: 'description',
  descriptionAr: 'descriptionAr',
  hypothesis: 'hypothesis',
  hypothesisAr: 'hypothesisAr',
  startDate: 'startDate',
  endDate: 'endDate',
  status: 'status',
  lockedAt: 'lockedAt',
  lockedBy: 'lockedBy',
  principalResearcherId: 'principalResearcherId',
  organizationId: 'organizationId',
  farmId: 'farmId',
  metadata: 'metadata',
  tags: 'tags',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt',
  version: 'version'
};

exports.Prisma.ResearchProtocolScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  name: 'name',
  nameAr: 'nameAr',
  description: 'description',
  descriptionAr: 'descriptionAr',
  methodology: 'methodology',
  methodologyAr: 'methodologyAr',
  variables: 'variables',
  measurementSchedule: 'measurementSchedule',
  equipmentRequired: 'equipmentRequired',
  safetyGuidelines: 'safetyGuidelines',
  version: 'version',
  approvedBy: 'approvedBy',
  approvedAt: 'approvedAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ResearchPlotScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  plotCode: 'plotCode',
  name: 'name',
  nameAr: 'nameAr',
  areaSqm: 'areaSqm',
  soilType: 'soilType',
  soilPh: 'soilPh',
  previousCrop: 'previousCrop',
  replicateNumber: 'replicateNumber',
  blockNumber: 'blockNumber',
  rowNumber: 'rowNumber',
  columnNumber: 'columnNumber',
  metadata: 'metadata',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.TreatmentScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  plotId: 'plotId',
  treatmentCode: 'treatmentCode',
  name: 'name',
  nameAr: 'nameAr',
  type: 'type',
  description: 'description',
  descriptionAr: 'descriptionAr',
  dosage: 'dosage',
  dosageUnit: 'dosageUnit',
  applicationMethod: 'applicationMethod',
  applicationFrequency: 'applicationFrequency',
  startDate: 'startDate',
  endDate: 'endDate',
  isControl: 'isControl',
  parameters: 'parameters',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ResearchDailyLogScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  plotId: 'plotId',
  treatmentId: 'treatmentId',
  logDate: 'logDate',
  logTime: 'logTime',
  category: 'category',
  title: 'title',
  titleAr: 'titleAr',
  notes: 'notes',
  notesAr: 'notesAr',
  measurements: 'measurements',
  weatherConditions: 'weatherConditions',
  photos: 'photos',
  attachments: 'attachments',
  recordedBy: 'recordedBy',
  deviceId: 'deviceId',
  offlineId: 'offlineId',
  hash: 'hash',
  syncedAt: 'syncedAt',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.LabSampleScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  plotId: 'plotId',
  logId: 'logId',
  sampleCode: 'sampleCode',
  type: 'type',
  description: 'description',
  descriptionAr: 'descriptionAr',
  collectionDate: 'collectionDate',
  collectionTime: 'collectionTime',
  collectedBy: 'collectedBy',
  storageLocation: 'storageLocation',
  storageConditions: 'storageConditions',
  quantity: 'quantity',
  quantityUnit: 'quantityUnit',
  analysisStatus: 'analysisStatus',
  analysisResults: 'analysisResults',
  analyzedBy: 'analyzedBy',
  analyzedAt: 'analyzedAt',
  photos: 'photos',
  metadata: 'metadata',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.DigitalSignatureScalarFieldEnum = {
  id: 'id',
  entityType: 'entityType',
  entityId: 'entityId',
  signerId: 'signerId',
  signatureHash: 'signatureHash',
  algorithm: 'algorithm',
  payloadHash: 'payloadHash',
  timestamp: 'timestamp',
  ipAddress: 'ipAddress',
  deviceInfo: 'deviceInfo',
  purpose: 'purpose',
  isValid: 'isValid',
  invalidatedAt: 'invalidatedAt',
  invalidatedReason: 'invalidatedReason',
  createdAt: 'createdAt'
};

exports.Prisma.ExperimentCollaboratorScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  userId: 'userId',
  role: 'role',
  permissions: 'permissions',
  invitedBy: 'invitedBy',
  acceptedAt: 'acceptedAt',
  createdAt: 'createdAt'
};

exports.Prisma.ExperimentAuditLogScalarFieldEnum = {
  id: 'id',
  experimentId: 'experimentId',
  entityType: 'entityType',
  entityId: 'entityId',
  action: 'action',
  oldValues: 'oldValues',
  newValues: 'newValues',
  changedBy: 'changedBy',
  changedAt: 'changedAt',
  ipAddress: 'ipAddress',
  userAgent: 'userAgent'
};

exports.Prisma.SortOrder = {
  asc: 'asc',
  desc: 'desc'
};

exports.Prisma.JsonNullValueInput = {
  JsonNull: Prisma.JsonNull
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
exports.GermplasmType = exports.$Enums.GermplasmType = {
  seed: 'seed',
  cutting: 'cutting',
  tissue: 'tissue',
  pollen: 'pollen',
  other: 'other'
};

exports.SeedQualityGrade = exports.$Enums.SeedQualityGrade = {
  certified: 'certified',
  foundation: 'foundation',
  registered: 'registered',
  breeder: 'breeder',
  commercial: 'commercial',
  farmer_saved: 'farmer_saved'
};

exports.ExperimentStatus = exports.$Enums.ExperimentStatus = {
  draft: 'draft',
  active: 'active',
  locked: 'locked',
  completed: 'completed',
  archived: 'archived'
};

exports.TreatmentType = exports.$Enums.TreatmentType = {
  fertilizer: 'fertilizer',
  pesticide: 'pesticide',
  irrigation: 'irrigation',
  seed_variety: 'seed_variety',
  other: 'other'
};

exports.LogCategory = exports.$Enums.LogCategory = {
  observation: 'observation',
  measurement: 'measurement',
  treatment: 'treatment',
  harvest: 'harvest',
  weather: 'weather',
  pest: 'pest',
  planting: 'planting',
  germination: 'germination',
  other: 'other'
};

exports.SampleType = exports.$Enums.SampleType = {
  soil: 'soil',
  plant: 'plant',
  water: 'water',
  pest: 'pest',
  other: 'other'
};

exports.Prisma.ModelName = {
  Germplasm: 'Germplasm',
  SeedLot: 'SeedLot',
  Planting: 'Planting',
  Experiment: 'Experiment',
  ResearchProtocol: 'ResearchProtocol',
  ResearchPlot: 'ResearchPlot',
  Treatment: 'Treatment',
  ResearchDailyLog: 'ResearchDailyLog',
  LabSample: 'LabSample',
  DigitalSignature: 'DigitalSignature',
  ExperimentCollaborator: 'ExperimentCollaborator',
  ExperimentAuditLog: 'ExperimentAuditLog'
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
