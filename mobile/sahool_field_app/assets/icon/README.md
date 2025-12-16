# SAHOOL App Icons - دليل إعداد الأيقونات

## Required Files - الملفات المطلوبة

Place the following PNG files in this directory:

| File Name | Size | Description |
|-----------|------|-------------|
| `app_icon.png` | 1024x1024 | Main app icon (square) |
| `app_icon_foreground.png` | 1024x1024 | Adaptive icon foreground (Android 8+) |
| `splash_logo.png` | 512x512 | Splash screen logo (white on transparent) |

## Design Guidelines - إرشادات التصميم

### App Icon (app_icon.png)
- **Shape**: Square with rounded corners (automatically applied)
- **Background**: Forest Green (#2E7D32)
- **Foreground**: White SAHOOL logo/icon
- **Safe Zone**: Keep logo within 66% center area for adaptive icons

### Splash Logo (splash_logo.png)
- **Background**: Transparent
- **Color**: White (#FFFFFF)
- **Size**: Should fit comfortably within 512x512 with padding

## Quick Setup - الإعداد السريع

If you don't have custom icons yet, you can use placeholder icons:

```bash
# Generate placeholder icons using ImageMagick (if installed)
cd assets/icon

# Create a simple green square as placeholder
convert -size 1024x1024 xc:#2E7D32 app_icon.png

# Create white circle as foreground
convert -size 1024x1024 xc:transparent -fill white -draw "circle 512,512 512,256" app_icon_foreground.png

# Create splash logo
convert -size 512x512 xc:transparent -fill white -gravity center -pointsize 100 -annotate 0 "سهول" splash_logo.png
```

## Generate Icons - توليد الأيقونات

After placing the files, run:

```bash
cd mobile/sahool_field_app
flutter pub get
dart run flutter_launcher_icons
dart run flutter_native_splash:create
```

## Color Reference - مرجع الألوان

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Forest Green | `#2E7D32` | Primary brand color |
| Dark Green | `#1B5E20` | Dark mode background |
| White | `#FFFFFF` | Logo/text on colored backgrounds |

## Notes - ملاحظات

- Icons should be in PNG format (not JPEG)
- No transparency needed for main app_icon.png
- splash_logo.png MUST have transparent background
- Use vector graphics (SVG) for design, export to PNG at required sizes
