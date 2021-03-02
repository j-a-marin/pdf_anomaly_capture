import sys, os, glob, re, io
import pandas as pd
import argparse
from collections import defaultdict
import numpy as np

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage

from lib.parse_helpers import parse_timecard_line_v2, timecard2dict, date_find
from lib.parse_helpers import weekly_mapping
from lib.parse_helpers import reform_produce
from lib.parse_helpers import handle_buffer_entries

from lib.regex_helper import filter_junk, clean_line_intake


from lib.settings import key_page
from lib.settings import last_timecard
#read?
import lib.settings

from setlog import setup_log
logger = setup_log()

def extract_text_from_pdf(pdf_path):

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            page_interpreter.process_page(page)
        text = fake_file_handle.getvalue()
        
    converter.close()
    fake_file_handle.close()
    
    if text: 
        return text

def extract_single_page_text(pdf_path):

    timecard = None
    
    # global last_timecard
    # print ('last global timecard is', last_timecard)

    page_num = re.search(r"bling_(\d{3})", pdf_path)[1]
    
    page = extract_text_from_pdf(pdf_path)
    
    # timecard = re.findall(r"Timecard\s+for\s+Pay\s+Period.*?(\d{6})",page)

    span = re.search(r"Timecard\s{1,2}for\s{1,2}Pay\s{1,2}Period", page)

    if span:
        timecard = "".join(re.findall(r"\d+", page[int(span.end()):int(span.end())+10][:7]))
        timecard = [timecard]

    refdates = re.findall(r"[A-Z]\w{2}-\d{1,2}.*75[6|7]0\s*[147|77329]",page)
    job_code = re.findall(r"[A-Z]\w{2}-\d{1,2}.*75[6|7]0\s*(147|77329)",page)

    
    if not refdates:

        key_page[page_num]['status'] = 'HR Table'
        key_page[page_num]['timecard'] = lib.settings.last_timecard
        # added on January 11
        key_page[page_num]['refdate'] = pd.DataFrame()

        return key_page
    
    if job_code:
        job_code = job_code[0]
    

    print ('********************')
    print ('new global last timecard is', lib.settings.last_timecard)
    print ('new timecard is', timecard)
    print ('********************')

    if timecard:
        timecard = timecard[0]
        print (' ////////////// we have a new timecard')
        lib.settings.last_timecard = timecard
        key_page[page_num]['timecard'] = timecard
        key_page[page_num]['status'] = "Full Record"
        key_page[page_num]['refdate'] = pd.DataFrame()

    else: 
        print ('********************** we do not have a new timecard')

        timecard = lib.settings.last_timecard
        key_page[page_num]['status'] = "Wrap Around"
        key_page[page_num]['timecard'] = timecard
        key_page[page_num]['refdate'] = pd.DataFrame()


    # refdates play a key role since they are keys to the timecard dictionary and also serve to split text to lines
    
    if not refdates:
        key_page[page_num]['status'] = 'HR Table'
        return key_page
        
    namz = ['Day','In_Time','Out_Time','Amount','Description','Department','Job_Code','OT']
    parsed_date_list = []

    if refdates:
        refdate_split = re.split(r'(?!^)(?=\w{3}-\d{1,2})', refdates[0])
        refdate_split_filter1 = [rs for rs in refdate_split if len(rs) > 10]


        buffer = ''

        for line in refdate_split_filter1:

            line = filter_junk(line)

            line_structure = re.search(r"\d[_;,\.]\d{2}", line) and re.search(r"75\d{2}", line)
            line_length_problem = len(line) > 60
            
            if not line_structure or line_length_problem:
            
                buffer += line
                
            else:
                            
                print ('refdate parsing', line.strip())

#             assert type(line) == str, 'line entering parse from page processing is not a string'
#             assert type(timecard) == str, 'timecard entering parse from page processing is not a string'
#             assert type(job_code) == str, 'job_code entering parse from page processing is not a string'

                parsed_date_list.append(parse_timecard_line_v2(line, timecard, job_code))

        print ("DATE__FIND__BUFFER", date_find(buffer,timecard))

        days_found_dict = date_find(buffer,timecard)

        print ("HANDLE BUFFER ENTRIES", handle_buffer_entries(days_found_dict, buffer))

        for hb_line in handle_buffer_entries(days_found_dict, buffer):

            parsed_date_list.append(parse_timecard_line_v2(hb_line, timecard, job_code))

    print ('parsed date list -->', parsed_date_list)
    
    temp_df = pd.concat(parsed_date_list, ignore_index=True, sort=False)

    temp_df['Out_Time_Hour'] = temp_df['Out_Time_Hour'].str.replace(r"(\d{2}).*(\d{2})", r"\1:\2")

    temp_df['Amount'] = temp_df['Amount'].str.replace(r"(\d{1,2}).*(\d{2})", r"\1.\2")
    key_page[page_num]['refdate'] = temp_df
    lib.settings.key_page = key_page
    return 

# main program starts here
if __name__ == '__main__':
    #Setup the argument parser class

    pdf_file_to_process = sys.argv[1]
    print(extract_text_from_pdf(pdf_file_to_process))
    print(extract_single_page_text(pdf_file_to_process))
    print(key_page)
