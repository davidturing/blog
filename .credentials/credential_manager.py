#!/usr/bin/env python3
"""
Credential Manager for DavidAgent
Unified credential discovery and management across multiple sources
"""

import os
import json
from typing import Dict, Optional

class CredentialManager:
    """Unified credential manager with automatic discovery"""
    
    def __init__(self):
        self.credential_paths = [
            '.credentials/',           # Global credentials
            'DavidAgent/.env',         # DavidAgent credentials  
            '.env',                    # Project root credentials
        ]
        self._cache = {}
        self._loaded_credentials = None
    
    def _load_all_credentials(self) -> Dict:
        """Load credentials from all configured paths"""
        if self._loaded_credentials is not None:
            return self._loaded_credentials
            
        all_creds = {}
        
        # Load from .credentials directory
        if os.path.exists('.credentials/wordpress.env'):
            all_creds.update(self._parse_env_file('.credentials/wordpress.env'))
            
        if os.path.exists('.credentials/api_keys.env'):
            all_creds.update(self._parse_env_file('.credentials/api_keys.env'))
            
        # Load from DavidAgent
        if os.path.exists('DavidAgent/.env'):
            all_creds.update(self._parse_env_file('DavidAgent/.env'))
            
        # Load from project root
        if os.path.exists('.env'):
            all_creds.update(self._parse_env_file('.env'))
            
        self._loaded_credentials = all_creds
        return all_creds
    
    def _parse_env_file(self, filepath: str) -> Dict:
        """Parse .env file format"""
        creds = {}
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip("'\"")
                        creds[key] = value
        except Exception as e:
            print(f"Warning: Failed to parse {filepath}: {e}")
        return creds
    
    def get_credential(self, key: str) -> Optional[str]:
        """Get credential by key with caching"""
        if key in self._cache:
            return self._cache[key]
            
        all_creds = self._load_all_credentials()
        value = all_creds.get(key)
        if value:
            self._cache[key] = value
        return value
    
    def get_wordpress_credentials(self, target_site: str = "dvspace5") -> Dict:
        """Get WordPress credentials for specific site"""
        all_creds = self._load_all_credentials()
        
        if target_site == "datagov1":
            # 首席数据官数字分身凭据
            wp_creds = {
                'WP_SITE_URL': all_creds.get('WP_DATAGOV1_SITE_URL', 'https://datagov1.wordpress.com') + '/xmlrpc.php',
                'WP_USERNAME': all_creds.get('WP_DATAGOV1_USERNAME', 'davidturing'),
                'WP_APP_PASSWORD': all_creds.get('WP_APP_PASSWORD_DATAGOV1') or all_creds.get('WP_DATAGOV1_APP_PASSWORD')
            }
        else:
            # 科技达人数字分身凭据 (默认)
            wp_creds = {
                'WP_SITE_URL': all_creds.get('WP_DVSPACE5_SITE_URL', 'https://dvspace5.wordpress.com') + '/xmlrpc.php',
                'WP_USERNAME': all_creds.get('WP_DVSPACE5_USERNAME', 'davidturing'),
                'WP_APP_PASSWORD': all_creds.get('WP_APP_PASSWORD_DVSPACE5') or all_creds.get('WP_DVSPACE5_APP_PASSWORD')
            }
            
        return wp_creds
    
    def get_digital_persona_config(self, persona_name: str) -> Dict:
        """Get digital persona configuration"""
        try:
            with open('.credentials/digital_personas.json', 'r') as f:
                personas = json.load(f)
                return personas.get(persona_name, {})
        except Exception as e:
            print(f"Warning: Failed to load digital personas: {e}")
            return {}

# Global instance for easy access
credential_manager = CredentialManager()

if __name__ == "__main__":
    # Test the credential manager
    print("Testing Credential Manager...")
    print(f"WP Username: {credential_manager.get_credential('WP_USERNAME')}")
    print(f"Gemini API Key: {'set' if credential_manager.get_credential('GEMINI_API_KEY') else 'not set'}")
    print("WordPress credentials:", credential_manager.get_wordpress_credentials())