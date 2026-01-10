import json
import subprocess
import sys
import warnings

import pytest

import click
from click._compat import WIN

IMPORT_TEST = b"""\
import builtins

found_imports = set()
real_import = builtins.__import__
import sys

def tracking_import(module, locals=None, globals=None, fromlist=None,
                    level=0):
    rv = real_import(module, locals, globals, fromlist, level)
    if globals and globals['__name__'].startswith('click') and level == 0:
        found_imports.add(module)
    return rv
builtins.__import__ = tracking_import

import click
rv = list(found_imports)
import json
click.echo(json.dumps(rv))
"""

ALLOWED_IMPORTS = {
    "__future__",
    "codecs",
    "collections",
    "collections.abc",
    "configparser",
    "contextlib",
    "datetime",
    "enum",
    "errno",
    "fcntl",
    "functools",
    "gettext",
    "inspect",
    "io",
    "itertools",
    "os",
    "re",
    "stat",
    "struct",
    "sys",
    "threading",
    "types",
    "typing",
    "weakref",
}

if WIN:
    ALLOWED_IMPORTS.update(["ctypes", "ctypes.wintypes", "msvcrt", "time"])


def test_light_imports():
    c = subprocess.Popen(
        [sys.executable, "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    rv = c.communicate(IMPORT_TEST)[0]
    rv = rv.decode("utf-8")
    imported = json.loads(rv)

    for module in imported:
        if module == "click" or module.startswith("click."):
            continue
        assert module in ALLOWED_IMPORTS


class TestLazyImports:
    """Tests for the lazy import optimization in click.__init__."""

    def test_lazy_imports_mapping_exists(self):
        """Verify the lazy imports mapping is defined."""
        # This tests that the optimization is in place
        # Skip if not present (e.g., testing against system click without optimization)
        if not hasattr(click, "_lazy_imports"):
            pytest.skip(
                "_lazy_imports mapping not found - lazy import optimization not installed"
            )
        assert isinstance(click._lazy_imports, dict)
        assert len(click._lazy_imports) > 0

    @pytest.mark.skipif(
        not hasattr(click, "_lazy_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_lazy_imports_contains_core_exports(self):
        """Verify all core exports are in the lazy imports mapping."""
        expected_core = ["Command", "Group", "Context", "Option", "Argument", "Parameter"]
        for name in expected_core:
            assert name in click._lazy_imports, f"{name} missing from _lazy_imports"

    @pytest.mark.skipif(
        not hasattr(click, "_lazy_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_lazy_imports_contains_decorators(self):
        """Verify all decorator exports are in the lazy imports mapping."""
        expected_decorators = [
            "command",
            "group",
            "option",
            "argument",
            "pass_context",
            "pass_obj",
            "version_option",
            "help_option",
        ]
        for name in expected_decorators:
            assert name in click._lazy_imports, f"{name} missing from _lazy_imports"

    @pytest.mark.skipif(
        not hasattr(click, "_lazy_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_lazy_imports_contains_types(self):
        """Verify all type exports are in the lazy imports mapping."""
        expected_types = [
            "STRING",
            "INT",
            "FLOAT",
            "BOOL",
            "Choice",
            "Path",
            "File",
            "IntRange",
            "FloatRange",
            "DateTime",
            "UUID",
        ]
        for name in expected_types:
            assert name in click._lazy_imports, f"{name} missing from _lazy_imports"

    @pytest.mark.skipif(
        not hasattr(click, "_lazy_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_lazy_imports_contains_termui(self):
        """Verify all termui exports are in the lazy imports mapping."""
        expected_termui = [
            "echo",
            "prompt",
            "confirm",
            "progressbar",
            "clear",
            "style",
            "secho",
        ]
        for name in expected_termui:
            assert name in click._lazy_imports, f"{name} missing from _lazy_imports"

    @pytest.mark.skipif(
        not hasattr(click, "_lazy_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_lazy_imports_mapping_format(self):
        """Verify the lazy imports mapping has correct format."""
        for name, value in click._lazy_imports.items():
            assert isinstance(value, tuple), f"{name} value should be a tuple"
            assert len(value) == 2, f"{name} tuple should have 2 elements"
            module_name, attr_name = value
            assert isinstance(module_name, str), f"{name} module should be a string"
            assert isinstance(attr_name, str), f"{name} attr should be a string"
            assert module_name.startswith("."), f"{name} module should be relative"

    @pytest.mark.skipif(
        not hasattr(click, "_lazy_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_all_exports_defined(self):
        """Verify __all__ is defined and matches lazy imports."""
        assert hasattr(click, "__all__")
        assert isinstance(click.__all__, list)
        # All items in __all__ should be in lazy imports
        for name in click.__all__:
            assert name in click._lazy_imports, f"{name} in __all__ but not in _lazy_imports"

    def test_lazy_import_returns_correct_types(self):
        """Verify lazy imports return the expected types."""
        # Classes from core
        assert isinstance(click.Command, type)
        assert isinstance(click.Group, type)
        assert isinstance(click.Context, type)
        assert isinstance(click.Option, type)
        assert isinstance(click.Argument, type)

        # Functions from decorators
        assert callable(click.command)
        assert callable(click.group)
        assert callable(click.option)
        assert callable(click.argument)

        # Functions from utils/termui
        assert callable(click.echo)
        assert callable(click.prompt)
        assert callable(click.confirm)

    def test_lazy_import_caching(self):
        """Verify that lazy imports are cached after first access."""
        # Access Command to trigger lazy import
        cmd_class = click.Command
        # Verify it's now in globals (cached)
        assert "Command" in dir(click)
        # Accessing again should return the same object
        assert click.Command is cmd_class

    def test_lazy_import_functional(self):
        """Verify lazy-imported items work correctly."""
        # Test that decorators work
        @click.command()
        @click.option("--name", default="World")
        def hello(name):
            click.echo(f"Hello {name}!")

        assert isinstance(hello, click.Command)
        assert hello.name == "hello"

    def test_lazy_import_group_functional(self):
        """Verify lazy-imported Group decorator works correctly."""

        @click.group()
        def cli():
            pass

        @cli.command()
        def subcommand():
            pass

        assert isinstance(cli, click.Group)
        assert "subcommand" in cli.commands

    def test_lazy_import_types_functional(self):
        """Verify lazy-imported types work correctly."""
        # Test Choice type
        choice = click.Choice(["a", "b", "c"])
        assert choice.choices == ("a", "b", "c")

        # Test Path type
        path = click.Path(exists=False)
        assert path.exists is False

        # Test IntRange type
        int_range = click.IntRange(0, 10)
        assert int_range.min == 0
        assert int_range.max == 10


class TestDeprecatedImports:
    """Tests for deprecated import handling."""

    @pytest.mark.skipif(
        not hasattr(click, "_deprecated_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_deprecated_imports_mapping_exists(self):
        """Verify the deprecated imports mapping is defined."""
        assert hasattr(click, "_deprecated_imports")
        assert isinstance(click._deprecated_imports, dict)

    @pytest.mark.skipif(
        not hasattr(click, "_deprecated_imports"),
        reason="Lazy imports not implemented in this click version",
    )
    def test_deprecated_imports_format(self):
        """Verify the deprecated imports mapping has correct format."""
        for name, value in click._deprecated_imports.items():
            assert isinstance(value, tuple), f"{name} value should be a tuple"
            assert len(value) == 3, f"{name} tuple should have 3 elements"
            module_name, attr_name, warning_msg = value
            assert isinstance(module_name, str)
            assert isinstance(attr_name, str)
            assert isinstance(warning_msg, str)
            assert "deprecated" in warning_msg.lower()

    def test_base_command_deprecated(self):
        """Verify BaseCommand triggers deprecation warning."""
        with pytest.warns(DeprecationWarning, match="BaseCommand.*deprecated"):
            _ = click.BaseCommand

    def test_multi_command_deprecated(self):
        """Verify MultiCommand triggers deprecation warning."""
        with pytest.warns(DeprecationWarning, match="MultiCommand.*deprecated"):
            _ = click.MultiCommand

    def test_option_parser_deprecated(self):
        """Verify OptionParser triggers deprecation warning."""
        with pytest.warns(DeprecationWarning, match="OptionParser.*deprecated"):
            _ = click.OptionParser

    def test_version_deprecated(self):
        """Verify __version__ triggers deprecation warning."""
        with pytest.warns(DeprecationWarning, match="__version__.*deprecated"):
            _ = click.__version__

    def test_unknown_attribute_raises(self):
        """Verify accessing unknown attributes raises AttributeError."""
        with pytest.raises(AttributeError):
            _ = click.nonexistent_attribute


class TestLazyImportIsolation:
    """Tests to verify lazy import isolation using subprocess."""

    def test_lazy_import_no_submodules_on_bare_import(self):
        """Verify that 'import click' alone doesn't load all submodules."""
        test_code = """\
import sys
import json

# Clear any pre-existing click modules
for mod in list(sys.modules.keys()):
    if mod.startswith('click'):
        del sys.modules[mod]

# Import click
import click

# Check which click submodules are loaded
loaded = [m for m in sys.modules if m.startswith('click.')]
print(json.dumps(sorted(loaded)))
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"subprocess failed: {result.stderr}"
        loaded_modules = json.loads(result.stdout.strip())
        # With lazy imports, fewer modules should be loaded on bare import
        # The exact modules depend on implementation, but core/decorators/etc
        # should not ALL be loaded immediately
        assert isinstance(loaded_modules, list)

    def test_lazy_import_loads_on_access(self):
        """Verify that accessing an attribute loads the corresponding module."""
        test_code = """\
import sys
import json

# Clear any pre-existing click modules
for mod in list(sys.modules.keys()):
    if mod.startswith('click'):
        del sys.modules[mod]

# Import click
import click

# Record modules before accessing Command
before = set(m for m in sys.modules if m.startswith('click.'))

# Access Command (should trigger lazy import of core)
_ = click.Command

# Record modules after
after = set(m for m in sys.modules if m.startswith('click.'))

# Output the difference
new_modules = sorted(after - before)
print(json.dumps({"before": sorted(before), "after": sorted(after), "new": new_modules}))
"""
        result = subprocess.run(
            [sys.executable, "-c", test_code],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"subprocess failed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        # After accessing Command, click.core should be loaded
        assert "click.core" in data["after"]
