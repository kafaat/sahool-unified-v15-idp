# SAHOOL Marketplace Service - Test Suite Documentation

## Overview

This directory contains comprehensive test suites for the SAHOOL Marketplace Service, covering all major functionality including product management, order processing, and payment operations.

## Test Files

### 1. marketplace.controller.spec.ts

**Purpose**: Tests API endpoints and controller logic

**Coverage**:

- Health check endpoints
- Product API endpoints (GET, POST)
- Product filtering (category, governorate, seller, price range)
- Harvest to product conversion
- Order creation and retrieval
- Order authorization and permissions
- Market statistics
- Integration tests
- Error handling

**Key Test Cases**:

- ✓ Health check returns proper status
- ✓ Get all products with pagination
- ✓ Filter products by multiple criteria
- ✓ Create new products
- ✓ Convert yield predictions to products
- ✓ Create orders with validation
- ✓ Enforce resource ownership for orders
- ✓ Admin can access all user orders
- ✓ Returns market statistics

### 2. product.service.spec.ts

**Purpose**: Tests product CRUD operations and business logic

**Coverage**:

- Product retrieval and filtering
- Product creation
- Harvest to product conversion
- Stock management
- Market statistics
- Pagination handling
- Edge cases and error handling

**Key Test Cases**:

- ✓ Find all products with filters
- ✓ Find product by ID
- ✓ Create product with all fields
- ✓ Create product with minimal fields
- ✓ Convert yield data to product listing
- ✓ Generate proper crop image URLs
- ✓ Handle different seller types
- ✓ Track product stock
- ✓ Return featured products first
- ✓ Handle special characters in product names
- ✓ Support concurrent read operations

### 3. order.service.spec.ts

**Purpose**: Tests order management and processing

**Coverage**:

- Order creation (single and multiple products)
- Order calculations (subtotal, fees, totals)
- Stock management during orders
- Order retrieval (buyer/seller views)
- Transaction handling
- Event publishing
- Concurrent order handling
- Error handling

**Key Test Cases**:

- ✓ Create order with single product
- ✓ Create order with multiple products
- ✓ Calculate service fee (2%) correctly
- ✓ Include fixed delivery fee
- ✓ Generate unique order numbers
- ✓ Decrement product stock atomically
- ✓ Handle insufficient stock errors
- ✓ Handle product not found errors
- ✓ Use transactions for concurrent orders
- ✓ Return buyer and seller orders separately
- ✓ Publish order.placed events
- ✓ Publish inventory low stock events
- ✓ Handle large orders with many items

### 4. payment.service.spec.ts

**Purpose**: Tests wallet operations and payment processing

**Coverage**:

- Wallet creation and management
- Deposit operations
- Withdrawal operations
- Transaction history
- Wallet limits and security
- Idempotency protection
- Audit logging
- Escrow management
- Wallet dashboard
- FinTech service integration

**Key Test Cases**:

- ✓ Get existing wallet
- ✓ Create wallet if not exists
- ✓ Deposit money to wallet
- ✓ Prevent duplicate deposits with idempotency keys
- ✓ Withdraw money from wallet
- ✓ Enforce balance checks
- ✓ Enforce daily withdrawal limits
- ✓ Enforce single transaction limits
- ✓ Reset daily limits on new day
- ✓ Use optimistic locking for race conditions
- ✓ Use SERIALIZABLE isolation level
- ✓ Create audit logs
- ✓ Return transaction history
- ✓ Update wallet limits based on credit tier
- ✓ Create and manage escrow
- ✓ Return comprehensive wallet dashboard

## Running Tests

### Prerequisites

Install dependencies first:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/marketplace-service
npm install
```

### Run All Tests

```bash
npm test
```

### Run Specific Test Suite

```bash
npm test -- marketplace.controller.spec.ts
npm test -- product.service.spec.ts
npm test -- order.service.spec.ts
npm test -- payment.service.spec.ts
```

### Run Tests in Watch Mode

```bash
npm test:watch
```

### Generate Coverage Report

```bash
npm test:cov
```

## Test Architecture

### Mocking Strategy

All tests use Jest mocks for:

- **PrismaService**: Database operations
- **EventsService**: NATS event publishing
- **External Services**: Credit, Loan, Escrow services

### Test Structure

Each test file follows this pattern:

1. **Setup**: Mock service initialization
2. **Test Suites**: Grouped by functionality
3. **Test Cases**: Individual test scenarios
4. **Cleanup**: Clear mocks after each test

### Assertions

Tests verify:

- Return values and data structures
- Function call parameters
- Error handling and messages
- Side effects (event publishing, audit logs)

## Code Coverage Goals

Target coverage for each file:

- **Statements**: ≥ 90%
- **Branches**: ≥ 85%
- **Functions**: ≥ 90%
- **Lines**: ≥ 90%

## Best Practices

### 1. Test Independence

Each test is independent and can run in any order.

### 2. Clear Test Names

Test names clearly describe what is being tested:

```typescript
it("should create an order with multiple products", async () => {
  // Test implementation
});
```

### 3. Arrange-Act-Assert Pattern

```typescript
// Arrange
const orderData = { ... };
mockService.method.mockResolvedValue(mockData);

// Act
const result = await service.createOrder(orderData);

// Assert
expect(result).toEqual(expectedResult);
```

### 4. Mock Data Realism

Mock data reflects real-world scenarios with:

- Realistic IDs and names
- Proper Arabic translations
- Valid data types and ranges
- Yemeni cultural context

### 5. Error Testing

Every happy path has corresponding error tests:

```typescript
it('should create product successfully', ...);
it('should throw error for invalid product data', ...);
```

## Common Testing Patterns

### Testing API Endpoints

```typescript
const result = await controller.getProducts("HARVEST");
expect(mockMarketService.findAllProducts).toHaveBeenCalledWith({
  category: "HARVEST",
});
```

### Testing Database Transactions

```typescript
mockPrismaService.$transaction.mockImplementation(async (callback) => {
  const tx = {
    /* mock transaction object */
  };
  return callback(tx);
});
```

### Testing Event Publishing

```typescript
await service.createOrder(orderData);
expect(mockEventsService.publishOrderPlaced).toHaveBeenCalledWith(
  expect.objectContaining({
    orderId: expect.any(String),
    totalAmount: expect.any(Number),
  }),
);
```

### Testing Error Handling

```typescript
mockService.method.mockRejectedValue(new Error("Error message"));
await expect(service.method()).rejects.toThrow("Error message");
```

## Debugging Tests

### View Test Output

```bash
npm test -- --verbose
```

### Run Single Test

```bash
npm test -- --testNamePattern="should create product"
```

### Debug with Node Inspector

```bash
node --inspect-brk node_modules/.bin/jest --runInBand
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Fast execution (< 10 seconds for all tests)
- No external dependencies
- Deterministic results
- Clear failure messages

## Maintenance

### When to Update Tests

1. **Adding New Features**: Write tests first (TDD)
2. **Bug Fixes**: Add test to reproduce bug, then fix
3. **Refactoring**: Ensure all tests still pass
4. **API Changes**: Update corresponding controller tests

### Test Naming Convention

- Files: `*.spec.ts`
- Test suites: `describe('ServiceName - Feature', ...)`
- Test cases: `it('should do something specific', ...)`

## Related Documentation

- [NestJS Testing Guide](https://docs.nestjs.com/fundamentals/testing)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Prisma Testing Guide](https://www.prisma.io/docs/guides/testing/unit-testing)

## Contact

For questions about these tests, contact the SAHOOL development team.

---

**Last Updated**: 2026-01-07
**Test Count**: 100+ test cases
**Coverage**: Product, Order, Payment, and API endpoints
