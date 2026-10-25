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
