"""
Projects Database for Resume Tailoring
All your projects with variations for different job types
"""

PROJECTS_DATABASE = {
    "wall-e": {
        "name": "3D printed animatronic WALL-E Robot",
        "dates": "September 2025 – Present",
        "location": "Northeastern University, Boston, MA",
        "categories": ["robotics", "mechanical", "controls", "software", "cad"],
        "keywords": ["kinematics", "inverse kinematics", "servo control", "trajectory planning", 
                    "ros2", "gazebo", "solidworks", "c++", "6-dof", "motion planning"],
        "bullet_points": {
            "full": [
                "Designed kinematic chain model for 6-DOF robotic system with 250+ custom parts in SolidWorks, analyzing joint configurations and workspace constraints.",
                "Developed inverse kinematics solver in C++ for coordinated multi-axis servo control, implementing trajectory planning and smooth motion profiles.",
                "Built control system integrating position/velocity control modes for precise manipulator movements.",
                "Built ROS2 Gazebo simulation environment to validate inverse kinematics and trajectory planning."
            ],
            "mechanical_focus": [
                "Designed kinematic chain model for 6-DOF robotic system with 250+ custom parts in SolidWorks, analyzing joint configurations and workspace constraints.",
                "Developed inverse kinematics solver in C++ for coordinated multi-axis servo control, implementing trajectory planning and smooth motion profiles.",
                "Built control system integrating position/velocity control modes for precise manipulator movements."
            ],
            "software_focus": [
                "Developed inverse kinematics solver in C++ for coordinated multi-axis servo control, implementing trajectory planning and smooth motion profiles.",
                "Built ROS2 Gazebo simulation environment to validate inverse kinematics and trajectory planning.",
                "Implemented real-time servo control system with position and velocity feedback loops."
            ]
        }
    },
    
    "bundle-adjustment": {
        "name": "Convex Bundle Adjustment Robustness Analysis",
        "dates": "September 2025 – Present",
        "location": "Northeastern University, Boston, MA",
        "categories": ["computer-vision", "optimization", "3d-reconstruction", "research", "software"],
        "keywords": ["bundle adjustment", "convex optimization", "3d reconstruction", "colmap", 
                    "semidefinite programming", "c++", "cuda", "computer vision", "slam"],
        "bullet_points": {
            "full": [
                "Investigated robustness of XM convex bundle adjustment algorithm through systematic stress-testing across mathematical extremes (κ=10¹⁹), noise injection (10× signal), and visual degradation. Achieved 90%+ solver success rates.",
                "Built end-to-end 3D reconstruction pipeline integrating COLMAP, GLOMAP, monocular depth estimation, and C++/CUDA XM solver for semidefinite programming relaxations.",
                "Identified feature extraction as the critical pipeline bottleneck, demonstrating that real-world failures occur in upstream matching (5.7% retention under severe blur) rather than convex optimization."
            ],
            "research_focus": [
                "Investigated robustness of XM convex bundle adjustment algorithm through systematic stress-testing across mathematical extremes (κ=10¹⁹), noise injection (10× signal), and visual degradation. Achieved 90%+ solver success rates.",
                "Identified feature extraction as the critical pipeline bottleneck, demonstrating that real-world failures occur in upstream matching (5.7% retention under severe blur) rather than convex optimization.",
                "Analyzed algorithmic failure modes through quantitative metrics and visualization techniques."
            ],
            "software_focus": [
                "Built end-to-end 3D reconstruction pipeline integrating COLMAP, GLOMAP, monocular depth estimation, and C++/CUDA XM solver for semidefinite programming relaxations.",
                "Implemented high-performance computing solutions using C++ and CUDA for large-scale optimization problems.",
                "Developed automated testing framework for systematic robustness analysis across parameter spaces."
            ]
        }
    },
    
    "ekf-localization": {
        "name": "Multi-Sensor Fusion Localization for Mobile Robotics",
        "dates": "November 2025 – December 2025",
        "location": "Northeastern University, Boston, MA",
        "categories": ["robotics", "state-estimation", "sensor-fusion", "software", "controls"],
        "keywords": ["extended kalman filter", "sensor fusion", "ros2", "localization", "imu", 
                    "gps", "lidar", "odometry", "state estimation", "navigation"],
        "bullet_points": {
            "full": [
                "Implemented Extended Kalman Filter (EKF) and Unscented Kalman Filter (UKF) for real-time robot localization, achieving 28.8% error reduction compared to dead reckoning baseline.",
                "Integrated multi-sensor fusion combining wheel odometry, IMU heading, simulated GPS, and LiDAR scan matching for centimeter-level position accuracy.",
                "Developed robust ICP-based scan matching module with multi-resolution alignment and outlier rejection, processing point clouds in real-time.",
                "Built comprehensive ROS2 system with trajectory visualization, covariance analysis, and quantitative performance metrics for sensor fusion evaluation."
            ],
            "controls_focus": [
                "Implemented Extended Kalman Filter (EKF) and Unscented Kalman Filter (UKF) for real-time robot localization, achieving 28.8% error reduction compared to dead reckoning baseline.",
                "Integrated multi-sensor fusion combining wheel odometry, IMU heading, simulated GPS, and LiDAR scan matching for centimeter-level position accuracy.",
                "Designed state estimation system with covariance tracking and uncertainty quantification for robust navigation."
            ],
            "software_focus": [
                "Built comprehensive ROS2 system with trajectory visualization, covariance analysis, and quantitative performance metrics for sensor fusion evaluation.",
                "Developed robust ICP-based scan matching module with multi-resolution alignment and outlier rejection, processing point clouds in real-time.",
                "Implemented modular architecture supporting multiple filter types (EKF, UKF) with unified interface for algorithm comparison."
            ]
        }
    },
    
    "terrain-classifier": {
        "name": "Machine Learning-Based Terrain Classification",
        "dates": "December 2025",
        "location": "Northeastern University, Boston, MA",
        "categories": ["machine-learning", "robotics", "sensor-fusion", "software"],
        "keywords": ["machine learning", "svm", "imu", "sensor data", "classification", 
                    "feature extraction", "ros2", "real-time", "scikit-learn"],
        "bullet_points": {
            "full": [
                "Developed SVM-based terrain classifier achieving 100% test accuracy using IMU sensor data with 100 time and frequency domain features.",
                "Built real-time ROS2 system classifying terrain at 50Hz with LDA dimensionality reduction from 100 to 10 features.",
                "Created synthetic data generator producing realistic IMU signals for four terrain types (asphalt, grass, gravel, sand) with configurable noise models."
            ],
            "ml_focus": [
                "Developed SVM-based terrain classifier achieving 100% test accuracy using IMU sensor data with 100 time and frequency domain features.",
                "Implemented comprehensive feature extraction pipeline including statistical moments, FFT analysis, and signal processing techniques.",
                "Applied Linear Discriminant Analysis (LDA) for dimensionality reduction while preserving class separability."
            ]
        }
    },
    
    "quadruped-robot": {
        "name": "RoboFox Quadruped Robot with Adaptive Gait Control",
        "dates": "December 2025 – Present",
        "location": "Northeastern University, Boston, MA",
        "categories": ["robotics", "controls", "mechanical", "state-estimation", "software"],
        "keywords": ["quadruped", "gait generation", "inverse kinematics", "state estimation", 
                    "ros2", "ekf", "leg odometry", "trajectory planning", "servo control"],
        "bullet_points": {
            "full": [
                "Designed and built 12-DOF quadruped robot with custom mechanical CAD integrating Corona DS-843MG servos, Raspberry Pi 4, and BNO055 IMU sensor.",
                "Implemented kinematic walker with inverse/forward kinematics solvers and gait generation supporting trot, walk, and pace patterns.",
                "Developed EKF-based state estimation using leg odometry computed via manipulator Jacobian, replacing traditional wheel odometry for legged robots.",
                "Created modular ROS2 software architecture with separate packages for robot description (URDF), control, and state estimation."
            ],
            "mechanical_focus": [
                "Designed and built 12-DOF quadruped robot with custom mechanical CAD integrating Corona DS-843MG servos, Raspberry Pi 4, and BNO055 IMU sensor.",
                "Developed complete kinematic model with forward and inverse kinematics for workspace analysis and motion planning.",
                "Designed custom mounting solutions for electronics and sensors with integrated cable routing and weight distribution optimization."
            ],
            "controls_focus": [
                "Implemented kinematic walker with inverse/forward kinematics solvers and gait generation supporting trot, walk, and pace patterns.",
                "Developed EKF-based state estimation using leg odometry computed via manipulator Jacobian, replacing traditional wheel odometry for legged robots.",
                "Created trajectory planning system for smooth gait transitions and terrain adaptation."
            ],
            "software_focus": [
                "Created modular ROS2 software architecture with separate packages for robot description (URDF), control, and state estimation.",
                "Implemented real-time control loop processing at 50Hz with multi-threaded architecture for sensor fusion and motion control.",
                "Developed comprehensive testing framework with simulation validation in RViz2 before hardware deployment."
            ]
        }
    },
    
    "balloon-boy": {
        "name": "Balloon Boy AI-Powered Animatronic Desktop Assistant",
        "dates": "December 2025 – Present",
        "location": "Northeastern University, Boston, MA",
        "categories": ["robotics", "ai", "software", "mechanical", "embedded"],
        "keywords": ["animatronic", "computer vision", "face tracking", "ai agent", "esp32", 
                    "servo control", "embedded systems", "opencv", "llm", "natural language processing"],
        "bullet_points": {
            "full": [
                "Designed 14-inch animatronic with custom dual-axis eye mechanism controlled by four servos through spatial four-bar linkages for realistic eye tracking.",
                "Built AI agent system integrating GPT-4o with web search, calendar management, and conversational memory using vector databases.",
                "Developed embedded control architecture with ESP32-CAM for video streaming, Arduino Nano for servo control via I2C PWM driver, and laptop-based AI processing.",
                "Implemented real-time face tracking using OpenCV with smooth servo interpolation for natural eye contact during conversations."
            ],
            "ai_focus": [
                "Built AI agent system integrating GPT-4o with web search, calendar management, and conversational memory using vector databases.",
                "Implemented hybrid local/cloud architecture routing queries between local LLM (Gemma 2 9B) and cloud API based on complexity analysis.",
                "Developed agentic behavior with autonomous tool discovery and function calling for calendar, web search, and system integration."
            ],
            "embedded_focus": [
                "Developed embedded control architecture with ESP32-CAM for video streaming, Arduino Nano for servo control via I2C PWM driver, and laptop-based AI processing.",
                "Implemented I2S audio pipeline with INMP441 microphone and MAX98357A amplifier for voice interaction with real-time speech recognition.",
                "Designed power distribution system with buck converters and proper voltage regulation for multi-component electronics integration."
            ]
        }
    }
}

# Job type to project priority mapping
JOB_TYPE_PREFERENCES = {
    "mechatronics": ["wall-e", "quadruped-robot", "balloon-boy", "ekf-localization", "terrain-classifier"],
    "software": ["ekf-localization", "terrain-classifier", "quadruped-robot", "bundle-adjustment", "balloon-boy"],
    "controls": ["quadruped-robot", "ekf-localization", "wall-e", "terrain-classifier", "balloon-boy"],
    "computer-vision": ["bundle-adjustment", "balloon-boy", "wall-e", "ekf-localization", "terrain-classifier"],
    "machine-learning": ["terrain-classifier", "balloon-boy", "bundle-adjustment", "ekf-localization", "quadruped-robot"],
    "mechanical": ["wall-e", "quadruped-robot", "balloon-boy", "ekf-localization", "terrain-classifier"],
    "robotics-general": ["quadruped-robot", "wall-e", "ekf-localization", "terrain-classifier", "balloon-boy"]
}

def get_project_info(project_id: str, variant: str = "full") -> dict:
    """
    Get project information
    
    Args:
        project_id: Project identifier
        variant: Which bullet point variant to use
                 ("full", "mechanical_focus", "software_focus", etc.)
    
    Returns:
        Project information dict
    """
    project = PROJECTS_DATABASE.get(project_id)
    if not project:
        return None
    
    # Get appropriate bullet points
    bullets = project["bullet_points"].get(variant, project["bullet_points"]["full"])
    
    return {
        "name": project["name"],
        "dates": project["dates"],
        "location": project["location"],
        "bullets": bullets,
        "categories": project["categories"],
        "keywords": project["keywords"]
    }

def get_all_projects() -> dict:
    """Get all available projects"""
    return PROJECTS_DATABASE

def get_projects_for_job_type(job_type: str, count: int = 2) -> list:
    """
    Get recommended projects for a job type
    
    Args:
        job_type: Type of job (e.g., "mechatronics", "software", "controls")
        count: Number of projects to return
        
    Returns:
        List of project IDs in priority order
    """
    preferences = JOB_TYPE_PREFERENCES.get(job_type, JOB_TYPE_PREFERENCES["robotics-general"])
    return preferences[:count]
