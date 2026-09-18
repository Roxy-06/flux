# CAPSULE generation and management service for portable project state

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from .models import (
    Capsule, CapsuleMetadata, ArchitectureGraph, ComponentContract, 
    StateRegistryEntry, DecisionLogEntry, CodePointer, ComponentType, TaskState
)
# Repository type is dict from database
# Graph data is dict from database
# RepoUnderstanding type is dict from database




class CapsuleGenerator:
    """Service for generating and managing CAPSULE snapshots of project state"""
    
    def __init__(self):
        pass  # Services removed for simplicity
        
    
    
    async def generate_capsule(
        self, 
        repository: dict,
        graph_data: Optional[dict] = None,
        understanding: Optional[dict] = None,
        existing_state: Optional[Dict[str, Any]] = None
    ) -> Capsule:
        """
        Generate a complete CAPSULE from repository analysis.
        
        Args:
            repository: dict metadata
            graph_data: Dependency graph analysis (optional, will generate if missing)
            understanding: Repository understanding (optional, will generate if missing) 
            existing_state: Previous capsule state for incremental updates
        
        Returns:
            Complete CAPSULE with project state
        """
        
        # Generate metadata
        metadata = self._generate_metadata(repository, existing_state)
        
        # Extract project intent
        project_intent = self._extract_project_intent(repository, understanding)
        
        # Build architecture graph
        architecture = await self._build_architecture_graph(repository, graph_data)
        
        # Generate component contracts
        components = await self._generate_component_contracts(repository, graph_data)
        
        # Extract tech stack
        tech_stack = await self._extract_tech_stack(repository)
        
        # Initialize or update state registry
        state_registry = self._build_state_registry(existing_state)
        
        # Initialize or update decision log
        decisions = self._build_decision_log(existing_state)
        
        # Extract known issues
        known_issues = self._extract_known_issues(repository)
        
        # Build code index
        code_index = self._build_code_index(components)
        
        return Capsule(
            metadata=metadata,
            project_intent=project_intent,
            architecture=architecture,
            components=components,
            tech_stack=tech_stack,
            state_registry=state_registry,
            decisions=decisions,
            known_issues=known_issues,
            code_index=code_index
        )
    
    
    def _generate_metadata(self, repository: dict, existing_state: Optional[Dict[str, Any]]) -> CapsuleMetadata:
        """Generate capsule metadata"""
        
        capsule_id = f"{repository.name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        if existing_state and "metadata" in existing_state:
            # Preserve some metadata from existing capsule
            existing_meta = existing_state["metadata"]
            created_at = datetime.fromisoformat(existing_meta.get("created_at", datetime.utcnow().isoformat()))
            created_by = existing_meta.get("created_by")
        else:
            created_at = datetime.utcnow()
            created_by = None
        
        return CapsuleMetadata(
            capsule_id=capsule_id,
            project_name=repository.name,
            project_repo=repository.html_url,
            created_at=created_at,
            updated_at=datetime.utcnow(),
            created_by=created_by
        )
    
    
    def _extract_project_intent(self, repository: dict, understanding: Optional[dict]) -> str:
        """Extract distilled project intent from repository metadata and understanding"""
        
        if understanding and understanding.overview:
            # Extract intent from AI-generated overview
            overview = understanding.overview
            # Take first sentence as intent, fallback to description
            first_sentence = overview.split('.')[0].strip()
            if len(first_sentence) > 20:
                return first_sentence + '.'
        
        # Fallback to repository description
        if repository.description:
            return repository.description
            
        return f"Software project: {repository.name}"
    
    
    async def _build_architecture_graph(self, repository: dict, graph_data: Optional[dict]) -> ArchitectureGraph:
        """Build architecture graph from dependency analysis"""
        
        if not graph_data:
            # Generate graph if not provided
            graph_data = await self.graph_service.build_graph(repository.owner, repository.name)
        
        # Convert graph data to architecture format
        nodes = []
        edges = []
        
        if graph_data and graph_data.nodes:
            for node_data in graph_data.nodes:
                nodes.append({
                    "id": node_data.get("id", ""),
                    "label": node_data.get("label", ""),
                    "type": node_data.get("type", "module"),
                    "size": node_data.get("size", 5),
                    "centrality": node_data.get("centrality", 0.0)
                })
        
        if graph_data and graph_data.edges:
            for edge_data in graph_data.edges:
                edges.append({
                    "source": edge_data.get("source", ""),
                    "target": edge_data.get("target", ""),
                    "type": edge_data.get("type", "dependency"),
                    "weight": edge_data.get("weight", 1.0)
                })
        
        return ArchitectureGraph(
            nodes=nodes,
            edges=edges,
            clusters=[],  # TODO: Extract from community detection
            centrality_metrics={},  # TODO: Extract centrality scores
            community_structure={}  # TODO: Extract community structure
        )
    
    
    async def _generate_component_contracts(self, repository: dict, graph_data: Optional[dict]) -> List[ComponentContract]:
        """Generate component contracts from AST analysis"""
        
        components = []
        
        # Get key files from graph analysis
        key_files = []
        if graph_data and graph_data.nodes:
            # Focus on high-centrality nodes
            sorted_nodes = sorted(
                graph_data.nodes, 
                key=lambda x: x.get("centrality", 0), 
                reverse=True
            )
            key_files = [node.get("id", "") for node in sorted_nodes[:10]]  # Top 10
        
        # Generate contracts for key components
        for file_path in key_files:
            if not file_path:
                continue
                
            try:
                # Infer component type from file path
                component_type = self._infer_component_type(file_path)
                
                # Extract basic contract info
                contract = ComponentContract(
                    component_id=self._generate_component_id(file_path),
                    component_type=component_type,
                    name=self._generate_component_name(file_path),
                    inputs=[],  # TODO: Extract from AST
                    outputs=[],  # TODO: Extract from AST  
                    dependencies=[],  # TODO: Extract from imports
                    guarantees=[],  # TODO: Extract from docstrings
                    constraints=[],  # TODO: Extract from type hints
                    code_pointer=CodePointer(file_path=file_path)
                )
                
                components.append(contract)
                
            except Exception as e:
                # Skip problematic files
                continue
        
        return components
    
    
    async def _extract_tech_stack(self, repository: dict) -> Dict[str, str]:
        """Extract tech stack and versions from repository files"""
        
        tech_stack = {}
        
        # Look for common dependency files
        repo_path = Path(f"workspaces/{repository.owner}/{repository.name}")
        
        if repo_path.exists():
            # Python
            requirements_file = repo_path / "requirements.txt"
            if requirements_file.exists():
                tech_stack["python_deps"] = "requirements.txt"
            
            # Node.js
            package_json = repo_path / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        pkg_data = json.load(f)
                        if "dependencies" in pkg_data:
                            key_deps = list(pkg_data["dependencies"].keys())[:5]  # Top 5
                            tech_stack["node_deps"] = ", ".join(key_deps)
                except Exception:
                    tech_stack["node_deps"] = "package.json"
            
            # Go
            go_mod = repo_path / "go.mod"
            if go_mod.exists():
                tech_stack["go_deps"] = "go.mod"
            
            # Rust  
            cargo_toml = repo_path / "Cargo.toml"
            if cargo_toml.exists():
                tech_stack["rust_deps"] = "Cargo.toml"
        
        # Default fallback
        if not tech_stack:
            tech_stack["language"] = "Multi-language"
            
        return tech_stack
    
    
    def _build_state_registry(self, existing_state: Optional[Dict[str, Any]]) -> List[StateRegistryEntry]:
        """Build or update state registry from existing state"""
        
        if existing_state and "state_registry" in existing_state:
            # Preserve existing state registry
            registry_data = existing_state["state_registry"]
            return [StateRegistryEntry(**entry) for entry in registry_data]
        
        # Initialize with basic project setup tasks
        return [
            StateRegistryEntry(
                task_id="project_setup",
                task_description="Initial project structure and configuration",
                state=TaskState.DONE,
                progress_notes=["Repository ingested and analyzed"]
            ),
            StateRegistryEntry(
                task_id="dependency_analysis", 
                task_description="AST parsing and dependency graph construction",
                state=TaskState.DONE,
                progress_notes=["Graph generated from AST analysis"]
            )
        ]
    
    
    def _build_decision_log(self, existing_state: Optional[Dict[str, Any]]) -> List[DecisionLogEntry]:
        """Build or update decision log from existing state"""
        
        if existing_state and "decisions" in existing_state:
            # Preserve existing decisions
            decisions_data = existing_state["decisions"]
            return [DecisionLogEntry(**entry) for entry in decisions_data]
        
        # Initialize with basic architectural decisions
        return [
            DecisionLogEntry(
                decision_id="use_tree_sitter_parsing",
                title="Use Tree-sitter for AST parsing",
                context="Need reliable cross-language AST parsing",
                decision="Adopt Tree-sitter for Python, JS/TS, Go, Rust parsing",
                rationale="Grammar-based parsing eliminates regex heuristics",
                consequences=["Reliable parsing", "Limited to supported languages"],
                alternatives_considered=["Regex-based parsing", "Language-specific parsers"]
            )
        ]
    
    
    def _extract_known_issues(self, repository: dict) -> List[Dict[str, Any]]:
        """Extract known issues from repository metadata"""
        
        known_issues = []
        
        # Add any repository-level issues
        if hasattr(repository, 'open_issues_count') and repository.open_issues_count > 0:
            known_issues.append({
                "type": "github_issues",
                "description": f"{repository.open_issues_count} open GitHub issues",
                "severity": "info",
                "attempted_solutions": []
            })
        
        return known_issues
    
    
    def _build_code_index(self, components: List[ComponentContract]) -> Dict[str, CodePointer]:
        """Build index of all code pointers from components"""
        
        code_index = {}
        
        for component in components:
            code_index[component.component_id] = component.code_pointer
        
        return code_index
    
    
    def _infer_component_type(self, file_path: str) -> ComponentType:
        """Infer component type from file path"""
        
        path_lower = file_path.lower()
        
        if "api" in path_lower or "router" in path_lower or "endpoint" in path_lower:
            return ComponentType.API_ENDPOINT
        elif "service" in path_lower:
            return ComponentType.SERVICE
        elif "model" in path_lower or "schema" in path_lower:
            return ComponentType.DATABASE_TABLE
        elif path_lower.endswith(".py") or path_lower.endswith(".js") or path_lower.endswith(".ts"):
            return ComponentType.MODULE
        else:
            return ComponentType.MODULE
    
    
    def _generate_component_id(self, file_path: str) -> str:
        """Generate unique component ID from file path"""
        
        # Remove extension and path separators, convert to snake_case
        name = Path(file_path).stem
        component_id = name.lower().replace("-", "_").replace(" ", "_")
        
        # Add hash suffix for uniqueness
        path_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        
        return f"{component_id}_{path_hash}"
    
    
    def _generate_component_name(self, file_path: str) -> str:
        """Generate human-readable component name from file path"""
        
        name = Path(file_path).stem
        
        # Convert to title case
        return name.replace("_", " ").replace("-", " ").title()
    
    
    async def seal_capsule(self, capsule: Capsule) -> str:
        """
        Seal a capsule for storage and transport.
        
        Returns:
            Serialized capsule JSON string
        """
        return capsule.model_dump_json(indent=2)
    
    
    async def break_open_capsule(self, capsule_json: str) -> Capsule:
        """
        Break open a sealed capsule from JSON.
        
        Args:
            capsule_json: Serialized capsule JSON
        
        Returns:
            Deserialized CAPSULE object
        """
        capsule_data = json.loads(capsule_json)
        return Capsule(**capsule_data)
    
    
    async def update_state_registry(self, capsule: Capsule, task_updates: List[Dict[str, Any]]) -> Capsule:
        """
        Update state registry with new task information.
        
        This is the key method for maintaining current project state.
        """
        
        # Update existing tasks or add new ones
        task_map = {entry.task_id: entry for entry in capsule.state_registry}
        
        for update in task_updates:
            task_id = update.get("task_id")
            if not task_id:
                continue
                
            if task_id in task_map:
                # Update existing task
                task = task_map[task_id]
                task.state = TaskState(update.get("state", task.state))
                task.current_attempt = update.get("current_attempt", task.current_attempt)
                task.last_attempt = update.get("last_attempt", task.last_attempt) 
                task.blockers = update.get("blockers", task.blockers)
                if "progress_notes" in update:
                    task.progress_notes.extend(update["progress_notes"])
                task.updated_at = datetime.utcnow()
            else:
                # Add new task
                new_task = StateRegistryEntry(
                    task_id=task_id,
                    task_description=update.get("task_description", ""),
                    state=TaskState(update.get("state", TaskState.STUBBED)),
                    current_attempt=update.get("current_attempt"),
                    last_attempt=update.get("last_attempt"),
                    blockers=update.get("blockers", []),
                    progress_notes=update.get("progress_notes", []),
                    related_components=update.get("related_components", [])
                )
                capsule.state_registry.append(new_task)
        
        # Update metadata
        capsule.metadata.updated_at = datetime.utcnow()
        capsule.metadata.total_tasks = len(capsule.state_registry)
        
        return capsule
