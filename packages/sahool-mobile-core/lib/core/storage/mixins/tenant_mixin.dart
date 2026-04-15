import 'package:drift/drift.dart';

/// Tenant Mixin - لإضافة userId لجميع الجداول
/// يُستخدم لدعم Multi-tenant
mixin TenantMixin on Table {
  TextColumn get userId => text()();
}
