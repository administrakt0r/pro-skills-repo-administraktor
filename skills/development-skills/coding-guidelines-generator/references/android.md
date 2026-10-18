# Android Guidelines

> Verified: 2026-10-18, Android Developer Official Docs, applies to Android API 24+ / AGP 8.x-9.x / Compose 1.7+

## Architecture & State
- **State Flow**: Use unidirectional data flow (UDF). Expose state from ViewModels as immutable `StateFlow<UiState>`. Never expose mutable `MutableStateFlow` or `MutableState` publicly.
- **Coroutines & Lifecycle**: Launch coroutines from ViewModels using `viewModelScope`. In Compose, use `collectAsStateWithLifecycle()` to stop flow collection when the lifecycle falls below `Lifecycle.State.STARTED`.
- **Process Death**: Handle configuration changes and process recreation by storing transient navigation and filter state via `SavedStateHandle`.
- **Jetpack Compose**: Keep composable functions restartable and skippable. Never perform I/O, database access, or heavy computation inside a composable function body; defer to ViewModels or `rememberCoroutineScope()`.

## Persistence & Security
- **Room Migrations**: Always specify explicit, automated, or manual `Migration` objects for database schema changes; never set `fallbackToDestructiveMigration()` in production code.
- **Security & Secrets**: Never commit keystores, signing keys, API tokens, or server secrets to VCS. Load credentials from environment variables or `local.properties` via Gradle BuildConfig/resValue.
- **Permissions**: Request runtime permissions incrementally right when needed, explaining context before the system prompt. Never assume a permission is granted across app launches.

## Build & Verification
- **Gradle**: Manage dependencies using Gradle Version Catalogs (`gradle/libs.versions.toml`).
- **Commands**:
  - Assemble: `./gradlew assembleDebug`
  - Unit tests: `./gradlew test`
  - Static analysis: `./gradlew lint`
- **R8 / Proguard**: When adding reflection-based libraries or data models, verify keep rules rather than disabling R8 or applying wildcard `-keep class **`.
