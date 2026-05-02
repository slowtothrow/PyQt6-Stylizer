from __future__ import annotations

import unittest

from pyqt6_stylizer.document.schema import StudioDocument
from pyqt6_stylizer.models import ExperienceLevel


class StudioDocumentTests(unittest.TestCase):
    def test_example_round_trip_is_lossless(self) -> None:
        original = StudioDocument.example()
        restored = StudioDocument.from_json(original.to_json())

        self.assertEqual(restored.to_dict(), original.to_dict())

    def test_invalid_experience_level_falls_back_to_basic(self) -> None:
        restored = StudioDocument.from_dict({"experience_level": "expert-plus"})

        self.assertEqual(restored.experience_level, ExperienceLevel.BASIC.value)


class ExperienceLevelTests(unittest.TestCase):
    def test_progressive_levels_unlock_expected_groups(self) -> None:
        self.assertTrue(ExperienceLevel.INTERMEDIATE.supports(ExperienceLevel.BASIC))
        self.assertTrue(ExperienceLevel.ADVANCED.supports(ExperienceLevel.INTERMEDIATE))
        self.assertFalse(ExperienceLevel.BASIC.supports(ExperienceLevel.ADVANCED))


if __name__ == "__main__":
    unittest.main()
