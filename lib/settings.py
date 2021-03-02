
# settings.py
from collections import defaultdict

# WE RUN INIT FROM MAIN PROCESS BUT HAVE ACCESS TO ANY SUBPROCESS THAT IMPORTS SETTINGS

# SUBPROCESS MAY WRITE THE GLOBAL VARIABLE 

def init():

    global last_timecard, bad_files, key_page
    last_timecard = None
    bad_files = []
    key_page = defaultdict(dict)


