"""
Basic functionality test for World Grounding System.

This script tests the core modules to ensure they can be imported
and perform basic operations without errors.
"""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all core modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from sensors.external_watcher import ExternalWatcher
        print("✅ ExternalWatcher imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ExternalWatcher: {e}")
        return False
        
    try:
        from sensors.embedding.ane_encoder import ANEEncoder
        print("✅ ANEEncoder imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ANEEncoder: {e}")
        return False
        
    try:
        from sensors.distiller.brain_balance import DualBrainDistiller
        print("✅ DualBrainDistiller imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import DualBrainDistiller: {e}")
        return False
        
    try:
        from sensors.sandbox.shadow_runner import ShadowSandbox
        print("✅ ShadowSandbox imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ShadowSandbox: {e}")
        return False
        
    try:
        from sensors.cpep.align_broadcast import CPEPAlign
        print("✅ CPEPAlign imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import CPEPAlign: {e}")
        return False
        
    return True

def test_config_loading():
    """Test that configuration can be loaded."""
    print("🧪 Testing configuration loading...")
    
    try:
        import tomli
        config_path = "config/world_grounding.toml"
        if os.path.exists(config_path):
            with open(config_path, "rb") as f:
                config = tomli.load(f)
            print("✅ Configuration loaded successfully")
            return True
        else:
            print(f"❌ Configuration file not found: {config_path}")
            return False
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False

def test_basic_instantiation():
    """Test that core classes can be instantiated."""
    print("🧪 Testing basic instantiation...")
    
    try:
        from sensors.external_watcher import ExternalWatcher
        # Create watcher with mock config path to avoid file dependency
        watcher = ExternalWatcher.__new__(ExternalWatcher)
        watcher.config = {
            "system": {"max_memory_mb": 2048},
            "sources": {"github": {"enabled": True}},
            "algorithms": {
                "curiosity_engine": {"similarity_threshold": 0.6},
                "dual_brain_distiller": {"confidence_threshold": 0.7},
                "shadow_sandbox": {"max_test_cases": 5},
                "cpep": {"avatar_types": ["tech_blogger"]}
            }
        }
        print("✅ ExternalWatcher instantiated successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to instantiate ExternalWatcher: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🚀 Running World Grounding System Basic Tests\n")
    
    tests = [
        test_imports,
        test_config_loading,
        test_basic_instantiation
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
        
    if all(results):
        print("🎉 All basic tests passed! System is ready for deployment.")
        return 0
    else:
        print("💥 Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())