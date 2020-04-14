import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tasmotadevicecontroller",
    version="0.0.8",
    author="chaptergy",
    description="Control Tasmota devices via their web api",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chaptergy/tasmota-device-controller",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
