# CAPSULE system data structures and schemas for portable project state

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """Task completion state for state registry"""
    DONE = "done"
    IN_PROGRESS = "in_progress" 
    STUBBED = "stubbed"
    BLOCKED = "blocked"


class ComponentType(str, Enum):
    """Type of code component for contract definitions"""
    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    SERVICE = "service"
    API_ENDPOINT = "api_endpoint"
    DATABASE_TABLE = "database_table"


class CodePointer(BaseModel):
    """Reference to specific code location without containing the actual code"""
    file_path: str = Field(..., description="Relative path to the file")
    line_start: Optional[int] = Field(None, description="Starting line number (1-indexed)")
    line_end: Optional[int] = Field(None, description="Ending line number (1-indexed)")
    function_name: Optional[str] = Field(None, description="Function or method name")
    class_name: Optional[str] = Field(None, description="Class name if applicable")
    commit_hash: Optional[str] = Field(None, description="Git commit hash for exact version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "src/services/parser.py",
                "line_start": 45,
                "line_end": 78,
                "function_name": "parse_ast_tree",
                "class_name": "ASTParser",
                "commit_hash": "abc123def"
            }
        }


class ComponentContract(BaseModel):
    """Mechanical and semantic contract for a code component"""
    component_id: str = Field(..., description="Unique identifier for the component")
    component_type: ComponentType = Field(..., description="Type of component")
    name: str = Field(..., description="Display name")
    
    # Mechanical contracts (AST-derived)
    inputs: List[str] = Field(default_factory=list, description="Input parameters/dependencies")
    outputs: List[str] = Field(default_factory=list, description="Return types/exports")
    dependencies: List[str] = Field(default_factory=list, description="Internal dependencies")
    
    # Semantic contracts (inferred from docs/types/tests)
    guarantees: List[str] = Field(default_factory=list, description="What this component promises to do")
    constraints: List[str] = Field(default_factory=list, description="Limitations and assumptions")
    
    # Code reference
    code_pointer: CodePointer = Field(..., description="Reference to the actual implementation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "component_id": "ast_parser",
                "component_type": "service",
                "name": "AST Parser Service",
                "inputs": ["source_code: str", "language: str"],
                "outputs": ["ParseResult"],
                "dependencies": ["tree_sitter", "language_models"],
                "guarantees": ["Returns valid AST for supported languages", "Handles syntax errors gracefully"],
                "constraints": ["Only supports Python, JS, TS, Go, Rust", "Requires valid UTF-8 input"],
                "code_pointer": {
                    "file_path": "services/parser.py",
                    "class_name": "ASTParser"
                }
            }
        }


class StateRegistryEntry(BaseModel):
    """Entry in the state registry tracking task completion and blockers"""
    task_id: str = Field(..., description="Unique task identifier")
    task_description: str = Field(..., description="Human-readable task description")
    state: TaskState = Field(..., description="Current completion state")
    
    # For in-progress tasks
    current_attempt: Optional[str] = Field(None, description="What is currently being tried")
    last_attempt: Optional[str] = Field(None, description="What was last attempted")
    blockers: List[str] = Field(default_factory=list, description="Current blockers preventing progress")
    
    # Progress tracking
    progress_notes: List[str] = Field(default_factory=list, description="Development notes and findings")
    related_components: List[str] = Field(default_factory=list, description="Component IDs this task affects")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "implement_voice_input",
                "task_description": "Add Web Speech API integration for voice commands",
                "state": "in_progress",
                "current_attempt": "Implementing browser compatibility checks",
                "last_attempt": "Added basic speech recognition hooks",
                "blockers": ["Safari support limited", "Need fallback UI"],
                "progress_notes": ["Chrome works well", "Firefox needs testing"],
                "related_components": ["voice_input_service", "ui_components"]
            }
        }


class DecisionLogEntry(BaseModel):
    """ADR-style decision log entry for architectural choices"""
    decision_id: str = Field(..., description="Unique decision identifier")
    title: str = Field(..., description="Brief decision title")
    context: str = Field(..., description="Why this decision was needed")
    decision: str = Field(..., description="What was decided")
    rationale: str = Field(..., description="Why this decision was made")
    consequences: List[str] = Field(default_factory=list, description="Expected outcomes and tradeoffs")
    alternatives_considered: List[str] = Field(default_factory=list, description="Other options that were considered")
    
    # Metadata
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    decided_by: Optional[str] = Field(None, description="Who made the decision")
    status: str = Field(default="active", description="active, superseded, deprecated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "decision_id": "use_mcp_for_ai_integration", 
                "title": "Use Model Context Protocol for AI tool integration",
                "context": "Need standard way to share capsules across multiple AI tools",
                "decision": "Implement MCP server with get_capsule, get_code, get_state_registry tools",
                "rationale": "MCP is vendor-neutral and supported by major AI tools",
                "consequences": ["Better tool compatibility", "Requires MCP server maintenance"],
                "alternatives_considered": ["Custom API per tool", "Direct JSON export only"]
            }
        }


class ArchitectureGraph(BaseModel):
    """Graph representation of system architecture and component relationships"""
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Graph nodes (components)")
    edges: List[Dict[str, Any]] = Field(default_factory=list, description="Graph edges (relationships)")
    clusters: List[Dict[str, Any]] = Field(default_factory=list, description="Component clusters/modules")
    
    # Graph metrics
    centrality_metrics: Dict[str, float] = Field(default_factory=dict, description="Node centrality scores")
    community_structure: Dict[str, List[str]] = Field(default_factory=dict, description="Detected communities")
    
    class Config:
        json_schema_extra = {
            "example": {
                "nodes": [
                    {"id": "ast_parser", "label": "AST Parser", "type": "service", "size": 10},
                    {"id": "graph_builder", "label": "Graph Builder", "type": "service", "size": 8}
                ],
                "edges": [
                    {"source": "ast_parser", "target": "graph_builder", "type": "dependency"}
                ],
                "clusters": [
                    {"id": "parsing", "label": "Parsing Services", "nodes": ["ast_parser"]}
                ]
            }
        }


class CapsuleMetadata(BaseModel):
    """Metadata about the capsule itself"""
    capsule_id: str = Field(..., description="Unique capsule identifier")
    project_name: str = Field(..., description="Project name")
    project_repo: Optional[str] = Field(None, description="Repository URL")
    
    # Versioning
    version: str = Field(default="1.0.0", description="Capsule format version")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Who created this capsule")
    
    # Size and complexity metrics
    total_components: int = Field(default=0, description="Number of components")
    total_tasks: int = Field(default=0, description="Number of tasks in state registry")
    total_decisions: int = Field(default=0, description="Number of decisions logged")
    
    class Config:
        json_schema_extra = {
            "example": {
                "capsule_id": "amica_v1_20240918",
                "project_name": "Amica",
                "project_repo": "https://github.com/example/amica",
                "version": "1.0.0",
                "total_components": 15,
                "total_tasks": 8,
                "total_decisions": 5
            }
        }


class Capsule(BaseModel):
    """
    Complete CAPSULE containing all portable project state.
    
    A CAPSULE is a compact, portable snapshot of project architecture,
    state, and decisions that enables seamless AI tool switching.
    """
    
    # Core metadata
    metadata: CapsuleMetadata = Field(..., description="Capsule metadata and versioning info")
    
    # 1. Project intent
    project_intent: str = Field(..., description="Short distilled goal statement")
    
    # 2. Architecture graph
    architecture: ArchitectureGraph = Field(..., description="System architecture and component relationships")
    
    # 3. Component contracts  
    components: List[ComponentContract] = Field(default_factory=list, description="Component contracts and interfaces")
    
    # 4. Tech stack
    tech_stack: Dict[str, str] = Field(default_factory=dict, description="Technologies and pinned versions")
    
    # 5. State registry
    state_registry: List[StateRegistryEntry] = Field(default_factory=list, description="Task completion state and blockers")
    
    # 6. Decision log
    decisions: List[DecisionLogEntry] = Field(default_factory=list, description="Architectural decisions and rationale")
    
    # 7. Known issues
    known_issues: List[Dict[str, Any]] = Field(default_factory=list, description="Known problems and attempted solutions")
    
    # 8. Code pointers index
    code_index: Dict[str, CodePointer] = Field(default_factory=dict, description="Index of all code references")
    
    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
                    "capsule_id": "amica_v1_20240918",
                    "project_name": "Amica", 
                    "project_repo": "https://github.com/example/amica"
                },
                "project_intent": "SaaS layer enabling portable project state between AI coding tools via CAPSULE system",
                "tech_stack": {
                    "backend": "Python 3.12 + FastAPI",
                    "frontend": "Next.js 16 + React 19", 
                    "database": "SQLite",
                    "ai_integration": "MCP Server"
                }
            }
        }


class FederatedCapsule(BaseModel):
    """
    Federated/hierarchical capsule for large projects.
    
    Top-level capsule contains project overview and index of subsystem capsules.
    Each subsystem has its own child capsule with full detail.
    """
    
    # Top-level capsule (lightweight)
    root_capsule: Capsule = Field(..., description="Top-level project capsule")
    
    # Subsystem index
    subsystems: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Index of subsystem capsules")
    
    # Loading metadata
    loaded_subsystems: List[str] = Field(default_factory=list, description="Currently loaded subsystem IDs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subsystems": {
                    "backend": {
                        "name": "Backend Services",
                        "summary": "FastAPI backend with AST parsing and graph services", 
                        "capsule_ref": "backend_capsule_hash_abc123",
                        "component_count": 12,
                        "connections": ["frontend", "database"]
                    },
                    "frontend": {
                        "name": "React Frontend",
                        "summary": "Next.js frontend with graph visualization",
                        "capsule_ref": "frontend_capsule_hash_def456", 
                        "component_count": 8,
                        "connections": ["backend"]
                    }
                }
            }
        }