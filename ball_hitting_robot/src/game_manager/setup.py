from setuptools import setup

package_name = 'game_manager'

setup(
    name=package_name,
    version='0.0.1',
    packages=["game_manager"],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='You',
    maintainer_email='you@example.com',
    description='Simple game manager: score and reset publisher',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'game_manager = game_manager.game_manager:main'
        ],
    },
)
