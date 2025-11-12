from setuptools import setup, find_packages

setup(
    name="hyperbion-tripolar",
    version="1.0.0",
    author="Sebastian Klemm",
    description="Hyperbion Tripolar Neural Network with Gabriel Cells and Multi-Wormhole Operators",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "networkx>=3.2",
        "matplotlib>=3.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
)
