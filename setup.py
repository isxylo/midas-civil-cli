from setuptools import setup, find_namespace_packages

with open("cli_anything/midas_civil/README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cli-anything-midas-civil",
    version="1.0.0",
    description="CLI harness for MIDAS Civil NX structural engineering software",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="cli-anything",
    license="MIT",
    packages=find_namespace_packages(include=["cli_anything.*"]),
    # cli_anything/ has NO __init__.py (PEP 420 namespace package)
    install_requires=[
        "click>=8.0",
        "requests>=2.28",
    ],
    entry_points={
        "console_scripts": [
            "cli-anything-midas-civil=cli_anything.midas_civil.midas_civil_cli:main",
        ]
    },
    python_requires=">=3.10",
    keywords=["midas", "civil", "structural", "engineering", "cli", "automation"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering",
    ],
)
