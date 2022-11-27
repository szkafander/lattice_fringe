from setuptools import setup, find_packages


setup(
    name='lattice_fringe',
    version='2022.11.16',
    description='Installing lattice_fringe',
    author='Paul Lukacs',
    url='https://github.com/szkafander/lattice_fringe',
    packages=find_packages(
        include=['lattice_fringe', 'lattice_fringe.*']
    ),
    include_package_data=False,
    install_requires=[
        'scikit-image~=0.19',
        'scipy~=1.7',
        'matplotlib~=3.5'
    ]
)
