"""
Startup script for Resume Evaluation System
Starts all required services
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent
        
    def start_redis(self):
        """Start Redis server"""
        print("🔄 Starting Redis server...")
        try:
            # Try to start Redis
            process = subprocess.Popen(
                ['redis-server'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(('redis', process))
            print("✅ Redis server started")
            time.sleep(2)  # Give Redis time to start
        except FileNotFoundError:
            print("❌ Redis not found. Please install Redis and ensure it's in your PATH")
            return False
        return True
    
    def start_celery_worker(self):
        """Start Celery worker"""
        print("🔄 Starting Celery worker...")
        try:
            process = subprocess.Popen(
                [sys.executable, '-m', 'celery', '-A', 'tasks', 'worker', '--loglevel=info'],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(('celery', process))
            print("✅ Celery worker started")
            time.sleep(3)  # Give Celery time to start
        except Exception as e:
            print(f"❌ Failed to start Celery worker: {e}")
            return False
        return True
    
    def start_flask_app(self):
        """Start Flask application"""
        print("🔄 Starting Flask application...")
        try:
            process = subprocess.Popen(
                [sys.executable, 'app.py'],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(('flask', process))
            print("✅ Flask application started on http://localhost:5000")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Failed to start Flask app: {e}")
            return False
        return True
    
    def start_streamlit(self):
        """Start Streamlit dashboard"""
        print("🔄 Starting Streamlit dashboard...")
        try:
            process = subprocess.Popen(
                [sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py'],
                cwd=self.base_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(('streamlit', process))
            print("✅ Streamlit dashboard started on http://localhost:8501")
            time.sleep(3)
        except Exception as e:
            print(f"❌ Failed to start Streamlit: {e}")
            return False
        return True
    
    def check_dependencies(self):
        """Check if all required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = [
            'flask', 'celery', 'redis', 'streamlit', 'openai',
            'sentence-transformers', 'spacy', 'pymupdf', 'python-docx'
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Please install them using: pip install -r requirements.txt")
            return False
        
        print("✅ All dependencies found")
        return True
    
    def setup_environment(self):
        """Set up environment variables"""
        print("🔧 Setting up environment...")
        
        env_file = self.base_dir / '.env'
        if not env_file.exists():
            print("⚠️  .env file not found. Creating from template...")
            env_example = self.base_dir / 'env_example.txt'
            if env_example.exists():
                with open(env_example, 'r') as f:
                    content = f.read()
                with open(env_file, 'w') as f:
                    f.write(content)
                print("✅ .env file created. Please update with your configuration.")
            else:
                print("❌ env_example.txt not found")
                return False
        
        print("✅ Environment setup complete")
        return True
    
    def start_all_services(self):
        """Start all services"""
        print("🚀 Starting Resume Evaluation System...")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Start services
        services = [
            self.start_redis,
            self.start_celery_worker,
            self.start_flask_app,
            self.start_streamlit
        ]
        
        for service in services:
            if not service():
                print("❌ Failed to start all services")
                self.stop_all_services()
                return False
        
        print("=" * 50)
        print("🎉 All services started successfully!")
        print("\nAccess points:")
        print("📊 Dashboard: http://localhost:8501")
        print("🔗 API: http://localhost:5000")
        print("\nPress Ctrl+C to stop all services")
        
        return True
    
    def stop_all_services(self):
        """Stop all running services"""
        print("\n🛑 Stopping all services...")
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️  {name} force stopped")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        self.processes.clear()
        print("✅ All services stopped")
    
    def run(self):
        """Main run method"""
        try:
            if self.start_all_services():
                # Keep running until interrupted
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            self.stop_all_services()
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            self.stop_all_services()

def main():
    """Main function"""
    manager = ServiceManager()
    manager.run()

if __name__ == "__main__":
    main()
