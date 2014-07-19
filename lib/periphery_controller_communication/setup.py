from setuptools import setup
from setuptools import find_packages


requires = [
    'pyserial',
    ]

setup(name='periphery_controller_communication',
      version='0.1',
      description='OpenAutomatedFarm periphery_controller_communication',
      url='http://github.com/AlexanderLang/OpenAutomatedFarm/lib/periphery_controller_communication',
      author='Alexander Lang',
      author_email='alexander.lang@gmail.com',
      license='GPL3',
      packages=find_packages(),
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      periphery_controller_worker = periphery_controller_communication.ConnectionWorker:main
      periphery_controller_manager = periphery_controller_communication.ControllerManager:main
      periphery_controller_reset = periphery_controller_communication.reset:main
      """,
      )
