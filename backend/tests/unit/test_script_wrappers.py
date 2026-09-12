"""Verify root maintenance launchers preserve canonical command behavior."""

from pathlib import Path
import runpy
import sys
from types import ModuleType
import unittest
from unittest.mock import Mock, patch


BACKEND_DIR = Path(__file__).resolve().parents[2]
WRAPPERS = (
    "check_data",
    "cleanup",
    "create_tables",
    "reset_dev_db",
    "seed_control_plane",
    "validate_control_plane",
)


class ScriptWrapperTests(unittest.TestCase):
    def test_each_wrapper_delegates_and_propagates_exit_code(self):
        for expected_exit_code, script_name in enumerate(WRAPPERS, start=10):
            with self.subTest(script=script_name):
                delegated_argv = []

                def canonical_entrypoint():
                    delegated_argv.extend(sys.argv)
                    return expected_exit_code

                canonical_main = Mock(side_effect=canonical_entrypoint)
                canonical_module = ModuleType(f"scripts.{script_name}")
                canonical_module.main = canonical_main
                scripts_package = ModuleType("scripts")
                scripts_package.__path__ = []
                setattr(scripts_package, script_name, canonical_module)
                argv = [f"{script_name}.py", "--sentinel", str(expected_exit_code)]

                with (
                    patch.dict(
                        sys.modules,
                        {
                            "scripts": scripts_package,
                            f"scripts.{script_name}": canonical_module,
                        },
                    ),
                    patch.object(sys, "argv", argv),
                    self.assertRaises(SystemExit) as context,
                ):
                    runpy.run_path(
                        str(BACKEND_DIR / f"{script_name}.py"),
                        run_name="__main__",
                    )

                self.assertEqual(context.exception.code, expected_exit_code)
                canonical_main.assert_called_once_with()
                self.assertEqual(Path(delegated_argv[0]).name, argv[0])
                self.assertEqual(delegated_argv[1:], argv[1:])


if __name__ == "__main__":
    unittest.main()
