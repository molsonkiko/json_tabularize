from setuptools import setup
import os


with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), "README.md")) as f:
    readme = f.read()

setup(
    name="json_tabularize",
    version="1.0.3",  # change this every time I release a new version
    packages=[
        "json_tabularize",
    ],
    package_dir={"json_tabularize": 'src'},
    package_data={
    },
    include_package_data=True,
    install_requires=[
        "genson",
    ],
    extras_require={
    },
    description="Get deeply nested JSON into tabular format",
    long_description=readme,
    long_description_content_type="text/markdown",
    license="MIT/X",
    author="Mark Johnston Olson",
    author_email="mjolsonsfca@gmail.com",
    url="https://github.com/molsonkiko/json_tabularize",
    # scripts=[ # maybe __main__ should be considered a script?
    # ],
    keywords=[
        "json",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
)
