"""Behavioral regression checks for portable, non-destructive audit helpers."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('scanner', BASE / 'scripts/scan_repo.py')
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class HelpersTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()

    def run_helper(self, *args):
        return subprocess.run([sys.executable, str(BASE / 'scripts/init_audit_folder.py'),
                               '--root', str(self.root), *args],
                              cwd=self.temp.name, capture_output=True, text=True)

    def test_init_preserves_and_log_resolves_relative_to_root(self):
        self.assertEqual(self.run_helper('init', '--folder', 'docs/seo-audit-shop').returncode, 0)
        folder = self.root / 'docs/seo-audit-shop'
        (folder / 'AUDIT.md').write_text('Original evidence\n')
        old_log = (folder / 'WORKLOG.md').read_text()
        self.assertEqual(self.run_helper('init', '--folder', 'docs/seo-audit-shop').returncode, 0)
        self.assertEqual((folder / 'AUDIT.md').read_text(), 'Original evidence\n')
        result = self.run_helper('log', '--folder', 'docs/seo-audit-shop', '--title', 'Check',
                                 '--done', 'Rendered', '--remaining', 'None', '--blockers', 'None')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((folder / 'WORKLOG.md').read_text().startswith(old_log))

    def test_ambiguous_folders_do_not_restart_ids(self):
        for name in ['seo-audit-shop', 'seo-audit-blog']:
            folder = self.root / name
            folder.mkdir()
            (folder / 'WORKLOG.md').write_text('SEO-019')
        self.assertNotEqual(self.run_helper('next-id').returncode, 0)
        folder = self.root / 'seo-audit-shop/evidence'
        folder.mkdir()
        (folder / 'proposal.md').write_text('SEO-044')
        result = self.run_helper('next-id', '--folder', 'seo-audit-shop', '--count', '2')
        self.assertEqual(result.stdout.splitlines(), ['SEO-045', 'SEO-046'])
        self.assertNotEqual(self.run_helper('next-id', '--count', '0').returncode, 0)

    def test_destinations_cannot_escape_or_follow_symlinks(self):
        self.assertNotEqual(self.run_helper('init', '--folder', '../outside').returncode, 0)
        outside = Path(self.temp.name) / 'outside'
        self.assertFalse(outside.exists())
        outside.mkdir()
        (self.root / 'seo-audit-link').symlink_to(outside, target_is_directory=True)
        self.assertNotEqual(self.run_helper('init', '--folder', 'seo-audit-link').returncode, 0)
        self.assertEqual(list(outside.iterdir()), [])
        audit = self.root / 'seo-optimization-work'
        audit.mkdir()
        (audit / 'AUDIT.md').symlink_to(outside / 'private.md')
        self.assertNotEqual(self.run_helper('init').returncode, 0)

    def test_scanner_prunes_and_excludes_symlink_files(self):
        for directory in ['node_modules/vendor', 'docs/seo-audit-shop', 'app']:
            (self.root / directory).mkdir(parents=True)
            (self.root / directory / 'index.html').write_text('<html><head></head></html>')
        (self.root / 'docs/seo-audit-shop/AUDIT.md').write_text('prior evidence')
        external = Path(self.temp.name) / 'outside.html'
        external.write_text('<html><head></head></html>')
        (self.root / 'external.html').symlink_to(external)
        report = scanner.scan(self.root, 3)
        self.assertEqual(report['counts']['document_templates'], 1)
        self.assertTrue(all(s['file'] == 'app/index.html' for s in report['signals']))

    def test_scanner_reports_static_schema_and_leaves_dynamic_as_leads(self):
        (self.root / 'page.html').write_text('''<html><head><title>{{ title }}</title></head>
<script type="application/ld+json">{"@context":"https://schema.org",bad}</script>
<script type="application/ld+json">{{ schema }}</script></html>''')
        report = scanner.scan(self.root, 25)
        self.assertEqual(report['signal_totals']['jsonld-syntax-error'], 1)
        self.assertNotIn('duplicate-static-title', report['signal_totals'])

    def test_scanner_does_not_overwrite_output(self):
        destination = self.root / 'report.json'
        destination.write_text('keep')
        result = subprocess.run([sys.executable, str(BASE / 'scripts/scan_repo.py'), '--root',
                                 str(self.root), '--out', str(destination)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(destination.read_text(), 'keep')

    def test_normal_source_folder_with_task_notes_is_not_excluded(self):
        app = self.root / 'app'
        app.mkdir()
        (app / 'TASKS.md').write_text('General engineering tasks')
        (app / 'page.html').write_text('<html><head></head></html>')
        self.assertEqual(scanner.scan(self.root, 5)['counts']['document_templates'], 1)

    def test_typescript_metadata_is_inspected(self):
        (self.root / 'metadata.ts').write_text('export const metadata = { robots: { index: false } };')
        report = scanner.scan(self.root, 5)
        self.assertEqual(report['counts']['next_metadata_exports'], 1)
        self.assertEqual(report['signal_totals']['noindex-in-component'], 1)

    def test_scanner_inventory_includes_nested_packages(self):
        package = self.root / 'apps/store'
        package.mkdir(parents=True)
        (package / 'package.json').write_text(json.dumps({'dependencies': {'next': '15.0.0'}}))
        report = scanner.scan(self.root, 5)
        self.assertIn('apps/store/package.json', report['package_manifests'])
        self.assertIn('Next.js', scanner.scan(package, 5)['project']['frameworks'])


if __name__ == '__main__':
    unittest.main()
