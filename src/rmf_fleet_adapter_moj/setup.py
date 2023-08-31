import os
from setuptools import setup
from glob import glob
package_name = 'rmf_fleet_adapter_moj'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['config.yaml']),
        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.xml')),
    ],
    install_requires=['setuptools', 'fastapi>=0.79.0', 'uvicorn>=0.18.2'],
    zip_safe=True,
    maintainer='root',
    maintainer_email='root@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['fleet_adapter=rmf_fleet_adapter_moj.fleet_adapter:main',
            'fleet_manager=rmf_fleet_adapter_moj.fleet_manager:main',
        ],
    },
)
