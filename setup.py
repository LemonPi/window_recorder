from setuptools import setup

setup(
    name='window_recorder',
    version='0.1.0',
    packages=['window_recorder'],
    url='https://github.com/LemonPi/window_recorder',
    license='MIT',
    author='zhsh',
    author_email='zhsh@umich.edu',
    description='Programatically video record a window given by name in Linux',
    install_requires=['opencv', 'mss']
)
