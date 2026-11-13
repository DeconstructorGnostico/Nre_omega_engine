import json

from nre.cli import main


def test_cli_commit(tmp_path, capsys):
    rc = main(["Explica", "qué", "es", "un", "invariante", "--runtime-dir", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0 and out["outcome"] == "COMMITTED"


def test_cli_authorize_flag(tmp_path, capsys):
    assert main(["Envía el reporte al cliente", "--runtime-dir", str(tmp_path / "a")]) == 2
    capsys.readouterr()
    assert main(["Envía el reporte al cliente", "--authorize", "--runtime-dir", str(tmp_path / "b")]) == 0
