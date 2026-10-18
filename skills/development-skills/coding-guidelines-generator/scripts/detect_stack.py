#!/usr/bin/env python3
"""
detect_stack.py - Deterministic, stdlib-only technology stack detector.

Scans a repository to detect programming languages, frameworks, build systems,
linters, and package managers without making any network calls.
Emits a structured JSON report to stdout.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Directories to skip unconditionally
IGNORED_DIRS: Set[str] = {
    "node_modules", "vendor", ".git", "build", "dist", ".gradle",
    ".venv", "venv", "__pycache__", ".next", ".turbo", ".output",
    ".cache", "target", "bin", "obj", ".idea", ".vscode"
}

# Limits for safety and token efficiency
MAX_FILES_SCANNED = 600
MAX_BYTES_READ = 65536  # 64 KB per file


def read_file_safe(path: Path, max_bytes: int = MAX_BYTES_READ) -> str:
    """Read a text file safely with size capping and encoding fallback."""
    try:
        with open(path, "rb") as f:
            chunk = f.read(max_bytes)
            return chunk.decode("utf-8", errors="replace")
    except Exception:
        return ""


def parse_json_safe(path: Path) -> Dict[str, Any]:
    """Parse JSON file safely, returning empty dict on failure."""
    content = read_file_safe(path)
    if not content:
        return {}
    try:
        return json.loads(content)
    except Exception:
        return {}


def is_safe_path(base_root: Path, target: Path) -> bool:
    """Ensure path does not follow symlinks outside base root."""
    try:
        resolved = target.resolve()
        base_resolved = base_root.resolve()
        return str(resolved).startswith(str(base_resolved))
    except Exception:
        return False


def collect_directory_entries(root: Path, max_depth: int) -> Tuple[List[Path], List[Path]]:
    """
    Collect files and directories respecting depth and ignored directories.
    Returns (files, directories).
    """
    files: List[Path] = []
    dirs: List[Path] = []
    base_depth = len(root.parts)

    for current_dir, dirnames, filenames in os.walk(root, followlinks=False):
        current_path = Path(current_dir)
        # Prune ignored directories
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]

        depth = len(current_path.parts) - base_depth
        if depth > max_depth:
            dirnames.clear()
            continue

        dirs.append(current_path)

        for fname in filenames:
            fpath = current_path / fname
            if is_safe_path(root, fpath):
                files.append(fpath)
                if len(files) >= MAX_FILES_SCANNED:
                    return files, dirs

    return files, dirs


def detect_monorepo(root: Path, files: List[Path], dirs: List[Path]) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    Detect whether the project is a monorepo and list package directories.
    """
    is_monorepo = False
    packages: List[Dict[str, Any]] = []

    root_pkg_json = parse_json_safe(root / "package.json")
    if "workspaces" in root_pkg_json or (root / "pnpm-workspace.yaml").exists() or (root / "lerna.json").exists():
        is_monorepo = True

    cargo_toml = read_file_safe(root / "Cargo.toml")
    if "[workspace]" in cargo_toml:
        is_monorepo = True

    if (root / "go.work").exists():
        is_monorepo = True

    settings_gradle = read_file_safe(root / "settings.gradle") + read_file_safe(root / "settings.gradle.kts")
    if "include(" in settings_gradle or "include " in settings_gradle:
        # Multi-module gradle
        is_monorepo = True

    # Scan package directories
    candidate_dirs = [d for d in dirs if d != root and (d.parent == root or d.parent.parent == root)]
    for c_dir in candidate_dirs:
        has_pkg = (c_dir / "package.json").exists() or (c_dir / "build.gradle").exists() or \
                  (c_dir / "build.gradle.kts").exists() or (c_dir / "Cargo.toml").exists() or \
                  (c_dir / "go.mod").exists() or (c_dir / "pyproject.toml").exists() or \
                  (c_dir / "composer.json").exists()

        if has_pkg:
            has_agents_md = (c_dir / "AGENTS.md").exists()
            rel_dir = str(c_dir.relative_to(root))
            packages.append({
                "directory": rel_dir,
                "has_local_agents_md": has_agents_md
            })

    if len(packages) >= 2:
        is_monorepo = True

    return is_monorepo, packages


def detect_android(dir_path: Path, files_in_dir: List[Path]) -> Optional[Dict[str, Any]]:
    """Detect Android stack in a directory."""
    has_android_plugin = False
    is_compose = False
    is_kotlin = False
    min_sdk = None
    target_sdk = None
    di_framework = None
    evidence: List[str] = []

    # Check Gradle files
    for gfile_name in ["build.gradle", "build.gradle.kts", "app/build.gradle", "app/build.gradle.kts"]:
        gpath = dir_path / gfile_name
        if gpath.exists():
            content = read_file_safe(gpath)
            if "com.android.application" in content or "com.android.library" in content or "com.android" in content:
                has_android_plugin = True
                evidence.append(gfile_name)
            if "compose" in content or "androidx.compose" in content or "composeOptions" in content:
                is_compose = True
            if "org.jetbrains.kotlin" in content or "kotlin" in content or gfile_name.endswith(".kts"):
                is_kotlin = True
            if "dagger.hilt" in content or "hilt" in content:
                di_framework = "Hilt"
            elif "org.koin" in content or "koin" in content:
                di_framework = "Koin"
            # check SDK
            for line in content.splitlines():
                if "minSdk" in line:
                    parts = line.split("=") if "=" in line else line.split()
                    if len(parts) >= 2:
                        min_sdk = parts[-1].strip().strip('"').strip("'")
                if "targetSdk" in line:
                    parts = line.split("=") if "=" in line else line.split()
                    if len(parts) >= 2:
                        target_sdk = parts[-1].strip().strip('"').strip("'")

    # Check AndroidManifest.xml
    manifests = list(dir_path.glob("**/AndroidManifest.xml"))
    if manifests:
        has_android_plugin = True
        evidence.append(str(manifests[0].relative_to(dir_path)))

    if not has_android_plugin:
        return None

    # Check kotlin files presence
    kt_files = list(dir_path.glob("**/*.kt"))
    if kt_files:
        is_kotlin = True

    gradle_wrapper = (dir_path / "gradlew").exists()
    build_cmd = "./gradlew assembleDebug" if gradle_wrapper else "gradle assembleDebug"
    test_cmd = "./gradlew test" if gradle_wrapper else "gradle test"
    lint_cmd = "./gradlew lint" if gradle_wrapper else "gradle lint"

    addons = []
    if is_compose:
        addons.append("Jetpack Compose")
    else:
        addons.append("XML Views")
    if di_framework:
        addons.append(f"DI: {di_framework}")
    if min_sdk:
        addons.append(f"minSdk: {min_sdk}")

    return {
        "stack": "android",
        "primary_language": "kotlin" if is_kotlin else "java",
        "layer_chain": ["android"],
        "target_file": "AGENTS-GUIDELINES-ANDROID.md",
        "reference_files": ["references/android.md"],
        "version": f"Android (minSdk {min_sdk or 'unknown'})",
        "package_manager": "gradle",
        "build_command": build_cmd,
        "test_command": test_cmd,
        "lint_command": lint_cmd,
        "framework_addons": addons,
        "confidence": "high",
        "evidence_files": evidence
    }


def detect_wordpress_and_php(dir_path: Path, files_in_dir: List[Path]) -> Optional[Dict[str, Any]]:
    """Detect WordPress (theme, plugin, full site) or standard PHP."""
    evidence: List[str] = []
    is_wp = False
    wp_type = None
    php_version = None

    # Check wp-config.php (Full site)
    if (dir_path / "wp-config.php").exists():
        is_wp = True
        wp_type = "site"
        evidence.append("wp-config.php")

    # Check style.css for Theme Name
    style_css = dir_path / "style.css"
    if style_css.exists():
        header_text = read_file_safe(style_css, max_bytes=8192)
        if "Theme Name:" in header_text:
            is_wp = True
            wp_type = "theme"
            evidence.append("style.css (Theme Name)")

    # Check for plugin header in PHP files
    for php_file in list(dir_path.glob("*.php")) + list(dir_path.glob("wp-content/plugins/*/*.php")):
        content = read_file_safe(php_file, max_bytes=8192)
        if "Plugin Name:" in content:
            is_wp = True
            wp_type = "plugin"
            evidence.append(str(php_file.relative_to(dir_path)))
            break

    # Check composer.json for PHP
    composer_json = dir_path / "composer.json"
    framework = None
    lint_cmd = None
    test_cmd = None

    if composer_json.exists():
        c_data = parse_json_safe(composer_json)
        require = c_data.get("require", {})
        require_dev = c_data.get("require-dev", {})
        scripts = c_data.get("scripts", {})

        evidence.append("composer.json")
        if "php" in require:
            php_version = require["php"]

        if "laravel/framework" in require:
            framework = "Laravel"
        elif "symfony/framework-bundle" in require:
            framework = "Symfony"
        elif "roots/bedrock" in require or "johnpbloch/wordpress" in require:
            is_wp = True
            wp_type = "bedrock/site"

        if "test" in scripts:
            test_cmd = "composer test"
        elif "phpunit/phpunit" in require_dev or (dir_path / "phpunit.xml").exists():
            test_cmd = "./vendor/bin/phpunit"

        if "lint" in scripts:
            lint_cmd = "composer lint"
        elif "squizlabs/php_codesniffer" in require_dev:
            lint_cmd = "./vendor/bin/phpcs"

    if is_wp:
        addons = [f"WordPress {wp_type}"] if wp_type else ["WordPress"]
        if (dir_path / "theme.json").exists():
            addons.append("Block Theme (theme.json)")
        return {
            "stack": "wordpress",
            "layer_chain": ["php", "wordpress"],
            "target_file": "AGENTS-GUIDELINES-WORDPRESS.md",
            "reference_files": ["references/php.md", "references/wordpress.md"],
            "version": php_version or "PHP 8.1+",
            "package_manager": "composer" if composer_json.exists() else "none",
            "build_command": "composer install --no-dev" if composer_json.exists() else None,
            "test_command": test_cmd or "phpunit",
            "lint_command": lint_cmd or "phpcs",
            "framework_addons": addons,
            "confidence": "high",
            "evidence_files": evidence
        }

    if composer_json.exists() or list(dir_path.glob("*.php")):
        addons = [framework] if framework else []
        return {
            "stack": "php",
            "layer_chain": ["php"],
            "target_file": "AGENTS-GUIDELINES-PHP.md",
            "reference_files": ["references/php.md"],
            "version": php_version or "PHP 8.1+",
            "package_manager": "composer" if composer_json.exists() else "none",
            "build_command": "composer install",
            "test_command": test_cmd or "./vendor/bin/phpunit",
            "lint_command": lint_cmd or "./vendor/bin/phpcs",
            "framework_addons": addons,
            "confidence": "high" if composer_json.exists() else "medium",
            "evidence_files": evidence or ["*.php"]
        }

    return None


def is_build_tooling_only_package_json(pkg_data: Dict[str, Any]) -> bool:
    """
    Check if a package.json is purely build tooling (common in PHP/WordPress/Android repos)
    rather than a standalone JS application.
    """
    deps = pkg_data.get("dependencies", {})
    dev_deps = pkg_data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}

    # If it depends on next, express, nest, electron, react-native, sveltekit, nuxt -> primary
    app_indicators = {"next", "express", "koa", "nest", "@nestjs/core", "electron", "react-native", "@sveltejs/kit", "nuxt"}
    if any(app in all_deps for app in app_indicators):
        return False

    # Common build tool packages
    tooling_packages = {
        "webpack", "vite", "gulp", "grunt", "sass", "tailwindcss", "postcss",
        "@wordpress/scripts", "autoprefixer", "esbuild", "rollup", "babel-loader",
        "prettier", "eslint"
    }
    # If all or nearly all dependencies are build tools and no major server/client framework
    if all_deps and all(any(tool in pkg for tool in tooling_packages) for pkg in all_deps.keys()):
        return True

    return False


def detect_js_ts_react_next(dir_path: Path, has_primary_non_js: bool) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Detect JavaScript, TypeScript, React, and Next.js layers.
    Returns (primary_stack, secondary_tooling).
    """
    pkg_json_path = dir_path / "package.json"
    if not pkg_json_path.exists():
        return None, None

    pkg_data = parse_json_safe(pkg_json_path)
    deps = pkg_data.get("dependencies", {})
    dev_deps = pkg_data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}
    scripts = pkg_data.get("scripts", {})

    evidence = ["package.json"]

    # Package manager detection
    pm = "npm"
    if (dir_path / "pnpm-lock.yaml").exists():
        pm = "pnpm"
        evidence.append("pnpm-lock.yaml")
    elif (dir_path / "yarn.lock").exists():
        pm = "yarn"
        evidence.append("yarn.lock")
    elif (dir_path / "bun.lockb").exists() or (dir_path / "bun.lock").exists():
        pm = "bun"
        evidence.append("bun.lockb")
    elif (dir_path / "package-lock.json").exists():
        evidence.append("package-lock.json")

    # TypeScript detection
    has_ts = False
    ts_configs = list(dir_path.glob("tsconfig*.json"))
    if ts_configs or "typescript" in all_deps:
        has_ts = True
        if ts_configs:
            evidence.append(ts_configs[0].name)

    # Next.js detection
    has_next = "next" in all_deps or any(dir_path.glob("next.config.*"))
    # React detection
    has_react = "react" in all_deps

    # Commands
    build_cmd = f"{pm} run build" if "build" in scripts else None
    test_cmd = f"{pm} test" if "test" in scripts else None
    lint_cmd = f"{pm} run lint" if "lint" in scripts else None

    # Check if this is merely build tooling for another primary stack
    if has_primary_non_js and is_build_tooling_only_package_json(pkg_data):
        secondary = {
            "type": "build_tooling",
            "package_manager": pm,
            "has_typescript": has_ts,
            "evidence": evidence
        }
        return None, secondary

    # Layer chain construction
    if has_next:
        layer_chain = ["javascript"]
        if has_ts:
            layer_chain.append("typescript")
        layer_chain.extend(["react", "nextjs"])

        # App router vs Pages router
        is_app_router = (dir_path / "app").exists() or (dir_path / "src" / "app").exists()
        next_ver = deps.get("next", dev_deps.get("next", "latest"))

        addons = ["App Router" if is_app_router else "Pages Router"]
        if has_ts:
            addons.append("TypeScript")

        return {
            "stack": "nextjs",
            "layer_chain": layer_chain,
            "target_file": "AGENTS-GUIDELINES-NEXTJS.md",
            "reference_files": ["references/nextjs.md"],
            "version": f"Next.js {next_ver}",
            "package_manager": pm,
            "build_command": build_cmd or f"{pm} run build",
            "test_command": test_cmd or f"{pm} test",
            "lint_command": lint_cmd or f"{pm} run lint",
            "framework_addons": addons,
            "confidence": "high",
            "evidence_files": evidence
        }, None

    if has_react:
        layer_chain = ["javascript"]
        if has_ts:
            layer_chain.append("typescript")
        layer_chain.append("react")

        react_ver = deps.get("react", dev_deps.get("react", "latest"))
        addons = ["TypeScript"] if has_ts else []

        return {
            "stack": "react",
            "layer_chain": layer_chain,
            "target_file": "AGENTS-GUIDELINES-REACT.md",
            "reference_files": ["references/react.md"],
            "version": f"React {react_ver}",
            "package_manager": pm,
            "build_command": build_cmd or f"{pm} run build",
            "test_command": test_cmd or f"{pm} test",
            "lint_command": lint_cmd or f"{pm} run lint",
            "framework_addons": addons,
            "confidence": "high",
            "evidence_files": evidence
        }, None

    # Base JS/TS
    layer_chain = ["javascript", "typescript"] if has_ts else ["javascript"]
    refs = ["references/javascript.md"]
    if has_ts:
        refs.append("references/typescript.md")

    return {
        "stack": "typescript" if has_ts else "javascript",
        "layer_chain": layer_chain,
        "target_file": "AGENTS-GUIDELINES-JS.md",
        "reference_files": refs,
        "version": "TypeScript" if has_ts else "ESM/Node.js",
        "package_manager": pm,
        "build_command": build_cmd,
        "test_command": test_cmd or f"{pm} test",
        "lint_command": lint_cmd or f"{pm} run lint",
        "framework_addons": ["TypeScript (strict)"] if has_ts else [],
        "confidence": "high",
        "evidence_files": evidence
    }, None


def detect_python(dir_path: Path, files_in_dir: List[Path]) -> Optional[Dict[str, Any]]:
    """Detect Python stack."""
    evidence: List[str] = []
    has_python = False
    pyproject = dir_path / "pyproject.toml"
    reqs = list(dir_path.glob("requirements*.txt"))
    uv_lock = dir_path / "uv.lock"
    poetry_lock = dir_path / "poetry.lock"
    pipfile = dir_path / "Pipfile"
    setup_py = dir_path / "setup.py"

    pm = "pip"
    if uv_lock.exists():
        pm = "uv"
        evidence.append("uv.lock")
        has_python = True
    elif poetry_lock.exists():
        pm = "poetry"
        evidence.append("poetry.lock")
        has_python = True
    elif pipfile.exists():
        pm = "pipenv"
        evidence.append("Pipfile")
        has_python = True
    elif pyproject.exists():
        evidence.append("pyproject.toml")
        has_python = True
    elif reqs:
        evidence.append(reqs[0].name)
        has_python = True
    elif setup_py.exists():
        evidence.append("setup.py")
        has_python = True

    if not has_python and not list(dir_path.glob("*.py")):
        return None

    # Check frameworks
    frameworks = []
    content = ""
    if pyproject.exists():
        content += read_file_safe(pyproject)
    for r in reqs:
        content += read_file_safe(r)

    content_lower = content.lower()
    if "fastapi" in content_lower:
        frameworks.append("FastAPI")
    if "django" in content_lower:
        frameworks.append("Django")
    if "flask" in content_lower:
        frameworks.append("Flask")

    test_cmd = f"{pm} run pytest" if pm in ("poetry", "uv") else "pytest"
    lint_cmd = f"{pm} run ruff check" if "ruff" in content_lower and pm in ("poetry", "uv") else "ruff check ."

    return {
        "stack": "python",
        "layer_chain": ["python"],
        "target_file": "AGENTS-GUIDELINES-PYTHON.md",
        "reference_files": ["references/python.md"],
        "version": "Python 3.10+",
        "package_manager": pm,
        "build_command": None,
        "test_command": test_cmd,
        "lint_command": lint_cmd,
        "framework_addons": frameworks,
        "confidence": "high" if evidence else "medium",
        "evidence_files": evidence or ["*.py"]
    }


def detect_extras(dir_path: Path) -> List[Dict[str, Any]]:
    """Detect Go, Rust, Java (non-Android)."""
    extras = []
    # Go
    go_mod = dir_path / "go.mod"
    if go_mod.exists():
        extras.append({
            "stack": "go",
            "layer_chain": ["go"],
            "target_file": "AGENTS-GUIDELINES-GO.md",
            "reference_files": ["references/go.md"],
            "version": "Go",
            "package_manager": "go modules",
            "build_command": "go build ./...",
            "test_command": "go test ./...",
            "lint_command": "golangci-lint run",
            "framework_addons": [],
            "confidence": "high",
            "evidence_files": ["go.mod"]
        })

    # Rust
    cargo_toml = dir_path / "Cargo.toml"
    if cargo_toml.exists():
        extras.append({
            "stack": "rust",
            "layer_chain": ["rust"],
            "target_file": "AGENTS-GUIDELINES-RUST.md",
            "reference_files": ["references/rust.md"],
            "version": "Rust",
            "package_manager": "cargo",
            "build_command": "cargo build --release",
            "test_command": "cargo test",
            "lint_command": "cargo clippy -- -D warnings",
            "framework_addons": [],
            "confidence": "high",
            "evidence_files": ["Cargo.toml"]
        })

    return extras


def scan_target(root: Path, max_depth: int = 4) -> Dict[str, Any]:
    """Scan root and produce final detection report."""
    files, dirs = collect_directory_entries(root, max_depth)
    is_monorepo, packages = detect_monorepo(root, files, dirs)

    stacks: List[Dict[str, Any]] = []
    secondary_tooling: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # Directories to inspect: root, plus packages in monorepo
    targets = [root]
    if is_monorepo and packages:
        for pkg in packages:
            p_path = root / pkg["directory"]
            if p_path not in targets:
                targets.append(p_path)

    for target_dir in targets:
        rel_dir = str(target_dir.relative_to(root)) if target_dir != root else "."
        has_local_agents_md = (target_dir / "AGENTS.md").exists()
        files_in_target = [f for f in files if str(f).startswith(str(target_dir))]

        # 1. Android
        android_res = detect_android(target_dir, files_in_target)
        # 2. WordPress / PHP
        wp_php_res = detect_wordpress_and_php(target_dir, files_in_target)

        has_primary_non_js = (android_res is not None) or (wp_php_res is not None)

        # 3. JS / TS / React / Next.js
        js_res, sec_tooling = detect_js_ts_react_next(target_dir, has_primary_non_js)
        # 4. Python
        python_res = detect_python(target_dir, files_in_target)
        # 5. Extras (Go, Rust)
        extras_res = detect_extras(target_dir)

        detected_for_dir = []
        if android_res:
            detected_for_dir.append(android_res)
        if wp_php_res:
            detected_for_dir.append(wp_php_res)
        if js_res:
            detected_for_dir.append(js_res)
        if python_res:
            detected_for_dir.append(python_res)
        detected_for_dir.extend(extras_res)

        if sec_tooling:
            sec_tooling["directory"] = rel_dir
            secondary_tooling.append(sec_tooling)

        for s in detected_for_dir:
            s["directory"] = rel_dir
            s["has_local_agents_md"] = has_local_agents_md
            stacks.append(s)

    # Empty repo or unknown check
    if not stacks and not files:
        warnings.append("Empty repository detected.")
    elif not stacks:
        warnings.append("No supported primary technology stack recognized from signature files.")

    return {
        "root": str(root.resolve()),
        "is_monorepo": is_monorepo,
        "packages": packages,
        "stacks": stacks,
        "secondary_tooling": secondary_tooling,
        "warnings": warnings
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic technology stack detector")
    parser.add_argument("--root", default=".", help="Root path to scan (default: current directory)")
    parser.add_argument("--max-depth", type=int, default=4, help="Maximum directory depth (default: 4)")
    args = parser.parse_args()

    root_path = Path(args.root)
    if not root_path.exists() or not root_path.is_dir():
        sys.stderr.write(f"Error: Invalid directory '{args.root}'\n")
        return 1

    report = scan_target(root_path, args.max_depth)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
