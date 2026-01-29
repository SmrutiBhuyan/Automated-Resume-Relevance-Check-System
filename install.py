"""
Installation script for Resume Evaluation System
Automates the setup process
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is too old. Need 3.8+")
        return False

def install_system_dependencies():
    """Install system dependencies based on OS"""
    print("🔧 Installing system dependencies...")
    
    system = platform.system().lower()
    
    if system == "linux":
        commands = [
            "sudo apt-get update",
            "sudo apt-get install -y python3-dev python3-pip postgresql postgresql-contrib redis-server",
        ]
    elif system == "darwin":  # macOS
        commands = [
            "brew install postgresql redis",
        ]
    elif system == "windows":
        print("⚠️  Windows detected. Please install PostgreSQL and Redis manually:")
        print("   - PostgreSQL: https://www.postgresql.org/download/windows/")
        print("   - Redis: https://github.com/microsoftarchive/redis/releases")
        return True
    else:
        print(f"⚠️  Unsupported OS: {system}")
        return True
    
    for command in commands:
        if not run_command(command, f"Running: {command}"):
            return False
    
    return True

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install requirements
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing Python packages"):
        return False
    
    return True

def install_spacy_model():
    """Install spaCy English model"""
    print("🧠 Installing spaCy English model...")
    
    if not run_command(f"{sys.executable} -m spacy download en_core_web_sm", "Installing spaCy model"):
        print("⚠️  spaCy model installation failed. You can install it later with:")
        print("   python -m spacy download en_core_web_sm")
        return False
    
    return True

def setup_environment():
    """Set up environment file"""
    print("⚙️  Setting up environment...")
    
    env_file = Path('.env')
    env_example = Path('env_example.txt')
    
    if not env_file.exists():
        if env_example.exists():
            print("📝 Creating .env file from template...")
            with open(env_example, 'r') as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created")
            print("⚠️  Please update .env with your actual configuration")
        else:
            print("❌ env_example.txt not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def setup_database():
    """Set up database"""
    print("🗄️  Setting up database...")
    
    # Check if PostgreSQL is running
    if not run_command("pg_isready", "Checking PostgreSQL"):
        print("⚠️  PostgreSQL is not running. Please start it manually:")
        print("   sudo systemctl start postgresql  # Linux")
        print("   brew services start postgresql   # macOS")
        return False
    
    # Run database setup
    if not run_command(f"{sys.executable} database_setup.py", "Setting up database tables"):
        print("⚠️  Database setup failed. You can run it manually later:")
        print("   python database_setup.py")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = ['uploads', 'uploads/resumes', 'uploads/job_descriptions', 'uploads/temp']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    return True

def run_tests():
    """Run system tests"""
    print("🧪 Running system tests...")
    
    if not run_command(f"{sys.executable} test_system.py", "Running tests"):
        print("⚠️  Some tests failed. Please check the output above")
        return False
    
    return True

def main():
    """Main installation function"""
    print("🚀 Resume Evaluation System - Installation")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Installation steps
    steps = [
        ("Installing system dependencies", install_system_dependencies),
        ("Installing Python dependencies", install_python_dependencies),
        ("Installing spaCy model", install_spacy_model),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Setting up database", setup_database),
        ("Running tests", run_tests),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Installation failed at: {step_name}")
            print("\nYou can try running individual steps manually.")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("\nNext steps:")
    print("1. Update your .env file with API keys and database credentials")
    print("2. Start Redis: redis-server")
    print("3. Start the system: python start_services.py")
    print("\nOr use Docker:")
    print("1. docker-compose up -d")
    print("\nAccess points:")
    print("- Dashboard: http://localhost:8501")
    print("- API: http://localhost:5000")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
