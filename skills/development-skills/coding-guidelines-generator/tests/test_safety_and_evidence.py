"""Behavioral regressions for detection evidence and managed-file safety."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from detect_stack import scan_target, is_safe_path
from upsert_section import apply_upsert, apply_substitutions


class RepositoryCase(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding='utf-8')
        return target

    def package(self, path='package.json', **values):
        return self.write(path, json.dumps(values))

    def stacks(self):
        return scan_target(self.root)['stacks']


class DetectionEvidenceTests(RepositoryCase):
    def test_missing_scripts_are_unknown(self):
        self.package(dependencies={'next': '14.2.0', 'react': '18.2.0'})
        stack = self.stacks()[0]
        for key in ('build_command', 'test_command', 'lint_command'):
            self.assertIsNone(stack[key], key)

    def test_typescript_is_in_generated_react_and_next_layers(self):
        for framework in ('react', 'next'):
            with self.subTest(framework=framework):
                self.package(dependencies={framework: '1.0', 'typescript': '5.5'})
                stack = self.stacks()[0]
                references = [ref for item in stack['guideline_files_to_generate']
                              for ref in item.get('references', [item['reference']])]
                self.assertIn('references/typescript.md', references)

    def test_single_nested_package_is_scanned(self):
        self.package('apps/web/package.json', dependencies={'react': '18.2.0'})
        self.assertTrue(any(s['directory'] == 'apps/web' for s in self.stacks()))

    def test_workspace_manager_inheritance_and_local_owner(self):
        self.package(packageManager='pnpm@9.15.0', workspaces=['packages/*'])
        self.package('packages/web/package.json', dependencies={'react': '18.2.0'})
        self.write('packages/web/AGENTS.md', 'Use existing accessibility primitives.\n')
        stack = next(s for s in self.stacks() if s['directory'] == 'packages/web')
        self.assertEqual(stack['package_manager'], 'pnpm')
        self.assertEqual(stack['guidelines_directory'], 'packages/web')
        section = scan_target(self.root)['dynamic_agents_section']
        self.assertNotIn('`./AGENTS-GUIDELINES-REACT.md`', section)

    def test_mixed_next_routers(self):
        self.package(dependencies={'next': '14.2.0'})
        self.write('app/page.tsx', 'export default function Page() {}')
        self.write('pages/index.tsx', 'export default function Home() {}')
        self.assertIn('Pages Router', self.stacks()[0]['framework_addons'])

    def test_python_tools_and_version_not_invented(self):
        self.write('main.py', 'print("hi")\n')
        stack = self.stacks()[0]
        self.assertIsNone(stack['test_command'])
        self.assertIsNone(stack['lint_command'])
        self.assertIn('unknown', stack['version'].lower())

    def test_php_does_not_call_install_a_build(self):
        self.write('index.php', '<?php echo "hi";')
        stack = self.stacks()[0]
        self.assertIsNone(stack['build_command'])
        self.assertIsNone(stack['test_command'])
        self.assertIn('unknown', stack['version'].lower())

    def test_non_object_and_malformed_manifests_do_not_crash(self):
        for data in ('[]', 'null', '{broken', '{"dependencies": null, "scripts": []}'):
            with self.subTest(data=data):
                self.write('package.json', data)
                report = scan_target(self.root)
                self.assertTrue(report['warnings'])

    def test_sibling_prefix_is_not_contained(self):
        sibling = self.root.parent / (self.root.name + '-outside') / 'package.json'
        self.assertFalse(is_safe_path(self.root, sibling))

    def test_symlinked_manifests_are_not_read(self):
        outside = self.root / 'outside.json'
        outside.write_text('{"dependencies":{"next":"15.0"}}')
        (self.root / 'package.json').symlink_to(outside)
        report = scan_target(self.root)
        self.assertFalse(any(s['stack'] == 'nextjs' for s in report['stacks']))
        self.assertTrue(report['warnings'])

    def test_package_typescript_sources_and_intermediate_owner(self):
        self.package(workspaces=['packages/*'])
        self.write('packages/AGENTS.md', 'Shared package instructions')
        self.package('packages/web/package.json', dependencies={'react': '18.2.0'})
        self.write('packages/web/src/App.tsx', 'export const App = () => null;')
        stack = next(s for s in self.stacks() if s['directory'] == 'packages/web')
        self.assertIn('typescript', stack['layer_chain'])
        self.assertEqual(stack['guidelines_directory'], 'packages')

    def test_secondary_tooling_inherits_workspace_manager(self):
        self.package(packageManager='pnpm@9', workspaces=['packages/*'])
        self.write('packages/theme/style.css', '/* Theme Name: Example */')
        self.package('packages/theme/package.json', devDependencies={'@wordpress/scripts': '27'})
        report = scan_target(self.root)
        self.assertEqual(report['secondary_tooling'][0]['package_manager'], 'pnpm')

    def test_metadata_only_workspace_is_not_a_js_application(self):
        self.package(packageManager='pnpm@9')
        self.write('pnpm-workspace.yaml', "packages: ['packages/*']")
        self.package('packages/web/package.json', dependencies={'react': '18'})
        self.assertFalse(any(s['directory'] == '.' for s in self.stacks()))

    def test_invalid_depth_rejected(self):
        with self.assertRaises(ValueError):
            scan_target(self.root, -1)

    def test_deterministic_report(self):
        self.package(workspaces=['packages/*'])
        for name in ('z', 'a'):
            self.package(f'packages/{name}/package.json', dependencies={'react': '18'})
        report = scan_target(self.root)
        self.assertEqual(report, scan_target(self.root))
        self.assertEqual([s['directory'] for s in report['stacks']],
                         sorted(s['directory'] for s in report['stacks']))


class ManagedBlockTests(unittest.TestCase):
    def test_malformed_or_duplicate_markers_fail_closed(self):
        samples = [
            '<!-- stack-guidelines:start -->\nmanual text',
            '<!-- stack-guidelines:end -->',
            '<!-- stack-guidelines:end -->\n<!-- stack-guidelines:start -->',
            '<!-- stack-guidelines:start -->a<!-- stack-guidelines:end -->\n'
            '<!-- stack-guidelines:start -->b<!-- stack-guidelines:end -->',
        ]
        for content in samples:
            with self.subTest(content=content), self.assertRaises(ValueError):
                apply_upsert(content, 'new rules', 'stack-guidelines')

    def test_remove_preserves_every_unmanaged_byte(self):
        before = 'manual header\r\n\n'
        after = '\n\nmanual footer\r\n'
        original = before + '<!-- stack-guidelines:start -->\nmanaged\n<!-- stack-guidelines:end -->' + after
        self.assertEqual(apply_upsert(original, '', 'stack-guidelines', remove=True), before + after)

    def test_missing_package_manager_is_not_silently_npm(self):
        with self.assertRaises(ValueError):
            apply_substitutions('Run {pm} test', {})


if __name__ == '__main__':
    unittest.main()
