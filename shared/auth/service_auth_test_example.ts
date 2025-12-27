/**
 * Service-to-Service Authentication Test Examples (TypeScript)
 * Quick tests to verify the service auth system is working correctly
 */

// Set up environment for testing
process.env.JWT_SECRET = 'test-secret-key-minimum-32-characters-long';
process.env.JWT_ALGORITHM = 'HS256';
process.env.JWT_ISSUER = 'sahool-platform';
process.env.JWT_AUDIENCE = 'sahool-api';

import {
  ALLOWED_SERVICES,
  SERVICE_COMMUNICATION_MATRIX,
  ServiceToken,
  createServiceToken,
  verifyServiceToken,
  isServiceAuthorized,
  getAllowedTargets,
  ServiceAuthException,
} from './service_auth';

/**
 * Test basic service token creation and verification
 */
function testBasicTokenCreation(): boolean {
  console.log('\n=== Test 1: Basic Token Creation ===');

  try {
    // Create a token
    const token = createServiceToken(
      'farm-service',
      'field-service',
      300,
    );
    console.log('✓ Token created successfully');
    console.log(`  Token (first 50 chars): ${token.substring(0, 50)}...`);

    // Verify the token
    const payload = verifyServiceToken(token);
    console.log('✓ Token verified successfully');
    console.log(`  Service Name: ${payload.service_name}`);
    console.log(`  Target Service: ${payload.target_service}`);
    console.log(`  Expires: ${payload.exp}`);
    console.log(`  Issued: ${payload.iat}`);

    if (payload.service_name !== 'farm-service') {
      throw new Error('Service name mismatch');
    }
    if (payload.target_service !== 'field-service') {
      throw new Error('Target service mismatch');
    }
    console.log('✓ All assertions passed');

    return true;
  } catch (error) {
    console.error(`✗ Test failed: ${error}`);
    return false;
  }
}

/**
 * Test ServiceToken class methods
 */
function testServiceClass(): boolean {
  console.log('\n=== Test 2: ServiceToken Class ===');

  try {
    // Create using class method
    const token = ServiceToken.create(
      'crop-service',
      'weather-service',
      600,
      { request_id: 'test-123' },
    );
    console.log('✓ Token created with ServiceToken.create()');

    // Verify using class method
    const payload = ServiceToken.verify(token);
    console.log('✓ Token verified with ServiceToken.verify()');
    console.log(`  Service: ${payload.service_name} → ${payload.target_service}`);

    if (payload.service_name !== 'crop-service') {
      throw new Error('Service name mismatch');
    }
    if (payload.target_service !== 'weather-service') {
      throw new Error('Target service mismatch');
    }
    console.log('✓ All assertions passed');

    return true;
  } catch (error) {
    console.error(`✗ Test failed: ${error}`);
    return false;
  }
}

/**
 * Test that unauthorized service calls are rejected
 */
function testUnauthorizedService(): boolean {
  console.log('\n=== Test 3: Unauthorized Service Call ===');

  try {
    // This should fail - notification-service cannot call farm-service
    const token = createServiceToken(
      'notification-service',
      'farm-service',
      300,
    );
    console.error('✗ Test failed: Should have thrown an exception');
    return false;
  } catch (error) {
    if (error instanceof ServiceAuthException) {
      console.log(`✓ Correctly rejected unauthorized call: ${error.error.code}`);
      return true;
    }
    console.error(`✗ Unexpected error: ${error}`);
    return false;
  }
}

/**
 * Test that invalid service names are rejected
 */
function testInvalidService(): boolean {
  console.log('\n=== Test 4: Invalid Service Name ===');

  try {
    // This should fail - invalid service name
    const token = createServiceToken(
      'invalid-service',
      'field-service',
      300,
    );
    console.error('✗ Test failed: Should have thrown an exception');
    return false;
  } catch (error) {
    if (error instanceof ServiceAuthException) {
      console.log(`✓ Correctly rejected invalid service: ${error.error.code}`);
      return true;
    }
    console.error(`✗ Unexpected error: ${error}`);
    return false;
  }
}

/**
 * Test service authorization checking
 */
function testServiceAuthorizationCheck(): boolean {
  console.log('\n=== Test 5: Service Authorization Check ===');

  // Authorized calls
  const authorizedPairs: [string, string][] = [
    ['farm-service', 'field-service'],
    ['crop-service', 'weather-service'],
    ['field-service', 'precision-ag-service'],
  ];

  for (const [service, target] of authorizedPairs) {
    if (isServiceAuthorized(service, target)) {
      console.log(`✓ ${service} → ${target} is authorized`);
    } else {
      console.error(`✗ ${service} → ${target} should be authorized`);
      return false;
    }
  }

  // Unauthorized calls
  const unauthorizedPairs: [string, string][] = [
    ['notification-service', 'farm-service'],
    ['analytics-service', 'crop-service'],
  ];

  for (const [service, target] of unauthorizedPairs) {
    if (!isServiceAuthorized(service, target)) {
      console.log(`✓ ${service} → ${target} is correctly unauthorized`);
    } else {
      console.error(`✗ ${service} → ${target} should be unauthorized`);
      return false;
    }
  }

  return true;
}

/**
 * Test getting allowed target services
 */
function testGetAllowedTargets(): boolean {
  console.log('\n=== Test 6: Get Allowed Targets ===');

  // Test farm-service
  const targets = getAllowedTargets('farm-service');
  console.log(`farm-service can call: ${targets.join(', ')}`);

  const expectedTargets = [
    'field-service',
    'crop-service',
    'equipment-service',
    'user-service',
    'tenant-service',
  ];
  for (const target of expectedTargets) {
    if (!targets.includes(target)) {
      console.error(`✗ Missing expected target: ${target}`);
      return false;
    }
  }

  console.log('✓ All expected targets found');

  // Test idp-service (should call all services)
  const idpTargets = getAllowedTargets('idp-service');
  console.log(`idp-service can call ${idpTargets.length} services`);

  if (idpTargets.length !== ALLOWED_SERVICES.length) {
    console.error('✗ IDP should be able to call all services');
    return false;
  }

  console.log('✓ IDP can call all services');
  return true;
}

/**
 * Test that all services are properly defined in the matrix
 */
function testAllServicesInMatrix(): boolean {
  console.log('\n=== Test 7: Service Matrix Validation ===');

  for (const service of ALLOWED_SERVICES) {
    if (!(service in SERVICE_COMMUNICATION_MATRIX)) {
      console.error(`✗ Service ${service} not in communication matrix`);
      return false;
    }
  }

  console.log(`✓ All ${ALLOWED_SERVICES.length} services defined in matrix`);

  // Count total communication paths
  const totalPaths = Object.values(SERVICE_COMMUNICATION_MATRIX)
    .reduce((sum, targets) => sum + targets.length, 0);
  console.log(`✓ Total communication paths: ${totalPaths}`);

  return true;
}

/**
 * Test token with very short TTL
 */
async function testTokenExpiration(): Promise<boolean> {
  console.log('\n=== Test 8: Token Expiration ===');

  try {
    // Create token with 1 second TTL
    const token = createServiceToken(
      'farm-service',
      'field-service',
      1,
    );
    console.log('✓ Token created with 1 second TTL');

    // Verify immediately (should work)
    verifyServiceToken(token);
    console.log('✓ Token verified immediately');

    // Wait 2 seconds
    console.log('  Waiting 2 seconds...');
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Try to verify (should fail)
    try {
      verifyServiceToken(token);
      console.error('✗ Expired token should have been rejected');
      return false;
    } catch (error) {
      console.log(`✓ Expired token correctly rejected`);
      return true;
    }
  } catch (error) {
    console.error(`✗ Test failed: ${error}`);
    return false;
  }
}

/**
 * Run all tests and report results
 */
async function runAllTests(): Promise<boolean> {
  console.log('\n' + '='.repeat(60));
  console.log('Service-to-Service Authentication Test Suite (TypeScript)');
  console.log('='.repeat(60));

  const tests: [string, () => boolean | Promise<boolean>][] = [
    ['Basic Token Creation', testBasicTokenCreation],
    ['ServiceToken Class', testServiceClass],
    ['Unauthorized Service Call', testUnauthorizedService],
    ['Invalid Service Name', testInvalidService],
    ['Service Authorization Check', testServiceAuthorizationCheck],
    ['Get Allowed Targets', testGetAllowedTargets],
    ['Service Matrix Validation', testAllServicesInMatrix],
    ['Token Expiration', testTokenExpiration],
  ];

  const results: [string, boolean][] = [];

  for (const [name, testFunc] of tests) {
    try {
      const result = await testFunc();
      results.push([name, result]);
    } catch (error) {
      console.error(`\n✗ Test '${name}' crashed: ${error}`);
      results.push([name, false]);
    }
  }

  // Print summary
  console.log('\n' + '='.repeat(60));
  console.log('Test Summary');
  console.log('='.repeat(60));

  const passed = results.filter(([_, result]) => result).length;
  const total = results.length;

  for (const [name, result] of results) {
    const status = result ? '✓ PASS' : '✗ FAIL';
    console.log(`${status}: ${name}`);
  }

  console.log(`\nResults: ${passed}/${total} tests passed`);

  if (passed === total) {
    console.log('\n🎉 All tests passed!');
    return true;
  } else {
    console.log(`\n⚠️  ${total - passed} test(s) failed`);
    return false;
  }
}

// Run tests if this file is executed directly
if (require.main === module) {
  runAllTests()
    .then(success => {
      process.exit(success ? 0 : 1);
    })
    .catch(error => {
      console.error('Fatal error:', error);
      process.exit(1);
    });
}

export { runAllTests };
