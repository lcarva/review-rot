"""TODO: docstring goes here."""

import argparse
import datetime
import logging
import os
from os.path import dirname, join
import unittest
from unittest import mock, TestCase

from dateutil.relativedelta import relativedelta
from reviewrot import (
    get_arguments,
    load_config_file,
    parse_cli_args,
    ParseAge,
    remove_wip,
)
import yaml


# Disable logging to avoid messing up test output
logging.disable(logging.CRITICAL)


class CommandLineParserTest(TestCase):
    """
    CLI Arguments will have higher precedence over the config file.

    By default, CLI arguments has False value
    for boolean expressions. In such cases, if config file arguments
    has boolean 'True' value, then 'True' value will be considered.
    """

    @classmethod
    def setUpClass(cls):
        """TODO: docstring goes here."""
        filename = join(dirname(__file__), "yaml/test_command_line.yaml")
        with open(filename, "r") as f:
            cls.config = yaml.safe_load(f)

    @mock.patch("reviewrot.exists", return_value=True)
    def test_arg_cacert_from_config(self, mocked_exists):
        """Ensure that cacert value from config file is used in ssl_verify argument."""
        cli_args = argparse.Namespace(
            cacert=None,
            insecure=False,
        )

        config_args = {
            "arguments": {
                "cacert": "ca.crt",
            },
        }

        arguments = get_arguments(cli_args, config_args)

        self.assertEqual(arguments.get("ssl_verify"), "ca.crt")
        assert mocked_exists.called

    @mock.patch("reviewrot.exists", return_value=True)
    def test_arg_cacert_from_cli(self, mocked_exists):
        """Ensure that cacert value from cli is used in ssl_verify argument."""
        cli_args = argparse.Namespace(
            cacert="ca.crt",
            insecure=False,
        )

        config_args = {}

        arguments = get_arguments(cli_args, config_args)

        self.assertEqual(arguments.get("ssl_verify"), "ca.crt")
        assert mocked_exists.called

    def test_args_from_config_with_insecure(self):
        """TODO: docstring goes here."""
        cli_args = argparse.Namespace(
            cacert=None,
            debug=False,
            format=None,
            insecure=False,
            reverse=False,
            age=None,
            sort=None,
        )

        config = self.config["test1"]
        config_args = self.config["test1"]["arguments"]
        arguments = get_arguments(cli_args, config)
        # arguments must contains values from config arguments

        debug_result = arguments.get("debug") == config_args.get("debug")
        format_result = arguments.get("format") == config_args.get("format")
        ssl_result = arguments.get("ssl_verify") != config_args.get("insecure")
        reverse_result = arguments.get("reverse") == config_args.get("reverse")
        age_result = arguments.get("age") == config_args.get("age")
        sort_result = arguments.get("sort") == config_args.get("sort")

        self.assertTrue(
            debug_result
            and reverse_result
            and format_result
            and age_result
            and ssl_result
            and sort_result
        )

    def test_args_from_command_line(self):
        """TODO: docstring goes here."""
        cli_args = argparse.Namespace(
            cacert=None,
            debug=True,
            format="json",
            insecure=True,
            reverse=True,
            age=None,
            sort="updated",
            subject="Test notification (subject from args)",
        )

        config = self.config["test2"]
        arguments = get_arguments(cli_args, config)
        # arguments must contains values from cli arguments

        debug_result = arguments.get("debug") == vars(cli_args).get("debug")
        format_result = arguments.get("format") == vars(cli_args).get("format")
        ssl_result = arguments.get("ssl_verify") is False
        reverse_result = arguments.get("reverse") == vars(cli_args).get("reverse")
        age = arguments.get("age") is None
        sort_result = arguments.get("sort") == vars(cli_args).get("sort")
        subject_result = arguments.get("subject") == vars(cli_args).get("subject")

        self.assertTrue(
            debug_result
            and reverse_result
            and format_result
            and ssl_result
            and age
            and sort_result
            and subject_result
        )

    def test_args_from_command_line_except_format(self):
        """TODO: docstring goes here."""
        cli_args = argparse.Namespace(
            cacert=None,
            debug=True,
            format=None,
            insecure=False,
            reverse=True,
            age=None,
            sort=None,
        )

        config = self.config["test3"]
        config_args = self.config["test3"]["arguments"]
        arguments = get_arguments(cli_args, config)
        # All arguments must contains values from cli arguments except 'format'
        # It should be from config file

        debug_result = arguments.get("debug") is True
        format_result = arguments.get("format") == config_args.get("format")
        ssl_result = arguments.get("ssl_verify") is True
        reverse_result = arguments.get("reverse") is True
        age = arguments.get("age") is None
        sort_result = arguments.get("sort") is None

        self.assertTrue(
            debug_result
            and reverse_result
            and format_result
            and ssl_result
            and age
            and sort_result
        )

    def test_args_ca_certi_invalid_path_from_config(self):
        """TODO: docstring goes here."""
        cli_args = argparse.Namespace(
            cacert=None,
            debug=False,
            format=None,
            insecure=False,
            reverse=False,
            age=None,
        )

        config = self.config["test4"]
        with self.assertRaises(IOError) as context:
            get_arguments(cli_args, config)
            msg = "No certificate file found "
            self.assertTrue(msg in str(context.exception), msg=context.exception)

    def test_args_ca_certi_invalid_path_from_command_line(self):
        """TODO: docstring goes here."""
        cli_args = argparse.Namespace(
            cacert="~/review-rot/",
            debug=False,
            format=None,
            insecure=False,
            reverse=False,
            age=None,
        )

        config = self.config["test5"]
        with self.assertRaises(IOError) as context:
            get_arguments(cli_args, config)
            msg = "No certificate file found "
            self.assertTrue(msg in str(context.exception), msg=context.exception)

    def test_args_cacert_with_insecure(self):
        """TODO: docstring goes here."""
        cli_args = argparse.Namespace(
            cacert=None,
            debug=False,
            format=None,
            insecure=False,
            reverse=False,
            age=None,
        )
        config = self.config["test6"]
        with self.assertRaises(ValueError) as context:
            get_arguments(cli_args, config)
            msg = "Certificate file can't be used with insecure flag"
            self.assertTrue(msg in str(context.exception), msg=context.exception)

    @mock.patch("reviewrot.input", return_value="n")
    def test_load_config_file_re_write_no(self, mocked_input):
        """TODO: docstring goes here."""
        filename = join(dirname(__file__), "yaml/test_old_format.yaml")
        load_config_file(filename)
        # Load the old style config file and don't convert it to
        # new style dict format.
        with open(filename, "r") as f:
            new_config = yaml.safe_load(f)

        arguments_present = "arguments" not in new_config
        git_services_present = "type" in new_config[0]
        self.assertTrue(
            isinstance(new_config, list) and arguments_present and git_services_present
        )

    @mock.patch("reviewrot.input", return_value="y")
    def test_load_config_file_re_write_yes(self, mocked_input):
        """TODO: docstring goes here."""
        filename = join(dirname(__file__), "yaml/test_old_format.yaml")
        load_config_file(filename)
        # Load the old style config file and converts it to new style
        # dict format. Also creates backup file before converting.
        with open(filename, "r") as f:
            new_config = yaml.safe_load(f)

        backup_config_file_exist = os.path.exists(filename + ".backup")
        arguments_present = "arguments" in new_config
        git_services_present = "git_services" in new_config
        self.assertTrue(
            isinstance(new_config, dict)
            and arguments_present
            and git_services_present
            and backup_config_file_exist
        )

    def test_age_argument_in_command_line_valid(self):
        """TODO: docstring goes here."""
        now = datetime.datetime.now()
        expected_date = now - relativedelta(days=5, hours=4)

        args = parse_cli_args(["--age", "older", "5d", "4h"])

        self.assertEqual(args.age.state, "older")
        self.assertEqual(
            args.age.date.replace(second=0, microsecond=0),
            expected_date.replace(second=0, microsecond=0),
        )

    def test_age_argument_in_config(self):
        """TODO: docstring goes here."""
        now = datetime.datetime.now()
        expected_date = now - relativedelta(days=5, hours=4)

        cli_args = argparse.Namespace(cacert=None, insecure=False)
        config = {"arguments": {"age": "older 5d 4h"}}

        arguments = get_arguments(cli_args, config)
        self.assertEqual(arguments.get("age").state, "older")
        self.assertEqual(
            arguments.get("age").date.replace(second=0, microsecond=0),
            expected_date.replace(second=0, microsecond=0),
        )

    @classmethod
    def tearDownClass(cls):
        """TODO: docstring goes here."""
        backup_filename = join(dirname(__file__), "yaml/test_old_format.yaml.backup")
        filename = join(dirname(__file__), "yaml/test_old_format.yaml")
        if os.path.exists(backup_filename) and os.path.exists(filename):
            os.remove(filename)
            os.rename(backup_filename, filename)


class ParseAgeTest(unittest.TestCase):
    """TODO: docstring goes here."""

    def test_missing_state(self):
        """TODO: docstring goes here."""
        with self.assertRaises(ValueError) as context:
            ParseAge.parse(["5d", "4h"])
        self.assertTrue(
            "Wrong or missing state, only older/newer is allowed"
            in str(context.exception)
        )

    def test_missing_relative_age(self):
        """TODO: docstring goes here."""
        with self.assertRaises(ValueError) as context:
            ParseAge.parse(["newer"])
        self.assertTrue("Missing arguments" in str(context.exception))

    def test_wrong_state(self):
        """TODO: docstring goes here."""
        with self.assertRaises(ValueError) as context:
            ParseAge.parse(["oldnew", "5d", "4h"])
        self.assertTrue(
            "Wrong or missing state, only older/newer is allowed"
            in str(context.exception)
        )

    def test_invalid_unit(self):
        """TODO: docstring goes here."""
        with self.assertRaises(ValueError) as context:
            ParseAge.parse(["older", "5", "4x"])
        self.assertTrue("Invalid unit" in str(context.exception))


class IgnoreWIPTest(unittest.TestCase):
    """TODO: docstring goes here."""

    def test_remove_wip(self):
        """TODO: docstring goes here."""
        results = [
            FakeReview(title="WIP: add a functionality"),
            FakeReview(title="WIP:fix bug"),
            FakeReview(title="wip:fix bug #3"),
            FakeReview(title="wip: fix bug #4"),
            FakeReview(title="[WIP] refactor"),
            FakeReview(title="[WIP]refactor #2"),
            FakeReview(title="[wip]refactor #3"),
            FakeReview(title="[wip] refactor #4"),
            FakeReview(title="Draft: fix bug #3"),
            FakeReview(title="[WIPER] Add the possibility of ignoring WIP PRs/MRs"),
        ]
        updated_results = remove_wip(results)

        # check that results with WIP in the title are removed
        self.assertEqual(len(updated_results), 1)
        self.assertEqual(
            updated_results[0].title,
            "[WIPER] Add the possibility of ignoring WIP PRs/MRs",
        )


class FakeReview:
    """Mocks small part of BaseReview."""

    def __init__(self, title):
        """TODO: docstring goes here."""
        self.title = title


if __name__ == "__main__":
    unittest.main()
