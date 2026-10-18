"""Cleanup refusal boundaries; no native APIs or live editor access."""
from pathlib import Path
import tempfile
import unittest
from v4kicad.safety import write_json,ToolError
from v4kicad.scratch_cleanup import evidence
from v4kicad.j7_migration import PRODUCTION


class ScratchCleanupTests(unittest.TestCase):
    def test_never_archives_production(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            write_json(root/'j7-migration-context.json',dict(target=str(PRODUCTION.resolve()),production=True,identity_only=False))
            write_json(root/'validation-disposition.json',{})
            with self.assertRaisesRegex(ToolError,'isolated agent scratch'):evidence(root)

    def test_native_assertion_or_IPC_stop_never_gets_cleanup_exception(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            write_json(root/'j7-migration-context.json',dict(target=str(root/'scratch.kicad_pcb'),production=False,identity_only=False))
            write_json(root/'validation-disposition.json',dict(classification='FALSE_POSITIVE_RUNTIME_PARENT_LINKS_ONLY',no_native_assertion_or_IPC_failure=True))
            write_json(root/'STOP.json',dict(error='Native assertion/IPC failure; worker stopped'))
            with self.assertRaisesRegex(ToolError,'No cleanup of native assertion/IPC failure'):evidence(root)


if __name__=='__main__':unittest.main()
