from setuptools import setup
import os
from glob import glob

package_name = 'control'

setup(
    name=package_name,
    version='1.0.0',
    packages=[package_name],
    
    # MODIFICARE MAJORĂ: Actualizarea data_files pentru a include urdf, worlds și launch
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        
        # 1. Copiază fișierele de lansare (launch files)
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.py'))),
            
        # 2. Copiază fișierele URDF (Descrierea robotului)
        (os.path.join('share', package_name, 'urdf'), 
            glob(os.path.join('urdf', '*.*'))),
            
        # 3. Copiază fișierele World (Arena de joc, Minge)
        (os.path.join('share', package_name, 'worlds'), 
            glob(os.path.join('worlds', '*.*'))),
    ],
    
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Robot Developer',
    maintainer_email='user@example.com',
    description='Robot control for ball hitting',
    license='Apache-2.0',
    tests_require=['pytest'],
    
    # Noul nod adăugat
    entry_points={
        'console_scripts': [
            'ball_controller = control.ball_controller:main', 
            'fake_ball_publisher = control.fake_ball_publisher:main', 
            'ball_perceptor = control.ball_perceptor:main',
            'demo_kick = control.demo_kick:main',
        ],
    },
)