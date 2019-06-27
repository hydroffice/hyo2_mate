import codecs
import os
import re

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# ------------------------------------------------------------------
#                         HELPER FUNCTIONS

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    # intentionally *not* adding an encoding option to open, See:
    #   https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M, )
    if version_match:
        return version_match.group(1)

    raise RuntimeError("Unable to find version string.")


# ------------------------------------------------------------------
#                          POPULATE SETUP

setup(
    name="hyo2.mate",
    version=find_version("hyo2", "mate", "__init__.py"),
    license='Apache2.0',

    namespace_packages=["hyo2"],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "*.test*", ]),
    package_data={
        "": [
            'mate/media/*.*',
            'mate/media/LICENSE',
        ],
    },
    zip_safe=False,
    setup_requires=[
        "setuptools",
        "wheel",
    ],
    install_requires=[
        "hyo2.abc",
        "pyall",
    ],
    python_requires='>=3.6',
    entry_points={
        "gui_scripts": [
            # 'mate = hyo2.mate.gui:gui',
        ],
        "console_scripts": [
        ],
    },
    test_suite="tests",

    description="The Multibeam Acquisition and Tracking Evaluator app and library.",
    long_description=(read("README.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("HISTORY.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read("AUTHORS.rst") + "\n\n\"\"\"\"\"\"\"\n\n" +
                      read(os.path.join("docs", "developer_guide_how_to_contribute.rst")))
    ,
    url="https://github.com/hydroffice/hyo2_mate",
    classifiers=[  #
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Office/Business :: Office Suites',
    ],
    keywords="hydrography ocean mapping survey raw data",
    author="Wenjun Wu (Geoscience Australia), Justy Siwabessy (Geoscience Australia), Lachlan Hurst (FrontiersSI), "
           "Giuseppe Masetti(UNH,CCOM)",
    author_email="wenjun.wu@ga.gov.au, justy.siwabessy@ga.gov.au, lhurst@frontiersi.com.au, gmasetti@ccom.unh.edu",
)
