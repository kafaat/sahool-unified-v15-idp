/**
 * Report Storage DI Token
 * رمز حقن التبعيات للتخزين
 *
 * Injection token used so `FieldReportsService` can depend on the
 * `IReportStorageProvider` interface without knowing whether the
 * concrete implementation is the in-memory or S3/MinIO adapter. The
 * module picks the right one based on the `REPORT_STORAGE` env var.
 */

import type { Provider } from "@nestjs/common";
import { InMemoryReportStorage } from "./inmemory-storage.adapter";
import type { IReportStorageProvider } from "./report-storage.provider";
import { S3ReportStorage } from "./s3-storage.adapter";

export const REPORT_STORAGE_TOKEN = "REPORT_STORAGE_PROVIDER";

/**
 * Build a NestJS provider that returns the right storage implementation
 * for the current environment. Read from env at module-init time; the
 * chosen backend is fixed for the life of the process (matches how the
 * platform resolves ``DATABASE_URL`` etc.).
 */
export function buildReportStorageProvider(): Provider {
  return {
    provide: REPORT_STORAGE_TOKEN,
    useFactory: (): IReportStorageProvider => {
      const backend = (process.env.REPORT_STORAGE ?? "inmemory").toLowerCase();
      if (backend === "s3" || backend === "minio") {
        return new S3ReportStorage();
      }
      return new InMemoryReportStorage();
    },
  };
}
