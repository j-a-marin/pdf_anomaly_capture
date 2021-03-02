import datetime
from dateutil.parser import parse
import sys, os, glob, re, io, pickle
import pandas as pd

from collections import defaultdict

from collections import Counter
from collections import OrderedDict
import bs4 as bs
import requests
import unicodedata
import numpy as np
import lxml

from lib.regex_helper import token2regex
from lib.regex_helper import token2regex_jobcode_5
from lib.regex_helper import filter_junk, clean_line_intake

pkl_file = open('./time_hash.pkl', 'rb')
time_hash = pickle.load(pkl_file)

import logging
logger = logging.getLogger(__name__)

def date_find(buffer, timecard):
    
    from datetime import datetime

    days_found = defaultdict(dict)
    
    '''
    FIRST WE NEED TO REFERENCE THE GLOBAL DATE DICTIONARY TO FIND VALID DATES
    '''

    regex_dates = set(re.findall(r"[A-Z][a-z]{2}[\s-]\d{1,2}", buffer))
#         print (regex_dates)
    
#         regex_dates_ = [re_dates + '/' + timecard_year for re_dates in regex_dates]
#         print (regex_dates_)
#         regex_dates_sorted = sorted(regex_dates_, key=lambda item: datetime.strptime(item, "%/%Y"))
    
#         print(regex_dates_sorted)

    for day in regex_dates:
                            
        month_Number, day_Number = timecard2dict(timecard)[day]['month'], timecard2dict(timecard)[day]['day']
        
        days_found[day]['date'] = month_Number.lstrip('0') + "/" + day_Number.lstrip('0') + "/" + timecard[:4]
        
#             days_found = sorted(days_found.items(), key=lambda item: datetime.strptime(item, "%/%Y"))
#             print (day)


    dayz = OrderedDict(
        sorted(days_found.items(), key=lambda item: datetime.strptime(item[1]['date'], "%m/%d/%Y")))

        
#         dayz = {k: v for k, v in sorted(days_found.items(), 
#                                         key=lambda k,v: datetime.strptime(v['date'], "%m/%d/%Y"),
#                                        reverse=False) }  
    
#         print ('DAYZ', dayz['Wed-1']['date'])
    
    days_found = dayz

    return days_found

def reform_produce(list_found_ref_dates, timecard):
    
    days_found_dict = defaultdict(dict)
    
    buffer = ''

    output = {}

    testlist = list_found_ref_dates

    for ix, line_intake in enumerate(testlist):
        
        line_intake = clean_line_intake(line_intake)
        
        # DESIGNATE NECESSARY COMPONENTS OF FULL INFORMATION LINE THAT CAN BE FED TO REST OF PROGRAM
        
        line_structure = re.search(r"\d[_;,\.]\d{2}", line_intake) and re.search(r"75\d{2}", line_intake)
        line_length_problem = len(line_intake) > 60
            
        if not line_structure or line_length_problem:
        
            buffer += line_intake
            
        else:
                        
#             print (ix, line_intake)
            yield line_intake
                        
    def date_find(days_found, buffer):
        
        from datetime import datetime
        
        '''
        FIRST WE NEED TO REFERENCE THE GLOBAL DATE DICTIONARY TO FIND VALID DATES
        '''

        regex_dates = set(re.findall(r"[A-Z][a-z]{2}[\s-]\d{1,2}", buffer))
#         print (regex_dates)
        
#         regex_dates_ = [re_dates + '/' + timecard_year for re_dates in regex_dates]
#         print (regex_dates_)
#         regex_dates_sorted = sorted(regex_dates_, key=lambda item: datetime.strptime(item, "%/%Y"))
        
#         print(regex_dates_sorted)

        for day in regex_dates:
                                
            month_Number, day_Number = timecard2dict(timecard)[day]['month'], timecard2dict(timecard)[day]['day']
            
            days_found[day]['date'] = month_Number.lstrip('0') + "/" + day_Number.lstrip('0') + "/" + timecard[:4]
            
#             days_found = sorted(days_found.items(), key=lambda item: datetime.strptime(item, "%/%Y"))
#             print (day)
    
    
        dayz = OrderedDict(
            sorted(days_found.items(), key=lambda item: datetime.strptime(item[1]['date'], "%m/%d/%Y")))

            
#         dayz = {k: v for k, v in sorted(days_found.items(), 
#                                         key=lambda k,v: datetime.strptime(v['date'], "%m/%d/%Y"),
#                                        reverse=False) }  
        
#         print ('DAYZ', dayz['Wed-1']['date'])
        
        days_found = dayz

        return days_found
    
    if buffer:
        
        days_found = date_find(days_found_dict, buffer)
        
        output = {'days_found':days_found, 'buffer':buffer}
        
        yield output

'''
MUST BE PLACED IN IF-BUFFER CONDITIONAL
'''

def handle_buffer_entries(days_found_dict, buffer):

    days_found = days_found_dict
        
    # days_found = days_found_dict['days_found']
    # buffer = days_found_dict['buffer']
    
    for ix, day in enumerate(days_found.keys()):
                                
        dt = days_found[day]['date'][:-5]
#             y = (re.findall(r"\d\/\d{2}\s\d{2}[:;]\d{2}\s+\d\/\d{2}\s\d{2}[:;]\d{2}", buffer))
        y = (re.findall(re.escape(dt) + r"\s*\d{2}[:;]\d{2}\s*" + 
                        re.escape(dt) + r"\s*\d{2}[:;\s]\d{2}\s*", buffer))

        y = [re.split(dt, yy.strip()) for yy in y]
        
#         print ('y', y)
        for yy in y: 
            yy.pop(0)
            yy.insert(0,dt)
            yy.insert(2,dt)
            
        days_found[day]['clock'] = [" ".join(yy) for yy in y]

        observ_length = len( [x.strip() for x in re.findall(r"\s*\d{1,2}\.\d{2}\s*", buffer)]) // len(set(days_found.keys()))

        amt = [x.strip() for x in re.findall(r"\s*\d{1,2}[\.]\d{2}\s*", buffer)][ix*observ_length:observ_length+
                                                                               ix*observ_length]
        days_found[day]['amt'] = amt

        desc = re.findall('\s*[A-Z][a-z]+[\s-][A-Z][a-z]+\s*', buffer)
        desc = [d.strip() for d in desc][ix*observ_length:observ_length+ix*observ_length]
        days_found[day]['desc'] = desc

        dept = re.findall('\s*75\d{2}\s*', buffer)
        dept = [d.strip() for d in dept][ix*observ_length:observ_length+ix*observ_length]
        days_found[day]['dept'] = dept

        code = re.findall('\s*(14\d{1}|773\d{2})\s*', buffer)
        code = [c.strip() for c in code][ix*observ_length:observ_length+ix*observ_length]
        days_found[day]['code'] = code

#         print ("y", y)
#         print ("amt", amt)
#         print ("desc", desc)
        
    out = []
    for d in days_found:
#         print (days_found)
        out.extend([" ".join( [d, xx[0], str(xx[1]), xx[2],  xx[3], xx[4]] ) 
              for xx in list(zip(days_found[d]['clock'],
                                days_found[d]['amt'],
                                days_found[d]['desc'],
                                  days_found[d]['dept'],
                                  days_found[d]['code']
                                ))])

        # if 'On-Call' in days_found[d]['desc']:
        #     special_index = days_found[d]['desc'].index('On-Call')

        #     out.append(" ".join([d, days_found[d]['amt'][special_index], 'On-Call', days_found[d]['dept'][special_index],
        #                        days_found[d]['code'][special_index]]))
            
#         print (days_found[d]['desc'])
        
#         ["Call" in t for t in ['Shift Leader', 'Shift Leader', 'On-Call']]

        special_handling_desc = defaultdict(dict)
        special_handling_desc['On-Call'] = 'On-Call 20'
        special_handling_desc['HRO/Benefit'] ='HRO/Benefit'
        special_handling_desc['CA Sick Paid Leave'] = 'CA Sick Paid Leave'
        special_handling_desc['Missed Break'] = 'Missed Break'
        special_handling_desc['Preceptor Pay'] = 'Preceptor Pay'
    
        for sd in days_found[d]['desc']:
            
            if sd in special_handling_desc[sd]:
                                   
                special_index = days_found[d]['desc'].index(sd)

                out.append(" ".join([d, days_found[d]['amt'][special_index], special_handling_desc[sd], 
                                     days_found[d]['dept'][special_index],
                                   days_found[d]['code'][special_index]]))

    return out
            

def weekly_mapping(year):
    
    http = 'https://www.epochconverter.com/weeks/' + str(year)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
    resp = requests.get(http, headers=headers)
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find('table', {'class': 'infotable'})
    weeks = {}

    for row in table.findAll('tr')[1:]:
        
        if row.findAll('td')[1].text !='':
            from_date = row.findAll('td')[1].text.strip(' \t\r\n')
            to_date = row.findAll('td')[2].text.strip(' \t\r\n')
            week = row.findAll('td')[0].text.strip(' \t\r\n')
        
        if from_date:
            weeks[week] = (from_date, to_date) 
     
    weeks = OrderedDict(sorted(weeks.items(), key=lambda t: t[0]))
    return weeks

def timecard2dict(timecard):
    
    if isinstance(timecard,list):
        timecard=timecard[0]

    if timecard:
        timecard_year = int(timecard[:-2])
        timecard_number = int(timecard[-2:])
        if timecard_number > 26:
            raise ValueError("Timecard Error: There are only 26 Timecards per Year")
        timecard_number_adjusted = timecard_number * 2

    end_timecard_window = time_hash[timecard_year]['Week ' + f'{timecard_number_adjusted:02}'][0]
    end_date = parse(end_timecard_window)
    no_of_days = datetime.timedelta(days=22) if timecard_number_adjusted !=2 else datetime.timedelta(days=22)
    begin = (end_date - no_of_days)

    out = {d.strftime('%a-%d'):{'day':d.strftime('%d'), 'month':d.strftime('%m')} for d in pd.date_range(begin, end_date, freq="D")}

    new_keys =  [k.replace('-0','-') for k in out.keys()]
    new_out = dict(zip(new_keys, out.values()))

    for k, v in new_out.items():
        if int(v['day']) < 10:        
            v['day'] = v['day'].lstrip('0')
        
    # out = {k: v for k, v in sorted(new_out.items(), 
    #     key=lambda item: datetime.date(timecard_year, int(item[1]['month']), int(item[1]['day']))) }

    # for k, v in new_out.items():
    #     if int(v['day']) < 10:        
    #         v['day'] = v['day'].strip('0')

    # out = {k: v for k, v in sorted(new_out.items(), key=lambda item: int(item[1]['day']))}

    return new_out

def parse_timecard_line_v2(line_intake, timecard, job_code):

    # line_intake = filter_junk(line_intake) # this line has been moved to Page_Processer.py
    
#     if isinstance(timecard, list):
#         timecard = timecard[0]
        
    dfx = pd.DataFrame([line_intake])
    scenario = None
    df2 = None
    token = None
    text_handling_dictionary = None
    description = ''
    
    print ('entry point timecard in line parser timecard_line_v2', timecard)
    
#     if not timecard:
#         timecard = last_timecard

#     print (timecard, 'timecard entered as string', timecard[0])
    
    '''
    DESCRIPTION DOMINANT CATEGORIES - THERE IS ALWAYS A DESCRIPTION HERE 
    --> token2regex(token, description, timecard)
    first we separate incoming lines on the basis of a text description so that tokens match dictionary items 
    each of which will have a regex recipe from token2regex() 
    '''


    def timecard2dict(timecard):
        
        if isinstance(timecard,list):
            timecard=timecard[0]

        if timecard:
            timecard_year = int(timecard[:-2])
            timecard_number = int(timecard[-2:])
            if timecard_number > 26:
                raise ValueError("Timecard Error: There are only 26 Timecards per Year")
            timecard_number_adjusted = timecard_number * 2

        end_timecard_window = time_hash[timecard_year]['Week ' + f'{timecard_number_adjusted:02}'][0]
        end_date = parse(end_timecard_window)
        no_of_days = datetime.timedelta(days=22) if timecard_number_adjusted !=2 else datetime.timedelta(days=22)
        begin = (end_date - no_of_days)

        out = {d.strftime('%a-%d'):{'day':d.strftime('%d'), 'month':d.strftime('%m')} for d in pd.date_range(begin, end_date, freq="D")}

        new_keys =  [k.replace('-0','-') for k in out.keys()]
        new_out = dict(zip(new_keys, out.values()))

        for k, v in new_out.items():
            if int(v['day']) < 10:        
                v['day'] = v['day'].lstrip('0')
            
        # out = {k: v for k, v in sorted(new_out.items(), 
        #     key=lambda item: datetime.date(timecard_year, int(item[1]['month']), int(item[1]['day']))) }

        # for k, v in new_out.items():
        #     if int(v['day']) < 10:        
        #         v['day'] = v['day'].strip('0')

        # out = {k: v for k, v in sorted(new_out.items(), key=lambda item: int(item[1]['day']))}

        return new_out
    

    
    if re.search(r"\s*[A-Za-z]{2,}[\s-]*[A-Za-z]{3,}\s*", line_intake): 

        print ("CONTAINS TEXT REGARDING JOB DESCRIPTION")
        
        text_content =  re.findall(r"([A-Za-z]{2,9}[\/\s-]*[A-Za-z]{3,}\s*([A-Za-z]{4}\s[A-Za-z]{5})?)", line_intake)
        description = text_content[0][0].strip()
        token = ["".join(re.findall('[A-Z]+',text[0]))[:2] for text in text_content][0]
    #         
    #         token = 'PP' # ONLY AS AN EXAMPLE - DO NOT TEST WITH THIS OTHERWISE YOU ONLY GET THAT FORMAT OUTPUT
    
        try:
            day_ = re.findall(r"[A-Za-z]{3}-\d{1}", line_intake)[0].title()
            day_num = timecard2dict(timecard)[day_]['day'].lstrip('0')
            month_num = timecard2dict(timecard)[day_]['month'].lstrip('0')
        except:
            day_ = re.findall(r"[A-Za-z]{3}-\d{2}", line_intake)[0].title()
            day_num = timecard2dict(timecard)[day_]['day'].lstrip('0')
            month_num = timecard2dict(timecard)[day_]['month'].lstrip('0')
            
        day_digits = len(day_num)
        month_digits = len(month_num)
        
        
        logger.info(f'UP LEVEL \
        token --> {token} timecard--> {timecard} day-digits-->{day_digits} month-digits-->{month_digits}\
        day-->{day_} day_num-->{day_num} month_num-->{month_num}')
        
        # print ("job code:", job_code, '***********************length', len(job_code))
        print ("month num:", month_num, '****************** length', len(month_num))        
        print ("day num:", day_num, '*********************** length', len(day_num))


                
        if len(job_code) == 3:
            text_handling_dictionary = token2regex(token, timecard, day_digits, month_digits, 
                                                   day_, day_num, month_num)
            
        elif len(job_code) > 3:
            print (token, timecard, day_digits, month_digits, 
                                                   day_, day_num, month_num)
            
            text_handling_dictionary = token2regex_jobcode_5(token, timecard, day_digits, month_digits, 
                                                   day_, day_num, month_num)
        print ('description', description, "\n")
        print ('where is TOKEN', token, "COMPLETION OF ENTRY \n")

#         print ('FULL KEYS', [k for k,v in text_handling_dictionary.items() if len(v) > 0])
#         print ('FULL DICT', text_handling_dictionary[token])

        day = text_handling_dictionary[token]['day']
        in_time_date = text_handling_dictionary[token]['in_time_date']
        in_time_hour = text_handling_dictionary[token]['in_time_hour']
        out_time_date = text_handling_dictionary[token]['out_time_date']
        out_time_hour = text_handling_dictionary[token]['out_time_hour']
        amount = text_handling_dictionary[token]['amount']
        # description = text_handling_dictionary[token]['description']
        dept = text_handling_dictionary[token]['dept']

        df2 = dfx[0].str.extractall(
        f'{day}.*{in_time_date}.*{in_time_hour}.*{out_time_date}.*{out_time_hour}.*{amount}.*{dept}', 
                                            flags=re.I).reset_index(level=1, drop=True)
        if token == 'OC':
            description += ' 20'

        if token == 'SH':
            description += ' Early'  

        df2.insert(loc = len(df2.columns), column = 'Description', value = description) 
        df2.insert(loc = len(df2.columns), column = 'Job_Code', value = job_code) 
    
    else:
                
        token = 'Standard'
#         text_content =  re.findall(r"([A-Za-z]{2,9}[\/\s-]*[A-Za-z]{3,}\s*([A-Za-z]{4}\s[A-Za-z]{5})?)", line_intake)
#         description = text_content[0][0].strip()
#         print (description)
#         token = ["".join(re.findall('[A-Z]+',text[0]))[:2] for text in text_content][0]
                
        try:
            day_ = re.findall(r"[A-Za-z]{3}-\d{1}", line_intake)[0].title()
#             print (day_)
#             print (timecard)
#             print (timecard2dict(timecard))
            day_num = timecard2dict(timecard)[day_]['day'].lstrip('0')
            month_num = timecard2dict(timecard)[day_]['month'].lstrip('0')
        except:
            day_ = re.findall(r"[A-Za-z]{3}-\d{2}", line_intake)[0].title()
            day_num = timecard2dict(timecard)[day_]['day'].lstrip('0')
            month_num = timecard2dict(timecard)[day_]['month'].lstrip('0')
    
        day_digits = len(day_num)
        month_digits = len(month_num)
        
        # logger.info(f'UP ONE LEVEL \
        # token --> {token}\
        # timecard--> {timecard} \
        # len day-digits-->{day_digits}\
        # len month-digits-->{month_digits}\
        # actual formatted day-->{day_} \
        # date day_num-->{day_num} \
        # date month_num-->{month_num}')
        
        if len(job_code) == 3:
            text_handling_dictionary = token2regex('Standard', timecard, day_digits, month_digits,
                                               day_, day_num, month_num)
        elif len(job_code) > 3:
            text_handling_dictionary = token2regex_jobcode_5('Standard', timecard, day_digits, month_digits, 
                                                   day_, day_num, month_num)
#         print ('KEYS 2', text_handling_dictionary.keys())
#         print ('DICT 2', text_handling_dictionary)
        day = text_handling_dictionary[token]['day']
        in_time_date = text_handling_dictionary[token]['in_time_date']
        in_time_hour = text_handling_dictionary[token]['in_time_hour']
        out_time_date = text_handling_dictionary[token]['out_time_date']
        out_time_hour = text_handling_dictionary[token]['out_time_hour']
        amount = text_handling_dictionary[token]['amount']
        # description = text_handling_dictionary[token]['description']
        dept = text_handling_dictionary[token]['dept']

        df2 = dfx[0].str.extractall(
        f'{day}.*{in_time_date}.*{in_time_hour}.*{out_time_date}.*{out_time_hour}.*{amount}.*{dept}', 
                                            flags=re.I).reset_index(level=1, drop=True)

        # df2.insert(loc = len(df2.columns), column = 'Description', value = description) # could be used if necessary upon deletiion of text_handling entry above
        df2.insert(loc = len(df2.columns), column = 'Job_Code', value = job_code) 
        if token == 'OC':
            description += ' 20'

        if token == 'SH':
            description += ' Early'
        df2.insert(loc = len(df2.columns), column = 'Description', value = description) 

        
    return df2
        