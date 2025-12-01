#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 Verification Script
Verifies that all Phase 1 components are properly set up.
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple

# Enable UTF-8 output on Windows
if sys.platform == 'win32':
    os.system('chcp 65001 > nul 2>&1')

# Simple checkmarks for cross-platform compatibility
CHECK = '[OK]'
CROSS = '[X]'
ARROW = '>>>'


def check_file_exists(filepath: Path, description: str) -> bool:
    """Check if a file exists."""
    if filepath.exists():
        print(f"{CHECK} {description}: {filepath.name}")
        return True
    else:
        print(f"{CROSS} {description}: {filepath.name} NOT FOUND")
        return False


def check_directory_exists(dirpath: Path, description: str) -> bool:
    """Check if a directory exists."""
    if dirpath.exists() and dirpath.is_dir():
        print(f"{CHECK} {description}: {dirpath.name}/")
        return True
    else:
        print(f"{CROSS} {description}: {dirpath.name}/ NOT FOUND")
        return False


def main():
    """Run verification checks."""
    print("=" * 60)
    print("EventGraph - Phase 1 Verification")
    print("=" * 60)
    print()

    project_root = Path(__file__).parent
    checks: List[Tuple[bool, str]] = []

    # Check core files
    print("\nCore Project Files:")
    checks.append((check_file_exists(project_root / "README.md", "README"), "Core Files"))
    checks.append((check_file_exists(project_root / "ROADMAP.md", "Roadmap"), "Core Files"))
    checks.append((check_file_exists(project_root / "SDD.md", "Design Doc"), "Core Files"))
    checks.append((check_file_exists(project_root / ".gitignore", "Git ignore"), "Core Files"))
    print()

    # Check Docker files
    print("\nDocker Infrastructure:")
    checks.append((check_file_exists(project_root / "docker-compose.yml", "Docker Compose"), "Docker"))
    checks.append((check_file_exists(project_root / "Dockerfile", "Dockerfile"), "Docker"))

    # Check Python files
    print("\nPython Configuration:")
    checks.append((check_file_exists(project_root / "requirements.txt", "Requirements"), "Python"))
    checks.append((check_file_exists(project_root / "requirements-dev.txt", "Dev Requirements"), "Python"))
    checks.append((check_file_exists(project_root / "pyproject.toml", "Project Config"), "Python"))
    checks.append((check_file_exists(project_root / "pytest.ini", "Pytest Config"), "Python"))

    # Check configuration
    print("\nConfiguration Files:")
    checks.append((check_file_exists(project_root / ".env.example", "Env Template"), "Config"))
    checks.append((check_file_exists(project_root / "config" / "settings.py", "Settings Module"), "Config"))
    checks.append((check_file_exists(project_root / "config" / "logging_config.py", "Logging Config"), "Config"))

    # Check source directories
    print("\nSource Code Structure:")
    checks.append((check_directory_exists(project_root / "src", "Source directory"), "Structure"))
    checks.append((check_directory_exists(project_root / "src" / "models", "Models package"), "Structure"))
    checks.append((check_directory_exists(project_root / "src" / "scrapers", "Scrapers package"), "Structure"))
    checks.append((check_directory_exists(project_root / "src" / "ai", "AI package"), "Structure"))
    checks.append((check_directory_exists(project_root / "src" / "database", "Database package"), "Structure"))
    checks.append((check_directory_exists(project_root / "src" / "utils", "Utils package"), "Structure"))

    # Check database module
    print("\nDatabase Module:")
    checks.append((check_file_exists(project_root / "src" / "database" / "connection.py", "Connection module"), "Database"))
    checks.append((check_file_exists(project_root / "src" / "main.py", "Main entry point"), "Database"))

    # Check test structure
    print("\nTesting Infrastructure:")
    checks.append((check_directory_exists(project_root / "tests", "Tests directory"), "Testing"))
    checks.append((check_directory_exists(project_root / "tests" / "unit", "Unit tests"), "Testing"))
    checks.append((check_directory_exists(project_root / "tests" / "integration", "Integration tests"), "Testing"))
    checks.append((check_file_exists(project_root / "tests" / "conftest.py", "Test fixtures"), "Testing"))
    checks.append((check_file_exists(project_root / "tests" / "unit" / "test_connection.py", "Connection tests"), "Testing"))
    checks.append((check_file_exists(project_root / "tests" / "unit" / "test_settings.py", "Settings tests"), "Testing"))

    # Check automation
    print("\nAutomation & Tools:")
    checks.append((check_file_exists(project_root / "Makefile", "Makefile"), "Automation"))
    checks.append((check_file_exists(project_root / "setup.sh", "Setup script (Unix)"), "Automation"))
    checks.append((check_file_exists(project_root / "setup.bat", "Setup script (Windows)"), "Automation"))
    checks.append((check_file_exists(project_root / ".github" / "workflows" / "ci.yml", "CI/CD pipeline"), "Automation"))

    # Check documentation
    print("\nDocumentation:")
    checks.append((check_directory_exists(project_root / "docs", "Docs directory"), "Documentation"))
    checks.append((check_file_exists(project_root / "docs" / "PHASE1_COMPLETION.md", "Phase 1 report"), "Documentation"))

    # Summary
    print("\n" + "=" * 60)
    total_checks = len(checks)
    passed_checks = sum(1 for check, _ in checks if check)
    failed_checks = total_checks - passed_checks

    print("Verification Summary:")
    print(f"  Total Checks: {total_checks}")
    print(f"  Passed: {passed_checks}")
    print(f"  Failed: {failed_checks}")
    print()

    if failed_checks == 0:
        print("[SUCCESS] Phase 1 verification PASSED!")
        print("All infrastructure components are in place.")
        print()
        print("Next steps:")
        print("1. Run setup script: ./setup.sh (Unix) or setup.bat (Windows)")
        print("2. Edit .env file with your API keys")
        print("3. Start Docker: docker-compose up -d")
        print("4. Run tests: pytest")
        print("5. Start application: python src/main.py")
        return 0
    else:
        print("[FAILED] Phase 1 verification FAILED!")
        print("Some components are missing. Please check above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
