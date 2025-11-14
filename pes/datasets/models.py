"""
Data models for dataset management.

This module defines the core data structures used throughout the dataset
management system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class Requirement:
    """Represents a single requirement from a dataset."""
    
    req_id: str
    """Unique identifier for the requirement (e.g., 'F-GES-01', 'RQ4')"""
    
    file_path: Path
    """Path to the requirement file"""
    
    content: str
    """Full text content of the requirement"""
    
    language: str
    """Language of the requirement (e.g., 'italian', 'english')"""
    
    metadata: Dict = field(default_factory=dict)
    """Additional metadata parsed from the requirement file"""
    
    def __repr__(self):
        return f"Requirement(req_id='{self.req_id}', language='{self.language}')"


@dataclass
class SourceFile:
    """Represents a source code file from a dataset."""
    
    file_name: str
    """Name of the source file (e.g., 'ModificaStanze.java')"""
    
    file_path: Path
    """Full path to the source file"""
    
    _content: Optional[str] = field(default=None, repr=False)
    """Cached content of the source file (lazy-loaded)"""
    
    @property
    def content(self) -> str:
        """Get the content of the source file (lazy-loaded)."""
        if self._content is None:
            with open(self.file_path, 'r', encoding='utf-8', errors='replace') as f:
                self._content = f.read()
        return self._content
    
    @property
    def extension(self) -> str:
        """Get the file extension."""
        return self.file_path.suffix
    
    def __repr__(self):
        return f"SourceFile(file_name='{self.file_name}')"


@dataclass
class TraceabilityLink:
    """Represents a traceability link between a requirement and source files."""
    
    source_id: str
    """Source requirement ID"""
    
    target_files: List[str]
    """List of target file names"""
    
    link_type: str = "Rq→Src"
    """Type of traceability link (e.g., 'Rq→Src', 'Rq→Test', 'UC→Src')"""
    
    def __repr__(self):
        file_count = len(self.target_files)
        return f"TraceabilityLink(source='{self.source_id}', targets={file_count} files)"


@dataclass
class Dataset:
    """Represents a complete COMET dataset."""
    
    name: str
    """Dataset name (e.g., 'Albergate', 'LibEST')"""
    
    base_path: Path
    """Base directory path for the dataset"""
    
    language: str
    """Primary language of requirements (e.g., 'italian', 'english')"""
    
    requirements: Dict[str, Requirement] = field(default_factory=dict)
    """Dictionary mapping requirement IDs to Requirement objects"""
    
    source_files: Dict[str, SourceFile] = field(default_factory=dict)
    """Dictionary mapping file names to SourceFile objects"""
    
    traceability_links: List[TraceabilityLink] = field(default_factory=list)
    """List of all traceability links in the dataset"""
    
    metadata: Dict = field(default_factory=dict)
    """Additional dataset metadata"""
    
    def __repr__(self):
        req_count = len(self.requirements)
        src_count = len(self.source_files)
        link_count = len(self.traceability_links)
        return (f"Dataset(name='{self.name}', requirements={req_count}, "
                f"source_files={src_count}, links={link_count})")
    
    def get_links_for_requirement(self, req_id: str) -> List[TraceabilityLink]:
        """Get all traceability links for a specific requirement."""
        return [link for link in self.traceability_links 
                if link.source_id == req_id or link.source_id == f"{req_id}.txt"]


@dataclass
class TraceabilityBundle:
    """
    A bundle containing a requirement and its linked source files.
    
    This is the primary data structure used when passing context to LLMs.
    """
    
    requirement: Requirement
    """The requirement at the center of this bundle"""
    
    linked_files: List[SourceFile]
    """Source files linked to this requirement"""
    
    token_count: int
    """Estimated total token count for the bundle"""
    
    truncated: bool = False
    """Whether the bundle was truncated to fit token budget"""
    
    metadata: Dict = field(default_factory=dict)
    """Additional bundle metadata"""
    
    def __repr__(self):
        file_count = len(self.linked_files)
        trunc = " [TRUNCATED]" if self.truncated else ""
        return (f"TraceabilityBundle(req='{self.requirement.req_id}', "
                f"files={file_count}, tokens={self.token_count}{trunc})")
