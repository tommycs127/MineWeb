import subprocess as sp
import os
import secrets as s
import platform as pf
import tempfile as tf

class classproperty(object):

    def __init__(cls, fget):
        cls.fget = fget
        
    def __get__(cls, owner_self, owner_cls):
        return cls.fget(owner_cls)

class MinecraftServerLocal(object):

    __message = ''

    @classmethod
    def __init__(cls, app=None, encode='big5'):
        cls.SERVER_LOCK_DIR = os.path.join(tf.gettempdir(), 'mcserver.lock')            
        cls.SERVER_DIR = '.'
        cls.TERMINAL_ENCODING = encode
        
        if app is not None:
            cls.init_app(app)

    @classmethod
    def init_app(cls, app):
        app.minecraftServerLocal = cls
        cls.SERVER_DIR = app.config['SERVER_DIR']
        cls.BASE_DIR = app.config['BASB_DIR']

    @classmethod
    def is_on(cls):
        if os.path.exists(cls.SERVER_LOCK_DIR):
            with open(cls.SERVER_LOCK_DIR, 'r') as f:
                BATCH_ID = f.readline()
            if pf.system() == 'Windows':
                cmd = f'TASKLIST /FI "ImageName eq cmd.exe" /FI "Status eq Running" /FI "WindowTitle eq {BATCH_ID}" /FO CSV'
                L = sp.check_output(cmd).decode(cls.TERMINAL_ENCODING).split('\r\n')[1:]
            elif pf.system() == 'Linux':
                cmd = ''
                
            if len(L[0].split(',')) > 1:
                return True
            else:
                os.remove(cls.SERVER_LOCK_DIR)
        return False
        
    @classmethod
    def set_message(cls, message):
        cls.__message = message
        
    @classproperty
    def message(cls):
        return cls.__message

    @classmethod
    def start(cls):
        if not cls.is_on():
            scripts_dir = os.path.join(cls.BASE_DIR, 'scripts\\')
            if pf.system() == 'Windows':
                BATCH_ID = f'mc-{s.token_hex(4)}'
                with open(cls.SERVER_LOCK_DIR, 'w') as f:
                    f.writelines(BATCH_ID)
                os.chdir(scripts_dir)
                os.system(f'start server_start.bat {cls.SERVER_DIR} {BATCH_ID} {cls.SERVER_LOCK_DIR}')
            elif pf.system() == 'Linux':
                pass
            else: # Darwin
                pass
