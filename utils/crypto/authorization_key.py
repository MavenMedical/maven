from Crypto.Hash import SHA256
import base64
import time
import json

# When the user creates a list of something, every element in that list is checked to make
# sure the user is authorized to see it.  If we later get details on that object,
# we do not want an extra database query or join just to verify the authorization.
# With the initial list, we will provide a key which will act as proof of authorization.
# This key will be a hash of a secret shared by all of our servers (possibly related to our site's
# private ssl cert), the userid, and the primary key of the returned object.
# When asking for details, if we can recreate the hash (and the user is authenticated), the user's
# authorization is confirmed.
# For now this is random, so it will not work between servers and is intentionally broken.
_TEMPORARY_SECRET = SHA256.new()
_TEMPORARY_SECRET.update(b'123')  # """bytes([random.randint(0,255) for _ in range(128)]))


class UnauthorizedException(Exception):
    pass


def bytestostring(b):
    return base64.b64encode(b).decode().replace('/', '_').replace('+', '-').replace('=', '.')


def stringtobytes(s):
    return base64.b64decode(s.replace('_', '/').replace('-', '+').replace('.', '='))


def authorization_key(data, length=44, timeout=None, timecode=None):
    global _TEMPORARY_SECRET
    sha = _TEMPORARY_SECRET.copy()
    return _authorization_key(sha, data, length, timeout, timecode)


def _authorization_key(sha, data, length=44, timeout=None, timecode=None):
    if timecode:
        data = (data, timecode)
    elif timeout:
        timecode = int(time.time() + timeout)
        timecode = bytestostring(timecode.to_bytes(4, 'big'))
        data = (data, timecode)
    # print(data)
    # print(pickle.dumps(data))
    sha.update(bytes(json.dumps(data), 'utf-8'))
    ret = bytestostring(sha.digest())
    if length:
        ret = ret[:length]
    if timecode:
        ret = ''.join([timecode, ret])
    return ret


def check_authorization(data, auth, length=44):
    if len(auth) < length:
        raise UnauthorizedException('User is not logged in.')  # this is an invalid auth key?

    if len(auth) > length:
        # a timeout is added, should be 8 bytes
        if not len(auth) == 8 + length:
            raise UnauthorizedException('User is not logged in.')  # this is an invalid auth key?

        auth_time = auth[:8]
        auth_key = auth[8:]
        t = int.from_bytes(stringtobytes(auth_time), 'big')
        if t < time.time():
            raise UnauthorizedException("User's login has timed out.")
        data = (data, auth_time)
    else:
        auth_key = auth

    # make sure the user's auth key is valid
    if not authorization_key(data, length) == auth_key:
        raise UnauthorizedException('User is not logged in.')  # this is an invalid auth key?
