# MCP (Model Context Protocol) server for CAPSULE system integration with AI tools

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

from .models import Capsule, CodePointer
from .generator import CapsuleGenerator
from models.database import get_repository_by_id
from models.database import get_graph_by_repo_id  
from models.database import get_understanding_by_repo_id


class MCPServer:
    """
    MCP server exposing CAPSULE tools for AI coding tools.
    
    Provides get_capsule, get_code, and get_state_registry tools
    that AI tools can use to access project context.
    """
    
    def __init__(self):
        self.capsule_generator = CapsuleGenerator()
        self.cached_capsules: Dict[str, Capsule] = {}
        self.server_running = False
    
    
    async def start_server(self, port: int = 3001):
        """Start the MCP server on the specified port"""
        
        # Note: This is a simplified MCP server implementation
        # In production, would use proper MCP SDK with full protocol support
        
        self.server_running = True
        print(f"MCP Server starting on port {port}")
        print("Available tools: get_capsule, get_code, get_state_registry")
        
        # TODO: Implement actual MCP protocol server
        # For now, this serves as the interface definition
        
        return {
            "status": "running",
            "port": port,
            "tools": [
                {
                    "name": "get_capsule",
                    "description": "Retrieve project CAPSULE with architecture and state",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repo_id": {"type": "string", "description": "Repository ID (owner/name)"},
                            "include_subsystems": {"type": "array", "items": {"type": "string"}, "description": "Specific subsystems to load"}
                        },
                        "required": ["repo_id"]
                    }
                },
                {
                    "name": "get_code", 
                    "description": "Retrieve specific code using CAPSULE code pointer",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "repo_id": {"type": "string", "description": "Repository ID"},
                            "file_path": {"type": "string", "description": "File path to retrieve"},
                            "line_start": {"type": "integer", "description": "Start line (optional)"},
                            "line_end": {"type": "integer", "description": "End line (optional)"},
                            "function_name": {"type": "string", "description": "Specific function (optional)"}
                        },
                        "required": ["repo_id", "file_path"]
                    }
                },
                {
                    "name": "get_state_registry",
                    "description": "Get current task state and blockers",
                    "parameters": {
                        "type": "object", 
                        "properties": {
                            "repo_id": {"type": "string", "description": "Repository ID"},
                            "task_filter": {"type": "string", "enum": ["all", "in_progress", "blocked"], "description": "Filter tasks by state"}
                        },
                        "required": ["repo_id"]
                    }
                }
            ]
        }
    
    
    async def get_capsule(self, repo_id: str, include_subsystems: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        MCP tool: Retrieve project CAPSULE.
        
        This is the core tool that AI tools use to get project context.
        """
        
        try:
            # Check cache first
            if repo_id in self.cached_capsules:
                capsule = self.cached_capsules[repo_id]
            else:
                # Generate fresh capsule
                capsule = await self._generate_capsule_for_repo(repo_id)
                self.cached_capsules[repo_id] = capsule
            
            if not capsule:
                return {"error": f"Could not generate capsule for repository {repo_id}"}
            
            # Convert to dict for MCP response
            capsule_dict = capsule.model_dump()
            
            # Add MCP-specific metadata
            capsule_dict["mcp_metadata"] = {
                "retrieved_at": capsule.metadata.updated_at.isoformat(),
                "format_version": "1.0.0",
                "compressed": False,  # TODO: Implement compression for large capsules
                "subsystems_loaded": include_subsystems or []
            }
            
            return {
                "status": "success",
                "capsule": capsule_dict
            }
            
        except Exception as e:
            return {"error": f"Failed to retrieve capsule: {str(e)}"}
    
    
    async def get_code(
        self, 
        repo_id: str, 
        file_path: str,
        line_start: Optional[int] = None,
        line_end: Optional[int] = None,
        function_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        MCP tool: Retrieve specific code using CAPSULE code pointer.
        
        This enables AI tools to get exact code on demand rather than 
        receiving large code dumps.
        """
        
        try:
            # Construct full path to repository
            repo_path = Path(f"workspaces") / repo_id / file_path
            
            if not repo_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            # Read file content
            with open(repo_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Apply line filtering if specified
            if line_start is not None or line_end is not None:
                start_idx = (line_start - 1) if line_start else 0
                end_idx = line_end if line_end else len(lines)
                lines = lines[start_idx:end_idx]
            
            code_content = ''.join(lines)
            
            # TODO: If function_name specified, extract just that function using AST
            
            return {
                "status": "success",
                "code": {
                    "file_path": file_path,
                    "content": code_content,
                    "line_count": len(lines),
                    "line_range": {
                        "start": line_start or 1,
                        "end": (line_start or 1) + len(lines) - 1
                    },
                    "encoding": "utf-8"
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to retrieve code: {str(e)}"}
    
    
    async def get_state_registry(self, repo_id: str, task_filter: str = "all") -> Dict[str, Any]:
        """
        MCP tool: Get current task state and blockers.
        
        This is crucial for AI tools to understand what's in progress,
        what was last attempted, and current blockers.
        """
        
        try:
            # Get capsule for state registry
            if repo_id in self.cached_capsules:
                capsule = self.cached_capsules[repo_id]
            else:
                capsule = await self._generate_capsule_for_repo(repo_id)
                if capsule:
                    self.cached_capsules[repo_id] = capsule
            
            if not capsule:
                return {"error": f"Could not retrieve state registry for {repo_id}"}
            
            # Filter tasks based on request
            tasks = capsule.state_registry
            
            if task_filter == "in_progress":
                tasks = [t for t in tasks if t.state == "in_progress"]
            elif task_filter == "blocked":
                tasks = [t for t in tasks if t.state == "blocked"]
            
            # Convert to dict format
            registry_data = {
                "repo_id": repo_id,
                "task_filter": task_filter,
                "total_tasks": len(capsule.state_registry),
                "filtered_count": len(tasks),
                "tasks": [task.model_dump() for task in tasks]
            }
            
            # Add summary statistics
            state_counts = {}
            for task in capsule.state_registry:
                state = task.state
                state_counts[state] = state_counts.get(state, 0) + 1
            
            registry_data["state_summary"] = state_counts
            
            return {
                "status": "success", 
                "state_registry": registry_data
            }
            
        except Exception as e:
            return {"error": f"Failed to retrieve state registry: {str(e)}"}
    
    
    async def _generate_capsule_for_repo(self, repo_id: str) -> Optional[Capsule]:
        """Generate a CAPSULE for the specified repository"""
        
        try:
            # Get repository data
            repository = get_repository_by_id(repo_id)
            if not repository:
                return None
            
            # Get graph and understanding if available
            graph_data = get_graph_by_repo_id(repo_id)
            understanding = get_understanding_by_repo_id(repo_id)
            
            # Generate capsule
            capsule = await self.capsule_generator.generate_capsule(
                repository=repository,
                graph_data=graph_data,
                understanding=understanding
            )
            
            return capsule
            
        except Exception as e:
            print(f"Error generating capsule for {repo_id}: {e}")
            return None
    
    
    async def update_capsule_state(self, repo_id: str, task_updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update the state registry for a repository's capsule.
        
        This is called when AI tools make progress on tasks.
        """
        
        try:
            if repo_id not in self.cached_capsules:
                return {"error": f"No cached capsule for {repo_id}"}
            
            capsule = self.cached_capsules[repo_id]
            
            # Update state registry
            updated_capsule = await self.capsule_generator.update_state_registry(
                capsule, task_updates
            )
            
            # Update cache
            self.cached_capsules[repo_id] = updated_capsule
            
            return {
                "status": "success",
                "message": f"Updated {len(task_updates)} tasks",
                "updated_at": updated_capsule.metadata.updated_at.isoformat()
            }
            
        except Exception as e:
            return {"error": f"Failed to update capsule state: {str(e)}"}
    
    
    async def export_capsule_json(self, repo_id: str) -> Dict[str, Any]:
        """
        Export capsule as JSON for manual paste into AI tools.
        
        This is the fallback when MCP connection is not available.
        """
        
        try:
            capsule_result = await self.get_capsule(repo_id)
            
            if "error" in capsule_result:
                return capsule_result
            
            capsule_json = json.dumps(capsule_result["capsule"], indent=2)
            
            return {
                "status": "success",
                "format": "json",
                "size_bytes": len(capsule_json.encode('utf-8')),
                "capsule_json": capsule_json,
                "usage_instructions": [
                    "Copy the capsule_json content",
                    "Paste into your AI tool chat",
                    "Add: 'Use this CAPSULE to understand the project context'",
                    "The AI tool can then ask for specific code via get_code requests"
                ]
            }
            
        except Exception as e:
            return {"error": f"Failed to export capsule JSON: {str(e)}"}
    
    
    def stop_server(self):
        """Stop the MCP server"""
        self.server_running = False
        print("MCP Server stopped")


# Global server instance
mcp_server = MCPServer()
