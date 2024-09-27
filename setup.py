from setuptools import setup

requirements = open('requirements.txt').readlines()
requirements = [r.strip() for r in requirements]

setup(
   name='kctv',
   version='1.0',
   description='',
   author='isabelcachola',
   packages=['kctv'],  #same as name
   install_requires=requirements #external packages as dependencies
)