/**
 * SAHOOL NATS Subject Constants
 * ثوابت موضوعات NATS - تحديد قنوات الأحداث في منصة سهول
 *
 * Centralizes all subject names to ensure consistency across services.
 * Follows the naming pattern: sahool.{domain}.{entity}.{action}
 *
 * @packageDocumentation
 */

// ============================================================================
// Field Subjects - موضوعات الحقول
// ============================================================================

/** Event when a field is created | حدث إنشاء حقل */
export const SAHOOL_FIELD_CREATED = "sahool.field.created" as const;
/** Event when a field is updated | حدث تحديث حقل */
export const SAHOOL_FIELD_UPDATED = "sahool.field.updated" as const;
/** Event when a field is deleted | حدث حذف حقل */
export const SAHOOL_FIELD_DELETED = "sahool.field.deleted" as const;
/** Wildcard for all field events | جميع أحداث الحقول */
export const SAHOOL_FIELD_ALL = "sahool.field.*" as const;

// ============================================================================
// Farm Subjects - موضوعات المزارع
// ============================================================================

/** Event when a farm is created | حدث إنشاء مزرعة */
export const SAHOOL_FARM_CREATED = "sahool.farm.created" as const;
/** Event when a farm is updated | حدث تحديث مزرعة */
export const SAHOOL_FARM_UPDATED = "sahool.farm.updated" as const;
/** Event when a farm is deleted | حدث حذف مزرعة */
export const SAHOOL_FARM_DELETED = "sahool.farm.deleted" as const;
/** Wildcard for all farm events | جميع أحداث المزارع */
export const SAHOOL_FARM_ALL = "sahool.farm.*" as const;

// ============================================================================
// Weather Subjects - موضوعات الطقس
// ============================================================================

/** Weather forecast event | حدث توقعات الطقس */
export const SAHOOL_WEATHER_FORECAST = "sahool.weather.forecast" as const;
/** Weather alert event | حدث تنبيه الطقس */
export const SAHOOL_WEATHER_ALERT = "sahool.weather.alert" as const;
/** Frost alert | تنبيه صقيع */
export const SAHOOL_WEATHER_ALERT_FROST = "sahool.weather.alert.frost" as const;
/** Heatwave alert | تنبيه موجة حر */
export const SAHOOL_WEATHER_ALERT_HEATWAVE = "sahool.weather.alert.heatwave" as const;
/** Storm alert | تنبيه عاصفة */
export const SAHOOL_WEATHER_ALERT_STORM = "sahool.weather.alert.storm" as const;
/** Heavy rain alert | تنبيه أمطار غزيرة */
export const SAHOOL_WEATHER_ALERT_RAIN = "sahool.weather.alert.rain" as const;
/** Drought alert | تنبيه جفاف */
export const SAHOOL_WEATHER_ALERT_DROUGHT = "sahool.weather.alert.drought" as const;
/** Wind alert | تنبيه رياح */
export const SAHOOL_WEATHER_ALERT_WIND = "sahool.weather.alert.wind" as const;
/** Wildcard for all weather events | جميع أحداث الطقس */
export const SAHOOL_WEATHER_ALL = "sahool.weather.*" as const;
/** Wildcard for all weather alerts | جميع تنبيهات الطقس */
export const SAHOOL_WEATHER_ALERTS_ALL = "sahool.weather.alert.*" as const;

// ============================================================================
// Satellite Subjects - موضوعات الأقمار الصناعية
// ============================================================================

/** Satellite data is ready for processing | بيانات الأقمار الصناعية جاهزة */
export const SAHOOL_SATELLITE_DATA_READY = "sahool.satellite.data.ready" as const;
/** Satellite processing started | بدء معالجة الأقمار الصناعية */
export const SAHOOL_SATELLITE_PROCESSING_STARTED = "sahool.satellite.processing.started" as const;
/** Satellite processing completed | اكتمال معالجة الأقمار الصناعية */
export const SAHOOL_SATELLITE_PROCESSING_COMPLETED = "sahool.satellite.processing.completed" as const;
/** Satellite processing failed | فشل معالجة الأقمار الصناعية */
export const SAHOOL_SATELLITE_PROCESSING_FAILED = "sahool.satellite.processing.failed" as const;
/** Satellite anomaly detected | اكتشاف شذوذ في الأقمار الصناعية */
export const SAHOOL_SATELLITE_ANOMALY = "sahool.satellite.anomaly" as const;
/** NDVI anomaly detected | اكتشاف شذوذ NDVI */
export const SAHOOL_SATELLITE_ANOMALY_NDVI = "sahool.satellite.anomaly.ndvi" as const;
/** Vegetation anomaly detected | اكتشاف شذوذ نباتي */
export const SAHOOL_SATELLITE_ANOMALY_VEGETATION = "sahool.satellite.anomaly.vegetation" as const;
/** Water stress anomaly detected | اكتشاف شذوذ إجهاد مائي */
export const SAHOOL_SATELLITE_ANOMALY_WATER = "sahool.satellite.anomaly.water" as const;
/** Disease pattern detected | اكتشاف نمط مرضي */
export const SAHOOL_SATELLITE_ANOMALY_DISEASE = "sahool.satellite.anomaly.disease" as const;
/** NDVI computed | تم حساب NDVI */
export const SAHOOL_NDVI_COMPUTED = "sahool.satellite.ndvi.computed" as const;
/** NDVI anomaly detected | اكتشاف شذوذ NDVI */
export const SAHOOL_NDVI_ANOMALY = "sahool.satellite.ndvi.anomaly" as const;
/** Wildcard for all satellite events | جميع أحداث الأقمار الصناعية */
export const SAHOOL_SATELLITE_ALL = "sahool.satellite.*" as const;
/** Wildcard for all satellite anomalies | جميع شذوذات الأقمار الصناعية */
export const SAHOOL_SATELLITE_ANOMALIES_ALL = "sahool.satellite.anomaly.*" as const;

// ============================================================================
// Crop Health Subjects - موضوعات صحة المحاصيل
// ============================================================================

/** Disease detected | اكتشاف مرض */
export const SAHOOL_HEALTH_DISEASE_DETECTED = "sahool.health.disease.detected" as const;
/** Pest detected | اكتشاف آفة */
export const SAHOOL_HEALTH_PEST_DETECTED = "sahool.health.pest.detected" as const;
/** Stress detected | اكتشاف إجهاد */
export const SAHOOL_HEALTH_STRESS_DETECTED = "sahool.health.stress.detected" as const;
/** Water stress | إجهاد مائي */
export const SAHOOL_HEALTH_STRESS_WATER = "sahool.health.stress.water" as const;
/** Nutrient stress | إجهاد غذائي */
export const SAHOOL_HEALTH_STRESS_NUTRIENT = "sahool.health.stress.nutrient" as const;
/** Heat stress | إجهاد حراري */
export const SAHOOL_HEALTH_STRESS_HEAT = "sahool.health.stress.heat" as const;
/** Cold stress | إجهاد بارد */
export const SAHOOL_HEALTH_STRESS_COLD = "sahool.health.stress.cold" as const;
/** Wildcard for all health events | جميع أحداث الصحة */
export const SAHOOL_HEALTH_ALL = "sahool.health.*" as const;
/** Wildcard for all stress events | جميع أحداث الإجهاد */
export const SAHOOL_HEALTH_STRESS_ALL = "sahool.health.stress.*" as const;

// ============================================================================
// Inventory Subjects - موضوعات المخزون
// ============================================================================

/** Low stock alert | تنبيه انخفاض المخزون */
export const SAHOOL_INVENTORY_LOW_STOCK = "sahool.inventory.low_stock" as const;
/** Out of stock alert | تنبيه نفاد المخزون */
export const SAHOOL_INVENTORY_OUT_OF_STOCK = "sahool.inventory.out_of_stock" as const;
/** Batch expired | انتهاء صلاحية الدفعة */
export const SAHOOL_INVENTORY_BATCH_EXPIRED = "sahool.inventory.batch.expired" as const;
/** Batch expiring soon | اقتراب انتهاء صلاحية الدفعة */
export const SAHOOL_INVENTORY_BATCH_EXPIRING = "sahool.inventory.batch.expiring" as const;
/** Inventory restocked | إعادة تعبئة المخزون */
export const SAHOOL_INVENTORY_RESTOCKED = "sahool.inventory.restocked" as const;
/** Inventory adjusted | تعديل المخزون */
export const SAHOOL_INVENTORY_ADJUSTED = "sahool.inventory.adjusted" as const;
/** Inventory movement | حركة المخزون */
export const SAHOOL_INVENTORY_MOVEMENT = "sahool.inventory.movement" as const;
/** Product created | إنشاء منتج */
export const SAHOOL_INVENTORY_PRODUCT_CREATED = "sahool.inventory.product.created" as const;
/** Product updated | تحديث منتج */
export const SAHOOL_INVENTORY_PRODUCT_UPDATED = "sahool.inventory.product.updated" as const;
/** Product deleted | حذف منتج */
export const SAHOOL_INVENTORY_PRODUCT_DELETED = "sahool.inventory.product.deleted" as const;
/** Wildcard for all inventory events | جميع أحداث المخزون */
export const SAHOOL_INVENTORY_ALL = "sahool.inventory.*" as const;
/** Wildcard for all batch events | جميع أحداث الدفعات */
export const SAHOOL_INVENTORY_BATCH_ALL = "sahool.inventory.batch.*" as const;
/** Wildcard for all product events | جميع أحداث المنتجات */
export const SAHOOL_INVENTORY_PRODUCT_ALL = "sahool.inventory.product.*" as const;

// ============================================================================
// Billing Subjects - موضوعات الفواتير والاشتراكات
// ============================================================================

/** Subscription created | إنشاء اشتراك */
export const SAHOOL_BILLING_SUBSCRIPTION_CREATED = "sahool.billing.subscription.created" as const;
/** Subscription updated | تحديث اشتراك */
export const SAHOOL_BILLING_SUBSCRIPTION_UPDATED = "sahool.billing.subscription.updated" as const;
/** Subscription renewed | تجديد اشتراك */
export const SAHOOL_BILLING_SUBSCRIPTION_RENEWED = "sahool.billing.subscription.renewed" as const;
/** Subscription cancelled | إلغاء اشتراك */
export const SAHOOL_BILLING_SUBSCRIPTION_CANCELLED = "sahool.billing.subscription.cancelled" as const;
/** Subscription expired | انتهاء اشتراك */
export const SAHOOL_BILLING_SUBSCRIPTION_EXPIRED = "sahool.billing.subscription.expired" as const;
/** Payment initiated | بدء الدفع */
export const SAHOOL_BILLING_PAYMENT_INITIATED = "sahool.billing.payment.initiated" as const;
/** Payment completed | اكتمال الدفع */
export const SAHOOL_BILLING_PAYMENT_COMPLETED = "sahool.billing.payment.completed" as const;
/** Payment failed | فشل الدفع */
export const SAHOOL_BILLING_PAYMENT_FAILED = "sahool.billing.payment.failed" as const;
/** Payment refunded | استرداد الدفع */
export const SAHOOL_BILLING_PAYMENT_REFUNDED = "sahool.billing.payment.refunded" as const;
/** Invoice created | إنشاء فاتورة */
export const SAHOOL_BILLING_INVOICE_CREATED = "sahool.billing.invoice.created" as const;
/** Invoice paid | سداد فاتورة */
export const SAHOOL_BILLING_INVOICE_PAID = "sahool.billing.invoice.paid" as const;
/** Invoice overdue | فاتورة متأخرة */
export const SAHOOL_BILLING_INVOICE_OVERDUE = "sahool.billing.invoice.overdue" as const;
/** Quota exceeded | تجاوز الحصة */
export const SAHOOL_BILLING_QUOTA_EXCEEDED = "sahool.billing.quota.exceeded" as const;
/** Quota warning | تحذير الحصة */
export const SAHOOL_BILLING_QUOTA_WARNING = "sahool.billing.quota.warning" as const;
/** Wildcard for all billing events | جميع أحداث الفواتير */
export const SAHOOL_BILLING_ALL = "sahool.billing.*" as const;
/** Wildcard for all subscription events | جميع أحداث الاشتراكات */
export const SAHOOL_BILLING_SUBSCRIPTION_ALL = "sahool.billing.subscription.*" as const;
/** Wildcard for all payment events | جميع أحداث الدفع */
export const SAHOOL_BILLING_PAYMENT_ALL = "sahool.billing.payment.*" as const;
/** Wildcard for all invoice events | جميع أحداث الفواتير */
export const SAHOOL_BILLING_INVOICE_ALL = "sahool.billing.invoice.*" as const;

// ============================================================================
// Task Subjects - موضوعات المهام
// ============================================================================

/** Task created | إنشاء مهمة */
export const SAHOOL_TASK_CREATED = "sahool.task.created" as const;
/** Task updated | تحديث مهمة */
export const SAHOOL_TASK_UPDATED = "sahool.task.updated" as const;
/** Task completed | اكتمال مهمة */
export const SAHOOL_TASK_COMPLETED = "sahool.task.completed" as const;
/** Task deleted | حذف مهمة */
export const SAHOOL_TASK_DELETED = "sahool.task.deleted" as const;
/** Task assigned | تعيين مهمة */
export const SAHOOL_TASK_ASSIGNED = "sahool.task.assigned" as const;
/** Wildcard for all task events | جميع أحداث المهام */
export const SAHOOL_TASK_ALL = "sahool.task.*" as const;

// ============================================================================
// Recommendation Subjects - موضوعات التوصيات
// ============================================================================

/** Recommendation created | إنشاء توصية */
export const SAHOOL_RECOMMENDATION_CREATED = "sahool.recommendation.created" as const;
/** Irrigation recommendation | توصية ري */
export const SAHOOL_RECOMMENDATION_IRRIGATION = "sahool.recommendation.irrigation" as const;
/** Fertilizer recommendation | توصية تسميد */
export const SAHOOL_RECOMMENDATION_FERTILIZER = "sahool.recommendation.fertilizer" as const;
/** Pest control recommendation | توصية مكافحة آفات */
export const SAHOOL_RECOMMENDATION_PEST_CONTROL = "sahool.recommendation.pest_control" as const;
/** Harvest recommendation | توصية حصاد */
export const SAHOOL_RECOMMENDATION_HARVEST = "sahool.recommendation.harvest" as const;
/** Wildcard for all recommendation events | جميع أحداث التوصيات */
export const SAHOOL_RECOMMENDATION_ALL = "sahool.recommendation.*" as const;

// ============================================================================
// Alert Subjects - موضوعات التنبيهات
// ============================================================================

/** Alert created | إنشاء تنبيه */
export const SAHOOL_ALERT_CREATED = "sahool.alert.created" as const;
/** Alert acknowledged | تأكيد التنبيه */
export const SAHOOL_ALERT_ACKNOWLEDGED = "sahool.alert.acknowledged" as const;
/** Alert resolved | حل التنبيه */
export const SAHOOL_ALERT_RESOLVED = "sahool.alert.resolved" as const;
/** Wildcard for all alert events | جميع أحداث التنبيهات */
export const SAHOOL_ALERT_ALL = "sahool.alert.*" as const;

// ============================================================================
// IoT Subjects - موضوعات إنترنت الأشياء
// ============================================================================

/** Sensor reading received | قراءة مستشعر */
export const SAHOOL_IOT_SENSOR_READING = "sahool.iot.sensor.reading" as const;
/** Sensor connected | اتصال مستشعر */
export const SAHOOL_IOT_SENSOR_CONNECTED = "sahool.iot.sensor.connected" as const;
/** Sensor disconnected | انقطاع مستشعر */
export const SAHOOL_IOT_SENSOR_DISCONNECTED = "sahool.iot.sensor.disconnected" as const;
/** Sensor alert | تنبيه مستشعر */
export const SAHOOL_IOT_SENSOR_ALERT = "sahool.iot.sensor.alert" as const;
/** Device registered | تسجيل جهاز */
export const SAHOOL_IOT_DEVICE_REGISTERED = "sahool.iot.device.registered" as const;
/** Device status update | تحديث حالة الجهاز */
export const SAHOOL_IOT_DEVICE_STATUS = "sahool.iot.device.status" as const;
/** Wildcard for all IoT events | جميع أحداث إنترنت الأشياء */
export const SAHOOL_IOT_ALL = "sahool.iot.*" as const;
/** Wildcard for all sensor events | جميع أحداث المستشعرات */
export const SAHOOL_IOT_SENSOR_ALL = "sahool.iot.sensor.*" as const;
/** Wildcard for all device events | جميع أحداث الأجهزة */
export const SAHOOL_IOT_DEVICE_ALL = "sahool.iot.device.*" as const;

// ============================================================================
// Notification Subjects - موضوعات الإشعارات
// ============================================================================

/** Send notification | إرسال إشعار */
export const SAHOOL_NOTIFICATION_SEND = "sahool.notification.send" as const;
/** Notification sent | تم الإرسال */
export const SAHOOL_NOTIFICATION_SENT = "sahool.notification.sent" as const;
/** Notification delivered | تم التوصيل */
export const SAHOOL_NOTIFICATION_DELIVERED = "sahool.notification.delivered" as const;
/** Notification failed | فشل الإشعار */
export const SAHOOL_NOTIFICATION_FAILED = "sahool.notification.failed" as const;
/** Notification read | قراءة الإشعار */
export const SAHOOL_NOTIFICATION_READ = "sahool.notification.read" as const;
/** Wildcard for all notification events | جميع أحداث الإشعارات */
export const SAHOOL_NOTIFICATION_ALL = "sahool.notification.*" as const;

// ============================================================================
// User Subjects - موضوعات المستخدمين
// ============================================================================

/** User registered | تسجيل مستخدم */
export const SAHOOL_USER_REGISTERED = "sahool.user.registered" as const;
/** User created | إنشاء مستخدم */
export const SAHOOL_USER_CREATED = "sahool.user.created" as const;
/** User verified | التحقق من المستخدم */
export const SAHOOL_USER_VERIFIED = "sahool.user.verified" as const;
/** User logged in | تسجيل الدخول */
export const SAHOOL_USER_LOGGED_IN = "sahool.user.logged_in" as const;
/** User logged out | تسجيل الخروج */
export const SAHOOL_USER_LOGGED_OUT = "sahool.user.logged_out" as const;
/** User updated | تحديث مستخدم */
export const SAHOOL_USER_UPDATED = "sahool.user.updated" as const;
/** User deleted | حذف مستخدم */
export const SAHOOL_USER_DELETED = "sahool.user.deleted" as const;
/** Wildcard for all user events | جميع أحداث المستخدمين */
export const SAHOOL_USER_ALL = "sahool.user.*" as const;

// ============================================================================
// Order Subjects - موضوعات الطلبات
// ============================================================================

/** Order placed | تقديم طلب */
export const SAHOOL_ORDER_PLACED = "sahool.order.placed" as const;
/** Order completed | اكتمال طلب */
export const SAHOOL_ORDER_COMPLETED = "sahool.order.completed" as const;
/** Order cancelled | إلغاء طلب */
export const SAHOOL_ORDER_CANCELLED = "sahool.order.cancelled" as const;
/** Wildcard for all order events | جميع أحداث الطلبات */
export const SAHOOL_ORDER_ALL = "sahool.order.*" as const;

// ============================================================================
// Agent Subjects - موضوعات الوكلاء الذكية
// ============================================================================

/** Agent execution started | بدء تنفيذ الوكيل */
export const SAHOOL_AGENT_EXECUTION_STARTED = "sahool.agent.execution.started" as const;
/** Agent execution completed | اكتمال تنفيذ الوكيل */
export const SAHOOL_AGENT_EXECUTION_COMPLETED = "sahool.agent.execution.completed" as const;
/** Agent execution failed | فشل تنفيذ الوكيل */
export const SAHOOL_AGENT_EXECUTION_FAILED = "sahool.agent.execution.failed" as const;
/** Agent step completed | اكتمال خطوة الوكيل */
export const SAHOOL_AGENT_STEP_COMPLETED = "sahool.agent.step.completed" as const;
/** Wildcard for all agent events | جميع أحداث الوكلاء */
export const SAHOOL_AGENT_ALL = "sahool.agent.*" as const;

// ============================================================================
// System Subjects - موضوعات النظام
// ============================================================================

/** System health check | فحص صحة النظام */
export const SAHOOL_SYSTEM_HEALTH = "sahool.system.health" as const;
/** System metric | مقياس النظام */
export const SAHOOL_SYSTEM_METRIC = "sahool.system.metric" as const;
/** System error | خطأ النظام */
export const SAHOOL_SYSTEM_ERROR = "sahool.system.error" as const;
/** System audit | تدقيق النظام */
export const SAHOOL_SYSTEM_AUDIT = "sahool.system.audit" as const;
/** Wildcard for all system events | جميع أحداث النظام */
export const SAHOOL_SYSTEM_ALL = "sahool.system.*" as const;

// ============================================================================
// Subject Registry - Type-Safe Subject Map
// ============================================================================

/**
 * All SAHOOL event subjects organized by domain.
 * جميع موضوعات الأحداث مرتبة حسب المجال
 */
export const EventSubjects = {
  // Field events
  FIELD_CREATED: SAHOOL_FIELD_CREATED,
  FIELD_UPDATED: SAHOOL_FIELD_UPDATED,
  FIELD_DELETED: SAHOOL_FIELD_DELETED,

  // Farm events
  FARM_CREATED: SAHOOL_FARM_CREATED,
  FARM_UPDATED: SAHOOL_FARM_UPDATED,
  FARM_DELETED: SAHOOL_FARM_DELETED,

  // Weather events
  WEATHER_FORECAST: SAHOOL_WEATHER_FORECAST,
  WEATHER_ALERT: SAHOOL_WEATHER_ALERT,
  WEATHER_ALERT_FROST: SAHOOL_WEATHER_ALERT_FROST,
  WEATHER_ALERT_HEATWAVE: SAHOOL_WEATHER_ALERT_HEATWAVE,
  WEATHER_ALERT_STORM: SAHOOL_WEATHER_ALERT_STORM,
  WEATHER_ALERT_RAIN: SAHOOL_WEATHER_ALERT_RAIN,
  WEATHER_ALERT_DROUGHT: SAHOOL_WEATHER_ALERT_DROUGHT,
  WEATHER_ALERT_WIND: SAHOOL_WEATHER_ALERT_WIND,

  // Satellite events
  SATELLITE_DATA_READY: SAHOOL_SATELLITE_DATA_READY,
  SATELLITE_PROCESSING_STARTED: SAHOOL_SATELLITE_PROCESSING_STARTED,
  SATELLITE_PROCESSING_COMPLETED: SAHOOL_SATELLITE_PROCESSING_COMPLETED,
  SATELLITE_PROCESSING_FAILED: SAHOOL_SATELLITE_PROCESSING_FAILED,
  SATELLITE_ANOMALY: SAHOOL_SATELLITE_ANOMALY,
  SATELLITE_ANOMALY_NDVI: SAHOOL_SATELLITE_ANOMALY_NDVI,
  NDVI_COMPUTED: SAHOOL_NDVI_COMPUTED,
  NDVI_ANOMALY: SAHOOL_NDVI_ANOMALY,

  // Health events
  HEALTH_DISEASE_DETECTED: SAHOOL_HEALTH_DISEASE_DETECTED,
  HEALTH_PEST_DETECTED: SAHOOL_HEALTH_PEST_DETECTED,
  HEALTH_STRESS_DETECTED: SAHOOL_HEALTH_STRESS_DETECTED,
  HEALTH_STRESS_WATER: SAHOOL_HEALTH_STRESS_WATER,
  HEALTH_STRESS_NUTRIENT: SAHOOL_HEALTH_STRESS_NUTRIENT,
  HEALTH_STRESS_HEAT: SAHOOL_HEALTH_STRESS_HEAT,
  HEALTH_STRESS_COLD: SAHOOL_HEALTH_STRESS_COLD,

  // Inventory events
  INVENTORY_LOW_STOCK: SAHOOL_INVENTORY_LOW_STOCK,
  INVENTORY_OUT_OF_STOCK: SAHOOL_INVENTORY_OUT_OF_STOCK,
  INVENTORY_BATCH_EXPIRED: SAHOOL_INVENTORY_BATCH_EXPIRED,
  INVENTORY_BATCH_EXPIRING: SAHOOL_INVENTORY_BATCH_EXPIRING,
  INVENTORY_RESTOCKED: SAHOOL_INVENTORY_RESTOCKED,
  INVENTORY_ADJUSTED: SAHOOL_INVENTORY_ADJUSTED,
  INVENTORY_MOVEMENT: SAHOOL_INVENTORY_MOVEMENT,

  // Billing events
  BILLING_SUBSCRIPTION_CREATED: SAHOOL_BILLING_SUBSCRIPTION_CREATED,
  BILLING_SUBSCRIPTION_UPDATED: SAHOOL_BILLING_SUBSCRIPTION_UPDATED,
  BILLING_SUBSCRIPTION_RENEWED: SAHOOL_BILLING_SUBSCRIPTION_RENEWED,
  BILLING_SUBSCRIPTION_CANCELLED: SAHOOL_BILLING_SUBSCRIPTION_CANCELLED,
  BILLING_SUBSCRIPTION_EXPIRED: SAHOOL_BILLING_SUBSCRIPTION_EXPIRED,
  BILLING_PAYMENT_INITIATED: SAHOOL_BILLING_PAYMENT_INITIATED,
  BILLING_PAYMENT_COMPLETED: SAHOOL_BILLING_PAYMENT_COMPLETED,
  BILLING_PAYMENT_FAILED: SAHOOL_BILLING_PAYMENT_FAILED,
  BILLING_PAYMENT_REFUNDED: SAHOOL_BILLING_PAYMENT_REFUNDED,
  BILLING_INVOICE_CREATED: SAHOOL_BILLING_INVOICE_CREATED,
  BILLING_INVOICE_PAID: SAHOOL_BILLING_INVOICE_PAID,
  BILLING_INVOICE_OVERDUE: SAHOOL_BILLING_INVOICE_OVERDUE,

  // Task events
  TASK_CREATED: SAHOOL_TASK_CREATED,
  TASK_UPDATED: SAHOOL_TASK_UPDATED,
  TASK_COMPLETED: SAHOOL_TASK_COMPLETED,
  TASK_DELETED: SAHOOL_TASK_DELETED,
  TASK_ASSIGNED: SAHOOL_TASK_ASSIGNED,

  // Recommendation events
  RECOMMENDATION_CREATED: SAHOOL_RECOMMENDATION_CREATED,
  RECOMMENDATION_IRRIGATION: SAHOOL_RECOMMENDATION_IRRIGATION,
  RECOMMENDATION_FERTILIZER: SAHOOL_RECOMMENDATION_FERTILIZER,
  RECOMMENDATION_PEST_CONTROL: SAHOOL_RECOMMENDATION_PEST_CONTROL,
  RECOMMENDATION_HARVEST: SAHOOL_RECOMMENDATION_HARVEST,

  // Alert events
  ALERT_CREATED: SAHOOL_ALERT_CREATED,
  ALERT_ACKNOWLEDGED: SAHOOL_ALERT_ACKNOWLEDGED,
  ALERT_RESOLVED: SAHOOL_ALERT_RESOLVED,

  // IoT events
  IOT_SENSOR_READING: SAHOOL_IOT_SENSOR_READING,
  IOT_SENSOR_CONNECTED: SAHOOL_IOT_SENSOR_CONNECTED,
  IOT_SENSOR_DISCONNECTED: SAHOOL_IOT_SENSOR_DISCONNECTED,
  IOT_SENSOR_ALERT: SAHOOL_IOT_SENSOR_ALERT,
  IOT_DEVICE_REGISTERED: SAHOOL_IOT_DEVICE_REGISTERED,
  IOT_DEVICE_STATUS: SAHOOL_IOT_DEVICE_STATUS,

  // Notification events
  NOTIFICATION_SEND: SAHOOL_NOTIFICATION_SEND,
  NOTIFICATION_SENT: SAHOOL_NOTIFICATION_SENT,
  NOTIFICATION_DELIVERED: SAHOOL_NOTIFICATION_DELIVERED,
  NOTIFICATION_FAILED: SAHOOL_NOTIFICATION_FAILED,
  NOTIFICATION_READ: SAHOOL_NOTIFICATION_READ,

  // User events
  USER_REGISTERED: SAHOOL_USER_REGISTERED,
  USER_CREATED: SAHOOL_USER_CREATED,
  USER_VERIFIED: SAHOOL_USER_VERIFIED,
  USER_LOGGED_IN: SAHOOL_USER_LOGGED_IN,
  USER_LOGGED_OUT: SAHOOL_USER_LOGGED_OUT,
  USER_UPDATED: SAHOOL_USER_UPDATED,
  USER_DELETED: SAHOOL_USER_DELETED,

  // Order events
  ORDER_PLACED: SAHOOL_ORDER_PLACED,
  ORDER_COMPLETED: SAHOOL_ORDER_COMPLETED,
  ORDER_CANCELLED: SAHOOL_ORDER_CANCELLED,

  // Agent events
  AGENT_EXECUTION_STARTED: SAHOOL_AGENT_EXECUTION_STARTED,
  AGENT_EXECUTION_COMPLETED: SAHOOL_AGENT_EXECUTION_COMPLETED,
  AGENT_EXECUTION_FAILED: SAHOOL_AGENT_EXECUTION_FAILED,
  AGENT_STEP_COMPLETED: SAHOOL_AGENT_STEP_COMPLETED,

  // System events
  SYSTEM_HEALTH: SAHOOL_SYSTEM_HEALTH,
  SYSTEM_METRIC: SAHOOL_SYSTEM_METRIC,
  SYSTEM_ERROR: SAHOOL_SYSTEM_ERROR,
  SYSTEM_AUDIT: SAHOOL_SYSTEM_AUDIT,
} as const;

/** Type for all valid event subject names */
export type EventSubject = (typeof EventSubjects)[keyof typeof EventSubjects];

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Get the full NATS subject for an event type.
 * الحصول على موضوع NATS الكامل لنوع الحدث
 *
 * @param eventType - Event type (e.g., "field.created")
 * @returns Full NATS subject (e.g., "sahool.field.created")
 */
export function getSubjectForEvent(eventType: string): string {
  if (eventType.startsWith("sahool.")) {
    return eventType;
  }
  return `sahool.${eventType}`;
}

/**
 * Get wildcard subject for a domain.
 * الحصول على موضوع شامل للمجال
 *
 * @param domain - Domain name (e.g., "field", "weather")
 * @returns Wildcard subject (e.g., "sahool.field.*")
 */
export function getWildcardSubject(domain: string): string {
  return `sahool.${domain}.*`;
}

/**
 * Validate if a subject follows SAHOOL naming conventions.
 * التحقق من صحة تسمية الموضوع
 *
 * @param subject - Subject string to validate
 * @returns True if valid
 */
export function isValidSubject(subject: string): boolean {
  if (!subject.startsWith("sahool.")) {
    return false;
  }
  const parts = subject.split(".");
  return parts.length >= 3; // sahool.domain.action (minimum)
}

/**
 * Get a tenant-scoped NATS subject.
 * الحصول على موضوع NATS محدد النطاق للمستأجر
 *
 * @param tenantId - Tenant identifier
 * @param domain - Event domain (e.g., "field")
 * @param action - Event action (e.g., "created")
 * @returns Tenant-scoped subject (e.g., "sahool.tenant.org_123.field.created")
 */
export function getTenantSubject(
  tenantId: string,
  domain: string,
  action: string
): string {
  if (!tenantId) {
    throw new Error("tenantId is required for tenant-scoped subjects");
  }
  return `sahool.tenant.${tenantId}.${domain}.${action}`;
}

/**
 * Get wildcard subject for a tenant.
 * الحصول على موضوع شامل للمستأجر
 *
 * @param tenantId - Tenant identifier
 * @param domain - Optional domain filter (default "*")
 * @returns Wildcard subject for tenant events
 */
export function getTenantWildcard(tenantId: string, domain = "*"): string {
  if (!tenantId) {
    throw new Error("tenantId is required for tenant-scoped subjects");
  }
  if (domain === "*") {
    return `sahool.tenant.${tenantId}.>`;
  }
  return `sahool.tenant.${tenantId}.${domain}.*`;
}

/**
 * Extract domain from a subject string.
 * استخراج المجال من سلسلة الموضوع
 *
 * @param subject - Full subject string
 * @returns Domain name or null
 */
export function extractDomain(subject: string): string | null {
  const parts = subject.split(".");
  if (parts.length >= 2 && parts[0] === "sahool") {
    // Handle tenant-scoped subjects: sahool.tenant.{id}.{domain}.{action}
    if (parts[1] === "tenant" && parts.length >= 4) {
      return parts[3];
    }
    return parts[1];
  }
  return null;
}
