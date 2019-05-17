from distutils.core import setup
from Cython.Build import cythonize

setup(
    name="TapeDetection",
    ext_modules = cythonize('*.pyx'),
)