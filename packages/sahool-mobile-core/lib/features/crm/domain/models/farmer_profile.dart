/// Farmer Profile Model
/// نموذج ملف المزارع
///
/// Represents a farmer/customer profile with contact info and preferences
library;

/// Farmer status
/// حالة المزارع
enum FarmerStatus {
  active,    // نشط
  inactive,  // غير نشط
  pending,   // قيد المراجعة
  suspended, // موقوف
}

/// Farmer segment for categorization
/// شريحة المزارع للتصنيف
enum FarmerSegment {
  premium,    // مميز (VIP)
  regular,    // عادي
  newFarmer,  // جديد
  potential,  // محتمل
}

/// Contact preference
/// تفضيل التواصل
enum ContactPreference {
  phone,     // هاتف
  whatsapp,  // واتساب
  sms,       // رسائل نصية
  email,     // بريد إلكتروني
  inPerson,  // شخصياً
}

/// Language preference
/// تفضيل اللغة
enum LanguagePreference {
  arabic,  // العربية
  english, // الإنجليزية
  both,    // كلاهما
}

/// Farmer Profile Model
/// نموذج ملف المزارع الشامل
class FarmerProfile {
  /// Unique identifier
  final String id;

  /// Tenant ID for multi-tenancy
  final String tenantId;

  /// Remote server ID
  final String? remoteId;

  /// Full name
  final String name;

  /// Name in Arabic
  final String? nameAr;

  /// Phone number (primary)
  final String phone;

  /// Alternative phone number
  final String? phoneAlt;

  /// WhatsApp number
  final String? whatsappNumber;

  /// Email address
  final String? email;

  /// National ID or registration number
  final String? nationalId;

  /// Profile photo URL
  final String? avatarUrl;

  // ─────────────────────────────────────────────────────────────────────────────
  // Location Information
  // ─────────────────────────────────────────────────────────────────────────────

  /// Governorate / Province
  final String? governorate;

  /// District / City
  final String? district;

  /// Village or area name
  final String? village;

  /// Full address
  final String? address;

  /// GPS latitude
  final double? latitude;

  /// GPS longitude
  final double? longitude;

  // ─────────────────────────────────────────────────────────────────────────────
  // Farm Information
  // ─────────────────────────────────────────────────────────────────────────────

  /// Total farm area in hectares
  final double? totalAreaHectares;

  /// Main crops grown
  final List<String> mainCrops;

  /// Number of fields
  final int? fieldCount;

  /// Water source (well, canal, rain)
  final String? waterSource;

  /// Irrigation type (drip, flood, sprinkler)
  final String? irrigationType;

  // ─────────────────────────────────────────────────────────────────────────────
  // CRM Information
  // ─────────────────────────────────────────────────────────────────────────────

  /// Farmer status
  final FarmerStatus status;

  /// Farmer segment/category
  final FarmerSegment segment;

  /// Preferred contact method
  final ContactPreference contactPreference;

  /// Preferred language
  final LanguagePreference languagePreference;

  /// Assigned agent/salesperson ID
  final String? assignedAgentId;

  /// Assigned agent name
  final String? assignedAgentName;

  /// Lead source (how they found us)
  final String? leadSource;

  /// Tags for filtering
  final List<String> tags;

  /// Custom notes
  final String? notes;

  // ─────────────────────────────────────────────────────────────────────────────
  // Statistics
  // ─────────────────────────────────────────────────────────────────────────────

  /// Total interactions count
  final int interactionCount;

  /// Last interaction date
  final DateTime? lastInteractionAt;

  /// Total purchase value
  final double? totalPurchaseValue;

  /// Customer lifetime value
  final double? lifetimeValue;

  /// Rating (1-5)
  final double? rating;

  // ─────────────────────────────────────────────────────────────────────────────
  // Metadata
  // ─────────────────────────────────────────────────────────────────────────────

  /// Is synced with server
  final bool synced;

  /// Is soft deleted
  final bool isDeleted;

  /// Created at timestamp
  final DateTime createdAt;

  /// Updated at timestamp
  final DateTime updatedAt;

  /// Additional metadata
  final Map<String, dynamic>? metadata;

  const FarmerProfile({
    required this.id,
    required this.tenantId,
    this.remoteId,
    required this.name,
    this.nameAr,
    required this.phone,
    this.phoneAlt,
    this.whatsappNumber,
    this.email,
    this.nationalId,
    this.avatarUrl,
    this.governorate,
    this.district,
    this.village,
    this.address,
    this.latitude,
    this.longitude,
    this.totalAreaHectares,
    this.mainCrops = const [],
    this.fieldCount,
    this.waterSource,
    this.irrigationType,
    this.status = FarmerStatus.active,
    this.segment = FarmerSegment.regular,
    this.contactPreference = ContactPreference.phone,
    this.languagePreference = LanguagePreference.arabic,
    this.assignedAgentId,
    this.assignedAgentName,
    this.leadSource,
    this.tags = const [],
    this.notes,
    this.interactionCount = 0,
    this.lastInteractionAt,
    this.totalPurchaseValue,
    this.lifetimeValue,
    this.rating,
    this.synced = false,
    this.isDeleted = false,
    required this.createdAt,
    required this.updatedAt,
    this.metadata,
  });

  // ============================================================
  // Computed Properties
  // ============================================================

  /// Display name (Arabic if available, otherwise English)
  String get displayName => nameAr ?? name;

  /// Full location string
  String get fullLocation {
    final parts = <String>[];
    if (village != null) parts.add(village!);
    if (district != null) parts.add(district!);
    if (governorate != null) parts.add(governorate!);
    return parts.isNotEmpty ? parts.join('، ') : 'غير محدد';
  }

  /// Has location coordinates
  bool get hasCoordinates => latitude != null && longitude != null;

  /// Is premium farmer
  bool get isPremium => segment == FarmerSegment.premium;

  /// Status in Arabic
  String get statusAr {
    switch (status) {
      case FarmerStatus.active:
        return 'نشط';
      case FarmerStatus.inactive:
        return 'غير نشط';
      case FarmerStatus.pending:
        return 'قيد المراجعة';
      case FarmerStatus.suspended:
        return 'موقوف';
    }
  }

  /// Segment in Arabic
  String get segmentAr {
    switch (segment) {
      case FarmerSegment.premium:
        return 'مميز';
      case FarmerSegment.regular:
        return 'عادي';
      case FarmerSegment.newFarmer:
        return 'جديد';
      case FarmerSegment.potential:
        return 'محتمل';
    }
  }

  /// Contact preference in Arabic
  String get contactPreferenceAr {
    switch (contactPreference) {
      case ContactPreference.phone:
        return 'هاتف';
      case ContactPreference.whatsapp:
        return 'واتساب';
      case ContactPreference.sms:
        return 'رسائل نصية';
      case ContactPreference.email:
        return 'بريد إلكتروني';
      case ContactPreference.inPerson:
        return 'شخصياً';
    }
  }

  /// Primary contact number (WhatsApp if available, otherwise phone)
  String get primaryContact => whatsappNumber ?? phone;

  // ============================================================
  // JSON Serialization
  // ============================================================

  /// Create from JSON
  factory FarmerProfile.fromJson(Map<String, dynamic> json) {
    final now = DateTime.now();

    return FarmerProfile(
      id: json['id'] as String? ?? json['_id'] as String,
      tenantId: json['tenant_id'] as String? ?? '',
      remoteId: json['remote_id'] as String?,
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      phone: json['phone'] as String? ?? '',
      phoneAlt: json['phone_alt'] as String?,
      whatsappNumber: json['whatsapp_number'] as String?,
      email: json['email'] as String?,
      nationalId: json['national_id'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      governorate: json['governorate'] as String?,
      district: json['district'] as String?,
      village: json['village'] as String?,
      address: json['address'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
      totalAreaHectares: (json['total_area_hectares'] as num?)?.toDouble(),
      mainCrops: (json['main_crops'] as List?)?.cast<String>() ?? [],
      fieldCount: json['field_count'] as int?,
      waterSource: json['water_source'] as String?,
      irrigationType: json['irrigation_type'] as String?,
      status: _parseStatus(json['status'] as String?),
      segment: _parseSegment(json['segment'] as String?),
      contactPreference: _parseContactPreference(json['contact_preference'] as String?),
      languagePreference: _parseLanguagePreference(json['language_preference'] as String?),
      assignedAgentId: json['assigned_agent_id'] as String?,
      assignedAgentName: json['assigned_agent_name'] as String?,
      leadSource: json['lead_source'] as String?,
      tags: (json['tags'] as List?)?.cast<String>() ?? [],
      notes: json['notes'] as String?,
      interactionCount: json['interaction_count'] as int? ?? 0,
      lastInteractionAt: json['last_interaction_at'] != null
          ? DateTime.parse(json['last_interaction_at'] as String)
          : null,
      totalPurchaseValue: (json['total_purchase_value'] as num?)?.toDouble(),
      lifetimeValue: (json['lifetime_value'] as num?)?.toDouble(),
      rating: (json['rating'] as num?)?.toDouble(),
      synced: json['synced'] as bool? ?? true,
      isDeleted: json['is_deleted'] as bool? ?? false,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : now,
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'] as String)
          : now,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'tenant_id': tenantId,
        'remote_id': remoteId,
        'name': name,
        'name_ar': nameAr,
        'phone': phone,
        'phone_alt': phoneAlt,
        'whatsapp_number': whatsappNumber,
        'email': email,
        'national_id': nationalId,
        'avatar_url': avatarUrl,
        'governorate': governorate,
        'district': district,
        'village': village,
        'address': address,
        'latitude': latitude,
        'longitude': longitude,
        'total_area_hectares': totalAreaHectares,
        'main_crops': mainCrops,
        'field_count': fieldCount,
        'water_source': waterSource,
        'irrigation_type': irrigationType,
        'status': status.name,
        'segment': segment.name,
        'contact_preference': contactPreference.name,
        'language_preference': languagePreference.name,
        'assigned_agent_id': assignedAgentId,
        'assigned_agent_name': assignedAgentName,
        'lead_source': leadSource,
        'tags': tags,
        'notes': notes,
        'interaction_count': interactionCount,
        'last_interaction_at': lastInteractionAt?.toIso8601String(),
        'total_purchase_value': totalPurchaseValue,
        'lifetime_value': lifetimeValue,
        'rating': rating,
        'synced': synced,
        'is_deleted': isDeleted,
        'created_at': createdAt.toIso8601String(),
        'updated_at': updatedAt.toIso8601String(),
        'metadata': metadata,
      };

  /// Copy with
  FarmerProfile copyWith({
    String? id,
    String? tenantId,
    String? remoteId,
    String? name,
    String? nameAr,
    String? phone,
    String? phoneAlt,
    String? whatsappNumber,
    String? email,
    String? nationalId,
    String? avatarUrl,
    String? governorate,
    String? district,
    String? village,
    String? address,
    double? latitude,
    double? longitude,
    double? totalAreaHectares,
    List<String>? mainCrops,
    int? fieldCount,
    String? waterSource,
    String? irrigationType,
    FarmerStatus? status,
    FarmerSegment? segment,
    ContactPreference? contactPreference,
    LanguagePreference? languagePreference,
    String? assignedAgentId,
    String? assignedAgentName,
    String? leadSource,
    List<String>? tags,
    String? notes,
    int? interactionCount,
    DateTime? lastInteractionAt,
    double? totalPurchaseValue,
    double? lifetimeValue,
    double? rating,
    bool? synced,
    bool? isDeleted,
    DateTime? createdAt,
    DateTime? updatedAt,
    Map<String, dynamic>? metadata,
  }) {
    return FarmerProfile(
      id: id ?? this.id,
      tenantId: tenantId ?? this.tenantId,
      remoteId: remoteId ?? this.remoteId,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      phone: phone ?? this.phone,
      phoneAlt: phoneAlt ?? this.phoneAlt,
      whatsappNumber: whatsappNumber ?? this.whatsappNumber,
      email: email ?? this.email,
      nationalId: nationalId ?? this.nationalId,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      governorate: governorate ?? this.governorate,
      district: district ?? this.district,
      village: village ?? this.village,
      address: address ?? this.address,
      latitude: latitude ?? this.latitude,
      longitude: longitude ?? this.longitude,
      totalAreaHectares: totalAreaHectares ?? this.totalAreaHectares,
      mainCrops: mainCrops ?? this.mainCrops,
      fieldCount: fieldCount ?? this.fieldCount,
      waterSource: waterSource ?? this.waterSource,
      irrigationType: irrigationType ?? this.irrigationType,
      status: status ?? this.status,
      segment: segment ?? this.segment,
      contactPreference: contactPreference ?? this.contactPreference,
      languagePreference: languagePreference ?? this.languagePreference,
      assignedAgentId: assignedAgentId ?? this.assignedAgentId,
      assignedAgentName: assignedAgentName ?? this.assignedAgentName,
      leadSource: leadSource ?? this.leadSource,
      tags: tags ?? this.tags,
      notes: notes ?? this.notes,
      interactionCount: interactionCount ?? this.interactionCount,
      lastInteractionAt: lastInteractionAt ?? this.lastInteractionAt,
      totalPurchaseValue: totalPurchaseValue ?? this.totalPurchaseValue,
      lifetimeValue: lifetimeValue ?? this.lifetimeValue,
      rating: rating ?? this.rating,
      synced: synced ?? this.synced,
      isDeleted: isDeleted ?? this.isDeleted,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FarmerProfile && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'FarmerProfile($id: $name, Phone: $phone)';
}

// Helper functions
FarmerStatus _parseStatus(String? status) {
  switch (status?.toLowerCase()) {
    case 'inactive':
      return FarmerStatus.inactive;
    case 'pending':
      return FarmerStatus.pending;
    case 'suspended':
      return FarmerStatus.suspended;
    case 'active':
    default:
      return FarmerStatus.active;
  }
}

FarmerSegment _parseSegment(String? segment) {
  switch (segment?.toLowerCase()) {
    case 'premium':
      return FarmerSegment.premium;
    case 'newfarmer':
    case 'new_farmer':
    case 'new':
      return FarmerSegment.newFarmer;
    case 'potential':
      return FarmerSegment.potential;
    case 'regular':
    default:
      return FarmerSegment.regular;
  }
}

ContactPreference _parseContactPreference(String? preference) {
  switch (preference?.toLowerCase()) {
    case 'whatsapp':
      return ContactPreference.whatsapp;
    case 'sms':
      return ContactPreference.sms;
    case 'email':
      return ContactPreference.email;
    case 'inperson':
    case 'in_person':
      return ContactPreference.inPerson;
    case 'phone':
    default:
      return ContactPreference.phone;
  }
}

LanguagePreference _parseLanguagePreference(String? preference) {
  switch (preference?.toLowerCase()) {
    case 'english':
      return LanguagePreference.english;
    case 'both':
      return LanguagePreference.both;
    case 'arabic':
    default:
      return LanguagePreference.arabic;
  }
}
