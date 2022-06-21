import os
from random import randint
from whoosh.analysis import StemmingAnalyzer
from secrets import token_hex

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or token_hex(16)
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or \
            'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    WHOOSH_ANALYZER = StemmingAnalyzer
    WHOOSH_INDEX_DIR = os.environ.get('WHOOSH_INDEX_DIR') or os.path.join(basedir, 'whoosh_index/')
    WHOOSH_INDEXING_CPUS = os.environ.get('WHOOSH_INDEXING_CPUS') or 2
    WHOOSH_INDEXING_RAM = os.environ.get('WHOOSH_INDEXING_RAM') or 256
    WHOOSH_RAM_CACHE = os.environ.get('WHOOSH_RAM_CACHE') or False
    BASB_DIR = basedir
    SERVER_DIR = os.environ.get('SERVER_DIR') or ''
    if not os.path.exists(SERVER_DIR):
        SERVER_DIR = os.path.dirname(os.path.dirname(basedir))
        
    with open(os.path.join(SERVER_DIR, 'server.properties'), 'r') as f:
        lines = [l.split('#')[0] for l in f.readlines() if l.split('#')[0]]
        options = dict()
        for l in lines:
            if len(l.split('=')) > 1:
                options[l.split('=')[0]] = l.split('=')[1][:-1]
            elif len(l.split('=')) > 0:
                options[l.split('=')[0]] = ''
                
    SERVER_IP = os.environ.get('SERVER_IP') or f'{options["server-ip"] or "localhost"}:{options["server-port"] or "25565"}'
    WEBSITE_NAME = os.environ.get('WEBSITE_NAME') or 'My Minecraft Server'