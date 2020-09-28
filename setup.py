import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cilogger",
    version="0.1.2",
    author="Christophe Marteau",
    author_email="christophe.marteau@gmail.com",
    description="A colorized and indented logging extension",
    long_description="The cilogger module extends the python logging module to indent and color the logs and "
                     "provides a log level of type 'TRACE'. It also contains two decorators:\n"
                     "* A function decorator '@ftrace' that allows you to draw function calls with its arguments"
                     "* A class decorator '@ctrace' that lets you plot method and property calls",
    long_description_content_type="text/markdown",
    url="https://github.com/christophe-marteau/python-cilogger",
    packages=setuptools.find_packages(),
    install_requires=['ansicolors'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3",
        "Operating System :: Linux",
    ],
)
