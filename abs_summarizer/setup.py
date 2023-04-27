import setuptools

with open('README.md', 'r') as f:
    long_description = f.read()
setuptools.setup(
    name = "abs_summarizer",
    version='0.0.1',
    author='Corrina Calanoc, Mia Mayerhofer, Madelyne Ventura, and Paul Wang',
    author_email='',
    description='ANLY 521 Final Project',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
)