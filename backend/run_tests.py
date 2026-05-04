"""
Comprehensive test runner for Toán Socratic backend
"""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {command}\n")

    result = subprocess.run(
        command,
        shell=True,
        cwd=Path(__file__).parent,
        capture_output=True,
        text=True
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("STDERR:", result.stderr)

    success = result.returncode == 0
    print(f"\n{'✅ PASSED' if success else '❌ FAILED'}: {description}")
    return success


def main():
    """Run all tests"""
    print("🧪 Toán Socratic Backend - Comprehensive Test Suite")
    print("="*60)

    tests = [
        # Unit tests
        ("uv run pytest tests/test_models.py -v -m unit", "Unit Tests - Database Models"),
        ("uv run pytest tests/test_llm_client.py -v -m unit", "Unit Tests - LLM Client"),
        ("uv run pytest tests/test_socratic_engine.py -v", "Unit Tests - Socratic Engine"),

        # Integration tests
        ("uv run pytest tests/test_api.py -v -m integration", "Integration Tests - API Endpoints"),
        ("uv run pytest tests/test_llm_client.py -v -m integration", "Integration Tests - LLM Client"),

        # API tests
        ("uv run pytest tests/test_api.py -v -m api", "API Tests - All Endpoints"),

        # Full test suite
        ("uv run pytest tests/ -v --tb=short", "Full Test Suite"),
    ]

    results = []
    for command, description in tests:
        try:
            success = run_command(command, description)
            results.append((description, success))
        except Exception as e:
            print(f"❌ ERROR running {description}: {e}")
            results.append((description, False))

    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")

    print(f"\nTotal: {passed}/{total} test suites passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test suite(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())