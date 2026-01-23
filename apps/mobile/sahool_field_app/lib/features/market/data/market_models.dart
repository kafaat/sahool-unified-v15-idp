/// SAHOOL Market Models
/// نماذج السوق والمالية - Clean Architecture Pattern
///
/// يحتوي على جميع نماذج البيانات للسوق والمحفظة والقروض
/// متوافقة مع API الخلفية (marketplace-service)

import 'package:flutter/material.dart';

// =============================================================================
// المحفظة - Wallet Models
// =============================================================================

/// تصنيف الائتمان
enum CreditTier {
  bronze('BRONZE', 'برونزي', Color(0xFFCD7F32)),
  silver('SILVER', 'فضي', Color(0xFFC0C0C0)),
  gold('GOLD', 'ذهبي', Color(0xFFFFD700)),
  platinum('PLATINUM', 'بلاتيني', Color(0xFFE5E4E2));

  final String value;
  final String arabicName;
  final Color color;

  const CreditTier(this.value, this.arabicName, this.color);

  static CreditTier fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'PLATINUM':
        return CreditTier.platinum;
      case 'GOLD':
        return CreditTier.gold;
      case 'SILVER':
        return CreditTier.silver;
      default:
        return CreditTier.bronze;
    }
  }
}

/// نموذج المحفظة
class WalletModel {
  final String id;
  final String userId;
  final String userType;
  final double balance;
  final String currency;
  final int creditScore;
  final CreditTier creditTier;
  final String creditTierAr;
  final double loanLimit;
  final double currentLoan;
  final double availableCredit;
  final bool isVerified;
  final DateTime createdAt;
  final DateTime updatedAt;

  const WalletModel({
    required this.id,
    required this.userId,
    required this.userType,
    required this.balance,
    required this.currency,
    required this.creditScore,
    required this.creditTier,
    required this.creditTierAr,
    required this.loanLimit,
    required this.currentLoan,
    required this.availableCredit,
    required this.isVerified,
    required this.createdAt,
    required this.updatedAt,
  });

  factory WalletModel.fromJson(Map<String, dynamic> json) {
    return WalletModel(
      id: json['id'] as String,
      userId: json['userId'] as String,
      userType: json['userType'] as String? ?? 'farmer',
      balance: (json['balance'] as num).toDouble(),
      currency: json['currency'] as String? ?? 'YER',
      creditScore: json['creditScore'] as int? ?? 300,
      creditTier: CreditTier.fromString(json['creditTier'] as String?),
      creditTierAr: json['creditTierAr'] as String? ?? 'برونزي',
      loanLimit: (json['loanLimit'] as num?)?.toDouble() ?? 0,
      currentLoan: (json['currentLoan'] as num?)?.toDouble() ?? 0,
      availableCredit: (json['availableCredit'] as num?)?.toDouble() ?? 0,
      isVerified: json['isVerified'] as bool? ?? false,
      createdAt: DateTime.parse(json['createdAt'] as String? ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updatedAt'] as String? ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'userId': userId,
    'userType': userType,
    'balance': balance,
    'currency': currency,
    'creditScore': creditScore,
    'creditTier': creditTier.value,
    'creditTierAr': creditTierAr,
    'loanLimit': loanLimit,
    'currentLoan': currentLoan,
    'availableCredit': availableCredit,
    'isVerified': isVerified,
  };

  /// نسبة التصنيف الائتماني (0-1)
  double get creditScorePercentage => ((creditScore - 300) / 550).clamp(0.0, 1.0);

  /// لون مؤشر الائتمان
  Color get scoreColor {
    if (creditScore >= 750) return Colors.green;
    if (creditScore >= 650) return Colors.lightGreen;
    if (creditScore >= 550) return Colors.orange;
    if (creditScore >= 450) return Colors.deepOrange;
    return Colors.red;
  }
}

// =============================================================================
// المعاملات - Transaction Models
// =============================================================================

/// نوع المعاملة
enum TransactionType {
  deposit('DEPOSIT', 'إيداع', Icons.arrow_downward, Colors.green),
  withdrawal('WITHDRAWAL', 'سحب', Icons.arrow_upward, Colors.red),
  purchase('PURCHASE', 'شراء', Icons.shopping_cart, Colors.orange),
  sale('SALE', 'بيع', Icons.store, Colors.blue),
  loan('LOAN', 'قرض', Icons.account_balance, Colors.purple),
  repayment('REPAYMENT', 'سداد', Icons.check_circle, Colors.teal),
  fee('FEE', 'رسوم', Icons.receipt, Colors.grey),
  refund('REFUND', 'استرداد', Icons.refresh, Colors.indigo);

  final String value;
  final String arabicName;
  final IconData icon;
  final Color color;

  const TransactionType(this.value, this.arabicName, this.icon, this.color);

  static TransactionType fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'WITHDRAWAL':
        return TransactionType.withdrawal;
      case 'PURCHASE':
        return TransactionType.purchase;
      case 'SALE':
        return TransactionType.sale;
      case 'LOAN':
        return TransactionType.loan;
      case 'REPAYMENT':
        return TransactionType.repayment;
      case 'FEE':
        return TransactionType.fee;
      case 'REFUND':
        return TransactionType.refund;
      default:
        return TransactionType.deposit;
    }
  }
}

/// نموذج المعاملة
class TransactionModel {
  final String id;
  final String walletId;
  final TransactionType type;
  final double amount;
  final double balanceAfter;
  final String? description;
  final String? descriptionAr;
  final String? referenceId;
  final DateTime createdAt;

  const TransactionModel({
    required this.id,
    required this.walletId,
    required this.type,
    required this.amount,
    required this.balanceAfter,
    this.description,
    this.descriptionAr,
    this.referenceId,
    required this.createdAt,
  });

  factory TransactionModel.fromJson(Map<String, dynamic> json) {
    return TransactionModel(
      id: json['id'] as String,
      walletId: json['walletId'] as String,
      type: TransactionType.fromString(json['type'] as String?),
      amount: (json['amount'] as num).toDouble(),
      balanceAfter: (json['balanceAfter'] as num).toDouble(),
      description: json['description'] as String?,
      descriptionAr: json['descriptionAr'] as String?,
      referenceId: json['referenceId'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
    );
  }

  /// هل المعاملة إيجابية (دخل)؟
  bool get isPositive => amount > 0;
}

// =============================================================================
// المنتجات - Product Models
// =============================================================================

/// فئة المنتج
enum ProductCategory {
  grains('GRAINS', 'حبوب', Icons.grain),
  vegetables('VEGETABLES', 'خضروات', Icons.eco),
  fruits('FRUITS', 'فواكه', Icons.apple),
  livestock('LIVESTOCK', 'ماشية', Icons.pets),
  supplies('SUPPLIES', 'مستلزمات', Icons.inventory),
  equipment('EQUIPMENT', 'معدات', Icons.agriculture);

  final String value;
  final String arabicName;
  final IconData icon;

  const ProductCategory(this.value, this.arabicName, this.icon);

  static ProductCategory fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'VEGETABLES':
        return ProductCategory.vegetables;
      case 'FRUITS':
        return ProductCategory.fruits;
      case 'LIVESTOCK':
        return ProductCategory.livestock;
      case 'SUPPLIES':
        return ProductCategory.supplies;
      case 'EQUIPMENT':
        return ProductCategory.equipment;
      default:
        return ProductCategory.grains;
    }
  }
}

/// حالة المنتج
enum ProductStatus {
  available('AVAILABLE', 'متاح'),
  reserved('RESERVED', 'محجوز'),
  sold('SOLD', 'مباع'),
  expired('EXPIRED', 'منتهي');

  final String value;
  final String arabicName;

  const ProductStatus(this.value, this.arabicName);

  static ProductStatus fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'RESERVED':
        return ProductStatus.reserved;
      case 'SOLD':
        return ProductStatus.sold;
      case 'EXPIRED':
        return ProductStatus.expired;
      default:
        return ProductStatus.available;
    }
  }
}

/// نموذج المنتج
class ProductModel {
  final String id;
  final String sellerId;
  final String? sellerName;
  final String name;
  final String nameAr;
  final String? description;
  final String? descriptionAr;
  final ProductCategory category;
  final double price;
  final String unit;
  final double quantity;
  final double availableQuantity;
  final String? governorate;
  final String? qualityGrade;
  final String? harvestDate;
  final String? imageUrl;
  final List<String> images;
  final bool featured;
  final bool organic;
  final ProductStatus status;
  final DateTime createdAt;
  final DateTime updatedAt;

  const ProductModel({
    required this.id,
    required this.sellerId,
    this.sellerName,
    required this.name,
    required this.nameAr,
    this.description,
    this.descriptionAr,
    required this.category,
    required this.price,
    required this.unit,
    required this.quantity,
    required this.availableQuantity,
    this.governorate,
    this.qualityGrade,
    this.harvestDate,
    this.imageUrl,
    this.images = const [],
    this.featured = false,
    this.organic = false,
    required this.status,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ProductModel.fromJson(Map<String, dynamic> json) {
    return ProductModel(
      id: json['id'] as String,
      sellerId: json['sellerId'] as String,
      sellerName: json['sellerName'] as String?,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String? ?? json['name'] as String,
      description: json['description'] as String?,
      descriptionAr: json['descriptionAr'] as String?,
      category: ProductCategory.fromString(json['category'] as String?),
      price: (json['price'] as num).toDouble(),
      unit: json['unit'] as String? ?? 'طن',
      quantity: (json['quantity'] as num?)?.toDouble() ?? 0,
      availableQuantity: (json['availableQuantity'] as num?)?.toDouble() ?? 0,
      governorate: json['governorate'] as String?,
      qualityGrade: json['qualityGrade'] as String?,
      harvestDate: json['harvestDate'] as String?,
      imageUrl: json['imageUrl'] as String?,
      images: (json['images'] as List<dynamic>?)?.cast<String>() ?? [],
      featured: json['featured'] as bool? ?? false,
      organic: json['organic'] as bool? ?? false,
      status: ProductStatus.fromString(json['status'] as String?),
      createdAt: DateTime.parse(json['createdAt'] as String? ?? DateTime.now().toIso8601String()),
      updatedAt: DateTime.parse(json['updatedAt'] as String? ?? DateTime.now().toIso8601String()),
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'sellerId': sellerId,
    'name': name,
    'nameAr': nameAr,
    'description': description,
    'category': category.value,
    'price': price,
    'unit': unit,
    'quantity': quantity,
    'governorate': governorate,
    'qualityGrade': qualityGrade,
    'harvestDate': harvestDate,
    'organic': organic,
  };

  /// السعر المنسق
  String get formattedPrice => '${price.toStringAsFixed(0)} ر.ي/$unit';

  /// هل المنتج متاح للشراء؟
  bool get isAvailable => status == ProductStatus.available && availableQuantity > 0;
}

// =============================================================================
// الطلبات - Order Models
// =============================================================================

/// حالة الطلب
enum OrderStatus {
  pending('PENDING', 'قيد الانتظار', Colors.orange),
  confirmed('CONFIRMED', 'مؤكد', Colors.blue),
  processing('PROCESSING', 'قيد التنفيذ', Colors.indigo),
  shipped('SHIPPED', 'تم الشحن', Colors.purple),
  delivered('DELIVERED', 'تم التسليم', Colors.green),
  cancelled('CANCELLED', 'ملغي', Colors.red);

  final String value;
  final String arabicName;
  final Color color;

  const OrderStatus(this.value, this.arabicName, this.color);

  static OrderStatus fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'CONFIRMED':
        return OrderStatus.confirmed;
      case 'PROCESSING':
        return OrderStatus.processing;
      case 'SHIPPED':
        return OrderStatus.shipped;
      case 'DELIVERED':
        return OrderStatus.delivered;
      case 'CANCELLED':
        return OrderStatus.cancelled;
      default:
        return OrderStatus.pending;
    }
  }
}

/// عنصر في الطلب
class OrderItem {
  final String productId;
  final String productName;
  final String productNameAr;
  final double quantity;
  final double unitPrice;
  final double totalPrice;

  const OrderItem({
    required this.productId,
    required this.productName,
    required this.productNameAr,
    required this.quantity,
    required this.unitPrice,
    required this.totalPrice,
  });

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      productId: json['productId'] as String,
      productName: json['productName'] as String? ?? '',
      productNameAr: json['productNameAr'] as String? ?? json['productName'] as String? ?? '',
      quantity: (json['quantity'] as num).toDouble(),
      unitPrice: (json['unitPrice'] as num).toDouble(),
      totalPrice: (json['totalPrice'] as num).toDouble(),
    );
  }
}

/// نموذج الطلب
class OrderModel {
  final String id;
  final String buyerId;
  final String? buyerName;
  final String sellerId;
  final String? sellerName;
  final List<OrderItem> items;
  final double totalAmount;
  final double fees;
  final double grandTotal;
  final OrderStatus status;
  final String? deliveryAddress;
  final String? paymentMethod;
  final String? notes;
  final DateTime createdAt;
  final DateTime updatedAt;

  const OrderModel({
    required this.id,
    required this.buyerId,
    this.buyerName,
    required this.sellerId,
    this.sellerName,
    required this.items,
    required this.totalAmount,
    required this.fees,
    required this.grandTotal,
    required this.status,
    this.deliveryAddress,
    this.paymentMethod,
    this.notes,
    required this.createdAt,
    required this.updatedAt,
  });

  factory OrderModel.fromJson(Map<String, dynamic> json) {
    return OrderModel(
      id: json['id'] as String,
      buyerId: json['buyerId'] as String,
      buyerName: json['buyerName'] as String?,
      sellerId: json['sellerId'] as String,
      sellerName: json['sellerName'] as String?,
      items: (json['items'] as List<dynamic>?)
          ?.map((e) => OrderItem.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      totalAmount: (json['totalAmount'] as num).toDouble(),
      fees: (json['fees'] as num?)?.toDouble() ?? 0,
      grandTotal: (json['grandTotal'] as num).toDouble(),
      status: OrderStatus.fromString(json['status'] as String?),
      deliveryAddress: json['deliveryAddress'] as String?,
      paymentMethod: json['paymentMethod'] as String?,
      notes: json['notes'] as String?,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );
  }

  /// عدد المنتجات في الطلب
  int get itemCount => items.length;
}

// =============================================================================
// القروض - Loan Models
// =============================================================================

/// حالة القرض
enum LoanStatus {
  pending('PENDING', 'قيد المراجعة', Colors.orange),
  approved('APPROVED', 'موافق عليه', Colors.blue),
  active('ACTIVE', 'نشط', Colors.green),
  completed('COMPLETED', 'مكتمل', Colors.teal),
  defaulted('DEFAULTED', 'متعثر', Colors.red),
  rejected('REJECTED', 'مرفوض', Colors.grey);

  final String value;
  final String arabicName;
  final Color color;

  const LoanStatus(this.value, this.arabicName, this.color);

  static LoanStatus fromString(String? value) {
    switch (value?.toUpperCase()) {
      case 'APPROVED':
        return LoanStatus.approved;
      case 'ACTIVE':
        return LoanStatus.active;
      case 'COMPLETED':
        return LoanStatus.completed;
      case 'DEFAULTED':
        return LoanStatus.defaulted;
      case 'REJECTED':
        return LoanStatus.rejected;
      default:
        return LoanStatus.pending;
    }
  }
}

/// نموذج القرض
class LoanModel {
  final String id;
  final String walletId;
  final double amount;
  final double adminFee;
  final double totalDue;
  final double paidAmount;
  final int termMonths;
  final String purpose;
  final String purposeAr;
  final String? purposeDetails;
  final String? collateralType;
  final double? collateralValue;
  final LoanStatus status;
  final DateTime? approvedAt;
  final DateTime? startDate;
  final DateTime? dueDate;
  final DateTime createdAt;
  final DateTime updatedAt;

  const LoanModel({
    required this.id,
    required this.walletId,
    required this.amount,
    required this.adminFee,
    required this.totalDue,
    required this.paidAmount,
    required this.termMonths,
    required this.purpose,
    required this.purposeAr,
    this.purposeDetails,
    this.collateralType,
    this.collateralValue,
    required this.status,
    this.approvedAt,
    this.startDate,
    this.dueDate,
    required this.createdAt,
    required this.updatedAt,
  });

  factory LoanModel.fromJson(Map<String, dynamic> json) {
    return LoanModel(
      id: json['id'] as String,
      walletId: json['walletId'] as String,
      amount: (json['amount'] as num).toDouble(),
      adminFee: (json['adminFee'] as num?)?.toDouble() ?? 0,
      totalDue: (json['totalDue'] as num).toDouble(),
      paidAmount: (json['paidAmount'] as num?)?.toDouble() ?? 0,
      termMonths: json['termMonths'] as int,
      purpose: json['purpose'] as String,
      purposeAr: json['purposeAr'] as String? ?? _translatePurpose(json['purpose'] as String),
      purposeDetails: json['purposeDetails'] as String?,
      collateralType: json['collateralType'] as String?,
      collateralValue: (json['collateralValue'] as num?)?.toDouble(),
      status: LoanStatus.fromString(json['status'] as String?),
      approvedAt: json['approvedAt'] != null ? DateTime.parse(json['approvedAt'] as String) : null,
      startDate: json['startDate'] != null ? DateTime.parse(json['startDate'] as String) : null,
      dueDate: json['dueDate'] != null ? DateTime.parse(json['dueDate'] as String) : null,
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );
  }

  static String _translatePurpose(String purpose) {
    switch (purpose.toLowerCase()) {
      case 'seeds':
        return 'شراء بذور';
      case 'fertilizer':
        return 'شراء أسمدة';
      case 'equipment':
        return 'شراء معدات';
      case 'irrigation':
        return 'نظام ري';
      case 'labor':
        return 'أجور عمال';
      case 'expansion':
        return 'توسيع المزرعة';
      default:
        return 'غرض آخر';
    }
  }

  /// المبلغ المتبقي
  double get remainingAmount => totalDue - paidAmount;

  /// نسبة السداد (0-1)
  double get paymentProgress => totalDue > 0 ? (paidAmount / totalDue).clamp(0.0, 1.0) : 0;

  /// هل القرض نشط؟
  bool get isActive => status == LoanStatus.active || status == LoanStatus.approved;
}

// =============================================================================
// التصنيف الائتماني - Credit Score Models
// =============================================================================

/// بيانات المزرعة لحساب التصنيف
class FarmData {
  final double totalArea;
  final int activeSeasons;
  final int fieldCount;
  final String diseaseRisk;
  final String irrigationType;
  final double avgYieldScore;
  final int onTimePayments;
  final int latePayments;

  const FarmData({
    required this.totalArea,
    required this.activeSeasons,
    required this.fieldCount,
    required this.diseaseRisk,
    required this.irrigationType,
    required this.avgYieldScore,
    this.onTimePayments = 0,
    this.latePayments = 0,
  });

  Map<String, dynamic> toJson() => {
    'totalArea': totalArea,
    'activeSeasons': activeSeasons,
    'fieldCount': fieldCount,
    'diseaseRisk': diseaseRisk,
    'irrigationType': irrigationType,
    'avgYieldScore': avgYieldScore,
    'onTimePayments': onTimePayments,
    'latePayments': latePayments,
  };
}

/// نتيجة حساب التصنيف الائتماني
class CreditScoreResult {
  final int score;
  final CreditTier tier;
  final String tierAr;
  final double loanLimit;
  final Map<String, int> breakdown;

  const CreditScoreResult({
    required this.score,
    required this.tier,
    required this.tierAr,
    required this.loanLimit,
    required this.breakdown,
  });

  factory CreditScoreResult.fromJson(Map<String, dynamic> json) {
    return CreditScoreResult(
      score: json['score'] as int,
      tier: CreditTier.fromString(json['tier'] as String?),
      tierAr: json['tierAr'] as String? ?? 'برونزي',
      loanLimit: (json['loanLimit'] as num).toDouble(),
      breakdown: (json['breakdown'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toInt()),
      ) ?? {},
    );
  }
}

// =============================================================================
// نتائج القروض - Loan Result Models
// =============================================================================

/// نتيجة طلب القرض
class LoanRequestResult {
  final bool approved;
  final String message;
  final LoanModel? loan;
  final String? rejectionReason;

  const LoanRequestResult({
    required this.approved,
    required this.message,
    this.loan,
    this.rejectionReason,
  });

  factory LoanRequestResult.fromJson(Map<String, dynamic> json) {
    return LoanRequestResult(
      approved: json['approved'] as bool? ?? false,
      message: json['message'] as String? ?? '',
      loan: json['loan'] != null ? LoanModel.fromJson(json['loan'] as Map<String, dynamic>) : null,
      rejectionReason: json['rejectionReason'] as String?,
    );
  }
}

/// نتيجة سداد القرض
class LoanRepaymentResult {
  final bool success;
  final String message;
  final double paidAmount;
  final double remainingAmount;
  final LoanModel? loan;

  const LoanRepaymentResult({
    required this.success,
    required this.message,
    required this.paidAmount,
    required this.remainingAmount,
    this.loan,
  });

  factory LoanRepaymentResult.fromJson(Map<String, dynamic> json) {
    return LoanRepaymentResult(
      success: json['success'] as bool? ?? false,
      message: json['message'] as String? ?? '',
      paidAmount: (json['paidAmount'] as num?)?.toDouble() ?? 0,
      remainingAmount: (json['remainingAmount'] as num?)?.toDouble() ?? 0,
      loan: json['loan'] != null ? LoanModel.fromJson(json['loan'] as Map<String, dynamic>) : null,
    );
  }
}

// =============================================================================
// إحصائيات السوق - Market Stats
// =============================================================================

/// إحصائيات السوق
class MarketStats {
  final int totalProducts;
  final int totalOrders;
  final int totalSellers;
  final int totalBuyers;
  final double totalVolume;
  final Map<String, int> productsByCategory;
  final Map<String, int> ordersByStatus;
  final List<TopSeller> topSellers;

  const MarketStats({
    required this.totalProducts,
    required this.totalOrders,
    required this.totalSellers,
    required this.totalBuyers,
    required this.totalVolume,
    required this.productsByCategory,
    required this.ordersByStatus,
    required this.topSellers,
  });

  factory MarketStats.fromJson(Map<String, dynamic> json) {
    return MarketStats(
      totalProducts: json['totalProducts'] as int? ?? 0,
      totalOrders: json['totalOrders'] as int? ?? 0,
      totalSellers: json['totalSellers'] as int? ?? 0,
      totalBuyers: json['totalBuyers'] as int? ?? 0,
      totalVolume: (json['totalVolume'] as num?)?.toDouble() ?? 0,
      productsByCategory: (json['productsByCategory'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toInt()),
      ) ?? {},
      ordersByStatus: (json['ordersByStatus'] as Map<String, dynamic>?)?.map(
        (k, v) => MapEntry(k, (v as num).toInt()),
      ) ?? {},
      topSellers: (json['topSellers'] as List<dynamic>?)
          ?.map((e) => TopSeller.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }
}

/// أفضل البائعين
class TopSeller {
  final String sellerId;
  final String sellerName;
  final int totalSales;
  final double totalRevenue;

  const TopSeller({
    required this.sellerId,
    required this.sellerName,
    required this.totalSales,
    required this.totalRevenue,
  });

  factory TopSeller.fromJson(Map<String, dynamic> json) {
    return TopSeller(
      sellerId: json['sellerId'] as String,
      sellerName: json['sellerName'] as String? ?? 'بائع',
      totalSales: json['totalSales'] as int? ?? 0,
      totalRevenue: (json['totalRevenue'] as num?)?.toDouble() ?? 0,
    );
  }
}

// =============================================================================
// سلة التسوق - Cart Models
// =============================================================================

/// عنصر في سلة التسوق
class CartItem {
  final String productId;
  final ProductModel product;
  final double quantity;

  const CartItem({
    required this.productId,
    required this.product,
    required this.quantity,
  });

  CartItem copyWith({double? quantity}) {
    return CartItem(
      productId: productId,
      product: product,
      quantity: quantity ?? this.quantity,
    );
  }

  /// السعر الإجمالي للعنصر
  double get totalPrice => product.price * quantity;

  /// تحويل إلى JSON للـ API
  Map<String, dynamic> toJson() => {
    'productId': productId,
    'quantity': quantity,
  };
}
