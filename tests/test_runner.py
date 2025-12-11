import unittest
import os
import sys

# Add the addon root to the Python path
addon_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if addon_root not in sys.path:
    sys.path.append(addon_root)

def run_tests():
    """
    Discovers and runs all tests within the 'tests' directory.
    """
    # Discover all tests in the 'tests' directory
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=os.path.dirname(__file__), pattern='test_*.py')

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with a non-zero status code if any tests failed
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
