##############################################################################
#  Copyright (c) 2014 - Maven Medical
#
#
#  Description: This model generates data for a data analysis exercise to be
#               given to hiring candidates
#
#  Author: Tom DuBois
##############################################################################


import random
import sys
import string

def weighted_choice(choices):
   total = sum(w for _, w in choices)
   r = random.uniform(0, total)
   upto = 0
   for c, w in choices:
      if upto + w > r:
         return c
      upto += w

diagnoses = set(['A','B','C'])

qualities = [.3,.35,.4,.45,.5,.7,.725,.75,.775,.8]
random.shuffle(qualities)

providers = [ 'Sophia', 'Emma', 'Olivia', 'Isabella', 'Mia', 'Jackson', 'Aiden', 'Liam', 'Lucas', 'Noah']

providers = sorted([p for p in zip(providers, qualities)])
#print(providers)

all_procs = ["%s%d%s" % (a,b,c) for a in 'ABC' for b in range(10) for c in '+-']
random.shuffle(all_procs)

def rc(): 
    return chr(random.randint(ord('A'),ord('Z')))

proc_map = {}
for x in all_procs:
    proc_map[x] = rc()+rc()+rc()+rc()+rc() 

#print(proc_map)

def new_patient(patient_id):
    state = random.sample(diagnoses,1)[0]
    
    (dr, dr_quality) = random.sample(providers,1)[0]

    outcome = random.normalvariate(8,1)
    if dr_quality > .6:
        outcome += 2

    proc_count = random.randint(6,8)
    proc_types = random.sample(range(10),proc_count)
    
    procs = []

    for proc_type in sorted(proc_types):
        p = random.uniform(0,1)
        if p < dr_quality:
            procs.append("%s%d%s" % (state, proc_type, '+'))
        elif p > .9:
            procs.append("%s%d%s" % (random.sample(diagnoses - set([state]),1)[0], proc_type, 
                          random.sample('+-',1)[0]))
        else:
            procs.append("%s%d%s" % (state, proc_type, '-'))

        
#    print((state, dr_quality, outcome, procs))
    print(patient_id, dr, int(outcome*100), ' '.join([proc_map[x] for x in procs]))
    print('MASTER', patient_id, dr, int(dr_quality*10), state, int(outcome*100), ' '.join(procs))

for x in range(int(sys.argv[1])):
    new_patient(x+1)
