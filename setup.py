"""
Quick setup and test script for the Meraki CLI tool.
"""
import os
import shutil

def setup_environment():
    """Set up the environment configuration."""
    env_example = ".env.example"
    env_file = ".env"
    
    if os.path.exists(env_example) and not os.path.exists(env_file):
        print("📋 Copying .env.example to .env...")
        shutil.copy(env_example, env_file)
        print("✅ Environment file created!")
        print("📝 Edit .env file with your actual Meraki API key if needed")
    elif os.path.exists(env_file):
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.example found")
    
    print("\n🔧 Configuration:")
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key = line.split('=')[0]
                    if 'API_KEY' in key:
                        print(f"   {key}=***[HIDDEN]***")
                    else:
                        print(f"   {line.strip()}")

def main():
    """Main setup function."""
    print("🚀 Meraki CLI Tool Setup")
    print("=" * 50)
    
    setup_environment()
    
    print("\n📋 Next Steps:")
    print("1. Verify your API key in .env file")
    print("2. Test SSL connectivity: cd src && python main.py --test-ssl")
    print("3. Run debug mode: cd src && python main.py --debug")
    print("4. Access web interface at: http://localhost:10000")

if __name__ == "__main__":
    main()
