"""Render actual firmware discovery/state output in Jinja's immutable sandbox."""

import argparse
import json
from pathlib import Path
import sys
import unittest

from jinja2 import make_logging_undefined
from jinja2.sandbox import ImmutableSandboxedEnvironment


class UpdateTemplates(unittest.TestCase):
    wire = None

    def setUp(self):
        self.environment = ImmutableSandboxedEnvironment(undefined=make_logging_undefined())
        self.environment.filters["to_json"] = json.dumps
        self.discovery = self.wire["discovery"]

    def render(self, template, state):
        return self.environment.from_string(template).render(value_json=state)

    def test_original_attribute_lookup_reproduces_the_failure(self):
        with self.assertRaises(TypeError):
            self.render("{{ value_json.update | to_json }}", self.wire["states"][0])

    def test_update_template_renders_the_actual_update_object(self):
        for state in self.wire["states"]:
            with self.subTest(status=state["details"]["status"]):
                rendered = self.render(self.discovery["value_template"], state)
                self.assertEqual(json.loads(rendered), state["update"])

    def test_attributes_template_renders_the_actual_details(self):
        for state in self.wire["states"]:
            rendered = self.render(self.discovery["json_attributes_template"], state)
            self.assertEqual(json.loads(rendered), state["details"])

    def test_availability_tracks_verified_feed_state(self):
        template = self.discovery["availability"][1]["value_template"]
        for state in self.wire["states"]:
            self.assertEqual(self.render(template, state), "online" if state["details"]["checked"] else "offline")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixture", type=Path)
    args = parser.parse_args()
    UpdateTemplates.wire = json.loads(args.fixture.read_text(encoding="utf-8"))
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(UpdateTemplates))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
