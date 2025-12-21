# Mapbox Setup Guide

This guide explains how to switch from `flutter_map` to `mapbox_maps_flutter` for enhanced map features.

## Why Mapbox?

Mapbox provides:
- High-quality satellite imagery
- Better offline map support
- Advanced styling options
- Better performance for large datasets

## Prerequisites

You need two tokens from Mapbox:
1. **Public Access Token** - For runtime map display
2. **Secret Downloads Token** - For building the Android/iOS SDK

## Step 1: Create Mapbox Account

1. Go to [https://account.mapbox.com/auth/signup/](https://account.mapbox.com/auth/signup/)
2. Sign up for a free account
3. The free tier includes 50,000 map loads per month

## Step 2: Get Your Tokens

### Public Access Token
1. Go to [https://account.mapbox.com/access-tokens/](https://account.mapbox.com/access-tokens/)
2. Copy your **Default public token** (starts with `pk.`)
3. Add it to your `.env` file:
   ```
   MAPBOX_ACCESS_TOKEN=pk.your_actual_token_here
   ```

### Secret Downloads Token
1. On the same page, click **Create a token**
2. Name it "Downloads Token"
3. Under **Secret scopes**, check `DOWNLOADS:READ`
4. Click **Create token**
5. **IMPORTANT**: Copy the token immediately (starts with `sk.`) - you won't see it again!
6. Add it to `android/gradle.properties`:
   ```
   MAPBOX_DOWNLOADS_TOKEN=sk.your_actual_secret_token_here
   ```

## Step 3: Enable Mapbox in Your App

1. Open `pubspec.yaml`
2. Uncomment the mapbox line:
   ```yaml
   mapbox_maps_flutter: ^1.1.0
   ```
3. Run:
   ```bash
   flutter pub get
   ```

## Step 4: Update Map Implementation

Replace `flutter_map` widgets with Mapbox widgets in your map screens.

Example:
```dart
import 'package:mapbox_maps_flutter/mapbox_maps_flutter.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

// In your widget:
MapboxMap(
  accessToken: dotenv.env['MAPBOX_ACCESS_TOKEN']!,
  styleUri: dotenv.env['MAPBOX_STYLE_URL'] ?? 
            'mapbox://styles/mapbox/satellite-streets-v12',
  // ... other configuration
)
```

## Troubleshooting

### "SDK Registry token is null"
- Make sure you added `MAPBOX_DOWNLOADS_TOKEN` to `android/gradle.properties`
- The token must start with `sk.`
- Run `flutter clean` after adding the token

### Build fails on iOS
- Add your secret token to `ios/Podfile` or create `~/.netrc` file
- See: [https://docs.mapbox.com/ios/maps/guides/install/](https://docs.mapbox.com/ios/maps/guides/install/)

### Map doesn't display
- Check that your public token (pk.) is in the `.env` file
- Verify the token has the correct scopes
- Check network connectivity

## Cost Considerations

- **Free tier**: 50,000 map loads/month
- **Paid plans**: Start at $5/month for additional loads
- Monitor usage at: [https://account.mapbox.com/](https://account.mapbox.com/)

## Alternative: Keep Using flutter_map

If you prefer not to use Mapbox:
- `flutter_map` works great with OpenStreetMap tiles (free)
- No authentication required
- Good for basic mapping needs
- Limited satellite imagery options
