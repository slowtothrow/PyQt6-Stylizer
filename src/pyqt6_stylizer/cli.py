from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .registry import PresetRegistry
from .reporting import DEFAULT_REPORT_PROMPT_PATH, write_repository_gui_evaluation_prompt


def resolve_run_callable():
    from .app import run

    return run


def build_parser() -> argparse.ArgumentParser:
    registry = PresetRegistry.default()
    parser = argparse.ArgumentParser(
        prog="pyqt6-stylizer",
        description="Launch the PyQt6 style exploration studio.",
    )
    parser.add_argument(
        "--preset",
        choices=[definition.preset_id for definition in registry.definitions()],
        help="Start the studio in a specific example preset.",
    )
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="Print the available example presets and exit.",
    )
    parser.add_argument(
        "--write-repository-gui-evaluation-prompt",
        nargs="?",
        const=DEFAULT_REPORT_PROMPT_PATH,
        metavar="PATH",
        help="Write a prompt.md template for anonymized PyQt6 repository interrogation and exit.",
    )
    parser.add_argument(
        "--report-repository-root",
        metavar="PATH",
        help="Optional repository root to embed in the generated evaluation prompt.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_presets:
        registry = PresetRegistry.default()
        for definition in registry.definitions():
            print(f"{definition.preset_id}: {definition.display_name}")
            print(f"  {definition.summary}")
        return 0

    if args.write_repository_gui_evaluation_prompt:
        output_path = write_repository_gui_evaluation_prompt(
            Path(args.write_repository_gui_evaluation_prompt),
            repository_root=args.report_repository_root,
        )
        print(f"Wrote repository GUI evaluation prompt to {output_path}")
        return 0

    run = resolve_run_callable()
    return run(startup_preset=args.preset)
