"""
World Grounding System - Basic Functionality Test

This script tests the core components of the World Grounding system
to ensure they can be imported and initialized correctly.
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all core modules can be imported."""
    print("Testing module imports...")
    
    try:
        from sensors.external_watcher import ExternalWatcher
        print("✅ ExternalWatcher imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ExternalWatcher: {e}")
        return False
        
    try:
        from sensors.embedding.ane_encoder import ANEEncoder
        print("✅ ANEEncoder imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ANEEncoder: {e}")
        return False
        
    try:
        from sensors.distiller.brain_balance import DualBrainDistiller
        print("✅ DualBrainDistiller imported successfully")
    except Exception as e:
        print(f"❌ Failed to import DualBrainDistiller: {e}")
        return False
        
    try:
        from sensors.sandbox.shadow_runner import ShadowSandbox
        print("✅ ShadowSandbox imported successfully")
    except Exception as e:
        print(f"❌ Failed to import ShadowSandbox: {e}")
        return False
        
    try:
        from sensors.cpep.align_broadcast import CPEPAlign
        print("✅ CPEPAlign imported successfully")
    except Exception as e:
        print(f"❌ Failed to import CPEPAlign: {e}")
        return False
        
    return True

def test_config_loading():
    """Test that configuration can be loaded."""
    print("\nTesting configuration loading...")
    
    try:
        import tomli
        config_path = "config/world_grounding.toml"
        if not os.path.exists(config_path):
            print("⚠️  Configuration file not found, creating default...")
            # Create default config for testing
            os.makedirs("config", exist_ok=True)
            with open(config_path, "w") as f:
                f.write("""
[system]
max_memory_mb = 2048
daily_bandwidth_limit_mb = 100
ane_enabled = false
background_only = false

[sources.github]
enabled = false

[sources.rss]  
enabled = false

[algorithms.curiosity_engine]
similarity_threshold = 0.6
embedding_model = "all-MiniLM-L6-v2"
""")
                
        from sensors.external_watcher import ExternalWatcher
        watcher = ExternalWatcher(config_path)
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False

def test_basic_initialization():
    """Test basic component initialization."""
    print("\nTesting basic component initialization...")
    
    try:
        # Test ANE Encoder (without ANE)
        from sensors.embedding.ane_encoder import ANEEncoder
        encoder_config = {"embedding_model": "all-MiniLM-L6-v2", "use_ane": False}
        encoder = ANEEncoder(encoder_config)
        print("✅ ANEEncoder initialized successfully")
        
        # Test Dual Brain Distiller
        from sensors.distiller.brain_balance import DualBrainDistiller
        distiller_config = {"confidence_threshold": 0.7, "min_content_length": 100}
        distiller = DualBrainDistiller(distiller_config)
        print("✅ DualBrainDistiller initialized successfully")
        
        # Test Shadow Sandbox (without Docker)
        from sensors.sandbox.shadow_runner import ShadowSandbox
        sandbox_config = {"max_test_cases": 5, "min_test_cases": 2, "timeout_seconds": 30}
        sandbox = ShadowSandbox(sandbox_config)
        print("✅ ShadowSandbox initialized successfully")
        
        # Test CPEP Align
        from sensors.cpep.align_broadcast import CPEPAlign
        cpep_config = {"avatar_types": ["tech_blogger"], "broadcast_delay_seconds": 1}
        cpep = CPEPAlign(cpep_config)
        print("✅ CPEPAlign initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize components: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running World Grounding System Basic Tests\n")
    
    success = True
    success &= test_imports()
    success &= test_config_loading()
    success &= test_basic_initialization()
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())