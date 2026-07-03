import sys
import inspect
import importlib.util
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path("cvcp/reference/python/src").resolve()))

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

sys.modules['pytest'] = DummyPytest()

test_dir = Path("cvcp/reference/python/tests")
passed = 0
failed = 0

for test_file in test_dir.rglob("test_*.py"):
    spec = importlib.util.spec_from_file_location(test_file.stem, test_file)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    for name, obj in inspect.getmembers(mod):
        if inspect.isfunction(obj) and name.startswith("test_"):
            try:
                obj()
                passed += 1
            except Exception as e:
                print(f"FAIL: {name} in {test_file.name}")
                import traceback
                traceback.print_exc()
                failed += 1

print(f"====================")
print(f"{passed} passed")
print(f"{failed} failed")
print(f"0 skipped")
print(f"====================")
if failed > 0:
    sys.exit(1)
