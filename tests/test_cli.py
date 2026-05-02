from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch

from pyqt6_stylizer.cli import build_parser, main


class CliTests(unittest.TestCase):
    def test_parser_accepts_preset_without_mode(self) -> None:
        parser = build_parser()

        args = parser.parse_args(["--preset", "showcase-playground"])

        self.assertEqual(args.preset, "showcase-playground")
        self.assertFalse(args.list_presets)

    def test_parser_accepts_report_prompt_flags(self) -> None:
        parser = build_parser()

        args = parser.parse_args(
            [
                "--write-repository-gui-evaluation-prompt",
                "prompt.md",
                "--report-repository-root",
                "/tmp/example",
            ]
        )

        self.assertEqual(args.write_repository_gui_evaluation_prompt, "prompt.md")
        self.assertEqual(args.report_repository_root, "/tmp/example")

    def test_list_presets_prints_available_examples(self) -> None:
        output = io.StringIO()

        with redirect_stdout(output):
            exit_code = main(["--list-presets"])

        rendered = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("showcase-playground: UI Showcase Playground", rendered)
        self.assertNotIn("plot-control-workbench", rendered)

    def test_main_writes_repository_gui_evaluation_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_path = Path(temp_dir) / "prompt.md"
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = main(
                    [
                        "--write-repository-gui-evaluation-prompt",
                        str(prompt_path),
                        "--report-repository-root",
                        "/tmp/repo-under-test",
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(prompt_path.exists())
            rendered = prompt_path.read_text(encoding="utf-8")
            self.assertIn("Repository GUI Evaluation Report Prompt", rendered)
            self.assertIn("/tmp/repo-under-test", rendered)
            self.assertIn("CaptainWidgetCastle", rendered)
            self.assertIn("PyQt6 Usage Breakdown", rendered)
            self.assertIn("Wrote repository GUI evaluation prompt", output.getvalue())

    def test_main_passes_startup_preset_to_run(self) -> None:
        run_stub = Mock(return_value=0)

        with patch("pyqt6_stylizer.cli.resolve_run_callable", return_value=run_stub):
            exit_code = main(["--preset", "showcase-playground"])

        self.assertEqual(exit_code, 0)
        run_stub.assert_called_once_with(startup_preset="showcase-playground")


if __name__ == "__main__":
    unittest.main()