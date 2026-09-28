# Stack discovery lookup

Use this to find how a repo builds, lints, and tests itself. It is a map of where to look, not a list of commands to assume. Always prefer what the repo's CI workflow actually runs, and only use commands the repo's own config evidences.

## Where CI lives (check first, it is the source of truth)

`.github/workflows/*.yml`, `.gitlab-ci.yml`, `.circleci/config.yml`, `azure-pipelines.yml`, `Jenkinsfile`, `bitbucket-pipelines.yml`, `.travis.yml`, `Makefile`, `justfile`, `Taskfile.yml`

## By stack

| Stack | Manifest / config to read | Typical places for scripts |
|---|---|---|
| Node / JS / TS | `package.json`, lockfile (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `bun.lockb`), `tsconfig.json`, `.nvmrc` | `scripts` block; workspaces field for monorepos. Use the package manager the lockfile indicates. |
| PHP | `composer.json`, `composer.lock`, `phpunit.xml`, `phpstan.neon`, `.php-cs-fixer.php`, `pint.json` | `scripts` block in composer.json; framework config (Laravel, Symfony, WordPress) |
| Go | `go.mod`, `go.work`, `Makefile`, `.golangci.yml` | `go build ./...`, `go vet`, `go test ./...` only if go.mod/CI indicates |
| Python | `pyproject.toml`, `setup.cfg`, `tox.ini`, `noxfile.py`, `requirements*.txt`, `Pipfile`, `.flake8`, `ruff.toml` | tool sections in pyproject; tox/nox envs |
| Rust | `Cargo.toml`, `Cargo.lock`, `rust-toolchain.toml`, `clippy.toml`, `rustfmt.toml` | cargo build/test/clippy/fmt as CI runs them |
| Ruby | `Gemfile`, `Gemfile.lock`, `.rubocop.yml`, `Rakefile` | rake tasks, bundler |
| Java / Kotlin / Android | `build.gradle(.kts)`, `settings.gradle(.kts)`, `gradlew`, `pom.xml`, `AndroidManifest.xml`, `lint.xml`, `detekt.yml`, `ktlint` config | Use the **Gradle/Maven wrapper** in the repo (`./gradlew`), not a system install. Android: unit tests and assemble/lint are usually runnable; instrumented tests need an emulator. |
| iOS / Swift | `*.xcodeproj`, `Package.swift`, `Podfile`, `fastlane/` | Usually needs macOS; if unavailable, review statically and say so |
| .NET | `*.sln`, `*.csproj`, `global.json` | dotnet build/test as CI does |
| Docker / infra | `Dockerfile`, `docker-compose.yml`, `*.tf`, `helm/`, `k8s/` | Infra changes are high-risk: BLOCKED by default |

## Reading "what ships"

- Library: publishable manifest (`"main"`/`"exports"`, `[lib]`, package metadata), no deploy config. "Working" means tests pass and public API is not broken.
- Web app / API: Dockerfile, deploy workflow, health endpoint, documented staging URL. "Working" means build passes and the health/smoke check responds.
- CLI: `bin` entries, `[[bin]]`, `main` package. "Working" means it builds and a `--help` or `--version` smoke run succeeds.
- Mobile app: store metadata, signing config, Gradle/Xcode targets. "Working" usually means it builds and unit tests pass; runtime on a device is unverified unless an emulator is available.
- Monorepo: workspaces, `packages/`, `apps/`, Nx/Turborepo/Bazel/Lerna config. Test affected packages first.

## Merge method hints

Look at recent merged history: single-parent commits with `(#123)` suffix suggest squash; "Merge pull request" commits suggest merge commits; linear history without PR markers suggests rebase. Repo settings (allowed merge methods) override this if readable.

## Safety reminder

Installing dependencies runs third-party code (postinstall scripts, build plugins). Do this only in an environment without real credentials, and never for a PR that modifies install/build scripts or lockfiles suspiciously.
