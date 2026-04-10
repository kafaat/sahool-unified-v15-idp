-- drift:safe reason=Every CREATE INDEX in this file targets a table that is
-- CREATE TABLE'd in this same migration (YOLO26 detections, terrain analyses,
-- hydrology results, leveling plans, edge device registrations). At CREATE INDEX
-- time those tables have zero rows, so the non-CONCURRENTLY builds are
-- instantaneous and cannot lock any production data. This file is executed
-- through the SAHOOL migration runner inside a single transaction, so
-- CREATE INDEX CONCURRENTLY is unusable here by design.
-- ============================================================================
-- SAHOOL Platform - Integration Tables Migration
-- Version: V20260131
-- Description: Add tables for YOLO26 detections, terrain analysis, hydrology,
--              and edge computing services
-- ============================================================================
-- وصف: إضافة جداول لاكتشافات YOLO26، تحليل التضاريس، الهيدرولوجيا،
--       وخدمات الحوسبة الطرفية
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ============================================================================
-- Table: yolo26_detections
-- Description: Store YOLO26 object detection results for pest, disease, weed,
--              and plant detection in agricultural fields
-- الوصف: تخزين نتائج الكشف بنموذج YOLO26 للآفات، الأمراض، الأعشاب الضارة،
--        والنباتات في الحقول الزراعية
-- ============================================================================
CREATE TABLE IF NOT EXISTS yolo26_detections (
    -- Primary key | المفتاح الأساسي
    detection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key to fields table | المفتاح الخارجي لجدول الحقول
    field_id UUID NOT NULL,

    -- Reference to source image | مرجع الصورة المصدر
    image_id UUID NOT NULL,

    -- Detection classification | تصنيف الكشف
    -- pest: آفة | disease: مرض | weed: عشب ضار | plant: نبات
    detection_type VARCHAR(20) NOT NULL CHECK (detection_type IN ('pest', 'disease', 'weed', 'plant')),

    -- Class name in English | اسم الفئة بالإنجليزية
    class_name VARCHAR(50) NOT NULL,

    -- Class name in Arabic | اسم الفئة بالعربية
    class_name_ar VARCHAR(50),

    -- Detection confidence score (0.0 - 1.0) | درجة الثقة في الكشف
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),

    -- Bounding box coordinates (normalized 0-1 or pixel values)
    -- إحداثيات مربع الإحاطة
    bbox_x_min FLOAT NOT NULL,
    bbox_y_min FLOAT NOT NULL,
    bbox_x_max FLOAT NOT NULL,
    bbox_y_max FLOAT NOT NULL,

    -- Segmentation mask in RLE or polygon format | قناع التجزئة
    segmentation_mask JSONB,

    -- Model version used for detection | إصدار النموذج المستخدم
    model_version VARCHAR(20) NOT NULL,

    -- Inference time in milliseconds | وقت الاستدلال بالميلي ثانية
    inference_time_ms FLOAT,

    -- Device where inference was performed | الجهاز الذي تم فيه الاستدلال
    -- cloud: سحابي | edge: طرفي | mobile: جوال
    device_type VARCHAR(20) NOT NULL DEFAULT 'cloud' CHECK (device_type IN ('cloud', 'edge', 'mobile')),

    -- Timestamps | الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comments on yolo26_detections columns
COMMENT ON TABLE yolo26_detections IS 'YOLO26 object detection results for agricultural imagery | نتائج الكشف بنموذج YOLO26 للصور الزراعية';
COMMENT ON COLUMN yolo26_detections.detection_id IS 'Unique detection identifier | معرف الكشف الفريد';
COMMENT ON COLUMN yolo26_detections.field_id IS 'Reference to the agricultural field | مرجع الحقل الزراعي';
COMMENT ON COLUMN yolo26_detections.image_id IS 'Reference to the source image | مرجع الصورة المصدر';
COMMENT ON COLUMN yolo26_detections.detection_type IS 'Type of detection: pest, disease, weed, plant | نوع الكشف: آفة، مرض، عشب ضار، نبات';
COMMENT ON COLUMN yolo26_detections.class_name IS 'Detection class name in English | اسم فئة الكشف بالإنجليزية';
COMMENT ON COLUMN yolo26_detections.class_name_ar IS 'Detection class name in Arabic | اسم فئة الكشف بالعربية';
COMMENT ON COLUMN yolo26_detections.confidence IS 'Model confidence score (0.0-1.0) | درجة ثقة النموذج';
COMMENT ON COLUMN yolo26_detections.bbox_x_min IS 'Bounding box minimum X coordinate | إحداثي X الأدنى لمربع الإحاطة';
COMMENT ON COLUMN yolo26_detections.bbox_y_min IS 'Bounding box minimum Y coordinate | إحداثي Y الأدنى لمربع الإحاطة';
COMMENT ON COLUMN yolo26_detections.bbox_x_max IS 'Bounding box maximum X coordinate | إحداثي X الأقصى لمربع الإحاطة';
COMMENT ON COLUMN yolo26_detections.bbox_y_max IS 'Bounding box maximum Y coordinate | إحداثي Y الأقصى لمربع الإحاطة';
COMMENT ON COLUMN yolo26_detections.segmentation_mask IS 'Instance segmentation mask data | بيانات قناع تجزئة النموذج';
COMMENT ON COLUMN yolo26_detections.model_version IS 'YOLO26 model version used | إصدار نموذج YOLO26 المستخدم';
COMMENT ON COLUMN yolo26_detections.inference_time_ms IS 'Inference time in milliseconds | وقت الاستدلال بالميلي ثانية';
COMMENT ON COLUMN yolo26_detections.device_type IS 'Device type: cloud, edge, mobile | نوع الجهاز: سحابي، طرفي، جوال';
COMMENT ON COLUMN yolo26_detections.created_at IS 'Detection timestamp | الطابع الزمني للكشف';

-- ============================================================================
-- Table: terrain_analyses
-- Description: Store terrain analysis results including elevation, slope,
--              aspect, and erosion risk assessments
-- الوصف: تخزين نتائج تحليل التضاريس بما في ذلك الارتفاع، الانحدار،
--        الاتجاه، وتقييمات مخاطر التعرية
-- ============================================================================
CREATE TABLE IF NOT EXISTS terrain_analyses (
    -- Primary key | المفتاح الأساسي
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key to fields table | المفتاح الخارجي لجدول الحقول
    field_id UUID NOT NULL,

    -- DEM (Digital Elevation Model) source | مصدر نموذج الارتفاع الرقمي
    dem_source VARCHAR(50) NOT NULL,

    -- DEM resolution in meters | دقة نموذج الارتفاع بالأمتار
    dem_resolution_m FLOAT NOT NULL,

    -- Elevation statistics in meters | إحصائيات الارتفاع بالأمتار
    elevation_min FLOAT NOT NULL,
    elevation_max FLOAT NOT NULL,
    elevation_mean FLOAT NOT NULL,
    elevation_range FLOAT NOT NULL,

    -- Slope statistics | إحصائيات الانحدار
    slope_mean FLOAT NOT NULL,
    slope_max FLOAT NOT NULL,
    slope_class VARCHAR(20) NOT NULL, -- flat, gentle, moderate, steep, very_steep
    slope_distribution JSONB, -- Distribution by slope class | توزيع حسب فئة الانحدار

    -- Aspect (slope direction) | الاتجاه (اتجاه الانحدار)
    aspect_dominant VARCHAR(10), -- N, NE, E, SE, S, SW, W, NW, flat
    aspect_distribution JSONB, -- Distribution by cardinal direction | توزيع حسب الاتجاهات الأساسية

    -- Flow accumulation | تراكم التدفق
    flow_accumulation_max FLOAT,
    stream_network_exists BOOLEAN DEFAULT FALSE,

    -- Topographic Wetness Index | مؤشر الرطوبة الطبوغرافية
    twi_mean FLOAT,
    twi_distribution JSONB,

    -- Risk assessments | تقييمات المخاطر
    -- low, moderate, high, very_high | منخفض، متوسط، عالي، عالي جداً
    erosion_risk VARCHAR(20),
    waterlogging_risk VARCHAR(20),

    -- Leveling recommendations | توصيات التسوية
    requires_leveling BOOLEAN DEFAULT FALSE,
    leveling_priority VARCHAR(20), -- none, low, medium, high, critical
    estimated_volume_m3 FLOAT, -- Estimated soil volume to move | حجم التربة المقدر للنقل

    -- Timestamps | الطوابع الزمنية
    analyzed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comments on terrain_analyses columns
COMMENT ON TABLE terrain_analyses IS 'Terrain analysis results for agricultural fields | نتائج تحليل التضاريس للحقول الزراعية';
COMMENT ON COLUMN terrain_analyses.analysis_id IS 'Unique analysis identifier | معرف التحليل الفريد';
COMMENT ON COLUMN terrain_analyses.field_id IS 'Reference to the agricultural field | مرجع الحقل الزراعي';
COMMENT ON COLUMN terrain_analyses.dem_source IS 'Source of Digital Elevation Model (SRTM, ASTER, LiDAR) | مصدر نموذج الارتفاع الرقمي';
COMMENT ON COLUMN terrain_analyses.dem_resolution_m IS 'DEM resolution in meters | دقة نموذج الارتفاع بالأمتار';
COMMENT ON COLUMN terrain_analyses.elevation_min IS 'Minimum elevation in meters | أدنى ارتفاع بالأمتار';
COMMENT ON COLUMN terrain_analyses.elevation_max IS 'Maximum elevation in meters | أقصى ارتفاع بالأمتار';
COMMENT ON COLUMN terrain_analyses.elevation_mean IS 'Mean elevation in meters | متوسط الارتفاع بالأمتار';
COMMENT ON COLUMN terrain_analyses.elevation_range IS 'Elevation range in meters | نطاق الارتفاع بالأمتار';
COMMENT ON COLUMN terrain_analyses.slope_mean IS 'Mean slope in degrees | متوسط الانحدار بالدرجات';
COMMENT ON COLUMN terrain_analyses.slope_max IS 'Maximum slope in degrees | أقصى انحدار بالدرجات';
COMMENT ON COLUMN terrain_analyses.slope_class IS 'Slope classification: flat, gentle, moderate, steep, very_steep | تصنيف الانحدار';
COMMENT ON COLUMN terrain_analyses.slope_distribution IS 'Slope distribution by class | توزيع الانحدار حسب الفئة';
COMMENT ON COLUMN terrain_analyses.aspect_dominant IS 'Dominant aspect direction | الاتجاه السائد';
COMMENT ON COLUMN terrain_analyses.aspect_distribution IS 'Aspect distribution by cardinal direction | توزيع الاتجاه';
COMMENT ON COLUMN terrain_analyses.flow_accumulation_max IS 'Maximum flow accumulation value | أقصى قيمة لتراكم التدفق';
COMMENT ON COLUMN terrain_analyses.stream_network_exists IS 'Whether stream network exists | وجود شبكة مجاري مائية';
COMMENT ON COLUMN terrain_analyses.twi_mean IS 'Mean Topographic Wetness Index | متوسط مؤشر الرطوبة الطبوغرافية';
COMMENT ON COLUMN terrain_analyses.twi_distribution IS 'TWI distribution data | توزيع مؤشر الرطوبة';
COMMENT ON COLUMN terrain_analyses.erosion_risk IS 'Erosion risk level: low, moderate, high, very_high | مستوى خطر التعرية';
COMMENT ON COLUMN terrain_analyses.waterlogging_risk IS 'Waterlogging risk level | مستوى خطر التشبع المائي';
COMMENT ON COLUMN terrain_analyses.requires_leveling IS 'Whether field requires leveling | هل يحتاج الحقل للتسوية';
COMMENT ON COLUMN terrain_analyses.leveling_priority IS 'Leveling priority: none, low, medium, high, critical | أولوية التسوية';
COMMENT ON COLUMN terrain_analyses.estimated_volume_m3 IS 'Estimated soil volume to move in cubic meters | حجم التربة المقدر للنقل بالمتر المكعب';
COMMENT ON COLUMN terrain_analyses.analyzed_at IS 'Analysis timestamp | الطابع الزمني للتحليل';

-- ============================================================================
-- Table: hydrology_analyses
-- Description: Store hydrology analysis results including stream networks,
--              basins, and depressions
-- الوصف: تخزين نتائج التحليل الهيدرولوجي بما في ذلك شبكات المجاري المائية،
--        الأحواض، والمنخفضات
-- ============================================================================
CREATE TABLE IF NOT EXISTS hydrology_analyses (
    -- Primary key | المفتاح الأساسي
    hydrology_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key to terrain_analyses | المفتاح الخارجي لجدول تحليل التضاريس
    terrain_analysis_id UUID NOT NULL,

    -- Stream network statistics | إحصائيات شبكة المجاري المائية
    stream_count INTEGER NOT NULL DEFAULT 0,
    total_stream_length_m FLOAT NOT NULL DEFAULT 0,

    -- Basin statistics | إحصائيات الأحواض
    basin_count INTEGER NOT NULL DEFAULT 0,

    -- Depression analysis | تحليل المنخفضات
    depression_count INTEGER NOT NULL DEFAULT 0,
    total_depression_area_m2 FLOAT NOT NULL DEFAULT 0,

    -- Detailed depression data | بيانات المنخفضات التفصيلية
    -- Array of {id, area_m2, depth_m, volume_m3, centroid, risk_level}
    depressions JSONB,

    -- Timestamps | الطوابع الزمنية
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comments on hydrology_analyses columns
COMMENT ON TABLE hydrology_analyses IS 'Hydrology analysis results for agricultural fields | نتائج التحليل الهيدرولوجي للحقول الزراعية';
COMMENT ON COLUMN hydrology_analyses.hydrology_id IS 'Unique hydrology analysis identifier | معرف التحليل الهيدرولوجي الفريد';
COMMENT ON COLUMN hydrology_analyses.terrain_analysis_id IS 'Reference to parent terrain analysis | مرجع تحليل التضاريس الأصلي';
COMMENT ON COLUMN hydrology_analyses.stream_count IS 'Number of stream segments | عدد قطاعات المجاري المائية';
COMMENT ON COLUMN hydrology_analyses.total_stream_length_m IS 'Total stream network length in meters | إجمالي طول شبكة المجاري بالأمتار';
COMMENT ON COLUMN hydrology_analyses.basin_count IS 'Number of drainage basins | عدد أحواض الصرف';
COMMENT ON COLUMN hydrology_analyses.depression_count IS 'Number of depressions/sinks | عدد المنخفضات';
COMMENT ON COLUMN hydrology_analyses.total_depression_area_m2 IS 'Total depression area in square meters | إجمالي مساحة المنخفضات بالمتر المربع';
COMMENT ON COLUMN hydrology_analyses.depressions IS 'Detailed depression data as JSON array | بيانات المنخفضات التفصيلية';
COMMENT ON COLUMN hydrology_analyses.created_at IS 'Analysis timestamp | الطابع الزمني للتحليل';

-- ============================================================================
-- Table: edge_devices
-- Description: Store edge computing device information for distributed
--              inference and processing
-- الوصف: تخزين معلومات أجهزة الحوسبة الطرفية للاستدلال والمعالجة الموزعة
-- ============================================================================
CREATE TABLE IF NOT EXISTS edge_devices (
    -- Primary key | المفتاح الأساسي
    device_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Device identification | تحديد الجهاز
    device_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) NOT NULL, -- jetson_nano, jetson_orin, raspberry_pi, mobile, etc.

    -- Device status | حالة الجهاز
    -- online, offline, maintenance, error | متصل، غير متصل، صيانة، خطأ
    status VARCHAR(20) NOT NULL DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'maintenance', 'error')),

    -- Hardware specifications | مواصفات العتاد
    memory_gb FLOAT,
    storage_gb FLOAT,

    -- Deployed models | النماذج المنشورة
    -- Array of {model_name, version, size_mb, last_updated}
    deployed_models JSONB,

    -- Current location | الموقع الحالي
    current_location GEOMETRY(Point, 4326),

    -- Usage statistics | إحصائيات الاستخدام
    total_inferences BIGINT NOT NULL DEFAULT 0,

    -- Timestamps | الطوابع الزمنية
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comments on edge_devices columns
COMMENT ON TABLE edge_devices IS 'Edge computing devices for distributed AI inference | أجهزة الحوسبة الطرفية للاستدلال الموزع';
COMMENT ON COLUMN edge_devices.device_id IS 'Unique device identifier | معرف الجهاز الفريد';
COMMENT ON COLUMN edge_devices.device_name IS 'Human-readable device name | اسم الجهاز المقروء';
COMMENT ON COLUMN edge_devices.device_type IS 'Device type/model | نوع/موديل الجهاز';
COMMENT ON COLUMN edge_devices.status IS 'Device status: online, offline, maintenance, error | حالة الجهاز';
COMMENT ON COLUMN edge_devices.memory_gb IS 'Device memory in gigabytes | ذاكرة الجهاز بالجيجابايت';
COMMENT ON COLUMN edge_devices.storage_gb IS 'Device storage in gigabytes | تخزين الجهاز بالجيجابايت';
COMMENT ON COLUMN edge_devices.deployed_models IS 'List of deployed AI models | قائمة النماذج المنشورة';
COMMENT ON COLUMN edge_devices.current_location IS 'Current GPS location of device | الموقع الحالي للجهاز';
COMMENT ON COLUMN edge_devices.total_inferences IS 'Total number of inferences performed | إجمالي عدد الاستدلالات';
COMMENT ON COLUMN edge_devices.last_sync_at IS 'Last synchronization timestamp | آخر وقت مزامنة';
COMMENT ON COLUMN edge_devices.created_at IS 'Device registration timestamp | وقت تسجيل الجهاز';

-- ============================================================================
-- Table: edge_jobs
-- Description: Store edge computing job queue and execution history
-- الوصف: تخزين قائمة انتظار وسجل تنفيذ مهام الحوسبة الطرفية
-- ============================================================================
CREATE TABLE IF NOT EXISTS edge_jobs (
    -- Primary key | المفتاح الأساسي
    job_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Foreign key to edge_devices | المفتاح الخارجي لجدول الأجهزة الطرفية
    device_id UUID NOT NULL,

    -- Job type | نوع المهمة
    -- detection, classification, segmentation, analysis
    job_type VARCHAR(50) NOT NULL,

    -- Job status | حالة المهمة
    -- pending, running, completed, failed, cancelled
    -- معلق، قيد التنفيذ، مكتمل، فشل، ملغى
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),

    -- Input data | بيانات الإدخال
    -- {image_ids, model_name, parameters, etc.}
    input_data JSONB,

    -- Output data | بيانات الإخراج
    -- {detection_ids, results, errors, etc.}
    output_data JSONB,

    -- Timestamps | الطوابع الزمنية
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Comments on edge_jobs columns
COMMENT ON TABLE edge_jobs IS 'Edge computing job queue and history | قائمة انتظار وسجل مهام الحوسبة الطرفية';
COMMENT ON COLUMN edge_jobs.job_id IS 'Unique job identifier | معرف المهمة الفريد';
COMMENT ON COLUMN edge_jobs.device_id IS 'Reference to the edge device | مرجع الجهاز الطرفي';
COMMENT ON COLUMN edge_jobs.job_type IS 'Type of job: detection, classification, segmentation, analysis | نوع المهمة';
COMMENT ON COLUMN edge_jobs.status IS 'Job status: pending, running, completed, failed, cancelled | حالة المهمة';
COMMENT ON COLUMN edge_jobs.input_data IS 'Job input parameters and data references | معاملات ومراجع بيانات الإدخال';
COMMENT ON COLUMN edge_jobs.output_data IS 'Job output results and data references | نتائج ومراجع بيانات الإخراج';
COMMENT ON COLUMN edge_jobs.started_at IS 'Job start timestamp | وقت بدء المهمة';
COMMENT ON COLUMN edge_jobs.completed_at IS 'Job completion timestamp | وقت اكتمال المهمة';
COMMENT ON COLUMN edge_jobs.created_at IS 'Job creation timestamp | وقت إنشاء المهمة';

-- ============================================================================
-- INDEXES | الفهارس
-- ============================================================================

-- yolo26_detections indexes
CREATE INDEX idx_yolo26_detections_field_id ON yolo26_detections(field_id);
CREATE INDEX idx_yolo26_detections_image_id ON yolo26_detections(image_id);
CREATE INDEX idx_yolo26_detections_detection_type ON yolo26_detections(detection_type);
CREATE INDEX idx_yolo26_detections_class_name ON yolo26_detections(class_name);
CREATE INDEX idx_yolo26_detections_confidence ON yolo26_detections(confidence);
CREATE INDEX idx_yolo26_detections_model_version ON yolo26_detections(model_version);
CREATE INDEX idx_yolo26_detections_device_type ON yolo26_detections(device_type);
CREATE INDEX idx_yolo26_detections_created_at ON yolo26_detections(created_at DESC);
-- Composite index for common query pattern | فهرس مركب للاستعلامات الشائعة
CREATE INDEX idx_yolo26_detections_field_type_created ON yolo26_detections(field_id, detection_type, created_at DESC);

-- terrain_analyses indexes
CREATE INDEX idx_terrain_analyses_field_id ON terrain_analyses(field_id);
CREATE INDEX idx_terrain_analyses_erosion_risk ON terrain_analyses(erosion_risk);
CREATE INDEX idx_terrain_analyses_waterlogging_risk ON terrain_analyses(waterlogging_risk);
CREATE INDEX idx_terrain_analyses_requires_leveling ON terrain_analyses(requires_leveling) WHERE requires_leveling = TRUE;
CREATE INDEX idx_terrain_analyses_analyzed_at ON terrain_analyses(analyzed_at DESC);
-- Composite index for risk assessment queries | فهرس مركب لاستعلامات تقييم المخاطر
CREATE INDEX idx_terrain_analyses_field_risks ON terrain_analyses(field_id, erosion_risk, waterlogging_risk);

-- hydrology_analyses indexes
CREATE INDEX idx_hydrology_analyses_terrain_analysis_id ON hydrology_analyses(terrain_analysis_id);
CREATE INDEX idx_hydrology_analyses_depression_count ON hydrology_analyses(depression_count) WHERE depression_count > 0;
CREATE INDEX idx_hydrology_analyses_created_at ON hydrology_analyses(created_at DESC);

-- edge_devices indexes
CREATE INDEX idx_edge_devices_device_type ON edge_devices(device_type);
CREATE INDEX idx_edge_devices_status ON edge_devices(status);
CREATE INDEX idx_edge_devices_last_sync_at ON edge_devices(last_sync_at DESC);
CREATE INDEX idx_edge_devices_created_at ON edge_devices(created_at DESC);
-- Spatial index for device locations | فهرس مكاني لمواقع الأجهزة
CREATE INDEX idx_edge_devices_location ON edge_devices USING GIST(current_location);
-- Index for online devices only | فهرس للأجهزة المتصلة فقط
CREATE INDEX idx_edge_devices_online ON edge_devices(device_id) WHERE status = 'online';

-- edge_jobs indexes
CREATE INDEX idx_edge_jobs_device_id ON edge_jobs(device_id);
CREATE INDEX idx_edge_jobs_job_type ON edge_jobs(job_type);
CREATE INDEX idx_edge_jobs_status ON edge_jobs(status);
CREATE INDEX idx_edge_jobs_created_at ON edge_jobs(created_at DESC);
CREATE INDEX idx_edge_jobs_started_at ON edge_jobs(started_at DESC);
CREATE INDEX idx_edge_jobs_completed_at ON edge_jobs(completed_at DESC);
-- Composite index for device job history | فهرس مركب لسجل مهام الجهاز
CREATE INDEX idx_edge_jobs_device_status_created ON edge_jobs(device_id, status, created_at DESC);
-- Index for pending jobs queue | فهرس لقائمة المهام المعلقة
CREATE INDEX idx_edge_jobs_pending ON edge_jobs(device_id, created_at) WHERE status = 'pending';

-- ============================================================================
-- FOREIGN KEY CONSTRAINTS | قيود المفاتيح الخارجية
-- ============================================================================

-- Note: The 'fields' table is assumed to exist in the database
-- ملاحظة: يُفترض وجود جدول 'fields' في قاعدة البيانات

-- yolo26_detections -> fields (NOT VALID to avoid full table scan during migration)
ALTER TABLE yolo26_detections
    ADD CONSTRAINT fk_yolo26_detections_field
    FOREIGN KEY (field_id)
    REFERENCES fields(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE NOT VALID;
ALTER TABLE yolo26_detections VALIDATE CONSTRAINT fk_yolo26_detections_field;

-- terrain_analyses -> fields
ALTER TABLE terrain_analyses
    ADD CONSTRAINT fk_terrain_analyses_field
    FOREIGN KEY (field_id)
    REFERENCES fields(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE NOT VALID;
ALTER TABLE terrain_analyses VALIDATE CONSTRAINT fk_terrain_analyses_field;

-- hydrology_analyses -> terrain_analyses
ALTER TABLE hydrology_analyses
    ADD CONSTRAINT fk_hydrology_analyses_terrain
    FOREIGN KEY (terrain_analysis_id)
    REFERENCES terrain_analyses(analysis_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE NOT VALID;
ALTER TABLE hydrology_analyses VALIDATE CONSTRAINT fk_hydrology_analyses_terrain;

-- edge_jobs -> edge_devices
ALTER TABLE edge_jobs
    ADD CONSTRAINT fk_edge_jobs_device
    FOREIGN KEY (device_id)
    REFERENCES edge_devices(device_id)
    ON DELETE CASCADE
    ON UPDATE CASCADE NOT VALID;
ALTER TABLE edge_jobs VALIDATE CONSTRAINT fk_edge_jobs_device;

-- ============================================================================
-- ADDITIONAL CONSTRAINTS | قيود إضافية
-- ============================================================================

-- Ensure bounding box coordinates are valid (NOT VALID to avoid full scan)
-- التأكد من صحة إحداثيات مربع الإحاطة
ALTER TABLE yolo26_detections
    ADD CONSTRAINT chk_yolo26_bbox_valid
    CHECK (bbox_x_min <= bbox_x_max AND bbox_y_min <= bbox_y_max) NOT VALID;
ALTER TABLE yolo26_detections VALIDATE CONSTRAINT chk_yolo26_bbox_valid;

-- Ensure elevation range is consistent
-- التأكد من اتساق نطاق الارتفاع
ALTER TABLE terrain_analyses
    ADD CONSTRAINT chk_terrain_elevation_valid
    CHECK (elevation_min <= elevation_mean AND elevation_mean <= elevation_max) NOT VALID;
ALTER TABLE terrain_analyses VALIDATE CONSTRAINT chk_terrain_elevation_valid;

-- Ensure DEM resolution is positive
-- التأكد من أن دقة DEM موجبة
ALTER TABLE terrain_analyses
    ADD CONSTRAINT chk_terrain_dem_resolution_positive
    CHECK (dem_resolution_m > 0) NOT VALID;
ALTER TABLE terrain_analyses VALIDATE CONSTRAINT chk_terrain_dem_resolution_positive;

-- Ensure job timestamps are logical
-- التأكد من منطقية الطوابع الزمنية للمهام
ALTER TABLE edge_jobs
    ADD CONSTRAINT chk_edge_jobs_timestamps_valid
    CHECK (
        (started_at IS NULL OR started_at >= created_at) AND
        (completed_at IS NULL OR (started_at IS NOT NULL AND completed_at >= started_at))
    ) NOT VALID;
ALTER TABLE edge_jobs VALIDATE CONSTRAINT chk_edge_jobs_timestamps_valid;

-- ============================================================================
-- GRANTS (adjust roles as needed) | الصلاحيات (تعديل الأدوار حسب الحاجة)
-- ============================================================================

-- Grant usage to application role
-- منح الصلاحيات لدور التطبيق
-- GRANT SELECT, INSERT, UPDATE, DELETE ON yolo26_detections TO sahool_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON terrain_analyses TO sahool_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON hydrology_analyses TO sahool_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON edge_devices TO sahool_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON edge_jobs TO sahool_app;

-- Grant read-only to analytics role
-- منح صلاحيات القراءة فقط لدور التحليلات
-- GRANT SELECT ON yolo26_detections TO sahool_analytics;
-- GRANT SELECT ON terrain_analyses TO sahool_analytics;
-- GRANT SELECT ON hydrology_analyses TO sahool_analytics;
-- GRANT SELECT ON edge_devices TO sahool_analytics;
-- GRANT SELECT ON edge_jobs TO sahool_analytics;

-- ============================================================================
-- END OF MIGRATION | نهاية الترحيل
-- ============================================================================
