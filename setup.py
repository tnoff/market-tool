import setuptools

setuptools.setup(
    name='market_tool',
    description='Stock Market Tool',
    author='Tyler D. North',
    author_email='tylernorth18@gmail.com',
    install_requires=[
        'requests >= 2.13.0',
    ],
    entry_points={
        'console_scripts' : [
            'stocks = market_tool.stocks:main',
        ],
    },
    packages=setuptools.find_packages(exclude=['tests']),
    version='0.0.1',
)
