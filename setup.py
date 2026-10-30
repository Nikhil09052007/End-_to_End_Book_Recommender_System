from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# edit below setup() function as per your project
REPO_NAME = "books_recommender_system"
AUTHOR_USER_NAME = "Nikhil Pandey"
SRC_REPO = "books_recommender_system"
AUTHOR_EMAIL = "pandeynikhil0905@gmail.com"
LIST_OF_REQUIREMENTS = [
    "scikit-learn",
    "pandas",
    "numpy",
    "PyYAML",
    "scipy",
    "streamlit",
    "six",
]



setup(
    name=SRC_REPO,
    version="0.0.1",
    author=AUTHOR_USER_NAME,
    description="A small local packages for ML based books recommendations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Nikhil09052007/End-_to_End_Book_Recommender_System",
    author_email=AUTHOR_EMAIL,
    packages=find_packages(),
    license="MIT",
    python_requires=">=3.7",
    install_requires=LIST_OF_REQUIREMENTS
)
