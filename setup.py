from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

requires = [
    'keyring',
    'ShopifyAPI'
]

setup(
    name='shopify2xero',
    version='0.0.1',
    description='A Python package for exporting Shopify data and importing it to Xero. For example, export Shopify orders and import them as Xero invoices ',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Maurice Berk',
    author_email='maurice@mauriceberk.com',
    url='https://github.com/mberk/shopify2xero',
    packages=['shopify2xero'],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.5',
)
