"""
Click is a simple Python module inspired by the stdlib optparse to make
writing command line scripts fun. Unlike other modules, it's based
around a simple API that does not come with too much magic and is
composable.
"""

from __future__ import annotations

# Lazy import mappings: attribute name -> (module, name in module)
_lazy_imports: dict[str, tuple[str, str]] = {
    # core
    "Argument": (".core", "Argument"),
    "Command": (".core", "Command"),
    "CommandCollection": (".core", "CommandCollection"),
    "Context": (".core", "Context"),
    "Group": (".core", "Group"),
    "Option": (".core", "Option"),
    "Parameter": (".core", "Parameter"),
    # decorators
    "argument": (".decorators", "argument"),
    "command": (".decorators", "command"),
    "confirmation_option": (".decorators", "confirmation_option"),
    "group": (".decorators", "group"),
    "help_option": (".decorators", "help_option"),
    "make_pass_decorator": (".decorators", "make_pass_decorator"),
    "option": (".decorators", "option"),
    "pass_context": (".decorators", "pass_context"),
    "pass_obj": (".decorators", "pass_obj"),
    "password_option": (".decorators", "password_option"),
    "version_option": (".decorators", "version_option"),
    # exceptions
    "Abort": (".exceptions", "Abort"),
    "BadArgumentUsage": (".exceptions", "BadArgumentUsage"),
    "BadOptionUsage": (".exceptions", "BadOptionUsage"),
    "BadParameter": (".exceptions", "BadParameter"),
    "ClickException": (".exceptions", "ClickException"),
    "FileError": (".exceptions", "FileError"),
    "MissingParameter": (".exceptions", "MissingParameter"),
    "NoSuchOption": (".exceptions", "NoSuchOption"),
    "UsageError": (".exceptions", "UsageError"),
    # formatting
    "HelpFormatter": (".formatting", "HelpFormatter"),
    "wrap_text": (".formatting", "wrap_text"),
    # globals
    "get_current_context": (".globals", "get_current_context"),
    # termui
    "clear": (".termui", "clear"),
    "confirm": (".termui", "confirm"),
    "echo_via_pager": (".termui", "echo_via_pager"),
    "edit": (".termui", "edit"),
    "getchar": (".termui", "getchar"),
    "launch": (".termui", "launch"),
    "pause": (".termui", "pause"),
    "progressbar": (".termui", "progressbar"),
    "prompt": (".termui", "prompt"),
    "secho": (".termui", "secho"),
    "style": (".termui", "style"),
    "unstyle": (".termui", "unstyle"),
    # types
    "BOOL": (".types", "BOOL"),
    "Choice": (".types", "Choice"),
    "DateTime": (".types", "DateTime"),
    "File": (".types", "File"),
    "FLOAT": (".types", "FLOAT"),
    "FloatRange": (".types", "FloatRange"),
    "INT": (".types", "INT"),
    "IntRange": (".types", "IntRange"),
    "ParamType": (".types", "ParamType"),
    "Path": (".types", "Path"),
    "STRING": (".types", "STRING"),
    "Tuple": (".types", "Tuple"),
    "UNPROCESSED": (".types", "UNPROCESSED"),
    "UUID": (".types", "UUID"),
    # utils
    "echo": (".utils", "echo"),
    "format_filename": (".utils", "format_filename"),
    "get_app_dir": (".utils", "get_app_dir"),
    "get_binary_stream": (".utils", "get_binary_stream"),
    "get_text_stream": (".utils", "get_text_stream"),
    "open_file": (".utils", "open_file"),
}

# Deprecated imports with their replacements
_deprecated_imports: dict[str, tuple[str, str, str]] = {
    # name -> (module, actual_name, warning_message)
    "BaseCommand": (
        ".core",
        "_BaseCommand",
        "'BaseCommand' is deprecated and will be removed in Click 9.0. Use"
        " 'Command' instead.",
    ),
    "MultiCommand": (
        ".core",
        "_MultiCommand",
        "'MultiCommand' is deprecated and will be removed in Click 9.0. Use"
        " 'Group' instead.",
    ),
    "OptionParser": (
        ".parser",
        "_OptionParser",
        "'OptionParser' is deprecated and will be removed in Click 9.0. The"
        " old parser is available in 'optparse'.",
    ),
}

__all__ = [
    # core
    "Argument",
    "Command",
    "CommandCollection",
    "Context",
    "Group",
    "Option",
    "Parameter",
    # decorators
    "argument",
    "command",
    "confirmation_option",
    "group",
    "help_option",
    "make_pass_decorator",
    "option",
    "pass_context",
    "pass_obj",
    "password_option",
    "version_option",
    # exceptions
    "Abort",
    "BadArgumentUsage",
    "BadOptionUsage",
    "BadParameter",
    "ClickException",
    "FileError",
    "MissingParameter",
    "NoSuchOption",
    "UsageError",
    # formatting
    "HelpFormatter",
    "wrap_text",
    # globals
    "get_current_context",
    # termui
    "clear",
    "confirm",
    "echo_via_pager",
    "edit",
    "getchar",
    "launch",
    "pause",
    "progressbar",
    "prompt",
    "secho",
    "style",
    "unstyle",
    # types
    "BOOL",
    "Choice",
    "DateTime",
    "File",
    "FLOAT",
    "FloatRange",
    "INT",
    "IntRange",
    "ParamType",
    "Path",
    "STRING",
    "Tuple",
    "UNPROCESSED",
    "UUID",
    # utils
    "echo",
    "format_filename",
    "get_app_dir",
    "get_binary_stream",
    "get_text_stream",
    "open_file",
]


def __getattr__(name: str) -> object:
    # Handle lazy imports
    if name in _lazy_imports:
        module_name, attr_name = _lazy_imports[name]
        import importlib

        module = importlib.import_module(module_name, __package__)
        value = getattr(module, attr_name)
        # Cache the import in the module's globals for subsequent access
        globals()[name] = value
        return value

    # Handle deprecated imports
    if name in _deprecated_imports:
        import importlib
        import warnings

        module_name, attr_name, warning_msg = _deprecated_imports[name]
        warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
        module = importlib.import_module(module_name, __package__)
        return getattr(module, attr_name)

    # Handle __version__ specially
    if name == "__version__":
        import importlib.metadata
        import warnings

        warnings.warn(
            "The '__version__' attribute is deprecated and will be removed in"
            " Click 9.1. Use feature detection or"
            " 'importlib.metadata.version(\"click\")' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return importlib.metadata.version("click")

    raise AttributeError(name)
