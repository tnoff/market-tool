import setuptools

setuptools.setup(
    name='market_tool',
    description='Stock Market Tool',
    author='Tyler D. North',
    author_email='tylernorth18@gmail.com',
    install_requires=[
        'pandas == 0.19.2',
        'pandas-datareader >= 0.3.0',
        'SQLAlchemy >= 1.1.9',
    ],
    entry_points={
        'console_scripts' : [
        ],
    },
    packages=setuptools.find_packages(exclude=['tests']),
    version='0.0.3',
)
