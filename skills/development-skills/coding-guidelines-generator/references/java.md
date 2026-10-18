# Java & Kotlin (Backend) Guidelines

> Verified: 2026-10-18, Oracle Java 21+ LTS & Kotlin 2.0+ Documentation

## Architecture & Nullability
- **Null Safety**: In Kotlin, embrace nullable types (`T?`) and smart casting; avoid the not-null assertion operator (`!!`). In Java, use `@NonNull` / `@Nullable` annotations or `Optional<T>` for return values that may be absent. Never return `null` for collections; return empty collections (`Collections.emptyList()`).
- **Resource Management**: In Java, always use `try-with-resources` for `AutoCloseable` instances. In Kotlin, use `.use { ... }`.

## Testing & Build
- **JUnit 5**: Use modern JUnit 5 (`@Test`, `@ParameterizedTest`, `@DisplayName`).
- **Build Tools**:
  - Gradle: `./gradlew test` and `./gradlew check`
  - Maven: `./mvnw clean test`
