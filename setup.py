from setuptools import setup, find_packages

setup(
    name="run_fast",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="跑得快纸牌游戏AI系统",
    long_description="跑得快纸牌游戏AI系统",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/run_fast",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 在这里添加项目依赖
    ],
    entry_points={
        "console_scripts": [
            "run_fast=main:main",
        ],
    },
)