"""
Buildly Labs Authentication and API Integration
Handles user login, org/product selection, and task management
"""
from typing import Dict, Any, Optional, List
import httpx
import json
import os
from pathlib import Path

class BuildlyLabsClient:
    """Client for Buildly Labs platform API"""
    
    def __init__(self, base_url: str = "https://labs.buildly.io/api"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        self.selected_org: Optional[Dict[str, Any]] = None
        self.selected_product: Optional[Dict[str, Any]] = None
        self.config_file = Path.home() / ".bb_agent_config.json"
    
    async def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate user with Buildly Labs
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            User info and authentication token
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.user_info = data.get("user")
                
                # Save token and user info
                await self._save_config()
                
                return {
                    "success": True,
                    "user": self.user_info,
                    "message": f"Welcome, {self.user_info.get('name', username)}!"
                }
            else:
                return {
                    "success": False,
                    "error": f"Login failed: {response.text}",
                    "status": response.status_code
                }
    
    async def get_organizations(self) -> Dict[str, Any]:
        """Get list of organizations user belongs to"""
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/organizations",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                orgs = response.json()
                return {
                    "success": True,
                    "organizations": orgs,
                    "count": len(orgs)
                }
            else:
                return {"error": f"Failed to fetch organizations: {response.text}"}
    
    async def select_organization(self, org_id: int) -> Dict[str, Any]:
        """Select an organization to work with"""
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/organizations/{org_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                self.selected_org = response.json()
                await self._save_config()
                
                return {
                    "success": True,
                    "organization": self.selected_org,
                    "message": f"Selected organization: {self.selected_org.get('name')}"
                }
            else:
                return {"error": f"Failed to select organization: {response.text}"}
    
    async def get_products(self, org_id: Optional[int] = None) -> Dict[str, Any]:
        """Get list of products in selected organization"""
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        org_id = org_id or (self.selected_org.get("id") if self.selected_org else None)
        if not org_id:
            return {"error": "No organization selected"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/organizations/{org_id}/products",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                products = response.json()
                return {
                    "success": True,
                    "products": products,
                    "count": len(products)
                }
            else:
                return {"error": f"Failed to fetch products: {response.text}"}
    
    async def select_product(self, product_id: int) -> Dict[str, Any]:
        """Select a product to work on"""
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products/{product_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                self.selected_product = response.json()
                await self._save_config()
                
                return {
                    "success": True,
                    "product": self.selected_product,
                    "message": f"Selected product: {self.selected_product.get('name')}"
                }
            else:
                return {"error": f"Failed to select product: {response.text}"}
    
    async def associate_api_with_product(
        self,
        product_id: int,
        api_name: str,
        api_url: str,
        api_description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Associate an API with a product"""
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/products/{product_id}/apis",
                headers=self._get_headers(),
                json={
                    "name": api_name,
                    "url": api_url,
                    "description": api_description
                }
            )
            
            if response.status_code in [200, 201]:
                api_info = response.json()
                return {
                    "success": True,
                    "api": api_info,
                    "message": f"API '{api_name}' associated with product"
                }
            else:
                return {"error": f"Failed to associate API: {response.text}"}
    
    async def get_prioritized_tasks(
        self,
        product_id: Optional[int] = None,
        task_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get prioritized list of features, issues, and punchlist items
        
        Args:
            product_id: Product ID (uses selected product if not provided)
            task_types: Filter by types: ['feature', 'issue', 'punchlist']
        """
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        product_id = product_id or (self.selected_product.get("id") if self.selected_product else None)
        if not product_id:
            return {"error": "No product selected"}
        
        # Build query parameters
        params = {}
        if task_types:
            params["types"] = ",".join(task_types)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/products/{product_id}/tasks",
                headers=self._get_headers(),
                params=params
            )
            
            if response.status_code == 200:
                tasks = response.json()
                
                # Organize by type and priority
                organized = {
                    "features": [],
                    "issues": [],
                    "punchlist": []
                }
                
                for task in tasks:
                    task_type = task.get("type", "").lower()
                    if task_type == "feature":
                        organized["features"].append(task)
                    elif task_type == "issue" or task_type == "bug":
                        organized["issues"].append(task)
                    elif task_type == "punchlist" or task_type == "task":
                        organized["punchlist"].append(task)
                
                # Sort by priority
                for category in organized.values():
                    category.sort(key=lambda x: x.get("priority", 999))
                
                return {
                    "success": True,
                    "tasks": organized,
                    "total": len(tasks),
                    "product": self.selected_product.get("name") if self.selected_product else None
                }
            else:
                return {"error": f"Failed to fetch tasks: {response.text}"}
    
    async def resolve_task(
        self,
        task_id: int,
        commit_sha: str,
        commit_message: str,
        pr_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Mark a task as resolved with commit information
        
        Args:
            task_id: Task ID to resolve
            commit_sha: Git commit SHA
            commit_message: Commit message
            pr_number: Optional PR number
        """
        if not self.token:
            return {"error": "Not authenticated. Please login first."}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/tasks/{task_id}/resolve",
                headers=self._get_headers(),
                json={
                    "commit_sha": commit_sha,
                    "commit_message": commit_message,
                    "pr_number": pr_number,
                    "resolved_at": httpx.codes.get("ISO-8601 timestamp"),
                    "resolved_by": self.user_info.get("id") if self.user_info else None
                }
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                return {
                    "success": True,
                    "task": result,
                    "message": f"Task #{task_id} marked as resolved"
                }
            else:
                return {"error": f"Failed to resolve task: {response.text}"}
    
    async def logout(self) -> Dict[str, Any]:
        """Logout and clear saved credentials"""
        self.token = None
        self.user_info = None
        self.selected_org = None
        self.selected_product = None
        
        if self.config_file.exists():
            self.config_file.unlink()
        
        return {"success": True, "message": "Logged out successfully"}
    
    async def load_saved_session(self) -> Dict[str, Any]:
        """Load previously saved session"""
        if not self.config_file.exists():
            return {"error": "No saved session found"}
        
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            self.token = config.get("token")
            self.user_info = config.get("user_info")
            self.selected_org = config.get("selected_org")
            self.selected_product = config.get("selected_product")
            
            return {
                "success": True,
                "user": self.user_info,
                "organization": self.selected_org,
                "product": self.selected_product
            }
        except Exception as e:
            return {"error": f"Failed to load session: {str(e)}"}
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authentication"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        return headers
    
    async def _save_config(self):
        """Save current session configuration"""
        config = {
            "token": self.token,
            "user_info": self.user_info,
            "selected_org": self.selected_org,
            "selected_product": self.selected_product
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)


# Tool definitions for MCP
BUILDLY_LOGIN_TOOL = {
    "name": "buildly_login",
    "description": "Login to Buildly Labs platform with username and password",
    "parameters": {
        "type": "object",
        "properties": {
            "username": {"type": "string", "description": "Username or email"},
            "password": {"type": "string", "description": "Password"}
        },
        "required": ["username", "password"]
    }
}

BUILDLY_SELECT_ORG_TOOL = {
    "name": "buildly_select_org",
    "description": "Select an organization to work with",
    "parameters": {
        "type": "object",
        "properties": {
            "org_id": {"type": "integer", "description": "Organization ID"}
        },
        "required": ["org_id"]
    }
}

BUILDLY_SELECT_PRODUCT_TOOL = {
    "name": "buildly_select_product",
    "description": "Select a product to work on",
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {"type": "integer", "description": "Product ID"}
        },
        "required": ["product_id"]
    }
}

BUILDLY_GET_TASKS_TOOL = {
    "name": "buildly_get_tasks",
    "description": "Get prioritized list of features, issues, and punchlist items for selected product",
    "parameters": {
        "type": "object",
        "properties": {
            "task_types": {
                "type": "array",
                "items": {"type": "string", "enum": ["feature", "issue", "punchlist"]},
                "description": "Filter by task types (optional)"
            }
        }
    }
}

BUILDLY_RESOLVE_TASK_TOOL = {
    "name": "buildly_resolve_task",
    "description": "Mark a task as resolved with commit information",
    "parameters": {
        "type": "object",
        "properties": {
            "task_id": {"type": "integer", "description": "Task ID to resolve"},
            "commit_sha": {"type": "string", "description": "Git commit SHA"},
            "commit_message": {"type": "string", "description": "Commit message"},
            "pr_number": {"type": "integer", "description": "Pull request number (optional)"}
        },
        "required": ["task_id", "commit_sha", "commit_message"]
    }
}

BUILDLY_ASSOCIATE_API_TOOL = {
    "name": "buildly_associate_api",
    "description": "Associate an API with the selected product",
    "parameters": {
        "type": "object",
        "properties": {
            "api_name": {"type": "string", "description": "API name"},
            "api_url": {"type": "string", "description": "API base URL"},
            "api_description": {"type": "string", "description": "API description (optional)"}
        },
        "required": ["api_name", "api_url"]
    }
}


# Global client instance
_buildly_client: Optional[BuildlyLabsClient] = None

def get_buildly_client(base_url: Optional[str] = None) -> BuildlyLabsClient:
    """Get or create Buildly Labs client instance"""
    global _buildly_client
    if _buildly_client is None:
        _buildly_client = BuildlyLabsClient(base_url or os.getenv("LABS_BASE_URL", "https://labs.buildly.io/api"))
    return _buildly_client


# Tool implementations
async def buildly_login(username: str, password: str) -> str:
    """Login to Buildly Labs"""
    client = get_buildly_client()
    result = await client.login(username, password)
    
    if result.get("success"):
        # Also fetch organizations
        orgs = await client.get_organizations()
        if orgs.get("success") and orgs.get("count", 0) > 0:
            result["organizations"] = orgs["organizations"]
            result["message"] += f"\n\nFound {orgs['count']} organization(s). Use buildly_select_org to choose one."
    
    return json.dumps(result, indent=2)

async def buildly_select_org(org_id: int) -> str:
    """Select organization"""
    client = get_buildly_client()
    result = await client.select_organization(org_id)
    
    if result.get("success"):
        # Also fetch products
        products = await client.get_products(org_id)
        if products.get("success") and products.get("count", 0) > 0:
            result["products"] = products["products"]
            result["message"] += f"\n\nFound {products['count']} product(s). Use buildly_select_product to choose one."
    
    return json.dumps(result, indent=2)

async def buildly_select_product(product_id: int) -> str:
    """Select product"""
    client = get_buildly_client()
    result = await client.select_product(product_id)
    
    if result.get("success"):
        # Also fetch tasks
        tasks = await client.get_prioritized_tasks(product_id)
        if tasks.get("success"):
            result["tasks_summary"] = {
                "features": len(tasks["tasks"]["features"]),
                "issues": len(tasks["tasks"]["issues"]),
                "punchlist": len(tasks["tasks"]["punchlist"]),
                "total": tasks["total"]
            }
            result["message"] += f"\n\nFound {tasks['total']} task(s) to work on."
    
    return json.dumps(result, indent=2)

async def buildly_get_tasks(task_types: Optional[List[str]] = None) -> str:
    """Get prioritized tasks"""
    client = get_buildly_client()
    result = await client.get_prioritized_tasks(task_types=task_types)
    return json.dumps(result, indent=2)

async def buildly_resolve_task(
    task_id: int,
    commit_sha: str,
    commit_message: str,
    pr_number: Optional[int] = None
) -> str:
    """Resolve task with commit"""
    client = get_buildly_client()
    result = await client.resolve_task(task_id, commit_sha, commit_message, pr_number)
    return json.dumps(result, indent=2)

async def buildly_associate_api(
    api_name: str,
    api_url: str,
    api_description: Optional[str] = None
) -> str:
    """Associate API with product"""
    client = get_buildly_client()
    
    if not client.selected_product:
        return json.dumps({"error": "No product selected"})
    
    result = await client.associate_api_with_product(
        client.selected_product["id"],
        api_name,
        api_url,
        api_description
    )
    return json.dumps(result, indent=2)
