"""
LaTeX Resume Template
"""

RESUME_TEMPLATE = r"""\documentclass[10pt,letterpaper]{article}  % Changed from 11pt to 10pt
\usepackage[margin=0.5in]{geometry}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{times}

% Remove page numbers
\pagenumbering{gobble}

% Section formatting (tighter)
\titleformat{\section}{\large\bfseries\uppercase}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{8pt}{4pt}  % Reduced from 10pt/6pt

% Subsection formatting
\titleformat{\subsection}[runin]{\bfseries\itshape}{}{0em}{}
\titlespacing{\subsection}{0pt}{4pt}{0pt}

% Tighter itemize spacing
\setlist[itemize]{leftmargin=*, nosep, topsep=2pt, after=\vspace{4pt}}

% Reduce space between paragraphs
\setlength{\parskip}{0pt}

\begin{document}

% Header (slightly smaller)
\begin{center}
{\Huge\textbf{Thiago Pari}} \\[3pt]  % Changed from \huge to \Large
Boston, MA $|$ 347-409-0333 $|$ parimaquera.t@northeastern.edu $|$
\href{https://linkedin.com/in/thiago-pari}{linkedin.com/in/thiago-pari} $|$ \href{https://thiago-pari.github.io/ThiagoPari}{thiago-pari.github.io/ThiagoPari}
\end{center}
\vspace{-6pt}  % Reduce space after header

\section{Education}

\noindent
%-----------------EDUCATION--------------
\textbf{Northeastern University} \hfill May 2027 \\
\textit{Master's, Robotics} \hfill GPA: 3.5
\begin{itemize}
    \item \textbf{Relevant Coursework:} Mobile Robotics, Robotics Sensing and Navigation, Machine Learning, Robot Mechanics and Control
\end{itemize}
\vspace{-4pt}

\noindent
\textbf{New York University} \hfill May 2025 \\
\textit{Bachelor's, Economics and Mathematics} \hfill GPA: 3.6
\begin{itemize}
    \item \textbf{Relevant Coursework:} Honors Analysis II, Differential Geometry, Numerical Analysis, Ordinary Differential Equations, Linear Algebra, Complex Analysis, Fourier Analysis Applied to Linear PDEs
\end{itemize}

%------------------SKILLS--------------------

\section{Skills}

\noindent
\textbf{Programming Languages:} C++, Python, MATLAB, C, SQL, Excel VBA \\
\textbf{Robotics \& Dynamics:} Multibody dynamics, Kinematic modeling, State estimation, Sensor fusion, ROS2, Git, GitHub \\
\textbf{Simulation \& Modeling:} Gazebo, Allan variance analysis, EKF, Control system design, Linux \\
\textbf{CAD \& Design:} SolidWorks, Autodesk Fusion \\
\textbf{Languages:} English, Spanish

\section{Projects}

%%% PROJECT 1 %%%
%%% PROJECT 2 %%%
%%% PROJECT 3 %%%

%----------------EXPERIENCE----------------------

\section{Professional Experience}

\noindent
\textbf{Citi} \hfill \textbf{New York, NY} \\
\textit{Summer Financial Analyst} \hfill June 2024 -- August 2024
\begin{itemize}
    \item Automated daily reporting workflows by developing Excel VBA macros, reducing processing time by 50\% and eliminating manual data collection errors
    \item Analyzed large datasets to identify non-compliance patterns, implementing systematic quality assurance reviews that reduced Core-IT non-compliance by 34\%
    \item Collaborated cross-functionally with risk management and legal teams to ensure data integrity and regulatory compliance
\end{itemize}
\vspace{-2pt}

\noindent
\textbf{New York University} \hfill \textbf{New York, NY} \\
\textit{Central Office Intern} \hfill January 2023 -- May 2024
\begin{itemize}
    \item Managed database operations for 100,000+ entries across Service Link and StarRez systems, ensuring data accuracy and system reliability
    \item Developed efficient workflows for processing student applications, improving response time and service quality for 10,000+ students
\end{itemize}

\end{document}
"""

def generate_project_latex(project_name: str, dates: str, location: str, bullets: list) -> str:
    """
    Generate LaTeX code for a project section
    
    Args:
        project_name: Name of project
        dates: Date range
        location: University/location
        bullets: List of bullet points
        
    Returns:
        LaTeX formatted project section
    """
    latex = f"    \\resumeProjectHeading\n"
    latex += f"      {{{project_name}}}{{{dates}}}\n"
    latex += f"      \\resumeItemListStart\n"
    
    for bullet in bullets:
        # Escape LaTeX special characters
        bullet_escaped = bullet.replace("%", "\\%").replace("&", "\\&").replace("#", "\\#")
        latex += f"        \\resumeItem{{{bullet_escaped}}}\n"
    
    latex += f"      \\resumeItemListEnd\n"
    
    return latex


def create_tailored_resume(project1_id: str, project2_id: str, 
                          project1_variant: str = "full", 
                          project2_variant: str = "full") -> str:
    """
    Create complete LaTeX resume with selected projects
    
    Args:
        project1_id: First project to include
        project2_id: Second project to include
        project1_variant: Which bullet point variant for project 1
        project2_variant: Which bullet point variant for project 2
        
    Returns:
        Complete LaTeX document as string
    """
    from data.projects_database import get_project_info
    
    # Get project info
    proj1 = get_project_info(project1_id, project1_variant)
    proj2 = get_project_info(project2_id, project2_variant)
    
    if not proj1 or not proj2:
        raise ValueError(f"Invalid project IDs: {project1_id}, {project2_id}")
    
    # Generate LaTeX for each project
    proj1_latex = generate_project_latex(
        proj1["name"], proj1["dates"], proj1["location"], proj1["bullets"]
    )
    
    proj2_latex = generate_project_latex(
        proj2["name"], proj2["dates"], proj2["location"], proj2["bullets"]
    )
    
    # Insert into template
    resume = RESUME_TEMPLATE.replace("%%PROJECT1%%", proj1_latex)
    resume = resume.replace("%%PROJECT2%%", proj2_latex)
    
    return resume


# Test
if __name__ == "__main__":
    resume = create_tailored_resume("wall-e", "ekf-localization")
    print(resume[:500])
    print("\n...\n")
    print(resume[-500:])
