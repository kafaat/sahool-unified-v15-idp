import {
  Injectable,
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Logger,
} from '@nestjs/common';
<<<<<<< HEAD
import { PrismaService } from '@/config/prisma.service';
=======
import { PrismaService } from '../config/prisma.service';
>>>>>>> 68c4f2a7b84c7c441a567209d85cf70ff80c5c7e

/**
 * Scientific Lock Guard - حارس القفل العلمي
 *
 * يمنع التعديل على التجارب المقفلة لضمان نزاهة البيانات البحثية
 * Prevents modifications to locked experiments to ensure research data integrity
 */
@Injectable()
export class ScientificLockGuard implements CanActivate {
  private readonly logger = new Logger(ScientificLockGuard.name);

  constructor(private readonly prisma: PrismaService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const { experimentId } = request.params;
    const method = request.method;

    // السماح بعمليات القراءة
    if (method === 'GET') {
      return true;
    }

    // إذا لم يكن هناك experimentId، السماح بالمرور
    if (!experimentId) {
      return true;
    }

    try {
      // التحقق من حالة التجربة
      const experiment = await this.prisma.experiment.findUnique({
        where: { id: experimentId },
        select: {
          id: true,
          status: true,
          lockedAt: true,
          lockedBy: true,
        },
      });

      if (!experiment) {
        return true; // سيتم التعامل مع 404 في الـ controller
      }

      // التحقق من القفل
      if (experiment.status === 'completed' || experiment.status === 'archived') {
        this.logger.warn(
          `Blocked modification attempt on ${experiment.status} experiment: ${experimentId}`,
        );
        throw new ForbiddenException({
          statusCode: 403,
          error: 'Scientific Lock Violation',
          message: `عملية مرفوضة: التجربة في حالة "${experiment.status}" ولا يمكن تعديلها`,
          messageEn: `Operation denied: Experiment is "${experiment.status}" and cannot be modified`,
          experimentId,
          status: experiment.status,
          lockedAt: experiment.lockedAt,
        });
      }

      // التحقق من القفل الصريح
      if (experiment.lockedAt) {
        this.logger.warn(
          `Blocked modification attempt on locked experiment: ${experimentId}`,
        );
        throw new ForbiddenException({
          statusCode: 403,
          error: 'Scientific Lock Active',
          message: 'عملية مرفوضة: التجربة مقفلة علمياً لضمان النزاهة',
          messageEn: 'Operation denied: Experiment is scientifically locked for data integrity',
          experimentId,
          lockedAt: experiment.lockedAt,
          lockedBy: experiment.lockedBy,
        });
      }

      return true;
    } catch (error) {
      if (error instanceof ForbiddenException) {
        throw error;
      }
      this.logger.error(`Error checking experiment lock: ${error.message}`);
      return true; // في حالة الخطأ، نسمح بالمرور ونترك الـ controller يتعامل مع الطلب
    }
  }
}

/**
 * Decorator to apply scientific lock guard
 */
export function ScientificLocked() {
  return function (
    target: any,
    propertyKey: string,
    descriptor: PropertyDescriptor,
  ) {
    // يمكن استخدام هذا الـ decorator مع @UseGuards(ScientificLockGuard)
    return descriptor;
  };
}
