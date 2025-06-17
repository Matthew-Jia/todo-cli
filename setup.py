from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="todo-cli",
    version="1.1.0",
    author="Matthew Jia",
    author_email="your.email@example.com",
    description="A simple, beautiful command-line todo application for developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Matthew-Jia/todo-cli",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "click>=8.0.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "todo=todo.cli:cli",
        ],
    },
)
