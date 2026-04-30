// AUTO-GENERATED - DO NOT EDIT MANUALLY
// Generated for the SAHOOL Low-Code PoC form guardrails.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/lowcode/generated/analyzesatellitegeometry_form.dart';

void main() {
  Widget buildSubject({
    String tenantId = 'tenant-001',
    Set<String> permissions = const {'analyzeSatelliteGeometry:write'},
    ValueChanged<Map<String, Object?>>? onSubmit,
  }) {
    return MaterialApp(
      home: Scaffold(
        body: AnalyzeSatelliteGeometryLowCodeForm(
          tenantId: tenantId,
          permissions: permissions,
          onSubmit: onSubmit ?? (_) {},
        ),
      ),
    );
  }

  testWidgets('Tenant Context missing shows guard message', (tester) async {
    await tester.pumpWidget(buildSubject(tenantId: ''));

    expect(find.text('Tenant context is required before UI generation.'), findsOneWidget);
    expect(find.byType(Form), findsNothing);
  });

  testWidgets('Permission missing shows guard message', (tester) async {
    await tester.pumpWidget(buildSubject(permissions: const <String>{}));

    expect(find.text('Missing permission for generated form.'), findsOneWidget);
    expect(find.byType(Form), findsNothing);
  });

  testWidgets('Required field empty shows validation error', (tester) async {
    await tester.pumpWidget(buildSubject());

    await tester.tap(find.text('Submit'));
    await tester.pump();

    expect(find.text('Required / مطلوب'), findsOneWidget);
  });

  testWidgets('Valid input calls onSubmit with payload', (tester) async {
    Map<String, Object?>? submitted;
    await tester.pumpWidget(buildSubject(onSubmit: (payload) => submitted = payload));

    await tester.enterText(find.byType(TextFormField).first, '{"type":"Polygon","coordinates":[]}');
    await tester.tap(find.text('Submit'));
    await tester.pump();

    expect(submitted, isNotNull);
    expect(submitted!['tenantId'], 'tenant-001');
    expect(submitted!['operationId'], 'analyzeSatelliteGeometry');
    expect(submitted!['method'], 'POST');
    expect(submitted!['path'], '/api/v1/satellite/v1/analyze');
    expect(submitted!['geometry'], '{"type":"Polygon","coordinates":[]}');
  });
}
