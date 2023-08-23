import os
import sys
from unittest import mock

import pytest
import click
from click.testing import CliRunner
from utilities_common.general import load_module_from_source

from .mock_tables import dbconnector

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
scripts_path = os.path.join(modules_path, 'scripts')
sys.path.insert(0, modules_path)

sys.modules['sonic_platform'] = mock.MagicMock()

# Load the file under test
interruptshow_path = os.path.join(scripts_path, 'interruptshow')
interruptshow = load_module_from_source('interruptshow', interruptshow_path)

# Replace swsscommon objects with mocked objects
interruptshow.SonicV2Connector = dbconnector.SonicV2Connector


class TestInterruptshow(object):
    def test_show(self, capsys):
        runner = CliRunner()
        result = runner.invoke(interruptshow.cli.commands["show"])
        click.echo(result.output)
        expected = """\
Usage: show [OPTIONS] COMMAND [ARGS]...

  Display dpu info

Options:
  --help  Show this message and exit.

Commands:
  interrupt  Show platform dpu interrupt
"""
        assert result.output == expected

    def test_show_interrupt_all(self, capsys):
        runner = CliRunner()
        result = runner.invoke(interruptshow.cli.commands["show"].commands["interrupt"], args=["-t", "all"])
        click.echo(result.output)
        expected = """\
Timestamp          Name           Count  Severity     Description
-----------------  -----------  -------  -----------  -----------------
20220807 13:25:31  interrupt_1        4  LEVEL_INFO   Info interrupt-1
20220807 13:34:11  interrupt_2        3  LEVEL_INFO   Info interrupt-2
20220807 13:37:07  interrupt_3        2  LEVEL_ERROR  Error interrupt-1
20220807 13:45:49  interrupt_4        1  LEVEL_FATAL  Fatal interrupt-1

"""
        assert result.output == expected

    def test_show_interrupt_fatal(self, capsys):
        runner = CliRunner()
        result = runner.invoke(interruptshow.cli.commands["show"].commands["interrupt"], args=["-t", "fatal"])
        click.echo(result.output)
        expected = """\
Timestamp          Name           Count  Severity     Description
-----------------  -----------  -------  -----------  -----------------
20220807 13:45:49  interrupt_4        1  LEVEL_FATAL  Fatal interrupt-1

"""
        assert result.output == expected

    def test_show_interrupt_error(self, capsys):
        runner = CliRunner()
        result = runner.invoke(interruptshow.cli.commands["show"].commands["interrupt"], args=["-t", "error"])
        click.echo(result.output)
        expected = """\
Timestamp          Name           Count  Severity     Description
-----------------  -----------  -------  -----------  -----------------
20220807 13:37:07  interrupt_3        2  LEVEL_ERROR  Error interrupt-1

"""
        assert result.output == expected

    def test_show_interrupt_wrong_itype(self, capsys):
        runner = CliRunner()
        result = runner.invoke(interruptshow.cli.commands["show"].commands["interrupt"], args=["-t", "wrong"])
        click.echo(result.output)
        expected = """\
Usage: interrupt [OPTIONS]

Error: Invalid value for "--itype" / "-t": 'wrong' is not an acceptable greeting. Please choose from: fatal, hwrma, error, all
"""
        assert result.output == expected

    def test_show_interrupt_not_available(self, capsys):
        runner = CliRunner()
        result = runner.invoke(interruptshow.cli.commands["show"].commands["interrupt"], args=["-t", "hwrma"])
        click.echo(result.output)
        expected = """\
No interrupt data available

"""
        assert result.output == expected