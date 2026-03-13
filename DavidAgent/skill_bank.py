#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill Bank with Namespace Management
Implements namespace-based skill storage and retrieval for DavidAgent.

Namespace format:
- Persona-specific: {persona_id}::{skill_name}::v{version}
- Global: global::skill_name::vX.X

Features:
1. Automatic namespace parsing for skill queries
2. Conflict prevention with clear error messages
3. Persona-filtered skill listing
4. Global skill promotion with authorization
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path


class SkillBank:
    """Manages skills with namespace support."""
    
    def __init__(self, digital_personas_path: str = "digital_personas.json"):
        """
        Initialize the SkillBank.
        
        Args:
            digital_personas_path: Path to the digital personas configuration file
        """
        self.digital_personas_path = digital_personas_path
        self.skills: Dict[str, Dict[str, Any]] = {}
        self._load_skills()
    
    def _load_skills(self):
        """Load skills from digital_personas.json into namespace format."""
        if not os.path.exists(self.digital_personas_path):
            return
        
        try:
            with open(self.digital_personas_path, 'r', encoding='utf-8') as f:
                personas = json.load(f)
            
            # Convert existing skills to namespace format
            for persona_id, persona_config in personas.items():
                if 'skills' in persona_config:
                    for skill_name, skill_data in persona_config['skills'].items():
                        version = skill_data.get('version', 'v1.0')
                        namespace = f"{persona_id}::{skill_name}::{version}"
                        self.skills[namespace] = {
                            'persona_id': persona_id,
                            'skill_name': skill_name,
                            'version': version,
                            'status': skill_data.get('status', 'incubating'),
                            'reward': skill_data.get('reward', 0.0),
                            'test_count': skill_data.get('test_count', 0),
                            'code': skill_data.get('code', ''),
                            'is_global': False
                        }
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Warning: Failed to load skills from {self.digital_personas_path}: {e}")
    
    def _parse_namespace(self, namespace: str) -> Tuple[str, str, str]:
        """
        Parse a namespace string into its components.
        
        Args:
            namespace: Namespace string in format {persona_id}::{skill_name}::v{version}
                      or global::skill_name::vX.X
            
        Returns:
            Tuple of (persona_id, skill_name, version)
            
        Raises:
            ValueError: If namespace format is invalid
        """
        parts = namespace.split('::')
        if len(parts) != 3:
            raise ValueError(f"Invalid namespace format: {namespace}. Expected format: persona::skill::vX.X or global::skill::vX.X")
        
        persona_id, skill_name, version = parts
        
        # Validate version format
        if not re.match(r'^v\d+\.\d+$', version):
            raise ValueError(f"Invalid version format: {version}. Expected format: vX.X")
        
        return persona_id, skill_name, version
    
    def _generate_namespace(self, persona_id: str, skill_name: str, version: str) -> str:
        """Generate a namespace string from components."""
        return f"{persona_id}::{skill_name}::{version}"
    
    def add_skill(self, persona_id: str, skill_name: str, version: str, 
                  skill_data: Dict[str, Any], force: bool = False) -> bool:
        """
        Add a new skill to the bank.
        
        Args:
            persona_id: ID of the persona owning the skill
            skill_name: Name of the skill
            version: Version of the skill (format: vX.X)
            skill_data: Skill data including code, status, etc.
            force: Whether to force overwrite (use with caution)
            
        Returns:
            True if skill was added successfully, False otherwise
            
        Raises:
            ValueError: If there's a conflict and force=False
        """
        namespace = self._generate_namespace(persona_id, skill_name, version)
        
        # Check for conflicts
        if namespace in self.skills and not force:
            existing_skill = self.skills[namespace]
            raise ValueError(
                f"Skill conflict detected! Namespace {namespace} already exists.\n"
                f"Existing skill owned by: {existing_skill['persona_id']}\n"
                f"Status: {existing_skill['status']}, Version: {existing_skill['version']}"
            )
        
        # Add the skill
        self.skills[namespace] = {
            'persona_id': persona_id,
            'skill_name': skill_name,
            'version': version,
            'status': skill_data.get('status', 'incubating'),
            'reward': skill_data.get('reward', 0.0),
            'test_count': skill_data.get('test_count', 0),
            'code': skill_data.get('code', ''),
            'is_global': False
        }
        
        return True
    
    def promote_to_global(self, namespace: str, owner_memory_manager) -> bool:
        """
        Promote a persona-specific skill to global status.
        
        Args:
            namespace: Namespace of the skill to promote
            owner_memory_manager: OwnerMemoryManager instance for authorization
            
        Returns:
            True if promotion was successful, False otherwise
        """
        if namespace not in self.skills:
            raise ValueError(f"Skill not found: {namespace}")
        
        skill = self.skills[namespace]
        if skill['is_global']:
            return True  # Already global
        
        # Check authorization
        if not owner_memory_manager.can_promote_to_global(skill):
            raise PermissionError(f"Insufficient permissions to promote {namespace} to global status")
        
        # Create global namespace
        global_namespace = f"global::{skill['skill_name']}::{skill['version']}"
        
        # Check if global version already exists
        if global_namespace in self.skills:
            existing_global = self.skills[global_namespace]
            if existing_global['version'] >= skill['version']:
                raise ValueError(
                    f"Global skill {global_namespace} already exists with same or higher version"
                )
        
        # Promote to global
        skill['is_global'] = True
        self.skills[global_namespace] = skill.copy()
        
        return True
    
    def get_skill(self, namespace: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a skill by its namespace.
        
        Args:
            namespace: Full namespace of the skill
            
        Returns:
            Skill data if found, None otherwise
        """
        return self.skills.get(namespace)
    
    def find_skills(self, persona_id: Optional[str] = None, 
                   skill_name: Optional[str] = None, 
                   status: Optional[str] = None) -> List[str]:
        """
        Find skills matching the given criteria.
        
        Args:
            persona_id: Filter by persona ID (None for all personas)
            skill_name: Filter by skill name (None for all skills)
            status: Filter by status (None for all statuses)
            
        Returns:
            List of matching namespace strings
        """
        matching_namespaces = []
        
        for namespace, skill in self.skills.items():
            # Skip global skills if filtering by specific persona
            if persona_id and skill['persona_id'] != persona_id and not skill['is_global']:
                continue
            
            # Skip if filtering by skill name and it doesn't match
            if skill_name and skill['skill_name'] != skill_name:
                continue
            
            # Skip if filtering by status and it doesn't match
            if status and skill['status'] != status:
                continue
            
            matching_namespaces.append(namespace)
        
        return matching_namespaces
    
    def list_skills_by_persona(self, persona_id: str) -> List[str]:
        """
        List all skills belonging to a specific persona.
        
        Args:
            persona_id: ID of the persona
            
        Returns:
            List of namespace strings for the persona's skills
        """
        return self.find_skills(persona_id=persona_id)
    
    def list_global_skills(self) -> List[str]:
        """List all global skills."""
        return [ns for ns, skill in self.skills.items() if skill['is_global']]
    
    def save_to_file(self, filepath: Optional[str] = None):
        """
        Save skills back to digital_personas.json format.
        
        Args:
            filepath: Path to save file (defaults to original digital_personas_path)
        """
        if filepath is None:
            filepath = self.digital_personas_path
        
        # Load existing personas
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                personas = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            personas = {}
        
        # Update skills in personas
        for namespace, skill in self.skills.items():
            if skill['is_global']:
                continue  # Skip global skills for now
            
            persona_id = skill['persona_id']
            if persona_id not in personas:
                personas[persona_id] = {'skills': {}}
            
            if 'skills' not in personas[persona_id]:
                personas[persona_id]['skills'] = {}
            
            personas[persona_id]['skills'][skill['skill_name']] = {
                'version': skill['version'],
                'status': skill['status'],
                'reward': skill['reward'],
                'test_count': skill['test_count'],
                'code': skill['code']
            }
        
        # Save back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(personas, f, indent=2, ensure_ascii=False)


class OwnerMemoryManager:
    """Manages authorization for global skill promotion."""
    
    def __init__(self, authorized_personas: List[str]):
        """
        Initialize with list of personas authorized to promote skills globally.
        
        Args:
            authorized_personas: List of persona IDs that can promote skills to global
        """
        self.authorized_personas = set(authorized_personas)
    
    def can_promote_to_global(self, skill: Dict[str, Any]) -> bool:
        """
        Check if a skill can be promoted to global status.
        
        Args:
            skill: Skill data dictionary
            
        Returns:
            True if promotion is allowed, False otherwise
        """
        return skill['persona_id'] in self.authorized_personas


# Example usage and testing
if __name__ == "__main__":
    # Initialize skill bank
    skill_bank = SkillBank()
    
    # Add some test skills
    test_skill_data = {
        'status': 'incubating',
        'reward': 2.7,
        'test_count': 2,
        'code': 'print("Hello from high_perf_lazy_loading!")'
    }
    
    try:
        skill_bank.add_skill(
            persona_id="data_officer",
            skill_name="high_perf_lazy_loading",
            version="v1.1",
            skill_data=test_skill_data
        )
        print("✓ Successfully added skill: data_officer::high_perf_lazy_loading::v1.1")
    except ValueError as e:
        print(f"✗ Failed to add skill: {e}")
    
    # Try to add the same skill again (should fail)
    try:
        skill_bank.add_skill(
            persona_id="data_officer",
            skill_name="high_perf_lazy_loading",
            version="v1.1",
            skill_data=test_skill_data
        )
        print("✗ Should have failed due to conflict!")
    except ValueError as e:
        print(f"✓ Correctly rejected duplicate skill: {e}")
    
    # Add a skill from a different persona with same name (should succeed)
    try:
        skill_bank.add_skill(
            persona_id="tech_enthusiast",
            skill_name="high_perf_lazy_loading",
            version="v1.0",
            skill_data={**test_skill_data, 'version': 'v1.0'}
        )
        print("✓ Successfully added skill from different persona with same name")
    except ValueError as e:
        print(f"✗ Failed to add skill from different persona: {e}")
    
    # List skills by persona
    data_officer_skills = skill_bank.list_skills_by_persona("data_officer")
    print(f"Data officer skills: {data_officer_skills}")
    
    tech_enthusiast_skills = skill_bank.list_skills_by_persona("tech_enthusiast")
    print(f"Tech enthusiast skills: {tech_enthusiast_skills}")
    
    # Test namespace parsing
    try:
        persona, skill, version = skill_bank._parse_namespace("data_officer::high_perf_lazy_loading::v1.1")
        print(f"✓ Parsed namespace: persona={persona}, skill={skill}, version={version}")
    except ValueError as e:
        print(f"✗ Failed to parse namespace: {e}")
    
    # Test invalid namespace
    try:
        skill_bank._parse_namespace("invalid::format")
        print("✗ Should have failed with invalid namespace!")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid namespace: {e}")