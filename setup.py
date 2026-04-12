from setuptools import find_packages, setup

package_name = 'actuators_control_driver'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['actuators_control_driver/dive_mission.launch.py']),
        ('share/' + package_name + '/config', ['actuators_control_driver/dive_mission_config.yaml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='borges',
    maintainer_email='joao.victor.tb@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    # tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'control_node = actuators_control_driver.control_node:main',
            'actuators_test = actuators_control_driver.actuators_test:main',
            'yoyo = actuators_control_driver.yoyo:main',
            'straight_forward = actuators_control_driver.straight_forward:main',
            'lora_guidance_simulator = actuators_control_driver.lora_guidance_simulator:main',
            'guidance_simulator = actuators_control_driver.guidance_simulator:main',
            'dive_mission = actuators_control_driver.dive_mission:main',
        ],
    },
)
