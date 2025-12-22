# ADR-002: Riverpod for State Management

## Status

Accepted

## Context

The SAHOOL mobile app requires robust state management for:

1. **Complex state**: Multi-screen forms, filters, sync status
2. **Dependency injection**: Services, repositories, configs
3. **Reactive updates**: Real-time UI updates on data changes
4. **Offline state**: Sync status, queue depth, conflict flags
5. **Testing**: Easy to mock and test business logic

We evaluated several Flutter state management solutions.

## Decision

We chose **Riverpod 2.x** as our state management solution.

### Key Reasons

1. **Compile-time safety**: Provider errors caught at compile time
2. **No BuildContext dependency**: Can access state anywhere
3. **Built-in caching**: Automatic disposal and caching
4. **Code generation**: Reduces boilerplate with riverpod_generator
5. **Testing support**: Easy to override providers in tests

### Implementation Pattern

```dart
// Provider definition
@riverpod
class FieldsNotifier extends _$FieldsNotifier {
  @override
  Future<List<Field>> build() async {
    final repository = ref.watch(fieldRepositoryProvider);
    return repository.getAll();
  }

  Future<void> addField(Field field) async {
    final repository = ref.read(fieldRepositoryProvider);
    await repository.insert(field);
    ref.invalidateSelf();
  }
}

// Usage in widget
class FieldsScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fieldsAsync = ref.watch(fieldsNotifierProvider);

    return fieldsAsync.when(
      data: (fields) => FieldsList(fields: fields),
      loading: () => const LoadingIndicator(),
      error: (e, st) => ErrorWidget(error: e),
    );
  }
}
```

## Consequences

### Positive

- **Type safety**: Compile-time provider validation
- **Testability**: Easy provider overrides in tests
- **Performance**: Fine-grained rebuilds with select()
- **DevTools**: Excellent debugging with Riverpod DevTools
- **Community**: Large ecosystem and documentation

### Negative

- **Learning curve**: Different paradigm from Provider
- **Boilerplate**: Requires code generation setup
- **Migration effort**: Converting from Provider took 2 weeks
- **Version churn**: API changes between major versions

### Neutral

- Code generation adds build step
- Requires understanding of AsyncValue pattern

## Alternatives Considered

### Alternative 1: Provider (Original)

**Rejected because:**
- Runtime errors for missing providers
- Requires BuildContext for access
- Limited caching capabilities
- Riverpod is the successor by same author

### Alternative 2: BLoC

**Rejected because:**
- More boilerplate for simple state
- Streams add complexity
- Less intuitive for team
- Overkill for our use case

### Alternative 3: GetX

**Rejected because:**
- Less type safety
- Controversial patterns
- Mixing concerns (routing, state, DI)
- Smaller enterprise adoption

## Migration Notes

Migrated from Provider to Riverpod in Sprint 8:
- 47 providers converted
- 2 weeks development time
- Zero production regressions

## References

- [Riverpod Documentation](https://riverpod.dev/)
- [riverpod_generator](https://pub.dev/packages/riverpod_generator)
- [Migration Guide](https://riverpod.dev/docs/migration/from_provider)
