#!/usr/bin/env python3
"""
run_tests.py - Comprehensive test suite for coding-guidelines-generator.

Validates:
1. detect_stack.py on 18 diverse repository architectures & fixtures.
2. upsert_section.py: first run, byte-identical second run, hand edits preservation,
   existing AGENTS.md, missing AGENTS.md, remove mode, dry-run mode.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
DETECT_SCRIPT = SCRIPTS_DIR / "detect_stack.py"
UPSERT_SCRIPT = SCRIPTS_DIR / "upsert_section.py"


def create_fixture(base_dir: Path, name: str, files: dict) -> Path:
    fdir = base_dir / name
    fdir.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        p = fdir / rel_path
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding="utf-8")
    return fdir


def run_detector(root_dir: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(DETECT_SCRIPT), "--root", str(root_dir)],
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(proc.stdout)


def test_detection_fixtures() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="stack_tests_"))
    try:
        # 1. Android Compose
        f_android_compose = create_fixture(temp_dir, "android_compose", {
            "build.gradle.kts": 'plugins { id("com.android.application") }\nandroid { composeOptions { kotlinCompilerExtensionVersion = "1.5.0" } }',
            "app/build.gradle.kts": 'dependencies { implementation("androidx.compose.ui:ui:1.6.0") }',
            "app/src/main/AndroidManifest.xml": '<manifest package="com.example.app"/>',
            "gradle/libs.versions.toml": '[versions]\nagp = "8.3.0"\n'
        })
        rep = run_detector(f_android_compose)
        assert len(rep["stacks"]) == 1, "Expected 1 stack for android_compose"
        assert rep["stacks"][0]["stack"] == "android"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-ANDROID.md"
        assert "Jetpack Compose" in rep["stacks"][0]["framework_addons"]

        # 2. Android XML
        f_android_xml = create_fixture(temp_dir, "android_xml", {
            "build.gradle": 'apply plugin: "com.android.application"\nandroid { compileSdkVersion 34 }',
            "src/main/AndroidManifest.xml": '<manifest package="com.example.xmlapp"/>',
            "src/main/res/layout/activity_main.xml": '<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"/>'
        })
        rep = run_detector(f_android_xml)
        assert rep["stacks"][0]["stack"] == "android"
        assert "XML Views" in rep["stacks"][0]["framework_addons"]

        # 3. Plain JS
        f_plain_js = create_fixture(temp_dir, "plain_js", {
            "package.json": json.dumps({"name": "plain-js", "type": "module", "scripts": {"test": "node --test"}})
        })
        rep = run_detector(f_plain_js)
        assert rep["stacks"][0]["stack"] == "javascript"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-JS.md"

        # 4. TypeScript
        f_ts = create_fixture(temp_dir, "ts", {
            "package.json": json.dumps({"name": "ts-lib", "scripts": {"build": "tsc"}}),
            "tsconfig.json": json.dumps({"compilerOptions": {"strict": True}})
        })
        rep = run_detector(f_ts)
        assert rep["stacks"][0]["stack"] == "typescript"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-JS.md"
        assert "references/typescript.md" in rep["stacks"][0]["reference_files"]

        # 5. React
        f_react = create_fixture(temp_dir, "react", {
            "package.json": json.dumps({"name": "my-react-app", "dependencies": {"react": "^18.3.1"}}),
            "tsconfig.json": "{}"
        })
        rep = run_detector(f_react)
        assert rep["stacks"][0]["stack"] == "react"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-REACT.md"

        # 6. Next.js App Router
        f_next_app = create_fixture(temp_dir, "nextjs_app", {
            "package.json": json.dumps({"name": "my-next-app", "dependencies": {"next": "15.0.0", "react": "19.0.0"}}),
            "app/page.tsx": "export default function Page() { return <h1>Home</h1>; }",
            "next.config.mjs": "export default {};"
        })
        rep = run_detector(f_next_app)
        assert rep["stacks"][0]["stack"] == "nextjs"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-NEXTJS.md"
        assert "App Router" in rep["stacks"][0]["framework_addons"]

        # 7. Next.js Pages Router
        f_next_pages = create_fixture(temp_dir, "nextjs_pages", {
            "package.json": json.dumps({"name": "pages-app", "dependencies": {"next": "14.2.0", "react": "18.2.0"}}),
            "pages/index.tsx": "export default function Index() { return null; }",
            "next.config.js": "module.exports = {};"
        })
        rep = run_detector(f_next_pages)
        assert rep["stacks"][0]["stack"] == "nextjs"
        assert "Pages Router" in rep["stacks"][0]["framework_addons"]

        # 8. Python Plain
        f_py_plain = create_fixture(temp_dir, "py_plain", {
            "pyproject.toml": '[project]\nname = "pkg"\nversion = "0.1.0"\n[tool.pytest.ini_options]\n'
        })
        rep = run_detector(f_py_plain)
        assert rep["stacks"][0]["stack"] == "python"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-PYTHON.md"

        # 9. Python Django
        f_py_django = create_fixture(temp_dir, "py_django", {
            "requirements.txt": "Django>=5.0\npsycopg2-binary>=2.9\n",
            "manage.py": "#!/usr/bin/env python"
        })
        rep = run_detector(f_py_django)
        assert "Django" in rep["stacks"][0]["framework_addons"]

        # 10. Python FastAPI
        f_py_fastapi = create_fixture(temp_dir, "py_fastapi", {
            "pyproject.toml": '[project]\ndependencies = ["fastapi>=0.110.0", "uvicorn>=0.28.0"]\n',
            "uv.lock": "# lockfile"
        })
        rep = run_detector(f_py_fastapi)
        assert "FastAPI" in rep["stacks"][0]["framework_addons"]
        assert rep["stacks"][0]["package_manager"] == "uv"

        # 11. PHP Plain
        f_php = create_fixture(temp_dir, "php_plain", {
            "composer.json": json.dumps({"require": {"php": "^8.2", "guzzlehttp/guzzle": "^7.8"}})
        })
        rep = run_detector(f_php)
        assert rep["stacks"][0]["stack"] == "php"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-PHP.md"

        # 12. WordPress Block Theme
        f_wp_block = create_fixture(temp_dir, "wp_block_theme", {
            "style.css": "/*\nTheme Name: Astra Block\nAuthor: WP Team\n*/\n",
            "theme.json": '{"version": 3}',
            "functions.php": "<?php // functions"
        })
        rep = run_detector(f_wp_block)
        assert rep["stacks"][0]["stack"] == "wordpress"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-WORDPRESS.md"
        assert any("Block Theme" in a for a in rep["stacks"][0]["framework_addons"])

        # 13. WordPress Classic Theme
        f_wp_classic = create_fixture(temp_dir, "wp_classic_theme", {
            "style.css": "/*\nTheme Name: Vintage Theme\n*/\nbody { color: black; }",
            "functions.php": "<?php // classic"
        })
        rep = run_detector(f_wp_classic)
        assert rep["stacks"][0]["stack"] == "wordpress"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-WORDPRESS.md"

        # 14. WordPress Plugin
        f_wp_plugin = create_fixture(temp_dir, "wp_plugin", {
            "my-plugin.php": "<?php\n/**\n * Plugin Name: Super Cache Pro\n */\n"
        })
        rep = run_detector(f_wp_plugin)
        assert rep["stacks"][0]["stack"] == "wordpress"
        assert any("plugin" in a.lower() for a in rep["stacks"][0]["framework_addons"])

        # 15. PHP/WordPress with Build Tooling package.json (Secondary Tooling Discrimination)
        f_wp_with_npm = create_fixture(temp_dir, "wp_npm_tooling", {
            "style.css": "/*\nTheme Name: Custom Theme\n*/\n",
            "package.json": json.dumps({
                "name": "theme-build",
                "devDependencies": {
                    "@wordpress/scripts": "^27.0.0",
                    "webpack": "^5.0.0",
                    "sass": "^1.0.0"
                }
            })
        })
        rep = run_detector(f_wp_with_npm)
        assert len(rep["stacks"]) == 1, "Expected only 1 primary stack"
        assert rep["stacks"][0]["stack"] == "wordpress"
        assert len(rep["secondary_tooling"]) == 1, "Expected package.json marked as secondary build tooling"
        assert rep["secondary_tooling"][0]["type"] == "build_tooling"

        # 16. Monorepo with per-package AGENTS.md
        f_mono_local = create_fixture(temp_dir, "mono_local", {
            "pnpm-workspace.yaml": "packages:\n  - 'packages/*'\n",
            "packages/web/package.json": json.dumps({"name": "web", "dependencies": {"next": "15.0.0", "react": "19.0.0"}}),
            "packages/web/AGENTS.md": "# Web Guidelines",
            "packages/api/pyproject.toml": '[project]\ndependencies = ["fastapi"]\n',
            "packages/api/AGENTS.md": "# API Guidelines"
        })
        rep = run_detector(f_mono_local)
        assert rep["is_monorepo"] is True
        web_stack = [s for s in rep["stacks"] if s["directory"] == "packages/web"][0]
        api_stack = [s for s in rep["stacks"] if s["directory"] == "packages/api"][0]
        assert web_stack["has_local_agents_md"] is True
        assert api_stack["has_local_agents_md"] is True

        # 17. Monorepo without per-package AGENTS.md
        f_mono_root = create_fixture(temp_dir, "mono_root", {
            "package.json": json.dumps({"name": "mono", "workspaces": ["apps/*"]}),
            "apps/frontend/package.json": json.dumps({"name": "frontend", "dependencies": {"react": "^18.0.0"}}),
            "apps/backend/composer.json": json.dumps({"require": {"php": "^8.2"}})
        })
        rep = run_detector(f_mono_root)
        assert rep["is_monorepo"] is True
        for s in rep["stacks"]:
            assert s["has_local_agents_md"] is False

        # 18. Empty repo
        f_empty = create_fixture(temp_dir, "empty_repo", {})
        rep = run_detector(f_empty)
        assert len(rep["stacks"]) == 0
        assert "Empty repository detected." in rep["warnings"]

        # 19. Repo with node_modules decoy (Ignored directories)
        f_decoy = create_fixture(temp_dir, "decoy_repo", {
            "node_modules/fake-next/package.json": json.dumps({"name": "fake", "dependencies": {"next": "15.0.0"}}),
            "Cargo.toml": '[package]\nname = "safe-rust"\nversion = "0.1.0"\n'
        })
        rep = run_detector(f_decoy)
        assert len(rep["stacks"]) == 1
        assert rep["stacks"][0]["stack"] == "rust"

        # 20. Java Backend (Maven)
        f_java = create_fixture(temp_dir, "java_backend", {
            "pom.xml": '<project xmlns="http://maven.apache.org/POM/4.0.0"><modelVersion>4.0.0</modelVersion><groupId>com.example</groupId><artifactId>demo</artifactId><version>1.0.0</version></project>',
            "src/main/java/com/example/App.java": "package com.example; public class App {}"
        })
        rep = run_detector(f_java)
        assert len(rep["stacks"]) == 1
        assert rep["stacks"][0]["stack"] == "java"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-JAVA.md"
        assert "Maven" in rep["stacks"][0]["framework_addons"]

        # 21. Shell Project
        f_shell = create_fixture(temp_dir, "shell_project", {
            ".shellcheckrc": "disable=SC2086\n",
            "scripts/deploy.sh": "#!/usr/bin/env bash\nset -euo pipefail\necho 'Deploying'\n",
            "scripts/build.sh": "#!/usr/bin/env bash\nset -euo pipefail\necho 'Building'\n"
        })
        rep = run_detector(f_shell)
        assert len(rep["stacks"]) == 1
        assert rep["stacks"][0]["stack"] == "shell"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-SHELL.md"

        # 22. Static HTML/CSS
        f_html = create_fixture(temp_dir, "static_html", {
            "index.html": "<!DOCTYPE html><html><head><title>App</title><link rel='stylesheet' href='styles.css'></head><body><h1>Hi</h1></body></html>",
            "styles.css": "body { margin: 0; }"
        })
        rep = run_detector(f_html)
        assert len(rep["stacks"]) == 1
        assert rep["stacks"][0]["stack"] == "html-css"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-HTML-CSS.md"

        # 23. Generic / Unknown Stack Fallback
        f_generic = create_fixture(temp_dir, "unknown_stack", {
            "dataset.csv": "col1,col2\n1,2\n",
            "notes.txt": "Project notes"
        })
        rep = run_detector(f_generic)
        assert len(rep["stacks"]) == 1
        assert rep["stacks"][0]["stack"] == "generic"
        assert rep["stacks"][0]["target_file"] == "AGENTS-GUIDELINES-GENERIC.md"
        assert "Read `./AGENTS-GUIDELINES-GENERIC.md`" in rep["dynamic_agents_section"]

        # 24. Python with requires-python = ">=3.8"
        f_py38 = create_fixture(temp_dir, "py_38", {
            "pyproject.toml": '[project]\nname = "legacy-compat"\nrequires-python = ">=3.8"\nversion = "0.1.0"\n'
        })
        rep = run_detector(f_py38)
        assert rep["stacks"][0]["stack"] == "python"
        assert "3.8" in rep["stacks"][0]["version"]

        # 25. Android nested app module deduplication
        f_android_nested = create_fixture(temp_dir, "android_nested", {
            "build.gradle": 'plugins { id "com.android.application" version "8.3.0" apply false }',
            "settings.gradle": 'include ":app"',
            "app/build.gradle": 'plugins { id "com.android.application" }',
            "app/src/main/AndroidManifest.xml": '<manifest package="com.example.nested"/>'
        })
        rep = run_detector(f_android_nested)
        android_stacks = [s for s in rep["stacks"] if s["stack"] == "android"]
        assert len(android_stacks) == 1, f"Expected exactly 1 Android stack, found {len(android_stacks)}"

        # 26. Distinct Android modules are retained even with identical metadata
        f_android_modules = create_fixture(temp_dir, "android_modules", {
            "settings.gradle": 'include ":app", ":library"',
            "app/build.gradle": 'plugins { id "com.android.application" }',
            "app/src/main/AndroidManifest.xml": '<manifest package="com.example.app"/>',
            "library/build.gradle": 'plugins { id "com.android.library" }',
            "library/src/main/AndroidManifest.xml": '<manifest package="com.example.library"/>'
        })
        rep = run_detector(f_android_modules)
        android_dirs = {s["directory"] for s in rep["stacks"] if s["stack"] == "android"}
        assert android_dirs == {"app", "library"}, f"Unexpected Android module directories: {android_dirs}"

        # 27. Standalone JavaScript source without package.json
        f_standalone_js = create_fixture(temp_dir, "standalone_js", {
            "main.mjs": "console.log('hello');\n"
        })
        rep = run_detector(f_standalone_js)
        assert rep["stacks"][0]["stack"] == "javascript"

        # 28. Kotlin-only Gradle backend
        f_kotlin = create_fixture(temp_dir, "kotlin_backend", {
            "build.gradle.kts": "plugins { kotlin(\"jvm\") version \"2.0.0\" }\n",
            "src/main/kotlin/App.kt": "fun main() = println(\"ok\")\n"
        })
        rep = run_detector(f_kotlin)
        assert rep["stacks"][0]["stack"] == "java"
        assert rep["stacks"][0]["version"] == "Kotlin (Gradle)"

        # 29. Workspace package below the second directory level
        f_deep_workspace = create_fixture(temp_dir, "deep_workspace", {
            "pnpm-workspace.yaml": "packages:\n  - 'apps/*/*'\n",
            "apps/team/web/package.json": json.dumps({"name": "web", "dependencies": {"react": "19.0.0"}}),
            "apps/team/web/AGENTS.md": "# Web Guidelines"
        })
        rep = run_detector(f_deep_workspace)
        assert any(s["directory"] == "apps/team/web" for s in rep["stacks"])

        # 30. Static HTML remains visible alongside shell deployment helpers
        f_html_shell = create_fixture(temp_dir, "html_shell", {
            "index.html": "<!DOCTYPE html><html><body><h1>Hi</h1></body></html>",
            ".shellcheckrc": "disable=SC2086\n",
            "deploy.sh": "#!/usr/bin/env bash\necho deploy\n",
            "build.sh": "#!/usr/bin/env bash\necho build\n"
        })
        rep = run_detector(f_html_shell)
        stacks = {s["stack"] for s in rep["stacks"]}
        assert {"shell", "html-css"}.issubset(stacks)

        # 26. Dynamic AGENTS.md links only include detected stacks
        rep_py = run_detector(f_py_plain)
        assert "AGENTS-GUIDELINES-PYTHON.md" in rep_py["dynamic_agents_section"]
        assert "AGENTS-GUIDELINES-JS.md" not in rep_py["dynamic_agents_section"]
        assert "AGENTS-GUIDELINES-ANDROID.md" not in rep_py["dynamic_agents_section"]

        print("✓ All 31 stack detection fixture tests passed successfully!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_upsert_script() -> None:
    temp_dir = Path(tempfile.mkdtemp(prefix="upsert_tests_"))
    try:
        test_file = temp_dir / "AGENTS.md"
        content_1 = "Line 1: Read ./AGENTS-GUIDELINES-JS.md"
        content_2 = "Line 1: Read ./AGENTS-GUIDELINES-JS.md\nLine 2: Read ./AGENTS-GUIDELINES-REACT.md"

        # 1. Missing AGENTS.md -> created
        proc = subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(test_file),
            "--content", content_1,
            "--header-meta", "skill=1.0.0", "verified=2026-10-18",
            "--hash"
        ], capture_output=True, text=True, check=True)

        assert test_file.exists()
        raw_1 = test_file.read_text(encoding="utf-8")
        assert "<!-- stack-guidelines:start skill=1.0.0 verified=2026-10-18 hash=" in raw_1
        assert "<!-- stack-guidelines:end -->" in raw_1
        assert content_1 in raw_1

        # 2. Second run with same content -> byte identical (idempotent)
        proc = subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(test_file),
            "--content", content_1,
            "--header-meta", "skill=1.0.0", "verified=2026-10-18",
            "--hash"
        ], capture_output=True, text=True, check=True)
        raw_2 = test_file.read_text(encoding="utf-8")
        assert raw_1 == raw_2, "Expected byte-identical idempotency on second run"

        # 3. Dry-run mode
        proc_dry_same = subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(test_file),
            "--content", content_1,
            "--header-meta", "skill=1.0.0", "verified=2026-10-18",
            "--hash",
            "--dry-run"
        ], capture_output=True, text=True)
        assert proc_dry_same.returncode == 0
        assert "Up to date" in proc_dry_same.stdout

        proc_dry_diff = subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(test_file),
            "--content", content_2,
            "--header-meta", "skill=1.0.0", "verified=2026-10-18",
            "--hash",
            "--dry-run"
        ], capture_output=True, text=True)
        assert proc_dry_diff.returncode == 1, "Dry run with differences must exit with code 1"
        assert "+Line 2: Read ./AGENTS-GUIDELINES-REACT.md" in proc_dry_diff.stdout

        # 4. Existing file with user content outside markers -> user content preserved
        user_header = "# My Custom Project Header\n\nCustom user instructions.\n\n"
        user_footer = "\n\n## Custom User Footer\nMore human notes."
        test_file.write_text(f"{user_header}{raw_1}{user_footer}", encoding="utf-8")

        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(test_file),
            "--content", content_2,
            "--header-meta", "skill=1.1.0", "verified=2026-10-18",
            "--hash"
        ], capture_output=True, text=True, check=True)

        updated_with_user = test_file.read_text(encoding="utf-8")
        assert updated_with_user.startswith(user_header), "User header must be preserved exactly"
        assert updated_with_user.endswith(user_footer), "User footer must be preserved exactly"
        assert "skill=1.1.0" in updated_with_user
        assert content_2 in updated_with_user

        # 5. Remove mode
        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(test_file),
            "--remove"
        ], capture_output=True, text=True, check=True)

        removed_content = test_file.read_text(encoding="utf-8")
        assert "stack-guidelines:start" not in removed_content
        assert "stack-guidelines:end" not in removed_content
        assert "# My Custom Project Header" in removed_content
        assert "Custom User Footer" in removed_content

        # 6. Template placeholder substitution (--substitute)
        sub_file = temp_dir / "SUBST.md"
        raw_template = "Run build with `{pm}` and deploy to `{env}`."
        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(sub_file),
            "--content", raw_template,
            "--substitute", "pm=pnpm", "env=production"
        ], capture_output=True, text=True, check=True)
        sub_result = sub_file.read_text(encoding="utf-8")
        assert "Run build with `pnpm` and deploy to `production`." in sub_result
        assert "{pm}" not in sub_result

        # 7. Byte-for-byte user content preservation with edge whitespace
        byte_file = temp_dir / "BYTE_PRESERVE.md"
        # Content with deliberate trailing spaces, trailing double newlines, etc.
        original_user_content = "   Line with leading spaces\nTrailing space line   \n\n\n"
        byte_file.write_text(original_user_content, encoding="utf-8")

        # Insert section at bottom
        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(byte_file),
            "--content", "Managed block content",
            "--position", "bottom"
        ], capture_output=True, text=True, check=True)

        # Remove section
        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(byte_file),
            "--remove"
        ], capture_output=True, text=True, check=True)

        restored_user_content = byte_file.read_text(encoding="utf-8")
        assert restored_user_content == original_user_content, (
            f"Expected byte-for-byte preservation.\nExpected: {repr(original_user_content)}\nActual:   {repr(restored_user_content)}"
        )

        # 8. CRLF bytes outside managed markers remain unchanged
        crlf_file = temp_dir / "CRLF_PRESERVE.md"
        original_crlf = b"User line 1\r\nUser line 2\r\n"
        crlf_file.write_bytes(original_crlf)
        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(crlf_file),
            "--content", "Managed CRLF block"
        ], capture_output=True, text=True, check=True)
        subprocess.run([
            sys.executable, str(UPSERT_SCRIPT),
            "--file", str(crlf_file),
            "--remove"
        ], capture_output=True, text=True, check=True)
        assert crlf_file.read_bytes() == original_crlf

        print("✓ All upsert_section.py lifecycle, substitution, and byte-preservation tests passed successfully!")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> int:
    print("Running coding-guidelines-generator test suite...")
    test_detection_fixtures()
    test_upsert_script()
    print("\nALL TEST SUITES PASSED.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
