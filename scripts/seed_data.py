"""
Seed sample data for testing
"""

import asyncio
import os
from pathlib import Path

# Sample text documents
SAMPLE_TEXTS = {
    "machine_learning.txt": """
    Machine Learning: A Comprehensive Overview
    
    Machine learning is a subset of artificial intelligence that enables systems to learn
    and improve from experience without being explicitly programmed. It focuses on the
    development of computer programs that can access data and use it to learn for themselves.
    
    Key Types of Machine Learning:
    
    1. Supervised Learning
       - Uses labeled training data
       - Examples: Classification, Regression
       - Common algorithms: Linear Regression, Decision Trees, Neural Networks
    
    2. Unsupervised Learning
       - Uses unlabeled data
       - Examples: Clustering, Dimensionality Reduction
       - Common algorithms: K-Means, PCA, Autoencoders
    
    3. Reinforcement Learning
       - Learns through interaction with environment
       - Examples: Game playing, Robotics
       - Common algorithms: Q-Learning, Policy Gradients
    
    Applications:
    - Natural Language Processing
    - Computer Vision
    - Recommendation Systems
    - Fraud Detection
    - Autonomous Vehicles
    """,
    
    "data_science.txt": """
    Data Science: Extracting Insights from Data
    
    Data science is an interdisciplinary field that uses scientific methods, processes,
    algorithms, and systems to extract knowledge and insights from structured and
    unstructured data.
    
    Core Components:
    
    1. Data Collection
       - Web scraping
       - APIs
       - Databases
       - Sensors
    
    2. Data Processing
       - Cleaning
       - Transformation
       - Feature engineering
    
    3. Data Analysis
       - Statistical analysis
       - Machine learning
       - Data mining
    
    4. Data Visualization
       - Charts and graphs
       - Dashboards
       - Interactive visualizations
    
    5. Communication
       - Reports
       - Presentations
       - Storytelling with data
    
    Popular Tools:
    - Python (Pandas, NumPy, Scikit-learn)
    - R (ggplot2, dplyr)
    - SQL
    - Tableau, Power BI
    - Jupyter Notebooks
    """,
    
    "cloud_computing.txt": """
    Cloud Computing: The Future of IT Infrastructure
    
    Cloud computing is the delivery of computing services—including servers, storage,
    databases, networking, software, analytics, and intelligence—over the Internet
    ("the cloud") to offer faster innovation, flexible resources, and economies of scale.
    
    Service Models:
    
    1. Infrastructure as a Service (IaaS)
       - Virtual machines
       - Storage
       - Networks
       - Examples: AWS EC2, Azure VMs, Google Compute Engine
    
    2. Platform as a Service (PaaS)
       - Development frameworks
       - Database management
       - Business analytics
       - Examples: Heroku, Google App Engine, Azure App Service
    
    3. Software as a Service (SaaS)
       - Email
       - Office software
       - CRM
       - Examples: Gmail, Microsoft 365, Salesforce
    
    Deployment Models:
    - Public Cloud
    - Private Cloud
    - Hybrid Cloud
    - Multi-Cloud
    
    Benefits:
    - Cost reduction
    - Scalability
    - Performance
    - Speed
    - Productivity
    - Reliability
    - Security
    """,
    
    "cybersecurity.txt": """
    Cybersecurity: Protecting Digital Assets
    
    Cybersecurity is the practice of protecting systems, networks, and programs from
    digital attacks. These cyberattacks are usually aimed at accessing, changing, or
    destroying sensitive information, extorting money from users, or interrupting
    normal business processes.
    
    Key Areas:
    
    1. Network Security
       - Firewalls
       - Intrusion detection systems
       - VPNs
       - Network segmentation
    
    2. Application Security
       - Secure coding practices
       - Vulnerability scanning
       - Penetration testing
       - Security patches
    
    3. Information Security
       - Data encryption
       - Access controls
       - Data loss prevention
       - Backup and recovery
    
    4. Operational Security
       - Risk assessment
       - Security policies
       - Incident response
       - Security training
    
    5. Disaster Recovery
       - Business continuity planning
       - Backup strategies
       - Recovery procedures
    
    Common Threats:
    - Malware
    - Phishing
    - Ransomware
    - Social engineering
    - DDoS attacks
    - Zero-day exploits
    
    Best Practices:
    - Strong passwords and MFA
    - Regular updates and patches
    - Employee training
    - Data backups
    - Least privilege access
    - Security monitoring
    """,
    
    "blockchain.txt": """
    Blockchain: Distributed Ledger Technology
    
    Blockchain is a distributed database or ledger that is shared among the nodes of
    a computer network. It stores information electronically in digital format and is
    best known for its crucial role in cryptocurrency systems.
    
    Key Characteristics:
    
    1. Decentralization
       - No central authority
       - Distributed network
       - Peer-to-peer transactions
    
    2. Transparency
       - Public ledger
       - Traceable transactions
       - Auditability
    
    3. Immutability
       - Cannot be altered
       - Cryptographic hashing
       - Chain of blocks
    
    4. Consensus Mechanisms
       - Proof of Work (PoW)
       - Proof of Stake (PoS)
       - Practical Byzantine Fault Tolerance
    
    Use Cases:
    
    - Cryptocurrency (Bitcoin, Ethereum)
    - Smart Contracts
    - Supply Chain Management
    - Healthcare Records
    - Voting Systems
    - Digital Identity
    - Real Estate
    - Intellectual Property
    
    Benefits:
    - Enhanced security
    - Reduced costs
    - Improved traceability
    - Increased efficiency
    - Greater transparency
    
    Challenges:
    - Scalability
    - Energy consumption
    - Regulatory uncertainty
    - Integration complexity
    """
}


def create_sample_files():
    """Create sample data files"""
    
    # Create directories
    base_path = Path("samples")
    text_path = base_path / "text"
    images_path = base_path / "images"
    pdfs_path = base_path / "pdfs"
    
    text_path.mkdir(parents=True, exist_ok=True)
    images_path.mkdir(parents=True, exist_ok=True)
    pdfs_path.mkdir(parents=True, exist_ok=True)
    
    print("📁 Creating sample data directories...")
    
    # Create text files
    print("📝 Creating text documents...")
    for filename, content in SAMPLE_TEXTS.items():
        file_path = text_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"   ✅ Created: {filename}")
    
    print("\n✅ Sample data created successfully!")
    print(f"\n📂 Sample files location:")
    print(f"   Text: {text_path.absolute()}")
    print(f"   Images: {images_path.absolute()} (add your own images here)")
    print(f"   PDFs: {pdfs_path.absolute()} (add your own PDFs here)")
    print(f"\n💡 Add your own images and PDFs to the respective directories")
    print(f"   for a complete demo.")


if __name__ == "__main__":
    create_sample_files()
