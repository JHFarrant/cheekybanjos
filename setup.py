import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cheeky-nandos",
    version="0.0.1",
    author="JHFarrant",
    author_email="JHFarrant@gmail.com",
    description="A python API client for the nandos delivery api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/JHFarrant/cheeky-nandos",
    packages=setuptools.find_packages(),
    python_requires='~=3',
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)