#!/usr/bin/env python3
"""
Script to validate diagnostic rules JSON structure and regex patterns.

Usage:
    python validate_rules.py --file rules-refactored.json
    python validate_rules.py --file rules.json --verbose
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


class RulesValidator:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []

    def log(self, message: str, level: str = "info"):
        """Log message based on level."""
        if level == "error":
            self.errors.append(message)
            print(f"❌ ERROR: {message}")
        elif level == "warning":
            self.warnings.append(message)
            print(f"⚠️  WARNING: {message}")
        elif level == "success":
            self.successes.append(message)
            if self.verbose:
                print(f"✅ {message}")
        else:
            print(f"ℹ️  {message}")

    def validate_meta(self, meta: Dict[str, Any]) -> bool:
        """Validate meta section."""
        print("\n📋 Validating meta section...")
        required_fields = ["name", "version", "description"]
        
        for field in required_fields:
            if field not in meta:
                self.log(f"Meta missing field: {field}", "error")
                return False
            self.log(f"Meta field '{field}' present", "success")
        
        return True

    def validate_topic_keywords(self, topics: Dict[str, List[str]]) -> bool:
        """Validate topic keywords."""
        print("\n🔑 Validating topic keywords...")
        if not topics:
            self.log("No topic keywords defined", "warning")
            return True
        
        for topic, keywords in topics.items():
            if not isinstance(keywords, list):
                self.log(f"Topic '{topic}' keywords not a list", "error")
                return False
            if not keywords:
                self.log(f"Topic '{topic}' has empty keywords", "warning")
            self.log(f"Topic '{topic}' has {len(keywords)} keywords", "success")
        
        return True

    def test_regex_pattern(self, pattern: str, test_cases: List[str]) -> Tuple[bool, List[str]]:
        """Test regex pattern against test cases."""
        try:
            compiled = re.compile(pattern, re.MULTILINE | re.DOTALL)
            results = []
            
            for test in test_cases:
                match = compiled.search(test)
                results.append(f"  {'✅' if match else '❌'} {test[:60]}")
            
            return True, results
        except re.error as e:
            return False, [f"  ❌ Regex error: {e}"]

    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        """Validate a single diagnostic rule."""
        rule_id = rule.get("id", "UNKNOWN")
        print(f"\n  Validating rule: {rule_id}")
        
        # Check required fields
        required_fields = [
            "id", "severity", "category", "error_type",
            "why_it_happens", "fix_summary", "patterns", "fix_steps"
        ]
        
        for field in required_fields:
            if field not in rule:
                self.log(f"Rule {rule_id} missing field: {field}", "error")
                return False
        
        # Validate severity
        valid_severities = ["critical", "high", "medium", "low"]
        if rule.get("severity") not in valid_severities:
            self.log(
                f"Rule {rule_id} has invalid severity: {rule.get('severity')}",
                "error"
            )
            return False
        
        self.log(f"Rule {rule_id}: severity={rule['severity']}", "success")
        
        # Validate patterns
        patterns = rule.get("patterns", [])
        if not patterns:
            self.log(f"Rule {rule_id} has no patterns", "warning")
            return True
        
        for idx, pattern in enumerate(patterns, 1):
            if "regex" not in pattern:
                self.log(f"Rule {rule_id} pattern {idx} missing regex", "error")
                return False
            
            # Test regex
            regex_str = pattern["regex"]
            test_cases = pattern.get("test_cases", [])
            
            if not test_cases:
                self.log(
                    f"Rule {rule_id} pattern {idx} has no test cases",
                    "warning"
                )
            else:
                success, results = self.test_regex_pattern(regex_str, test_cases)
                
                if not success:
                    self.log(
                        f"Rule {rule_id} pattern {idx} regex error: {results[0]}",
                        "error"
                    )
                    return False
                
                print(f"    Pattern '{pattern.get('name', 'unnamed')}':")
                for result in results:
                    print(result)
        
        # Validate fix_steps
        fix_steps = rule.get("fix_steps", [])
        if not fix_steps:
            self.log(f"Rule {rule_id} has no fix steps", "warning")
        else:
            self.log(f"Rule {rule_id} has {len(fix_steps)} fix steps", "success")
        
        return True

    def validate_test_cases(self, test_cases: List[Dict[str, Any]]) -> bool:
        """Validate test cases section."""
        print("\n📝 Validating test cases...")
        if not test_cases:
            self.log("No test cases defined", "warning")
            return True
        
        for test_group in test_cases:
            problem_id = test_group.get("problem_id", "UNKNOWN")
            cases = test_group.get("cases", [])
            self.log(f"Problem '{problem_id}' has {len(cases)} test cases", "success")
        
        return True

    def validate_rules_file(self, file_path: Path) -> bool:
        """Validate entire rules JSON file."""
        print(f"🔍 Validating: {file_path}\n")
        
        # Load JSON
        try:
            with open(file_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.log(f"Invalid JSON: {e}", "error")
            return False
        except FileNotFoundError:
            self.log(f"File not found: {file_path}", "error")
            return False
        
        # Validate structure
        if not self.validate_meta(data.get("meta", {})):
            return False
        
        if not self.validate_topic_keywords(data.get("topic_keywords", {})):
            return False
        
        # Validate rules
        print("\n📋 Validating diagnostic rules...")
        rules = data.get("diagnostic_rules", [])
        if not rules:
            self.log("No diagnostic rules found", "error")
            return False
        
        self.log(f"Found {len(rules)} rules", "success")
        
        for rule in rules:
            if not self.validate_rule(rule):
                return False
        
        # Validate test cases
        if not self.validate_test_cases(data.get("test_cases", [])):
            return False
        
        return True

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n❌ Errors:")
            for error in self.errors:
                print(f"  - {error}")
        
        if self.warnings and self.verbose:
            print("\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        print("=" * 60)
        
        if self.errors:
            print("❌ VALIDATION FAILED")
            return False
        else:
            print("✅ VALIDATION PASSED")
            return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate diagnostic rules JSON structure and regex patterns"
    )
    parser.add_argument(
        "--file",
        type=Path,
        required=True,
        help="Path to rules JSON file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    
    args = parser.parse_args()
    
    validator = RulesValidator(verbose=args.verbose)
    success = validator.validate_rules_file(args.file)
    validator.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
