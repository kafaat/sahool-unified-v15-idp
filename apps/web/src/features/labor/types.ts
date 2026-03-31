/**
 * Labor Management Feature - Types
 * أنواع ميزة إدارة العمالة
 */

export type WorkerStatus =
  | 'active'
  | 'inactive'
  | 'on_leave'
  | 'terminated'
  | 'suspended';

export type WorkerType =
  | 'full_time'
  | 'part_time'
  | 'seasonal'
  | 'contract'
  | 'daily';

export type TaskStatus =
  | 'pending'
  | 'assigned'
  | 'in_progress'
  | 'completed'
  | 'cancelled'
  | 'on_hold'
  | 'blocked';

export type TaskPriority = 'critical' | 'high' | 'medium' | 'low';

export type TaskCategory =
  | 'planting'
  | 'irrigation'
  | 'fertilization'
  | 'pesticide_application'
  | 'harvesting'
  | 'pruning'
  | 'weeding'
  | 'soil_preparation'
  | 'equipment_maintenance'
  | 'scouting'
  | 'greenhouse_work'
  | 'general_labor'
  | 'quality_control'
  | 'packing';

export type SkillLevel =
  | 'none'
  | 'beginner'
  | 'intermediate'
  | 'advanced'
  | 'expert';

export type AttendanceStatus =
  | 'present'
  | 'absent'
  | 'late'
  | 'early_leave'
  | 'half_day'
  | 'on_leave'
  | 'holiday';

export type LeaveType =
  | 'annual'
  | 'sick'
  | 'emergency'
  | 'maternity'
  | 'paternity'
  | 'unpaid'
  | 'pilgrimage'
  | 'compensatory';

export type LeaveStatus = 'pending' | 'approved' | 'rejected';

export interface WorkerSkill {
  id: string;
  skillName: string;
  skillNameAr: string;
  category: TaskCategory;
  level: SkillLevel;
  isCertified: boolean;
  certificationExpiry?: string;
}

export interface WorkerCertification {
  id: string;
  certificationType: string;
  name: string;
  nameAr: string;
  issueDate: string;
  expiryDate: string;
  issuingAuthority: string;
  certificateNumber: string;
  isVerified: boolean;
}

export interface Worker {
  id: string;
  tenantId: string;
  farmId: string;
  firstName: string;
  firstNameAr: string;
  lastName: string;
  lastNameAr: string;
  phone: string;
  email?: string;
  status: WorkerStatus;
  workerType: WorkerType;
  hireDate: string;
  department: string;
  departmentAr: string;
  position: string;
  positionAr: string;
  supervisorId?: string;
  hourlyRate?: number;
  dailyRate?: number;
  monthlyRate?: number;
  currency: string;
  skills: WorkerSkill[];
  certifications: WorkerCertification[];
  nationalId?: string;
  languages: string[];
  photoUrl?: string;
  createdAt: string;
  updatedAt: string;
}

export interface FarmTask {
  id: string;
  tenantId: string;
  farmId: string;
  fieldId?: string;
  fieldName?: string;
  fieldNameAr?: string;
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  category: TaskCategory;
  priority: TaskPriority;
  status: TaskStatus;
  plannedStart: string;
  plannedEnd: string;
  actualStart?: string;
  actualEnd?: string;
  estimatedHours: number;
  actualHours?: number;
  assignedWorkers: string[];
  supervisorId?: string;
  requiredSkills: string[];
  requiredPpe: string[];
  reiRestricted: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface WorkShift {
  id: string;
  name: string;
  nameAr: string;
  startTime: string;
  endTime: string;
  totalHours: number;
  workDays: number[];
}

export interface AttendanceRecord {
  id: string;
  workerId: string;
  workerName: string;
  workerNameAr: string;
  date: string;
  status: AttendanceStatus;
  checkInTime?: string;
  checkOutTime?: string;
  workedHours?: number;
  overtime?: number;
  notes?: string;
}

export interface LeaveRequest {
  id: string;
  workerId: string;
  workerName: string;
  workerNameAr: string;
  leaveType: LeaveType;
  startDate: string;
  endDate: string;
  totalDays: number;
  reason: string;
  reasonAr: string;
  status: LeaveStatus;
  approvedBy?: string;
  approvalDate?: string;
}

export interface Timesheet {
  id: string;
  workerId: string;
  workerName: string;
  workerNameAr: string;
  periodStart: string;
  periodEnd: string;
  totalHoursWorked: number;
  overtimeHours: number;
  hourlyRate: number;
  totalWages: number;
  currency: string;
  status: string;
}

export interface SafetyViolation {
  id: string;
  workerId: string;
  violationType: string;
  description: string;
  descriptionAr: string;
  date: string;
  severity: TaskPriority;
  status: string;
  correctiveAction: string;
  correctiveActionAr: string;
}

export interface REIZone {
  id: string;
  name: string;
  nameAr: string;
  fieldId: string;
  reiHours: number;
  startDate: string;
  endDate: string;
  triggerCause: string;
  restrictedActivities: string[];
}

export interface WorkerFilters {
  status?: WorkerStatus;
  workerType?: WorkerType;
  farmId?: string;
  department?: string;
  search?: string;
}

export interface TaskFilters {
  status?: TaskStatus;
  priority?: TaskPriority;
  category?: TaskCategory;
  fieldId?: string;
  assignedWorkerId?: string;
  search?: string;
}

export interface AttendanceFilters {
  workerId?: string;
  date?: string;
  dateFrom?: string;
  dateTo?: string;
  status?: AttendanceStatus;
}

export interface WorkerFormData {
  firstName: string;
  firstNameAr: string;
  lastName: string;
  lastNameAr: string;
  phone: string;
  email?: string;
  workerType: WorkerType;
  hireDate: string;
  department: string;
  departmentAr: string;
  position: string;
  positionAr: string;
  supervisorId?: string;
  hourlyRate?: number;
  dailyRate?: number;
  monthlyRate?: number;
  currency: string;
  nationalId?: string;
  languages: string[];
}

export interface TaskFormData {
  title: string;
  titleAr: string;
  description: string;
  descriptionAr: string;
  category: TaskCategory;
  priority: TaskPriority;
  fieldId?: string;
  plannedStart: string;
  plannedEnd: string;
  estimatedHours: number;
  assignedWorkers: string[];
  supervisorId?: string;
  requiredSkills: string[];
  requiredPpe: string[];
  reiRestricted: boolean;
}

export interface LaborStats {
  totalWorkers: number;
  activeWorkers: number;
  byStatus: Record<string, number>;
  byType: Record<string, number>;
  totalTasks: number;
  tasksByStatus: Record<string, number>;
  tasksByPriority: Record<string, number>;
  averageAttendanceRate: number;
  totalWagesThisMonth: number;
  currency: string;
}
