import sys
import importlib.util
from pathlib import Path

# Add root to path so we can import cvcp.tck
sys.path.insert(0, str(Path(".").resolve()))

class DummyPytest:
    class ExceptionInfo:
        def __init__(self):
            self.value = None
    class raises:
        def __init__(self, exc_type, match=None):
            self.exc_type = exc_type
            self.match = match
            self.info = DummyPytest.ExceptionInfo()
        def __enter__(self):
            return self.info
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                raise AssertionError(f"Expected {self.exc_type.__name__} but nothing was raised")
            if not issubclass(exc_type, self.exc_type):
                return False
            if self.match and self.match not in str(exc_val):
                raise AssertionError(f"Pattern '{self.match}' not found in '{exc_val}'")
            self.info.value = exc_val
            return True

    @staticmethod
    def fixture(func):
        func._is_fixture = True
        return func

sys.modules['pytest'] = DummyPytest()

test_dir = Path("cvcp/tck/tests")
passed = 0
failed = 0

import shutil
import tempfile
import inspect

for test_file in test_dir.rglob("test_*.py"):
    spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    fixtures = {}
    for name, obj in vars(mod).items():
        if hasattr(obj, "_is_fixture"):
            fixtures[name] = obj

    for name, obj in vars(mod).items():
        if name.startswith("test_") and callable(obj):
            try:
                # Basic fixture resolution
                kwargs = {}
                sig = inspect.signature(obj)
                for param in sig.parameters:
                    if param == "tmp_path":
                        tmp = tempfile.mkdtemp()
                        kwargs[param] = Path(tmp)
                    elif param in fixtures:
                        fix_sig = inspect.signature(fixtures[param])
                        if "tmp_path" in fix_sig.parameters:
                            tmp = tempfile.mkdtemp()
                            kwargs[param] = fixtures[param](Path(tmp))
                        else:
                            kwargs[param] = fixtures[param]()
                
                obj(**kwargs)
                passed += 1
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"FAIL: {name} in {test_file.name}")
                failed += 1

print(f"{'='*20}")
print(f"{passed} passed")
print(f"{failed} failed")
print(f"0 skipped")
print(f"{'='*20}")

if failed > 0:
    sys.exit(1)
