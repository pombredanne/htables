import distutils.core

distutils.core.setup(
    name='htables',
    version='0.3-rc1',
    author='Eau de Web',
    author_email='office@eaudeweb.ro',
    py_modules=['htables'],
    install_requires=[
        'psycopg2',
    ],
)
