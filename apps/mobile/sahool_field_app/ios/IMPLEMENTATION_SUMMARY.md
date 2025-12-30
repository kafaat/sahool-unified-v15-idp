# iOS Universal Links Implementation Summary

## Date: 2025-12-30

This document summarizes the iOS Universal Links implementation for the Sahool Field App.

## Changes Made

### 1. Created Runner.entitlements
**File:** `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/Runner/Runner.entitlements`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>com.apple.developer.associated-domains</key>
	<array>
		<string>applinks:sahool.app</string>
		<string>applinks:www.sahool.app</string>
	</array>
</dict>
</plist>
```

**Purpose:** Enables Universal Links for sahool.app domain

---

### 2. Updated Info.plist
**File:** `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/Runner/Info.plist`

**Added:**
```xml
<key>CFBundleURLTypes</key>
<array>
	<dict>
		<key>CFBundleTypeRole</key>
		<string>Editor</string>
		<key>CFBundleURLName</key>
		<string>app.sahool.field</string>
		<key>CFBundleURLSchemes</key>
		<array>
			<string>sahool</string>
		</array>
	</dict>
</array>
```

**Purpose:** Enables custom URL scheme `sahool://` for deep linking

---

### 3. Created Apple App Site Association File
**File:** `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/apple-app-site-association`

```json
{
  "applinks": {
    "apps": [],
    "details": [
      {
        "appID": "TEAMID.com.example.sahoolFieldApp",
        "paths": [
          "/field/*",
          "/crop/*",
          "/task/*",
          "/ecological/*",
          "/scouting/*",
          "/advisor/*",
          "/scanner/*"
        ]
      }
    ]
  },
  "webcredentials": {
    "apps": [
      "TEAMID.com.example.sahoolFieldApp"
    ]
  }
}
```

**Purpose:** Server-side configuration for Universal Links
**Action Required:** Replace `TEAMID` with your Apple Team ID and deploy to server

---

### 4. Updated Xcode Project Configuration
**File:** `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/Runner.xcodeproj/project.pbxproj`

**Changes:**
- Added `Runner.entitlements` file reference to project
- Added entitlements file to Runner group
- Added `CODE_SIGN_ENTITLEMENTS = Runner/Runner.entitlements;` to:
  - Debug build configuration
  - Release build configuration
  - Profile build configuration

**Verification:** 3 occurrences of `CODE_SIGN_ENTITLEMENTS` in project file

---

### 5. Created Documentation
**Files:**
- `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/UNIVERSAL_LINKS_README.md`
- `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/IMPLEMENTATION_SUMMARY.md` (this file)

---

## Current Configuration

### Bundle Identifier
```
com.example.sahoolFieldApp
```

### Supported Domains
- `sahool.app`
- `www.sahool.app`

### Custom URL Scheme
```
sahool://
```

### Supported Deep Link Paths
Based on existing Flutter routes:
- `/field/:id` - Field details
- `/field/:id/dashboard` - Field dashboard
- `/field/:id/ecological` - Field ecological records
- `/crop/*` - Crop pages
- `/task/*` - Task pages
- `/ecological/*` - Ecological records
- `/scouting/*` - Scouting features
- `/advisor/*` - AI advisor
- `/scanner/*` - Scanner

---

## Flutter Integration

### Router Configuration
**File:** `/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/lib/core/routes/app_router.dart`

The app uses `go_router` v14.6.2 which automatically handles deep links. No additional Flutter code is required.

**Key Features:**
- Automatic URL parsing
- Route parameter extraction
- Error handling for invalid routes
- Support for both Universal Links and custom schemes

---

## Required Actions Before Deployment

### 1. Update Team ID
Replace `TEAMID` in `apple-app-site-association` file with your actual Apple Team ID:

**How to find Team ID:**
1. Log in to https://developer.apple.com
2. Go to Membership section
3. Copy your Team ID (format: ABC123XYZ)

### 2. Deploy AASA File to Server
Upload `apple-app-site-association` to:
```
https://sahool.app/.well-known/apple-app-site-association
https://sahool.app/apple-app-site-association
```

**Server Requirements:**
- Must be HTTPS
- Content-Type: `application/json`
- No file extension
- No redirects
- Accessible from root domain

### 3. Update Bundle Identifier (Optional)
If you want to change from `com.example.sahoolFieldApp`:
1. Update in Xcode project settings
2. Update in `apple-app-site-association` file
3. Update in Apple Developer Portal

### 4. Configure Apple Developer Portal
1. Enable Associated Domains capability
2. Add domains: `applinks:sahool.app`
3. Create/update provisioning profile

### 5. Test Implementation
**On Simulator:**
```bash
xcrun simctl openurl booted "https://sahool.app/field/test123"
xcrun simctl openurl booted "sahool://field/test123"
```

**On Device:**
1. Send yourself a link via iMessage/WhatsApp
2. Tap the link
3. App should open directly

**Verify AASA:**
```bash
curl https://sahool.app/.well-known/apple-app-site-association
```

---

## Testing Checklist

- [ ] Replace TEAMID in AASA file
- [ ] Deploy AASA file to server
- [ ] Verify AASA file is accessible via HTTPS
- [ ] Open Xcode and verify Associated Domains capability
- [ ] Build and run on simulator
- [ ] Test custom scheme: `sahool://field/123`
- [ ] Build and install on physical device
- [ ] Test Universal Link: `https://sahool.app/field/123`
- [ ] Verify deep link opens correct screen
- [ ] Test invalid URLs show error screen
- [ ] Verify fallback to Safari when app not installed

---

## Example Deep Links

### Universal Links (HTTPS)
```
https://sahool.app/field/abc123
https://sahool.app/field/abc123/dashboard
https://sahool.app/field/abc123/ecological
https://sahool.app/ecological/biodiversity
https://sahool.app/scouting
```

### Custom Scheme
```
sahool://field/abc123
sahool://field/abc123/dashboard
sahool://ecological/biodiversity
```

---

## Troubleshooting

### Universal Links Not Working

1. **AASA file not found:**
   - Verify file is at `/.well-known/apple-app-site-association`
   - Check HTTPS is working
   - Ensure no redirects

2. **Team ID mismatch:**
   - Double-check Team ID in AASA file
   - Verify bundle identifier matches

3. **iOS cache issue:**
   - Uninstall app completely
   - Restart device
   - Reinstall app (iOS fetches AASA on first install)

4. **Domain blacklisted:**
   - iOS caches failed attempts for 24 hours
   - Use different domain for testing

### Custom Schemes Not Working

1. Verify Info.plist has CFBundleURLTypes
2. Check scheme is lowercase
3. Ensure no conflicts with other apps

---

## File Locations Summary

```
/home/user/sahool-unified-v15-idp/apps/mobile/sahool_field_app/ios/
├── Runner/
│   ├── Runner.entitlements                    [NEW - Associated Domains]
│   └── Info.plist                             [MODIFIED - URL Schemes]
├── Runner.xcodeproj/
│   └── project.pbxproj                        [MODIFIED - Build Settings]
├── apple-app-site-association                 [NEW - Server Configuration]
├── UNIVERSAL_LINKS_README.md                  [NEW - Documentation]
└── IMPLEMENTATION_SUMMARY.md                  [NEW - This file]
```

---

## References

- [Apple Universal Links](https://developer.apple.com/ios/universal-links/)
- [AASA Validator](https://search.developer.apple.com/appsearch-validation-tool/)
- [go_router Package](https://pub.dev/packages/go_router)
- [Flutter Deep Linking](https://docs.flutter.dev/ui/navigation/deep-linking)

---

## Notes

- No changes were made to Flutter Dart code as `go_router` handles deep links automatically
- The app already has proper routing structure in place
- All iOS configuration is complete and ready for deployment
- Deep link handling will work immediately after AASA deployment

---

## Next Steps

1. Get your Apple Team ID
2. Update `apple-app-site-association` file
3. Deploy AASA file to production server (https://sahool.app)
4. Test on physical device
5. Submit to App Store with Associated Domains entitlement enabled
