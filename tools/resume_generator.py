"""
Resume Generation System
Analyzes job descriptions and creates tailored resumes
"""
from pathlib import Path
from typing import Dict, List, Tuple
import re

from data.projects_database import PROJECTS_DATABASE, get_project_info
from templates.resume_latex import create_tailored_resume
from tools.file_operations import FileOperationTools

class ResumeGenerator:
    """
    Analyzes job descriptions and generates tailored resumes
    """
    
    def __init__(self):
        self.file_ops = FileOperationTools()
        self.projects = PROJECTS_DATABASE
    
    def analyze_job_description(self, job_text: str) -> Dict:
        """
        Analyze job description to determine focus areas
        
        Returns:
            {
                "primary_focus": "mechatronics" | "software" | "controls" | etc,
                "keywords_found": [...],
                "recommended_projects": [...],
                "reasoning": "..."
            }
        """
        job_lower = job_text.lower()
        
        # Score each project based on keyword matches
        project_scores = {}
        keyword_matches = {}
        
        for project_id, project in self.projects.items():
            score = 0
            matches = []
            
            # Check each keyword
            for keyword in project["keywords"]:
                if keyword.lower() in job_lower:
                    score += 1
                    matches.append(keyword)
            
            # Boost score for category matches in job title/description
            for category in project["categories"]:
                if category.lower() in job_lower:
                    score += 2
                    matches.append(f"category:{category}")
            
            project_scores[project_id] = score
            keyword_matches[project_id] = matches
        
        # Sort projects by score
        ranked_projects = sorted(
            project_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        # Determine primary focus based on keywords
        focus_keywords = {
            "mechatronics": ["mechatronics", "mechanical", "electrical", "servo", "motor", "actuator"],
            "software": ["software", "programming", "python", "c++", "ros", "algorithm"],
            "controls": ["control", "pid", "feedback", "trajectory", "motion planning", "kalman"],
            "computer-vision": ["vision", "opencv", "image", "camera", "perception", "3d reconstruction"],
            "machine-learning": ["machine learning", "ml", "ai", "neural", "classification", "deep learning"],
            "state-estimation": ["localization", "slam", "odometry", "sensor fusion", "kalman", "state estimation"]
        }
        
        focus_scores = {}
        for focus, keywords in focus_keywords.items():
            focus_scores[focus] = sum(1 for kw in keywords if kw in job_lower)
        
        primary_focus = max(focus_scores, key=focus_scores.get)
        
        # Get top 2 projects
        top_2_projects = [p[0] for p in ranked_projects[:2]]
        
        return {
            "primary_focus": primary_focus,
            "project_scores": project_scores,
            "keyword_matches": keyword_matches,
            "recommended_projects": top_2_projects,
            "reasoning": self._explain_selection(top_2_projects, keyword_matches, primary_focus)
        }
    
    def _explain_selection(self, projects: List[str], matches: Dict, focus: str) -> str:
        """Generate human-readable explanation of project selection"""
        explanation = f"Based on job analysis (primary focus: {focus}):\n\n"
        
        for i, proj_id in enumerate(projects, 1):
            proj_name = self.projects[proj_id]["name"]
            proj_matches = matches[proj_id]
            explanation += f"{i}. {proj_name}\n"
            explanation += f"   Matched keywords: {', '.join(proj_matches[:5])}\n"
            explanation += f"   Match score: {len(proj_matches)}\n\n"
        
        return explanation
    
    def generate_resume(
        self,
        job_description: str,
        company_name: str,
        position_name: str
    ) -> Dict:
        """
        Main resume generation function
        
        Args:
            job_description: Full job description text
            company_name: Company name (for filename)
            position_name: Position title (for filename)
            
        Returns:
            {
                "pdf_path": "path/to/resume.pdf",
                "analysis": {...},
                "projects_used": [...],
                "status": "success"
            }
        """
        # Step 1: Analyze job description
        print("\n  📊 Analyzing job description...")
        analysis = self.analyze_job_description(job_description)
        
        print(f"    Primary focus: {analysis['primary_focus']}")
        print(f"    Recommended projects: {analysis['recommended_projects']}")
        
        # Step 2: Select projects and variants
        project1_id = analysis['recommended_projects'][0]
        project2_id = analysis['recommended_projects'][1]
        
        # Determine which bullet variant to use based on focus
        variant_map = {
            "mechatronics": "mechanical_focus",
            "software": "software_focus",
            "controls": "controls_focus",
            "computer-vision": "software_focus",
            "machine-learning": "ml_focus",
            "state-estimation": "controls_focus"
        }
        
        variant = variant_map.get(analysis['primary_focus'], "full")
        
        # Check if projects have this variant, fallback to full
        proj1 = get_project_info(project1_id, "full")
        if variant in proj1.get("bullet_points", {}).get("bullet_points", {}):
            variant1 = variant
        else:
            variant1 = "full"
        
        variant2 = variant1  # Use same variant for both
        
        print(f"    Using bullet variant: {variant1}")
        
        # Step 3: Generate LaTeX
        print("  📝 Generating LaTeX...")
        latex_content = create_tailored_resume(project1_id, project2_id, variant1, variant2)
        
        # Step 4: Create filename
        # Sanitize company and position names for filename
        safe_company = re.sub(r'[^\w\s-]', '', company_name).strip().replace(' ', '_')
        safe_position = re.sub(r'[^\w\s-]', '', position_name).strip().replace(' ', '_')
        
        tex_filename = f"Resume_{safe_company}_{safe_position}.tex"
        pdf_filename = f"Resume_{safe_company}_{safe_position}.pdf"
        
        # Step 5: Write LaTeX file
        print(f"  💾 Writing {tex_filename}...")
        tex_path = self.file_ops.write_file(tex_filename, latex_content)
        
        # Step 6: Compile to PDF
        print(f"  🔨 Compiling to PDF...")
        try:
            pdf_path = self.file_ops.compile_latex_to_pdf(tex_filename)
            print(f"  ✅ Resume generated: {pdf_path}")
            
            return {
                "pdf_path": pdf_path,
                "tex_path": tex_path,
                "analysis": analysis,
                "projects_used": [project1_id, project2_id],
                "variants": [variant1, variant2],
                "status": "success"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "tex_path": tex_path,
                "status": "failed",
                "message": "LaTeX file created but PDF compilation failed. Check if pdflatex is installed."
            }
    
    def generate_from_file(self, job_file_path: str, company_name: str, position_name: str) -> Dict:
        """
        Generate resume from a job description file
        
        Args:
            job_file_path: Path to job description file
            company_name: Company name
            position_name: Position title
            
        Returns:
            Result dict from generate_resume
        """
        # Read job description
        print(f"  📄 Reading job description from {job_file_path}...")
        job_text = self.file_ops.read_file(job_file_path)
        
        # Generate resume
        return self.generate_resume(job_text, company_name, position_name)


# Example usage
if __name__ == "__main__":
    generator = ResumeGenerator()
    
    # Test with sample job description
    sample_job = """
    Robotics Software Engineer
    
    We are seeking a Robotics Software Engineer to join our team.
    
    Requirements:
    - Experience with ROS2 and Gazebo simulation
    - Strong C++ and Python programming skills
    - Knowledge of state estimation and sensor fusion
    - Experience with Extended Kalman Filters
    - Familiarity with SLAM and localization algorithms
    
    Preferred:
    - Experience with quadruped or mobile robots
    - Knowledge of inverse kinematics
    - Computer vision experience
    """
    
    result = generator.generate_resume(
        job_description=sample_job,
        company_name="Boston Dynamics",
        position_name="Robotics_Software_Engineer"
    )
    
    print(f"\n📋 Result:")
    print(f"  Status: {result['status']}")
    if result['status'] == 'success':
        print(f"  PDF: {result['pdf_path']}")
        print(f"  Projects: {result['projects_used']}")
    else:
        print(f"  Error: {result.get('error')}")
