import Foundation
import Security
import CommonCrypto

/// Certificate Pinning Manager for iOS
/// Provides programmatic certificate pinning using public key pinning (SPKI)
/// This complements the Info.plist NSPinnedDomains configuration
///
/// Usage:
/// ```swift
/// // Initialize in AppDelegate
/// CertificatePinningManager.shared.configure()
///
/// // Use in URLSession
/// let session = URLSession(configuration: .default, delegate: CertificatePinningManager.shared, delegateQueue: nil)
/// ```
class CertificatePinningManager: NSObject, URLSessionDelegate {

    // MARK: - Singleton
    static let shared = CertificatePinningManager()

    // MARK: - Configuration

    /// Certificate pins for each domain
    /// Key: domain name
    /// Value: array of base64-encoded SHA256 public key hashes
    private var certificatePins: [String: [String]] = [:]

    /// Whether to enforce strict pinning (fail if no pins match)
    private var enforceStrict: Bool = true

    /// Whether to allow bypass in debug builds
    private var allowDebugBypass: Bool = true

    /// Pin expiry tracking
    private var pinExpiry: [String: Date] = [:]

    // MARK: - Initialization

    private override init() {
        super.init()
    }

    /// Configure certificate pinning with default SAHOOL domains
    func configure(enforceStrict: Bool = true, allowDebugBypass: Bool = true) {
        self.enforceStrict = enforceStrict
        self.allowDebugBypass = allowDebugBypass

        // Configure default pins for SAHOOL domains
        configureDefaultPins()

        // Log configuration status
        logConfiguration()
    }

    /// Configure default certificate pins for SAHOOL domains
    private func configureDefaultPins() {
        // Production API domain: api.sahool.io
        certificatePins["api.sahool.io"] = [
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", // Primary pin - REPLACE
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="  // Backup pin - REPLACE
        ]
        pinExpiry["api.sahool.io"] = Date(timeIntervalSince1970: 1735689600) // 2026-12-31

        // Production API domain: api.sahool.app
        certificatePins["api.sahool.app"] = [
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=", // Primary pin - REPLACE
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="  // Backup pin - REPLACE
        ]
        pinExpiry["api.sahool.app"] = Date(timeIntervalSince1970: 1735689600) // 2026-12-31

        // Staging API domain
        certificatePins["api-staging.sahool.app"] = [
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE="  // Staging pin - REPLACE
        ]
        pinExpiry["api-staging.sahool.app"] = Date(timeIntervalSince1970: 1719792000) // 2026-06-30

        // WebSocket production
        certificatePins["ws.sahool.app"] = [
            "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC="  // WebSocket pin - REPLACE
        ]
        pinExpiry["ws.sahool.app"] = Date(timeIntervalSince1970: 1735689600) // 2026-12-31

        // WebSocket staging
        certificatePins["ws-staging.sahool.app"] = [
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF="  // Staging WebSocket pin - REPLACE
        ]
        pinExpiry["ws-staging.sahool.app"] = Date(timeIntervalSince1970: 1719792000) // 2026-06-30
    }

    // MARK: - Public Methods

    /// Add or update pins for a domain
    /// - Parameters:
    ///   - domain: The domain name
    ///   - pins: Array of base64-encoded SHA256 public key hashes
    ///   - expiryDate: Optional expiry date for the pins
    func addPins(forDomain domain: String, pins: [String], expiryDate: Date? = nil) {
        certificatePins[domain] = pins
        if let expiry = expiryDate {
            pinExpiry[domain] = expiry
        }
        print("📌 Certificate pins added for domain: \(domain)")
    }

    /// Remove pins for a domain
    /// - Parameter domain: The domain name
    func removePins(forDomain domain: String) {
        certificatePins.removeValue(forKey: domain)
        pinExpiry.removeValue(forKey: domain)
        print("🗑️ Certificate pins removed for domain: \(domain)")
    }

    /// Get configured domains
    func getConfiguredDomains() -> [String] {
        return Array(certificatePins.keys)
    }

    /// Check if pins are expired for a domain
    /// - Parameter domain: The domain name
    /// - Returns: True if all pins are expired
    func arePinsExpired(forDomain domain: String) -> Bool {
        guard let expiryDate = pinExpiry[domain] else {
            return false
        }
        return Date() > expiryDate
    }

    /// Get expiring pins (within specified days)
    /// - Parameter daysThreshold: Number of days threshold
    /// - Returns: Dictionary of domains with expiring pins
    func getExpiringPins(daysThreshold: Int = 30) -> [String: Date] {
        let threshold = Date().addingTimeInterval(TimeInterval(daysThreshold * 86400))
        var expiringPins: [String: Date] = [:]

        for (domain, expiryDate) in pinExpiry {
            if expiryDate < threshold && expiryDate > Date() {
                expiringPins[domain] = expiryDate
            }
        }

        return expiringPins
    }

    // MARK: - URLSessionDelegate

    /// Handle authentication challenge for certificate pinning
    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        // Only handle server trust authentication
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.performDefaultHandling, nil)
            return
        }

        let host = challenge.protectionSpace.host

        // Debug bypass in non-production builds
        #if DEBUG
        if allowDebugBypass {
            print("⚠️ Certificate pinning bypassed for \(host) in DEBUG mode")
            completionHandler(.performDefaultHandling, nil)
            return
        }
        #endif

        // Validate certificate pinning
        if validateCertificatePinning(serverTrust: serverTrust, forHost: host) {
            print("✅ Certificate pin matched for host: \(host)")
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            print("❌ Certificate validation failed for host: \(host)")
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }

    // MARK: - Private Methods

    /// Validate certificate pinning
    /// - Parameters:
    ///   - serverTrust: The server trust to validate
    ///   - host: The host name
    /// - Returns: True if validation succeeds
    private func validateCertificatePinning(serverTrust: SecTrust, forHost host: String) -> Bool {
        // Get pins for this host
        let pins = getPins(forHost: host)

        // No pins configured
        if pins.isEmpty {
            if enforceStrict {
                print("❌ No certificate pins configured for host: \(host)")
                return false
            }
            // Allow connection if not enforcing strict mode
            return true
        }

        // Check if pins are expired
        if arePinsExpired(forDomain: host) {
            print("⚠️ Certificate pins expired for host: \(host)")
            if enforceStrict {
                return false
            }
        }

        // Set SSL policy for domain validation
        let policies = [SecPolicyCreateSSL(true, host as CFString)]
        SecTrustSetPolicies(serverTrust, policies as CFTypeRef)

        // Evaluate trust
        var secresult = SecTrustResultType.invalid
        let status = SecTrustEvaluate(serverTrust, &secresult)

        guard status == errSecSuccess else {
            print("❌ Trust evaluation failed with status: \(status)")
            return false
        }

        // Get certificate chain
        guard let certificateCount = SecTrustGetCertificateCount(serverTrust) as Int?,
              certificateCount > 0 else {
            print("❌ No certificates in chain")
            return false
        }

        // Check each certificate in the chain
        for index in 0..<certificateCount {
            guard let certificate = SecTrustGetCertificateAtIndex(serverTrust, index) else {
                continue
            }

            // Extract public key
            if let publicKey = extractPublicKey(from: certificate) {
                let publicKeyHash = sha256Hash(data: publicKey)
                let publicKeyHashBase64 = publicKeyHash.base64EncodedString()

                // Check if hash matches any configured pins
                if pins.contains(publicKeyHashBase64) {
                    print("✅ Public key hash matched for \(host)")
                    print("   Hash: \(publicKeyHashBase64)")
                    return true
                }
            }
        }

        // Log all public key hashes for debugging
        print("❌ No matching pins found for host: \(host)")
        print("   Expected one of: \(pins)")
        logCertificateChain(serverTrust: serverTrust)

        return false
    }

    /// Get pins for a specific host (supports wildcards)
    /// - Parameter host: The host name
    /// - Returns: Array of certificate pins
    private func getPins(forHost host: String) -> [String] {
        var pins: [String] = []

        // Exact match
        if let exactPins = certificatePins[host] {
            pins.append(contentsOf: exactPins)
        }

        // Wildcard match (*.domain.com)
        for (domain, domainPins) in certificatePins {
            if domain.hasPrefix("*.") {
                let baseDomain = String(domain.dropFirst(2))
                if host.hasSuffix(baseDomain) {
                    pins.append(contentsOf: domainPins)
                }
            }
        }

        return pins
    }

    /// Extract public key from certificate
    /// - Parameter certificate: The certificate
    /// - Returns: Public key data
    private func extractPublicKey(from certificate: SecCertificate) -> Data? {
        // Create trust with certificate
        var trust: SecTrust?
        let policy = SecPolicyCreateBasicX509()
        let status = SecTrustCreateWithCertificates(certificate, policy, &trust)

        guard status == errSecSuccess, let trust = trust else {
            return nil
        }

        // Extract public key
        if #available(iOS 14.0, *) {
            guard let publicKey = SecTrustCopyKey(trust) else {
                return nil
            }
            return extractPublicKeyData(from: publicKey)
        } else {
            guard let publicKey = SecTrustCopyPublicKey(trust) else {
                return nil
            }
            return extractPublicKeyData(from: publicKey)
        }
    }

    /// Extract public key data in SPKI format
    /// - Parameter publicKey: The public key
    /// - Returns: SPKI formatted public key data
    private func extractPublicKeyData(from publicKey: SecKey) -> Data? {
        var error: Unmanaged<CFError>?
        guard let publicKeyData = SecKeyCopyExternalRepresentation(publicKey, &error) as Data? else {
            if let error = error?.takeRetainedValue() {
                print("❌ Failed to extract public key: \(error)")
            }
            return nil
        }
        return publicKeyData
    }

    /// Calculate SHA256 hash of data
    /// - Parameter data: The data to hash
    /// - Returns: SHA256 hash
    private func sha256Hash(data: Data) -> Data {
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        data.withUnsafeBytes {
            _ = CC_SHA256($0.baseAddress, CC_LONG(data.count), &hash)
        }
        return Data(hash)
    }

    /// Log certificate chain information for debugging
    /// - Parameter serverTrust: The server trust
    private func logCertificateChain(serverTrust: SecTrust) {
        guard let certificateCount = SecTrustGetCertificateCount(serverTrust) as Int? else {
            return
        }

        print("📜 Certificate Chain (\(certificateCount) certificates):")

        for index in 0..<certificateCount {
            guard let certificate = SecTrustGetCertificateAtIndex(serverTrust, index) else {
                continue
            }

            if let publicKey = extractPublicKey(from: certificate) {
                let publicKeyHash = sha256Hash(data: publicKey)
                let publicKeyHashBase64 = publicKeyHash.base64EncodedString()

                print("   Certificate \(index):")
                if let summary = SecCertificateCopySubjectSummary(certificate) as String? {
                    print("     Subject: \(summary)")
                }
                print("     Public Key Hash: \(publicKeyHashBase64)")
            }
        }
    }

    /// Log configuration status
    private func logConfiguration() {
        print("🔐 Certificate Pinning Configuration:")
        print("   Enforce Strict: \(enforceStrict)")
        print("   Allow Debug Bypass: \(allowDebugBypass)")
        print("   Configured Domains: \(certificatePins.count)")

        for (domain, pins) in certificatePins {
            print("   - \(domain): \(pins.count) pin(s)")
            if let expiryDate = pinExpiry[domain] {
                let daysUntilExpiry = Calendar.current.dateComponents([.day], from: Date(), to: expiryDate).day ?? 0
                print("     Expiry: \(expiryDate) (\(daysUntilExpiry) days)")
            }
        }

        // Check for expiring pins
        let expiringPins = getExpiringPins(daysThreshold: 30)
        if !expiringPins.isEmpty {
            print("   ⚠️ Expiring Soon:")
            for (domain, expiryDate) in expiringPins {
                let daysUntilExpiry = Calendar.current.dateComponents([.day], from: Date(), to: expiryDate).day ?? 0
                print("     - \(domain): \(daysUntilExpiry) days")
            }
        }
    }
}

// MARK: - Certificate Pinning Helper Extension

extension URLSession {
    /// Create a URLSession with certificate pinning enabled
    /// - Returns: URLSession configured with certificate pinning
    static func withCertificatePinning() -> URLSession {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60

        return URLSession(
            configuration: configuration,
            delegate: CertificatePinningManager.shared,
            delegateQueue: nil
        )
    }
}

// MARK: - Certificate Pin Model

/// Certificate pin information
struct CertificatePin {
    /// The domain name
    let domain: String

    /// Base64-encoded SHA256 public key hash
    let publicKeyHash: String

    /// Optional expiry date
    let expiryDate: Date?

    /// Optional description
    let description: String?

    /// Check if pin is expired
    var isExpired: Bool {
        guard let expiryDate = expiryDate else {
            return false
        }
        return Date() > expiryDate
    }

    /// Days until expiry
    var daysUntilExpiry: Int? {
        guard let expiryDate = expiryDate else {
            return nil
        }
        return Calendar.current.dateComponents([.day], from: Date(), to: expiryDate).day
    }
}

// MARK: - Certificate Utilities

/// Utility functions for certificate management
class CertificateUtilities {

    /// Extract certificate fingerprint for debugging
    /// - Parameter url: The URL to connect to
    /// - Returns: Public key hash in base64 format
    static func extractCertificateFingerprint(from url: URL) async throws -> String? {
        let (_, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              let serverTrust = (httpResponse.value(forHTTPHeaderField: "Server-Trust") as? SecTrust) else {
            return nil
        }

        guard let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            return nil
        }

        let manager = CertificatePinningManager.shared
        guard let publicKey = manager.extractPublicKey(from: certificate) else {
            return nil
        }

        let hash = manager.sha256Hash(data: publicKey)
        return hash.base64EncodedString()
    }

    /// Get SPKI hash from command line for a domain
    /// This provides instructions for getting the actual hash
    /// - Parameter domain: The domain name
    /// - Returns: Command to run
    static func getHashExtractionCommand(forDomain domain: String) -> String {
        return """
        # Extract SPKI hash for \(domain):
        openssl s_client -connect \(domain):443 -servername \(domain) < /dev/null 2>/dev/null | \\
        openssl x509 -pubkey -noout | \\
        openssl pkey -pubin -outform der | \\
        openssl dgst -sha256 -binary | \\
        openssl enc -base64
        """
    }
}
