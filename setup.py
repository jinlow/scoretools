import setuptools

setuptools.setup(
    name="scoretools",
    version="0.0.1",
    author="James Inlow",
    author_email="james.d.inlow@gmail.com",
    description="Tools for testing the value of credit scores.",
    packages=setuptools.find_packages(),
    install_requires=["pandas", "numpy", "matplotlib", "xlsxwriter"],
    python_requires=">=3.6",
)
