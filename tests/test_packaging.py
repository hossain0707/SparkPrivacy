import json
from pathlib import Path
from sparkprivacy.paths import frontend_dir


def test_all_frontend_files_available():
    assert all((frontend_dir()/n).is_file() for n in ('index.html','app.js','styles.css','mark.svg'))


def test_entrypoint_self_test():
    from desktop_launcher import self_test
    assert self_test()['ok']


def test_readme_and_ci_have_matching_distribution_names():
    root=Path(__file__).resolve().parents[1]
    workflow=(root/'.github/workflows/ci.yml').read_text()
    expected=('SparkPrivacy-Setup-Windows-x64.exe','SparkPrivacy-macOS-Apple-Silicon-unsigned.dmg',
              'SparkPrivacy-macOS-Intel-unsigned.dmg','SparkPrivacy-Linux-Ubuntu-x64.deb')
    assert all(filename in workflow for filename in expected)


def test_no_external_frontend_scripts():
    assert 'https://' not in (frontend_dir()/'index.html').read_text(encoding='utf-8')


def test_consoleless_windows_launch_regression(tmp_path, monkeypatch):
    """PyInstaller --windowed sets both streams to None on Windows.

    Prior to the fix uvicorn.logging.DefaultFormatter tried to call
    sys.stdout.isatty(), raising an AttributeError at launch.
    """
    import sys
    from desktop_launcher import startup_self_test, make_uvicorn_config
    from sparkprivacy.server import create_app

    with monkeypatch.context() as m:
        m.setattr(sys, "stdout", None)
        m.setattr(sys, "stderr", None)
        cfg = make_uvicorn_config(create_app(data_dir=tmp_path), 17011)
        assert cfg.log_config is None
        result = startup_self_test()
    assert result == {"ok": True, "backend_ready": True, "frontend_ready": True, "consoleless_safe": True}


def test_desktop_startup_report_written_without_stdout(tmp_path, monkeypatch):
    import sys
    from desktop_launcher import main

    report = tmp_path / "start.json"
    with monkeypatch.context() as m:
        m.setattr(sys, "argv", ["desktop_launcher.py", "--startup-self-test", str(report)])
        m.setattr(sys, "stdout", None)
        m.setattr(sys, "stderr", None)
        import pytest
        with pytest.raises(SystemExit) as status:
            main()
    assert status.value.code == 0
    result = json.loads(report.read_text(encoding="utf-8"))
    assert result["ok"] and result["backend_ready"] and result["frontend_ready"]
