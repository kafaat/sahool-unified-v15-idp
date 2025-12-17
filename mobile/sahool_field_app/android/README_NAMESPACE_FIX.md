# Android Build Configuration

## Namespace Fix for AGP 8.0+ Compatibility

### Problem
Android Gradle Plugin (AGP) 8.0+ requires all Android modules to explicitly specify a `namespace` in their build configuration. Third-party Flutter plugins that haven't been updated may be missing this declaration, causing build failures:

```
A problem occurred configuring project ':isar_flutter_libs'.
> Could not create an instance of type com.android.build.api.variant.impl.LibraryVariantBuilderImpl.
   > Namespace not specified. Specify a namespace in the module's build file.
```

### Solution
We've implemented a Groovy-based script (`fix-namespace.gradle`) that automatically adds the missing namespace to any plugin that doesn't have it defined. This script:

1. Iterates through all subprojects after evaluation
2. Checks if the project is an Android library or application
3. If namespace is missing, automatically assigns one based on the plugin name
4. Logs a warning for visibility

### Files
- `android/fix-namespace.gradle` - The Groovy script that performs the fix
- `android/build.gradle.kts` - Applies the fix-namespace.gradle script

### Why This Approach?
- **Non-invasive**: Doesn't modify third-party plugin source code
- **Maintainable**: Works across dependency updates
- **Groovy-based**: More reliable than Kotlin DSL reflection for dynamic configuration
- **Automatic**: No manual intervention needed for new plugins

### Alternative Solutions
1. **Update to community fork**: Use isar-community.dev packages (requires changing dependency source)
2. **Manual patching**: Edit cached dependencies (reset on updates)
3. **Kotlin DSL workaround**: More complex with reflection/type casting

### References
- [Android Developers: AGP 8.0 Migration](https://developer.android.com/build/releases/past-releases/agp-8-0-0-release-notes)
- [Isar GitHub Issue #1354](https://github.com/isar/isar/issues/1354)
- [Stack Overflow: Namespace Not Defined](https://stackoverflow.com/questions/79031081/flutter-isar-database-v3-1-01-namespace-not-defined)
