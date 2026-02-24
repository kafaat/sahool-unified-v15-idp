import Foundation
import Security
import CommonCrypto

/// Certificate Pinning Manager for iOS
/// Provides programmatic certificate pinning using public key pinning (SPKI)
/// This complements the Info.plist NSPinnedDomains configuration
class CertificatePinningManager: NSObject, URLSessionDelegate {

    // MARK: - Singleton
    static let shared = CertificatePinningManager()

    // MARK: - Configuration

    /// Certificate pins for each domain (base64-encoded SHA256 public key hashes)
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
        configureDefaultPins()
        logConfiguration()
    }

    /// Configure default certificate pins for SAHOOL domains
    private func configureDefaultPins() {
        certificatePins["api.sahool.io"] = [
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
        ]
        pinExpiry["api.sahool.io"] = Date(timeIntervalSince1970: 1735689600)

        certificatePins["api.sahool.app"] = [
            "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
            "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB="
        ]
        pinExpiry["api.sahool.app"] = Date(timeIntervalSince1970: 1735689600)

        certificatePins["api-staging.sahool.app"] = [
            "EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE="
        ]
        pinExpiry["api-staging.sahool.app"] = Date(timeIntervalSince1970: 1719792000)

        certificatePins["ws.sahool.app"] = [
            "CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC="
        ]
        pinExpiry["ws.sahool.app"] = Date(timeIntervalSince1970: 1735689600)

        certificatePins["ws-staging.sahool.app"] = [
            "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF="
        ]
        pinExpiry["ws-staging.sahool.app"] = Date(timeIntervalSince1970: 1719792000)
    }

    // MARK: - Public Methods

    /// Add or update pins for a domain
    func addPins(forDomain domain: String, pins: [String], expiryDate: Date? = nil) {
        certificatePins[domain] = pins
        if let expiry = expiryDate {
            pinExpiry[domain] = expiry
        }
    }

    /// Remove pins for a domain
    func removePins(forDomain domain: String) {
        certificatePins.removeValue(forKey: domain)
        pinExpiry.removeValue(forKey: domain)
    }

    /// Get configured domains
    func getConfiguredDomains() -> [String] {
        return Array(certificatePins.keys)
    }

    /// Check if pins are expired for a domain
    func arePinsExpired(forDomain domain: String) -> Bool {
        guard let expiryDate = pinExpiry[domain] else {
            return false
        }
        return Date() > expiryDate
    }

    /// Get expiring pins (within specified days)
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

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard challenge.protectionSpace.authenticationMethod == NSURLAuthenticationMethodServerTrust,
              let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.performDefaultHandling, nil)
            return
        }

        let host = challenge.protectionSpace.host

        #if DEBUG
        if allowDebugBypass {
            completionHandler(.performDefaultHandling, nil)
            return
        }
        #endif

        if validateCertificatePinning(serverTrust: serverTrust, forHost: host) {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }

    // MARK: - Private Methods

    private func validateCertificatePinning(serverTrust: SecTrust, forHost host: String) -> Bool {
        let pins = getPins(forHost: host)

        if pins.isEmpty {
            return !enforceStrict
        }

        if arePinsExpired(forDomain: host) && enforceStrict {
            return false
        }

        // Set SSL policy for domain validation
        let policies = [SecPolicyCreateSSL(true, host as CFString)]
        SecTrustSetPolicies(serverTrust, policies as CFTypeRef)

        // Evaluate trust using modern API (iOS 12+)
        var error: CFError?
        let trustResult = SecTrustEvaluateWithError(serverTrust, &error)

        guard trustResult else {
            return false
        }

        // Get certificate chain using modern API (iOS 15+)
        guard let certificates = SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate],
              !certificates.isEmpty else {
            return false
        }

        // Check each certificate in the chain
        for certificate in certificates {
            if let publicKey = extractPublicKey(from: certificate) {
                let publicKeyHash = sha256Hash(data: publicKey)
                let publicKeyHashBase64 = publicKeyHash.base64EncodedString()
                if pins.contains(publicKeyHashBase64) {
                    return true
                }
            }
        }

        return false
    }

    /// Get pins for a specific host (supports wildcards)
    private func getPins(forHost host: String) -> [String] {
        var pins: [String] = []

        if let exactPins = certificatePins[host] {
            pins.append(contentsOf: exactPins)
        }

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
    fileprivate func extractPublicKey(from certificate: SecCertificate) -> Data? {
        var trust: SecTrust?
        let policy = SecPolicyCreateBasicX509()
        let status = SecTrustCreateWithCertificates(certificate, policy, &trust)

        guard status == errSecSuccess, let trust = trust else {
            return nil
        }

        guard let publicKey = SecTrustCopyKey(trust) else {
            return nil
        }
        return extractPublicKeyData(from: publicKey)
    }

    /// Extract public key data
    private func extractPublicKeyData(from publicKey: SecKey) -> Data? {
        var error: Unmanaged<CFError>?
        guard let publicKeyData = SecKeyCopyExternalRepresentation(publicKey, &error) as Data? else {
            return nil
        }
        return publicKeyData
    }

    /// Calculate SHA256 hash
    fileprivate func sha256Hash(data: Data) -> Data {
        var hash = [UInt8](repeating: 0, count: Int(CC_SHA256_DIGEST_LENGTH))
        data.withUnsafeBytes {
            _ = CC_SHA256($0.baseAddress, CC_LONG(data.count), &hash)
        }
        return Data(hash)
    }

    /// Log configuration status
    private func logConfiguration() {
        print("Certificate Pinning: strict=\(enforceStrict), domains=\(certificatePins.count)")
    }
}

// MARK: - URLSession Extension

extension URLSession {
    /// Create a URLSession with certificate pinning enabled
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
