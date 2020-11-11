from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
  name = 'dj-graphene',         
  packages = ['dj_graphene'],   
  version = '0.0.2-b.2',      
  license='MIT',        
  description = 'A graphene-django wrapper to do stuffs in the Django way 💃🕺',   
  author = 'Yasiel Cabrera',                   
  author_email = 'yasiel9506@gmail.com',      
  url = 'https://github.com/YasielCabrera/dj-graphene',  
  keywords = ['GRAPHENE', 'GRAPHENE-DJANGO', 'GRAPHQL', 'DJANGO', 'MODELS', 'API', 'PERMISSIONS'],
  install_requires = [
          'graphene',        
          'graphene-django',
          'django'
      ],
  long_description=long_description,
  long_description_content_type='text/markdown',  
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Environment :: Web Environment',
    'Framework :: Django',
    'Programming Language :: Python :: 3',     
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
  ],
)
