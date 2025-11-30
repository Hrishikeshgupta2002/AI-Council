"""
Setup script for Agentic Council System.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="agentic-council",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A beautiful CLI-based multi-agent council system using Ollama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agentic-council",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "langchain>=0.3.0",
        "langchain-ollama>=0.1.0",
        "langchain-core>=0.3.0",
        "pydantic>=2.0.0",
        "rich>=13.7.0",
    ],
    entry_points={
        "console_scripts": [
            "agentic-council=agentic_council.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

