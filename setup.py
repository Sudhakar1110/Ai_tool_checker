from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="ai_tool_checker",
    version="1.0.0",
    description="AI Tool Discovery & Industry Compatibility Checker for ERPNext v15+",
    author="Your Organization",
    author_email="dev@yourorg.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
