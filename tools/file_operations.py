"""
File Operation Tools for Resume Generation
WITH SAFETY RESTRICTIONS
"""
import os
import subprocess
from pathlib import Path
from typing import Optional
import shutil

# SAFETY: Define allowed directories
ALLOWED_READ_DIRS = [
    Path.home() / "job_descriptions",
    Path.home() / "Downloads",
    Path.home() / "Documents"
]

ALLOWED_WRITE_DIR = Path.home() / "resumes"
ALLOWED_WRITE_DIR.mkdir(exist_ok=True)  # Create if doesn't exist

class FileSafetyError(Exception):
    """Raised when file operation violates safety policy"""
    pass

class FileOperationTools:
    """
    File operations with strict safety controls
    
    Safety Rules:
    1. Can only READ from: ~/job_descriptions, ~/Downloads, ~/Documents
    2. Can only WRITE to: ~/resumes
    3. Cannot delete ANY files
    4. Cannot access system directories
    """
    
    def __init__(self):
        self.write_dir = ALLOWED_WRITE_DIR
        print(f"  📁 Resume output directory: {self.write_dir}")
    
    def read_file(self, filepath: str) -> str:
        """
        Read a file (with safety checks)
        
        Args:
            filepath: Path to file
            
        Returns:
            File contents
            
        Raises:
            FileSafetyError: If file is outside allowed directories
        """
        path = Path(filepath).expanduser().resolve()
        
        # Safety check: Must be in allowed read directories
        if not any(self._is_subpath(path, allowed_dir) for allowed_dir in ALLOWED_READ_DIRS):
            raise FileSafetyError(
                f"Cannot read from {path}. "
                f"Allowed directories: {[str(d) for d in ALLOWED_READ_DIRS]}"
            )
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        # Read and return
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def write_file(self, filename: str, content: str) -> str:
        """
        Write a file to ~/resumes (with safety checks)
        
        Args:
            filename: Name of file (no path, just filename)
            content: Content to write
            
        Returns:
            Full path to written file
            
        Raises:
            FileSafetyError: If trying to write outside ~/resumes
        """
        # Safety: Only allow filename, not paths
        if "/" in filename or "\\" in filename:
            raise FileSafetyError(
                f"Filename cannot contain path separators. "
                f"Use just the filename, it will be saved to {self.write_dir}"
            )
        
        # Construct full path (always in ~/resumes)
        filepath = self.write_dir / filename
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def compile_latex_to_pdf(self, tex_filename: str) -> str:
        """
        Compile LaTeX to PDF using pdflatex
        
        Args:
            tex_filename: Name of .tex file in ~/resumes
            
        Returns:
            Path to generated PDF
            
        Raises:
            FileSafetyError: If file not in ~/resumes
            RuntimeError: If compilation fails
        """
        tex_path = self.write_dir / tex_filename
        
        # Safety check
        if not tex_path.exists():
            raise FileNotFoundError(f"TeX file not found: {tex_path}")
        
        if not self._is_subpath(tex_path, self.write_dir):
            raise FileSafetyError(f"Can only compile files in {self.write_dir}")
        
        # Check pdflatex is installed
        if not shutil.which("pdflatex"):
            raise RuntimeError(
                "pdflatex not installed. Install with: sudo apt install texlive-latex-base"
            )
        
        # Compile (run twice for proper formatting)
        try:
            for i in range(2):
                result = subprocess.run(
                    ["pdflatex", "-interaction=nonstopmode", tex_filename],
                    cwd=self.write_dir,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0 and i == 1:  # Only error on second pass
                    # Extract error from log
                    log_file = self.write_dir / tex_filename.replace('.tex', '.log')
                    if log_file.exists():
                        with open(log_file) as f:
                            log = f.read()
                            # Find first error
                            for line in log.split('\n'):
                                if '!' in line:
                                    raise RuntimeError(f"LaTeX compilation error: {line}")
                    
                    raise RuntimeError(f"LaTeX compilation failed")
            
            # Clean up auxiliary files
            base_name = tex_filename.replace('.tex', '')
            for ext in ['.aux', '.log', '.out']:
                aux_file = self.write_dir / f"{base_name}{ext}"
                if aux_file.exists():
                    aux_file.unlink()
            
            pdf_path = self.write_dir / f"{base_name}.pdf"
            
            if not pdf_path.exists():
                raise RuntimeError("PDF not generated")
            
            return str(pdf_path)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("LaTeX compilation timed out")
    
    def _is_subpath(self, path: Path, parent: Path) -> bool:
        """Check if path is under parent directory"""
        try:
            path.resolve().relative_to(parent.resolve())
            return True
        except ValueError:
            return False
    
    def list_resumes(self) -> list:
        """List all resumes in output directory"""
        pdf_files = list(self.write_dir.glob("*.pdf"))
        return [f.name for f in sorted(pdf_files, key=lambda x: x.stat().st_mtime, reverse=True)]


# Function definitions for OpenAI function calling
def get_file_tools_definitions() -> list:
    """Get OpenAI function definitions for file tools"""
    return [
        {
            "type": "function",
            "function": {
                "name": "read_job_description",
                "description": "Read a job description file from ~/job_descriptions, ~/Downloads, or ~/Documents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Full path to job description file"
                        }
                    },
                    "required": ["filepath"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "generate_tailored_resume",
                "description": "Generate a tailored resume PDF based on a job description. Analyzes the job requirements and selects the 2 most relevant projects, then compiles to PDF.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "job_description": {
                            "type": "string",
                            "description": "The full job description text"
                        },
                        "company_name": {
                            "type": "string",
                            "description": "Name of company (for filename)"
                        },
                        "position_name": {
                            "type": "string",
                            "description": "Position title (for filename)"
                        }
                    },
                    "required": ["job_description", "company_name", "position_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_generated_resumes",
                "description": "List all previously generated resumes in the ~/resumes folder",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]


if __name__ == "__main__":
    # Test safety
    tools = FileOperationTools()
    
    print(f"Output directory: {tools.write_dir}")
    print(f"\nAllowed read directories:")
    for d in ALLOWED_READ_DIRS:
        print(f"  - {d}")
    
    # Test write
    print("\nTesting file write...")
    path = tools.write_file("test.txt", "Hello world!")
    print(f"  ✓ Wrote to: {path}")
    
    # Test safety violation
    print("\nTesting safety check...")
    try:
        tools.write_file("../etc/passwd", "malicious")
    except FileSafetyError as e:
        print(f"  ✓ Safety check worked: {e}")
