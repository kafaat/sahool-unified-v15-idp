/// SAHOOL Mobile App - Generated Localization Files
/// DO NOT EDIT MANUALLY - Generated from ARB files in lib/l10n/
///
/// Supported locales:
/// - ar (Arabic) - Primary language for Yemen
/// - en (English)

import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_ar.dart';
import 'app_localizations_en.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('ar'),
    Locale('en')
  ];

  /// No description provided for @appName.
  ///
  /// In en, this message translates to:
  /// **'SAHOOL'**
  String get appName;

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'SAHOOL - Smart Agriculture Platform'**
  String get appTitle;

  /// No description provided for @appDescription.
  ///
  /// In en, this message translates to:
  /// **'Comprehensive platform for agricultural field management in Yemen'**
  String get appDescription;

  /// No description provided for @version.
  ///
  /// In en, this message translates to:
  /// **'Version'**
  String get version;

  /// No description provided for @buildNumber.
  ///
  /// In en, this message translates to:
  /// **'Build Number'**
  String get buildNumber;

  /// No description provided for @yes.
  ///
  /// In en, this message translates to:
  /// **'Yes'**
  String get yes;

  /// No description provided for @no.
  ///
  /// In en, this message translates to:
  /// **'No'**
  String get no;

  /// No description provided for @ok.
  ///
  /// In en, this message translates to:
  /// **'OK'**
  String get ok;

  /// No description provided for @cancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get cancel;

  /// No description provided for @save.
  ///
  /// In en, this message translates to:
  /// **'Save'**
  String get save;

  /// No description provided for @delete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get delete;

  /// No description provided for @edit.
  ///
  /// In en, this message translates to:
  /// **'Edit'**
  String get edit;

  /// No description provided for @add.
  ///
  /// In en, this message translates to:
  /// **'Add'**
  String get add;

  /// No description provided for @update.
  ///
  /// In en, this message translates to:
  /// **'Update'**
  String get update;

  /// No description provided for @create.
  ///
  /// In en, this message translates to:
  /// **'Create'**
  String get create;

  /// No description provided for @close.
  ///
  /// In en, this message translates to:
  /// **'Close'**
  String get close;

  /// No description provided for @back.
  ///
  /// In en, this message translates to:
  /// **'Back'**
  String get back;

  /// No description provided for @next.
  ///
  /// In en, this message translates to:
  /// **'Next'**
  String get next;

  /// No description provided for @previous.
  ///
  /// In en, this message translates to:
  /// **'Previous'**
  String get previous;

  /// No description provided for @done.
  ///
  /// In en, this message translates to:
  /// **'Done'**
  String get done;

  /// No description provided for @finish.
  ///
  /// In en, this message translates to:
  /// **'Finish'**
  String get finish;

  /// No description provided for @skip.
  ///
  /// In en, this message translates to:
  /// **'Skip'**
  String get skip;

  /// No description provided for @continue_.
  ///
  /// In en, this message translates to:
  /// **'Continue'**
  String get continue_;

  /// No description provided for @submit.
  ///
  /// In en, this message translates to:
  /// **'Submit'**
  String get submit;

  /// No description provided for @confirm.
  ///
  /// In en, this message translates to:
  /// **'Confirm'**
  String get confirm;

  /// No description provided for @retry.
  ///
  /// In en, this message translates to:
  /// **'Retry'**
  String get retry;

  /// No description provided for @refresh.
  ///
  /// In en, this message translates to:
  /// **'Refresh'**
  String get refresh;

  /// No description provided for @reload.
  ///
  /// In en, this message translates to:
  /// **'Reload'**
  String get reload;

  /// No description provided for @loading.
  ///
  /// In en, this message translates to:
  /// **'Loading...'**
  String get loading;

  /// No description provided for @processing.
  ///
  /// In en, this message translates to:
  /// **'Processing...'**
  String get processing;

  /// No description provided for @saving.
  ///
  /// In en, this message translates to:
  /// **'Saving...'**
  String get saving;

  /// No description provided for @deleting.
  ///
  /// In en, this message translates to:
  /// **'Deleting...'**
  String get deleting;

  /// No description provided for @updating.
  ///
  /// In en, this message translates to:
  /// **'Updating...'**
  String get updating;

  /// No description provided for @uploading.
  ///
  /// In en, this message translates to:
  /// **'Uploading...'**
  String get uploading;

  /// No description provided for @downloading.
  ///
  /// In en, this message translates to:
  /// **'Downloading...'**
  String get downloading;

  /// No description provided for @syncing.
  ///
  /// In en, this message translates to:
  /// **'Syncing...'**
  String get syncing;

  /// No description provided for @sending.
  ///
  /// In en, this message translates to:
  /// **'Sending...'**
  String get sending;

  /// No description provided for @searching.
  ///
  /// In en, this message translates to:
  /// **'Searching...'**
  String get searching;

  /// No description provided for @search.
  ///
  /// In en, this message translates to:
  /// **'Search'**
  String get search;

  /// No description provided for @filter.
  ///
  /// In en, this message translates to:
  /// **'Filter'**
  String get filter;

  /// No description provided for @sort.
  ///
  /// In en, this message translates to:
  /// **'Sort'**
  String get sort;

  /// No description provided for @view.
  ///
  /// In en, this message translates to:
  /// **'View'**
  String get view;

  /// No description provided for @share.
  ///
  /// In en, this message translates to:
  /// **'Share'**
  String get share;

  /// No description provided for @export.
  ///
  /// In en, this message translates to:
  /// **'Export'**
  String get export;

  /// No description provided for @import.
  ///
  /// In en, this message translates to:
  /// **'Import'**
  String get import;

  /// No description provided for @download.
  ///
  /// In en, this message translates to:
  /// **'Download'**
  String get download;

  /// No description provided for @upload.
  ///
  /// In en, this message translates to:
  /// **'Upload'**
  String get upload;

  /// No description provided for @select.
  ///
  /// In en, this message translates to:
  /// **'Select'**
  String get select;

  /// No description provided for @selectAll.
  ///
  /// In en, this message translates to:
  /// **'Select All'**
  String get selectAll;

  /// No description provided for @deselectAll.
  ///
  /// In en, this message translates to:
  /// **'Deselect All'**
  String get deselectAll;

  /// No description provided for @clear.
  ///
  /// In en, this message translates to:
  /// **'Clear'**
  String get clear;

  /// No description provided for @clearAll.
  ///
  /// In en, this message translates to:
  /// **'Clear All'**
  String get clearAll;

  /// No description provided for @apply.
  ///
  /// In en, this message translates to:
  /// **'Apply'**
  String get apply;

  /// No description provided for @reset.
  ///
  /// In en, this message translates to:
  /// **'Reset'**
  String get reset;

  /// No description provided for @undo.
  ///
  /// In en, this message translates to:
  /// **'Undo'**
  String get undo;

  /// No description provided for @redo.
  ///
  /// In en, this message translates to:
  /// **'Redo'**
  String get redo;

  /// No description provided for @copy.
  ///
  /// In en, this message translates to:
  /// **'Copy'**
  String get copy;

  /// No description provided for @paste.
  ///
  /// In en, this message translates to:
  /// **'Paste'**
  String get paste;

  /// No description provided for @cut.
  ///
  /// In en, this message translates to:
  /// **'Cut'**
  String get cut;

  /// No description provided for @duplicate.
  ///
  /// In en, this message translates to:
  /// **'Duplicate'**
  String get duplicate;

  /// No description provided for @move.
  ///
  /// In en, this message translates to:
  /// **'Move'**
  String get move;

  /// No description provided for @rename.
  ///
  /// In en, this message translates to:
  /// **'Rename'**
  String get rename;

  /// No description provided for @details.
  ///
  /// In en, this message translates to:
  /// **'Details'**
  String get details;

  /// No description provided for @info.
  ///
  /// In en, this message translates to:
  /// **'Info'**
  String get info;

  /// No description provided for @help.
  ///
  /// In en, this message translates to:
  /// **'Help'**
  String get help;

  /// No description provided for @about.
  ///
  /// In en, this message translates to:
  /// **'About'**
  String get about;

  /// No description provided for @settings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get settings;

  /// No description provided for @preferences.
  ///
  /// In en, this message translates to:
  /// **'Preferences'**
  String get preferences;

  /// No description provided for @options.
  ///
  /// In en, this message translates to:
  /// **'Options'**
  String get options;

  /// No description provided for @more.
  ///
  /// In en, this message translates to:
  /// **'More'**
  String get more;

  /// No description provided for @less.
  ///
  /// In en, this message translates to:
  /// **'Less'**
  String get less;

  /// No description provided for @show.
  ///
  /// In en, this message translates to:
  /// **'Show'**
  String get show;

  /// No description provided for @hide.
  ///
  /// In en, this message translates to:
  /// **'Hide'**
  String get hide;

  /// No description provided for @expand.
  ///
  /// In en, this message translates to:
  /// **'Expand'**
  String get expand;

  /// No description provided for @collapse.
  ///
  /// In en, this message translates to:
  /// **'Collapse'**
  String get collapse;

  /// No description provided for @maximize.
  ///
  /// In en, this message translates to:
  /// **'Maximize'**
  String get maximize;

  /// No description provided for @minimize.
  ///
  /// In en, this message translates to:
  /// **'Minimize'**
  String get minimize;

  /// No description provided for @enable.
  ///
  /// In en, this message translates to:
  /// **'Enable'**
  String get enable;

  /// No description provided for @disable.
  ///
  /// In en, this message translates to:
  /// **'Disable'**
  String get disable;

  /// No description provided for @activate.
  ///
  /// In en, this message translates to:
  /// **'Activate'**
  String get activate;

  /// No description provided for @deactivate.
  ///
  /// In en, this message translates to:
  /// **'Deactivate'**
  String get deactivate;

  /// No description provided for @on.
  ///
  /// In en, this message translates to:
  /// **'On'**
  String get on;

  /// No description provided for @off.
  ///
  /// In en, this message translates to:
  /// **'Off'**
  String get off;

  /// No description provided for @open.
  ///
  /// In en, this message translates to:
  /// **'Open'**
  String get open;

  /// No description provided for @print.
  ///
  /// In en, this message translates to:
  /// **'Print'**
  String get print;

  /// No description provided for @preview.
  ///
  /// In en, this message translates to:
  /// **'Preview'**
  String get preview;

  /// No description provided for @zoom.
  ///
  /// In en, this message translates to:
  /// **'Zoom'**
  String get zoom;

  /// No description provided for @zoomIn.
  ///
  /// In en, this message translates to:
  /// **'Zoom In'**
  String get zoomIn;

  /// No description provided for @zoomOut.
  ///
  /// In en, this message translates to:
  /// **'Zoom Out'**
  String get zoomOut;

  /// No description provided for @fitToScreen.
  ///
  /// In en, this message translates to:
  /// **'Fit to Screen'**
  String get fitToScreen;

  /// No description provided for @fullScreen.
  ///
  /// In en, this message translates to:
  /// **'Full Screen'**
  String get fullScreen;

  /// No description provided for @exitFullScreen.
  ///
  /// In en, this message translates to:
  /// **'Exit Full Screen'**
  String get exitFullScreen;

  /// No description provided for @active.
  ///
  /// In en, this message translates to:
  /// **'Active'**
  String get active;

  /// No description provided for @inactive.
  ///
  /// In en, this message translates to:
  /// **'Inactive'**
  String get inactive;

  /// No description provided for @enabled.
  ///
  /// In en, this message translates to:
  /// **'Enabled'**
  String get enabled;

  /// No description provided for @disabled.
  ///
  /// In en, this message translates to:
  /// **'Disabled'**
  String get disabled;

  /// No description provided for @online.
  ///
  /// In en, this message translates to:
  /// **'Online'**
  String get online;

  /// No description provided for @offline.
  ///
  /// In en, this message translates to:
  /// **'Offline'**
  String get offline;

  /// No description provided for @available.
  ///
  /// In en, this message translates to:
  /// **'Available'**
  String get available;

  /// No description provided for @unavailable.
  ///
  /// In en, this message translates to:
  /// **'Unavailable'**
  String get unavailable;

  /// No description provided for @pending.
  ///
  /// In en, this message translates to:
  /// **'Pending'**
  String get pending;

  /// No description provided for @approved.
  ///
  /// In en, this message translates to:
  /// **'Approved'**
  String get approved;

  /// No description provided for @rejected.
  ///
  /// In en, this message translates to:
  /// **'Rejected'**
  String get rejected;

  /// No description provided for @completed.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get completed;

  /// No description provided for @inProgress.
  ///
  /// In en, this message translates to:
  /// **'In Progress'**
  String get inProgress;

  /// No description provided for @notStarted.
  ///
  /// In en, this message translates to:
  /// **'Not Started'**
  String get notStarted;

  /// No description provided for @cancelled.
  ///
  /// In en, this message translates to:
  /// **'Cancelled'**
  String get cancelled;

  /// No description provided for @failed.
  ///
  /// In en, this message translates to:
  /// **'Failed'**
  String get failed;

  /// No description provided for @success.
  ///
  /// In en, this message translates to:
  /// **'Success'**
  String get success;

  /// No description provided for @error.
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error;

  /// No description provided for @warning.
  ///
  /// In en, this message translates to:
  /// **'Warning'**
  String get warning;

  /// No description provided for @info_.
  ///
  /// In en, this message translates to:
  /// **'Info'**
  String get info_;

  /// No description provided for @today.
  ///
  /// In en, this message translates to:
  /// **'Today'**
  String get today;

  /// No description provided for @yesterday.
  ///
  /// In en, this message translates to:
  /// **'Yesterday'**
  String get yesterday;

  /// No description provided for @tomorrow.
  ///
  /// In en, this message translates to:
  /// **'Tomorrow'**
  String get tomorrow;

  /// No description provided for @now.
  ///
  /// In en, this message translates to:
  /// **'Now'**
  String get now;

  /// No description provided for @recently.
  ///
  /// In en, this message translates to:
  /// **'Recently'**
  String get recently;

  /// No description provided for @date.
  ///
  /// In en, this message translates to:
  /// **'Date'**
  String get date;

  /// No description provided for @time.
  ///
  /// In en, this message translates to:
  /// **'Time'**
  String get time;

  /// No description provided for @dateTime.
  ///
  /// In en, this message translates to:
  /// **'Date & Time'**
  String get dateTime;

  /// No description provided for @startDate.
  ///
  /// In en, this message translates to:
  /// **'Start Date'**
  String get startDate;

  /// No description provided for @endDate.
  ///
  /// In en, this message translates to:
  /// **'End Date'**
  String get endDate;

  /// No description provided for @startTime.
  ///
  /// In en, this message translates to:
  /// **'Start Time'**
  String get startTime;

  /// No description provided for @endTime.
  ///
  /// In en, this message translates to:
  /// **'End Time'**
  String get endTime;

  /// No description provided for @duration.
  ///
  /// In en, this message translates to:
  /// **'Duration'**
  String get duration;

  /// No description provided for @timezone.
  ///
  /// In en, this message translates to:
  /// **'Timezone'**
  String get timezone;

  /// No description provided for @calendar.
  ///
  /// In en, this message translates to:
  /// **'Calendar'**
  String get calendar;

  /// No description provided for @schedule.
  ///
  /// In en, this message translates to:
  /// **'Schedule'**
  String get schedule;

  /// No description provided for @day.
  ///
  /// In en, this message translates to:
  /// **'Day'**
  String get day;

  /// No description provided for @week.
  ///
  /// In en, this message translates to:
  /// **'Week'**
  String get week;

  /// No description provided for @month.
  ///
  /// In en, this message translates to:
  /// **'Month'**
  String get month;

  /// No description provided for @year.
  ///
  /// In en, this message translates to:
  /// **'Year'**
  String get year;

  /// No description provided for @hour.
  ///
  /// In en, this message translates to:
  /// **'Hour'**
  String get hour;

  /// No description provided for @minute.
  ///
  /// In en, this message translates to:
  /// **'Minute'**
  String get minute;

  /// No description provided for @second.
  ///
  /// In en, this message translates to:
  /// **'Second'**
  String get second;

  /// No description provided for @days.
  ///
  /// In en, this message translates to:
  /// **'Days'**
  String get days;

  /// No description provided for @weeks.
  ///
  /// In en, this message translates to:
  /// **'Weeks'**
  String get weeks;

  /// No description provided for @months.
  ///
  /// In en, this message translates to:
  /// **'Months'**
  String get months;

  /// No description provided for @years.
  ///
  /// In en, this message translates to:
  /// **'Years'**
  String get years;

  /// No description provided for @hours.
  ///
  /// In en, this message translates to:
  /// **'Hours'**
  String get hours;

  /// No description provided for @minutes.
  ///
  /// In en, this message translates to:
  /// **'Minutes'**
  String get minutes;

  /// No description provided for @seconds.
  ///
  /// In en, this message translates to:
  /// **'Seconds'**
  String get seconds;

  /// No description provided for @am.
  ///
  /// In en, this message translates to:
  /// **'AM'**
  String get am;

  /// No description provided for @pm.
  ///
  /// In en, this message translates to:
  /// **'PM'**
  String get pm;

  /// No description provided for @count.
  ///
  /// In en, this message translates to:
  /// **'Count'**
  String get count;

  /// No description provided for @total.
  ///
  /// In en, this message translates to:
  /// **'Total'**
  String get total;

  /// No description provided for @subtotal.
  ///
  /// In en, this message translates to:
  /// **'Subtotal'**
  String get subtotal;

  /// No description provided for @average.
  ///
  /// In en, this message translates to:
  /// **'Average'**
  String get average;

  /// No description provided for @minimum.
  ///
  /// In en, this message translates to:
  /// **'Minimum'**
  String get minimum;

  /// No description provided for @maximum.
  ///
  /// In en, this message translates to:
  /// **'Maximum'**
  String get maximum;

  /// No description provided for @sum.
  ///
  /// In en, this message translates to:
  /// **'Sum'**
  String get sum;

  /// No description provided for @percentage.
  ///
  /// In en, this message translates to:
  /// **'Percentage'**
  String get percentage;

  /// No description provided for @ratio.
  ///
  /// In en, this message translates to:
  /// **'Ratio'**
  String get ratio;

  /// No description provided for @rate.
  ///
  /// In en, this message translates to:
  /// **'Rate'**
  String get rate;

  /// No description provided for @quantity.
  ///
  /// In en, this message translates to:
  /// **'Quantity'**
  String get quantity;

  /// No description provided for @amount.
  ///
  /// In en, this message translates to:
  /// **'Amount'**
  String get amount;

  /// No description provided for @value.
  ///
  /// In en, this message translates to:
  /// **'Value'**
  String get value;

  /// No description provided for @price.
  ///
  /// In en, this message translates to:
  /// **'Price'**
  String get price;

  /// No description provided for @cost.
  ///
  /// In en, this message translates to:
  /// **'Cost'**
  String get cost;

  /// No description provided for @unit.
  ///
  /// In en, this message translates to:
  /// **'Unit'**
  String get unit;

  /// No description provided for @units.
  ///
  /// In en, this message translates to:
  /// **'Units'**
  String get units;

  /// No description provided for @home.
  ///
  /// In en, this message translates to:
  /// **'Home'**
  String get home;

  /// No description provided for @dashboard.
  ///
  /// In en, this message translates to:
  /// **'Dashboard'**
  String get dashboard;

  /// No description provided for @fields.
  ///
  /// In en, this message translates to:
  /// **'Fields'**
  String get fields;

  /// No description provided for @myFields.
  ///
  /// In en, this message translates to:
  /// **'My Fields'**
  String get myFields;

  /// No description provided for @fieldsList.
  ///
  /// In en, this message translates to:
  /// **'Fields List'**
  String get fieldsList;

  /// No description provided for @fieldDetails.
  ///
  /// In en, this message translates to:
  /// **'Field Details'**
  String get fieldDetails;

  /// No description provided for @addField.
  ///
  /// In en, this message translates to:
  /// **'Add Field'**
  String get addField;

  /// No description provided for @editField.
  ///
  /// In en, this message translates to:
  /// **'Edit Field'**
  String get editField;

  /// No description provided for @deleteField.
  ///
  /// In en, this message translates to:
  /// **'Delete Field'**
  String get deleteField;

  /// No description provided for @weather.
  ///
  /// In en, this message translates to:
  /// **'Weather'**
  String get weather;

  /// No description provided for @weatherForecast.
  ///
  /// In en, this message translates to:
  /// **'Weather Forecast'**
  String get weatherForecast;

  /// No description provided for @weatherAlerts.
  ///
  /// In en, this message translates to:
  /// **'Weather Alerts'**
  String get weatherAlerts;

  /// No description provided for @satellite.
  ///
  /// In en, this message translates to:
  /// **'Satellite'**
  String get satellite;

  /// No description provided for @satelliteImagery.
  ///
  /// In en, this message translates to:
  /// **'Satellite Imagery'**
  String get satelliteImagery;

  /// No description provided for @ndvi.
  ///
  /// In en, this message translates to:
  /// **'NDVI'**
  String get ndvi;

  /// No description provided for @ndviMap.
  ///
  /// In en, this message translates to:
  /// **'NDVI Map'**
  String get ndviMap;

  /// No description provided for @ndviAnalysis.
  ///
  /// In en, this message translates to:
  /// **'NDVI Analysis'**
  String get ndviAnalysis;

  /// No description provided for @ndviHistory.
  ///
  /// In en, this message translates to:
  /// **'NDVI History'**
  String get ndviHistory;

  /// No description provided for @vra.
  ///
  /// In en, this message translates to:
  /// **'Variable Rate Application'**
  String get vra;

  /// No description provided for @vraMap.
  ///
  /// In en, this message translates to:
  /// **'VRA Map'**
  String get vraMap;

  /// No description provided for @vraPrescription.
  ///
  /// In en, this message translates to:
  /// **'VRA Prescription'**
  String get vraPrescription;

  /// No description provided for @vraZones.
  ///
  /// In en, this message translates to:
  /// **'VRA Zones'**
  String get vraZones;

  /// No description provided for @gdd.
  ///
  /// In en, this message translates to:
  /// **'Growing Degree Days'**
  String get gdd;

  /// No description provided for @gddCalculator.
  ///
  /// In en, this message translates to:
  /// **'GDD Calculator'**
  String get gddCalculator;

  /// No description provided for @gddTracking.
  ///
  /// In en, this message translates to:
  /// **'GDD Tracking'**
  String get gddTracking;

  /// No description provided for @gddForecast.
  ///
  /// In en, this message translates to:
  /// **'GDD Forecast'**
  String get gddForecast;

  /// No description provided for @spray.
  ///
  /// In en, this message translates to:
  /// **'Spray'**
  String get spray;

  /// No description provided for @sprayRecommendations.
  ///
  /// In en, this message translates to:
  /// **'Spray Recommendations'**
  String get sprayRecommendations;

  /// No description provided for @spraySchedule.
  ///
  /// In en, this message translates to:
  /// **'Spray Schedule'**
  String get spraySchedule;

  /// No description provided for @sprayHistory.
  ///
  /// In en, this message translates to:
  /// **'Spray History'**
  String get sprayHistory;

  /// No description provided for @sprayTiming.
  ///
  /// In en, this message translates to:
  /// **'Spray Timing'**
  String get sprayTiming;

  /// No description provided for @rotation.
  ///
  /// In en, this message translates to:
  /// **'Crop Rotation'**
  String get rotation;

  /// No description provided for @rotationPlan.
  ///
  /// In en, this message translates to:
  /// **'Rotation Plan'**
  String get rotationPlan;

  /// No description provided for @rotationHistory.
  ///
  /// In en, this message translates to:
  /// **'Rotation History'**
  String get rotationHistory;

  /// No description provided for @rotationAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Rotation Analysis'**
  String get rotationAnalysis;

  /// No description provided for @profitability.
  ///
  /// In en, this message translates to:
  /// **'Profitability'**
  String get profitability;

  /// No description provided for @profitabilityAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Profitability Analysis'**
  String get profitabilityAnalysis;

  /// No description provided for @profitabilityReport.
  ///
  /// In en, this message translates to:
  /// **'Profitability Report'**
  String get profitabilityReport;

  /// No description provided for @profitabilityDashboard.
  ///
  /// In en, this message translates to:
  /// **'Profitability Dashboard'**
  String get profitabilityDashboard;

  /// No description provided for @inventory.
  ///
  /// In en, this message translates to:
  /// **'Inventory'**
  String get inventory;

  /// No description provided for @inventoryManagement.
  ///
  /// In en, this message translates to:
  /// **'Inventory Management'**
  String get inventoryManagement;

  /// No description provided for @inventoryList.
  ///
  /// In en, this message translates to:
  /// **'Inventory List'**
  String get inventoryList;

  /// No description provided for @inventoryMovements.
  ///
  /// In en, this message translates to:
  /// **'Inventory Movements'**
  String get inventoryMovements;

  /// No description provided for @crops.
  ///
  /// In en, this message translates to:
  /// **'Crops'**
  String get crops;

  /// No description provided for @cropsList.
  ///
  /// In en, this message translates to:
  /// **'Crops List'**
  String get cropsList;

  /// No description provided for @cropDetails.
  ///
  /// In en, this message translates to:
  /// **'Crop Details'**
  String get cropDetails;

  /// No description provided for @cropHealth.
  ///
  /// In en, this message translates to:
  /// **'Crop Health'**
  String get cropHealth;

  /// No description provided for @chat.
  ///
  /// In en, this message translates to:
  /// **'Chat'**
  String get chat;

  /// No description provided for @messages.
  ///
  /// In en, this message translates to:
  /// **'Messages'**
  String get messages;

  /// No description provided for @conversations.
  ///
  /// In en, this message translates to:
  /// **'Conversations'**
  String get conversations;

  /// No description provided for @notifications.
  ///
  /// In en, this message translates to:
  /// **'Notifications'**
  String get notifications;

  /// No description provided for @alerts.
  ///
  /// In en, this message translates to:
  /// **'Alerts'**
  String get alerts;

  /// No description provided for @smartAlerts.
  ///
  /// In en, this message translates to:
  /// **'Smart Alerts'**
  String get smartAlerts;

  /// No description provided for @tasks.
  ///
  /// In en, this message translates to:
  /// **'Tasks'**
  String get tasks;

  /// No description provided for @myTasks.
  ///
  /// In en, this message translates to:
  /// **'My Tasks'**
  String get myTasks;

  /// No description provided for @tasksList.
  ///
  /// In en, this message translates to:
  /// **'Tasks List'**
  String get tasksList;

  /// No description provided for @taskDetails.
  ///
  /// In en, this message translates to:
  /// **'Task Details'**
  String get taskDetails;

  /// No description provided for @equipment.
  ///
  /// In en, this message translates to:
  /// **'Equipment'**
  String get equipment;

  /// No description provided for @equipmentList.
  ///
  /// In en, this message translates to:
  /// **'Equipment List'**
  String get equipmentList;

  /// No description provided for @equipmentDetails.
  ///
  /// In en, this message translates to:
  /// **'Equipment Details'**
  String get equipmentDetails;

  /// No description provided for @map.
  ///
  /// In en, this message translates to:
  /// **'Map'**
  String get map;

  /// No description provided for @maps.
  ///
  /// In en, this message translates to:
  /// **'Maps'**
  String get maps;

  /// No description provided for @mapView.
  ///
  /// In en, this message translates to:
  /// **'Map View'**
  String get mapView;

  /// No description provided for @satellite_map.
  ///
  /// In en, this message translates to:
  /// **'Satellite Map'**
  String get satellite_map;

  /// No description provided for @terrain.
  ///
  /// In en, this message translates to:
  /// **'Terrain'**
  String get terrain;

  /// No description provided for @analytics.
  ///
  /// In en, this message translates to:
  /// **'Analytics'**
  String get analytics;

  /// No description provided for @reports.
  ///
  /// In en, this message translates to:
  /// **'Reports'**
  String get reports;

  /// No description provided for @statistics.
  ///
  /// In en, this message translates to:
  /// **'Statistics'**
  String get statistics;

  /// No description provided for @profile.
  ///
  /// In en, this message translates to:
  /// **'Profile'**
  String get profile;

  /// No description provided for @myProfile.
  ///
  /// In en, this message translates to:
  /// **'My Profile'**
  String get myProfile;

  /// No description provided for @account.
  ///
  /// In en, this message translates to:
  /// **'Account'**
  String get account;

  /// No description provided for @accountSettings.
  ///
  /// In en, this message translates to:
  /// **'Account Settings'**
  String get accountSettings;

  /// No description provided for @wallet.
  ///
  /// In en, this message translates to:
  /// **'Wallet'**
  String get wallet;

  /// No description provided for @payment.
  ///
  /// In en, this message translates to:
  /// **'Payment'**
  String get payment;

  /// No description provided for @billing.
  ///
  /// In en, this message translates to:
  /// **'Billing'**
  String get billing;

  /// No description provided for @marketplace.
  ///
  /// In en, this message translates to:
  /// **'Marketplace'**
  String get marketplace;

  /// No description provided for @market.
  ///
  /// In en, this message translates to:
  /// **'Market'**
  String get market;

  /// No description provided for @community.
  ///
  /// In en, this message translates to:
  /// **'Community'**
  String get community;

  /// No description provided for @advisor.
  ///
  /// In en, this message translates to:
  /// **'Advisor'**
  String get advisor;

  /// No description provided for @aiAdvisor.
  ///
  /// In en, this message translates to:
  /// **'AI Advisor'**
  String get aiAdvisor;

  /// No description provided for @research.
  ///
  /// In en, this message translates to:
  /// **'Research'**
  String get research;

  /// No description provided for @lab.
  ///
  /// In en, this message translates to:
  /// **'Lab'**
  String get lab;

  /// No description provided for @scanner.
  ///
  /// In en, this message translates to:
  /// **'Scanner'**
  String get scanner;

  /// No description provided for @scouting.
  ///
  /// In en, this message translates to:
  /// **'Scouting'**
  String get scouting;

  /// No description provided for @fieldScout.
  ///
  /// In en, this message translates to:
  /// **'Field Scout'**
  String get fieldScout;

  /// No description provided for @iot.
  ///
  /// In en, this message translates to:
  /// **'IoT'**
  String get iot;

  /// No description provided for @virtualSensors.
  ///
  /// In en, this message translates to:
  /// **'Virtual Sensors'**
  String get virtualSensors;

  /// No description provided for @gamification.
  ///
  /// In en, this message translates to:
  /// **'Gamification'**
  String get gamification;

  /// No description provided for @onboarding.
  ///
  /// In en, this message translates to:
  /// **'Onboarding'**
  String get onboarding;

  /// No description provided for @sync.
  ///
  /// In en, this message translates to:
  /// **'Sync'**
  String get sync;

  /// No description provided for @dailyBrief.
  ///
  /// In en, this message translates to:
  /// **'Daily Brief'**
  String get dailyBrief;

  /// No description provided for @login.
  ///
  /// In en, this message translates to:
  /// **'Login'**
  String get login;

  /// No description provided for @logout.
  ///
  /// In en, this message translates to:
  /// **'Logout'**
  String get logout;

  /// No description provided for @signIn.
  ///
  /// In en, this message translates to:
  /// **'Sign In'**
  String get signIn;

  /// No description provided for @signOut.
  ///
  /// In en, this message translates to:
  /// **'Sign Out'**
  String get signOut;

  /// No description provided for @signUp.
  ///
  /// In en, this message translates to:
  /// **'Sign Up'**
  String get signUp;

  /// No description provided for @register.
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get register;

  /// No description provided for @registration.
  ///
  /// In en, this message translates to:
  /// **'Registration'**
  String get registration;

  /// No description provided for @email.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get email;

  /// No description provided for @emailAddress.
  ///
  /// In en, this message translates to:
  /// **'Email Address'**
  String get emailAddress;

  /// No description provided for @password.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get password;

  /// No description provided for @passwordConfirm.
  ///
  /// In en, this message translates to:
  /// **'Confirm Password'**
  String get passwordConfirm;

  /// No description provided for @oldPassword.
  ///
  /// In en, this message translates to:
  /// **'Old Password'**
  String get oldPassword;

  /// No description provided for @newPassword.
  ///
  /// In en, this message translates to:
  /// **'New Password'**
  String get newPassword;

  /// No description provided for @confirmPassword.
  ///
  /// In en, this message translates to:
  /// **'Confirm Password'**
  String get confirmPassword;

  /// No description provided for @forgotPassword.
  ///
  /// In en, this message translates to:
  /// **'Forgot Password?'**
  String get forgotPassword;

  /// No description provided for @resetPassword.
  ///
  /// In en, this message translates to:
  /// **'Reset Password'**
  String get resetPassword;

  /// No description provided for @changePassword.
  ///
  /// In en, this message translates to:
  /// **'Change Password'**
  String get changePassword;

  /// No description provided for @rememberMe.
  ///
  /// In en, this message translates to:
  /// **'Remember Me'**
  String get rememberMe;

  /// No description provided for @staySignedIn.
  ///
  /// In en, this message translates to:
  /// **'Stay Signed In'**
  String get staySignedIn;

  /// No description provided for @firstName.
  ///
  /// In en, this message translates to:
  /// **'First Name'**
  String get firstName;

  /// No description provided for @lastName.
  ///
  /// In en, this message translates to:
  /// **'Last Name'**
  String get lastName;

  /// No description provided for @fullName.
  ///
  /// In en, this message translates to:
  /// **'Full Name'**
  String get fullName;

  /// No description provided for @phoneNumber.
  ///
  /// In en, this message translates to:
  /// **'Phone Number'**
  String get phoneNumber;

  /// No description provided for @mobile.
  ///
  /// In en, this message translates to:
  /// **'Mobile'**
  String get mobile;

  /// No description provided for @username.
  ///
  /// In en, this message translates to:
  /// **'Username'**
  String get username;

  /// No description provided for @verificationCode.
  ///
  /// In en, this message translates to:
  /// **'Verification Code'**
  String get verificationCode;

  /// No description provided for @verify.
  ///
  /// In en, this message translates to:
  /// **'Verify'**
  String get verify;

  /// No description provided for @verification.
  ///
  /// In en, this message translates to:
  /// **'Verification'**
  String get verification;

  /// No description provided for @verified.
  ///
  /// In en, this message translates to:
  /// **'Verified'**
  String get verified;

  /// No description provided for @notVerified.
  ///
  /// In en, this message translates to:
  /// **'Not Verified'**
  String get notVerified;

  /// No description provided for @resendCode.
  ///
  /// In en, this message translates to:
  /// **'Resend Code'**
  String get resendCode;

  /// No description provided for @welcomeBack.
  ///
  /// In en, this message translates to:
  /// **'Welcome Back'**
  String get welcomeBack;

  /// No description provided for @welcome.
  ///
  /// In en, this message translates to:
  /// **'Welcome'**
  String get welcome;

  /// No description provided for @createAccount.
  ///
  /// In en, this message translates to:
  /// **'Create Account'**
  String get createAccount;

  /// No description provided for @alreadyHaveAccount.
  ///
  /// In en, this message translates to:
  /// **'Already have an account?'**
  String get alreadyHaveAccount;

  /// No description provided for @dontHaveAccount.
  ///
  /// In en, this message translates to:
  /// **'Don\'\'t have an account?'**
  String get dontHaveAccount;

  /// No description provided for @agreeToTerms.
  ///
  /// In en, this message translates to:
  /// **'I agree to the Terms and Conditions'**
  String get agreeToTerms;

  /// No description provided for @termsAndConditions.
  ///
  /// In en, this message translates to:
  /// **'Terms and Conditions'**
  String get termsAndConditions;

  /// No description provided for @privacyPolicy.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy;

  /// No description provided for @acceptTerms.
  ///
  /// In en, this message translates to:
  /// **'Accept Terms'**
  String get acceptTerms;

  /// No description provided for @field.
  ///
  /// In en, this message translates to:
  /// **'Field'**
  String get field;

  /// No description provided for @fieldName.
  ///
  /// In en, this message translates to:
  /// **'Field Name'**
  String get fieldName;

  /// No description provided for @fieldArea.
  ///
  /// In en, this message translates to:
  /// **'Field Area'**
  String get fieldArea;

  /// No description provided for @fieldLocation.
  ///
  /// In en, this message translates to:
  /// **'Field Location'**
  String get fieldLocation;

  /// No description provided for @fieldBoundary.
  ///
  /// In en, this message translates to:
  /// **'Field Boundary'**
  String get fieldBoundary;

  /// No description provided for @fieldStatus.
  ///
  /// In en, this message translates to:
  /// **'Field Status'**
  String get fieldStatus;

  /// No description provided for @fieldType.
  ///
  /// In en, this message translates to:
  /// **'Field Type'**
  String get fieldType;

  /// No description provided for @fieldOwner.
  ///
  /// In en, this message translates to:
  /// **'Field Owner'**
  String get fieldOwner;

  /// No description provided for @fieldManager.
  ///
  /// In en, this message translates to:
  /// **'Field Manager'**
  String get fieldManager;

  /// No description provided for @fieldNotes.
  ///
  /// In en, this message translates to:
  /// **'Field Notes'**
  String get fieldNotes;

  /// No description provided for @fieldDescription.
  ///
  /// In en, this message translates to:
  /// **'Field Description'**
  String get fieldDescription;

  /// No description provided for @fieldCreatedDate.
  ///
  /// In en, this message translates to:
  /// **'Field Created Date'**
  String get fieldCreatedDate;

  /// No description provided for @fieldLastModified.
  ///
  /// In en, this message translates to:
  /// **'Last Modified'**
  String get fieldLastModified;

  /// No description provided for @selectField.
  ///
  /// In en, this message translates to:
  /// **'Select Field'**
  String get selectField;

  /// No description provided for @noFieldsFound.
  ///
  /// In en, this message translates to:
  /// **'No Fields Found'**
  String get noFieldsFound;

  /// No description provided for @noFieldsAdded.
  ///
  /// In en, this message translates to:
  /// **'No Fields Added Yet'**
  String get noFieldsAdded;

  /// No description provided for @addFirstField.
  ///
  /// In en, this message translates to:
  /// **'Add Your First Field'**
  String get addFirstField;

  /// No description provided for @drawFieldBoundary.
  ///
  /// In en, this message translates to:
  /// **'Draw Field Boundary'**
  String get drawFieldBoundary;

  /// No description provided for @importFieldBoundary.
  ///
  /// In en, this message translates to:
  /// **'Import Field Boundary'**
  String get importFieldBoundary;

  /// No description provided for @editFieldBoundary.
  ///
  /// In en, this message translates to:
  /// **'Edit Field Boundary'**
  String get editFieldBoundary;

  /// No description provided for @fieldArea_hectares.
  ///
  /// In en, this message translates to:
  /// **'Area (Hectares)'**
  String get fieldArea_hectares;

  /// No description provided for @fieldArea_acres.
  ///
  /// In en, this message translates to:
  /// **'Area (Acres)'**
  String get fieldArea_acres;

  /// No description provided for @fieldArea_sqmeters.
  ///
  /// In en, this message translates to:
  /// **'Area (Square Meters)'**
  String get fieldArea_sqmeters;

  /// No description provided for @fieldPerimeter.
  ///
  /// In en, this message translates to:
  /// **'Field Perimeter'**
  String get fieldPerimeter;

  /// No description provided for @fieldCentroid.
  ///
  /// In en, this message translates to:
  /// **'Field Center'**
  String get fieldCentroid;

  /// No description provided for @fieldCoordinates.
  ///
  /// In en, this message translates to:
  /// **'Field Coordinates'**
  String get fieldCoordinates;

  /// No description provided for @latitude.
  ///
  /// In en, this message translates to:
  /// **'Latitude'**
  String get latitude;

  /// No description provided for @longitude.
  ///
  /// In en, this message translates to:
  /// **'Longitude'**
  String get longitude;

  /// No description provided for @altitude.
  ///
  /// In en, this message translates to:
  /// **'Altitude'**
  String get altitude;

  /// No description provided for @accuracy.
  ///
  /// In en, this message translates to:
  /// **'Accuracy'**
  String get accuracy;

  /// No description provided for @soil.
  ///
  /// In en, this message translates to:
  /// **'Soil'**
  String get soil;

  /// No description provided for @soilType.
  ///
  /// In en, this message translates to:
  /// **'Soil Type'**
  String get soilType;

  /// No description provided for @soilTexture.
  ///
  /// In en, this message translates to:
  /// **'Soil Texture'**
  String get soilTexture;

  /// No description provided for @soilMoisture.
  ///
  /// In en, this message translates to:
  /// **'Soil Moisture'**
  String get soilMoisture;

  /// No description provided for @soilTemperature.
  ///
  /// In en, this message translates to:
  /// **'Soil Temperature'**
  String get soilTemperature;

  /// No description provided for @soilPH.
  ///
  /// In en, this message translates to:
  /// **'Soil pH'**
  String get soilPH;

  /// No description provided for @soilNitrogen.
  ///
  /// In en, this message translates to:
  /// **'Soil Nitrogen'**
  String get soilNitrogen;

  /// No description provided for @soilPhosphorus.
  ///
  /// In en, this message translates to:
  /// **'Soil Phosphorus'**
  String get soilPhosphorus;

  /// No description provided for @soilPotassium.
  ///
  /// In en, this message translates to:
  /// **'Soil Potassium'**
  String get soilPotassium;

  /// No description provided for @soilOrganicMatter.
  ///
  /// In en, this message translates to:
  /// **'Soil Organic Matter'**
  String get soilOrganicMatter;

  /// No description provided for @soilHealth.
  ///
  /// In en, this message translates to:
  /// **'Soil Health'**
  String get soilHealth;

  /// No description provided for @soilAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Soil Analysis'**
  String get soilAnalysis;

  /// No description provided for @soilTest.
  ///
  /// In en, this message translates to:
  /// **'Soil Test'**
  String get soilTest;

  /// No description provided for @soilTestResults.
  ///
  /// In en, this message translates to:
  /// **'Soil Test Results'**
  String get soilTestResults;

  /// No description provided for @soilSampling.
  ///
  /// In en, this message translates to:
  /// **'Soil Sampling'**
  String get soilSampling;

  /// No description provided for @soilSample.
  ///
  /// In en, this message translates to:
  /// **'Soil Sample'**
  String get soilSample;

  /// No description provided for @soilData.
  ///
  /// In en, this message translates to:
  /// **'Soil Data'**
  String get soilData;

  /// No description provided for @soilConditions.
  ///
  /// In en, this message translates to:
  /// **'Soil Conditions'**
  String get soilConditions;

  /// No description provided for @soilQuality.
  ///
  /// In en, this message translates to:
  /// **'Soil Quality'**
  String get soilQuality;

  /// No description provided for @soilFertility.
  ///
  /// In en, this message translates to:
  /// **'Soil Fertility'**
  String get soilFertility;

  /// No description provided for @soilNutrients.
  ///
  /// In en, this message translates to:
  /// **'Soil Nutrients'**
  String get soilNutrients;

  /// No description provided for @soilComposition.
  ///
  /// In en, this message translates to:
  /// **'Soil Composition'**
  String get soilComposition;

  /// No description provided for @soilProfile.
  ///
  /// In en, this message translates to:
  /// **'Soil Profile'**
  String get soilProfile;

  /// No description provided for @crop.
  ///
  /// In en, this message translates to:
  /// **'Crop'**
  String get crop;

  /// No description provided for @cropName.
  ///
  /// In en, this message translates to:
  /// **'Crop Name'**
  String get cropName;

  /// No description provided for @cropType.
  ///
  /// In en, this message translates to:
  /// **'Crop Type'**
  String get cropType;

  /// No description provided for @cropVariety.
  ///
  /// In en, this message translates to:
  /// **'Crop Variety'**
  String get cropVariety;

  /// No description provided for @cropSeason.
  ///
  /// In en, this message translates to:
  /// **'Crop Season'**
  String get cropSeason;

  /// No description provided for @cropStage.
  ///
  /// In en, this message translates to:
  /// **'Crop Stage'**
  String get cropStage;

  /// No description provided for @cropGrowthStage.
  ///
  /// In en, this message translates to:
  /// **'Crop Growth Stage'**
  String get cropGrowthStage;

  /// No description provided for @plantingDate.
  ///
  /// In en, this message translates to:
  /// **'Planting Date'**
  String get plantingDate;

  /// No description provided for @harvestDate.
  ///
  /// In en, this message translates to:
  /// **'Harvest Date'**
  String get harvestDate;

  /// No description provided for @expectedYield.
  ///
  /// In en, this message translates to:
  /// **'Expected Yield'**
  String get expectedYield;

  /// No description provided for @actualYield.
  ///
  /// In en, this message translates to:
  /// **'Actual Yield'**
  String get actualYield;

  /// No description provided for @yieldPerHectare.
  ///
  /// In en, this message translates to:
  /// **'Yield Per Hectare'**
  String get yieldPerHectare;

  /// No description provided for @yieldPerAcre.
  ///
  /// In en, this message translates to:
  /// **'Yield Per Acre'**
  String get yieldPerAcre;

  /// No description provided for @seedRate.
  ///
  /// In en, this message translates to:
  /// **'Seed Rate'**
  String get seedRate;

  /// No description provided for @plantDensity.
  ///
  /// In en, this message translates to:
  /// **'Plant Density'**
  String get plantDensity;

  /// No description provided for @rowSpacing.
  ///
  /// In en, this message translates to:
  /// **'Row Spacing'**
  String get rowSpacing;

  /// No description provided for @plantSpacing.
  ///
  /// In en, this message translates to:
  /// **'Plant Spacing'**
  String get plantSpacing;

  /// No description provided for @irrigationMethod.
  ///
  /// In en, this message translates to:
  /// **'Irrigation Method'**
  String get irrigationMethod;

  /// No description provided for @cropRotation.
  ///
  /// In en, this message translates to:
  /// **'Crop Rotation'**
  String get cropRotation;

  /// No description provided for @cropHistory.
  ///
  /// In en, this message translates to:
  /// **'Crop History'**
  String get cropHistory;

  /// No description provided for @cropCalendar.
  ///
  /// In en, this message translates to:
  /// **'Crop Calendar'**
  String get cropCalendar;

  /// No description provided for @cropPlanning.
  ///
  /// In en, this message translates to:
  /// **'Crop Planning'**
  String get cropPlanning;

  /// No description provided for @cropManagement.
  ///
  /// In en, this message translates to:
  /// **'Crop Management'**
  String get cropManagement;

  /// No description provided for @cropMonitoring.
  ///
  /// In en, this message translates to:
  /// **'Crop Monitoring'**
  String get cropMonitoring;

  /// No description provided for @cropProtection.
  ///
  /// In en, this message translates to:
  /// **'Crop Protection'**
  String get cropProtection;

  /// No description provided for @cropNutrition.
  ///
  /// In en, this message translates to:
  /// **'Crop Nutrition'**
  String get cropNutrition;

  /// No description provided for @cropDisease.
  ///
  /// In en, this message translates to:
  /// **'Crop Disease'**
  String get cropDisease;

  /// No description provided for @cropPest.
  ///
  /// In en, this message translates to:
  /// **'Crop Pest'**
  String get cropPest;

  /// No description provided for @cropWeed.
  ///
  /// In en, this message translates to:
  /// **'Crop Weed'**
  String get cropWeed;

  /// No description provided for @cropStress.
  ///
  /// In en, this message translates to:
  /// **'Crop Stress'**
  String get cropStress;

  /// No description provided for @cropPerformance.
  ///
  /// In en, this message translates to:
  /// **'Crop Performance'**
  String get cropPerformance;

  /// No description provided for @cropComparison.
  ///
  /// In en, this message translates to:
  /// **'Crop Comparison'**
  String get cropComparison;

  /// No description provided for @wheat.
  ///
  /// In en, this message translates to:
  /// **'Wheat'**
  String get wheat;

  /// No description provided for @barley.
  ///
  /// In en, this message translates to:
  /// **'Barley'**
  String get barley;

  /// No description provided for @sorghum.
  ///
  /// In en, this message translates to:
  /// **'Sorghum'**
  String get sorghum;

  /// No description provided for @millet.
  ///
  /// In en, this message translates to:
  /// **'Millet'**
  String get millet;

  /// No description provided for @maize.
  ///
  /// In en, this message translates to:
  /// **'Maize'**
  String get maize;

  /// No description provided for @rice.
  ///
  /// In en, this message translates to:
  /// **'Rice'**
  String get rice;

  /// No description provided for @qat.
  ///
  /// In en, this message translates to:
  /// **'Qat'**
  String get qat;

  /// No description provided for @coffee.
  ///
  /// In en, this message translates to:
  /// **'Coffee'**
  String get coffee;

  /// No description provided for @cotton.
  ///
  /// In en, this message translates to:
  /// **'Cotton'**
  String get cotton;

  /// No description provided for @sesame.
  ///
  /// In en, this message translates to:
  /// **'Sesame'**
  String get sesame;

  /// No description provided for @tomato.
  ///
  /// In en, this message translates to:
  /// **'Tomato'**
  String get tomato;

  /// No description provided for @potato.
  ///
  /// In en, this message translates to:
  /// **'Potato'**
  String get potato;

  /// No description provided for @onion.
  ///
  /// In en, this message translates to:
  /// **'Onion'**
  String get onion;

  /// No description provided for @cucumber.
  ///
  /// In en, this message translates to:
  /// **'Cucumber'**
  String get cucumber;

  /// No description provided for @watermelon.
  ///
  /// In en, this message translates to:
  /// **'Watermelon'**
  String get watermelon;

  /// No description provided for @melon.
  ///
  /// In en, this message translates to:
  /// **'Melon'**
  String get melon;

  /// No description provided for @mango.
  ///
  /// In en, this message translates to:
  /// **'Mango'**
  String get mango;

  /// No description provided for @banana.
  ///
  /// In en, this message translates to:
  /// **'Banana'**
  String get banana;

  /// No description provided for @papaya.
  ///
  /// In en, this message translates to:
  /// **'Papaya'**
  String get papaya;

  /// No description provided for @grape.
  ///
  /// In en, this message translates to:
  /// **'Grape'**
  String get grape;

  /// No description provided for @pomegranate.
  ///
  /// In en, this message translates to:
  /// **'Pomegranate'**
  String get pomegranate;

  /// No description provided for @citrus.
  ///
  /// In en, this message translates to:
  /// **'Citrus'**
  String get citrus;

  /// No description provided for @orange.
  ///
  /// In en, this message translates to:
  /// **'Orange'**
  String get orange;

  /// No description provided for @lemon.
  ///
  /// In en, this message translates to:
  /// **'Lemon'**
  String get lemon;

  /// No description provided for @alfalfa.
  ///
  /// In en, this message translates to:
  /// **'Alfalfa'**
  String get alfalfa;

  /// No description provided for @clover.
  ///
  /// In en, this message translates to:
  /// **'Clover'**
  String get clover;

  /// No description provided for @peanut.
  ///
  /// In en, this message translates to:
  /// **'Peanut'**
  String get peanut;

  /// No description provided for @chickpea.
  ///
  /// In en, this message translates to:
  /// **'Chickpea'**
  String get chickpea;

  /// No description provided for @lentil.
  ///
  /// In en, this message translates to:
  /// **'Lentil'**
  String get lentil;

  /// No description provided for @bean.
  ///
  /// In en, this message translates to:
  /// **'Bean'**
  String get bean;

  /// No description provided for @pea.
  ///
  /// In en, this message translates to:
  /// **'Pea'**
  String get pea;

  /// No description provided for @currentWeather.
  ///
  /// In en, this message translates to:
  /// **'Current Weather'**
  String get currentWeather;

  /// No description provided for @weatherConditions.
  ///
  /// In en, this message translates to:
  /// **'Weather Conditions'**
  String get weatherConditions;

  /// No description provided for @weatherData.
  ///
  /// In en, this message translates to:
  /// **'Weather Data'**
  String get weatherData;

  /// No description provided for @weatherStation.
  ///
  /// In en, this message translates to:
  /// **'Weather Station'**
  String get weatherStation;

  /// No description provided for @temperature.
  ///
  /// In en, this message translates to:
  /// **'Temperature'**
  String get temperature;

  /// No description provided for @minTemperature.
  ///
  /// In en, this message translates to:
  /// **'Min Temperature'**
  String get minTemperature;

  /// No description provided for @maxTemperature.
  ///
  /// In en, this message translates to:
  /// **'Max Temperature'**
  String get maxTemperature;

  /// No description provided for @feelsLike.
  ///
  /// In en, this message translates to:
  /// **'Feels Like'**
  String get feelsLike;

  /// No description provided for @humidity.
  ///
  /// In en, this message translates to:
  /// **'Humidity'**
  String get humidity;

  /// No description provided for @relativeHumidity.
  ///
  /// In en, this message translates to:
  /// **'Relative Humidity'**
  String get relativeHumidity;

  /// No description provided for @precipitation.
  ///
  /// In en, this message translates to:
  /// **'Precipitation'**
  String get precipitation;

  /// No description provided for @rainfall.
  ///
  /// In en, this message translates to:
  /// **'Rainfall'**
  String get rainfall;

  /// No description provided for @rain.
  ///
  /// In en, this message translates to:
  /// **'Rain'**
  String get rain;

  /// No description provided for @rainfallAmount.
  ///
  /// In en, this message translates to:
  /// **'Rainfall Amount'**
  String get rainfallAmount;

  /// No description provided for @rainChance.
  ///
  /// In en, this message translates to:
  /// **'Rain Chance'**
  String get rainChance;

  /// No description provided for @snowfall.
  ///
  /// In en, this message translates to:
  /// **'Snowfall'**
  String get snowfall;

  /// No description provided for @hail.
  ///
  /// In en, this message translates to:
  /// **'Hail'**
  String get hail;

  /// No description provided for @wind.
  ///
  /// In en, this message translates to:
  /// **'Wind'**
  String get wind;

  /// No description provided for @windSpeed.
  ///
  /// In en, this message translates to:
  /// **'Wind Speed'**
  String get windSpeed;

  /// No description provided for @windDirection.
  ///
  /// In en, this message translates to:
  /// **'Wind Direction'**
  String get windDirection;

  /// No description provided for @windGust.
  ///
  /// In en, this message translates to:
  /// **'Wind Gust'**
  String get windGust;

  /// No description provided for @pressure.
  ///
  /// In en, this message translates to:
  /// **'Pressure'**
  String get pressure;

  /// No description provided for @atmosphericPressure.
  ///
  /// In en, this message translates to:
  /// **'Atmospheric Pressure'**
  String get atmosphericPressure;

  /// No description provided for @visibility.
  ///
  /// In en, this message translates to:
  /// **'Visibility'**
  String get visibility;

  /// No description provided for @cloudCover.
  ///
  /// In en, this message translates to:
  /// **'Cloud Cover'**
  String get cloudCover;

  /// No description provided for @cloudiness.
  ///
  /// In en, this message translates to:
  /// **'Cloudiness'**
  String get cloudiness;

  /// No description provided for @dewPoint.
  ///
  /// In en, this message translates to:
  /// **'Dew Point'**
  String get dewPoint;

  /// No description provided for @uvIndex.
  ///
  /// In en, this message translates to:
  /// **'UV Index'**
  String get uvIndex;

  /// No description provided for @sunrise.
  ///
  /// In en, this message translates to:
  /// **'Sunrise'**
  String get sunrise;

  /// No description provided for @sunset.
  ///
  /// In en, this message translates to:
  /// **'Sunset'**
  String get sunset;

  /// No description provided for @moonPhase.
  ///
  /// In en, this message translates to:
  /// **'Moon Phase'**
  String get moonPhase;

  /// No description provided for @weatherAlert.
  ///
  /// In en, this message translates to:
  /// **'Weather Alert'**
  String get weatherAlert;

  /// No description provided for @severeWeather.
  ///
  /// In en, this message translates to:
  /// **'Severe Weather'**
  String get severeWeather;

  /// No description provided for @weatherWarning.
  ///
  /// In en, this message translates to:
  /// **'Weather Warning'**
  String get weatherWarning;

  /// No description provided for @weatherWatch.
  ///
  /// In en, this message translates to:
  /// **'Weather Watch'**
  String get weatherWatch;

  /// No description provided for @storm.
  ///
  /// In en, this message translates to:
  /// **'Storm'**
  String get storm;

  /// No description provided for @thunderstorm.
  ///
  /// In en, this message translates to:
  /// **'Thunderstorm'**
  String get thunderstorm;

  /// No description provided for @lightning.
  ///
  /// In en, this message translates to:
  /// **'Lightning'**
  String get lightning;

  /// No description provided for @thunder.
  ///
  /// In en, this message translates to:
  /// **'Thunder'**
  String get thunder;

  /// No description provided for @fog.
  ///
  /// In en, this message translates to:
  /// **'Fog'**
  String get fog;

  /// No description provided for @mist.
  ///
  /// In en, this message translates to:
  /// **'Mist'**
  String get mist;

  /// No description provided for @haze.
  ///
  /// In en, this message translates to:
  /// **'Haze'**
  String get haze;

  /// No description provided for @dust.
  ///
  /// In en, this message translates to:
  /// **'Dust'**
  String get dust;

  /// No description provided for @sandstorm.
  ///
  /// In en, this message translates to:
  /// **'Sandstorm'**
  String get sandstorm;

  /// No description provided for @partlyCloudy.
  ///
  /// In en, this message translates to:
  /// **'Partly Cloudy'**
  String get partlyCloudy;

  /// No description provided for @cloudy.
  ///
  /// In en, this message translates to:
  /// **'Cloudy'**
  String get cloudy;

  /// No description provided for @overcast.
  ///
  /// In en, this message translates to:
  /// **'Overcast'**
  String get overcast;

  /// No description provided for @drizzle.
  ///
  /// In en, this message translates to:
  /// **'Drizzle'**
  String get drizzle;

  /// No description provided for @lightRain.
  ///
  /// In en, this message translates to:
  /// **'Light Rain'**
  String get lightRain;

  /// No description provided for @moderateRain.
  ///
  /// In en, this message translates to:
  /// **'Moderate Rain'**
  String get moderateRain;

  /// No description provided for @heavyRain.
  ///
  /// In en, this message translates to:
  /// **'Heavy Rain'**
  String get heavyRain;

  /// No description provided for @showers.
  ///
  /// In en, this message translates to:
  /// **'Showers'**
  String get showers;

  /// No description provided for @sunny.
  ///
  /// In en, this message translates to:
  /// **'Sunny'**
  String get sunny;

  /// No description provided for @hot.
  ///
  /// In en, this message translates to:
  /// **'Hot'**
  String get hot;

  /// No description provided for @warm.
  ///
  /// In en, this message translates to:
  /// **'Warm'**
  String get warm;

  /// No description provided for @cool.
  ///
  /// In en, this message translates to:
  /// **'Cool'**
  String get cool;

  /// No description provided for @cold.
  ///
  /// In en, this message translates to:
  /// **'Cold'**
  String get cold;

  /// No description provided for @freezing.
  ///
  /// In en, this message translates to:
  /// **'Freezing'**
  String get freezing;

  /// No description provided for @dry.
  ///
  /// In en, this message translates to:
  /// **'Dry'**
  String get dry;

  /// No description provided for @wet.
  ///
  /// In en, this message translates to:
  /// **'Wet'**
  String get wet;

  /// No description provided for @windy.
  ///
  /// In en, this message translates to:
  /// **'Windy'**
  String get windy;

  /// No description provided for @calm.
  ///
  /// In en, this message translates to:
  /// **'Calm'**
  String get calm;

  /// No description provided for @weatherForecast_hourly.
  ///
  /// In en, this message translates to:
  /// **'Hourly Forecast'**
  String get weatherForecast_hourly;

  /// No description provided for @weatherForecast_daily.
  ///
  /// In en, this message translates to:
  /// **'Daily Forecast'**
  String get weatherForecast_daily;

  /// No description provided for @weatherForecast_weekly.
  ///
  /// In en, this message translates to:
  /// **'Weekly Forecast'**
  String get weatherForecast_weekly;

  /// No description provided for @forecast_3days.
  ///
  /// In en, this message translates to:
  /// **'3-Day Forecast'**
  String get forecast_3days;

  /// No description provided for @forecast_7days.
  ///
  /// In en, this message translates to:
  /// **'7-Day Forecast'**
  String get forecast_7days;

  /// No description provided for @forecast_14days.
  ///
  /// In en, this message translates to:
  /// **'14-Day Forecast'**
  String get forecast_14days;

  /// No description provided for @historicalWeather.
  ///
  /// In en, this message translates to:
  /// **'Historical Weather'**
  String get historicalWeather;

  /// No description provided for @weatherHistory.
  ///
  /// In en, this message translates to:
  /// **'Weather History'**
  String get weatherHistory;

  /// No description provided for @weatherTrends.
  ///
  /// In en, this message translates to:
  /// **'Weather Trends'**
  String get weatherTrends;

  /// No description provided for @weatherComparison.
  ///
  /// In en, this message translates to:
  /// **'Weather Comparison'**
  String get weatherComparison;

  /// No description provided for @satelliteImage.
  ///
  /// In en, this message translates to:
  /// **'Satellite Image'**
  String get satelliteImage;

  /// No description provided for @satelliteData.
  ///
  /// In en, this message translates to:
  /// **'Satellite Data'**
  String get satelliteData;

  /// No description provided for @satelliteProvider.
  ///
  /// In en, this message translates to:
  /// **'Satellite Provider'**
  String get satelliteProvider;

  /// No description provided for @imageDate.
  ///
  /// In en, this message translates to:
  /// **'Image Date'**
  String get imageDate;

  /// No description provided for @imageResolution.
  ///
  /// In en, this message translates to:
  /// **'Image Resolution'**
  String get imageResolution;

  /// No description provided for @imageQuality.
  ///
  /// In en, this message translates to:
  /// **'Image Quality'**
  String get imageQuality;

  /// No description provided for @cloudCoverage.
  ///
  /// In en, this message translates to:
  /// **'Cloud Coverage'**
  String get cloudCoverage;

  /// No description provided for @cloudFree.
  ///
  /// In en, this message translates to:
  /// **'Cloud Free'**
  String get cloudFree;

  /// No description provided for @viewImage.
  ///
  /// In en, this message translates to:
  /// **'View Image'**
  String get viewImage;

  /// No description provided for @downloadImage.
  ///
  /// In en, this message translates to:
  /// **'Download Image'**
  String get downloadImage;

  /// No description provided for @compareImages.
  ///
  /// In en, this message translates to:
  /// **'Compare Images'**
  String get compareImages;

  /// No description provided for @imageGallery.
  ///
  /// In en, this message translates to:
  /// **'Image Gallery'**
  String get imageGallery;

  /// No description provided for @imageLibrary.
  ///
  /// In en, this message translates to:
  /// **'Image Library'**
  String get imageLibrary;

  /// No description provided for @recentImages.
  ///
  /// In en, this message translates to:
  /// **'Recent Images'**
  String get recentImages;

  /// No description provided for @historicalImages.
  ///
  /// In en, this message translates to:
  /// **'Historical Images'**
  String get historicalImages;

  /// No description provided for @ndviValue.
  ///
  /// In en, this message translates to:
  /// **'NDVI Value'**
  String get ndviValue;

  /// No description provided for @ndviRange.
  ///
  /// In en, this message translates to:
  /// **'NDVI Range'**
  String get ndviRange;

  /// No description provided for @ndviScore.
  ///
  /// In en, this message translates to:
  /// **'NDVI Score'**
  String get ndviScore;

  /// No description provided for @ndviIndex.
  ///
  /// In en, this message translates to:
  /// **'NDVI Index'**
  String get ndviIndex;

  /// No description provided for @vegetationHealth.
  ///
  /// In en, this message translates to:
  /// **'Vegetation Health'**
  String get vegetationHealth;

  /// No description provided for @vegetationDensity.
  ///
  /// In en, this message translates to:
  /// **'Vegetation Density'**
  String get vegetationDensity;

  /// No description provided for @vegetationCover.
  ///
  /// In en, this message translates to:
  /// **'Vegetation Cover'**
  String get vegetationCover;

  /// No description provided for @vegetationIndex.
  ///
  /// In en, this message translates to:
  /// **'Vegetation Index'**
  String get vegetationIndex;

  /// No description provided for @plantHealth.
  ///
  /// In en, this message translates to:
  /// **'Plant Health'**
  String get plantHealth;

  /// No description provided for @plantVigor.
  ///
  /// In en, this message translates to:
  /// **'Plant Vigor'**
  String get plantVigor;

  /// No description provided for @plantStress.
  ///
  /// In en, this message translates to:
  /// **'Plant Stress'**
  String get plantStress;

  /// No description provided for @biomass.
  ///
  /// In en, this message translates to:
  /// **'Biomass'**
  String get biomass;

  /// No description provided for @greenness.
  ///
  /// In en, this message translates to:
  /// **'Greenness'**
  String get greenness;

  /// No description provided for @chlorophyll.
  ///
  /// In en, this message translates to:
  /// **'Chlorophyll'**
  String get chlorophyll;

  /// No description provided for @photosynthesis.
  ///
  /// In en, this message translates to:
  /// **'Photosynthesis'**
  String get photosynthesis;

  /// No description provided for @ndviLow.
  ///
  /// In en, this message translates to:
  /// **'Low NDVI'**
  String get ndviLow;

  /// No description provided for @ndviMedium.
  ///
  /// In en, this message translates to:
  /// **'Medium NDVI'**
  String get ndviMedium;

  /// No description provided for @ndviHigh.
  ///
  /// In en, this message translates to:
  /// **'High NDVI'**
  String get ndviHigh;

  /// No description provided for @healthyVegetation.
  ///
  /// In en, this message translates to:
  /// **'Healthy Vegetation'**
  String get healthyVegetation;

  /// No description provided for @stressedVegetation.
  ///
  /// In en, this message translates to:
  /// **'Stressed Vegetation'**
  String get stressedVegetation;

  /// No description provided for @bareGround.
  ///
  /// In en, this message translates to:
  /// **'Bare Ground'**
  String get bareGround;

  /// No description provided for @waterBody.
  ///
  /// In en, this message translates to:
  /// **'Water Body'**
  String get waterBody;

  /// No description provided for @ndviTimeSeries.
  ///
  /// In en, this message translates to:
  /// **'NDVI Time Series'**
  String get ndviTimeSeries;

  /// No description provided for @ndviTrend.
  ///
  /// In en, this message translates to:
  /// **'NDVI Trend'**
  String get ndviTrend;

  /// No description provided for @ndviChange.
  ///
  /// In en, this message translates to:
  /// **'NDVI Change'**
  String get ndviChange;

  /// No description provided for @ndviAnomaly.
  ///
  /// In en, this message translates to:
  /// **'NDVI Anomaly'**
  String get ndviAnomaly;

  /// No description provided for @ndviComparison.
  ///
  /// In en, this message translates to:
  /// **'NDVI Comparison'**
  String get ndviComparison;

  /// No description provided for @multispectral.
  ///
  /// In en, this message translates to:
  /// **'Multispectral'**
  String get multispectral;

  /// No description provided for @trueColor.
  ///
  /// In en, this message translates to:
  /// **'True Color'**
  String get trueColor;

  /// No description provided for @falseColor.
  ///
  /// In en, this message translates to:
  /// **'False Color'**
  String get falseColor;

  /// No description provided for @infrared.
  ///
  /// In en, this message translates to:
  /// **'Infrared'**
  String get infrared;

  /// No description provided for @nearInfrared.
  ///
  /// In en, this message translates to:
  /// **'Near Infrared'**
  String get nearInfrared;

  /// No description provided for @redBand.
  ///
  /// In en, this message translates to:
  /// **'Red Band'**
  String get redBand;

  /// No description provided for @greenBand.
  ///
  /// In en, this message translates to:
  /// **'Green Band'**
  String get greenBand;

  /// No description provided for @blueBand.
  ///
  /// In en, this message translates to:
  /// **'Blue Band'**
  String get blueBand;

  /// No description provided for @nirBand.
  ///
  /// In en, this message translates to:
  /// **'NIR Band'**
  String get nirBand;

  /// No description provided for @variableRateApplication.
  ///
  /// In en, this message translates to:
  /// **'Variable Rate Application'**
  String get variableRateApplication;

  /// No description provided for @vraTitle.
  ///
  /// In en, this message translates to:
  /// **'Variable Rate Application Maps'**
  String get vraTitle;

  /// No description provided for @prescriptionMap.
  ///
  /// In en, this message translates to:
  /// **'Prescription Map'**
  String get prescriptionMap;

  /// No description provided for @applicationMap.
  ///
  /// In en, this message translates to:
  /// **'Application Map'**
  String get applicationMap;

  /// No description provided for @managementZones.
  ///
  /// In en, this message translates to:
  /// **'Management Zones'**
  String get managementZones;

  /// No description provided for @zone.
  ///
  /// In en, this message translates to:
  /// **'Zone'**
  String get zone;

  /// No description provided for @zones.
  ///
  /// In en, this message translates to:
  /// **'Zones'**
  String get zones;

  /// No description provided for @zoneNumber.
  ///
  /// In en, this message translates to:
  /// **'Zone Number'**
  String get zoneNumber;

  /// No description provided for @zoneName.
  ///
  /// In en, this message translates to:
  /// **'Zone Name'**
  String get zoneName;

  /// No description provided for @zoneArea.
  ///
  /// In en, this message translates to:
  /// **'Zone Area'**
  String get zoneArea;

  /// No description provided for @zoneType.
  ///
  /// In en, this message translates to:
  /// **'Zone Type'**
  String get zoneType;

  /// No description provided for @highProductivity.
  ///
  /// In en, this message translates to:
  /// **'High Productivity'**
  String get highProductivity;

  /// No description provided for @mediumProductivity.
  ///
  /// In en, this message translates to:
  /// **'Medium Productivity'**
  String get mediumProductivity;

  /// No description provided for @lowProductivity.
  ///
  /// In en, this message translates to:
  /// **'Low Productivity'**
  String get lowProductivity;

  /// No description provided for @applicationRate.
  ///
  /// In en, this message translates to:
  /// **'Application Rate'**
  String get applicationRate;

  /// No description provided for @recommendedRate.
  ///
  /// In en, this message translates to:
  /// **'Recommended Rate'**
  String get recommendedRate;

  /// No description provided for @minimumRate.
  ///
  /// In en, this message translates to:
  /// **'Minimum Rate'**
  String get minimumRate;

  /// No description provided for @maximumRate.
  ///
  /// In en, this message translates to:
  /// **'Maximum Rate'**
  String get maximumRate;

  /// No description provided for @variableRate.
  ///
  /// In en, this message translates to:
  /// **'Variable Rate'**
  String get variableRate;

  /// No description provided for @uniformRate.
  ///
  /// In en, this message translates to:
  /// **'Uniform Rate'**
  String get uniformRate;

  /// No description provided for @rateAdjustment.
  ///
  /// In en, this message translates to:
  /// **'Rate Adjustment'**
  String get rateAdjustment;

  /// No description provided for @seedingRate.
  ///
  /// In en, this message translates to:
  /// **'Seeding Rate'**
  String get seedingRate;

  /// No description provided for @fertilizerRate.
  ///
  /// In en, this message translates to:
  /// **'Fertilizer Rate'**
  String get fertilizerRate;

  /// No description provided for @nitrogenRate.
  ///
  /// In en, this message translates to:
  /// **'Nitrogen Rate'**
  String get nitrogenRate;

  /// No description provided for @phosphorusRate.
  ///
  /// In en, this message translates to:
  /// **'Phosphorus Rate'**
  String get phosphorusRate;

  /// No description provided for @potassiumRate.
  ///
  /// In en, this message translates to:
  /// **'Potassium Rate'**
  String get potassiumRate;

  /// No description provided for @pesticideRate.
  ///
  /// In en, this message translates to:
  /// **'Pesticide Rate'**
  String get pesticideRate;

  /// No description provided for @herbicideRate.
  ///
  /// In en, this message translates to:
  /// **'Herbicide Rate'**
  String get herbicideRate;

  /// No description provided for @fungicideRate.
  ///
  /// In en, this message translates to:
  /// **'Fungicide Rate'**
  String get fungicideRate;

  /// No description provided for @insecticideRate.
  ///
  /// In en, this message translates to:
  /// **'Insecticide Rate'**
  String get insecticideRate;

  /// No description provided for @irrigationRate.
  ///
  /// In en, this message translates to:
  /// **'Irrigation Rate'**
  String get irrigationRate;

  /// No description provided for @waterApplication.
  ///
  /// In en, this message translates to:
  /// **'Water Application'**
  String get waterApplication;

  /// No description provided for @inputOptimization.
  ///
  /// In en, this message translates to:
  /// **'Input Optimization'**
  String get inputOptimization;

  /// No description provided for @precisionAgriculture.
  ///
  /// In en, this message translates to:
  /// **'Precision Agriculture'**
  String get precisionAgriculture;

  /// No description provided for @siteSpecific.
  ///
  /// In en, this message translates to:
  /// **'Site Specific'**
  String get siteSpecific;

  /// No description provided for @spatialVariability.
  ///
  /// In en, this message translates to:
  /// **'Spatial Variability'**
  String get spatialVariability;

  /// No description provided for @yieldMapping.
  ///
  /// In en, this message translates to:
  /// **'Yield Mapping'**
  String get yieldMapping;

  /// No description provided for @yieldData.
  ///
  /// In en, this message translates to:
  /// **'Yield Data'**
  String get yieldData;

  /// No description provided for @yieldVariability.
  ///
  /// In en, this message translates to:
  /// **'Yield Variability'**
  String get yieldVariability;

  /// No description provided for @soilVariability.
  ///
  /// In en, this message translates to:
  /// **'Soil Variability'**
  String get soilVariability;

  /// No description provided for @topography.
  ///
  /// In en, this message translates to:
  /// **'Topography'**
  String get topography;

  /// No description provided for @slope.
  ///
  /// In en, this message translates to:
  /// **'Slope'**
  String get slope;

  /// No description provided for @elevation.
  ///
  /// In en, this message translates to:
  /// **'Elevation'**
  String get elevation;

  /// No description provided for @drainage.
  ///
  /// In en, this message translates to:
  /// **'Drainage'**
  String get drainage;

  /// No description provided for @vraImplementation.
  ///
  /// In en, this message translates to:
  /// **'VRA Implementation'**
  String get vraImplementation;

  /// No description provided for @vraEquipment.
  ///
  /// In en, this message translates to:
  /// **'VRA Equipment'**
  String get vraEquipment;

  /// No description provided for @vraController.
  ///
  /// In en, this message translates to:
  /// **'VRA Controller'**
  String get vraController;

  /// No description provided for @vraCompatibility.
  ///
  /// In en, this message translates to:
  /// **'VRA Compatibility'**
  String get vraCompatibility;

  /// No description provided for @vraExport.
  ///
  /// In en, this message translates to:
  /// **'VRA Export'**
  String get vraExport;

  /// No description provided for @vraFormat.
  ///
  /// In en, this message translates to:
  /// **'VRA Format'**
  String get vraFormat;

  /// No description provided for @shapefileExport.
  ///
  /// In en, this message translates to:
  /// **'Shapefile Export'**
  String get shapefileExport;

  /// No description provided for @isobusFormat.
  ///
  /// In en, this message translates to:
  /// **'ISOBUS Format'**
  String get isobusFormat;

  /// No description provided for @vraSummary.
  ///
  /// In en, this message translates to:
  /// **'VRA Summary'**
  String get vraSummary;

  /// No description provided for @vraStatistics.
  ///
  /// In en, this message translates to:
  /// **'VRA Statistics'**
  String get vraStatistics;

  /// No description provided for @totalApplication.
  ///
  /// In en, this message translates to:
  /// **'Total Application'**
  String get totalApplication;

  /// No description provided for @averageRate.
  ///
  /// In en, this message translates to:
  /// **'Average Rate'**
  String get averageRate;

  /// No description provided for @standardDeviation.
  ///
  /// In en, this message translates to:
  /// **'Standard Deviation'**
  String get standardDeviation;

  /// No description provided for @coefficient_of_variation.
  ///
  /// In en, this message translates to:
  /// **'Coefficient of Variation'**
  String get coefficient_of_variation;

  /// No description provided for @growingDegreeDays.
  ///
  /// In en, this message translates to:
  /// **'Growing Degree Days'**
  String get growingDegreeDays;

  /// No description provided for @gddTitle.
  ///
  /// In en, this message translates to:
  /// **'GDD Calculator'**
  String get gddTitle;

  /// No description provided for @gddAccumulated.
  ///
  /// In en, this message translates to:
  /// **'Accumulated GDD'**
  String get gddAccumulated;

  /// No description provided for @gddDaily.
  ///
  /// In en, this message translates to:
  /// **'Daily GDD'**
  String get gddDaily;

  /// No description provided for @gddTotal.
  ///
  /// In en, this message translates to:
  /// **'Total GDD'**
  String get gddTotal;

  /// No description provided for @gddRequired.
  ///
  /// In en, this message translates to:
  /// **'Required GDD'**
  String get gddRequired;

  /// No description provided for @gddRemaining.
  ///
  /// In en, this message translates to:
  /// **'Remaining GDD'**
  String get gddRemaining;

  /// No description provided for @gddProgress.
  ///
  /// In en, this message translates to:
  /// **'GDD Progress'**
  String get gddProgress;

  /// No description provided for @baseTemperature.
  ///
  /// In en, this message translates to:
  /// **'Base Temperature'**
  String get baseTemperature;

  /// No description provided for @upperThreshold.
  ///
  /// In en, this message translates to:
  /// **'Upper Threshold'**
  String get upperThreshold;

  /// No description provided for @lowerThreshold.
  ///
  /// In en, this message translates to:
  /// **'Lower Threshold'**
  String get lowerThreshold;

  /// No description provided for @dailyMax.
  ///
  /// In en, this message translates to:
  /// **'Daily Max'**
  String get dailyMax;

  /// No description provided for @dailyMin.
  ///
  /// In en, this message translates to:
  /// **'Daily Min'**
  String get dailyMin;

  /// No description provided for @dailyAverage.
  ///
  /// In en, this message translates to:
  /// **'Daily Average'**
  String get dailyAverage;

  /// No description provided for @gddCalculation.
  ///
  /// In en, this message translates to:
  /// **'GDD Calculation'**
  String get gddCalculation;

  /// No description provided for @gddMethod.
  ///
  /// In en, this message translates to:
  /// **'GDD Method'**
  String get gddMethod;

  /// No description provided for @standardMethod.
  ///
  /// In en, this message translates to:
  /// **'Standard Method'**
  String get standardMethod;

  /// No description provided for @modifiedMethod.
  ///
  /// In en, this message translates to:
  /// **'Modified Method'**
  String get modifiedMethod;

  /// No description provided for @sineCurve.
  ///
  /// In en, this message translates to:
  /// **'Sine Curve'**
  String get sineCurve;

  /// No description provided for @growthStages.
  ///
  /// In en, this message translates to:
  /// **'Growth Stages'**
  String get growthStages;

  /// No description provided for @currentStage.
  ///
  /// In en, this message translates to:
  /// **'Current Stage'**
  String get currentStage;

  /// No description provided for @nextStage.
  ///
  /// In en, this message translates to:
  /// **'Next Stage'**
  String get nextStage;

  /// No description provided for @stageProgress.
  ///
  /// In en, this message translates to:
  /// **'Stage Progress'**
  String get stageProgress;

  /// No description provided for @stageName.
  ///
  /// In en, this message translates to:
  /// **'Stage Name'**
  String get stageName;

  /// No description provided for @stageDescription.
  ///
  /// In en, this message translates to:
  /// **'Stage Description'**
  String get stageDescription;

  /// No description provided for @stageDuration.
  ///
  /// In en, this message translates to:
  /// **'Stage Duration'**
  String get stageDuration;

  /// No description provided for @gddToNextStage.
  ///
  /// In en, this message translates to:
  /// **'GDD to Next Stage'**
  String get gddToNextStage;

  /// No description provided for @daysToNextStage.
  ///
  /// In en, this message translates to:
  /// **'Days to Next Stage'**
  String get daysToNextStage;

  /// No description provided for @emergence.
  ///
  /// In en, this message translates to:
  /// **'Emergence'**
  String get emergence;

  /// No description provided for @vegetative.
  ///
  /// In en, this message translates to:
  /// **'Vegetative'**
  String get vegetative;

  /// No description provided for @flowering.
  ///
  /// In en, this message translates to:
  /// **'Flowering'**
  String get flowering;

  /// No description provided for @pollination.
  ///
  /// In en, this message translates to:
  /// **'Pollination'**
  String get pollination;

  /// No description provided for @fruitDevelopment.
  ///
  /// In en, this message translates to:
  /// **'Fruit Development'**
  String get fruitDevelopment;

  /// No description provided for @maturity.
  ///
  /// In en, this message translates to:
  /// **'Maturity'**
  String get maturity;

  /// No description provided for @harvest.
  ///
  /// In en, this message translates to:
  /// **'Harvest'**
  String get harvest;

  /// No description provided for @seedling.
  ///
  /// In en, this message translates to:
  /// **'Seedling'**
  String get seedling;

  /// No description provided for @tillering.
  ///
  /// In en, this message translates to:
  /// **'Tillering'**
  String get tillering;

  /// No description provided for @stemElongation.
  ///
  /// In en, this message translates to:
  /// **'Stem Elongation'**
  String get stemElongation;

  /// No description provided for @heading.
  ///
  /// In en, this message translates to:
  /// **'Heading'**
  String get heading;

  /// No description provided for @anthesis.
  ///
  /// In en, this message translates to:
  /// **'Anthesis'**
  String get anthesis;

  /// No description provided for @grainFilling.
  ///
  /// In en, this message translates to:
  /// **'Grain Filling'**
  String get grainFilling;

  /// No description provided for @doughStage.
  ///
  /// In en, this message translates to:
  /// **'Dough Stage'**
  String get doughStage;

  /// No description provided for @ripening.
  ///
  /// In en, this message translates to:
  /// **'Ripening'**
  String get ripening;

  /// No description provided for @gddHistory.
  ///
  /// In en, this message translates to:
  /// **'GDD History'**
  String get gddHistory;

  /// No description provided for @gddChart.
  ///
  /// In en, this message translates to:
  /// **'GDD Chart'**
  String get gddChart;

  /// No description provided for @gddComparison.
  ///
  /// In en, this message translates to:
  /// **'GDD Comparison'**
  String get gddComparison;

  /// No description provided for @gddSeasons.
  ///
  /// In en, this message translates to:
  /// **'GDD Seasons'**
  String get gddSeasons;

  /// No description provided for @thermalTime.
  ///
  /// In en, this message translates to:
  /// **'Thermal Time'**
  String get thermalTime;

  /// No description provided for @heatUnits.
  ///
  /// In en, this message translates to:
  /// **'Heat Units'**
  String get heatUnits;

  /// No description provided for @chillingHours.
  ///
  /// In en, this message translates to:
  /// **'Chilling Hours'**
  String get chillingHours;

  /// No description provided for @vernalization.
  ///
  /// In en, this message translates to:
  /// **'Vernalization'**
  String get vernalization;

  /// No description provided for @sprayRecommendation.
  ///
  /// In en, this message translates to:
  /// **'Spray Recommendation'**
  String get sprayRecommendation;

  /// No description provided for @sprayApplication.
  ///
  /// In en, this message translates to:
  /// **'Spray Application'**
  String get sprayApplication;

  /// No description provided for @sprayDate.
  ///
  /// In en, this message translates to:
  /// **'Spray Date'**
  String get sprayDate;

  /// No description provided for @sprayTime.
  ///
  /// In en, this message translates to:
  /// **'Spray Time'**
  String get sprayTime;

  /// No description provided for @optimalSprayTime.
  ///
  /// In en, this message translates to:
  /// **'Optimal Spray Time'**
  String get optimalSprayTime;

  /// No description provided for @recommendedSprayTime.
  ///
  /// In en, this message translates to:
  /// **'Recommended Spray Time'**
  String get recommendedSprayTime;

  /// No description provided for @sprayWindow.
  ///
  /// In en, this message translates to:
  /// **'Spray Window'**
  String get sprayWindow;

  /// No description provided for @sprayConditions.
  ///
  /// In en, this message translates to:
  /// **'Spray Conditions'**
  String get sprayConditions;

  /// No description provided for @idealConditions.
  ///
  /// In en, this message translates to:
  /// **'Ideal Conditions'**
  String get idealConditions;

  /// No description provided for @favorableConditions.
  ///
  /// In en, this message translates to:
  /// **'Favorable Conditions'**
  String get favorableConditions;

  /// No description provided for @unfavorableConditions.
  ///
  /// In en, this message translates to:
  /// **'Unfavorable Conditions'**
  String get unfavorableConditions;

  /// No description provided for @poorConditions.
  ///
  /// In en, this message translates to:
  /// **'Poor Conditions'**
  String get poorConditions;

  /// No description provided for @doNotSpray.
  ///
  /// In en, this message translates to:
  /// **'Do Not Spray'**
  String get doNotSpray;

  /// No description provided for @sprayRating.
  ///
  /// In en, this message translates to:
  /// **'Spray Rating'**
  String get sprayRating;

  /// No description provided for @sprayScore.
  ///
  /// In en, this message translates to:
  /// **'Spray Score'**
  String get sprayScore;

  /// No description provided for @excellent.
  ///
  /// In en, this message translates to:
  /// **'Excellent'**
  String get excellent;

  /// No description provided for @good.
  ///
  /// In en, this message translates to:
  /// **'Good'**
  String get good;

  /// No description provided for @fair.
  ///
  /// In en, this message translates to:
  /// **'Fair'**
  String get fair;

  /// No description provided for @poor.
  ///
  /// In en, this message translates to:
  /// **'Poor'**
  String get poor;

  /// No description provided for @sprayProduct.
  ///
  /// In en, this message translates to:
  /// **'Spray Product'**
  String get sprayProduct;

  /// No description provided for @sprayChemical.
  ///
  /// In en, this message translates to:
  /// **'Spray Chemical'**
  String get sprayChemical;

  /// No description provided for @activIngredient.
  ///
  /// In en, this message translates to:
  /// **'Active Ingredient'**
  String get activIngredient;

  /// No description provided for @productName.
  ///
  /// In en, this message translates to:
  /// **'Product Name'**
  String get productName;

  /// No description provided for @tradeName.
  ///
  /// In en, this message translates to:
  /// **'Trade Name'**
  String get tradeName;

  /// No description provided for @formulation.
  ///
  /// In en, this message translates to:
  /// **'Formulation'**
  String get formulation;

  /// No description provided for @concentration.
  ///
  /// In en, this message translates to:
  /// **'Concentration'**
  String get concentration;

  /// No description provided for @dosage.
  ///
  /// In en, this message translates to:
  /// **'Dosage'**
  String get dosage;

  /// No description provided for @sprayVolume.
  ///
  /// In en, this message translates to:
  /// **'Spray Volume'**
  String get sprayVolume;

  /// No description provided for @waterVolume.
  ///
  /// In en, this message translates to:
  /// **'Water Volume'**
  String get waterVolume;

  /// No description provided for @carrierVolume.
  ///
  /// In en, this message translates to:
  /// **'Carrier Volume'**
  String get carrierVolume;

  /// No description provided for @sprayRate.
  ///
  /// In en, this message translates to:
  /// **'Spray Rate'**
  String get sprayRate;

  /// No description provided for @applicationMethod.
  ///
  /// In en, this message translates to:
  /// **'Application Method'**
  String get applicationMethod;

  /// No description provided for @sprayEquipment.
  ///
  /// In en, this message translates to:
  /// **'Spray Equipment'**
  String get sprayEquipment;

  /// No description provided for @sprayer.
  ///
  /// In en, this message translates to:
  /// **'Sprayer'**
  String get sprayer;

  /// No description provided for @nozzle.
  ///
  /// In en, this message translates to:
  /// **'Nozzle'**
  String get nozzle;

  /// No description provided for @nozzleType.
  ///
  /// In en, this message translates to:
  /// **'Nozzle Type'**
  String get nozzleType;

  /// No description provided for @nozzleSize.
  ///
  /// In en, this message translates to:
  /// **'Nozzle Size'**
  String get nozzleSize;

  /// No description provided for @sprayPressure.
  ///
  /// In en, this message translates to:
  /// **'Spray Pressure'**
  String get sprayPressure;

  /// No description provided for @dropletSize.
  ///
  /// In en, this message translates to:
  /// **'Droplet Size'**
  String get dropletSize;

  /// No description provided for @fineMist.
  ///
  /// In en, this message translates to:
  /// **'Fine Mist'**
  String get fineMist;

  /// No description provided for @coarseSpray.
  ///
  /// In en, this message translates to:
  /// **'Coarse Spray'**
  String get coarseSpray;

  /// No description provided for @mediumSpray.
  ///
  /// In en, this message translates to:
  /// **'Medium Spray'**
  String get mediumSpray;

  /// No description provided for @sprayDrift.
  ///
  /// In en, this message translates to:
  /// **'Spray Drift'**
  String get sprayDrift;

  /// No description provided for @driftRisk.
  ///
  /// In en, this message translates to:
  /// **'Drift Risk'**
  String get driftRisk;

  /// No description provided for @lowDrift.
  ///
  /// In en, this message translates to:
  /// **'Low Drift'**
  String get lowDrift;

  /// No description provided for @highDrift.
  ///
  /// In en, this message translates to:
  /// **'High Drift'**
  String get highDrift;

  /// No description provided for @windSpeed_spray.
  ///
  /// In en, this message translates to:
  /// **'Wind Speed'**
  String get windSpeed_spray;

  /// No description provided for @maxWindSpeed.
  ///
  /// In en, this message translates to:
  /// **'Max Wind Speed'**
  String get maxWindSpeed;

  /// No description provided for @temperature_spray.
  ///
  /// In en, this message translates to:
  /// **'Temperature'**
  String get temperature_spray;

  /// No description provided for @humidity_spray.
  ///
  /// In en, this message translates to:
  /// **'Humidity'**
  String get humidity_spray;

  /// No description provided for @deltaT.
  ///
  /// In en, this message translates to:
  /// **'Delta T'**
  String get deltaT;

  /// No description provided for @evaporationRate.
  ///
  /// In en, this message translates to:
  /// **'Evaporation Rate'**
  String get evaporationRate;

  /// No description provided for @inversionLayer.
  ///
  /// In en, this message translates to:
  /// **'Inversion Layer'**
  String get inversionLayer;

  /// No description provided for @rainforecast.
  ///
  /// In en, this message translates to:
  /// **'Rain Forecast'**
  String get rainforecast;

  /// No description provided for @rainWithin.
  ///
  /// In en, this message translates to:
  /// **'Rain Within'**
  String get rainWithin;

  /// No description provided for @noRain.
  ///
  /// In en, this message translates to:
  /// **'No Rain'**
  String get noRain;

  /// No description provided for @pestControl.
  ///
  /// In en, this message translates to:
  /// **'Pest Control'**
  String get pestControl;

  /// No description provided for @diseaseControl.
  ///
  /// In en, this message translates to:
  /// **'Disease Control'**
  String get diseaseControl;

  /// No description provided for @weedControl.
  ///
  /// In en, this message translates to:
  /// **'Weed Control'**
  String get weedControl;

  /// No description provided for @insect.
  ///
  /// In en, this message translates to:
  /// **'Insect'**
  String get insect;

  /// No description provided for @fungus.
  ///
  /// In en, this message translates to:
  /// **'Fungus'**
  String get fungus;

  /// No description provided for @weed.
  ///
  /// In en, this message translates to:
  /// **'Weed'**
  String get weed;

  /// No description provided for @targetPest.
  ///
  /// In en, this message translates to:
  /// **'Target Pest'**
  String get targetPest;

  /// No description provided for @pestStage.
  ///
  /// In en, this message translates to:
  /// **'Pest Stage'**
  String get pestStage;

  /// No description provided for @pestPressure.
  ///
  /// In en, this message translates to:
  /// **'Pest Pressure'**
  String get pestPressure;

  /// No description provided for @thresholdLevel.
  ///
  /// In en, this message translates to:
  /// **'Threshold Level'**
  String get thresholdLevel;

  /// No description provided for @economicThreshold.
  ///
  /// In en, this message translates to:
  /// **'Economic Threshold'**
  String get economicThreshold;

  /// No description provided for @scoutingReport.
  ///
  /// In en, this message translates to:
  /// **'Scouting Report'**
  String get scoutingReport;

  /// No description provided for @pestIdentification.
  ///
  /// In en, this message translates to:
  /// **'Pest Identification'**
  String get pestIdentification;

  /// No description provided for @sprayInterval.
  ///
  /// In en, this message translates to:
  /// **'Spray Interval'**
  String get sprayInterval;

  /// No description provided for @reentryInterval.
  ///
  /// In en, this message translates to:
  /// **'Reentry Interval'**
  String get reentryInterval;

  /// No description provided for @preharvest_interval.
  ///
  /// In en, this message translates to:
  /// **'Preharvest Interval'**
  String get preharvest_interval;

  /// No description provided for @phi.
  ///
  /// In en, this message translates to:
  /// **'PHI'**
  String get phi;

  /// No description provided for @rei.
  ///
  /// In en, this message translates to:
  /// **'REI'**
  String get rei;

  /// No description provided for @sprayLog.
  ///
  /// In en, this message translates to:
  /// **'Spray Log'**
  String get sprayLog;

  /// No description provided for @sprayRecord.
  ///
  /// In en, this message translates to:
  /// **'Spray Record'**
  String get sprayRecord;

  /// No description provided for @operatorName.
  ///
  /// In en, this message translates to:
  /// **'Operator Name'**
  String get operatorName;

  /// No description provided for @applicatorLicense.
  ///
  /// In en, this message translates to:
  /// **'Applicator License'**
  String get applicatorLicense;

  /// No description provided for @sprayArea.
  ///
  /// In en, this message translates to:
  /// **'Spray Area'**
  String get sprayArea;

  /// No description provided for @totalArea.
  ///
  /// In en, this message translates to:
  /// **'Total Area'**
  String get totalArea;

  /// No description provided for @productUsed.
  ///
  /// In en, this message translates to:
  /// **'Product Used'**
  String get productUsed;

  /// No description provided for @amountUsed.
  ///
  /// In en, this message translates to:
  /// **'Amount Used'**
  String get amountUsed;

  /// No description provided for @mixingInstructions.
  ///
  /// In en, this message translates to:
  /// **'Mixing Instructions'**
  String get mixingInstructions;

  /// No description provided for @tankMix.
  ///
  /// In en, this message translates to:
  /// **'Tank Mix'**
  String get tankMix;

  /// No description provided for @compatibility.
  ///
  /// In en, this message translates to:
  /// **'Compatibility'**
  String get compatibility;

  /// No description provided for @safetyPrecautions.
  ///
  /// In en, this message translates to:
  /// **'Safety Precautions'**
  String get safetyPrecautions;

  /// No description provided for @ppe.
  ///
  /// In en, this message translates to:
  /// **'PPE'**
  String get ppe;

  /// No description provided for @protectiveEquipment.
  ///
  /// In en, this message translates to:
  /// **'Protective Equipment'**
  String get protectiveEquipment;

  /// No description provided for @sprayCompleted.
  ///
  /// In en, this message translates to:
  /// **'Spray Completed'**
  String get sprayCompleted;

  /// No description provided for @sprayPending.
  ///
  /// In en, this message translates to:
  /// **'Spray Pending'**
  String get sprayPending;

  /// No description provided for @sprayCancelled.
  ///
  /// In en, this message translates to:
  /// **'Spray Cancelled'**
  String get sprayCancelled;

  /// No description provided for @cropRotationPlan.
  ///
  /// In en, this message translates to:
  /// **'Crop Rotation Plan'**
  String get cropRotationPlan;

  /// No description provided for @rotationCycle.
  ///
  /// In en, this message translates to:
  /// **'Rotation Cycle'**
  String get rotationCycle;

  /// No description provided for @rotationSequence.
  ///
  /// In en, this message translates to:
  /// **'Rotation Sequence'**
  String get rotationSequence;

  /// No description provided for @rotationSchedule.
  ///
  /// In en, this message translates to:
  /// **'Rotation Schedule'**
  String get rotationSchedule;

  /// No description provided for @rotationPattern.
  ///
  /// In en, this message translates to:
  /// **'Rotation Pattern'**
  String get rotationPattern;

  /// No description provided for @rotationYear.
  ///
  /// In en, this message translates to:
  /// **'Rotation Year'**
  String get rotationYear;

  /// No description provided for @currentCrop.
  ///
  /// In en, this message translates to:
  /// **'Current Crop'**
  String get currentCrop;

  /// No description provided for @previousCrop.
  ///
  /// In en, this message translates to:
  /// **'Previous Crop'**
  String get previousCrop;

  /// No description provided for @nextCrop.
  ///
  /// In en, this message translates to:
  /// **'Next Crop'**
  String get nextCrop;

  /// No description provided for @plannedCrop.
  ///
  /// In en, this message translates to:
  /// **'Planned Crop'**
  String get plannedCrop;

  /// No description provided for @rotationBenefits.
  ///
  /// In en, this message translates to:
  /// **'Rotation Benefits'**
  String get rotationBenefits;

  /// No description provided for @soilHealth_rotation.
  ///
  /// In en, this message translates to:
  /// **'Soil Health'**
  String get soilHealth_rotation;

  /// No description provided for @soilImprovement.
  ///
  /// In en, this message translates to:
  /// **'Soil Improvement'**
  String get soilImprovement;

  /// No description provided for @nitrogenFixation.
  ///
  /// In en, this message translates to:
  /// **'Nitrogen Fixation'**
  String get nitrogenFixation;

  /// No description provided for @organicMatter_rotation.
  ///
  /// In en, this message translates to:
  /// **'Organic Matter'**
  String get organicMatter_rotation;

  /// No description provided for @soilStructure.
  ///
  /// In en, this message translates to:
  /// **'Soil Structure'**
  String get soilStructure;

  /// No description provided for @soilBiology.
  ///
  /// In en, this message translates to:
  /// **'Soil Biology'**
  String get soilBiology;

  /// No description provided for @pestManagement_rotation.
  ///
  /// In en, this message translates to:
  /// **'Pest Management'**
  String get pestManagement_rotation;

  /// No description provided for @diseaseBreak.
  ///
  /// In en, this message translates to:
  /// **'Disease Break'**
  String get diseaseBreak;

  /// No description provided for @pestCycle.
  ///
  /// In en, this message translates to:
  /// **'Pest Cycle'**
  String get pestCycle;

  /// No description provided for @weedSuppression.
  ///
  /// In en, this message translates to:
  /// **'Weed Suppression'**
  String get weedSuppression;

  /// No description provided for @soilborneDisease.
  ///
  /// In en, this message translates to:
  /// **'Soilborne Disease'**
  String get soilborneDisease;

  /// No description provided for @cropCompatibility.
  ///
  /// In en, this message translates to:
  /// **'Crop Compatibility'**
  String get cropCompatibility;

  /// No description provided for @compatible.
  ///
  /// In en, this message translates to:
  /// **'Compatible'**
  String get compatible;

  /// No description provided for @incompatible.
  ///
  /// In en, this message translates to:
  /// **'Incompatible'**
  String get incompatible;

  /// No description provided for @highlyCompatible.
  ///
  /// In en, this message translates to:
  /// **'Highly Compatible'**
  String get highlyCompatible;

  /// No description provided for @moderatelyCompatible.
  ///
  /// In en, this message translates to:
  /// **'Moderately Compatible'**
  String get moderatelyCompatible;

  /// No description provided for @notRecommended.
  ///
  /// In en, this message translates to:
  /// **'Not Recommended'**
  String get notRecommended;

  /// No description provided for @legume.
  ///
  /// In en, this message translates to:
  /// **'Legume'**
  String get legume;

  /// No description provided for @cereal.
  ///
  /// In en, this message translates to:
  /// **'Cereal'**
  String get cereal;

  /// No description provided for @oilseed.
  ///
  /// In en, this message translates to:
  /// **'Oilseed'**
  String get oilseed;

  /// No description provided for @vegetable.
  ///
  /// In en, this message translates to:
  /// **'Vegetable'**
  String get vegetable;

  /// No description provided for @forage.
  ///
  /// In en, this message translates to:
  /// **'Forage'**
  String get forage;

  /// No description provided for @coverCrop.
  ///
  /// In en, this message translates to:
  /// **'Cover Crop'**
  String get coverCrop;

  /// No description provided for @greenManure.
  ///
  /// In en, this message translates to:
  /// **'Green Manure'**
  String get greenManure;

  /// No description provided for @fallowPeriod.
  ///
  /// In en, this message translates to:
  /// **'Fallow Period'**
  String get fallowPeriod;

  /// No description provided for @restPeriod.
  ///
  /// In en, this message translates to:
  /// **'Rest Period'**
  String get restPeriod;

  /// No description provided for @rotationDuration.
  ///
  /// In en, this message translates to:
  /// **'Rotation Duration'**
  String get rotationDuration;

  /// No description provided for @twoYearRotation.
  ///
  /// In en, this message translates to:
  /// **'Two-Year Rotation'**
  String get twoYearRotation;

  /// No description provided for @threeYearRotation.
  ///
  /// In en, this message translates to:
  /// **'Three-Year Rotation'**
  String get threeYearRotation;

  /// No description provided for @fourYearRotation.
  ///
  /// In en, this message translates to:
  /// **'Four-Year Rotation'**
  String get fourYearRotation;

  /// No description provided for @longTermRotation.
  ///
  /// In en, this message translates to:
  /// **'Long-Term Rotation'**
  String get longTermRotation;

  /// No description provided for @rotationRecommendations.
  ///
  /// In en, this message translates to:
  /// **'Rotation Recommendations'**
  String get rotationRecommendations;

  /// No description provided for @rotationSuggestions.
  ///
  /// In en, this message translates to:
  /// **'Rotation Suggestions'**
  String get rotationSuggestions;

  /// No description provided for @rotationWarning.
  ///
  /// In en, this message translates to:
  /// **'Rotation Warning'**
  String get rotationWarning;

  /// No description provided for @rotationConflict.
  ///
  /// In en, this message translates to:
  /// **'Rotation Conflict'**
  String get rotationConflict;

  /// No description provided for @monoculture.
  ///
  /// In en, this message translates to:
  /// **'Monoculture'**
  String get monoculture;

  /// No description provided for @diversification.
  ///
  /// In en, this message translates to:
  /// **'Diversification'**
  String get diversification;

  /// No description provided for @cropDiversity.
  ///
  /// In en, this message translates to:
  /// **'Crop Diversity'**
  String get cropDiversity;

  /// No description provided for @sustainableAgriculture.
  ///
  /// In en, this message translates to:
  /// **'Sustainable Agriculture'**
  String get sustainableAgriculture;

  /// No description provided for @rotationImpact.
  ///
  /// In en, this message translates to:
  /// **'Rotation Impact'**
  String get rotationImpact;

  /// No description provided for @yieldImpact.
  ///
  /// In en, this message translates to:
  /// **'Yield Impact'**
  String get yieldImpact;

  /// No description provided for @economicImpact.
  ///
  /// In en, this message translates to:
  /// **'Economic Impact'**
  String get economicImpact;

  /// No description provided for @environmentalImpact.
  ///
  /// In en, this message translates to:
  /// **'Environmental Impact'**
  String get environmentalImpact;

  /// No description provided for @financialAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Financial Analysis'**
  String get financialAnalysis;

  /// No description provided for @economicAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Economic Analysis'**
  String get economicAnalysis;

  /// No description provided for @costAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Cost Analysis'**
  String get costAnalysis;

  /// No description provided for @revenue.
  ///
  /// In en, this message translates to:
  /// **'Revenue'**
  String get revenue;

  /// No description provided for @totalRevenue.
  ///
  /// In en, this message translates to:
  /// **'Total Revenue'**
  String get totalRevenue;

  /// No description provided for @grossRevenue.
  ///
  /// In en, this message translates to:
  /// **'Gross Revenue'**
  String get grossRevenue;

  /// No description provided for @netRevenue.
  ///
  /// In en, this message translates to:
  /// **'Net Revenue'**
  String get netRevenue;

  /// No description provided for @income.
  ///
  /// In en, this message translates to:
  /// **'Income'**
  String get income;

  /// No description provided for @totalIncome.
  ///
  /// In en, this message translates to:
  /// **'Total Income'**
  String get totalIncome;

  /// No description provided for @grossIncome.
  ///
  /// In en, this message translates to:
  /// **'Gross Income'**
  String get grossIncome;

  /// No description provided for @netIncome.
  ///
  /// In en, this message translates to:
  /// **'Net Income'**
  String get netIncome;

  /// No description provided for @profit.
  ///
  /// In en, this message translates to:
  /// **'Profit'**
  String get profit;

  /// No description provided for @totalProfit.
  ///
  /// In en, this message translates to:
  /// **'Total Profit'**
  String get totalProfit;

  /// No description provided for @grossProfit.
  ///
  /// In en, this message translates to:
  /// **'Gross Profit'**
  String get grossProfit;

  /// No description provided for @netProfit.
  ///
  /// In en, this message translates to:
  /// **'Net Profit'**
  String get netProfit;

  /// No description provided for @loss.
  ///
  /// In en, this message translates to:
  /// **'Loss'**
  String get loss;

  /// No description provided for @profitMargin.
  ///
  /// In en, this message translates to:
  /// **'Profit Margin'**
  String get profitMargin;

  /// No description provided for @profitMargin_percentage.
  ///
  /// In en, this message translates to:
  /// **'Profit Margin (%)'**
  String get profitMargin_percentage;

  /// No description provided for @grossMargin.
  ///
  /// In en, this message translates to:
  /// **'Gross Margin'**
  String get grossMargin;

  /// No description provided for @netMargin.
  ///
  /// In en, this message translates to:
  /// **'Net Margin'**
  String get netMargin;

  /// No description provided for @operatingMargin.
  ///
  /// In en, this message translates to:
  /// **'Operating Margin'**
  String get operatingMargin;

  /// No description provided for @costs.
  ///
  /// In en, this message translates to:
  /// **'Costs'**
  String get costs;

  /// No description provided for @totalCosts.
  ///
  /// In en, this message translates to:
  /// **'Total Costs'**
  String get totalCosts;

  /// No description provided for @directCosts.
  ///
  /// In en, this message translates to:
  /// **'Direct Costs'**
  String get directCosts;

  /// No description provided for @indirectCosts.
  ///
  /// In en, this message translates to:
  /// **'Indirect Costs'**
  String get indirectCosts;

  /// No description provided for @fixedCosts.
  ///
  /// In en, this message translates to:
  /// **'Fixed Costs'**
  String get fixedCosts;

  /// No description provided for @variableCosts.
  ///
  /// In en, this message translates to:
  /// **'Variable Costs'**
  String get variableCosts;

  /// No description provided for @operatingCosts.
  ///
  /// In en, this message translates to:
  /// **'Operating Costs'**
  String get operatingCosts;

  /// No description provided for @productionCosts.
  ///
  /// In en, this message translates to:
  /// **'Production Costs'**
  String get productionCosts;

  /// No description provided for @costPerHectare.
  ///
  /// In en, this message translates to:
  /// **'Cost Per Hectare'**
  String get costPerHectare;

  /// No description provided for @costPerAcre.
  ///
  /// In en, this message translates to:
  /// **'Cost Per Acre'**
  String get costPerAcre;

  /// No description provided for @costPerUnit.
  ///
  /// In en, this message translates to:
  /// **'Cost Per Unit'**
  String get costPerUnit;

  /// No description provided for @seedCost.
  ///
  /// In en, this message translates to:
  /// **'Seed Cost'**
  String get seedCost;

  /// No description provided for @fertilizerCost.
  ///
  /// In en, this message translates to:
  /// **'Fertilizer Cost'**
  String get fertilizerCost;

  /// No description provided for @pesticideCost.
  ///
  /// In en, this message translates to:
  /// **'Pesticide Cost'**
  String get pesticideCost;

  /// No description provided for @irrigationCost.
  ///
  /// In en, this message translates to:
  /// **'Irrigation Cost'**
  String get irrigationCost;

  /// No description provided for @laborCost.
  ///
  /// In en, this message translates to:
  /// **'Labor Cost'**
  String get laborCost;

  /// No description provided for @machineCost.
  ///
  /// In en, this message translates to:
  /// **'Machine Cost'**
  String get machineCost;

  /// No description provided for @fuelCost.
  ///
  /// In en, this message translates to:
  /// **'Fuel Cost'**
  String get fuelCost;

  /// No description provided for @maintenanceCost.
  ///
  /// In en, this message translates to:
  /// **'Maintenance Cost'**
  String get maintenanceCost;

  /// No description provided for @rentCost.
  ///
  /// In en, this message translates to:
  /// **'Rent Cost'**
  String get rentCost;

  /// No description provided for @landRent.
  ///
  /// In en, this message translates to:
  /// **'Land Rent'**
  String get landRent;

  /// No description provided for @equipmentRent.
  ///
  /// In en, this message translates to:
  /// **'Equipment Rent'**
  String get equipmentRent;

  /// No description provided for @insuranceCost.
  ///
  /// In en, this message translates to:
  /// **'Insurance Cost'**
  String get insuranceCost;

  /// No description provided for @transportCost.
  ///
  /// In en, this message translates to:
  /// **'Transport Cost'**
  String get transportCost;

  /// No description provided for @storageCost.
  ///
  /// In en, this message translates to:
  /// **'Storage Cost'**
  String get storageCost;

  /// No description provided for @marketingCost.
  ///
  /// In en, this message translates to:
  /// **'Marketing Cost'**
  String get marketingCost;

  /// No description provided for @overheadCosts.
  ///
  /// In en, this message translates to:
  /// **'Overhead Costs'**
  String get overheadCosts;

  /// No description provided for @administrativeCosts.
  ///
  /// In en, this message translates to:
  /// **'Administrative Costs'**
  String get administrativeCosts;

  /// No description provided for @financialCosts.
  ///
  /// In en, this message translates to:
  /// **'Financial Costs'**
  String get financialCosts;

  /// No description provided for @interestExpense.
  ///
  /// In en, this message translates to:
  /// **'Interest Expense'**
  String get interestExpense;

  /// No description provided for @depreciation.
  ///
  /// In en, this message translates to:
  /// **'Depreciation'**
  String get depreciation;

  /// No description provided for @amortization.
  ///
  /// In en, this message translates to:
  /// **'Amortization'**
  String get amortization;

  /// No description provided for @breakEvenPoint.
  ///
  /// In en, this message translates to:
  /// **'Break Even Point'**
  String get breakEvenPoint;

  /// No description provided for @breakEvenYield.
  ///
  /// In en, this message translates to:
  /// **'Break Even Yield'**
  String get breakEvenYield;

  /// No description provided for @breakEvenPrice.
  ///
  /// In en, this message translates to:
  /// **'Break Even Price'**
  String get breakEvenPrice;

  /// No description provided for @breakEvenAnalysis.
  ///
  /// In en, this message translates to:
  /// **'Break Even Analysis'**
  String get breakEvenAnalysis;

  /// No description provided for @roi.
  ///
  /// In en, this message translates to:
  /// **'ROI'**
  String get roi;

  /// No description provided for @returnOnInvestment.
  ///
  /// In en, this message translates to:
  /// **'Return on Investment'**
  String get returnOnInvestment;

  /// No description provided for @returnOnAssets.
  ///
  /// In en, this message translates to:
  /// **'Return on Assets'**
  String get returnOnAssets;

  /// No description provided for @returnOnEquity.
  ///
  /// In en, this message translates to:
  /// **'Return on Equity'**
  String get returnOnEquity;

  /// No description provided for @paybackPeriod.
  ///
  /// In en, this message translates to:
  /// **'Payback Period'**
  String get paybackPeriod;

  /// No description provided for @netPresentValue.
  ///
  /// In en, this message translates to:
  /// **'Net Present Value'**
  String get netPresentValue;

  /// No description provided for @npv.
  ///
  /// In en, this message translates to:
  /// **'NPV'**
  String get npv;

  /// No description provided for @irr.
  ///
  /// In en, this message translates to:
  /// **'IRR'**
  String get irr;

  /// No description provided for @internalRateOfReturn.
  ///
  /// In en, this message translates to:
  /// **'Internal Rate of Return'**
  String get internalRateOfReturn;

  /// No description provided for @profitabilityIndex.
  ///
  /// In en, this message translates to:
  /// **'Profitability Index'**
  String get profitabilityIndex;

  /// No description provided for @costBenefitRatio.
  ///
  /// In en, this message translates to:
  /// **'Cost-Benefit Ratio'**
  String get costBenefitRatio;

  /// No description provided for @benefitCostRatio.
  ///
  /// In en, this message translates to:
  /// **'Benefit-Cost Ratio'**
  String get benefitCostRatio;

  /// No description provided for @marketPrice.
  ///
  /// In en, this message translates to:
  /// **'Market Price'**
  String get marketPrice;

  /// No description provided for @sellingPrice.
  ///
  /// In en, this message translates to:
  /// **'Selling Price'**
  String get sellingPrice;

  /// No description provided for @purchasePrice.
  ///
  /// In en, this message translates to:
  /// **'Purchase Price'**
  String get purchasePrice;

  /// No description provided for @pricePerUnit.
  ///
  /// In en, this message translates to:
  /// **'Price Per Unit'**
  String get pricePerUnit;

  /// No description provided for @pricePerKg.
  ///
  /// In en, this message translates to:
  /// **'Price Per Kg'**
  String get pricePerKg;

  /// No description provided for @pricePerTon.
  ///
  /// In en, this message translates to:
  /// **'Price Per Ton'**
  String get pricePerTon;

  /// No description provided for @yieldValue.
  ///
  /// In en, this message translates to:
  /// **'Yield Value'**
  String get yieldValue;

  /// No description provided for @marketValue.
  ///
  /// In en, this message translates to:
  /// **'Market Value'**
  String get marketValue;

  /// No description provided for @cropValue.
  ///
  /// In en, this message translates to:
  /// **'Crop Value'**
  String get cropValue;

  /// No description provided for @budgetPlanning.
  ///
  /// In en, this message translates to:
  /// **'Budget Planning'**
  String get budgetPlanning;

  /// No description provided for @budget.
  ///
  /// In en, this message translates to:
  /// **'Budget'**
  String get budget;

  /// No description provided for @forecastedBudget.
  ///
  /// In en, this message translates to:
  /// **'Forecasted Budget'**
  String get forecastedBudget;

  /// No description provided for @actualBudget.
  ///
  /// In en, this message translates to:
  /// **'Actual Budget'**
  String get actualBudget;

  /// No description provided for @budgetVariance.
  ///
  /// In en, this message translates to:
  /// **'Budget Variance'**
  String get budgetVariance;

  /// No description provided for @costOverrun.
  ///
  /// In en, this message translates to:
  /// **'Cost Overrun'**
  String get costOverrun;

  /// No description provided for @savings.
  ///
  /// In en, this message translates to:
  /// **'Savings'**
  String get savings;

  /// No description provided for @costSavings.
  ///
  /// In en, this message translates to:
  /// **'Cost Savings'**
  String get costSavings;

  /// No description provided for @profitabilityTrend.
  ///
  /// In en, this message translates to:
  /// **'Profitability Trend'**
  String get profitabilityTrend;

  /// No description provided for @historicalProfitability.
  ///
  /// In en, this message translates to:
  /// **'Historical Profitability'**
  String get historicalProfitability;

  /// No description provided for @projectedProfitability.
  ///
  /// In en, this message translates to:
  /// **'Projected Profitability'**
  String get projectedProfitability;

  /// No description provided for @seasonalProfitability.
  ///
  /// In en, this message translates to:
  /// **'Seasonal Profitability'**
  String get seasonalProfitability;

  /// No description provided for @comparativeProfitability.
  ///
  /// In en, this message translates to:
  /// **'Comparative Profitability'**
  String get comparativeProfitability;

  /// No description provided for @benchmarking.
  ///
  /// In en, this message translates to:
  /// **'Benchmarking'**
  String get benchmarking;

  /// No description provided for @industryAverage.
  ///
  /// In en, this message translates to:
  /// **'Industry Average'**
  String get industryAverage;

  /// No description provided for @bestPractices.
  ///
  /// In en, this message translates to:
  /// **'Best Practices'**
  String get bestPractices;

  /// No description provided for @financialKPIs.
  ///
  /// In en, this message translates to:
  /// **'Financial KPIs'**
  String get financialKPIs;

  /// No description provided for @economicIndicators.
  ///
  /// In en, this message translates to:
  /// **'Economic Indicators'**
  String get economicIndicators;

  /// No description provided for @financialSummary.
  ///
  /// In en, this message translates to:
  /// **'Financial Summary'**
  String get financialSummary;

  /// No description provided for @incomeStatement.
  ///
  /// In en, this message translates to:
  /// **'Income Statement'**
  String get incomeStatement;

  /// No description provided for @cashFlow.
  ///
  /// In en, this message translates to:
  /// **'Cash Flow'**
  String get cashFlow;

  /// No description provided for @cashFlowStatement.
  ///
  /// In en, this message translates to:
  /// **'Cash Flow Statement'**
  String get cashFlowStatement;

  /// No description provided for @balanceSheet.
  ///
  /// In en, this message translates to:
  /// **'Balance Sheet'**
  String get balanceSheet;

  /// No description provided for @assets.
  ///
  /// In en, this message translates to:
  /// **'Assets'**
  String get assets;

  /// No description provided for @liabilities.
  ///
  /// In en, this message translates to:
  /// **'Liabilities'**
  String get liabilities;

  /// No description provided for @equity.
  ///
  /// In en, this message translates to:
  /// **'Equity'**
  String get equity;

  /// No description provided for @workingCapital.
  ///
  /// In en, this message translates to:
  /// **'Working Capital'**
  String get workingCapital;

  /// No description provided for @currentAssets.
  ///
  /// In en, this message translates to:
  /// **'Current Assets'**
  String get currentAssets;

  /// No description provided for @currentLiabilities.
  ///
  /// In en, this message translates to:
  /// **'Current Liabilities'**
  String get currentLiabilities;

  /// No description provided for @liquidityRatio.
  ///
  /// In en, this message translates to:
  /// **'Liquidity Ratio'**
  String get liquidityRatio;

  /// No description provided for @debtRatio.
  ///
  /// In en, this message translates to:
  /// **'Debt Ratio'**
  String get debtRatio;

  /// No description provided for @leverageRatio.
  ///
  /// In en, this message translates to:
  /// **'Leverage Ratio'**
  String get leverageRatio;

  /// No description provided for @financialHealth.
  ///
  /// In en, this message translates to:
  /// **'Financial Health'**
  String get financialHealth;

  /// No description provided for @creditScore.
  ///
  /// In en, this message translates to:
  /// **'Credit Score'**
  String get creditScore;

  /// No description provided for @inventoryItem.
  ///
  /// In en, this message translates to:
  /// **'Inventory Item'**
  String get inventoryItem;

  /// No description provided for @itemName.
  ///
  /// In en, this message translates to:
  /// **'Item Name'**
  String get itemName;

  /// No description provided for @itemCode.
  ///
  /// In en, this message translates to:
  /// **'Item Code'**
  String get itemCode;

  /// No description provided for @itemDescription.
  ///
  /// In en, this message translates to:
  /// **'Item Description'**
  String get itemDescription;

  /// No description provided for @itemCategory.
  ///
  /// In en, this message translates to:
  /// **'Item Category'**
  String get itemCategory;

  /// No description provided for @itemType.
  ///
  /// In en, this message translates to:
  /// **'Item Type'**
  String get itemType;

  /// No description provided for @stock.
  ///
  /// In en, this message translates to:
  /// **'Stock'**
  String get stock;

  /// No description provided for @inStock.
  ///
  /// In en, this message translates to:
  /// **'In Stock'**
  String get inStock;

  /// No description provided for @outOfStock.
  ///
  /// In en, this message translates to:
  /// **'Out of Stock'**
  String get outOfStock;

  /// No description provided for @lowStock.
  ///
  /// In en, this message translates to:
  /// **'Low Stock'**
  String get lowStock;

  /// No description provided for @stockLevel.
  ///
  /// In en, this message translates to:
  /// **'Stock Level'**
  String get stockLevel;

  /// No description provided for @currentStock.
  ///
  /// In en, this message translates to:
  /// **'Current Stock'**
  String get currentStock;

  /// No description provided for @availableStock.
  ///
  /// In en, this message translates to:
  /// **'Available Stock'**
  String get availableStock;

  /// No description provided for @reservedStock.
  ///
  /// In en, this message translates to:
  /// **'Reserved Stock'**
  String get reservedStock;

  /// No description provided for @stockOnHand.
  ///
  /// In en, this message translates to:
  /// **'Stock on Hand'**
  String get stockOnHand;

  /// No description provided for @minimumStock.
  ///
  /// In en, this message translates to:
  /// **'Minimum Stock'**
  String get minimumStock;

  /// No description provided for @maximumStock.
  ///
  /// In en, this message translates to:
  /// **'Maximum Stock'**
  String get maximumStock;

  /// No description provided for @reorderPoint.
  ///
  /// In en, this message translates to:
  /// **'Reorder Point'**
  String get reorderPoint;

  /// No description provided for @reorderQuantity.
  ///
  /// In en, this message translates to:
  /// **'Reorder Quantity'**
  String get reorderQuantity;

  /// No description provided for @safetyStock.
  ///
  /// In en, this message translates to:
  /// **'Safety Stock'**
  String get safetyStock;

  /// No description provided for @stockAlert.
  ///
  /// In en, this message translates to:
  /// **'Stock Alert'**
  String get stockAlert;

  /// No description provided for @stockWarning.
  ///
  /// In en, this message translates to:
  /// **'Stock Warning'**
  String get stockWarning;

  /// No description provided for @stockMovement.
  ///
  /// In en, this message translates to:
  /// **'Stock Movement'**
  String get stockMovement;

  /// No description provided for @stockIn.
  ///
  /// In en, this message translates to:
  /// **'Stock In'**
  String get stockIn;

  /// No description provided for @stockOut.
  ///
  /// In en, this message translates to:
  /// **'Stock Out'**
  String get stockOut;

  /// No description provided for @stockTransfer.
  ///
  /// In en, this message translates to:
  /// **'Stock Transfer'**
  String get stockTransfer;

  /// No description provided for @stockAdjustment.
  ///
  /// In en, this message translates to:
  /// **'Stock Adjustment'**
  String get stockAdjustment;

  /// No description provided for @stockTake.
  ///
  /// In en, this message translates to:
  /// **'Stock Take'**
  String get stockTake;

  /// No description provided for @physicalInventory.
  ///
  /// In en, this message translates to:
  /// **'Physical Inventory'**
  String get physicalInventory;

  /// No description provided for @stockCount.
  ///
  /// In en, this message translates to:
  /// **'Stock Count'**
  String get stockCount;

  /// No description provided for @cycleCount.
  ///
  /// In en, this message translates to:
  /// **'Cycle Count'**
  String get cycleCount;

  /// No description provided for @inventoryAudit.
  ///
  /// In en, this message translates to:
  /// **'Inventory Audit'**
  String get inventoryAudit;

  /// No description provided for @discrepancy.
  ///
  /// In en, this message translates to:
  /// **'Discrepancy'**
  String get discrepancy;

  /// No description provided for @variance.
  ///
  /// In en, this message translates to:
  /// **'Variance'**
  String get variance;

  /// No description provided for @shrinkage.
  ///
  /// In en, this message translates to:
  /// **'Shrinkage'**
  String get shrinkage;

  /// No description provided for @wastage.
  ///
  /// In en, this message translates to:
  /// **'Wastage'**
  String get wastage;

  /// No description provided for @damage.
  ///
  /// In en, this message translates to:
  /// **'Damage'**
  String get damage;

  /// No description provided for @expired.
  ///
  /// In en, this message translates to:
  /// **'Expired'**
  String get expired;

  /// No description provided for @expiryDate.
  ///
  /// In en, this message translates to:
  /// **'Expiry Date'**
  String get expiryDate;

  /// No description provided for @batchNumber.
  ///
  /// In en, this message translates to:
  /// **'Batch Number'**
  String get batchNumber;

  /// No description provided for @lotNumber.
  ///
  /// In en, this message translates to:
  /// **'Lot Number'**
  String get lotNumber;

  /// No description provided for @serialNumber.
  ///
  /// In en, this message translates to:
  /// **'Serial Number'**
  String get serialNumber;

  /// No description provided for @supplier.
  ///
  /// In en, this message translates to:
  /// **'Supplier'**
  String get supplier;

  /// No description provided for @supplierName.
  ///
  /// In en, this message translates to:
  /// **'Supplier Name'**
  String get supplierName;

  /// No description provided for @supplierCode.
  ///
  /// In en, this message translates to:
  /// **'Supplier Code'**
  String get supplierCode;

  /// No description provided for @purchase.
  ///
  /// In en, this message translates to:
  /// **'Purchase'**
  String get purchase;

  /// No description provided for @purchaseOrder.
  ///
  /// In en, this message translates to:
  /// **'Purchase Order'**
  String get purchaseOrder;

  /// No description provided for @purchaseDate.
  ///
  /// In en, this message translates to:
  /// **'Purchase Date'**
  String get purchaseDate;

  /// No description provided for @purchaseQuantity.
  ///
  /// In en, this message translates to:
  /// **'Purchase Quantity'**
  String get purchaseQuantity;

  /// No description provided for @delivery.
  ///
  /// In en, this message translates to:
  /// **'Delivery'**
  String get delivery;

  /// No description provided for @deliveryDate.
  ///
  /// In en, this message translates to:
  /// **'Delivery Date'**
  String get deliveryDate;

  /// No description provided for @deliveryNote.
  ///
  /// In en, this message translates to:
  /// **'Delivery Note'**
  String get deliveryNote;

  /// No description provided for @received.
  ///
  /// In en, this message translates to:
  /// **'Received'**
  String get received;

  /// No description provided for @receivedDate.
  ///
  /// In en, this message translates to:
  /// **'Received Date'**
  String get receivedDate;

  /// No description provided for @receivedQuantity.
  ///
  /// In en, this message translates to:
  /// **'Received Quantity'**
  String get receivedQuantity;

  /// No description provided for @issue.
  ///
  /// In en, this message translates to:
  /// **'Issue'**
  String get issue;

  /// No description provided for @issued.
  ///
  /// In en, this message translates to:
  /// **'Issued'**
  String get issued;

  /// No description provided for @issuedDate.
  ///
  /// In en, this message translates to:
  /// **'Issued Date'**
  String get issuedDate;

  /// No description provided for @issuedQuantity.
  ///
  /// In en, this message translates to:
  /// **'Issued Quantity'**
  String get issuedQuantity;

  /// No description provided for @usage.
  ///
  /// In en, this message translates to:
  /// **'Usage'**
  String get usage;

  /// No description provided for @consumption.
  ///
  /// In en, this message translates to:
  /// **'Consumption'**
  String get consumption;

  /// No description provided for @consumptionRate.
  ///
  /// In en, this message translates to:
  /// **'Consumption Rate'**
  String get consumptionRate;

  /// No description provided for @usageHistory.
  ///
  /// In en, this message translates to:
  /// **'Usage History'**
  String get usageHistory;

  /// No description provided for @location.
  ///
  /// In en, this message translates to:
  /// **'Location'**
  String get location;

  /// No description provided for @storageLocation.
  ///
  /// In en, this message translates to:
  /// **'Storage Location'**
  String get storageLocation;

  /// No description provided for @warehouse.
  ///
  /// In en, this message translates to:
  /// **'Warehouse'**
  String get warehouse;

  /// No description provided for @bin.
  ///
  /// In en, this message translates to:
  /// **'Bin'**
  String get bin;

  /// No description provided for @shelf.
  ///
  /// In en, this message translates to:
  /// **'Shelf'**
  String get shelf;

  /// No description provided for @zone_inventory.
  ///
  /// In en, this message translates to:
  /// **'Zone'**
  String get zone_inventory;

  /// No description provided for @inventoryValue.
  ///
  /// In en, this message translates to:
  /// **'Inventory Value'**
  String get inventoryValue;

  /// No description provided for @totalValue.
  ///
  /// In en, this message translates to:
  /// **'Total Value'**
  String get totalValue;

  /// No description provided for @unitValue.
  ///
  /// In en, this message translates to:
  /// **'Unit Value'**
  String get unitValue;

  /// No description provided for @valuationMethod.
  ///
  /// In en, this message translates to:
  /// **'Valuation Method'**
  String get valuationMethod;

  /// No description provided for @fifo.
  ///
  /// In en, this message translates to:
  /// **'FIFO (First In First Out)'**
  String get fifo;

  /// No description provided for @lifo.
  ///
  /// In en, this message translates to:
  /// **'LIFO (Last In First Out)'**
  String get lifo;

  /// No description provided for @averageCost.
  ///
  /// In en, this message translates to:
  /// **'Average Cost'**
  String get averageCost;

  /// No description provided for @weightedAverage.
  ///
  /// In en, this message translates to:
  /// **'Weighted Average'**
  String get weightedAverage;

  /// No description provided for @inventoryTurnover.
  ///
  /// In en, this message translates to:
  /// **'Inventory Turnover'**
  String get inventoryTurnover;

  /// No description provided for @turnoverRatio.
  ///
  /// In en, this message translates to:
  /// **'Turnover Ratio'**
  String get turnoverRatio;

  /// No description provided for @daysInventory.
  ///
  /// In en, this message translates to:
  /// **'Days Inventory'**
  String get daysInventory;

  /// No description provided for @inventoryAge.
  ///
  /// In en, this message translates to:
  /// **'Inventory Age'**
  String get inventoryAge;

  /// No description provided for @slowMoving.
  ///
  /// In en, this message translates to:
  /// **'Slow Moving'**
  String get slowMoving;

  /// No description provided for @fastMoving.
  ///
  /// In en, this message translates to:
  /// **'Fast Moving'**
  String get fastMoving;

  /// No description provided for @obsolete.
  ///
  /// In en, this message translates to:
  /// **'Obsolete'**
  String get obsolete;

  /// No description provided for @deadStock.
  ///
  /// In en, this message translates to:
  /// **'Dead Stock'**
  String get deadStock;

  /// No description provided for @inventoryReport.
  ///
  /// In en, this message translates to:
  /// **'Inventory Report'**
  String get inventoryReport;

  /// No description provided for @stockReport.
  ///
  /// In en, this message translates to:
  /// **'Stock Report'**
  String get stockReport;

  /// No description provided for @inventorySummary.
  ///
  /// In en, this message translates to:
  /// **'Inventory Summary'**
  String get inventorySummary;

  /// No description provided for @movementReport.
  ///
  /// In en, this message translates to:
  /// **'Movement Report'**
  String get movementReport;

  /// No description provided for @valuationReport.
  ///
  /// In en, this message translates to:
  /// **'Valuation Report'**
  String get valuationReport;

  /// No description provided for @agingReport.
  ///
  /// In en, this message translates to:
  /// **'Aging Report'**
  String get agingReport;

  /// No description provided for @message.
  ///
  /// In en, this message translates to:
  /// **'Message'**
  String get message;

  /// No description provided for @newMessage.
  ///
  /// In en, this message translates to:
  /// **'New Message'**
  String get newMessage;

  /// No description provided for @sendMessage.
  ///
  /// In en, this message translates to:
  /// **'Send Message'**
  String get sendMessage;

  /// No description provided for @replyMessage.
  ///
  /// In en, this message translates to:
  /// **'Reply Message'**
  String get replyMessage;

  /// No description provided for @forwardMessage.
  ///
  /// In en, this message translates to:
  /// **'Forward Message'**
  String get forwardMessage;

  /// No description provided for @deleteMessage.
  ///
  /// In en, this message translates to:
  /// **'Delete Message'**
  String get deleteMessage;

  /// No description provided for @editMessage.
  ///
  /// In en, this message translates to:
  /// **'Edit Message'**
  String get editMessage;

  /// No description provided for @messageText.
  ///
  /// In en, this message translates to:
  /// **'Message Text'**
  String get messageText;

  /// No description provided for @messageContent.
  ///
  /// In en, this message translates to:
  /// **'Message Content'**
  String get messageContent;

  /// No description provided for @typeMessage.
  ///
  /// In en, this message translates to:
  /// **'Type a message...'**
  String get typeMessage;

  /// No description provided for @conversation.
  ///
  /// In en, this message translates to:
  /// **'Conversation'**
  String get conversation;

  /// No description provided for @newConversation.
  ///
  /// In en, this message translates to:
  /// **'New Conversation'**
  String get newConversation;

  /// No description provided for @conversationList.
  ///
  /// In en, this message translates to:
  /// **'Conversation List'**
  String get conversationList;

  /// No description provided for @openConversation.
  ///
  /// In en, this message translates to:
  /// **'Open Conversation'**
  String get openConversation;

  /// No description provided for @closeConversation.
  ///
  /// In en, this message translates to:
  /// **'Close Conversation'**
  String get closeConversation;

  /// No description provided for @deleteConversation.
  ///
  /// In en, this message translates to:
  /// **'Delete Conversation'**
  String get deleteConversation;

  /// No description provided for @archiveConversation.
  ///
  /// In en, this message translates to:
  /// **'Archive Conversation'**
  String get archiveConversation;

  /// No description provided for @unarchiveConversation.
  ///
  /// In en, this message translates to:
  /// **'Unarchive Conversation'**
  String get unarchiveConversation;

  /// No description provided for @muteConversation.
  ///
  /// In en, this message translates to:
  /// **'Mute Conversation'**
  String get muteConversation;

  /// No description provided for @unmuteConversation.
  ///
  /// In en, this message translates to:
  /// **'Unmute Conversation'**
  String get unmuteConversation;

  /// No description provided for @markAsRead.
  ///
  /// In en, this message translates to:
  /// **'Mark as Read'**
  String get markAsRead;

  /// No description provided for @markAsUnread.
  ///
  /// In en, this message translates to:
  /// **'Mark as Unread'**
  String get markAsUnread;

  /// No description provided for @unreadMessages.
  ///
  /// In en, this message translates to:
  /// **'Unread Messages'**
  String get unreadMessages;

  /// No description provided for @readMessages.
  ///
  /// In en, this message translates to:
  /// **'Read Messages'**
  String get readMessages;

  /// No description provided for @recipient.
  ///
  /// In en, this message translates to:
  /// **'Recipient'**
  String get recipient;

  /// No description provided for @sender.
  ///
  /// In en, this message translates to:
  /// **'Sender'**
  String get sender;

  /// No description provided for @sent.
  ///
  /// In en, this message translates to:
  /// **'Sent'**
  String get sent;

  /// No description provided for @delivered.
  ///
  /// In en, this message translates to:
  /// **'Delivered'**
  String get delivered;

  /// No description provided for @read.
  ///
  /// In en, this message translates to:
  /// **'Read'**
  String get read;

  /// No description provided for @typing.
  ///
  /// In en, this message translates to:
  /// **'Typing...'**
  String get typing;

  /// No description provided for @online_.
  ///
  /// In en, this message translates to:
  /// **'Online'**
  String get online_;

  /// No description provided for @offline_.
  ///
  /// In en, this message translates to:
  /// **'Offline'**
  String get offline_;

  /// No description provided for @lastSeen.
  ///
  /// In en, this message translates to:
  /// **'Last Seen'**
  String get lastSeen;

  /// No description provided for @attachment.
  ///
  /// In en, this message translates to:
  /// **'Attachment'**
  String get attachment;

  /// No description provided for @attachFile.
  ///
  /// In en, this message translates to:
  /// **'Attach File'**
  String get attachFile;

  /// No description provided for @attachImage.
  ///
  /// In en, this message translates to:
  /// **'Attach Image'**
  String get attachImage;

  /// No description provided for @attachDocument.
  ///
  /// In en, this message translates to:
  /// **'Attach Document'**
  String get attachDocument;

  /// No description provided for @photo.
  ///
  /// In en, this message translates to:
  /// **'Photo'**
  String get photo;

  /// No description provided for @video.
  ///
  /// In en, this message translates to:
  /// **'Video'**
  String get video;

  /// No description provided for @audio.
  ///
  /// In en, this message translates to:
  /// **'Audio'**
  String get audio;

  /// No description provided for @document.
  ///
  /// In en, this message translates to:
  /// **'Document'**
  String get document;

  /// No description provided for @file.
  ///
  /// In en, this message translates to:
  /// **'File'**
  String get file;

  /// No description provided for @emoji.
  ///
  /// In en, this message translates to:
  /// **'Emoji'**
  String get emoji;

  /// No description provided for @sticker.
  ///
  /// In en, this message translates to:
  /// **'Sticker'**
  String get sticker;

  /// No description provided for @voiceMessage.
  ///
  /// In en, this message translates to:
  /// **'Voice Message'**
  String get voiceMessage;

  /// No description provided for @recordVoice.
  ///
  /// In en, this message translates to:
  /// **'Record Voice'**
  String get recordVoice;

  /// No description provided for @playVoice.
  ///
  /// In en, this message translates to:
  /// **'Play Voice'**
  String get playVoice;

  /// No description provided for @pauseVoice.
  ///
  /// In en, this message translates to:
  /// **'Pause Voice'**
  String get pauseVoice;

  /// No description provided for @searchMessages.
  ///
  /// In en, this message translates to:
  /// **'Search Messages'**
  String get searchMessages;

  /// No description provided for @filterMessages.
  ///
  /// In en, this message translates to:
  /// **'Filter Messages'**
  String get filterMessages;

  /// No description provided for @chatSettings.
  ///
  /// In en, this message translates to:
  /// **'Chat Settings'**
  String get chatSettings;

  /// No description provided for @chatNotifications.
  ///
  /// In en, this message translates to:
  /// **'Chat Notifications'**
  String get chatNotifications;

  /// No description provided for @chatHistory.
  ///
  /// In en, this message translates to:
  /// **'Chat History'**
  String get chatHistory;

  /// No description provided for @clearChatHistory.
  ///
  /// In en, this message translates to:
  /// **'Clear Chat History'**
  String get clearChatHistory;

  /// No description provided for @exportChat.
  ///
  /// In en, this message translates to:
  /// **'Export Chat'**
  String get exportChat;

  /// No description provided for @groupChat.
  ///
  /// In en, this message translates to:
  /// **'Group Chat'**
  String get groupChat;

  /// No description provided for @createGroup.
  ///
  /// In en, this message translates to:
  /// **'Create Group'**
  String get createGroup;

  /// No description provided for @groupName.
  ///
  /// In en, this message translates to:
  /// **'Group Name'**
  String get groupName;

  /// No description provided for @groupMembers.
  ///
  /// In en, this message translates to:
  /// **'Group Members'**
  String get groupMembers;

  /// No description provided for @addMember.
  ///
  /// In en, this message translates to:
  /// **'Add Member'**
  String get addMember;

  /// No description provided for @removeMember.
  ///
  /// In en, this message translates to:
  /// **'Remove Member'**
  String get removeMember;

  /// No description provided for @leaveGroup.
  ///
  /// In en, this message translates to:
  /// **'Leave Group'**
  String get leaveGroup;

  /// No description provided for @groupAdmin.
  ///
  /// In en, this message translates to:
  /// **'Group Admin'**
  String get groupAdmin;

  /// No description provided for @groupSettings.
  ///
  /// In en, this message translates to:
  /// **'Group Settings'**
  String get groupSettings;

  /// No description provided for @notification.
  ///
  /// In en, this message translates to:
  /// **'Notification'**
  String get notification;

  /// No description provided for @newNotification.
  ///
  /// In en, this message translates to:
  /// **'New Notification'**
  String get newNotification;

  /// No description provided for @notificationList.
  ///
  /// In en, this message translates to:
  /// **'Notification List'**
  String get notificationList;

  /// No description provided for @readNotification.
  ///
  /// In en, this message translates to:
  /// **'Read Notification'**
  String get readNotification;

  /// No description provided for @unreadNotification.
  ///
  /// In en, this message translates to:
  /// **'Unread Notification'**
  String get unreadNotification;

  /// No description provided for @deleteNotification.
  ///
  /// In en, this message translates to:
  /// **'Delete Notification'**
  String get deleteNotification;

  /// No description provided for @clearNotifications.
  ///
  /// In en, this message translates to:
  /// **'Clear Notifications'**
  String get clearNotifications;

  /// No description provided for @notificationSettings.
  ///
  /// In en, this message translates to:
  /// **'Notification Settings'**
  String get notificationSettings;

  /// No description provided for @enableNotifications.
  ///
  /// In en, this message translates to:
  /// **'Enable Notifications'**
  String get enableNotifications;

  /// No description provided for @disableNotifications.
  ///
  /// In en, this message translates to:
  /// **'Disable Notifications'**
  String get disableNotifications;

  /// No description provided for @notificationSound.
  ///
  /// In en, this message translates to:
  /// **'Notification Sound'**
  String get notificationSound;

  /// No description provided for @notificationVibration.
  ///
  /// In en, this message translates to:
  /// **'Notification Vibration'**
  String get notificationVibration;

  /// No description provided for @pushNotifications.
  ///
  /// In en, this message translates to:
  /// **'Push Notifications'**
  String get pushNotifications;

  /// No description provided for @emailNotifications.
  ///
  /// In en, this message translates to:
  /// **'Email Notifications'**
  String get emailNotifications;

  /// No description provided for @smsNotifications.
  ///
  /// In en, this message translates to:
  /// **'SMS Notifications'**
  String get smsNotifications;

  /// No description provided for @alert.
  ///
  /// In en, this message translates to:
  /// **'Alert'**
  String get alert;

  /// No description provided for @newAlert.
  ///
  /// In en, this message translates to:
  /// **'New Alert'**
  String get newAlert;

  /// No description provided for @alertType.
  ///
  /// In en, this message translates to:
  /// **'Alert Type'**
  String get alertType;

  /// No description provided for @alertLevel.
  ///
  /// In en, this message translates to:
  /// **'Alert Level'**
  String get alertLevel;

  /// No description provided for @alertPriority.
  ///
  /// In en, this message translates to:
  /// **'Alert Priority'**
  String get alertPriority;

  /// No description provided for @criticalAlert.
  ///
  /// In en, this message translates to:
  /// **'Critical Alert'**
  String get criticalAlert;

  /// No description provided for @highPriorityAlert.
  ///
  /// In en, this message translates to:
  /// **'High Priority Alert'**
  String get highPriorityAlert;

  /// No description provided for @mediumPriorityAlert.
  ///
  /// In en, this message translates to:
  /// **'Medium Priority Alert'**
  String get mediumPriorityAlert;

  /// No description provided for @lowPriorityAlert.
  ///
  /// In en, this message translates to:
  /// **'Low Priority Alert'**
  String get lowPriorityAlert;

  /// No description provided for @weatherAlert_.
  ///
  /// In en, this message translates to:
  /// **'Weather Alert'**
  String get weatherAlert_;

  /// No description provided for @frostAlert.
  ///
  /// In en, this message translates to:
  /// **'Frost Alert'**
  String get frostAlert;

  /// No description provided for @heatAlert.
  ///
  /// In en, this message translates to:
  /// **'Heat Alert'**
  String get heatAlert;

  /// No description provided for @droughtAlert.
  ///
  /// In en, this message translates to:
  /// **'Drought Alert'**
  String get droughtAlert;

  /// No description provided for @floodAlert.
  ///
  /// In en, this message translates to:
  /// **'Flood Alert'**
  String get floodAlert;

  /// No description provided for @windAlert.
  ///
  /// In en, this message translates to:
  /// **'Wind Alert'**
  String get windAlert;

  /// No description provided for @stormAlert.
  ///
  /// In en, this message translates to:
  /// **'Storm Alert'**
  String get stormAlert;

  /// No description provided for @pestAlert.
  ///
  /// In en, this message translates to:
  /// **'Pest Alert'**
  String get pestAlert;

  /// No description provided for @diseaseAlert.
  ///
  /// In en, this message translates to:
  /// **'Disease Alert'**
  String get diseaseAlert;

  /// No description provided for @irrigationAlert.
  ///
  /// In en, this message translates to:
  /// **'Irrigation Alert'**
  String get irrigationAlert;

  /// No description provided for @fertilizerAlert.
  ///
  /// In en, this message translates to:
  /// **'Fertilizer Alert'**
  String get fertilizerAlert;

  /// No description provided for @sprayAlert.
  ///
  /// In en, this message translates to:
  /// **'Spray Alert'**
  String get sprayAlert;

  /// No description provided for @harvestAlert.
  ///
  /// In en, this message translates to:
  /// **'Harvest Alert'**
  String get harvestAlert;

  /// No description provided for @taskAlert.
  ///
  /// In en, this message translates to:
  /// **'Task Alert'**
  String get taskAlert;

  /// No description provided for @reminderAlert.
  ///
  /// In en, this message translates to:
  /// **'Reminder Alert'**
  String get reminderAlert;

  /// No description provided for @systemAlert.
  ///
  /// In en, this message translates to:
  /// **'System Alert'**
  String get systemAlert;

  /// No description provided for @maintenanceAlert.
  ///
  /// In en, this message translates to:
  /// **'Maintenance Alert'**
  String get maintenanceAlert;

  /// No description provided for @updateAlert.
  ///
  /// In en, this message translates to:
  /// **'Update Alert'**
  String get updateAlert;

  /// No description provided for @securityAlert.
  ///
  /// In en, this message translates to:
  /// **'Security Alert'**
  String get securityAlert;

  /// No description provided for @alertAcknowledge.
  ///
  /// In en, this message translates to:
  /// **'Acknowledge Alert'**
  String get alertAcknowledge;

  /// No description provided for @alertDismiss.
  ///
  /// In en, this message translates to:
  /// **'Dismiss Alert'**
  String get alertDismiss;

  /// No description provided for @alertSnooze.
  ///
  /// In en, this message translates to:
  /// **'Snooze Alert'**
  String get alertSnooze;

  /// No description provided for @alertHistory.
  ///
  /// In en, this message translates to:
  /// **'Alert History'**
  String get alertHistory;

  /// No description provided for @activeAlerts.
  ///
  /// In en, this message translates to:
  /// **'Active Alerts'**
  String get activeAlerts;

  /// No description provided for @resolvedAlerts.
  ///
  /// In en, this message translates to:
  /// **'Resolved Alerts'**
  String get resolvedAlerts;

  /// No description provided for @dismissedAlerts.
  ///
  /// In en, this message translates to:
  /// **'Dismissed Alerts'**
  String get dismissedAlerts;

  /// No description provided for @task.
  ///
  /// In en, this message translates to:
  /// **'Task'**
  String get task;

  /// No description provided for @newTask.
  ///
  /// In en, this message translates to:
  /// **'New Task'**
  String get newTask;

  /// No description provided for @createTask.
  ///
  /// In en, this message translates to:
  /// **'Create Task'**
  String get createTask;

  /// No description provided for @editTask.
  ///
  /// In en, this message translates to:
  /// **'Edit Task'**
  String get editTask;

  /// No description provided for @deleteTask.
  ///
  /// In en, this message translates to:
  /// **'Delete Task'**
  String get deleteTask;

  /// No description provided for @completeTask.
  ///
  /// In en, this message translates to:
  /// **'Complete Task'**
  String get completeTask;

  /// No description provided for @taskName.
  ///
  /// In en, this message translates to:
  /// **'Task Name'**
  String get taskName;

  /// No description provided for @taskTitle.
  ///
  /// In en, this message translates to:
  /// **'Task Title'**
  String get taskTitle;

  /// No description provided for @taskDescription.
  ///
  /// In en, this message translates to:
  /// **'Task Description'**
  String get taskDescription;

  /// No description provided for @taskType.
  ///
  /// In en, this message translates to:
  /// **'Task Type'**
  String get taskType;

  /// No description provided for @taskCategory.
  ///
  /// In en, this message translates to:
  /// **'Task Category'**
  String get taskCategory;

  /// No description provided for @taskStatus.
  ///
  /// In en, this message translates to:
  /// **'Task Status'**
  String get taskStatus;

  /// No description provided for @taskPriority.
  ///
  /// In en, this message translates to:
  /// **'Task Priority'**
  String get taskPriority;

  /// No description provided for @highPriority.
  ///
  /// In en, this message translates to:
  /// **'High Priority'**
  String get highPriority;

  /// No description provided for @mediumPriority.
  ///
  /// In en, this message translates to:
  /// **'Medium Priority'**
  String get mediumPriority;

  /// No description provided for @lowPriority.
  ///
  /// In en, this message translates to:
  /// **'Low Priority'**
  String get lowPriority;

  /// No description provided for @urgentTask.
  ///
  /// In en, this message translates to:
  /// **'Urgent Task'**
  String get urgentTask;

  /// No description provided for @normalTask.
  ///
  /// In en, this message translates to:
  /// **'Normal Task'**
  String get normalTask;

  /// No description provided for @taskDueDate.
  ///
  /// In en, this message translates to:
  /// **'Task Due Date'**
  String get taskDueDate;

  /// No description provided for @dueDate.
  ///
  /// In en, this message translates to:
  /// **'Due Date'**
  String get dueDate;

  /// No description provided for @dueTime.
  ///
  /// In en, this message translates to:
  /// **'Due Time'**
  String get dueTime;

  /// No description provided for @overdue.
  ///
  /// In en, this message translates to:
  /// **'Overdue'**
  String get overdue;

  /// No description provided for @dueSoon.
  ///
  /// In en, this message translates to:
  /// **'Due Soon'**
  String get dueSoon;

  /// No description provided for @dueToday.
  ///
  /// In en, this message translates to:
  /// **'Due Today'**
  String get dueToday;

  /// No description provided for @dueTomorrow.
  ///
  /// In en, this message translates to:
  /// **'Due Tomorrow'**
  String get dueTomorrow;

  /// No description provided for @dueThisWeek.
  ///
  /// In en, this message translates to:
  /// **'Due This Week'**
  String get dueThisWeek;

  /// No description provided for @taskAssignee.
  ///
  /// In en, this message translates to:
  /// **'Task Assignee'**
  String get taskAssignee;

  /// No description provided for @assignedTo.
  ///
  /// In en, this message translates to:
  /// **'Assigned To'**
  String get assignedTo;

  /// No description provided for @assignedBy.
  ///
  /// In en, this message translates to:
  /// **'Assigned By'**
  String get assignedBy;

  /// No description provided for @assignTask.
  ///
  /// In en, this message translates to:
  /// **'Assign Task'**
  String get assignTask;

  /// No description provided for @reassignTask.
  ///
  /// In en, this message translates to:
  /// **'Reassign Task'**
  String get reassignTask;

  /// No description provided for @unassignedTask.
  ///
  /// In en, this message translates to:
  /// **'Unassigned Task'**
  String get unassignedTask;

  /// No description provided for @taskProgress.
  ///
  /// In en, this message translates to:
  /// **'Task Progress'**
  String get taskProgress;

  /// No description provided for @progressPercentage.
  ///
  /// In en, this message translates to:
  /// **'Progress Percentage'**
  String get progressPercentage;

  /// No description provided for @notStartedTask.
  ///
  /// In en, this message translates to:
  /// **'Not Started'**
  String get notStartedTask;

  /// No description provided for @inProgressTask.
  ///
  /// In en, this message translates to:
  /// **'In Progress'**
  String get inProgressTask;

  /// No description provided for @completedTask.
  ///
  /// In en, this message translates to:
  /// **'Completed'**
  String get completedTask;

  /// No description provided for @cancelledTask.
  ///
  /// In en, this message translates to:
  /// **'Cancelled'**
  String get cancelledTask;

  /// No description provided for @onHoldTask.
  ///
  /// In en, this message translates to:
  /// **'On Hold'**
  String get onHoldTask;

  /// No description provided for @taskList.
  ///
  /// In en, this message translates to:
  /// **'Task List'**
  String get taskList;

  /// No description provided for @taskBoard.
  ///
  /// In en, this message translates to:
  /// **'Task Board'**
  String get taskBoard;

  /// No description provided for @taskCalendar.
  ///
  /// In en, this message translates to:
  /// **'Task Calendar'**
  String get taskCalendar;

  /// No description provided for @upcomingTasks.
  ///
  /// In en, this message translates to:
  /// **'Upcoming Tasks'**
  String get upcomingTasks;

  /// No description provided for @overdueTasks.
  ///
  /// In en, this message translates to:
  /// **'Overdue Tasks'**
  String get overdueTasks;

  /// No description provided for @completedTasks.
  ///
  /// In en, this message translates to:
  /// **'Completed Tasks'**
  String get completedTasks;

  /// No description provided for @activeTasks.
  ///
  /// In en, this message translates to:
  /// **'Active Tasks'**
  String get activeTasks;

  /// No description provided for @allTasks.
  ///
  /// In en, this message translates to:
  /// **'All Tasks'**
  String get allTasks;

  /// No description provided for @myTasksOnly.
  ///
  /// In en, this message translates to:
  /// **'My Tasks Only'**
  String get myTasksOnly;

  /// No description provided for @teamTasks.
  ///
  /// In en, this message translates to:
  /// **'Team Tasks'**
  String get teamTasks;

  /// No description provided for @taskReminder.
  ///
  /// In en, this message translates to:
  /// **'Task Reminder'**
  String get taskReminder;

  /// No description provided for @setReminder.
  ///
  /// In en, this message translates to:
  /// **'Set Reminder'**
  String get setReminder;

  /// No description provided for @reminderTime.
  ///
  /// In en, this message translates to:
  /// **'Reminder Time'**
  String get reminderTime;

  /// No description provided for @taskNotes.
  ///
  /// In en, this message translates to:
  /// **'Task Notes'**
  String get taskNotes;

  /// No description provided for @taskComments.
  ///
  /// In en, this message translates to:
  /// **'Task Comments'**
  String get taskComments;

  /// No description provided for @addComment.
  ///
  /// In en, this message translates to:
  /// **'Add Comment'**
  String get addComment;

  /// No description provided for @taskAttachments.
  ///
  /// In en, this message translates to:
  /// **'Task Attachments'**
  String get taskAttachments;

  /// No description provided for @addAttachment.
  ///
  /// In en, this message translates to:
  /// **'Add Attachment'**
  String get addAttachment;

  /// No description provided for @taskChecklist.
  ///
  /// In en, this message translates to:
  /// **'Task Checklist'**
  String get taskChecklist;

  /// No description provided for @subtask.
  ///
  /// In en, this message translates to:
  /// **'Subtask'**
  String get subtask;

  /// No description provided for @addSubtask.
  ///
  /// In en, this message translates to:
  /// **'Add Subtask'**
  String get addSubtask;

  /// No description provided for @parentTask.
  ///
  /// In en, this message translates to:
  /// **'Parent Task'**
  String get parentTask;

  /// No description provided for @taskDependency.
  ///
  /// In en, this message translates to:
  /// **'Task Dependency'**
  String get taskDependency;

  /// No description provided for @dependsOn.
  ///
  /// In en, this message translates to:
  /// **'Depends On'**
  String get dependsOn;

  /// No description provided for @blockedBy.
  ///
  /// In en, this message translates to:
  /// **'Blocked By'**
  String get blockedBy;

  /// No description provided for @taskTemplate.
  ///
  /// In en, this message translates to:
  /// **'Task Template'**
  String get taskTemplate;

  /// No description provided for @recurringTask.
  ///
  /// In en, this message translates to:
  /// **'Recurring Task'**
  String get recurringTask;

  /// No description provided for @repeatTask.
  ///
  /// In en, this message translates to:
  /// **'Repeat Task'**
  String get repeatTask;

  /// No description provided for @repeatDaily.
  ///
  /// In en, this message translates to:
  /// **'Daily'**
  String get repeatDaily;

  /// No description provided for @repeatWeekly.
  ///
  /// In en, this message translates to:
  /// **'Weekly'**
  String get repeatWeekly;

  /// No description provided for @repeatMonthly.
  ///
  /// In en, this message translates to:
  /// **'Monthly'**
  String get repeatMonthly;

  /// No description provided for @repeatYearly.
  ///
  /// In en, this message translates to:
  /// **'Yearly'**
  String get repeatYearly;

  /// No description provided for @taskFilter.
  ///
  /// In en, this message translates to:
  /// **'Task Filter'**
  String get taskFilter;

  /// No description provided for @filterByStatus.
  ///
  /// In en, this message translates to:
  /// **'Filter by Status'**
  String get filterByStatus;

  /// No description provided for @filterByPriority.
  ///
  /// In en, this message translates to:
  /// **'Filter by Priority'**
  String get filterByPriority;

  /// No description provided for @filterByDate.
  ///
  /// In en, this message translates to:
  /// **'Filter by Date'**
  String get filterByDate;

  /// No description provided for @filterByAssignee.
  ///
  /// In en, this message translates to:
  /// **'Filter by Assignee'**
  String get filterByAssignee;

  /// No description provided for @sortTasks.
  ///
  /// In en, this message translates to:
  /// **'Sort Tasks'**
  String get sortTasks;

  /// No description provided for @sortByDate.
  ///
  /// In en, this message translates to:
  /// **'Sort by Date'**
  String get sortByDate;

  /// No description provided for @sortByPriority.
  ///
  /// In en, this message translates to:
  /// **'Sort by Priority'**
  String get sortByPriority;

  /// No description provided for @sortByStatus.
  ///
  /// In en, this message translates to:
  /// **'Sort by Status'**
  String get sortByStatus;

  /// No description provided for @taskStatistics.
  ///
  /// In en, this message translates to:
  /// **'Task Statistics'**
  String get taskStatistics;

  /// No description provided for @taskCompletion.
  ///
  /// In en, this message translates to:
  /// **'Task Completion'**
  String get taskCompletion;

  /// No description provided for @completionRate.
  ///
  /// In en, this message translates to:
  /// **'Completion Rate'**
  String get completionRate;

  /// No description provided for @taskPerformance.
  ///
  /// In en, this message translates to:
  /// **'Task Performance'**
  String get taskPerformance;

  /// No description provided for @equipmentName.
  ///
  /// In en, this message translates to:
  /// **'Equipment Name'**
  String get equipmentName;

  /// No description provided for @equipmentType.
  ///
  /// In en, this message translates to:
  /// **'Equipment Type'**
  String get equipmentType;

  /// No description provided for @equipmentModel.
  ///
  /// In en, this message translates to:
  /// **'Equipment Model'**
  String get equipmentModel;

  /// No description provided for @equipmentBrand.
  ///
  /// In en, this message translates to:
  /// **'Equipment Brand'**
  String get equipmentBrand;

  /// No description provided for @equipmentStatus.
  ///
  /// In en, this message translates to:
  /// **'Equipment Status'**
  String get equipmentStatus;

  /// No description provided for @equipmentCondition.
  ///
  /// In en, this message translates to:
  /// **'Equipment Condition'**
  String get equipmentCondition;

  /// No description provided for @operationalEquipment.
  ///
  /// In en, this message translates to:
  /// **'Operational'**
  String get operationalEquipment;

  /// No description provided for @underMaintenance.
  ///
  /// In en, this message translates to:
  /// **'Under Maintenance'**
  String get underMaintenance;

  /// No description provided for @outOfService.
  ///
  /// In en, this message translates to:
  /// **'Out of Service'**
  String get outOfService;

  /// No description provided for @inUse.
  ///
  /// In en, this message translates to:
  /// **'In Use'**
  String get inUse;

  /// No description provided for @available_equipment.
  ///
  /// In en, this message translates to:
  /// **'Available'**
  String get available_equipment;

  /// No description provided for @reserved.
  ///
  /// In en, this message translates to:
  /// **'Reserved'**
  String get reserved;

  /// No description provided for @tractor.
  ///
  /// In en, this message translates to:
  /// **'Tractor'**
  String get tractor;

  /// No description provided for @plow.
  ///
  /// In en, this message translates to:
  /// **'Plow'**
  String get plow;

  /// No description provided for @harrow.
  ///
  /// In en, this message translates to:
  /// **'Harrow'**
  String get harrow;

  /// No description provided for @seeder.
  ///
  /// In en, this message translates to:
  /// **'Seeder'**
  String get seeder;

  /// No description provided for @planter.
  ///
  /// In en, this message translates to:
  /// **'Planter'**
  String get planter;

  /// No description provided for @cultivator.
  ///
  /// In en, this message translates to:
  /// **'Cultivator'**
  String get cultivator;

  /// No description provided for @fertilizer_spreader.
  ///
  /// In en, this message translates to:
  /// **'Fertilizer Spreader'**
  String get fertilizer_spreader;

  /// No description provided for @sprayer_equipment.
  ///
  /// In en, this message translates to:
  /// **'Sprayer'**
  String get sprayer_equipment;

  /// No description provided for @harvester.
  ///
  /// In en, this message translates to:
  /// **'Harvester'**
  String get harvester;

  /// No description provided for @combine.
  ///
  /// In en, this message translates to:
  /// **'Combine'**
  String get combine;

  /// No description provided for @trailer.
  ///
  /// In en, this message translates to:
  /// **'Trailer'**
  String get trailer;

  /// No description provided for @wagon.
  ///
  /// In en, this message translates to:
  /// **'Wagon'**
  String get wagon;

  /// No description provided for @irrigationSystem.
  ///
  /// In en, this message translates to:
  /// **'Irrigation System'**
  String get irrigationSystem;

  /// No description provided for @pump.
  ///
  /// In en, this message translates to:
  /// **'Pump'**
  String get pump;

  /// No description provided for @generator.
  ///
  /// In en, this message translates to:
  /// **'Generator'**
  String get generator;

  /// No description provided for @equipmentHours.
  ///
  /// In en, this message translates to:
  /// **'Equipment Hours'**
  String get equipmentHours;

  /// No description provided for @operatingHours.
  ///
  /// In en, this message translates to:
  /// **'Operating Hours'**
  String get operatingHours;

  /// No description provided for @totalHours.
  ///
  /// In en, this message translates to:
  /// **'Total Hours'**
  String get totalHours;

  /// No description provided for @hoursUsed.
  ///
  /// In en, this message translates to:
  /// **'Hours Used'**
  String get hoursUsed;

  /// No description provided for @hourMeter.
  ///
  /// In en, this message translates to:
  /// **'Hour Meter'**
  String get hourMeter;

  /// No description provided for @fuelConsumption.
  ///
  /// In en, this message translates to:
  /// **'Fuel Consumption'**
  String get fuelConsumption;

  /// No description provided for @fuelType.
  ///
  /// In en, this message translates to:
  /// **'Fuel Type'**
  String get fuelType;

  /// No description provided for @fuelLevel.
  ///
  /// In en, this message translates to:
  /// **'Fuel Level'**
  String get fuelLevel;

  /// No description provided for @refuel.
  ///
  /// In en, this message translates to:
  /// **'Refuel'**
  String get refuel;

  /// No description provided for @maintenance.
  ///
  /// In en, this message translates to:
  /// **'Maintenance'**
  String get maintenance;

  /// No description provided for @maintenanceSchedule.
  ///
  /// In en, this message translates to:
  /// **'Maintenance Schedule'**
  String get maintenanceSchedule;

  /// No description provided for @maintenanceHistory.
  ///
  /// In en, this message translates to:
  /// **'Maintenance History'**
  String get maintenanceHistory;

  /// No description provided for @maintenanceRecord.
  ///
  /// In en, this message translates to:
  /// **'Maintenance Record'**
  String get maintenanceRecord;

  /// No description provided for @nextMaintenance.
  ///
  /// In en, this message translates to:
  /// **'Next Maintenance'**
  String get nextMaintenance;

  /// No description provided for @dueMaintenance.
  ///
  /// In en, this message translates to:
  /// **'Due Maintenance'**
  String get dueMaintenance;

  /// No description provided for @overdueMaintenance.
  ///
  /// In en, this message translates to:
  /// **'Overdue Maintenance'**
  String get overdueMaintenance;

  /// No description provided for @preventiveMaintenance.
  ///
  /// In en, this message translates to:
  /// **'Preventive Maintenance'**
  String get preventiveMaintenance;

  /// No description provided for @correctiveMaintenance.
  ///
  /// In en, this message translates to:
  /// **'Corrective Maintenance'**
  String get correctiveMaintenance;

  /// No description provided for @emergencyRepair.
  ///
  /// In en, this message translates to:
  /// **'Emergency Repair'**
  String get emergencyRepair;

  /// No description provided for @repair.
  ///
  /// In en, this message translates to:
  /// **'Repair'**
  String get repair;

  /// No description provided for @repairCost.
  ///
  /// In en, this message translates to:
  /// **'Repair Cost'**
  String get repairCost;

  /// No description provided for @partsReplaced.
  ///
  /// In en, this message translates to:
  /// **'Parts Replaced'**
  String get partsReplaced;

  /// No description provided for @spareParts.
  ///
  /// In en, this message translates to:
  /// **'Spare Parts'**
  String get spareParts;

  /// No description provided for @equipmentOwner.
  ///
  /// In en, this message translates to:
  /// **'Equipment Owner'**
  String get equipmentOwner;

  /// No description provided for @equipmentOperator.
  ///
  /// In en, this message translates to:
  /// **'Equipment Operator'**
  String get equipmentOperator;

  /// No description provided for @licenseNumber.
  ///
  /// In en, this message translates to:
  /// **'License Number'**
  String get licenseNumber;

  /// No description provided for @equipmentLog.
  ///
  /// In en, this message translates to:
  /// **'Equipment Log'**
  String get equipmentLog;

  /// No description provided for @usageLog.
  ///
  /// In en, this message translates to:
  /// **'Usage Log'**
  String get usageLog;

  /// No description provided for @equipmentBooking.
  ///
  /// In en, this message translates to:
  /// **'Equipment Booking'**
  String get equipmentBooking;

  /// No description provided for @bookEquipment.
  ///
  /// In en, this message translates to:
  /// **'Book Equipment'**
  String get bookEquipment;

  /// No description provided for @bookingDate.
  ///
  /// In en, this message translates to:
  /// **'Booking Date'**
  String get bookingDate;

  /// No description provided for @bookingDuration.
  ///
  /// In en, this message translates to:
  /// **'Booking Duration'**
  String get bookingDuration;

  /// No description provided for @equipmentRental.
  ///
  /// In en, this message translates to:
  /// **'Equipment Rental'**
  String get equipmentRental;

  /// No description provided for @rentalRate.
  ///
  /// In en, this message translates to:
  /// **'Rental Rate'**
  String get rentalRate;

  /// No description provided for @rentalPeriod.
  ///
  /// In en, this message translates to:
  /// **'Rental Period'**
  String get rentalPeriod;

  /// No description provided for @rentalAgreement.
  ///
  /// In en, this message translates to:
  /// **'Rental Agreement'**
  String get rentalAgreement;

  /// No description provided for @equipmentInsurance.
  ///
  /// In en, this message translates to:
  /// **'Equipment Insurance'**
  String get equipmentInsurance;

  /// No description provided for @insurancePolicy.
  ///
  /// In en, this message translates to:
  /// **'Insurance Policy'**
  String get insurancePolicy;

  /// No description provided for @policyNumber.
  ///
  /// In en, this message translates to:
  /// **'Policy Number'**
  String get policyNumber;

  /// No description provided for @insuranceExpiry.
  ///
  /// In en, this message translates to:
  /// **'Insurance Expiry'**
  String get insuranceExpiry;

  /// No description provided for @equipmentValue.
  ///
  /// In en, this message translates to:
  /// **'Equipment Value'**
  String get equipmentValue;

  /// No description provided for @purchaseValue.
  ///
  /// In en, this message translates to:
  /// **'Purchase Value'**
  String get purchaseValue;

  /// No description provided for @currentValue.
  ///
  /// In en, this message translates to:
  /// **'Current Value'**
  String get currentValue;

  /// No description provided for @depreciation_equipment.
  ///
  /// In en, this message translates to:
  /// **'Depreciation'**
  String get depreciation_equipment;

  /// No description provided for @residualValue.
  ///
  /// In en, this message translates to:
  /// **'Residual Value'**
  String get residualValue;

  /// No description provided for @equipmentPhoto.
  ///
  /// In en, this message translates to:
  /// **'Equipment Photo'**
  String get equipmentPhoto;

  /// No description provided for @equipmentDocument.
  ///
  /// In en, this message translates to:
  /// **'Equipment Document'**
  String get equipmentDocument;

  /// No description provided for @manualDocument.
  ///
  /// In en, this message translates to:
  /// **'Manual'**
  String get manualDocument;

  /// No description provided for @warrantyDocument.
  ///
  /// In en, this message translates to:
  /// **'Warranty'**
  String get warrantyDocument;

  /// No description provided for @warrantyPeriod.
  ///
  /// In en, this message translates to:
  /// **'Warranty Period'**
  String get warrantyPeriod;

  /// No description provided for @warrantyExpiry.
  ///
  /// In en, this message translates to:
  /// **'Warranty Expiry'**
  String get warrantyExpiry;

  /// No description provided for @report.
  ///
  /// In en, this message translates to:
  /// **'Report'**
  String get report;

  /// No description provided for @generateReport.
  ///
  /// In en, this message translates to:
  /// **'Generate Report'**
  String get generateReport;

  /// No description provided for @viewReport.
  ///
  /// In en, this message translates to:
  /// **'View Report'**
  String get viewReport;

  /// No description provided for @downloadReport.
  ///
  /// In en, this message translates to:
  /// **'Download Report'**
  String get downloadReport;

  /// No description provided for @printReport.
  ///
  /// In en, this message translates to:
  /// **'Print Report'**
  String get printReport;

  /// No description provided for @shareReport.
  ///
  /// In en, this message translates to:
  /// **'Share Report'**
  String get shareReport;

  /// No description provided for @exportReport.
  ///
  /// In en, this message translates to:
  /// **'Export Report'**
  String get exportReport;

  /// No description provided for @reportType.
  ///
  /// In en, this message translates to:
  /// **'Report Type'**
  String get reportType;

  /// No description provided for @reportPeriod.
  ///
  /// In en, this message translates to:
  /// **'Report Period'**
  String get reportPeriod;

  /// No description provided for @reportDate.
  ///
  /// In en, this message translates to:
  /// **'Report Date'**
  String get reportDate;

  /// No description provided for @reportRange.
  ///
  /// In en, this message translates to:
  /// **'Report Range'**
  String get reportRange;

  /// No description provided for @customReport.
  ///
  /// In en, this message translates to:
  /// **'Custom Report'**
  String get customReport;

  /// No description provided for @standardReport.
  ///
  /// In en, this message translates to:
  /// **'Standard Report'**
  String get standardReport;

  /// No description provided for @summaryReport.
  ///
  /// In en, this message translates to:
  /// **'Summary Report'**
  String get summaryReport;

  /// No description provided for @detailedReport.
  ///
  /// In en, this message translates to:
  /// **'Detailed Report'**
  String get detailedReport;

  /// No description provided for @dailyReport.
  ///
  /// In en, this message translates to:
  /// **'Daily Report'**
  String get dailyReport;

  /// No description provided for @weeklyReport.
  ///
  /// In en, this message translates to:
  /// **'Weekly Report'**
  String get weeklyReport;

  /// No description provided for @monthlyReport.
  ///
  /// In en, this message translates to:
  /// **'Monthly Report'**
  String get monthlyReport;

  /// No description provided for @quarterlyReport.
  ///
  /// In en, this message translates to:
  /// **'Quarterly Report'**
  String get quarterlyReport;

  /// No description provided for @annualReport.
  ///
  /// In en, this message translates to:
  /// **'Annual Report'**
  String get annualReport;

  /// No description provided for @fieldReport.
  ///
  /// In en, this message translates to:
  /// **'Field Report'**
  String get fieldReport;

  /// No description provided for @cropReport.
  ///
  /// In en, this message translates to:
  /// **'Crop Report'**
  String get cropReport;

  /// No description provided for @weatherReport.
  ///
  /// In en, this message translates to:
  /// **'Weather Report'**
  String get weatherReport;

  /// No description provided for @yieldReport.
  ///
  /// In en, this message translates to:
  /// **'Yield Report'**
  String get yieldReport;

  /// No description provided for @financialReport.
  ///
  /// In en, this message translates to:
  /// **'Financial Report'**
  String get financialReport;

  /// No description provided for @performanceReport.
  ///
  /// In en, this message translates to:
  /// **'Performance Report'**
  String get performanceReport;

  /// No description provided for @comparisonReport.
  ///
  /// In en, this message translates to:
  /// **'Comparison Report'**
  String get comparisonReport;

  /// No description provided for @trendReport.
  ///
  /// In en, this message translates to:
  /// **'Trend Report'**
  String get trendReport;

  /// No description provided for @analysisReport.
  ///
  /// In en, this message translates to:
  /// **'Analysis Report'**
  String get analysisReport;

  /// No description provided for @chart.
  ///
  /// In en, this message translates to:
  /// **'Chart'**
  String get chart;

  /// No description provided for @graph.
  ///
  /// In en, this message translates to:
  /// **'Graph'**
  String get graph;

  /// No description provided for @barChart.
  ///
  /// In en, this message translates to:
  /// **'Bar Chart'**
  String get barChart;

  /// No description provided for @lineChart.
  ///
  /// In en, this message translates to:
  /// **'Line Chart'**
  String get lineChart;

  /// No description provided for @pieChart.
  ///
  /// In en, this message translates to:
  /// **'Pie Chart'**
  String get pieChart;

  /// No description provided for @areaChart.
  ///
  /// In en, this message translates to:
  /// **'Area Chart'**
  String get areaChart;

  /// No description provided for @scatterPlot.
  ///
  /// In en, this message translates to:
  /// **'Scatter Plot'**
  String get scatterPlot;

  /// No description provided for @histogram.
  ///
  /// In en, this message translates to:
  /// **'Histogram'**
  String get histogram;

  /// No description provided for @heatmap.
  ///
  /// In en, this message translates to:
  /// **'Heatmap'**
  String get heatmap;

  /// No description provided for @timeSeries.
  ///
  /// In en, this message translates to:
  /// **'Time Series'**
  String get timeSeries;

  /// No description provided for @trendLine.
  ///
  /// In en, this message translates to:
  /// **'Trend Line'**
  String get trendLine;

  /// No description provided for @dataVisualization.
  ///
  /// In en, this message translates to:
  /// **'Data Visualization'**
  String get dataVisualization;

  /// No description provided for @dataPoint.
  ///
  /// In en, this message translates to:
  /// **'Data Point'**
  String get dataPoint;

  /// No description provided for @dataSet.
  ///
  /// In en, this message translates to:
  /// **'Data Set'**
  String get dataSet;

  /// No description provided for @dataSource.
  ///
  /// In en, this message translates to:
  /// **'Data Source'**
  String get dataSource;

  /// No description provided for @dataRange.
  ///
  /// In en, this message translates to:
  /// **'Data Range'**
  String get dataRange;

  /// No description provided for @dataPeriod.
  ///
  /// In en, this message translates to:
  /// **'Data Period'**
  String get dataPeriod;

  /// No description provided for @metric.
  ///
  /// In en, this message translates to:
  /// **'Metric'**
  String get metric;

  /// No description provided for @kpi.
  ///
  /// In en, this message translates to:
  /// **'KPI'**
  String get kpi;

  /// No description provided for @indicator.
  ///
  /// In en, this message translates to:
  /// **'Indicator'**
  String get indicator;

  /// No description provided for @benchmark.
  ///
  /// In en, this message translates to:
  /// **'Benchmark'**
  String get benchmark;

  /// No description provided for @target.
  ///
  /// In en, this message translates to:
  /// **'Target'**
  String get target;

  /// No description provided for @actual.
  ///
  /// In en, this message translates to:
  /// **'Actual'**
  String get actual;

  /// No description provided for @variance_analytics.
  ///
  /// In en, this message translates to:
  /// **'Variance'**
  String get variance_analytics;

  /// No description provided for @deviation.
  ///
  /// In en, this message translates to:
  /// **'Deviation'**
  String get deviation;

  /// No description provided for @trend.
  ///
  /// In en, this message translates to:
  /// **'Trend'**
  String get trend;

  /// No description provided for @pattern.
  ///
  /// In en, this message translates to:
  /// **'Pattern'**
  String get pattern;

  /// No description provided for @correlation.
  ///
  /// In en, this message translates to:
  /// **'Correlation'**
  String get correlation;

  /// No description provided for @comparison.
  ///
  /// In en, this message translates to:
  /// **'Comparison'**
  String get comparison;

  /// No description provided for @forecast.
  ///
  /// In en, this message translates to:
  /// **'Forecast'**
  String get forecast;

  /// No description provided for @projection.
  ///
  /// In en, this message translates to:
  /// **'Projection'**
  String get projection;

  /// No description provided for @prediction.
  ///
  /// In en, this message translates to:
  /// **'Prediction'**
  String get prediction;

  /// No description provided for @estimation.
  ///
  /// In en, this message translates to:
  /// **'Estimation'**
  String get estimation;

  /// No description provided for @calculation.
  ///
  /// In en, this message translates to:
  /// **'Calculation'**
  String get calculation;

  /// No description provided for @aggregation.
  ///
  /// In en, this message translates to:
  /// **'Aggregation'**
  String get aggregation;

  /// No description provided for @summary.
  ///
  /// In en, this message translates to:
  /// **'Summary'**
  String get summary;

  /// No description provided for @overview.
  ///
  /// In en, this message translates to:
  /// **'Overview'**
  String get overview;

  /// No description provided for @insight.
  ///
  /// In en, this message translates to:
  /// **'Insight'**
  String get insight;

  /// No description provided for @finding.
  ///
  /// In en, this message translates to:
  /// **'Finding'**
  String get finding;

  /// No description provided for @recommendation.
  ///
  /// In en, this message translates to:
  /// **'Recommendation'**
  String get recommendation;

  /// No description provided for @conclusion.
  ///
  /// In en, this message translates to:
  /// **'Conclusion'**
  String get conclusion;

  /// No description provided for @myAccount.
  ///
  /// In en, this message translates to:
  /// **'My Account'**
  String get myAccount;

  /// No description provided for @editProfile.
  ///
  /// In en, this message translates to:
  /// **'Edit Profile'**
  String get editProfile;

  /// No description provided for @viewProfile.
  ///
  /// In en, this message translates to:
  /// **'View Profile'**
  String get viewProfile;

  /// No description provided for @profilePicture.
  ///
  /// In en, this message translates to:
  /// **'Profile Picture'**
  String get profilePicture;

  /// No description provided for @changePicture.
  ///
  /// In en, this message translates to:
  /// **'Change Picture'**
  String get changePicture;

  /// No description provided for @uploadPicture.
  ///
  /// In en, this message translates to:
  /// **'Upload Picture'**
  String get uploadPicture;

  /// No description provided for @removePicture.
  ///
  /// In en, this message translates to:
  /// **'Remove Picture'**
  String get removePicture;

  /// No description provided for @personalInformation.
  ///
  /// In en, this message translates to:
  /// **'Personal Information'**
  String get personalInformation;

  /// No description provided for @contactInformation.
  ///
  /// In en, this message translates to:
  /// **'Contact Information'**
  String get contactInformation;

  /// No description provided for @address.
  ///
  /// In en, this message translates to:
  /// **'Address'**
  String get address;

  /// No description provided for @streetAddress.
  ///
  /// In en, this message translates to:
  /// **'Street Address'**
  String get streetAddress;

  /// No description provided for @city.
  ///
  /// In en, this message translates to:
  /// **'City'**
  String get city;

  /// No description provided for @district.
  ///
  /// In en, this message translates to:
  /// **'District'**
  String get district;

  /// No description provided for @governorate.
  ///
  /// In en, this message translates to:
  /// **'Governorate'**
  String get governorate;

  /// No description provided for @country.
  ///
  /// In en, this message translates to:
  /// **'Country'**
  String get country;

  /// No description provided for @postalCode.
  ///
  /// In en, this message translates to:
  /// **'Postal Code'**
  String get postalCode;

  /// No description provided for @phone.
  ///
  /// In en, this message translates to:
  /// **'Phone'**
  String get phone;

  /// No description provided for @mobilePhone.
  ///
  /// In en, this message translates to:
  /// **'Mobile Phone'**
  String get mobilePhone;

  /// No description provided for @alternativePhone.
  ///
  /// In en, this message translates to:
  /// **'Alternative Phone'**
  String get alternativePhone;

  /// No description provided for @website.
  ///
  /// In en, this message translates to:
  /// **'Website'**
  String get website;

  /// No description provided for @biography.
  ///
  /// In en, this message translates to:
  /// **'Biography'**
  String get biography;

  /// No description provided for @bio.
  ///
  /// In en, this message translates to:
  /// **'Bio'**
  String get bio;

  /// No description provided for @language.
  ///
  /// In en, this message translates to:
  /// **'Language'**
  String get language;

  /// No description provided for @languagePreference.
  ///
  /// In en, this message translates to:
  /// **'Language Preference'**
  String get languagePreference;

  /// No description provided for @arabic.
  ///
  /// In en, this message translates to:
  /// **'Arabic'**
  String get arabic;

  /// No description provided for @english.
  ///
  /// In en, this message translates to:
  /// **'English'**
  String get english;

  /// No description provided for @dateFormat.
  ///
  /// In en, this message translates to:
  /// **'Date Format'**
  String get dateFormat;

  /// No description provided for @timeFormat.
  ///
  /// In en, this message translates to:
  /// **'Time Format'**
  String get timeFormat;

  /// No description provided for @numberFormat.
  ///
  /// In en, this message translates to:
  /// **'Number Format'**
  String get numberFormat;

  /// No description provided for @currency.
  ///
  /// In en, this message translates to:
  /// **'Currency'**
  String get currency;

  /// No description provided for @yemeniRial.
  ///
  /// In en, this message translates to:
  /// **'Yemeni Rial'**
  String get yemeniRial;

  /// No description provided for @usDollar.
  ///
  /// In en, this message translates to:
  /// **'US Dollar'**
  String get usDollar;

  /// No description provided for @accountType.
  ///
  /// In en, this message translates to:
  /// **'Account Type'**
  String get accountType;

  /// No description provided for @farmer.
  ///
  /// In en, this message translates to:
  /// **'Farmer'**
  String get farmer;

  /// No description provided for @agronomist.
  ///
  /// In en, this message translates to:
  /// **'Agronomist'**
  String get agronomist;

  /// No description provided for @supplier_.
  ///
  /// In en, this message translates to:
  /// **'Supplier'**
  String get supplier_;

  /// No description provided for @contractor.
  ///
  /// In en, this message translates to:
  /// **'Contractor'**
  String get contractor;

  /// No description provided for @organization.
  ///
  /// In en, this message translates to:
  /// **'Organization'**
  String get organization;

  /// No description provided for @company.
  ///
  /// In en, this message translates to:
  /// **'Company'**
  String get company;

  /// No description provided for @farmInformation.
  ///
  /// In en, this message translates to:
  /// **'Farm Information'**
  String get farmInformation;

  /// No description provided for @farmName.
  ///
  /// In en, this message translates to:
  /// **'Farm Name'**
  String get farmName;

  /// No description provided for @farmSize.
  ///
  /// In en, this message translates to:
  /// **'Farm Size'**
  String get farmSize;

  /// No description provided for @farmLocation.
  ///
  /// In en, this message translates to:
  /// **'Farm Location'**
  String get farmLocation;

  /// No description provided for @farmType.
  ///
  /// In en, this message translates to:
  /// **'Farm Type'**
  String get farmType;

  /// No description provided for @mainCrops.
  ///
  /// In en, this message translates to:
  /// **'Main Crops'**
  String get mainCrops;

  /// No description provided for @farmingPractices.
  ///
  /// In en, this message translates to:
  /// **'Farming Practices'**
  String get farmingPractices;

  /// No description provided for @organicFarming.
  ///
  /// In en, this message translates to:
  /// **'Organic Farming'**
  String get organicFarming;

  /// No description provided for @conventionalFarming.
  ///
  /// In en, this message translates to:
  /// **'Conventional Farming'**
  String get conventionalFarming;

  /// No description provided for @memberSince.
  ///
  /// In en, this message translates to:
  /// **'Member Since'**
  String get memberSince;

  /// No description provided for @registrationDate.
  ///
  /// In en, this message translates to:
  /// **'Registration Date'**
  String get registrationDate;

  /// No description provided for @lastLogin.
  ///
  /// In en, this message translates to:
  /// **'Last Login'**
  String get lastLogin;

  /// No description provided for @accountStatus.
  ///
  /// In en, this message translates to:
  /// **'Account Status'**
  String get accountStatus;

  /// No description provided for @activeAccount.
  ///
  /// In en, this message translates to:
  /// **'Active Account'**
  String get activeAccount;

  /// No description provided for @inactiveAccount.
  ///
  /// In en, this message translates to:
  /// **'Inactive Account'**
  String get inactiveAccount;

  /// No description provided for @suspendedAccount.
  ///
  /// In en, this message translates to:
  /// **'Suspended Account'**
  String get suspendedAccount;

  /// No description provided for @verifiedAccount.
  ///
  /// In en, this message translates to:
  /// **'Verified Account'**
  String get verifiedAccount;

  /// No description provided for @emailVerified.
  ///
  /// In en, this message translates to:
  /// **'Email Verified'**
  String get emailVerified;

  /// No description provided for @phoneVerified.
  ///
  /// In en, this message translates to:
  /// **'Phone Verified'**
  String get phoneVerified;

  /// No description provided for @identityVerified.
  ///
  /// In en, this message translates to:
  /// **'Identity Verified'**
  String get identityVerified;

  /// No description provided for @subscription.
  ///
  /// In en, this message translates to:
  /// **'Subscription'**
  String get subscription;

  /// No description provided for @subscriptionPlan.
  ///
  /// In en, this message translates to:
  /// **'Subscription Plan'**
  String get subscriptionPlan;

  /// No description provided for @freePlan.
  ///
  /// In en, this message translates to:
  /// **'Free Plan'**
  String get freePlan;

  /// No description provided for @basicPlan.
  ///
  /// In en, this message translates to:
  /// **'Basic Plan'**
  String get basicPlan;

  /// No description provided for @premiumPlan.
  ///
  /// In en, this message translates to:
  /// **'Premium Plan'**
  String get premiumPlan;

  /// No description provided for @enterprisePlan.
  ///
  /// In en, this message translates to:
  /// **'Enterprise Plan'**
  String get enterprisePlan;

  /// No description provided for @subscriptionStatus.
  ///
  /// In en, this message translates to:
  /// **'Subscription Status'**
  String get subscriptionStatus;

  /// No description provided for @subscriptionExpiry.
  ///
  /// In en, this message translates to:
  /// **'Subscription Expiry'**
  String get subscriptionExpiry;

  /// No description provided for @renewSubscription.
  ///
  /// In en, this message translates to:
  /// **'Renew Subscription'**
  String get renewSubscription;

  /// No description provided for @upgradeAccount.
  ///
  /// In en, this message translates to:
  /// **'Upgrade Account'**
  String get upgradeAccount;

  /// No description provided for @downgradeAccount.
  ///
  /// In en, this message translates to:
  /// **'Downgrade Account'**
  String get downgradeAccount;

  /// No description provided for @deleteAccount.
  ///
  /// In en, this message translates to:
  /// **'Delete Account'**
  String get deleteAccount;

  /// No description provided for @deactivateAccount.
  ///
  /// In en, this message translates to:
  /// **'Deactivate Account'**
  String get deactivateAccount;

  /// No description provided for @exportData.
  ///
  /// In en, this message translates to:
  /// **'Export Data'**
  String get exportData;

  /// No description provided for @dataPrivacy.
  ///
  /// In en, this message translates to:
  /// **'Data Privacy'**
  String get dataPrivacy;

  /// No description provided for @dataProtection.
  ///
  /// In en, this message translates to:
  /// **'Data Protection'**
  String get dataProtection;

  /// No description provided for @consentSettings.
  ///
  /// In en, this message translates to:
  /// **'Consent Settings'**
  String get consentSettings;

  /// No description provided for @generalSettings.
  ///
  /// In en, this message translates to:
  /// **'General Settings'**
  String get generalSettings;

  /// No description provided for @appSettings.
  ///
  /// In en, this message translates to:
  /// **'App Settings'**
  String get appSettings;

  /// No description provided for @displaySettings.
  ///
  /// In en, this message translates to:
  /// **'Display Settings'**
  String get displaySettings;

  /// No description provided for @theme.
  ///
  /// In en, this message translates to:
  /// **'Theme'**
  String get theme;

  /// No description provided for @lightTheme.
  ///
  /// In en, this message translates to:
  /// **'Light Theme'**
  String get lightTheme;

  /// No description provided for @darkTheme.
  ///
  /// In en, this message translates to:
  /// **'Dark Theme'**
  String get darkTheme;

  /// No description provided for @autoTheme.
  ///
  /// In en, this message translates to:
  /// **'Auto Theme'**
  String get autoTheme;

  /// No description provided for @fontSize.
  ///
  /// In en, this message translates to:
  /// **'Font Size'**
  String get fontSize;

  /// No description provided for @smallFont.
  ///
  /// In en, this message translates to:
  /// **'Small Font'**
  String get smallFont;

  /// No description provided for @mediumFont.
  ///
  /// In en, this message translates to:
  /// **'Medium Font'**
  String get mediumFont;

  /// No description provided for @largeFont.
  ///
  /// In en, this message translates to:
  /// **'Large Font'**
  String get largeFont;

  /// No description provided for @extraLargeFont.
  ///
  /// In en, this message translates to:
  /// **'Extra Large Font'**
  String get extraLargeFont;

  /// No description provided for @textDirection.
  ///
  /// In en, this message translates to:
  /// **'Text Direction'**
  String get textDirection;

  /// No description provided for @ltr.
  ///
  /// In en, this message translates to:
  /// **'Left to Right'**
  String get ltr;

  /// No description provided for @rtl.
  ///
  /// In en, this message translates to:
  /// **'Right to Left'**
  String get rtl;

  /// No description provided for @mapSettings.
  ///
  /// In en, this message translates to:
  /// **'Map Settings'**
  String get mapSettings;

  /// No description provided for @mapProvider.
  ///
  /// In en, this message translates to:
  /// **'Map Provider'**
  String get mapProvider;

  /// No description provided for @mapType.
  ///
  /// In en, this message translates to:
  /// **'Map Type'**
  String get mapType;

  /// No description provided for @mapZoom.
  ///
  /// In en, this message translates to:
  /// **'Map Zoom'**
  String get mapZoom;

  /// No description provided for @mapCenter.
  ///
  /// In en, this message translates to:
  /// **'Map Center'**
  String get mapCenter;

  /// No description provided for @showMyLocation.
  ///
  /// In en, this message translates to:
  /// **'Show My Location'**
  String get showMyLocation;

  /// No description provided for @offlineMaps.
  ///
  /// In en, this message translates to:
  /// **'Offline Maps'**
  String get offlineMaps;

  /// No description provided for @downloadMaps.
  ///
  /// In en, this message translates to:
  /// **'Download Maps'**
  String get downloadMaps;

  /// No description provided for @storageSettings.
  ///
  /// In en, this message translates to:
  /// **'Storage Settings'**
  String get storageSettings;

  /// No description provided for @storageUsed.
  ///
  /// In en, this message translates to:
  /// **'Storage Used'**
  String get storageUsed;

  /// No description provided for @storageAvailable.
  ///
  /// In en, this message translates to:
  /// **'Storage Available'**
  String get storageAvailable;

  /// No description provided for @clearCache.
  ///
  /// In en, this message translates to:
  /// **'Clear Cache'**
  String get clearCache;

  /// No description provided for @clearData.
  ///
  /// In en, this message translates to:
  /// **'Clear Data'**
  String get clearData;

  /// No description provided for @manageStorage.
  ///
  /// In en, this message translates to:
  /// **'Manage Storage'**
  String get manageStorage;

  /// No description provided for @syncSettings.
  ///
  /// In en, this message translates to:
  /// **'Sync Settings'**
  String get syncSettings;

  /// No description provided for @autoSync.
  ///
  /// In en, this message translates to:
  /// **'Auto Sync'**
  String get autoSync;

  /// No description provided for @syncInterval.
  ///
  /// In en, this message translates to:
  /// **'Sync Interval'**
  String get syncInterval;

  /// No description provided for @syncOnWifiOnly.
  ///
  /// In en, this message translates to:
  /// **'Sync on WiFi Only'**
  String get syncOnWifiOnly;

  /// No description provided for @syncNow.
  ///
  /// In en, this message translates to:
  /// **'Sync Now'**
  String get syncNow;

  /// No description provided for @lastSync.
  ///
  /// In en, this message translates to:
  /// **'Last Sync'**
  String get lastSync;

  /// No description provided for @syncStatus.
  ///
  /// In en, this message translates to:
  /// **'Sync Status'**
  String get syncStatus;

  /// No description provided for @syncSuccess.
  ///
  /// In en, this message translates to:
  /// **'Sync Success'**
  String get syncSuccess;

  /// No description provided for @syncFailed.
  ///
  /// In en, this message translates to:
  /// **'Sync Failed'**
  String get syncFailed;

  /// No description provided for @syncInProgress.
  ///
  /// In en, this message translates to:
  /// **'Sync in Progress'**
  String get syncInProgress;

  /// No description provided for @networkSettings.
  ///
  /// In en, this message translates to:
  /// **'Network Settings'**
  String get networkSettings;

  /// No description provided for @connectionType.
  ///
  /// In en, this message translates to:
  /// **'Connection Type'**
  String get connectionType;

  /// No description provided for @wifi.
  ///
  /// In en, this message translates to:
  /// **'WiFi'**
  String get wifi;

  /// No description provided for @mobileData.
  ///
  /// In en, this message translates to:
  /// **'Mobile Data'**
  String get mobileData;

  /// No description provided for @offlineMode.
  ///
  /// In en, this message translates to:
  /// **'Offline Mode'**
  String get offlineMode;

  /// No description provided for @dataUsage.
  ///
  /// In en, this message translates to:
  /// **'Data Usage'**
  String get dataUsage;

  /// No description provided for @dataSaver.
  ///
  /// In en, this message translates to:
  /// **'Data Saver'**
  String get dataSaver;

  /// No description provided for @locationSettings.
  ///
  /// In en, this message translates to:
  /// **'Location Settings'**
  String get locationSettings;

  /// No description provided for @enableLocation.
  ///
  /// In en, this message translates to:
  /// **'Enable Location'**
  String get enableLocation;

  /// No description provided for @locationPermission.
  ///
  /// In en, this message translates to:
  /// **'Location Permission'**
  String get locationPermission;

  /// No description provided for @locationAccuracy.
  ///
  /// In en, this message translates to:
  /// **'Location Accuracy'**
  String get locationAccuracy;

  /// No description provided for @highAccuracy.
  ///
  /// In en, this message translates to:
  /// **'High Accuracy'**
  String get highAccuracy;

  /// No description provided for @balancedAccuracy.
  ///
  /// In en, this message translates to:
  /// **'Balanced Accuracy'**
  String get balancedAccuracy;

  /// No description provided for @lowAccuracy.
  ///
  /// In en, this message translates to:
  /// **'Low Accuracy'**
  String get lowAccuracy;

  /// No description provided for @batterySaver.
  ///
  /// In en, this message translates to:
  /// **'Battery Saver'**
  String get batterySaver;

  /// No description provided for @securitySettings.
  ///
  /// In en, this message translates to:
  /// **'Security Settings'**
  String get securitySettings;

  /// No description provided for @biometricLogin.
  ///
  /// In en, this message translates to:
  /// **'Biometric Login'**
  String get biometricLogin;

  /// No description provided for @fingerprint.
  ///
  /// In en, this message translates to:
  /// **'Fingerprint'**
  String get fingerprint;

  /// No description provided for @faceRecognition.
  ///
  /// In en, this message translates to:
  /// **'Face Recognition'**
  String get faceRecognition;

  /// No description provided for @pinCode.
  ///
  /// In en, this message translates to:
  /// **'PIN Code'**
  String get pinCode;

  /// No description provided for @setPinCode.
  ///
  /// In en, this message translates to:
  /// **'Set PIN Code'**
  String get setPinCode;

  /// No description provided for @changePinCode.
  ///
  /// In en, this message translates to:
  /// **'Change PIN Code'**
  String get changePinCode;

  /// No description provided for @twoFactorAuth.
  ///
  /// In en, this message translates to:
  /// **'Two-Factor Authentication'**
  String get twoFactorAuth;

  /// No description provided for @enable2FA.
  ///
  /// In en, this message translates to:
  /// **'Enable 2FA'**
  String get enable2FA;

  /// No description provided for @disable2FA.
  ///
  /// In en, this message translates to:
  /// **'Disable 2FA'**
  String get disable2FA;

  /// No description provided for @sessionTimeout.
  ///
  /// In en, this message translates to:
  /// **'Session Timeout'**
  String get sessionTimeout;

  /// No description provided for @autoLogout.
  ///
  /// In en, this message translates to:
  /// **'Auto Logout'**
  String get autoLogout;

  /// No description provided for @deviceManagement.
  ///
  /// In en, this message translates to:
  /// **'Device Management'**
  String get deviceManagement;

  /// No description provided for @trustedDevices.
  ///
  /// In en, this message translates to:
  /// **'Trusted Devices'**
  String get trustedDevices;

  /// No description provided for @deviceName.
  ///
  /// In en, this message translates to:
  /// **'Device Name'**
  String get deviceName;

  /// No description provided for @deviceType.
  ///
  /// In en, this message translates to:
  /// **'Device Type'**
  String get deviceType;

  /// No description provided for @lastUsed.
  ///
  /// In en, this message translates to:
  /// **'Last Used'**
  String get lastUsed;

  /// No description provided for @removeDevice.
  ///
  /// In en, this message translates to:
  /// **'Remove Device'**
  String get removeDevice;

  /// No description provided for @permissionsSettings.
  ///
  /// In en, this message translates to:
  /// **'Permissions Settings'**
  String get permissionsSettings;

  /// No description provided for @cameraPermission.
  ///
  /// In en, this message translates to:
  /// **'Camera Permission'**
  String get cameraPermission;

  /// No description provided for @microphonePermission.
  ///
  /// In en, this message translates to:
  /// **'Microphone Permission'**
  String get microphonePermission;

  /// No description provided for @storagePermission.
  ///
  /// In en, this message translates to:
  /// **'Storage Permission'**
  String get storagePermission;

  /// No description provided for @contactsPermission.
  ///
  /// In en, this message translates to:
  /// **'Contacts Permission'**
  String get contactsPermission;

  /// No description provided for @grantPermission.
  ///
  /// In en, this message translates to:
  /// **'Grant Permission'**
  String get grantPermission;

  /// No description provided for @denyPermission.
  ///
  /// In en, this message translates to:
  /// **'Deny Permission'**
  String get denyPermission;

  /// No description provided for @backupSettings.
  ///
  /// In en, this message translates to:
  /// **'Backup Settings'**
  String get backupSettings;

  /// No description provided for @autoBackup.
  ///
  /// In en, this message translates to:
  /// **'Auto Backup'**
  String get autoBackup;

  /// No description provided for @backupNow.
  ///
  /// In en, this message translates to:
  /// **'Backup Now'**
  String get backupNow;

  /// No description provided for @lastBackup.
  ///
  /// In en, this message translates to:
  /// **'Last Backup'**
  String get lastBackup;

  /// No description provided for @backupLocation.
  ///
  /// In en, this message translates to:
  /// **'Backup Location'**
  String get backupLocation;

  /// No description provided for @restoreBackup.
  ///
  /// In en, this message translates to:
  /// **'Restore Backup'**
  String get restoreBackup;

  /// No description provided for @backupFrequency.
  ///
  /// In en, this message translates to:
  /// **'Backup Frequency'**
  String get backupFrequency;

  /// No description provided for @advancedSettings.
  ///
  /// In en, this message translates to:
  /// **'Advanced Settings'**
  String get advancedSettings;

  /// No description provided for @developerMode.
  ///
  /// In en, this message translates to:
  /// **'Developer Mode'**
  String get developerMode;

  /// No description provided for @debugMode.
  ///
  /// In en, this message translates to:
  /// **'Debug Mode'**
  String get debugMode;

  /// No description provided for @logSettings.
  ///
  /// In en, this message translates to:
  /// **'Log Settings'**
  String get logSettings;

  /// No description provided for @enableLogging.
  ///
  /// In en, this message translates to:
  /// **'Enable Logging'**
  String get enableLogging;

  /// No description provided for @viewLogs.
  ///
  /// In en, this message translates to:
  /// **'View Logs'**
  String get viewLogs;

  /// No description provided for @exportLogs.
  ///
  /// In en, this message translates to:
  /// **'Export Logs'**
  String get exportLogs;

  /// No description provided for @clearLogs.
  ///
  /// In en, this message translates to:
  /// **'Clear Logs'**
  String get clearLogs;

  /// No description provided for @resetSettings.
  ///
  /// In en, this message translates to:
  /// **'Reset Settings'**
  String get resetSettings;

  /// No description provided for @resetToDefaults.
  ///
  /// In en, this message translates to:
  /// **'Reset to Defaults'**
  String get resetToDefaults;

  /// No description provided for @factoryReset.
  ///
  /// In en, this message translates to:
  /// **'Factory Reset'**
  String get factoryReset;

  /// No description provided for @error_.
  ///
  /// In en, this message translates to:
  /// **'Error'**
  String get error_;

  /// No description provided for @errorOccurred.
  ///
  /// In en, this message translates to:
  /// **'An Error Occurred'**
  String get errorOccurred;

  /// No description provided for @errorMessage.
  ///
  /// In en, this message translates to:
  /// **'Error Message'**
  String get errorMessage;

  /// No description provided for @errorCode.
  ///
  /// In en, this message translates to:
  /// **'Error Code'**
  String get errorCode;

  /// No description provided for @errorDetails.
  ///
  /// In en, this message translates to:
  /// **'Error Details'**
  String get errorDetails;

  /// No description provided for @somethingWentWrong.
  ///
  /// In en, this message translates to:
  /// **'Something Went Wrong'**
  String get somethingWentWrong;

  /// No description provided for @tryAgain.
  ///
  /// In en, this message translates to:
  /// **'Try Again'**
  String get tryAgain;

  /// No description provided for @tryAgainLater.
  ///
  /// In en, this message translates to:
  /// **'Try Again Later'**
  String get tryAgainLater;

  /// No description provided for @contactSupport.
  ///
  /// In en, this message translates to:
  /// **'Contact Support'**
  String get contactSupport;

  /// No description provided for @reportError.
  ///
  /// In en, this message translates to:
  /// **'Report Error'**
  String get reportError;

  /// No description provided for @validationError.
  ///
  /// In en, this message translates to:
  /// **'Validation Error'**
  String get validationError;

  /// No description provided for @requiredField.
  ///
  /// In en, this message translates to:
  /// **'This field is required'**
  String get requiredField;

  /// No description provided for @invalidEmail.
  ///
  /// In en, this message translates to:
  /// **'Invalid Email'**
  String get invalidEmail;

  /// No description provided for @invalidPhone.
  ///
  /// In en, this message translates to:
  /// **'Invalid Phone Number'**
  String get invalidPhone;

  /// No description provided for @invalidPassword.
  ///
  /// In en, this message translates to:
  /// **'Invalid Password'**
  String get invalidPassword;

  /// No description provided for @passwordTooShort.
  ///
  /// In en, this message translates to:
  /// **'Password Too Short'**
  String get passwordTooShort;

  /// No description provided for @passwordsDoNotMatch.
  ///
  /// In en, this message translates to:
  /// **'Passwords Do Not Match'**
  String get passwordsDoNotMatch;

  /// No description provided for @invalidInput.
  ///
  /// In en, this message translates to:
  /// **'Invalid Input'**
  String get invalidInput;

  /// No description provided for @invalidFormat.
  ///
  /// In en, this message translates to:
  /// **'Invalid Format'**
  String get invalidFormat;

  /// No description provided for @invalidValue.
  ///
  /// In en, this message translates to:
  /// **'Invalid Value'**
  String get invalidValue;

  /// No description provided for @valueTooLow.
  ///
  /// In en, this message translates to:
  /// **'Value Too Low'**
  String get valueTooLow;

  /// No description provided for @valueTooHigh.
  ///
  /// In en, this message translates to:
  /// **'Value Too High'**
  String get valueTooHigh;

  /// No description provided for @invalidDate.
  ///
  /// In en, this message translates to:
  /// **'Invalid Date'**
  String get invalidDate;

  /// No description provided for @dateInPast.
  ///
  /// In en, this message translates to:
  /// **'Date in Past'**
  String get dateInPast;

  /// No description provided for @dateInFuture.
  ///
  /// In en, this message translates to:
  /// **'Date in Future'**
  String get dateInFuture;

  /// No description provided for @invalidRange.
  ///
  /// In en, this message translates to:
  /// **'Invalid Range'**
  String get invalidRange;

  /// No description provided for @fieldRequired.
  ///
  /// In en, this message translates to:
  /// **'Field Required'**
  String get fieldRequired;

  /// No description provided for @fieldEmpty.
  ///
  /// In en, this message translates to:
  /// **'Field Empty'**
  String get fieldEmpty;

  /// No description provided for @fieldTooLong.
  ///
  /// In en, this message translates to:
  /// **'Field Too Long'**
  String get fieldTooLong;

  /// No description provided for @fieldTooShort.
  ///
  /// In en, this message translates to:
  /// **'Field Too Short'**
  String get fieldTooShort;

  /// No description provided for @invalidCharacters.
  ///
  /// In en, this message translates to:
  /// **'Invalid Characters'**
  String get invalidCharacters;

  /// No description provided for @networkError.
  ///
  /// In en, this message translates to:
  /// **'Network Error'**
  String get networkError;

  /// No description provided for @connectionError.
  ///
  /// In en, this message translates to:
  /// **'Connection Error'**
  String get connectionError;

  /// No description provided for @noInternet.
  ///
  /// In en, this message translates to:
  /// **'No Internet Connection'**
  String get noInternet;

  /// No description provided for @noConnection.
  ///
  /// In en, this message translates to:
  /// **'No Connection'**
  String get noConnection;

  /// No description provided for @connectionLost.
  ///
  /// In en, this message translates to:
  /// **'Connection Lost'**
  String get connectionLost;

  /// No description provided for @connectionTimeout.
  ///
  /// In en, this message translates to:
  /// **'Connection Timeout'**
  String get connectionTimeout;

  /// No description provided for @serverError.
  ///
  /// In en, this message translates to:
  /// **'Server Error'**
  String get serverError;

  /// No description provided for @serverNotResponding.
  ///
  /// In en, this message translates to:
  /// **'Server Not Responding'**
  String get serverNotResponding;

  /// No description provided for @serviceUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Service Unavailable'**
  String get serviceUnavailable;

  /// No description provided for @maintenanceMode.
  ///
  /// In en, this message translates to:
  /// **'Maintenance Mode'**
  String get maintenanceMode;

  /// No description provided for @temporarilyUnavailable.
  ///
  /// In en, this message translates to:
  /// **'Temporarily Unavailable'**
  String get temporarilyUnavailable;

  /// No description provided for @notFound.
  ///
  /// In en, this message translates to:
  /// **'Not Found'**
  String get notFound;

  /// No description provided for @pageNotFound.
  ///
  /// In en, this message translates to:
  /// **'Page Not Found'**
  String get pageNotFound;

  /// No description provided for @resourceNotFound.
  ///
  /// In en, this message translates to:
  /// **'Resource Not Found'**
  String get resourceNotFound;

  /// No description provided for @fileNotFound.
  ///
  /// In en, this message translates to:
  /// **'File Not Found'**
  String get fileNotFound;

  /// No description provided for @dataNotFound.
  ///
  /// In en, this message translates to:
  /// **'Data Not Found'**
  String get dataNotFound;

  /// No description provided for @noDataAvailable.
  ///
  /// In en, this message translates to:
  /// **'No Data Available'**
  String get noDataAvailable;

  /// No description provided for @noResults.
  ///
  /// In en, this message translates to:
  /// **'No Results'**
  String get noResults;

  /// No description provided for @noResultsFound.
  ///
  /// In en, this message translates to:
  /// **'No Results Found'**
  String get noResultsFound;

  /// No description provided for @emptyList.
  ///
  /// In en, this message translates to:
  /// **'Empty List'**
  String get emptyList;

  /// No description provided for @unauthorized.
  ///
  /// In en, this message translates to:
  /// **'Unauthorized'**
  String get unauthorized;

  /// No description provided for @accessDenied.
  ///
  /// In en, this message translates to:
  /// **'Access Denied'**
  String get accessDenied;

  /// No description provided for @permissionDenied.
  ///
  /// In en, this message translates to:
  /// **'Permission Denied'**
  String get permissionDenied;

  /// No description provided for @insufficientPermissions.
  ///
  /// In en, this message translates to:
  /// **'Insufficient Permissions'**
  String get insufficientPermissions;

  /// No description provided for @sessionExpired.
  ///
  /// In en, this message translates to:
  /// **'Session Expired'**
  String get sessionExpired;

  /// No description provided for @loginRequired.
  ///
  /// In en, this message translates to:
  /// **'Login Required'**
  String get loginRequired;

  /// No description provided for @authenticationFailed.
  ///
  /// In en, this message translates to:
  /// **'Authentication Failed'**
  String get authenticationFailed;

  /// No description provided for @invalidCredentials.
  ///
  /// In en, this message translates to:
  /// **'Invalid Credentials'**
  String get invalidCredentials;

  /// No description provided for @accountLocked.
  ///
  /// In en, this message translates to:
  /// **'Account Locked'**
  String get accountLocked;

  /// No description provided for @accountDisabled.
  ///
  /// In en, this message translates to:
  /// **'Account Disabled'**
  String get accountDisabled;

  /// No description provided for @tooManyAttempts.
  ///
  /// In en, this message translates to:
  /// **'Too Many Attempts'**
  String get tooManyAttempts;

  /// No description provided for @rateLimitExceeded.
  ///
  /// In en, this message translates to:
  /// **'Rate Limit Exceeded'**
  String get rateLimitExceeded;

  /// No description provided for @requestTooLarge.
  ///
  /// In en, this message translates to:
  /// **'Request Too Large'**
  String get requestTooLarge;

  /// No description provided for @fileTooLarge.
  ///
  /// In en, this message translates to:
  /// **'File Too Large'**
  String get fileTooLarge;

  /// No description provided for @invalidFileType.
  ///
  /// In en, this message translates to:
  /// **'Invalid File Type'**
  String get invalidFileType;

  /// No description provided for @uploadFailed.
  ///
  /// In en, this message translates to:
  /// **'Upload Failed'**
  String get uploadFailed;

  /// No description provided for @downloadFailed.
  ///
  /// In en, this message translates to:
  /// **'Download Failed'**
  String get downloadFailed;

  /// No description provided for @saveFailed.
  ///
  /// In en, this message translates to:
  /// **'Save Failed'**
  String get saveFailed;

  /// No description provided for @deleteFailed.
  ///
  /// In en, this message translates to:
  /// **'Delete Failed'**
  String get deleteFailed;

  /// No description provided for @updateFailed.
  ///
  /// In en, this message translates to:
  /// **'Update Failed'**
  String get updateFailed;

  /// No description provided for @operationFailed.
  ///
  /// In en, this message translates to:
  /// **'Operation Failed'**
  String get operationFailed;

  /// No description provided for @syncFailed_.
  ///
  /// In en, this message translates to:
  /// **'Sync Failed'**
  String get syncFailed_;

  /// No description provided for @syncConflict.
  ///
  /// In en, this message translates to:
  /// **'Sync Conflict'**
  String get syncConflict;

  /// No description provided for @dataCorrupted.
  ///
  /// In en, this message translates to:
  /// **'Data Corrupted'**
  String get dataCorrupted;

  /// No description provided for @databaseError.
  ///
  /// In en, this message translates to:
  /// **'Database Error'**
  String get databaseError;

  /// No description provided for @unknownError.
  ///
  /// In en, this message translates to:
  /// **'Unknown Error'**
  String get unknownError;

  /// No description provided for @unexpectedError.
  ///
  /// In en, this message translates to:
  /// **'Unexpected Error'**
  String get unexpectedError;

  /// No description provided for @areYouSure.
  ///
  /// In en, this message translates to:
  /// **'Are You Sure?'**
  String get areYouSure;

  /// No description provided for @confirmAction.
  ///
  /// In en, this message translates to:
  /// **'Confirm Action'**
  String get confirmAction;

  /// No description provided for @confirmDelete.
  ///
  /// In en, this message translates to:
  /// **'Confirm Delete'**
  String get confirmDelete;

  /// No description provided for @confirmDeleteMessage.
  ///
  /// In en, this message translates to:
  /// **'Are you sure you want to delete this item?'**
  String get confirmDeleteMessage;

  /// No description provided for @cannotBeUndone.
  ///
  /// In en, this message translates to:
  /// **'This action cannot be undone'**
  String get cannotBeUndone;

  /// No description provided for @permanentAction.
  ///
  /// In en, this message translates to:
  /// **'Permanent Action'**
  String get permanentAction;

  /// No description provided for @confirmLogout.
  ///
  /// In en, this message translates to:
  /// **'Confirm Logout'**
  String get confirmLogout;

  /// No description provided for @confirmLogoutMessage.
  ///
  /// In en, this message translates to:
  /// **'Do you want to logout?'**
  String get confirmLogoutMessage;

  /// No description provided for @confirmCancel.
  ///
  /// In en, this message translates to:
  /// **'Confirm Cancel'**
  String get confirmCancel;

  /// No description provided for @confirmCancelMessage.
  ///
  /// In en, this message translates to:
  /// **'Do you want to cancel the changes?'**
  String get confirmCancelMessage;

  /// No description provided for @unsavedChanges.
  ///
  /// In en, this message translates to:
  /// **'Unsaved Changes'**
  String get unsavedChanges;

  /// No description provided for @unsavedChangesMessage.
  ///
  /// In en, this message translates to:
  /// **'You have unsaved changes. Do you want to save?'**
  String get unsavedChangesMessage;

  /// No description provided for @discardChanges.
  ///
  /// In en, this message translates to:
  /// **'Discard Changes'**
  String get discardChanges;

  /// No description provided for @saveChanges.
  ///
  /// In en, this message translates to:
  /// **'Save Changes'**
  String get saveChanges;

  /// No description provided for @confirmExit.
  ///
  /// In en, this message translates to:
  /// **'Confirm Exit'**
  String get confirmExit;

  /// No description provided for @confirmExitMessage.
  ///
  /// In en, this message translates to:
  /// **'Do you want to exit?'**
  String get confirmExitMessage;

  /// No description provided for @confirmOverwrite.
  ///
  /// In en, this message translates to:
  /// **'Confirm Overwrite'**
  String get confirmOverwrite;

  /// No description provided for @confirmOverwriteMessage.
  ///
  /// In en, this message translates to:
  /// **'File already exists. Do you want to overwrite it?'**
  String get confirmOverwriteMessage;

  /// No description provided for @confirmReplace.
  ///
  /// In en, this message translates to:
  /// **'Confirm Replace'**
  String get confirmReplace;

  /// No description provided for @confirmReplaceMessage.
  ///
  /// In en, this message translates to:
  /// **'Do you want to replace the current item?'**
  String get confirmReplaceMessage;

  /// No description provided for @confirmReset.
  ///
  /// In en, this message translates to:
  /// **'Confirm Reset'**
  String get confirmReset;

  /// No description provided for @confirmResetMessage.
  ///
  /// In en, this message translates to:
  /// **'Do you want to reset settings to defaults?'**
  String get confirmResetMessage;

  /// No description provided for @confirmClear.
  ///
  /// In en, this message translates to:
  /// **'Confirm Clear'**
  String get confirmClear;

  /// No description provided for @confirmClearMessage.
  ///
  /// In en, this message translates to:
  /// **'Do you want to clear all data?'**
  String get confirmClearMessage;

  /// No description provided for @successMessage.
  ///
  /// In en, this message translates to:
  /// **'Success Message'**
  String get successMessage;

  /// No description provided for @operationSuccessful.
  ///
  /// In en, this message translates to:
  /// **'Operation Successful'**
  String get operationSuccessful;

  /// No description provided for @savedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Saved Successfully'**
  String get savedSuccessfully;

  /// No description provided for @deletedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Deleted Successfully'**
  String get deletedSuccessfully;

  /// No description provided for @updatedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Updated Successfully'**
  String get updatedSuccessfully;

  /// No description provided for @createdSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Created Successfully'**
  String get createdSuccessfully;

  /// No description provided for @uploadedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Uploaded Successfully'**
  String get uploadedSuccessfully;

  /// No description provided for @downloadedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Downloaded Successfully'**
  String get downloadedSuccessfully;

  /// No description provided for @sentSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Sent Successfully'**
  String get sentSuccessfully;

  /// No description provided for @syncedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Synced Successfully'**
  String get syncedSuccessfully;

  /// No description provided for @completedSuccessfully.
  ///
  /// In en, this message translates to:
  /// **'Completed Successfully'**
  String get completedSuccessfully;

  /// No description provided for @actionCompleted.
  ///
  /// In en, this message translates to:
  /// **'Action Completed'**
  String get actionCompleted;

  /// No description provided for @taskCompleted.
  ///
  /// In en, this message translates to:
  /// **'Task Completed'**
  String get taskCompleted;

  /// No description provided for @processingComplete.
  ///
  /// In en, this message translates to:
  /// **'Processing Complete'**
  String get processingComplete;

  /// No description provided for @thankyou.
  ///
  /// In en, this message translates to:
  /// **'Thank You'**
  String get thankyou;

  /// No description provided for @welcomeMessage.
  ///
  /// In en, this message translates to:
  /// **'Welcome'**
  String get welcomeMessage;

  /// No description provided for @goodMorning.
  ///
  /// In en, this message translates to:
  /// **'Good Morning'**
  String get goodMorning;

  /// No description provided for @goodAfternoon.
  ///
  /// In en, this message translates to:
  /// **'Good Afternoon'**
  String get goodAfternoon;

  /// No description provided for @goodEvening.
  ///
  /// In en, this message translates to:
  /// **'Good Evening'**
  String get goodEvening;

  /// No description provided for @goodNight.
  ///
  /// In en, this message translates to:
  /// **'Good Night'**
  String get goodNight;

  /// No description provided for @hectare.
  ///
  /// In en, this message translates to:
  /// **'Hectare'**
  String get hectare;

  /// No description provided for @hectares.
  ///
  /// In en, this message translates to:
  /// **'Hectares'**
  String get hectares;

  /// No description provided for @acre.
  ///
  /// In en, this message translates to:
  /// **'Acre'**
  String get acre;

  /// No description provided for @acres.
  ///
  /// In en, this message translates to:
  /// **'Acres'**
  String get acres;

  /// No description provided for @squareMeter.
  ///
  /// In en, this message translates to:
  /// **'Square Meter'**
  String get squareMeter;

  /// No description provided for @squareMeters.
  ///
  /// In en, this message translates to:
  /// **'Square Meters'**
  String get squareMeters;

  /// No description provided for @squareKilometer.
  ///
  /// In en, this message translates to:
  /// **'Square Kilometer'**
  String get squareKilometer;

  /// No description provided for @squareKilometers.
  ///
  /// In en, this message translates to:
  /// **'Square Kilometers'**
  String get squareKilometers;

  /// No description provided for @kilometer.
  ///
  /// In en, this message translates to:
  /// **'Kilometer'**
  String get kilometer;

  /// No description provided for @kilometers.
  ///
  /// In en, this message translates to:
  /// **'Kilometers'**
  String get kilometers;

  /// No description provided for @meter.
  ///
  /// In en, this message translates to:
  /// **'Meter'**
  String get meter;

  /// No description provided for @meters.
  ///
  /// In en, this message translates to:
  /// **'Meters'**
  String get meters;

  /// No description provided for @centimeter.
  ///
  /// In en, this message translates to:
  /// **'Centimeter'**
  String get centimeter;

  /// No description provided for @centimeters.
  ///
  /// In en, this message translates to:
  /// **'Centimeters'**
  String get centimeters;

  /// No description provided for @millimeter.
  ///
  /// In en, this message translates to:
  /// **'Millimeter'**
  String get millimeter;

  /// No description provided for @millimeters.
  ///
  /// In en, this message translates to:
  /// **'Millimeters'**
  String get millimeters;

  /// No description provided for @kilogram.
  ///
  /// In en, this message translates to:
  /// **'Kilogram'**
  String get kilogram;

  /// No description provided for @kilograms.
  ///
  /// In en, this message translates to:
  /// **'Kilograms'**
  String get kilograms;

  /// No description provided for @ton.
  ///
  /// In en, this message translates to:
  /// **'Ton'**
  String get ton;

  /// No description provided for @tons.
  ///
  /// In en, this message translates to:
  /// **'Tons'**
  String get tons;

  /// No description provided for @gram.
  ///
  /// In en, this message translates to:
  /// **'Gram'**
  String get gram;

  /// No description provided for @grams.
  ///
  /// In en, this message translates to:
  /// **'Grams'**
  String get grams;

  /// No description provided for @liter.
  ///
  /// In en, this message translates to:
  /// **'Liter'**
  String get liter;

  /// No description provided for @liters.
  ///
  /// In en, this message translates to:
  /// **'Liters'**
  String get liters;

  /// No description provided for @milliliter.
  ///
  /// In en, this message translates to:
  /// **'Milliliter'**
  String get milliliter;

  /// No description provided for @milliliters.
  ///
  /// In en, this message translates to:
  /// **'Milliliters'**
  String get milliliters;

  /// No description provided for @cubicMeter.
  ///
  /// In en, this message translates to:
  /// **'Cubic Meter'**
  String get cubicMeter;

  /// No description provided for @cubicMeters.
  ///
  /// In en, this message translates to:
  /// **'Cubic Meters'**
  String get cubicMeters;

  /// No description provided for @celsius.
  ///
  /// In en, this message translates to:
  /// **'Celsius'**
  String get celsius;

  /// No description provided for @fahrenheit.
  ///
  /// In en, this message translates to:
  /// **'Fahrenheit'**
  String get fahrenheit;

  /// No description provided for @kelvin.
  ///
  /// In en, this message translates to:
  /// **'Kelvin'**
  String get kelvin;

  /// No description provided for @percent.
  ///
  /// In en, this message translates to:
  /// **'Percent'**
  String get percent;

  /// No description provided for @percentage_.
  ///
  /// In en, this message translates to:
  /// **'Percentage'**
  String get percentage_;

  /// No description provided for @kmPerHour.
  ///
  /// In en, this message translates to:
  /// **'km/h'**
  String get kmPerHour;

  /// No description provided for @meterPerSecond.
  ///
  /// In en, this message translates to:
  /// **'m/s'**
  String get meterPerSecond;

  /// No description provided for @milesPerHour.
  ///
  /// In en, this message translates to:
  /// **'mph'**
  String get milesPerHour;

  /// No description provided for @millimetersPerDay.
  ///
  /// In en, this message translates to:
  /// **'mm/day'**
  String get millimetersPerDay;

  /// No description provided for @millimetersPerHour.
  ///
  /// In en, this message translates to:
  /// **'mm/hour'**
  String get millimetersPerHour;

  /// No description provided for @kgPerHectare.
  ///
  /// In en, this message translates to:
  /// **'kg/ha'**
  String get kgPerHectare;

  /// No description provided for @tonsPerHectare.
  ///
  /// In en, this message translates to:
  /// **'tons/ha'**
  String get tonsPerHectare;

  /// No description provided for @litersPerHectare.
  ///
  /// In en, this message translates to:
  /// **'L/ha'**
  String get litersPerHectare;

  /// No description provided for @partsPerMillion.
  ///
  /// In en, this message translates to:
  /// **'Parts Per Million'**
  String get partsPerMillion;

  /// No description provided for @ppm.
  ///
  /// In en, this message translates to:
  /// **'ppm'**
  String get ppm;

  /// No description provided for @ph.
  ///
  /// In en, this message translates to:
  /// **'pH'**
  String get ph;

  /// No description provided for @wattPerSquareMeter.
  ///
  /// In en, this message translates to:
  /// **'W/m²'**
  String get wattPerSquareMeter;

  /// No description provided for @joule.
  ///
  /// In en, this message translates to:
  /// **'Joule'**
  String get joule;

  /// No description provided for @pascal.
  ///
  /// In en, this message translates to:
  /// **'Pascal'**
  String get pascal;

  /// No description provided for @bar.
  ///
  /// In en, this message translates to:
  /// **'Bar'**
  String get bar;

  /// No description provided for @millibar.
  ///
  /// In en, this message translates to:
  /// **'Millibar'**
  String get millibar;

  /// No description provided for @microSiemens.
  ///
  /// In en, this message translates to:
  /// **'Microsiemens'**
  String get microSiemens;

  /// No description provided for @dS_m.
  ///
  /// In en, this message translates to:
  /// **'dS/m'**
  String get dS_m;

  /// No description provided for @ec.
  ///
  /// In en, this message translates to:
  /// **'EC'**
  String get ec;

  /// No description provided for @all.
  ///
  /// In en, this message translates to:
  /// **'All'**
  String get all;

  /// No description provided for @none.
  ///
  /// In en, this message translates to:
  /// **'None'**
  String get none;

  /// No description provided for @other.
  ///
  /// In en, this message translates to:
  /// **'Other'**
  String get other;

  /// No description provided for @others.
  ///
  /// In en, this message translates to:
  /// **'Others'**
  String get others;

  /// No description provided for @unknown.
  ///
  /// In en, this message translates to:
  /// **'Unknown'**
  String get unknown;

  /// No description provided for @notApplicable.
  ///
  /// In en, this message translates to:
  /// **'Not Applicable'**
  String get notApplicable;

  /// No description provided for @na.
  ///
  /// In en, this message translates to:
  /// **'N/A'**
  String get na;

  /// No description provided for @tbd.
  ///
  /// In en, this message translates to:
  /// **'TBD'**
  String get tbd;

  /// No description provided for @comingSoon.
  ///
  /// In en, this message translates to:
  /// **'Coming Soon'**
  String get comingSoon;

  /// No description provided for @underConstruction.
  ///
  /// In en, this message translates to:
  /// **'Under Construction'**
  String get underConstruction;

  /// No description provided for @beta.
  ///
  /// In en, this message translates to:
  /// **'Beta'**
  String get beta;

  /// No description provided for @newStatus.
  ///
  /// In en, this message translates to:
  /// **'New'**
  String get newStatus;

  /// No description provided for @updated.
  ///
  /// In en, this message translates to:
  /// **'Updated'**
  String get updated;

  /// No description provided for @featured.
  ///
  /// In en, this message translates to:
  /// **'Featured'**
  String get featured;

  /// No description provided for @popular.
  ///
  /// In en, this message translates to:
  /// **'Popular'**
  String get popular;

  /// No description provided for @recommended.
  ///
  /// In en, this message translates to:
  /// **'Recommended'**
  String get recommended;

  /// No description provided for @optional.
  ///
  /// In en, this message translates to:
  /// **'Optional'**
  String get optional;

  /// No description provided for @required_.
  ///
  /// In en, this message translates to:
  /// **'Required'**
  String get required_;

  /// No description provided for @mandatory.
  ///
  /// In en, this message translates to:
  /// **'Mandatory'**
  String get mandatory;

  /// No description provided for @defaultValue.
  ///
  /// In en, this message translates to:
  /// **'Default'**
  String get defaultValue;

  /// No description provided for @custom.
  ///
  /// In en, this message translates to:
  /// **'Custom'**
  String get custom;

  /// No description provided for @automatic.
  ///
  /// In en, this message translates to:
  /// **'Automatic'**
  String get automatic;

  /// No description provided for @manual.
  ///
  /// In en, this message translates to:
  /// **'Manual'**
  String get manual;

  /// No description provided for @private.
  ///
  /// In en, this message translates to:
  /// **'Private'**
  String get private;

  /// No description provided for @public.
  ///
  /// In en, this message translates to:
  /// **'Public'**
  String get public;

  /// No description provided for @shared.
  ///
  /// In en, this message translates to:
  /// **'Shared'**
  String get shared;

  /// No description provided for @personal.
  ///
  /// In en, this message translates to:
  /// **'Personal'**
  String get personal;

  /// No description provided for @professional.
  ///
  /// In en, this message translates to:
  /// **'Professional'**
  String get professional;

  /// No description provided for @business.
  ///
  /// In en, this message translates to:
  /// **'Business'**
  String get business;

  /// No description provided for @individual.
  ///
  /// In en, this message translates to:
  /// **'Individual'**
  String get individual;

  /// No description provided for @team.
  ///
  /// In en, this message translates to:
  /// **'Team'**
  String get team;

  /// No description provided for @group.
  ///
  /// In en, this message translates to:
  /// **'Group'**
  String get group;

  /// No description provided for @member.
  ///
  /// In en, this message translates to:
  /// **'Member'**
  String get member;

  /// No description provided for @members.
  ///
  /// In en, this message translates to:
  /// **'Members'**
  String get members;

  /// No description provided for @owner.
  ///
  /// In en, this message translates to:
  /// **'Owner'**
  String get owner;

  /// No description provided for @admin.
  ///
  /// In en, this message translates to:
  /// **'Admin'**
  String get admin;

  /// No description provided for @administrator.
  ///
  /// In en, this message translates to:
  /// **'Administrator'**
  String get administrator;

  /// No description provided for @user.
  ///
  /// In en, this message translates to:
  /// **'User'**
  String get user;

  /// No description provided for @users.
  ///
  /// In en, this message translates to:
  /// **'Users'**
  String get users;

  /// No description provided for @guest.
  ///
  /// In en, this message translates to:
  /// **'Guest'**
  String get guest;

  /// No description provided for @visitor.
  ///
  /// In en, this message translates to:
  /// **'Visitor'**
  String get visitor;

  /// No description provided for @support.
  ///
  /// In en, this message translates to:
  /// **'Support'**
  String get support;

  /// No description provided for @helpCenter.
  ///
  /// In en, this message translates to:
  /// **'Help Center'**
  String get helpCenter;

  /// No description provided for @documentation.
  ///
  /// In en, this message translates to:
  /// **'Documentation'**
  String get documentation;

  /// No description provided for @tutorial.
  ///
  /// In en, this message translates to:
  /// **'Tutorial'**
  String get tutorial;

  /// No description provided for @guide.
  ///
  /// In en, this message translates to:
  /// **'Guide'**
  String get guide;

  /// No description provided for @faq.
  ///
  /// In en, this message translates to:
  /// **'FAQ'**
  String get faq;

  /// No description provided for @contactUs.
  ///
  /// In en, this message translates to:
  /// **'Contact Us'**
  String get contactUs;

  /// No description provided for @sendFeedback.
  ///
  /// In en, this message translates to:
  /// **'Send Feedback'**
  String get sendFeedback;

  /// No description provided for @reportBug.
  ///
  /// In en, this message translates to:
  /// **'Report Bug'**
  String get reportBug;

  /// No description provided for @requestFeature.
  ///
  /// In en, this message translates to:
  /// **'Request Feature'**
  String get requestFeature;

  /// No description provided for @rateApp.
  ///
  /// In en, this message translates to:
  /// **'Rate App'**
  String get rateApp;

  /// No description provided for @leaveReview.
  ///
  /// In en, this message translates to:
  /// **'Leave Review'**
  String get leaveReview;

  /// No description provided for @shareApp.
  ///
  /// In en, this message translates to:
  /// **'Share App'**
  String get shareApp;

  /// No description provided for @inviteFriends.
  ///
  /// In en, this message translates to:
  /// **'Invite Friends'**
  String get inviteFriends;

  /// No description provided for @socialMedia.
  ///
  /// In en, this message translates to:
  /// **'Social Media'**
  String get socialMedia;

  /// No description provided for @facebook.
  ///
  /// In en, this message translates to:
  /// **'Facebook'**
  String get facebook;

  /// No description provided for @twitter.
  ///
  /// In en, this message translates to:
  /// **'Twitter'**
  String get twitter;

  /// No description provided for @instagram.
  ///
  /// In en, this message translates to:
  /// **'Instagram'**
  String get instagram;

  /// No description provided for @youtube.
  ///
  /// In en, this message translates to:
  /// **'YouTube'**
  String get youtube;

  /// No description provided for @linkedin.
  ///
  /// In en, this message translates to:
  /// **'LinkedIn'**
  String get linkedin;

  /// No description provided for @whatsapp.
  ///
  /// In en, this message translates to:
  /// **'WhatsApp'**
  String get whatsapp;

  /// No description provided for @telegram.
  ///
  /// In en, this message translates to:
  /// **'Telegram'**
  String get telegram;

  /// No description provided for @legal.
  ///
  /// In en, this message translates to:
  /// **'Legal'**
  String get legal;

  /// No description provided for @terms.
  ///
  /// In en, this message translates to:
  /// **'Terms'**
  String get terms;

  /// No description provided for @termsOfService.
  ///
  /// In en, this message translates to:
  /// **'Terms of Service'**
  String get termsOfService;

  /// No description provided for @privacyPolicy_.
  ///
  /// In en, this message translates to:
  /// **'Privacy Policy'**
  String get privacyPolicy_;

  /// No description provided for @cookiePolicy.
  ///
  /// In en, this message translates to:
  /// **'Cookie Policy'**
  String get cookiePolicy;

  /// No description provided for @license.
  ///
  /// In en, this message translates to:
  /// **'License'**
  String get license;

  /// No description provided for @copyright.
  ///
  /// In en, this message translates to:
  /// **'Copyright'**
  String get copyright;

  /// No description provided for @allRightsReserved.
  ///
  /// In en, this message translates to:
  /// **'All Rights Reserved'**
  String get allRightsReserved;

  /// No description provided for @poweredBy.
  ///
  /// In en, this message translates to:
  /// **'Powered By'**
  String get poweredBy;

  /// No description provided for @developedBy.
  ///
  /// In en, this message translates to:
  /// **'Developed By'**
  String get developedBy;

  /// No description provided for @versionInfo.
  ///
  /// In en, this message translates to:
  /// **'Version Info'**
  String get versionInfo;

  /// No description provided for @checkForUpdates.
  ///
  /// In en, this message translates to:
  /// **'Check for Updates'**
  String get checkForUpdates;

  /// No description provided for @updateAvailable.
  ///
  /// In en, this message translates to:
  /// **'Update Available'**
  String get updateAvailable;

  /// No description provided for @updateNow.
  ///
  /// In en, this message translates to:
  /// **'Update Now'**
  String get updateNow;

  /// No description provided for @updateLater.
  ///
  /// In en, this message translates to:
  /// **'Update Later'**
  String get updateLater;

  /// No description provided for @upToDate.
  ///
  /// In en, this message translates to:
  /// **'Up to Date'**
  String get upToDate;

  /// No description provided for @whatsNew.
  ///
  /// In en, this message translates to:
  /// **'What\'\'s New'**
  String get whatsNew;

  /// No description provided for @releaseNotes.
  ///
  /// In en, this message translates to:
  /// **'Release Notes'**
  String get releaseNotes;

  /// No description provided for @changelog.
  ///
  /// In en, this message translates to:
  /// **'Changelog'**
  String get changelog;

  /// No description provided for @improvements.
  ///
  /// In en, this message translates to:
  /// **'Improvements'**
  String get improvements;

  /// No description provided for @bugFixes.
  ///
  /// In en, this message translates to:
  /// **'Bug Fixes'**
  String get bugFixes;

  /// No description provided for @newFeatures.
  ///
  /// In en, this message translates to:
  /// **'New Features'**
  String get newFeatures;

  /// No description provided for @performance.
  ///
  /// In en, this message translates to:
  /// **'Performance'**
  String get performance;

  /// No description provided for @stability.
  ///
  /// In en, this message translates to:
  /// **'Stability'**
  String get stability;

  /// No description provided for @security_.
  ///
  /// In en, this message translates to:
  /// **'Security'**
  String get security_;

  /// No description provided for @accessibility.
  ///
  /// In en, this message translates to:
  /// **'Accessibility'**
  String get accessibility;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['ar', 'en'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'ar':
      return AppLocalizationsAr();
    case 'en':
      return AppLocalizationsEn();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
