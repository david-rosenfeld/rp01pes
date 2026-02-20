#!/usr/bin/env python3
"""Validation script for task_05_documentation."""

import sys
import py_compile
from pathlib import Path


def validate(workspace: Path) -> tuple[bool, list[str]]:
    """
    Validate task_05_documentation completion.

    Returns:
        Tuple of (success, list of error messages)
    """
    errors = []
    cache_file = workspace / "cache.py"

    # Check file exists
    if not cache_file.exists():
        return False, ["cache.py not found"]

    # Check syntax
    try:
        py_compile.compile(str(cache_file), doraise=True)
    except py_compile.PyCompileError as e:
        return False, [f"Syntax error: {e}"]

    # Import and check docstrings
    sys.path.insert(0, str(workspace))
    try:
        if 'cache' in sys.modules:
            del sys.modules['cache']

        import cache

        # Check module docstring
        if not cache.__doc__:
            errors.append("Module missing docstring")

        # Check class docstring
        if not cache.TTLCache.__doc__:
            errors.append("TTLCache class missing docstring")

        # Check method docstrings
        methods = ['get', 'set', 'delete', 'clear']
        for method_name in methods:
            method = getattr(cache.TTLCache, method_name, None)
            if method is None:
                errors.append(f"Method '{method_name}' not found")
            elif not method.__doc__:
                errors.append(f"Method '{method_name}' missing docstring")
            else:
                # Check for Google-style sections (Args, Returns) where applicable
                doc = method.__doc__
                if method_name in ['get', 'set', 'delete']:
                    if 'Args:' not in doc and 'args:' not in doc.lower():
                        errors.append(f"Method '{method_name}' docstring missing Args section")
                if method_name in ['get', 'delete']:
                    if 'Returns:' not in doc and 'returns:' not in doc.lower():
                        errors.append(f"Method '{method_name}' docstring missing Returns section")

        # Test that class still functions
        try:
            c = cache.TTLCache(default_ttl=1)
            c.set("test", "value")
            if c.get("test") != "value":
                errors.append("TTLCache.get() not working correctly")
            if not c.delete("test"):
                errors.append("TTLCache.delete() not working correctly")
            if c.get("test") is not None:
                errors.append("TTLCache.delete() didn't remove item")
            c.set("test2", "value2")
            c.clear()
            if c.get("test2") is not None:
                errors.append("TTLCache.clear() didn't clear cache")
        except Exception as e:
            errors.append(f"TTLCache functionality broken: {e}")

    except Exception as e:
        errors.append(f"Import error: {type(e).__name__}: {e}")
    finally:
        sys.path.remove(str(workspace))
        if 'cache' in sys.modules:
            del sys.modules['cache']

    return len(errors) == 0, errors


if __name__ == "__main__":
    workspace = Path.cwd()
    if len(sys.argv) > 1:
        workspace = Path(sys.argv[1])

    success, errors = validate(workspace)

    if success:
        print("PASS: All validation checks passed")
        sys.exit(0)
    else:
        print("FAIL: Validation errors:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
