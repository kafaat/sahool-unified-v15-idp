# iOS Universal Links Configuration

This document explains the iOS Universal Links setup for the Sahool Field App.

## Overview

Universal Links allow your app to be opened directly from web links without going through Safari. When a user taps a link to `https://sahool.app/field/123`, the app will open directly to that specific field.

## Configuration Files

### 1. Runner.entitlements
**Location:** `/ios/Runner/Runner.entitlements`

This file enables Universal Links for the following domains:
- `sahool.app`
- `www.sahool.app`

The entitlements file has been added to the Xcode project and is configured for all build configurations (Debug, Release, Profile).

### 2. Info.plist
**Location:** `/ios/Runner/Info.plist`

The Info.plist now includes:
- **CFBundleURLTypes**: Defines the custom URL scheme `sahool://` for deep linking
- This enables both Universal Links (https://sahool.app) and custom schemes (sahool://)

### 3. Apple App Site Association File
**Location:** `/ios/apple-app-site-association`

This JSON file must be deployed to your web server at:
```
https://sahool.app/.well-known/apple-app-site-association
https://sahool.app/apple-app-site-association
```

**Important:** Replace `TEAMID` in the file with your actual Apple Team ID.

## Server Deployment Steps

### 1. Find Your Team ID
- Log in to [Apple Developer Portal](https://developer.apple.com)
- Navigate to Membership section
- Copy your Team ID (e.g., `ABC123XYZ`)

### 2. Update the AASA File
Edit `apple-app-site-association` and replace:
```json
"appID": "TEAMID.com.example.sahoolFieldApp"
```
with:
```json
"appID": "ABC123XYZ.com.example.sahoolFieldApp"
```

### 3. Deploy to Server
Upload the file to your web server:

```bash
# Upload to both locations
/.well-known/apple-app-site-association
/apple-app-site-association
```

**Server Configuration Requirements:**
- Content-Type: `application/json` (or `application/pkcs7-mime` for signed files)
- HTTPS required (HTTP will not work)
- No file extension
- Must be accessible at the root of your domain
- No redirects (direct 200 OK response)

### 4. Verify Deployment
Test your AASA file:
```bash
curl -I https://sahool.app/.well-known/apple-app-site-association
curl https://sahool.app/.well-known/apple-app-site-association
```

Or use Apple's validation tool:
https://search.developer.apple.com/appsearch-validation-tool/

## Xcode Configuration

The following changes have been made to the Xcode project:

1. **Added Runner.entitlements** to the project
2. **Enabled Associated Domains** capability
3. **Added CODE_SIGN_ENTITLEMENTS** to all build configurations

**To verify in Xcode:**
1. Open `Runner.xcworkspace` in Xcode
2. Select the Runner target
3. Go to "Signing & Capabilities" tab
4. Verify "Associated Domains" capability is present
5. Verify domains include `applinks:sahool.app`

## Flutter Deep Link Handling

The app uses `go_router` for navigation, which automatically handles deep links.

### Supported Deep Link Paths

Based on the current routing configuration:

| Path | Description |
|------|-------------|
| `/field/:id` | Field details page |
| `/field/:id/dashboard` | Field dashboard |
| `/field/:id/ecological` | Field ecological records |
| `/crop/*` | Crop-related pages |
| `/task/*` | Task-related pages |
| `/ecological/*` | Ecological records |
| `/scouting/*` | Scouting features |
| `/advisor/*` | AI advisor |
| `/scanner/*` | QR/Barcode scanner |

### Example Deep Links

- `https://sahool.app/field/abc123` → Opens field details
- `sahool://field/abc123` → Opens via custom scheme
- `https://sahool.app/ecological/biodiversity` → Opens biodiversity records

### Testing Deep Links

#### On Physical Device:
1. Send yourself a message with the link (iMessage, WhatsApp, etc.)
2. Tap the link
3. App should open directly

#### On Simulator:
```bash
xcrun simctl openurl booted "https://sahool.app/field/test123"
xcrun simctl openurl booted "sahool://field/test123"
```

#### Via Terminal (Physical Device):
```bash
# Get your device's UDID
idevice_id -l

# Open URL on device
idevicedebug run com.example.sahoolFieldApp -u YOUR_UDID --url "https://sahool.app/field/test123"
```

## Additional Flutter Configuration

The app's `go_router` configuration in `/lib/core/routes/app_router.dart` automatically handles:
- Route parsing from URLs
- Navigation to appropriate screens
- Error handling for invalid routes

No additional code is needed in Flutter as `go_router` handles deep links automatically when configured with routes.

## Troubleshooting

### Universal Links Not Working

1. **Verify AASA file is accessible:**
   ```bash
   curl https://sahool.app/.well-known/apple-app-site-association
   ```

2. **Check Team ID is correct:**
   - Ensure you replaced `TEAMID` with your actual Team ID
   - Team ID format: uppercase letters and numbers (e.g., `ABC123XYZ`)

3. **Verify bundle identifier:**
   - Current: `com.example.sahoolFieldApp`
   - Must match the identifier in AASA file

4. **Force iOS to re-download AASA:**
   - Uninstall the app completely
   - Restart device
   - Reinstall the app
   - iOS will fetch the AASA file on first launch

5. **Check domain is not blacklisted:**
   - iOS caches failed AASA attempts
   - Wait 24 hours or use a different domain for testing

6. **Enable debug logging:**
   ```swift
   // Add to AppDelegate.swift
   if #available(iOS 14.0, *) {
       swcutil_show_app_links_domains(Bundle.main.bundleIdentifier! as CFString)
   }
   ```

### Custom Schemes Not Working

1. Verify Info.plist contains CFBundleURLTypes
2. Check scheme is lowercase (`sahool`, not `SAHOOL`)
3. Ensure no other app uses the same scheme

### Deep Links Open Safari Instead

- This is iOS fallback behavior when:
  - AASA file is not found
  - Team ID doesn't match
  - App is not installed
  - User held link to see preview

## Security Considerations

1. **Always use HTTPS** - Universal Links require HTTPS
2. **Validate deep link parameters** in Flutter code
3. **Handle malicious URLs** gracefully
4. **Don't expose sensitive data** in URLs

## Next Steps

1. Replace `TEAMID` in `apple-app-site-association` with your actual Team ID
2. Update bundle identifier if needed (currently `com.example.sahoolFieldApp`)
3. Deploy AASA file to production server
4. Test on physical device
5. Submit app to App Store with Associated Domains entitlement

## References

- [Apple Universal Links Documentation](https://developer.apple.com/ios/universal-links/)
- [Apple App Site Association Validation](https://search.developer.apple.com/appsearch-validation-tool/)
- [go_router Documentation](https://pub.dev/packages/go_router)
- [Flutter Deep Linking](https://docs.flutter.dev/ui/navigation/deep-linking)
