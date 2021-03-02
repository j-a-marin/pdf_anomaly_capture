
import sys, os, glob, re, io
import pandas as pd
import argparse
from collections import defaultdict
import datetime
import numpy as np
import pandas as pd


from setlog import setup_log
logger = setup_log()

import lib.settings
lib.settings.init() 

from lib.settings import key_page

import Page_Processer

import pickle
from tqdm import tqdm

last_timecard = Page_Processer.getllasttimecard()   

# main program starts here
if __name__ == '__main__':

    # for use with wildcard * 
    # for filename in sys.argv[1:]:
    #     print (filename)

    #Setup the argument parser class
    parser = argparse.ArgumentParser(prog='Document Processer', 
        description='''Processes content for segments or entirety of OCR-Treated PDF
        ''')
    #We use the optional switch -- otherwise it is mandatory
    parser.add_argument('--begin', '-b', action='store', help='First page to process', default=0)
    parser.add_argument('--end', '-e', action='store', help='Last page to process', default=-1)
    parser.add_argument('--singleton', '-s', action='store_true', help='Single page only')

    #Run the argument parser
    args = parser.parse_args()
    # print (args.begin, args.end)
    begin, end = int(args.begin), int(args.end)

    file_directory = '../ON_CALL_CASE/'
    os.chdir(file_directory)
    # print (os.getcwd()) 

    if args.singleton:
        end = begin + 1 

    elif args.end == -1:
        end = len(glob.glob(r'./*bling*')) + begin

    else:
        end = end + 1

    print (f"processing begin page {begin} to {end}")


    print (list(range(begin, end)))
    for f in tqdm(sorted(glob.glob(r'./*bling*'))): 
        # print (f)
        page_num = int(re.search(r'bling_(\d+)', f).group(1))
        
        if page_num in range(begin, end):
            print ('processing page ', f)
            print (f'saved last_timecard {lib.settings.last_timecard}')

            try:
                print(Page_Processer.extract_single_page_text(f))

            except Exception as e:


                logger.error(f"{page_num} not processed properly with message {e}")
                continue

    print (lib.settings.key_page)

    # args = ["awk", '{print $4}', "oneDayFileLoader.log"]
    # p = sp.Popen(args, stdin = sp.PIPE, stdout = sp.PIPE, stderr = sp.PIPE )
    # lib.settings.key_page['errata'] = [e.decode().strip() for e in p.stdout.readlines()]

    calling_file_directory = '../PDF_TEXT_PROCESSING_2021/'
    os.chdir(calling_file_directory)

    date_pickle = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")      
    output = open(f'alternate_key_page_{date_pickle}.pkl', 'wb')
    print (f"pickling file...on...{os.getcwd()}")
    pickle.dump(lib.settings.key_page, output)


  