from setuptools import setup, find_namespace_packages

setup(
    name="prettyppt",
    version="0.1.0",
    description="Universal AI-Agent Presentation Toolkit: 80+ Aesthetic Templates & Multi-Scenario Prompts",
    author="PrettyPPT Team",
    packages=find_namespace_packages(include=["prettyppt*"]),
    package_data={"prettyppt": ["viewers/*.html"]},
    include_package_data=True,
    install_requires=[
        "python-pptx>=0.6.21",
        "jinja2>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "prettyppt=prettyppt.cli:main",
        ],
    },
    python_requires=">=3.8",
)
