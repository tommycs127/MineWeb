import json
import os
import uuid
import requests

def getOfflineUUID(name) -> str:
    class NULL_NAMESPACE: bytes = b''
    return str(uuid.uuid3(NULL_NAMESPACE, 'OfflinePlayer:'+name))
    
def getOnlineUUID(name) -> str:
    url = f'https://api.mojang.com/users/profiles/minecraft/{name}'
    res = requests.get(url)
    if res.content:
        return res.json()['id']
    return None
    
def checkAuthenticated(name, password):
    data = {"agent": {"name": "Minecraft", "version": 1},
            "name": name,
            "password": password}
    res = requests.post('https://authserver.mojang.com/authenticate', json=data).json()
    
    if 'accessToken' in res.keys():
        data = {'accessToken': res['accessToken'],
                'clientToken': res['clientToken']}
        requests.post(f'https://authserver.mojang.com/invalidate', json=data)
        
    return res

def toJson(name='', ip='', reg_time='') -> dict:
    if type(name) is not str: raise TypeError('name is not str or list')
    return {'name':name, 'uuid':getOfflineUUID(name), 'ip':ip, 'reg_time':reg_time}