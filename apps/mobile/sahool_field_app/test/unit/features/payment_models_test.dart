import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/payment/data/payment_models.dart';
import 'package:sahool_field_app/features/payment/data/tharwatt_service.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // PaymentStatus Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('PaymentStatus', () {
    test('has exactly 6 values', () {
      expect(PaymentStatus.values.length, 6);
    });

    test('contains all expected values', () {
      expect(PaymentStatus.values, contains(PaymentStatus.pending));
      expect(PaymentStatus.values, contains(PaymentStatus.processing));
      expect(PaymentStatus.values, contains(PaymentStatus.completed));
      expect(PaymentStatus.values, contains(PaymentStatus.failed));
      expect(PaymentStatus.values, contains(PaymentStatus.cancelled));
      expect(PaymentStatus.values, contains(PaymentStatus.refunded));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PaymentType Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('PaymentType', () {
    test('has exactly 5 values', () {
      expect(PaymentType.values.length, 5);
    });

    test('contains all expected values', () {
      expect(PaymentType.values, contains(PaymentType.deposit));
      expect(PaymentType.values, contains(PaymentType.withdraw));
      expect(PaymentType.values, contains(PaymentType.transfer));
      expect(PaymentType.values, contains(PaymentType.payment));
      expect(PaymentType.values, contains(PaymentType.topup));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PaymentMethod Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('PaymentMethod', () {
    test('has exactly 4 values', () {
      expect(PaymentMethod.values.length, 4);
    });

    test('contains all expected values', () {
      expect(PaymentMethod.values, contains(PaymentMethod.tharwatt));
      expect(PaymentMethod.values, contains(PaymentMethod.bankTransfer));
      expect(PaymentMethod.values, contains(PaymentMethod.mobileMoney));
      expect(PaymentMethod.values, contains(PaymentMethod.cash));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PaymentTransaction
  // ═══════════════════════════════════════════════════════════════════════════

  group('PaymentTransaction', () {
    final baseJson = <String, dynamic>{
      'id': 'txn-001',
      'externalId': 'ext-001',
      'walletId': 'wallet-001',
      'amount': 5000.0,
      'currency': 'YER',
      'status': 'completed',
      'type': 'deposit',
      'method': 'tharwatt',
      'description': 'Test deposit',
      'errorMessage': null,
      'metadata': {'key': 'value'},
      'createdAt': '2026-03-20T10:00:00.000Z',
      'completedAt': '2026-03-20T10:05:00.000Z',
    };

    test('fromJson creates PaymentTransaction with all fields', () {
      final txn = PaymentTransaction.fromJson(baseJson);
      expect(txn.id, 'txn-001');
      expect(txn.externalId, 'ext-001');
      expect(txn.walletId, 'wallet-001');
      expect(txn.amount, 5000.0);
      expect(txn.currency, 'YER');
      expect(txn.status, PaymentStatus.completed);
      expect(txn.type, PaymentType.deposit);
      expect(txn.method, PaymentMethod.tharwatt);
      expect(txn.description, 'Test deposit');
      expect(txn.errorMessage, isNull);
      expect(txn.metadata, {'key': 'value'});
      expect(txn.completedAt, isNotNull);
    });

    test('fromJson uses transactionId as fallback for id', () {
      final json = Map<String, dynamic>.from(baseJson);
      json.remove('id');
      json['transactionId'] = 'txn-fallback';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.id, 'txn-fallback');
    });

    test('fromJson uses reference as fallback for externalId', () {
      final json = Map<String, dynamic>.from(baseJson);
      json.remove('externalId');
      json['reference'] = 'ref-001';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.externalId, 'ref-001');
    });

    test('fromJson uses error as fallback for errorMessage', () {
      final json = Map<String, dynamic>.from(baseJson);
      json.remove('errorMessage');
      json['error'] = 'Something failed';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.errorMessage, 'Something failed');
    });

    test('fromJson uses paymentMethod as fallback for method', () {
      final json = Map<String, dynamic>.from(baseJson);
      json.remove('method');
      json['paymentMethod'] = 'cash';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.method, PaymentMethod.cash);
    });

    test('fromJson defaults currency to YER', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['currency'] = null;
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.currency, 'YER');
    });

    test('fromJson defaults amount to 0.0 when null', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['amount'] = null;
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.amount, 0.0);
    });

    test('fromJson converts integer amount to double', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['amount'] = 3000;
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.amount, 3000.0);
      expect(txn.amount, isA<double>());
    });

    test('fromJson handles null completedAt', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['completedAt'] = null;
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.completedAt, isNull);
    });

    test('fromJson parses status "success" as completed', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['status'] = 'success';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.status, PaymentStatus.completed);
    });

    test('fromJson parses status "error" as failed', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['status'] = 'error';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.status, PaymentStatus.failed);
    });

    test('fromJson parses status "canceled" (American spelling) as cancelled', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['status'] = 'canceled';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.status, PaymentStatus.cancelled);
    });

    test('fromJson defaults unknown status to pending', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['status'] = 'unknown_status';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.status, PaymentStatus.pending);
    });

    test('fromJson defaults null status to pending', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['status'] = null;
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.status, PaymentStatus.pending);
    });

    test('fromJson parses type "withdrawal" as withdraw', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['type'] = 'withdrawal';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.type, PaymentType.withdraw);
    });

    test('fromJson defaults unknown type to deposit', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['type'] = 'unknown_type';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.type, PaymentType.deposit);
    });

    test('fromJson parses method "bank" as bankTransfer', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['method'] = 'bank';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.method, PaymentMethod.bankTransfer);
    });

    test('fromJson parses method "bank_transfer" as bankTransfer', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['method'] = 'bank_transfer';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.method, PaymentMethod.bankTransfer);
    });

    test('fromJson parses method "mobile" as mobileMoney', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['method'] = 'mobile';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.method, PaymentMethod.mobileMoney);
    });

    test('fromJson parses method "mobile_money" as mobileMoney', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['method'] = 'mobile_money';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.method, PaymentMethod.mobileMoney);
    });

    test('fromJson defaults unknown method to tharwatt', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['method'] = 'unknown_method';
      final txn = PaymentTransaction.fromJson(json);
      expect(txn.method, PaymentMethod.tharwatt);
    });

    test('toJson produces correct map', () {
      final txn = PaymentTransaction.fromJson(baseJson);
      final json = txn.toJson();
      expect(json['id'], 'txn-001');
      expect(json['externalId'], 'ext-001');
      expect(json['walletId'], 'wallet-001');
      expect(json['amount'], 5000.0);
      expect(json['currency'], 'YER');
      expect(json['status'], 'completed');
      expect(json['type'], 'deposit');
      expect(json['method'], 'tharwatt');
      expect(json['createdAt'], isNotNull);
      expect(json['completedAt'], isNotNull);
    });

    test('toJson round-trips through fromJson', () {
      final txn = PaymentTransaction.fromJson(baseJson);
      final json = txn.toJson();
      final restored = PaymentTransaction.fromJson(json);
      expect(restored.id, txn.id);
      expect(restored.amount, txn.amount);
      expect(restored.status, txn.status);
      expect(restored.type, txn.type);
      expect(restored.method, txn.method);
    });

    test('statusAr returns correct Arabic for each status', () {
      final pending = PaymentTransaction.fromJson(
          {...baseJson, 'status': 'pending'});
      expect(pending.statusAr, 'قيد الانتظار');

      final processing = PaymentTransaction.fromJson(
          {...baseJson, 'status': 'processing'});
      expect(processing.statusAr, 'قيد المعالجة');

      final completed = PaymentTransaction.fromJson(
          {...baseJson, 'status': 'completed'});
      expect(completed.statusAr, 'مكتملة');

      final failed = PaymentTransaction.fromJson(
          {...baseJson, 'status': 'failed'});
      expect(failed.statusAr, 'فاشلة');

      final cancelled = PaymentTransaction.fromJson(
          {...baseJson, 'status': 'cancelled'});
      expect(cancelled.statusAr, 'ملغية');

      final refunded = PaymentTransaction.fromJson(
          {...baseJson, 'status': 'refunded'});
      expect(refunded.statusAr, 'مستردة');
    });

    test('typeAr returns correct Arabic for each type', () {
      final deposit = PaymentTransaction.fromJson(
          {...baseJson, 'type': 'deposit'});
      expect(deposit.typeAr, 'إيداع');

      final withdraw = PaymentTransaction.fromJson(
          {...baseJson, 'type': 'withdraw'});
      expect(withdraw.typeAr, 'سحب');

      final transfer = PaymentTransaction.fromJson(
          {...baseJson, 'type': 'transfer'});
      expect(transfer.typeAr, 'تحويل');

      final payment = PaymentTransaction.fromJson(
          {...baseJson, 'type': 'payment'});
      expect(payment.typeAr, 'دفع');

      final topup = PaymentTransaction.fromJson(
          {...baseJson, 'type': 'topup'});
      expect(topup.typeAr, 'شحن رصيد');
    });

    test('methodAr returns correct Arabic for each method', () {
      final tharwatt = PaymentTransaction.fromJson(
          {...baseJson, 'method': 'tharwatt'});
      expect(tharwatt.methodAr, 'ثروات');

      final bank = PaymentTransaction.fromJson(
          {...baseJson, 'method': 'bank'});
      expect(bank.methodAr, 'تحويل بنكي');

      final mobile = PaymentTransaction.fromJson(
          {...baseJson, 'method': 'mobile'});
      expect(mobile.methodAr, 'محفظة موبايل');

      final cash = PaymentTransaction.fromJson(
          {...baseJson, 'method': 'cash'});
      expect(cash.methodAr, 'نقدي');
    });

    test('equality uses Equatable props (id, externalId, walletId, amount, status)', () {
      final txn1 = PaymentTransaction.fromJson(baseJson);
      final txn2 = PaymentTransaction.fromJson(baseJson);
      expect(txn1, equals(txn2));
    });

    test('different id means not equal', () {
      final txn1 = PaymentTransaction.fromJson(baseJson);
      final txn2 = PaymentTransaction.fromJson({...baseJson, 'id': 'txn-999'});
      expect(txn1, isNot(equals(txn2)));
    });

    test('different amount means not equal', () {
      final txn1 = PaymentTransaction.fromJson(baseJson);
      final txn2 = PaymentTransaction.fromJson({...baseJson, 'amount': 9999.0});
      expect(txn1, isNot(equals(txn2)));
    });

    test('different status means not equal', () {
      final txn1 = PaymentTransaction.fromJson(baseJson);
      final txn2 = PaymentTransaction.fromJson({...baseJson, 'status': 'failed'});
      expect(txn1, isNot(equals(txn2)));
    });

    test('same props but different description are still equal', () {
      final txn1 = PaymentTransaction.fromJson(baseJson);
      final txn2 = PaymentTransaction.fromJson(
          {...baseJson, 'description': 'Different desc'});
      expect(txn1, equals(txn2));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // InitiatePaymentRequest
  // ═══════════════════════════════════════════════════════════════════════════

  group('InitiatePaymentRequest', () {
    test('toJson includes all provided fields', () {
      final req = InitiatePaymentRequest(
        amount: 1000.0,
        currency: 'YER',
        type: PaymentType.topup,
        description: 'Phone topup',
        phoneNumber: '777123456',
        accountNumber: null,
        metadata: {'source': 'app'},
      );
      final json = req.toJson();
      expect(json['amount'], 1000.0);
      expect(json['currency'], 'YER');
      expect(json['type'], 'topup');
      expect(json['description'], 'Phone topup');
      expect(json['phoneNumber'], '777123456');
      expect(json['accountNumber'], isNull);
      expect(json['metadata'], {'source': 'app'});
    });

    test('toJson defaults currency to YER', () {
      final req = InitiatePaymentRequest(
        amount: 500.0,
        type: PaymentType.deposit,
      );
      final json = req.toJson();
      expect(json['currency'], 'YER');
    });

    test('toJson includes type as string name', () {
      final req = InitiatePaymentRequest(
        amount: 500.0,
        type: PaymentType.transfer,
      );
      expect(req.toJson()['type'], 'transfer');
    });

    test('toJson includes null for optional fields when not provided', () {
      final req = InitiatePaymentRequest(
        amount: 200.0,
        type: PaymentType.payment,
      );
      final json = req.toJson();
      expect(json['description'], isNull);
      expect(json['phoneNumber'], isNull);
      expect(json['accountNumber'], isNull);
      expect(json['metadata'], isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // TharwattPaymentResponse
  // ═══════════════════════════════════════════════════════════════════════════

  group('TharwattPaymentResponse', () {
    final responseJson = <String, dynamic>{
      'transactionId': 'thr-001',
      'reference': 'ref-001',
      'status': 'success',
      'message': 'Payment successful',
      'redirectUrl': 'https://pay.tharwatt.com/redirect',
      'data': {'extra': 'info'},
    };

    test('fromJson creates response with all fields', () {
      final resp = TharwattPaymentResponse.fromJson(responseJson);
      expect(resp.transactionId, 'thr-001');
      expect(resp.reference, 'ref-001');
      expect(resp.status, 'success');
      expect(resp.message, 'Payment successful');
      expect(resp.redirectUrl, 'https://pay.tharwatt.com/redirect');
      expect(resp.data, {'extra': 'info'});
    });

    test('fromJson uses transaction_id as fallback', () {
      final json = <String, dynamic>{
        'transaction_id': 'thr-fallback',
        'status': 'pending',
      };
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.transactionId, 'thr-fallback');
    });

    test('fromJson uses id as fallback for transactionId', () {
      final json = <String, dynamic>{
        'id': 'thr-id',
        'status': 'pending',
      };
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.transactionId, 'thr-id');
    });

    test('fromJson defaults transactionId to empty string', () {
      final json = <String, dynamic>{'status': 'pending'};
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.transactionId, '');
    });

    test('fromJson uses ref as fallback for reference', () {
      final json = <String, dynamic>{
        'transactionId': 'thr-001',
        'ref': 'ref-alt',
        'status': 'pending',
      };
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.reference, 'ref-alt');
    });

    test('fromJson uses msg as fallback for message', () {
      final json = <String, dynamic>{
        'transactionId': 'thr-001',
        'msg': 'Alt message',
        'status': 'pending',
      };
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.message, 'Alt message');
    });

    test('fromJson uses redirect_url as fallback', () {
      final json = <String, dynamic>{
        'transactionId': 'thr-001',
        'redirect_url': 'https://alt.url',
        'status': 'pending',
      };
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.redirectUrl, 'https://alt.url');
    });

    test('fromJson uses url as fallback for redirectUrl', () {
      final json = <String, dynamic>{
        'transactionId': 'thr-001',
        'url': 'https://url.fallback',
        'status': 'pending',
      };
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.redirectUrl, 'https://url.fallback');
    });

    test('fromJson defaults status to pending', () {
      final json = <String, dynamic>{'transactionId': 'thr-001'};
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.status, 'pending');
    });

    test('isSuccess returns true for "success" status', () {
      final resp = TharwattPaymentResponse.fromJson(responseJson);
      expect(resp.isSuccess, true);
    });

    test('isSuccess returns true for "completed" status', () {
      final json = Map<String, dynamic>.from(responseJson);
      json['status'] = 'completed';
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.isSuccess, true);
    });

    test('isSuccess returns true for "SUCCESS" (case insensitive)', () {
      final json = Map<String, dynamic>.from(responseJson);
      json['status'] = 'SUCCESS';
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.isSuccess, true);
    });

    test('isSuccess returns false for "pending" status', () {
      final json = Map<String, dynamic>.from(responseJson);
      json['status'] = 'pending';
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.isSuccess, false);
    });

    test('isSuccess returns false for "failed" status', () {
      final json = Map<String, dynamic>.from(responseJson);
      json['status'] = 'failed';
      final resp = TharwattPaymentResponse.fromJson(json);
      expect(resp.isSuccess, false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // TharwattConfig
  // ═══════════════════════════════════════════════════════════════════════════

  group('TharwattConfig', () {
    test('test factory creates config with test URL', () {
      final config = TharwattConfig.test();
      expect(config.baseUrl, 'https://developers-test.tharwatt.com:5253');
      expect(config.isTestMode, true);
      expect(config.apiKey, isNull);
      expect(config.merchantId, isNull);
      expect(config.secretKey, isNull);
    });

    test('production factory creates config with production URL', () {
      final config = TharwattConfig.production(
        apiKey: 'key-123',
        merchantId: 'merchant-001',
        secretKey: 'secret-xyz',
      );
      expect(config.baseUrl, 'https://api.tharwatt.com');
      expect(config.isTestMode, false);
      expect(config.apiKey, 'key-123');
      expect(config.merchantId, 'merchant-001');
      expect(config.secretKey, 'secret-xyz');
    });

    test('default constructor defaults isTestMode to true', () {
      const config = TharwattConfig(baseUrl: 'https://custom.url');
      expect(config.isTestMode, true);
    });

    test('default constructor allows setting all fields', () {
      const config = TharwattConfig(
        baseUrl: 'https://custom.url',
        apiKey: 'key',
        merchantId: 'mid',
        secretKey: 'sk',
        isTestMode: false,
      );
      expect(config.baseUrl, 'https://custom.url');
      expect(config.apiKey, 'key');
      expect(config.merchantId, 'mid');
      expect(config.secretKey, 'sk');
      expect(config.isTestMode, false);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MobileOperator
  // ═══════════════════════════════════════════════════════════════════════════

  group('MobileOperator', () {
    final operatorJson = <String, dynamic>{
      'id': 'yemen_mobile',
      'name': 'Yemen Mobile',
      'nameAr': 'يمن موبايل',
      'logo': 'https://example.com/logo.png',
      'denominations': [100, 200, 500, 1000, 2000],
    };

    test('fromJson creates MobileOperator with all fields', () {
      final op = MobileOperator.fromJson(operatorJson);
      expect(op.id, 'yemen_mobile');
      expect(op.name, 'Yemen Mobile');
      expect(op.nameAr, 'يمن موبايل');
      expect(op.logo, 'https://example.com/logo.png');
      expect(op.denominations, [100.0, 200.0, 500.0, 1000.0, 2000.0]);
    });

    test('fromJson defaults id to empty string when null', () {
      final json = Map<String, dynamic>.from(operatorJson);
      json['id'] = null;
      final op = MobileOperator.fromJson(json);
      expect(op.id, '');
    });

    test('fromJson defaults name to empty string when null', () {
      final json = Map<String, dynamic>.from(operatorJson);
      json['name'] = null;
      json['nameAr'] = null;
      final op = MobileOperator.fromJson(json);
      expect(op.name, '');
    });

    test('fromJson uses name_ar as fallback for nameAr', () {
      final json = <String, dynamic>{
        'id': 'test',
        'name': 'Test Op',
        'name_ar': 'اختبار',
      };
      final op = MobileOperator.fromJson(json);
      expect(op.nameAr, 'اختبار');
    });

    test('fromJson uses name as fallback for nameAr when both ar keys are null', () {
      final json = <String, dynamic>{
        'id': 'test',
        'name': 'Test Op',
      };
      final op = MobileOperator.fromJson(json);
      expect(op.nameAr, 'Test Op');
    });

    test('fromJson handles null denominations', () {
      final json = Map<String, dynamic>.from(operatorJson);
      json['denominations'] = null;
      final op = MobileOperator.fromJson(json);
      expect(op.denominations, isEmpty);
    });

    test('fromJson handles null logo', () {
      final json = Map<String, dynamic>.from(operatorJson);
      json['logo'] = null;
      final op = MobileOperator.fromJson(json);
      expect(op.logo, isNull);
    });

    test('defaultOperators returns 4 operators', () {
      final operators = MobileOperator.defaultOperators;
      expect(operators.length, 4);
    });

    test('defaultOperators contains Yemen Mobile', () {
      final operators = MobileOperator.defaultOperators;
      final ym = operators.firstWhere((o) => o.id == 'yemen_mobile');
      expect(ym.name, 'Yemen Mobile');
      expect(ym.nameAr, 'يمن موبايل');
      expect(ym.denominations, [100, 200, 500, 1000, 2000]);
    });

    test('defaultOperators contains MTN Yemen', () {
      final operators = MobileOperator.defaultOperators;
      final mtn = operators.firstWhere((o) => o.id == 'mtn');
      expect(mtn.name, 'MTN Yemen');
      expect(mtn.nameAr, 'MTN اليمن');
    });

    test('defaultOperators contains Sabafon', () {
      final operators = MobileOperator.defaultOperators;
      final saba = operators.firstWhere((o) => o.id == 'sabafon');
      expect(saba.name, 'Sabafon');
      expect(saba.nameAr, 'سبأفون');
    });

    test('defaultOperators contains Y Telecom', () {
      final operators = MobileOperator.defaultOperators;
      final yt = operators.firstWhere((o) => o.id == 'y_telecom');
      expect(yt.name, 'Y Telecom');
      expect(yt.nameAr, 'واي');
    });

    test('all default operators have 5 denominations', () {
      for (final op in MobileOperator.defaultOperators) {
        expect(op.denominations.length, 5,
            reason: '${op.name} should have 5 denominations');
      }
    });

    test('all default operators have same denomination values', () {
      for (final op in MobileOperator.defaultOperators) {
        expect(op.denominations, [100, 200, 500, 1000, 2000],
            reason: '${op.name} denominations mismatch');
      }
    });
  });
}
