#!/usr/bin/env python3
"""
BB Agent Manager - System Verification & Health Check
Verifies that all components are working correctly

Usage:
    python verify_buildly_integration.py [--verbose]
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
import json

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bb_agent_manager.config import AgentSettings
from bb_agent_manager.tools.buildly_auth import get_buildly_client


class SystemVerifier:
    """Verify all system components"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.checks: List[Tuple[str, bool, str]] = []
    
    async def verify_all(self):
        """Run all verification checks"""
        print("\n" + "="*70)
        print("🔍 BB AGENT MANAGER - SYSTEM VERIFICATION")
        print("="*70)
        
        # 1. Check environment
        print("\n1️⃣  Environment Configuration")
        print("-"*70)
        await self._check_env_config()
        
        # 2. Check imports
        print("\n2️⃣  Python Dependencies")
        print("-"*70)
        await self._check_imports()
        
        # 3. Check Buildly Labs
        print("\n3️⃣  Buildly Labs Connection")
        print("-"*70)
        await self._check_buildly_connection()
        
        # 4. Check AI providers
        print("\n4️⃣  AI Provider Setup")
        print("-"*70)
        await self._check_ai_providers()
        
        # 5. Check file structure
        print("\n5️⃣  Project Structure")
        print("-"*70)
        await self._check_file_structure()
        
        # 6. Check credentials
        print("\n6️⃣  Authentication Status")
        print("-"*70)
        await self._check_credentials()
        
        # Summary
        await self._print_summary()
    
    async def _check_env_config(self):
        """Check environment configuration"""
        try:
            settings = AgentSettings()
            
            checks = {
                "LABS_BASE_URL": settings.labs_base_url,
                "LABS_API_TOKEN": "Set" if settings.labs_api_token else "Not set",
                "LLM_PROVIDER": settings.llm_provider or "default",
            }
            
            for key, value in checks.items():
                if value and value != "Not set":
                    print(f"  ✓ {key}: {value[:50] if len(str(value)) > 50 else value}")
                    self.checks.append((key, True, "Configured"))
                else:
                    print(f"  ✗ {key}: Not configured")
                    self.checks.append((key, False, "Missing"))
        
        except Exception as e:
            print(f"  ✗ Error reading environment: {e}")
            self.checks.append(("Environment", False, str(e)))
    
    async def _check_imports(self):
        """Check all required imports"""
        required_modules = {
            "httpx": "HTTP client",
            "asyncio": "Async support",
            "pydantic": "Data validation",
            "pathlib": "Path handling",
        }
        
        for module_name, description in required_modules.items():
            try:
                __import__(module_name)
                print(f"  ✓ {module_name}: {description}")
                self.checks.append((f"Import {module_name}", True, "Available"))
            except ImportError:
                print(f"  ✗ {module_name}: NOT INSTALLED")
                self.checks.append((f"Import {module_name}", False, "Not installed"))
    
    async def _check_buildly_connection(self):
        """Check Buildly Labs API connection"""
        try:
            settings = AgentSettings()
            client = get_buildly_client(settings.labs_base_url)
            
            # Try to load saved session
            result = await client.load_saved_session()
            
            if result.get("success"):
                user = result.get("user", {})
                print(f"  ✓ Authentication: Logged in as {user.get('name')}")
                self.checks.append(("Buildly Auth", True, "Authenticated"))
                
                # Check organizations
                if client.selected_org:
                    org = client.selected_org
                    print(f"  ✓ Organization: {org.get('name')}")
                    self.checks.append(("Buildly Org", True, "Selected"))
                else:
                    print(f"  ⚠ Organization: Not selected")
                    self.checks.append(("Buildly Org", False, "Not selected"))
                
                # Check products
                if client.selected_product:
                    prod = client.selected_product
                    print(f"  ✓ Product: {prod.get('name')}")
                    self.checks.append(("Buildly Product", True, "Selected"))
                else:
                    print(f"  ⚠ Product: Not selected")
                    self.checks.append(("Buildly Product", False, "Not selected"))
            else:
                print(f"  ✗ Authentication: No saved session")
                print(f"     Run: python scripts/test_buildly_integration.py")
                self.checks.append(("Buildly Auth", False, "No session"))
        
        except Exception as e:
            print(f"  ✗ Connection error: {e}")
            self.checks.append(("Buildly Connection", False, str(e)))
    
    async def _check_ai_providers(self):
        """Check AI provider configuration"""
        settings = AgentSettings()
        
        providers = {
            "Claude": {"key": "CLAUDE_API_KEY"},
            "OpenAI": {"key": "OPENAI_API_KEY"},
            "Gemini": {"key": "GEMINI_API_KEY"},
            "Ollama": {"url": "OLLAMA_BASE_URL"},
        }
        
        configured_count = 0
        
        for provider_name, config in providers.items():
            if "key" in config:
                key_name = config["key"]
                has_key = bool(getattr(settings, key_name.lower(), None))
                if has_key:
                    print(f"  ✓ {provider_name}: Configured")
                    self.checks.append((f"AI {provider_name}", True, "Ready"))
                    configured_count += 1
                else:
                    print(f"  - {provider_name}: Not configured")
                    self.checks.append((f"AI {provider_name}", False, "Not set"))
            else:
                url_name = config.get("url")
                # Check if Ollama is running
                print(f"  - {provider_name}: Requires local service")
                self.checks.append((f"AI {provider_name}", False, "Requires service"))
        
        if configured_count == 0:
            print(f"  ⚠ Warning: No AI providers configured")
        else:
            print(f"  ✓ {configured_count} AI provider(s) available")
    
    async def _check_file_structure(self):
        """Check project file structure"""
        root = Path(__file__).parent
        
        required_dirs = {
            "bb_agent_manager": "Main package",
            "scripts": "Script utilities",
            "devdocs": "Documentation",
            "tests": "Test suite",
        }
        
        required_files = {
            "requirements.txt": "Dependencies",
            ".env": "Configuration",
            "README.md": "Project README",
        }
        
        # Check directories
        for dir_name, description in required_dirs.items():
            dir_path = root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                print(f"  ✓ {dir_name}/: {description}")
                self.checks.append((f"Dir {dir_name}", True, "Present"))
            else:
                print(f"  ✗ {dir_name}/: Missing")
                self.checks.append((f"Dir {dir_name}", False, "Missing"))
        
        # Check files
        for file_name, description in required_files.items():
            file_path = root / file_name
            if file_path.exists() and file_path.is_file():
                print(f"  ✓ {file_name}: {description}")
                self.checks.append((f"File {file_name}", True, "Present"))
            else:
                print(f"  - {file_name}: {description} (optional)")
                self.checks.append((f"File {file_name}", False, "Missing"))
    
    async def _check_credentials(self):
        """Check Buildly Labs credentials"""
        config_file = Path.home() / ".bb_agent_config.json"
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                user = config.get("user", {})
                org = config.get("organization", {})
                product = config.get("product", {})
                
                print(f"  ✓ Credentials file: {config_file}")
                self.checks.append(("Credentials", True, "Found"))
                
                if user:
                    print(f"     User: {user.get('name', user.get('username'))}")
                if org:
                    print(f"     Organization: {org.get('name')}")
                if product:
                    print(f"     Product: {product.get('name')}")
            
            except Exception as e:
                print(f"  ✗ Error reading credentials: {e}")
                self.checks.append(("Credentials", False, f"Error: {e}"))
        else:
            print(f"  ⚠ Credentials file: Not found")
            print(f"     Location: {config_file}")
            print(f"     Run: python scripts/test_buildly_integration.py")
            self.checks.append(("Credentials", False, "Not found"))
    
    async def _print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("📊 VERIFICATION SUMMARY")
        print("="*70)
        
        passed = sum(1 for _, success, _ in self.checks if success)
        failed = sum(1 for _, success, _ in self.checks if not success)
        total = len(self.checks)
        
        print(f"\nTotal Checks: {total}")
        print(f"  ✓ Passed: {passed}")
        print(f"  ✗ Failed: {failed}")
        print(f"  Success Rate: {(passed/total)*100:.1f}%")
        
        if failed == 0:
            print("\n🎉 All systems operational!")
            print("\nReady to use:")
            print("  • python scripts/ai_work_coach.py")
            print("  • python scripts/ai_task_prioritizer.py")
            print("  • python scripts/task_state_manager.py")
        else:
            print("\n⚠️  Some issues need attention:")
            for check, success, message in self.checks:
                if not success:
                    print(f"  • {check}: {message}")
            
            print("\nNext steps:")
            print("  1. Configure missing API keys in .env")
            print("  2. Run: python scripts/test_buildly_integration.py")
            print("  3. Run this verification again")
        
        print("\n" + "="*70)
        
        return failed == 0
    
    def save_results(self):
        """Save verification results to JSON"""
        results = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "checks": [
                {
                    "name": name,
                    "passed": success,
                    "message": message
                }
                for name, success, message in self.checks
            ],
            "summary": {
                "total": len(self.checks),
                "passed": sum(1 for _, s, _ in self.checks if s),
                "failed": sum(1 for _, s, _ in self.checks if not s),
            }
        }
        
        results_file = Path(__file__).parent / "verification_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"✓ Results saved to: {results_file}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="System verification and health check")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    verifier = SystemVerifier(verbose=args.verbose)
    await verifier.verify_all()
    verifier.save_results()


if __name__ == "__main__":
    asyncio.run(main())
