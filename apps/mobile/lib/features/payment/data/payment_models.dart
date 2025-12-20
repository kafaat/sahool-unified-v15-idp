/// نماذج بوابة المدفوعات
/// Payment Gateway Models

import 'package:equatable/equatable.dart';

/// حالة المعاملة
enum PaymentStatus {
  pending,    // قيد الانتظار
  processing, // قيد المعالجة
  completed,  // مكتملة
  failed,     // فاشلة
  cancelled,  // ملغية
  refunded,   // مستردة
}

/// نوع المعاملة
enum PaymentType {
  deposit,    // إيداع
  withdraw,   // سحب
  transfer,   // تحويل
  payment,    // دفع
  topup,      // شحن رصيد
}

/// طريقة الدفع
enum PaymentMethod {
  tharwatt,   // ثروات
  bankTransfer, // تحويل بنكي
  mobileMoney,  // محفظة موبايل
  cash,         // نقدي
}

/// معاملة الدفع
class PaymentTransaction extends Equatable {
  final String id;
  final String? externalId;
  final String walletId;
  final double amount;
  final String currency;
  final PaymentStatus status;
  final PaymentType type;
  final PaymentMethod method;
  final String? description;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;
  final DateTime createdAt;
  final DateTime? completedAt;

  const PaymentTransaction({
    required this.id,
    this.externalId,
    required this.walletId,
    required this.amount,
    this.currency = 'YER',
    required this.status,
    required this.type,
    required this.method,
    this.description,
    this.errorMessage,
    this.metadata,
    required this.createdAt,
    this.completedAt,
  });

  factory PaymentTransaction.fromJson(Map<String, dynamic> json) {
    return PaymentTransaction(
      id: json['id'] ?? json['transactionId'] ?? '',
      externalId: json['externalId'] ?? json['reference'],
      walletId: json['walletId'] ?? '',
      amount: (json['amount'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'YER',
      status: _parseStatus(json['status']),
      type: _parseType(json['type']),
      method: _parseMethod(json['method'] ?? json['paymentMethod']),
      description: json['description'],
      errorMessage: json['errorMessage'] ?? json['error'],
      metadata: json['metadata'],
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'])
          : DateTime.now(),
      completedAt: json['completedAt'] != null
          ? DateTime.parse(json['completedAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'externalId': externalId,
        'walletId': walletId,
        'amount': amount,
        'currency': currency,
        'status': status.name,
        'type': type.name,
        'method': method.name,
        'description': description,
        'errorMessage': errorMessage,
        'metadata': metadata,
        'createdAt': createdAt.toIso8601String(),
        'completedAt': completedAt?.toIso8601String(),
      };

  static PaymentStatus _parseStatus(String? status) {
    switch (status?.toLowerCase()) {
      case 'pending':
        return PaymentStatus.pending;
      case 'processing':
        return PaymentStatus.processing;
      case 'completed':
      case 'success':
        return PaymentStatus.completed;
      case 'failed':
      case 'error':
        return PaymentStatus.failed;
      case 'cancelled':
      case 'canceled':
        return PaymentStatus.cancelled;
      case 'refunded':
        return PaymentStatus.refunded;
      default:
        return PaymentStatus.pending;
    }
  }

  static PaymentType _parseType(String? type) {
    switch (type?.toLowerCase()) {
      case 'deposit':
        return PaymentType.deposit;
      case 'withdraw':
      case 'withdrawal':
        return PaymentType.withdraw;
      case 'transfer':
        return PaymentType.transfer;
      case 'payment':
        return PaymentType.payment;
      case 'topup':
        return PaymentType.topup;
      default:
        return PaymentType.deposit;
    }
  }

  static PaymentMethod _parseMethod(String? method) {
    switch (method?.toLowerCase()) {
      case 'tharwatt':
        return PaymentMethod.tharwatt;
      case 'bank':
      case 'bank_transfer':
        return PaymentMethod.bankTransfer;
      case 'mobile':
      case 'mobile_money':
        return PaymentMethod.mobileMoney;
      case 'cash':
        return PaymentMethod.cash;
      default:
        return PaymentMethod.tharwatt;
    }
  }

  String get statusAr {
    switch (status) {
      case PaymentStatus.pending:
        return 'قيد الانتظار';
      case PaymentStatus.processing:
        return 'قيد المعالجة';
      case PaymentStatus.completed:
        return 'مكتملة';
      case PaymentStatus.failed:
        return 'فاشلة';
      case PaymentStatus.cancelled:
        return 'ملغية';
      case PaymentStatus.refunded:
        return 'مستردة';
    }
  }

  String get typeAr {
    switch (type) {
      case PaymentType.deposit:
        return 'إيداع';
      case PaymentType.withdraw:
        return 'سحب';
      case PaymentType.transfer:
        return 'تحويل';
      case PaymentType.payment:
        return 'دفع';
      case PaymentType.topup:
        return 'شحن رصيد';
    }
  }

  String get methodAr {
    switch (method) {
      case PaymentMethod.tharwatt:
        return 'ثروات';
      case PaymentMethod.bankTransfer:
        return 'تحويل بنكي';
      case PaymentMethod.mobileMoney:
        return 'محفظة موبايل';
      case PaymentMethod.cash:
        return 'نقدي';
    }
  }

  @override
  List<Object?> get props => [id, externalId, walletId, amount, status];
}

/// طلب بدء الدفع
class InitiatePaymentRequest {
  final double amount;
  final String currency;
  final PaymentType type;
  final String? description;
  final String? phoneNumber;
  final String? accountNumber;
  final Map<String, dynamic>? metadata;

  InitiatePaymentRequest({
    required this.amount,
    this.currency = 'YER',
    required this.type,
    this.description,
    this.phoneNumber,
    this.accountNumber,
    this.metadata,
  });

  Map<String, dynamic> toJson() => {
        'amount': amount,
        'currency': currency,
        'type': type.name,
        'description': description,
        'phoneNumber': phoneNumber,
        'accountNumber': accountNumber,
        'metadata': metadata,
      };
}

/// استجابة بدء الدفع من Tharwatt
class TharwattPaymentResponse {
  final String transactionId;
  final String? reference;
  final String status;
  final String? message;
  final String? redirectUrl;
  final Map<String, dynamic>? data;

  TharwattPaymentResponse({
    required this.transactionId,
    this.reference,
    required this.status,
    this.message,
    this.redirectUrl,
    this.data,
  });

  factory TharwattPaymentResponse.fromJson(Map<String, dynamic> json) {
    return TharwattPaymentResponse(
      transactionId: json['transactionId'] ?? json['transaction_id'] ?? json['id'] ?? '',
      reference: json['reference'] ?? json['ref'],
      status: json['status'] ?? 'pending',
      message: json['message'] ?? json['msg'],
      redirectUrl: json['redirectUrl'] ?? json['redirect_url'] ?? json['url'],
      data: json['data'],
    );
  }

  bool get isSuccess =>
      status.toLowerCase() == 'success' || status.toLowerCase() == 'completed';
}

/// تكوين بوابة Tharwatt
class TharwattConfig {
  final String baseUrl;
  final String? apiKey;
  final String? merchantId;
  final String? secretKey;
  final bool isTestMode;

  const TharwattConfig({
    required this.baseUrl,
    this.apiKey,
    this.merchantId,
    this.secretKey,
    this.isTestMode = true,
  });

  /// التكوين الافتراضي للاختبار
  factory TharwattConfig.test() {
    return const TharwattConfig(
      baseUrl: 'https://developers-test.tharwatt.com:5253',
      isTestMode: true,
    );
  }

  /// التكوين الإنتاجي
  factory TharwattConfig.production({
    required String apiKey,
    required String merchantId,
    required String secretKey,
  }) {
    return TharwattConfig(
      baseUrl: 'https://api.tharwatt.com',
      apiKey: apiKey,
      merchantId: merchantId,
      secretKey: secretKey,
      isTestMode: false,
    );
  }
}
