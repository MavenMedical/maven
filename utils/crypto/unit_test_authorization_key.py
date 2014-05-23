import time

import utils.crypto.authorization_key as AK
import maven_logging as ML


user = 'tom'
bad_user='not tom'

k1 = AK.authorization_key(user)
k2 = AK.authorization_key(user, 30)
k3 = AK.authorization_key(user, 44, 1)

AK.check_authorization(user,k1)
ML.PRINT("Access with a regular key worked")
try:
    AK.check_authorization(bad_user,k1)
except:
    ML.PRINT("Access for a different user failed")
AK.check_authorization(user,k2, 30)
ML.PRINT('Access with an explicitly shorter key worked')
try:
    AK.check_authorization(user,k2)
except:
    ML.PRINT('Access with a shorter key, but without being explicit about it failed')
AK.check_authorization(user,k3)
ML.PRINT("Access with a timed key worked")
time.sleep(2)
try:
    AK.check_authorization(user,k3)
except:
    ML.PRINT("Access with a timed key failed after the timeout")
