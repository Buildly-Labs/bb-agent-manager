#!/usr/bin/env python3
"""
BB Agent Manager - Buildly Labs Integration Test Suite
Tests login, organization/product selection, task management, and AI prioritization

Usage:
    python scripts/test_buildly_integration.py [--username USER] [--password PASS] [--verbose]
    
Example:
    python scripts/test_buildly_integration.py --username glind --password mypass --verbose
"""

import asyncio
import json
import sys
from typing import Dict, Any, Optional
from pathlib import Path
import argparse
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bb_agent_manager.tools.buildly_auth import BuildlyLabsClient, get_buildly_client
from bb_agent_manager.config import AgentSettings


class BuldlyIntegrationTester:
    """Comprehensive Buildly Labs integration tester"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.client: Optional[BuildlyLabsClient] = None
        self.settings: Optional[AgentSettings] = None
        self.results: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "passed": 0,
                "failed": 0,
                "skipped": 0
            }
        }
    
    def _log(self, message: str, level: str = "INFO"):
        """Log message with level"""
        prefix = f"[{level}]"
        if level == "ERROR":
            prefix = f"\033[91m{prefix}\033[0m"  # Red
        elif level == "SUCCESS":
            prefix = f"\033[92m{prefix}\033[0m"  # Green
        elif level == "WARNING":
            prefix = f"\033[93m{prefix}\033[0m"  # Yellow
        
        if self.verbose or level in ["ERROR", "SUCCESS", "WARNING"]:
            print(f"{prefix} {message}")
    
    def _record_test(self, name: str, passed: bool, details: str = "", error: Optional[str] = None):
        """Record test result"""
        status = "PASSED" if passed else "FAILED"
        self.results["tests"].append({
            "name": name,
            "status": status,
            "details": details,
            "error": error
        })
        
        if passed:
            self.results["summary"]["passed"] += 1
            self._log(f"✓ {name}", "SUCCESS")
        else:
            self.results["summary"]["failed"] += 1
            self._log(f"✗ {name}", "ERROR")
            if error:
                self._log(f"  Error: {error}", "ERROR")
    
    async def test_connection(self) -> bool:
        """Test basic API connectivity"""
        self._log("Testing API connectivity...", "INFO")
        
        try:
            self.settings = AgentSettings()
            self.client = BuildlyLabsClient(
                base_url=self.settings.labs_base_url
            )
            self._record_test(
                "API Connectivity",
                True,
                f"Base URL: {self.settings.labs_base_url}"
            )
            return True
        except Exception as e:
            self._record_test(
                "API Connectivity",
                False,
                "Failed to initialize client",
                str(e)
            )
            return False
    
    async def test_authentication(self, username: str, password: str) -> bool:
        """Test user authentication"""
        self._log(f"Testing authentication for user: {username}", "INFO")
        
        try:
            if not self.client:
                self._log("Client not initialized", "ERROR")
                return False
            
            result = await self.client.login(username, password)
            
            if result.get("success"):
                user_info = result.get("user", {})
                self._record_test(
                    "User Authentication",
                    True,
                    f"User: {user_info.get('name', username)}, "
                    f"Email: {user_info.get('email', 'N/A')}"
                )
                self._log(f"  Authenticated as: {user_info.get('name')}", "INFO")
                return True
            else:
                error = result.get("error", "Unknown error")
                self._record_test(
                    "User Authentication",
                    False,
                    f"Authentication failed",
                    error
                )
                return False
        except Exception as e:
            self._record_test(
                "User Authentication",
                False,
                "Authentication test failed",
                str(e)
            )
            return False
    
    async def test_get_organizations(self) -> bool:
        """Test fetching organizations"""
        self._log("Testing organization retrieval...", "INFO")
        
        try:
            if not self.client or not self.client.token:
                self._log("Not authenticated", "ERROR")
                return False
            
            result = await self.client.get_organizations()
            
            if result.get("success"):
                orgs = result.get("organizations", [])
                org_names = [org.get("name") for org in orgs]
                
                self._record_test(
                    "Get Organizations",
                    True,
                    f"Found {len(orgs)} organization(s): {', '.join(org_names)}"
                )
                
                for org in orgs:
                    self._log(f"  • {org.get('name')} (ID: {org.get('id')})", "INFO")
                
                return len(orgs) > 0
            else:
                error = result.get("error", "Unknown error")
                self._record_test(
                    "Get Organizations",
                    False,
                    "Failed to retrieve organizations",
                    error
                )
                return False
        except Exception as e:
            self._record_test(
                "Get Organizations",
                False,
                "Organization retrieval failed",
                str(e)
            )
            return False
    
    async def test_select_organization(self, org_id: int) -> bool:
        """Test selecting an organization"""
        self._log(f"Testing organization selection (ID: {org_id})...", "INFO")
        
        try:
            result = await self.client.select_organization(org_id)
            
            if result.get("success"):
                org = result.get("organization", {})
                self._record_test(
                    "Select Organization",
                    True,
                    f"Selected: {org.get('name')} (ID: {org.get('id')})"
                )
                self._log(f"  Organization: {org.get('name')}", "INFO")
                return True
            else:
                error = result.get("error", "Unknown error")
                self._record_test(
                    "Select Organization",
                    False,
                    "Failed to select organization",
                    error
                )
                return False
        except Exception as e:
            self._record_test(
                "Select Organization",
                False,
                "Organization selection failed",
                str(e)
            )
            return False
    
    async def test_get_products(self, org_id: int) -> bool:
        """Test fetching products"""
        self._log(f"Testing product retrieval for organization {org_id}...", "INFO")
        
        try:
            result = await self.client.get_products(org_id)
            
            if result.get("success"):
                products = result.get("products", [])
                product_names = [p.get("name") for p in products]
                
                self._record_test(
                    "Get Products",
                    True,
                    f"Found {len(products)} product(s): {', '.join(product_names)}"
                )
                
                for product in products:
                    self._log(f"  • {product.get('name')} (ID: {product.get('id')})", "INFO")
                
                return len(products) > 0
            else:
                error = result.get("error", "Unknown error")
                self._record_test(
                    "Get Products",
                    False,
                    "Failed to retrieve products",
                    error
                )
                return False
        except Exception as e:
            self._record_test(
                "Get Products",
                False,
                "Product retrieval failed",
                str(e)
            )
            return False
    
    async def test_select_product(self, product_id: int) -> bool:
        """Test selecting a product"""
        self._log(f"Testing product selection (ID: {product_id})...", "INFO")
        
        try:
            result = await self.client.select_product(product_id)
            
            if result.get("success"):
                product = result.get("product", {})
                self._record_test(
                    "Select Product",
                    True,
                    f"Selected: {product.get('name')} (ID: {product.get('id')})"
                )
                self._log(f"  Product: {product.get('name')}", "INFO")
                return True
            else:
                error = result.get("error", "Unknown error")
                self._record_test(
                    "Select Product",
                    False,
                    "Failed to select product",
                    error
                )
                return False
        except Exception as e:
            self._record_test(
                "Select Product",
                False,
                "Product selection failed",
                str(e)
            )
            return False
    
    async def test_get_tasks(self, product_id: int, task_types: Optional[list] = None) -> bool:
        """Test fetching prioritized tasks"""
        self._log(f"Testing task retrieval for product {product_id}...", "INFO")
        
        try:
            result = await self.client.get_prioritized_tasks(product_id, task_types)
            
            if result.get("success"):
                tasks = result.get("tasks", {})
                total = result.get("total", 0)
                
                features_count = len(tasks.get("features", []))
                issues_count = len(tasks.get("issues", []))
                punchlist_count = len(tasks.get("punchlist", []))
                
                self._record_test(
                    "Get Prioritized Tasks",
                    True,
                    f"Found {total} tasks: "
                    f"{features_count} features, "
                    f"{issues_count} issues, "
                    f"{punchlist_count} punchlist items"
                )
                
                # Log tasks details
                if features_count > 0:
                    self._log(f"  Features ({features_count}):", "INFO")
                    for feature in tasks.get("features", [])[:3]:
                        self._log(f"    - {feature.get('title')} (Priority: {feature.get('priority')})", "INFO")
                
                if issues_count > 0:
                    self._log(f"  Issues ({issues_count}):", "INFO")
                    for issue in tasks.get("issues", [])[:3]:
                        self._log(f"    - {issue.get('title')} (Priority: {issue.get('priority')})", "INFO")
                
                if punchlist_count > 0:
                    self._log(f"  Punchlist ({punchlist_count}):", "INFO")
                    for item in tasks.get("punchlist", [])[:3]:
                        self._log(f"    - {item.get('title')} (Priority: {item.get('priority')})", "INFO")
                
                return total > 0
            else:
                error = result.get("error", "Unknown error")
                self._record_test(
                    "Get Prioritized Tasks",
                    False,
                    "Failed to retrieve tasks",
                    error
                )
                return False
        except Exception as e:
            self._record_test(
                "Get Prioritized Tasks",
                False,
                "Task retrieval failed",
                str(e)
            )
            return False
    
    async def test_save_and_load_session(self) -> bool:
        """Test session persistence"""
        self._log("Testing session persistence...", "INFO")
        
        try:
            # Session should already be saved from login
            result = await self.client.load_saved_session()
            
            if result.get("success"):
                user = result.get("user", {})
                org = result.get("organization", {})
                product = result.get("product", {})
                
                details = f"User: {user.get('name')}"
                if org:
                    details += f", Organization: {org.get('name')}"
                if product:
                    details += f", Product: {product.get('name')}"
                
                self._record_test(
                    "Session Persistence",
                    True,
                    details
                )
                return True
            else:
                self._record_test(
                    "Session Persistence",
                    False,
                    "No saved session found",
                    result.get("error")
                )
                return False
        except Exception as e:
            self._record_test(
                "Session Persistence",
                False,
                "Session loading failed",
                str(e)
            )
            return False
    
    async def run_full_test_suite(self, username: str, password: str):
        """Run complete integration test suite"""
        print("\n" + "="*70)
        print("BB AGENT MANAGER - BUILDLY LABS INTEGRATION TEST SUITE")
        print("="*70 + "\n")
        
        # 1. Test connectivity
        if not await self.test_connection():
            self._log("Cannot proceed without API connectivity", "ERROR")
            return
        
        print("\n" + "-"*70)
        print("AUTHENTICATION")
        print("-"*70 + "\n")
        
        # 2. Test authentication
        if not await self.test_authentication(username, password):
            self._log("Cannot proceed without authentication", "ERROR")
            return
        
        print("\n" + "-"*70)
        print("ORGANIZATION MANAGEMENT")
        print("-"*70 + "\n")
        
        # 3. Test organization retrieval
        if not await self.test_get_organizations():
            self._log("No organizations available", "WARNING")
            return
        
        # 4. Select first organization
        orgs = await self.client.get_organizations()
        if orgs.get("success") and orgs.get("organizations"):
            org_id = orgs["organizations"][0].get("id")
            
            if await self.test_select_organization(org_id):
                print("\n" + "-"*70)
                print("PRODUCT MANAGEMENT")
                print("-"*70 + "\n")
                
                # 5. Get products
                if await self.test_get_products(org_id):
                    # 6. Select first product
                    products = await self.client.get_products(org_id)
                    if products.get("success") and products.get("products"):
                        product_id = products["products"][0].get("id")
                        
                        if await self.test_select_product(product_id):
                            print("\n" + "-"*70)
                            print("TASK MANAGEMENT & PRIORITIZATION")
                            print("-"*70 + "\n")
                            
                            # 7. Get tasks
                            await self.test_get_tasks(product_id)
                            
                            # 8. Get only issues
                            print("\n" + "-"*70)
                            print("FILTERING BY TASK TYPE")
                            print("-"*70 + "\n")
                            await self.test_get_tasks(product_id, ["issue"])
        
        print("\n" + "-"*70)
        print("SESSION MANAGEMENT")
        print("-"*70 + "\n")
        
        # 9. Test session persistence
        await self.test_save_and_load_session()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Passed: {self.results['summary']['passed']}")
        print(f"Failed: {self.results['summary']['failed']}")
        print(f"Skipped: {self.results['summary']['skipped']}")
        print("="*70 + "\n")
        
        # Save results
        self._save_results()
    
    def _save_results(self):
        """Save test results to file"""
        results_file = Path(__file__).parent.parent / "test_results_buildly.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        self._log(f"Test results saved to: {results_file}", "INFO")


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Test Buildly Labs integration"
    )
    parser.add_argument("--username", help="Buildly Labs username")
    parser.add_argument("--password", help="Buildly Labs password")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    username = args.username or input("Enter Buildly Labs username: ")
    password = args.password or input("Enter Buildly Labs password: ")
    
    tester = BuldlyIntegrationTester(verbose=args.verbose)
    await tester.run_full_test_suite(username, password)


if __name__ == "__main__":
    asyncio.run(main())
