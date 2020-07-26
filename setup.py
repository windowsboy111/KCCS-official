from distutils.core import setup
import json
long_description = ''
cfg = json.load(open('ext/bot_settings.json', 'r'))
with open("docs/README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='Merlin-bot',
    packages=['.'],
    version=cfg['version'],
    license='MIT',
    description=cfg['description'],
    long_description_content_type="text/markdown",
    long_description=long_description,
    author=cfg['author name'],
    author_email='cyruschan0111@gmail.com',
    url='https://github.com/windowsboy111/Merlin-bot/',
    download_url=f'https://github.com/windowsboy111/Merlin-bot/archive/{cfg["version"]}.tar.gz',
    keywords=['discord', 'bot', 'discord.py'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Natural Language :: Cantonese',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8'
    ],
)
