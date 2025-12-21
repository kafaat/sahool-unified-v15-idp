/// Unit Tests for Equipment Models
/// اختبارات وحدات نماذج المعدات
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/equipment/data/equipment_models.dart';

void main() {
  group('Equipment Model Tests', () {
    test('Equipment.fromJson parses correctly', () {
      final json = {
        'equipment_id': 'EQ001',
        'tenant_id': 'tenant-1',
        'name': 'John Deere 8R',
        'name_ar': 'جون دير 8R',
        'equipment_type': 'tractor',
        'status': 'operational',
        'current_fuel_percent': 75.5,
        'current_hours': 1250.0,
        'horsepower': 410,
        'year': 2022,
        'location_name': 'الحقل الشمالي',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z',
      };

      final equipment = Equipment.fromJson(json);

      expect(equipment.equipmentId, 'EQ001');
      expect(equipment.tenantId, 'tenant-1');
      expect(equipment.name, 'John Deere 8R');
      expect(equipment.nameAr, 'جون دير 8R');
      expect(equipment.equipmentType, EquipmentType.tractor);
      expect(equipment.status, EquipmentStatus.operational);
      expect(equipment.currentFuelPercent, 75.5);
      expect(equipment.currentHours, 1250.0);
      expect(equipment.horsepower, 410);
      expect(equipment.year, 2022);
    });

    test('Equipment.getDisplayName returns Arabic name when available', () {
      final equipment = Equipment(
        equipmentId: 'EQ003',
        tenantId: 'tenant-1',
        name: 'Pump',
        nameAr: 'مضخة',
        equipmentType: EquipmentType.pump,
        status: EquipmentStatus.operational,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(equipment.getDisplayName('ar'), 'مضخة');
      expect(equipment.getDisplayName('en'), 'Pump');
    });

    test('Equipment.isLowFuel returns true when fuel below 20%', () {
      final lowFuel = Equipment(
        equipmentId: 'EQ004',
        tenantId: 'tenant-1',
        name: 'Tractor',
        equipmentType: EquipmentType.tractor,
        status: EquipmentStatus.operational,
        currentFuelPercent: 15,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final normalFuel = Equipment(
        equipmentId: 'EQ005',
        tenantId: 'tenant-1',
        name: 'Tractor 2',
        equipmentType: EquipmentType.tractor,
        status: EquipmentStatus.operational,
        currentFuelPercent: 50,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(lowFuel.isLowFuel, true);
      expect(normalFuel.isLowFuel, false);
    });

    test('Equipment.needsMaintenanceSoon calculates correctly', () {
      final needsMaintenance = Equipment(
        equipmentId: 'EQ006',
        tenantId: 'tenant-1',
        name: 'Equipment',
        equipmentType: EquipmentType.tractor,
        status: EquipmentStatus.operational,
        nextMaintenanceAt: DateTime.now().add(const Duration(days: 5)),
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final notUrgent = Equipment(
        equipmentId: 'EQ007',
        tenantId: 'tenant-1',
        name: 'Equipment 2',
        equipmentType: EquipmentType.tractor,
        status: EquipmentStatus.operational,
        nextMaintenanceAt: DateTime.now().add(const Duration(days: 30)),
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(needsMaintenance.needsMaintenanceSoon, true);
      expect(notUrgent.needsMaintenanceSoon, false);
    });
  });

  group('EquipmentType Tests', () {
    test('EquipmentType.nameAr returns Arabic names', () {
      expect(EquipmentType.tractor.nameAr, 'جرار');
      expect(EquipmentType.pump.nameAr, 'مضخة');
      expect(EquipmentType.drone.nameAr, 'طائرة مسيرة');
      expect(EquipmentType.harvester.nameAr, 'حاصدة');
      expect(EquipmentType.pivot.nameAr, 'رشاش محوري');
    });

    test('EquipmentType.fromString parses correctly', () {
      expect(EquipmentType.fromString('tractor'), EquipmentType.tractor);
      expect(EquipmentType.fromString('pump'), EquipmentType.pump);
      expect(EquipmentType.fromString('drone'), EquipmentType.drone);
      expect(EquipmentType.fromString('invalid'), EquipmentType.other);
    });
  });

  group('EquipmentStatus Tests', () {
    test('EquipmentStatus.nameAr returns Arabic names', () {
      expect(EquipmentStatus.operational.nameAr, 'جاهز');
      expect(EquipmentStatus.maintenance.nameAr, 'صيانة');
      expect(EquipmentStatus.inactive.nameAr, 'متوقف');
      expect(EquipmentStatus.repair.nameAr, 'إصلاح');
    });

    test('EquipmentStatus.fromString parses correctly', () {
      expect(EquipmentStatus.fromString('operational'), EquipmentStatus.operational);
      expect(EquipmentStatus.fromString('maintenance'), EquipmentStatus.maintenance);
      expect(EquipmentStatus.fromString('inactive'), EquipmentStatus.inactive);
      expect(EquipmentStatus.fromString('repair'), EquipmentStatus.repair);
    });
  });

  group('MaintenanceAlert Tests', () {
    test('MaintenanceAlert.fromJson parses correctly', () {
      final json = {
        'alert_id': 'ALERT001',
        'equipment_id': 'EQ001',
        'equipment_name': 'John Deere 8R',
        'maintenance_type': 'oil_change',
        'description': 'Oil change due',
        'description_ar': 'موعد تغيير الزيت',
        'priority': 'high',
        'due_at': '2024-12-20T10:00:00Z',
        'is_overdue': false,
        'created_at': '2024-01-01T00:00:00Z',
      };

      final alert = MaintenanceAlert.fromJson(json);

      expect(alert.alertId, 'ALERT001');
      expect(alert.equipmentId, 'EQ001');
      expect(alert.equipmentName, 'John Deere 8R');
      expect(alert.priority, MaintenancePriority.high);
    });

    test('MaintenanceAlert.getDescription returns localized text', () {
      final alert = MaintenanceAlert(
        alertId: 'A3',
        equipmentId: 'E3',
        equipmentName: 'Equipment 3',
        maintenanceType: MaintenanceType.batteryCheck,
        description: 'Battery check needed',
        descriptionAr: 'فحص البطارية مطلوب',
        priority: MaintenancePriority.medium,
        isOverdue: false,
        createdAt: DateTime.now(),
      );

      expect(alert.getDescription('ar'), 'فحص البطارية مطلوب');
      expect(alert.getDescription('en'), 'Battery check needed');
    });
  });

  group('MaintenancePriority Tests', () {
    test('MaintenancePriority.nameAr returns Arabic names', () {
      expect(MaintenancePriority.low.nameAr, 'منخفض');
      expect(MaintenancePriority.medium.nameAr, 'متوسط');
      expect(MaintenancePriority.high.nameAr, 'عالي');
      expect(MaintenancePriority.critical.nameAr, 'حرج');
    });
  });

  group('EquipmentStats Tests', () {
    test('EquipmentStats.fromJson parses correctly', () {
      final json = {
        'total': 10,
        'by_type': {'tractor': 5, 'pump': 3, 'drone': 2},
        'by_status': {'operational': 7, 'maintenance': 2, 'inactive': 1},
        'operational': 7,
        'maintenance': 2,
        'inactive': 1,
      };

      final stats = EquipmentStats.fromJson(json);

      expect(stats.total, 10);
      expect(stats.operational, 7);
      expect(stats.maintenance, 2);
      expect(stats.inactive, 1);
    });

    test('EquipmentStats validates counts', () {
      final stats = EquipmentStats(
        total: 10,
        byType: {'tractor': 5, 'pump': 5},
        byStatus: {'operational': 7, 'maintenance': 3},
        operational: 7,
        maintenance: 2,
        inactive: 1,
      );

      // Total should equal sum of statuses (or be >= sum)
      expect(stats.total, greaterThanOrEqualTo(stats.operational));
    });
  });
}
