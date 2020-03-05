import setuptools

setuptools.setup(
    name='market_tool',
    description='Stock Market Tool',
    author='Tyler D. North',
    author_email='ty_north@yahoo.com',
    install_requires=[
        'jsonschema >= 2.6.0',
        'pandas == 0.19.2',
        'pandas-datareader >= 0.3.0',
        'psycopg2 >= 2.7.3.2',
        'PyMySQL >= 0.7.11',
        'scipy >= 0.19.0',
        'SQLAlchemy >= 1.1.9',
    ],
    entry_points={
        'console_scripts' : [
            'market-tool = market_tool.command_line:main',
        ],
    },
    packages=setuptools.find_packages(exclude=['tests']),
    version='0.0.6',
)
