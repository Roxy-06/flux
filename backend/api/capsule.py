# FastAPI Router for CAPSULE system operations and MCP server management

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from capsule.generator import CapsuleGenerator
from capsule.mcp_server import mcp_server
from capsule.models import Capsule, StateRegistryEntry
from models.database import get_repository_by_id, get_graph_by_repo_id, get_understanding_by_repo_id


router = APIRouter(tags=["capsule"])


class CapsuleRequest(BaseModel):
    """Request schema for CAPSULE generation"""
    regenerate: bool = Field(False, description="Force regeneration even if cached")
    include_subsystems: Optional[List[str]] = Field(None, description="Specific subsystems to include")


class StateUpdateRequest(BaseModel):
    """Request schema for updating state registry"""
    task_updates: List[Dict[str, Any]] = Field(..., description="Task state updates")


class MCPServerRequest(BaseModel):
    """Request schema for MCP server control"""
    port: int = Field(3001, description="Port to run MCP server on")


# CAPSULE Operations

@router.post("/api/repos/{owner}/{repo}/capsule")
async def generate_capsule(owner: str, repo: str, req: CapsuleRequest = CapsuleRequest()):
    """
    Generate or retrieve a CAPSULE for the specified repository.
    
    The CAPSULE contains project architecture, state, decisions, and code pointers
    for seamless AI tool context transfer.
    """
    
    repo_id = f"{owner.lower()}/{repo.lower()}"
    
    try:
        # Get repository data
        repository = get_repository_by_id(repo_id)
        if not repository:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {repo_id} not found. Please ingest the repository first."
            )
        
        # Get supporting data
        graph_data = get_graph_by_repo_id(repo_id)
        understanding = get_understanding_by_repo_id(repo_id)
        
        # Generate CAPSULE
        generator = CapsuleGenerator()
        capsule = await generator.generate_capsule(
            repository=repository,
            graph_data=graph_data,
            understanding=understanding
        )
        
        return {
            "status": "success",
            "repository": {"owner": owner, "name": repo},
            "capsule": capsule.model_dump(),
            "size_info": {
                "total_components": len(capsule.components),
                "total_tasks": len(capsule.state_registry),
                "total_decisions": len(capsule.decisions),
                "total_issues": len(capsule.known_issues)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate CAPSULE: {str(e)}"
        )


@router.get("/api/repos/{owner}/{repo}/capsule")
async def get_capsule(owner: str, repo: str):
    """Retrieve existing CAPSULE for repository"""
    
    repo_id = f"{owner.lower()}/{repo.lower()}"
    
    try:
        # Use MCP server to get capsule
        result = await mcp_server.get_capsule(repo_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve CAPSULE: {str(e)}"
        )


@router.put("/api/repos/{owner}/{repo}/capsule/state")  
async def update_capsule_state(owner: str, repo: str, req: StateUpdateRequest):
    """
    Update the state registry in a repository's CAPSULE.
    
    This is used to track task progress, blockers, and current work.
    """
    
    repo_id = f"{owner.lower()}/{repo.lower()}"
    
    try:
        result = await mcp_server.update_capsule_state(repo_id, req.task_updates)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update CAPSULE state: {str(e)}"
        )


@router.get("/api/repos/{owner}/{repo}/capsule/export")
async def export_capsule_json(owner: str, repo: str):
    """
    Export CAPSULE as JSON for manual paste into AI tools.
    
    This is the fallback when MCP connection is not available.
    """
    
    repo_id = f"{owner.lower()}/{repo.lower()}"
    
    try:
        result = await mcp_server.export_capsule_json(repo_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export CAPSULE: {str(e)}"
        )


# MCP Server Operations

@router.post("/api/mcp/start")
async def start_mcp_server(req: MCPServerRequest = MCPServerRequest()):
    """
    Start the MCP server for AI tool integration.
    
    The MCP server exposes get_capsule, get_code, and get_state_registry tools
    that AI tools can use to access project context.
    """
    
    try:
        result = await mcp_server.start_server(port=req.port)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start MCP server: {str(e)}"
        )


@router.post("/api/mcp/stop") 
async def stop_mcp_server():
    """Stop the MCP server"""
    
    try:
        mcp_server.stop_server()
        return {"status": "stopped", "message": "MCP server stopped successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop MCP server: {str(e)}"
        )


@router.get("/api/mcp/status")
async def get_mcp_server_status():
    """Get MCP server status and available tools"""
    
    return {
        "status": "running" if mcp_server.server_running else "stopped",
        "tools": [
            {
                "name": "get_capsule",
                "description": "Retrieve project CAPSULE with architecture and state"
            },
            {
                "name": "get_code", 
                "description": "Retrieve specific code using CAPSULE code pointer"
            },
            {
                "name": "get_state_registry",
                "description": "Get current task state and blockers"
            }
        ],
        "cached_repos": list(mcp_server.cached_capsules.keys())
    }


# Code Retrieval (MCP Tool Implementation)

@router.get("/api/repos/{owner}/{repo}/code")
async def get_code(
    owner: str,
    repo: str, 
    file_path: str,
    line_start: Optional[int] = None,
    line_end: Optional[int] = None,
    function_name: Optional[str] = None
):
    """
    Retrieve specific code from repository.
    
    This implements the get_code MCP tool for direct API access.
    """
    
    repo_id = f"{owner.lower()}/{repo.lower()}"
    
    try:
        result = await mcp_server.get_code(
            repo_id=repo_id,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            function_name=function_name
        )
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve code: {str(e)}"
        )


@router.get("/api/repos/{owner}/{repo}/state-registry")
async def get_state_registry(owner: str, repo: str, task_filter: str = "all"):
    """
    Get current task state registry from CAPSULE.
    
    This implements the get_state_registry MCP tool for direct API access.
    """
    
    repo_id = f"{owner.lower()}/{repo.lower()}"
    
    try:
        result = await mcp_server.get_state_registry(repo_id, task_filter)
        
        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve state registry: {str(e)}"
        )