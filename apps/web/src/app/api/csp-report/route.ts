/**
 * CSP Violation Report Endpoint
 * نقطة نهاية تقارير انتهاكات سياسة أمان المحتوى
 *
 * This endpoint receives Content Security Policy violation reports
 * and logs them for monitoring and debugging purposes.
 */

import { NextRequest, NextResponse } from 'next/server';

interface CSPReport {
  'csp-report': {
    'document-uri': string;
    'violated-directive': string;
    'effective-directive': string;
    'original-policy': string;
    'blocked-uri': string;
    'status-code': number;
    'source-file'?: string;
    'line-number'?: number;
    'column-number'?: number;
  };
}

export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type');

    // CSP reports can be sent as application/csp-report or application/json
    if (!contentType?.includes('application/csp-report') && !contentType?.includes('application/json')) {
      return NextResponse.json(
        { error: 'Invalid content type' },
        { status: 400 }
      );
    }

    const report: CSPReport = await request.json();
    const violation = report['csp-report'];

    if (!violation) {
      return NextResponse.json(
        { error: 'Invalid CSP report format' },
        { status: 400 }
      );
    }

    // Log CSP violation
    console.error('CSP Violation Report:', {
      timestamp: new Date().toISOString(),
      documentUri: violation['document-uri'],
      violatedDirective: violation['violated-directive'],
      effectiveDirective: violation['effective-directive'],
      blockedUri: violation['blocked-uri'],
      sourceFile: violation['source-file'],
      lineNumber: violation['line-number'],
      columnNumber: violation['column-number'],
      statusCode: violation['status-code'],
    });

    // In production, you might want to:
    // 1. Store violations in a database
    // 2. Send alerts for critical violations
    // 3. Aggregate violations for analysis
    // 4. Filter out known false positives

    // Example: Track critical violations
    const criticalDirectives = ['script-src', 'default-src', 'frame-ancestors'];
    const isCritical = criticalDirectives.some(directive =>
      violation['violated-directive'].includes(directive)
    );

    if (isCritical) {
      console.error('CRITICAL CSP VIOLATION:', {
        directive: violation['violated-directive'],
        blockedUri: violation['blocked-uri'],
        documentUri: violation['document-uri'],
      });

      // TODO: Send alert to monitoring service (e.g., Sentry, DataDog, etc.)
      // await sendAlert({
      //   type: 'csp-violation',
      //   severity: 'critical',
      //   violation,
      // });
    }

    return NextResponse.json({ success: true }, { status: 204 });
  } catch (error) {
    console.error('Error processing CSP report:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({
    status: 'ok',
    endpoint: 'csp-report',
    description: 'Content Security Policy violation reporting endpoint',
  });
}
