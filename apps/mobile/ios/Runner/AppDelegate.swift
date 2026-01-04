import Flutter
import UIKit

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    // Initialize certificate pinning for enhanced security
    configureCertificatePinning()

    // Register Flutter plugins
    GeneratedPluginRegistrant.register(with: self)

    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  /// Configure SSL/TLS certificate pinning
  private func configureCertificatePinning() {
    #if DEBUG
    // In debug mode, allow bypass for development
    // Certificate pinning is still configured but can be bypassed
    CertificatePinningManager.shared.configure(
      enforceStrict: false,
      allowDebugBypass: true
    )
    print("🔐 Certificate pinning configured in DEBUG mode (bypass enabled)")
    #else
    // In release mode, enforce strict pinning
    CertificatePinningManager.shared.configure(
      enforceStrict: true,
      allowDebugBypass: false
    )
    print("🔐 Certificate pinning configured in RELEASE mode (strict enforcement)")
    #endif

    // Check for expiring pins
    let expiringPins = CertificatePinningManager.shared.getExpiringPins(daysThreshold: 30)
    if !expiringPins.isEmpty {
      print("⚠️ WARNING: Some certificate pins will expire soon:")
      for (domain, expiryDate) in expiringPins {
        print("   - \(domain): \(expiryDate)")
      }
    }
  }
}
