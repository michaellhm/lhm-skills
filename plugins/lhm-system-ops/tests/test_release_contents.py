import importlib.util
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]


def load_script(name):
    path = PLUGIN / 'scripts' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_plugin_fixture_rejects_generated_python_bytecode(tmp_path):
    fixture = tmp_path / 'plugin-fixture'
    generated = fixture / 'assets' / '__pycache__' / 'adapter.cpython-314.pyc'
    generated.parent.mkdir(parents=True)
    generated.write_bytes(b'generated-bytecode-fixture')

    validator = load_script('validate_system_ops')
    release_builder = load_script('build_release')

    assert validator.generated_bytecode_paths(fixture) == [
        Path('assets/__pycache__'),
        Path('assets/__pycache__/adapter.cpython-314.pyc'),
    ]
    assert release_builder.generated_bytecode_paths(fixture) == [
        Path('assets/__pycache__'),
        Path('assets/__pycache__/adapter.cpython-314.pyc'),
    ]


def test_plugin_tree_has_no_generated_python_bytecode():
    validator = load_script('validate_system_ops')
    assert validator.generated_bytecode_paths(PLUGIN) == []


def test_release_builder_excludes_generated_cache_paths(tmp_path):
    builder = load_script('build_release')
    normal = tmp_path / 'asset.txt'; normal.write_text('ok')
    cache = tmp_path / '.pytest_cache' / 'nodeids'; cache.parent.mkdir(); cache.write_text('volatile')
    bytecode = tmp_path / '__pycache__' / 'asset.pyc'; bytecode.parent.mkdir(); bytecode.write_bytes(b'volatile')
    assert builder.releasable(normal)
    assert not builder.releasable(cache)
    assert not builder.releasable(bytecode)
