// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'otp_config.dart';

// **************************************************************************
// RiverpodGenerator
// **************************************************************************

String _$otpChannelConfigHash() => r'a7da3f3398515fc759ecff69a95191fbb899a2c5';

/// Copied from Dart SDK
class _SystemHash {
  _SystemHash._();

  static int combine(int hash, int value) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + value);
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x0007ffff & hash) << 10));
    return hash ^ (hash >> 6);
  }

  static int finish(int hash) {
    // ignore: parameter_assignments
    hash = 0x1fffffff & (hash + ((0x03ffffff & hash) << 3));
    // ignore: parameter_assignments
    hash = hash ^ (hash >> 11);
    return 0x1fffffff & (hash + ((0x00003fff & hash) << 15));
  }
}

/// Channel-specific configuration provider
///
/// Copied from [otpChannelConfig].
@ProviderFor(otpChannelConfig)
const otpChannelConfigProvider = OtpChannelConfigFamily();

/// Channel-specific configuration provider
///
/// Copied from [otpChannelConfig].
class OtpChannelConfigFamily extends Family<OTPChannelConfig?> {
  /// Channel-specific configuration provider
  ///
  /// Copied from [otpChannelConfig].
  const OtpChannelConfigFamily();

  /// Channel-specific configuration provider
  ///
  /// Copied from [otpChannelConfig].
  OtpChannelConfigProvider call(
    OTPChannel channel,
  ) {
    return OtpChannelConfigProvider(
      channel,
    );
  }

  @override
  OtpChannelConfigProvider getProviderOverride(
    covariant OtpChannelConfigProvider provider,
  ) {
    return call(
      provider.channel,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'otpChannelConfigProvider';
}

/// Channel-specific configuration provider
///
/// Copied from [otpChannelConfig].
class OtpChannelConfigProvider extends AutoDisposeProvider<OTPChannelConfig?> {
  /// Channel-specific configuration provider
  ///
  /// Copied from [otpChannelConfig].
  OtpChannelConfigProvider(
    OTPChannel channel,
  ) : this._internal(
          (ref) => otpChannelConfig(
            ref as OtpChannelConfigRef,
            channel,
          ),
          from: otpChannelConfigProvider,
          name: r'otpChannelConfigProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$otpChannelConfigHash,
          dependencies: OtpChannelConfigFamily._dependencies,
          allTransitiveDependencies:
              OtpChannelConfigFamily._allTransitiveDependencies,
          channel: channel,
        );

  OtpChannelConfigProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.channel,
  }) : super.internal();

  final OTPChannel channel;

  @override
  Override overrideWith(
    OTPChannelConfig? Function(OtpChannelConfigRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: OtpChannelConfigProvider._internal(
        (ref) => create(ref as OtpChannelConfigRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        channel: channel,
      ),
    );
  }

  @override
  AutoDisposeProviderElement<OTPChannelConfig?> createElement() {
    return _OtpChannelConfigProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is OtpChannelConfigProvider && other.channel == channel;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, channel.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin OtpChannelConfigRef on AutoDisposeProviderRef<OTPChannelConfig?> {
  /// The parameter `channel` of this provider.
  OTPChannel get channel;
}

class _OtpChannelConfigProviderElement
    extends AutoDisposeProviderElement<OTPChannelConfig?>
    with OtpChannelConfigRef {
  _OtpChannelConfigProviderElement(super.provider);

  @override
  OTPChannel get channel => (origin as OtpChannelConfigProvider).channel;
}

String _$enabledOTPChannelsHash() =>
    r'ba62e3c4904d5a8c9136c76baa1944853e5f1eea';

/// Enabled channels provider (sorted by priority)
///
/// Copied from [enabledOTPChannels].
@ProviderFor(enabledOTPChannels)
final enabledOTPChannelsProvider =
    AutoDisposeProvider<List<MapEntry<String, OTPChannelConfig>>>.internal(
  enabledOTPChannels,
  name: r'enabledOTPChannelsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$enabledOTPChannelsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef EnabledOTPChannelsRef
    = AutoDisposeProviderRef<List<MapEntry<String, OTPChannelConfig>>>;
String _$primaryOTPChannelsHash() =>
    r'0121123a8d22ea4e278469f5679e77fd703aec15';

/// Primary channels provider (for UI display)
///
/// Copied from [primaryOTPChannels].
@ProviderFor(primaryOTPChannels)
final primaryOTPChannelsProvider =
    AutoDisposeProvider<List<MapEntry<String, OTPChannelConfig>>>.internal(
  primaryOTPChannels,
  name: r'primaryOTPChannelsProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$primaryOTPChannelsHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef PrimaryOTPChannelsRef
    = AutoDisposeProviderRef<List<MapEntry<String, OTPChannelConfig>>>;
String _$otpRateLimitConfigHash() =>
    r'553fb513490acea453ba15b27797b0ba5f236895';

/// Rate limit configuration provider
///
/// Copied from [otpRateLimitConfig].
@ProviderFor(otpRateLimitConfig)
final otpRateLimitConfigProvider =
    AutoDisposeProvider<OTPRateLimitConfig>.internal(
  otpRateLimitConfig,
  name: r'otpRateLimitConfigProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$otpRateLimitConfigHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
typedef OtpRateLimitConfigRef = AutoDisposeProviderRef<OTPRateLimitConfig>;
String _$otpFeatureFlagHash() => r'e73704bbdd267c1aaa51706e1580cab77b7285ba';

/// Feature flag provider
///
/// Copied from [otpFeatureFlag].
@ProviderFor(otpFeatureFlag)
const otpFeatureFlagProvider = OtpFeatureFlagFamily();

/// Feature flag provider
///
/// Copied from [otpFeatureFlag].
class OtpFeatureFlagFamily extends Family<bool> {
  /// Feature flag provider
  ///
  /// Copied from [otpFeatureFlag].
  const OtpFeatureFlagFamily();

  /// Feature flag provider
  ///
  /// Copied from [otpFeatureFlag].
  OtpFeatureFlagProvider call(
    String featureName,
  ) {
    return OtpFeatureFlagProvider(
      featureName,
    );
  }

  @override
  OtpFeatureFlagProvider getProviderOverride(
    covariant OtpFeatureFlagProvider provider,
  ) {
    return call(
      provider.featureName,
    );
  }

  static const Iterable<ProviderOrFamily>? _dependencies = null;

  @override
  Iterable<ProviderOrFamily>? get dependencies => _dependencies;

  static const Iterable<ProviderOrFamily>? _allTransitiveDependencies = null;

  @override
  Iterable<ProviderOrFamily>? get allTransitiveDependencies =>
      _allTransitiveDependencies;

  @override
  String? get name => r'otpFeatureFlagProvider';
}

/// Feature flag provider
///
/// Copied from [otpFeatureFlag].
class OtpFeatureFlagProvider extends AutoDisposeProvider<bool> {
  /// Feature flag provider
  ///
  /// Copied from [otpFeatureFlag].
  OtpFeatureFlagProvider(
    String featureName,
  ) : this._internal(
          (ref) => otpFeatureFlag(
            ref as OtpFeatureFlagRef,
            featureName,
          ),
          from: otpFeatureFlagProvider,
          name: r'otpFeatureFlagProvider',
          debugGetCreateSourceHash:
              const bool.fromEnvironment('dart.vm.product')
                  ? null
                  : _$otpFeatureFlagHash,
          dependencies: OtpFeatureFlagFamily._dependencies,
          allTransitiveDependencies:
              OtpFeatureFlagFamily._allTransitiveDependencies,
          featureName: featureName,
        );

  OtpFeatureFlagProvider._internal(
    super._createNotifier, {
    required super.name,
    required super.dependencies,
    required super.allTransitiveDependencies,
    required super.debugGetCreateSourceHash,
    required super.from,
    required this.featureName,
  }) : super.internal();

  final String featureName;

  @override
  Override overrideWith(
    bool Function(OtpFeatureFlagRef provider) create,
  ) {
    return ProviderOverride(
      origin: this,
      override: OtpFeatureFlagProvider._internal(
        (ref) => create(ref as OtpFeatureFlagRef),
        from: from,
        name: null,
        dependencies: null,
        allTransitiveDependencies: null,
        debugGetCreateSourceHash: null,
        featureName: featureName,
      ),
    );
  }

  @override
  AutoDisposeProviderElement<bool> createElement() {
    return _OtpFeatureFlagProviderElement(this);
  }

  @override
  bool operator ==(Object other) {
    return other is OtpFeatureFlagProvider && other.featureName == featureName;
  }

  @override
  int get hashCode {
    var hash = _SystemHash.combine(0, runtimeType.hashCode);
    hash = _SystemHash.combine(hash, featureName.hashCode);

    return _SystemHash.finish(hash);
  }
}

@Deprecated('Will be removed in 3.0. Use Ref instead')
// ignore: unused_element
mixin OtpFeatureFlagRef on AutoDisposeProviderRef<bool> {
  /// The parameter `featureName` of this provider.
  String get featureName;
}

class _OtpFeatureFlagProviderElement extends AutoDisposeProviderElement<bool>
    with OtpFeatureFlagRef {
  _OtpFeatureFlagProviderElement(super.provider);

  @override
  String get featureName => (origin as OtpFeatureFlagProvider).featureName;
}

String _$oTPConfigNotifierHash() => r'1fcd1d44930c6a5721fdafaeb14282f0ab014c38';

/// Main OTP Configuration provider
/// موفر التكوين الرئيسي لـ OTP
///
/// Copied from [OTPConfigNotifier].
@ProviderFor(OTPConfigNotifier)
final oTPConfigNotifierProvider =
    AutoDisposeAsyncNotifierProvider<OTPConfigNotifier, OTPConfig>.internal(
  OTPConfigNotifier.new,
  name: r'oTPConfigNotifierProvider',
  debugGetCreateSourceHash: const bool.fromEnvironment('dart.vm.product')
      ? null
      : _$oTPConfigNotifierHash,
  dependencies: null,
  allTransitiveDependencies: null,
);

typedef _$OTPConfigNotifier = AutoDisposeAsyncNotifier<OTPConfig>;
// ignore_for_file: type=lint
// ignore_for_file: subtype_of_sealed_class, invalid_use_of_internal_member, invalid_use_of_visible_for_testing_member, deprecated_member_use_from_same_package
