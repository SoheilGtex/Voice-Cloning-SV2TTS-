from click.testing import CliRunner
from voice_cloner.cli import cli

def test_cli_help():
    r = CliRunner().invoke(cli, ["--help"])
    assert r.exit_code == 0
    assert "Voice Cloner CLI" in r.output
