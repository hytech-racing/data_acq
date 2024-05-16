from setuptools import setup, find_packages


setup(
    name="py_data_acq",
    version="1.0",
    packages=find_packages(),
    scripts=['runner.py', 'broadcast-test.py', 'test_param_server.py'],
    package_data={
        'py_data_acq': ['web_server/templates/*.html', 'templates/**/*.html']
    }, 
)