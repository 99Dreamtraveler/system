"""Regression tests for presentation IDs returned with similarity groups."""
import ast
import unittest
from pathlib import Path


def load_group_id_formatter():
    source_path = Path(__file__).parents[1] / "services" / "similarity.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    function = next(node for node in module.body if isinstance(node, ast.FunctionDef) and node.name == "format_group_id")
    namespace = {}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(source_path), "exec"), namespace)
    return namespace["format_group_id"]


class SimilarityGroupIdTests(unittest.TestCase):
    def test_group_ids_use_the_total_group_count_as_the_padding_width(self):
        format_group_id = load_group_id_formatter()

        self.assertEqual(format_group_id(1, 1), "1")
        self.assertEqual(format_group_id(9, 9), "9")
        self.assertEqual(format_group_id(1, 15), "01")
        self.assertEqual(format_group_id(15, 15), "15")
        self.assertEqual(format_group_id(1, 115), "001")
        self.assertEqual(format_group_id(115, 115), "115")


if __name__ == "__main__":
    unittest.main()
