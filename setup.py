import setuptools
setuptools.setup(
    name="ekans",
    version="0.0.1",
    author="Scott Kirklin",
    author_email="scott.kirklin@gmail.com",
    description="A curses snake game.",
    long_description_content_type="text/markdown",
    url="https://github.com/skirklin/ekans",
    project_urls={
        "Bug Tracker": "https://github.com/skirklin/ekans/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=["scripts/ekans"],
    python_requires=">=3.6",

)