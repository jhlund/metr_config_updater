import setuptools
from metr_config_updater_version.version import CONFIG_RETRIEVAL_VERSION

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="metr_config_retrieval",
    version=CONFIG_RETRIEVAL_VERSION,
    author="Johan Lund",
    author_email="Johan.H.Lund@gmail.com",
    description="CLI Tool designed for automated update of config file on upstart",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=" ",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'metr_config_update=source.metr_config_updater:cli'
        ],
    },
    install_requires=['click'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Linux",
        "Development Status :: 4 - Beta",
        "Environment :: Console"
    ],
    python_requires='>=3.6'
)
