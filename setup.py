from setuptools import setup, find_packages

setup(
    name="clinical_trial_pipeline",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",  
        "pymongo",   
        "openai",
        "langchain",
        "python-dotenv",
        "langchain-openai",
        "openai",
        "pytest",
        "pytest-mock"
    ],
    author="Taoufik Bourgana",
    author_email="taoufik.bourgana@gmail.com",
    description="A pipeline for processing clinical trial data",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown")