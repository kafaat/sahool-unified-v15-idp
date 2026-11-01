import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/farm/presentation/screens/farm_creation_screen.dart';

void main() {
  testWidgets('changing governorate clears the previous district',
      (tester) async {
    await tester.pumpWidget(const ProviderScope(
      child: MaterialApp(home: FarmCreationScreen()),
    ));

    final dropdowns = find.byType(DropdownButtonFormField<String>);
    expect(dropdowns, findsOneWidget);
    tester
        .widget<DropdownButtonFormField<String>>(dropdowns)
        .onChanged!('صنعاء');
    await tester.pump();

    expect(dropdowns, findsNWidgets(2));
    tester
        .widget<DropdownButtonFormField<String>>(dropdowns.at(1))
        .onChanged!('صنعاء المدينة');
    await tester.pump();
    expect(
      tester.state<FormFieldState<String>>(dropdowns.at(1)).value,
      'صنعاء المدينة',
    );

    tester
        .widget<DropdownButtonFormField<String>>(dropdowns.first)
        .onChanged!('عدن');
    await tester.pump();
    expect(tester.state<FormFieldState<String>>(dropdowns.first).value, 'عدن');
    expect(tester.state<FormFieldState<String>>(dropdowns.at(1)).value, isNull);
    final district = tester.widget<DropdownButton<String>>(find.descendant(
      of: dropdowns.at(1),
      matching: find.byType(DropdownButton<String>),
    ));
    expect(district.items!.map((item) => item.value), contains('كريتر'));
    expect(district.items!.map((item) => item.value),
        isNot(contains('صنعاء المدينة')));
    expect(tester.takeException(), isNull);
  });
}
