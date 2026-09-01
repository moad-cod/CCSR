from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


PLUGIN_PATH = Path(__file__).parents[3] / "airflow" / "plugins" / "ragforge_control_plane.py"
SPEC = importlib.util.spec_from_file_location("ragforge_control_plane_test", PLUGIN_PATH)
assert SPEC and SPEC.loader
PLUGIN = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PLUGIN)


class AirflowControlPlaneCallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.context = {
            "dag_run": SimpleNamespace(
                conf={"ingestion_run_id": "run-id"},
                run_id="airflow-run-id",
            )
        }

    def test_dag_callback_without_exception_does_not_overwrite_task_failure(self):
        control_plane = Mock()

        with patch.object(PLUGIN, "RAGForgeControlPlane", return_value=control_plane):
            PLUGIN.mark_task_failure(self.context)

        control_plane.assert_not_called()

    def test_task_callback_persists_specific_exception(self):
        control_plane = Mock()
        self.context["exception"] = RuntimeError("embedding worker exceeded memory limit")

        with patch.object(PLUGIN, "RAGForgeControlPlane", return_value=control_plane):
            PLUGIN.mark_task_failure(self.context)

        control_plane.update_status.assert_called_once_with(
            "run-id",
            "failed",
            airflow_dag_run_id="airflow-run-id",
            error_message="embedding worker exceeded memory limit",
        )


if __name__ == "__main__":
    unittest.main()
