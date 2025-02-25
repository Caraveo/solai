from setuptools import setup, find_packages
import os

# Read README.md if it exists
long_description = 'A CLI assistant powered by OpenAI'

setup(
    name="solai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        'click',
        'python-dotenv',
        'openai',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'sol=solai.app:main',
        ],
    },
    author="Your Name",
    author_email="jon@ziavision.com",
    description="A CLI assistant powered by OpenAI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/caraveo/solai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 