
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

exports.Prisma.ProductScalarFieldEnum = {
  id: 'id',
  name: 'name',
  nameAr: 'nameAr',
  category: 'category',
  price: 'price',
  stock: 'stock',
  unit: 'unit',
  description: 'description',
  descriptionAr: 'descriptionAr',
  imageUrl: 'imageUrl',
  sellerId: 'sellerId',
  sellerType: 'sellerType',
  sellerName: 'sellerName',
  governorate: 'governorate',
  district: 'district',
  cropType: 'cropType',
  harvestDate: 'harvestDate',
  qualityGrade: 'qualityGrade',
  status: 'status',
  featured: 'featured',
  deletedAt: 'deletedAt',
  deletedBy: 'deletedBy',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.OrderScalarFieldEnum = {
  id: 'id',
  orderNumber: 'orderNumber',
  buyerId: 'buyerId',
  buyerName: 'buyerName',
  buyerPhone: 'buyerPhone',
  subtotal: 'subtotal',
  deliveryFee: 'deliveryFee',
  serviceFee: 'serviceFee',
  totalAmount: 'totalAmount',
  status: 'status',
  paymentStatus: 'paymentStatus',
  paymentMethod: 'paymentMethod',
  deliveryAddress: 'deliveryAddress',
  deliveryDate: 'deliveryDate',
  deliveryNotes: 'deliveryNotes',
  deletedAt: 'deletedAt',
  deletedBy: 'deletedBy',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.OrderItemScalarFieldEnum = {
  id: 'id',
  orderId: 'orderId',
  productId: 'productId',
  quantity: 'quantity',
  unitPrice: 'unitPrice',
  totalPrice: 'totalPrice'
};

exports.Prisma.WalletScalarFieldEnum = {
  id: 'id',
  userId: 'userId',
  userType: 'userType',
  balance: 'balance',
  escrowBalance: 'escrowBalance',
  currency: 'currency',
  creditScore: 'creditScore',
  creditTier: 'creditTier',
  loanLimit: 'loanLimit',
  currentLoan: 'currentLoan',
  dailyWithdrawLimit: 'dailyWithdrawLimit',
  singleTransactionLimit: 'singleTransactionLimit',
  requiresPinForAmount: 'requiresPinForAmount',
  dailyWithdrawnToday: 'dailyWithdrawnToday',
  lastWithdrawReset: 'lastWithdrawReset',
  version: 'version',
  isVerified: 'isVerified',
  kycStatus: 'kycStatus',
  pin: 'pin',
  deletedAt: 'deletedAt',
  deletedBy: 'deletedBy',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.TransactionScalarFieldEnum = {
  id: 'id',
  walletId: 'walletId',
  type: 'type',
  amount: 'amount',
  balanceAfter: 'balanceAfter',
  balanceBefore: 'balanceBefore',
  referenceId: 'referenceId',
  referenceType: 'referenceType',
  description: 'description',
  descriptionAr: 'descriptionAr',
  status: 'status',
  idempotencyKey: 'idempotencyKey',
  userId: 'userId',
  ipAddress: 'ipAddress',
  createdAt: 'createdAt'
};

exports.Prisma.LoanScalarFieldEnum = {
  id: 'id',
  walletId: 'walletId',
  amount: 'amount',
  interestRate: 'interestRate',
  totalDue: 'totalDue',
  paidAmount: 'paidAmount',
  termMonths: 'termMonths',
  startDate: 'startDate',
  dueDate: 'dueDate',
  purpose: 'purpose',
  purposeDetails: 'purposeDetails',
  collateralType: 'collateralType',
  collateralValue: 'collateralValue',
  status: 'status',
  deletedAt: 'deletedAt',
  deletedBy: 'deletedBy',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.CreditEventScalarFieldEnum = {
  id: 'id',
  walletId: 'walletId',
  eventType: 'eventType',
  amount: 'amount',
  impact: 'impact',
  description: 'description',
  metadata: 'metadata',
  createdAt: 'createdAt'
};

exports.Prisma.EscrowScalarFieldEnum = {
  id: 'id',
  orderId: 'orderId',
  buyerWalletId: 'buyerWalletId',
  sellerWalletId: 'sellerWalletId',
  amount: 'amount',
  status: 'status',
  notes: 'notes',
  disputeReason: 'disputeReason',
  createdAt: 'createdAt',
  releasedAt: 'releasedAt',
  refundedAt: 'refundedAt'
};

exports.Prisma.ScheduledPaymentScalarFieldEnum = {
  id: 'id',
  walletId: 'walletId',
  amount: 'amount',
  frequency: 'frequency',
  nextPaymentDate: 'nextPaymentDate',
  loanId: 'loanId',
  description: 'description',
  descriptionAr: 'descriptionAr',
  isActive: 'isActive',
  failedAttempts: 'failedAttempts',
  lastPaymentDate: 'lastPaymentDate',
  lastFailureReason: 'lastFailureReason',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.WalletAuditLogScalarFieldEnum = {
  id: 'id',
  walletId: 'walletId',
  transactionId: 'transactionId',
  userId: 'userId',
  operation: 'operation',
  balanceBefore: 'balanceBefore',
  balanceAfter: 'balanceAfter',
  amount: 'amount',
  escrowBalanceBefore: 'escrowBalanceBefore',
  escrowBalanceAfter: 'escrowBalanceAfter',
  versionBefore: 'versionBefore',
  versionAfter: 'versionAfter',
  idempotencyKey: 'idempotencyKey',
  ipAddress: 'ipAddress',
  metadata: 'metadata',
  createdAt: 'createdAt'
};

exports.Prisma.SellerProfileScalarFieldEnum = {
  id: 'id',
  userId: 'userId',
  tenantId: 'tenantId',
  businessName: 'businessName',
  businessType: 'businessType',
  taxId: 'taxId',
  rating: 'rating',
  totalSales: 'totalSales',
  totalRevenue: 'totalRevenue',
  verified: 'verified',
  verifiedAt: 'verifiedAt',
  bankAccount: 'bankAccount',
  payoutPreferences: 'payoutPreferences',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.BuyerProfileScalarFieldEnum = {
  id: 'id',
  userId: 'userId',
  tenantId: 'tenantId',
  shippingAddresses: 'shippingAddresses',
  preferredPayment: 'preferredPayment',
  totalPurchases: 'totalPurchases',
  totalSpent: 'totalSpent',
  loyaltyPoints: 'loyaltyPoints',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ProductReviewScalarFieldEnum = {
  id: 'id',
  productId: 'productId',
  buyerId: 'buyerId',
  orderId: 'orderId',
  rating: 'rating',
  title: 'title',
  comment: 'comment',
  photos: 'photos',
  verified: 'verified',
  helpful: 'helpful',
  reported: 'reported',
  createdAt: 'createdAt',
  updatedAt: 'updatedAt'
};

exports.Prisma.ReviewResponseScalarFieldEnum = {
  id: 'id',
  reviewId: 'reviewId',
  sellerId: 'sellerId',
  response: 'response',
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

exports.Prisma.NullsOrder = {
  first: 'first',
  last: 'last'
};

exports.Prisma.JsonNullValueFilter = {
  DbNull: Prisma.DbNull,
  JsonNull: Prisma.JsonNull,
  AnyNull: Prisma.AnyNull
};
exports.ProductCategory = exports.$Enums.ProductCategory = {
  HARVEST: 'HARVEST',
  SEEDS: 'SEEDS',
  FERTILIZER: 'FERTILIZER',
  PESTICIDE: 'PESTICIDE',
  EQUIPMENT: 'EQUIPMENT',
  IRRIGATION: 'IRRIGATION',
  OTHER: 'OTHER'
};

exports.SellerType = exports.$Enums.SellerType = {
  FARMER: 'FARMER',
  COMPANY: 'COMPANY',
  COOPERATIVE: 'COOPERATIVE'
};

exports.ProductStatus = exports.$Enums.ProductStatus = {
  AVAILABLE: 'AVAILABLE',
  SOLD_OUT: 'SOLD_OUT',
  RESERVED: 'RESERVED',
  PENDING: 'PENDING'
};

exports.OrderStatus = exports.$Enums.OrderStatus = {
  PENDING: 'PENDING',
  CONFIRMED: 'CONFIRMED',
  PROCESSING: 'PROCESSING',
  SHIPPED: 'SHIPPED',
  DELIVERED: 'DELIVERED',
  CANCELLED: 'CANCELLED'
};

exports.PaymentStatus = exports.$Enums.PaymentStatus = {
  UNPAID: 'UNPAID',
  PARTIAL: 'PARTIAL',
  PAID: 'PAID',
  REFUNDED: 'REFUNDED'
};

exports.CreditTier = exports.$Enums.CreditTier = {
  BRONZE: 'BRONZE',
  SILVER: 'SILVER',
  GOLD: 'GOLD',
  PLATINUM: 'PLATINUM'
};

exports.TransactionType = exports.$Enums.TransactionType = {
  DEPOSIT: 'DEPOSIT',
  WITHDRAWAL: 'WITHDRAWAL',
  PURCHASE: 'PURCHASE',
  SALE: 'SALE',
  LOAN: 'LOAN',
  REPAYMENT: 'REPAYMENT',
  FEE: 'FEE',
  REFUND: 'REFUND',
  MARKETPLACE_SALE: 'MARKETPLACE_SALE',
  MARKETPLACE_PURCHASE: 'MARKETPLACE_PURCHASE',
  LOAN_DISBURSEMENT: 'LOAN_DISBURSEMENT',
  LOAN_REPAYMENT: 'LOAN_REPAYMENT',
  ESCROW_HOLD: 'ESCROW_HOLD',
  ESCROW_RELEASE: 'ESCROW_RELEASE',
  ESCROW_REFUND: 'ESCROW_REFUND',
  SCHEDULED_PAYMENT: 'SCHEDULED_PAYMENT',
  TRANSFER_IN: 'TRANSFER_IN',
  TRANSFER_OUT: 'TRANSFER_OUT'
};

exports.TransactionStatus = exports.$Enums.TransactionStatus = {
  PENDING: 'PENDING',
  COMPLETED: 'COMPLETED',
  FAILED: 'FAILED',
  CANCELLED: 'CANCELLED'
};

exports.LoanPurpose = exports.$Enums.LoanPurpose = {
  SEEDS: 'SEEDS',
  FERTILIZER: 'FERTILIZER',
  EQUIPMENT: 'EQUIPMENT',
  IRRIGATION: 'IRRIGATION',
  EXPANSION: 'EXPANSION',
  EMERGENCY: 'EMERGENCY',
  OTHER: 'OTHER'
};

exports.LoanStatus = exports.$Enums.LoanStatus = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  ACTIVE: 'ACTIVE',
  PAID: 'PAID',
  DEFAULTED: 'DEFAULTED',
  REJECTED: 'REJECTED'
};

exports.CreditEventType = exports.$Enums.CreditEventType = {
  LOAN_REPAID_ONTIME: 'LOAN_REPAID_ONTIME',
  LOAN_REPAID_LATE: 'LOAN_REPAID_LATE',
  LOAN_DEFAULTED: 'LOAN_DEFAULTED',
  ORDER_COMPLETED: 'ORDER_COMPLETED',
  ORDER_CANCELLED: 'ORDER_CANCELLED',
  VERIFICATION_UPGRADE: 'VERIFICATION_UPGRADE',
  FARM_VERIFIED: 'FARM_VERIFIED',
  COOPERATIVE_JOINED: 'COOPERATIVE_JOINED',
  LAND_VERIFIED: 'LAND_VERIFIED'
};

exports.EscrowStatus = exports.$Enums.EscrowStatus = {
  HELD: 'HELD',
  RELEASED: 'RELEASED',
  REFUNDED: 'REFUNDED',
  DISPUTED: 'DISPUTED',
  CANCELLED: 'CANCELLED'
};

exports.PaymentFrequency = exports.$Enums.PaymentFrequency = {
  DAILY: 'DAILY',
  WEEKLY: 'WEEKLY',
  BIWEEKLY: 'BIWEEKLY',
  MONTHLY: 'MONTHLY',
  QUARTERLY: 'QUARTERLY',
  YEARLY: 'YEARLY'
};

exports.BusinessType = exports.$Enums.BusinessType = {
  INDIVIDUAL: 'INDIVIDUAL',
  FARM: 'FARM',
  COOPERATIVE: 'COOPERATIVE',
  DISTRIBUTOR: 'DISTRIBUTOR',
  RETAILER: 'RETAILER'
};

exports.Prisma.ModelName = {
  Product: 'Product',
  Order: 'Order',
  OrderItem: 'OrderItem',
  Wallet: 'Wallet',
  Transaction: 'Transaction',
  Loan: 'Loan',
  CreditEvent: 'CreditEvent',
  Escrow: 'Escrow',
  ScheduledPayment: 'ScheduledPayment',
  WalletAuditLog: 'WalletAuditLog',
  SellerProfile: 'SellerProfile',
  BuyerProfile: 'BuyerProfile',
  ProductReview: 'ProductReview',
  ReviewResponse: 'ReviewResponse'
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
