"""End-to-end tests of reviewed multi-file guideline plans."""
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'apply_guidelines.py'


class ApplyPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'repo'
        self.root.mkdir()
        self.plan = self.root.parent / 'plan.json'

    def entry(self, path, content):
        target = self.root / path
        digest = hashlib.sha256(target.read_bytes()).hexdigest() if target.exists() else None
        return {'path': path, 'content': content, 'expected_sha256': digest}

    def run_plan(self, entries, *args):
        self.plan.write_text(json.dumps({'schema_version': 1, 'files': entries}))
        return subprocess.run([sys.executable, str(SCRIPT), '--root', str(self.root),
                               '--plan', str(self.plan), *args], capture_output=True, text=True, timeout=10)

    def test_preview_apply_refresh_check_remove_preserves_crlf(self):
        original = b'# Project\r\n\r\nKeep this sentence.  \r\n'
        agents = self.root / 'AGENTS.md'
        agents.write_bytes(original)
        entries = [self.entry('AGENTS-GUIDELINES-JS.md', '# JS\nScope: src/\nUse existing modules.'),
                   self.entry('AGENTS.md', 'Read `./AGENTS-GUIDELINES-JS.md` before editing src/.')]
        preview = self.run_plan(entries, '--dry-run')
        self.assertEqual(preview.returncode, 1, preview.stderr)
        self.assertEqual(agents.read_bytes(), original)
        self.assertFalse((self.root / 'AGENTS-GUIDELINES-JS.md').exists())
        applied = self.run_plan(entries)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        snapshot = {p.name: p.read_bytes() for p in self.root.iterdir()}
        fresh = [self.entry(e['path'], e['content']) for e in entries]
        self.assertEqual(self.run_plan(fresh, '--check').returncode, 0)
        self.assertEqual(self.run_plan(fresh).returncode, 0)
        self.assertEqual(snapshot, {p.name: p.read_bytes() for p in self.root.iterdir()})
        fresh[0]['content'] += '\nPropagate errors.'
        self.assertEqual(self.run_plan(fresh, '--check').returncode, 1)
        self.assertEqual(self.run_plan(fresh).returncode, 0)
        fresh = [self.entry(e['path'], e['content']) for e in fresh]
        removed = self.run_plan(fresh, '--remove')
        self.assertEqual(removed.returncode, 0, removed.stderr)
        self.assertEqual(agents.read_bytes(), original)
        self.assertEqual((self.root / 'AGENTS-GUIDELINES-JS.md').read_bytes(), b'')

    def test_preflight_rejects_late_conflict_without_partial_writes(self):
        (self.root / 'AGENTS.md').write_text('<!-- stack-guidelines:start --> broken')
        entries = [self.entry('AGENTS-GUIDELINES-JS.md', 'Rules'), self.entry('AGENTS.md', 'Links')]
        result = self.run_plan(entries)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertFalse((self.root / 'AGENTS-GUIDELINES-JS.md').exists())

    def test_stale_plan_does_not_overwrite_user_edit(self):
        entries = [self.entry('AGENTS.md', 'Rules')]
        (self.root / 'AGENTS.md').write_text('New human instructions')
        result = self.run_plan(entries)
        self.assertEqual(result.returncode, 2)
        self.assertEqual((self.root / 'AGENTS.md').read_text(), 'New human instructions')

    def test_hash_conflict_preserves_hand_edits(self):
        entries = [self.entry('AGENTS.md', 'Keep this rule')]
        self.assertEqual(self.run_plan(entries).returncode, 0)
        target = self.root / 'AGENTS.md'
        target.write_text(target.read_text().replace('Keep this rule', 'My human rule'))
        for mode in ((), ('--remove',)):
            with self.subTest(mode=mode):
                fresh = [self.entry('AGENTS.md', 'New rule')]
                self.assertEqual(self.run_plan(fresh, *mode).returncode, 2)
                self.assertIn('My human rule', target.read_text())

    def test_escape_symlinks_and_application_targets_rejected(self):
        outside = self.root.parent / 'AGENTS.md'
        outside.write_text('Outside instructions')
        (self.root / 'linked').symlink_to(self.root.parent, target_is_directory=True)
        for path in ('../AGENTS.md', 'linked/AGENTS.md', 'src/app.py', '.git/AGENTS.md'):
            with self.subTest(path=path):
                result = self.run_plan([{'path': path, 'content': 'bad', 'expected_sha256': None}])
                self.assertEqual(result.returncode, 2)
        self.assertEqual(outside.read_text(), 'Outside instructions')

    def test_unmanaged_guideline_collision_is_preserved(self):
        target = self.root / 'AGENTS-GUIDELINES-JS.md'
        target.write_text('Hand-authored guidance')
        result = self.run_plan([self.entry(target.name, 'Generated guidance')])
        self.assertEqual(result.returncode, 2)
        self.assertEqual(target.read_text(), 'Hand-authored guidance')

    def test_missing_link_target_rejected(self):
        result = self.run_plan([self.entry('AGENTS.md', 'Read `./AGENTS-GUIDELINES-GO.md`.')])
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / 'AGENTS.md').exists())

    def test_existing_human_parent_and_external_links_preserved(self):
        (self.root / 'pkg').mkdir()
        (self.root / 'AGENTS.md').write_text('Root instructions')
        original = '[root rules](../AGENTS.md)\n[upstream](https://example.com/AGENTS.md)\n'
        target = self.root / 'pkg/AGENTS.md'
        target.write_text(original)
        result = self.run_plan([self.entry('pkg/AGENTS.md', 'Scoped instructions')])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(target.read_text().startswith(original))

    def test_authored_parent_and_external_links_resolve(self):
        (self.root / 'pkg').mkdir()
        entries = [self.entry('pkg/AGENTS.md', 'Read [root](../AGENTS.md) and [docs](https://example.com/AGENTS.md).'),
                   self.entry('AGENTS.md', 'Root instructions')]
        result = self.run_plan(entries)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_duplicate_targets_rejected(self):
        item = self.entry('AGENTS.md', 'Rules')
        self.assertEqual(self.run_plan([item, item]).returncode, 2)


if __name__ == '__main__':
    unittest.main()
