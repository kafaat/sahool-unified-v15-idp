# Android App Links - Digital Asset Links Configuration

## Overview
This file documents the configuration needed for Android App Links verification.

## Asset Links File Location
The `assetlinks.json` file in this directory is a **reference copy**. For Android App Links to work, you must host this file on your web server at:

```
https://sahool.app/.well-known/assetlinks.json
https://www.sahool.app/.well-known/assetlinks.json
```

## Getting SHA-256 Certificate Fingerprints

### For Debug Key
```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

### For Release Key
```bash
keytool -list -v -keystore /path/to/your/release-keystore.jks -alias your-alias-name
```

Look for the `SHA256` fingerprint in the output and replace `REPLACE_WITH_YOUR_RELEASE_KEY_SHA256` and `REPLACE_WITH_YOUR_DEBUG_KEY_SHA256` in the `assetlinks.json` file.

## Testing Deep Links

### Test with ADB
```bash
# Test HTTPS deep link
adb shell am start -W -a android.intent.action.VIEW -d "https://sahool.app/field/123"

# Test custom scheme deep link
adb shell am start -W -a android.intent.action.VIEW -d "sahool://open/field/123"
```

### Verify Asset Links
After deploying the file to your server, verify it with:
```bash
# Check if file is accessible
curl https://sahool.app/.well-known/assetlinks.json

# Use Google's Digital Asset Links API
https://digitalassetlinks.googleapis.com/v1/statements:list?source.web.site=https://sahool.app&relation=delegate_permission/common.handle_all_urls
```

## Deployment Checklist
- [ ] Generate SHA-256 fingerprints for debug and release keys
- [ ] Update `assetlinks.json` with correct fingerprints
- [ ] Upload `assetlinks.json` to `https://sahool.app/.well-known/assetlinks.json`
- [ ] Ensure the file is served with `Content-Type: application/json`
- [ ] Ensure the file is accessible via HTTPS (not HTTP)
- [ ] Test deep links using ADB
- [ ] Verify using Digital Asset Links API

## Supported Deep Link Patterns
- `https://sahool.app/field/{fieldId}` - Open field details
- `https://sahool.app/crop/{cropId}` - Open crop details (if implemented)
- `https://sahool.app/task/{taskId}` - Open task details (if implemented)
- `sahool://open/{path}` - Custom scheme for any path
