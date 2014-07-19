from setuptools import setup
from setuptools import find_packages


requires = [
    'field_controller_database',
    ]

setup(name='farm_utilities',
      version='0.1',
      description='OpenAutomatedFarm farm utilities',
      url='http://github.com/AlexanderLang/OpenAutomatedFarm/lib/farm_utilities',
      author='Alexander Lang',
      author_email='alexander.lang@gmail.com',
      license='GPL3',
      packages=find_packages(),
      zip_safe=False,
      install_requires=requires,
      entry_points="""\
      [console_scripts]
      measurement_scheduler = farm_utilities.MeasurementScheduler:main
      measurement_logger = farm_utilities.MeasurementLogger:main
      """,
      )
