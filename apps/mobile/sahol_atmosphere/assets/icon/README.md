# SAHOOL Atmosphere App Icons
# أيقونات تطبيق ساهول أتموسفير

## Required Icon Files
## الملفات المطلوبة

| File | Size | Purpose |
|------|------|---------|
| `app_icon.png` | 1024x1024 | Main app icon (Android adaptive, iOS) |
| `app_icon_foreground.png` | 1024x1024 | Android adaptive icon foreground |
| `splash_logo.png` | 512x512 | Splash screen logo |

## Design Guidelines
## إرشادات التصميم

### Theme Colors
- Primary Background: `#0D1F12` (Dark Forest)
- Secondary Background: `#050A06` (Near Black)
- Accent (Success): `#00E676` (Bio-Luminescent Green)
- Glow Color: `#00FF88` (Atmosphere Glow)

### Icon Style
- Modern, minimalist design
- Bio-luminescent glow effect
- Agricultural/atmospheric theme
- Compatible with dark mode UI

## Generation
## التوليد

Run the icon generation script:
```bash
python scripts/generate_icons.py
```

Or use flutter_launcher_icons:
```bash
dart run flutter_launcher_icons
```

## After Adding Icons
## بعد إضافة الأيقونات

1. Run flutter_launcher_icons:
   ```bash
   dart run flutter_launcher_icons
   ```

2. Generate splash screen:
   ```bash
   dart run flutter_native_splash:create
   ```
