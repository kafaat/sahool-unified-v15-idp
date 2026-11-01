import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:intl/intl.dart' hide TextDirection;
import 'package:table_calendar/table_calendar.dart';

void main() {
  for (final language in ['ar', 'en']) {
    testWidgets('calendar renders and selects a day in $language',
        (tester) async {
      final focusedDay = DateTime(2030, 1, 15);
      DateTime? selectedDay;

      await tester.pumpWidget(MaterialApp(
        locale: Locale(language),
        supportedLocales: const [Locale('ar'), Locale('en')],
        localizationsDelegates: GlobalMaterialLocalizations.delegates,
        home: Scaffold(
          body: TableCalendar(
            firstDay: DateTime(2030),
            lastDay: DateTime(2030, 3, 31),
            focusedDay: focusedDay,
            locale: language,
            startingDayOfWeek: StartingDayOfWeek.saturday,
            headerStyle: const HeaderStyle(formatButtonVisible: false),
            onDaySelected: (selected, focused) => selectedDay = selected,
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text(DateFormat.yMMMM(language).format(focusedDay)),
          findsOneWidget);
      expect(
        Directionality.of(tester.element(find.byType(TableCalendar))),
        language == 'ar' ? TextDirection.rtl : TextDirection.ltr,
      );
      // TableCalendar's default day cells use day.day even for Arabic; its
      // localized month header and layout direction are checked above.
      await tester.tap(find.text('${focusedDay.day}'));
      await tester.pumpAndSettle();
      expect(isSameDay(selectedDay, focusedDay), isTrue);
      expect(tester.takeException(), isNull);
    });
  }
}
