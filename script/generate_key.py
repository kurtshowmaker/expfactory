#!/usr/bin/env python

import random
import string

choices = string.ascii_letters + string.digits + string.punctuation
selected = [random.SystemRandom().choice(choices) for _ in range(50)]
selected = selected.replace('"','a').replace("'",'B') # remove quotes
generated_key = ''.join(selected)
print(generated_key)
