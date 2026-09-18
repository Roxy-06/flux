#!/usr/bin/env python3
"""
Amica Transformation Validation Test

This script validates that all PRD requirements have been implemented correctly.
"""

import os
import sys
import json
from pathlib import Path

def test_file_exists(path, description):
    """Test if a file exists and report result"""
    if Path(path).exists():
        print(f"? {description}: {path}")
        return True
    else:
        print(f"? {description}: {path} (MISSING)")
        return False

def test_file_contains(path, text, description):
    """Test if a file contains specific text"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            if text in content:
                print(f"? {description}")
                return True
            else:
                print(f"? {description} (TEXT NOT FOUND)")
                return False
    except FileNotFoundError:
        print(f"? {description} (FILE NOT FOUND)")
        return False

def main():
    print("?? AMICA TRANSFORMATION VALIDATION")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    # Test 1: Product rebranding
    total += 1
    if test_file_contains("README.md", "Amica", "Product renamed to Amica in README"):
        passed += 1
    
    total += 1 
    if test_file_contains("backend/main.py", "Amica", "Backend rebranded to Amica"):
        passed += 1
    
    total += 1
    if test_file_contains("frontend/package.json", "amica-frontend", "Frontend package renamed"):
        passed += 1
    
    # Test 2: CAPSULE system implementation
    total += 1
    if test_file_exists("backend/capsule/__init__.py", "CAPSULE system package"):
        passed += 1
    
    total += 1
    if test_file_exists("backend/capsule/models.py", "CAPSULE data models"):
        passed += 1
    
    total += 1 
    if test_file_exists("backend/capsule/generator.py", "CAPSULE generator"):
        passed += 1
    
    total += 1
    if test_file_exists("backend/capsule/mcp_server.py", "MCP server"):
        passed += 1
    
    # Test 3: API endpoints for CAPSULE
    total += 1
    if test_file_exists("backend/api/capsule.py", "CAPSULE API endpoints"):
        passed += 1
    
    total += 1
    if test_file_contains("backend/api/capsule.py", "get_capsule", "CAPSULE API has get_capsule"):
        passed += 1
    
    total += 1
    if test_file_contains("backend/api/capsule.py", "get_code", "CAPSULE API has get_code"):
        passed += 1
    
    # Test 4: Frontend enhancements
    total += 1
    if test_file_exists("frontend/app/components/VoiceInput.tsx", "Voice input component"):
        passed += 1
    
    total += 1
    if test_file_exists("frontend/app/components/DarkModeToggle.tsx", "Dark mode toggle"):
        passed += 1
    
    total += 1
    if test_file_exists("frontend/app/components/CapsuleManager.tsx", "CAPSULE manager component"):
        passed += 1
    
    # Test 5: Updated frontend API 
    total += 1
    if test_file_contains("frontend/app/lib/api.ts", "generateCapsule", "Frontend API has CAPSULE functions"):
        passed += 1
    
    total += 1
    if test_file_contains("frontend/app/lib/api.ts", "startMCPServer", "Frontend API has MCP functions"):
        passed += 1
    
    # Test 6: Removed agent handoff features
    total += 1
    if not Path("backend/api/agent.py").exists():
        print("? Agent handoff API removed")
        passed += 1
    else:
        print("? Agent handoff API still exists (should be removed)")
    
    total += 1
    if not test_file_contains("backend/main.py", "agent_router", "Agent router removed from main"):
        passed += 1
    
    # Test 7: Updated branding in frontend
    total += 1
    if test_file_contains("frontend/app/page.tsx", "AMICA", "Frontend shows AMICA branding"):
        passed += 1
    
    total += 1
    if test_file_contains("frontend/app/page.tsx", "context portability", "Frontend mentions context portability"):
        passed += 1
        
    total += 1
    if test_file_contains("frontend/app/page.tsx", "CAPSULE", "Frontend mentions CAPSULE system"):
        passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"?? VALIDATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("?? ALL TESTS PASSED - Amica transformation complete!")
        return 0
    else:
        print(f"??  {total - passed} tests failed - see details above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
