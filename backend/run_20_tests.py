import os
import sys
import time
import django
from unittest import TextTestResult, TextTestRunner

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test.utils import setup_test_environment, teardown_test_environment
from django.db import connection
from django.test.runner import DiscoverRunner
from habits.test_suite_20 import Application20Tests

class DetailedTestResult(TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.test_records = []
        self._test_start = 0

    def startTest(self, test):
        self._test_start = time.perf_counter()
        super().startTest(test)

    def addSuccess(self, test):
        elapsed = time.perf_counter() - self._test_start
        super().addSuccess(test)
        self.test_records.append({
            'name': test._testMethodName,
            'doc': test._testMethodDoc or '',
            'status': 'PASS',
            'duration': f"{elapsed:.3f}s",
            'error': None
        })

    def addFailure(self, test, err):
        elapsed = time.perf_counter() - self._test_start
        super().addFailure(test, err)
        self.test_records.append({
            'name': test._testMethodName,
            'doc': test._testMethodDoc or '',
            'status': 'FAIL',
            'duration': f"{elapsed:.3f}s",
            'error': str(err[1])
        })

    def addError(self, test, err):
        elapsed = time.perf_counter() - self._test_start
        super().addError(test, err)
        self.test_records.append({
            'name': test._testMethodName,
            'doc': test._testMethodDoc or '',
            'status': 'ERROR',
            'duration': f"{elapsed:.3f}s",
            'error': str(err[1])
        })

def run_tests():
    runner = DiscoverRunner(verbosity=0, interactive=False)
    runner.setup_test_environment()
    old_config = runner.setup_databases()

    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(Application20Tests)
    result = DetailedTestResult(sys.stdout, descriptions=True, verbosity=0)
    suite.run(result)

    runner.teardown_databases(old_config)
    runner.teardown_test_environment()

    print("\n" + "=" * 95)
    print("           HABIT TRACKER - 20 COMPREHENSIVE AUTOMATED TESTCASES EXECUTION REPORT")
    print("=" * 95)
    header = f"{'#':<4} {'Test ID':<8} {'Status':<8} {'Time':<8} {'Test Case Description'}"
    print(header)
    print("-" * 95)

    passed_count = 0
    failed_count = 0

    # Sort tests by method name so TC-01 to TC-20 display in order
    sorted_records = sorted(result.test_records, key=lambda x: x['name'])

    for idx, rec in enumerate(sorted_records, 1):
        test_id = rec['name'].split('_')[1].upper() if '_' in rec['name'] else f"TC-{idx:02d}"
        doc_summary = rec['doc'].split('\n')[0].strip() if rec['doc'] else rec['name']
        # Strip TC prefix from doc if present
        if ':' in doc_summary:
            doc_summary = doc_summary.split(':', 1)[1].strip()

        status_str = f"[{rec['status']}]"
        print(f"{idx:<4} {test_id:<8} {status_str:<8} {rec['duration']:<8} {doc_summary}")

        if rec['status'] == 'PASS':
            passed_count += 1
        else:
            failed_count += 1
            if rec['error']:
                print(f"     └─ Error: {rec['error']}")

    print("=" * 95)
    print(f"Total Tests Executed: {len(sorted_records)} | Passed: {passed_count} | Failed: {failed_count} | Pass Rate: {(passed_count/len(sorted_records)*100):.1f}%")
    print("=" * 95 + "\n")

    return passed_count, failed_count

if __name__ == '__main__':
    run_tests()
