from hashlib import sha256

SHA256 = lambda s: sha256(bytes(s, encoding='ascii')).hexdigest()
hashPassword = lambda pw, salt: f'$SHA${salt}${SHA256(SHA256(pw)+salt)}'
checkPassword = lambda pw, hash: hash == hashPassword(pw, hash.split('$')[2])