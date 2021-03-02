# DATE: DEC 28
# THIS FUNCTION IS ONLY FOR LINES CONTAINING A TEXT DESCRIPTION
# SOME LINES WILL H
from collections import defaultdict

import re
import numpy as np 
import logging
logger = logging.getLogger(__name__)

def clean_line_intake(line_intake):
    
    def remove_sludge(line_intake):
        
        line_intake = re.sub(r"rpt.*Timecard\s?for\s?Pay\s?Period\s*:\s*\d{6}", r"", line_intake)
        
        line_intake = re.sub(r"Day.*OT", r"", line_intake)
                             
        return line_intake
    
    def clean_more(line_intake):
        
        line_intake = re.sub(r"M\w{2}-", r"Mon-", line_intake)
        line_intake = re.sub(r"Tu\w{1}-", r"Tue-", line_intake)
        line_intake = re.sub(r"W\w{2}-", r"Wed-", line_intake)
        line_intake = re.sub(r"Th\w{1}-", r"Thu-", line_intake)
        line_intake = re.sub(r"F\w{2}-", r"Fri-", line_intake)
        line_intake = re.sub(r"Sa\w{1}-", r"Sat-", line_intake)
        line_intake = re.sub(r"Su\w{1}-", r"Sun-", line_intake)

        line_intake = re.sub(r"San.*Hospital", r"", line_intake)
        line_intake = re.sub(r"Pay.*\d{6}[\s-]+\d{6}", r"", line_intake)
        line_intake = re.sub(r"Dates.*\/20\d{2}", r"", line_intake)

        line_intake = re.sub(r";", r":", line_intake)

        return line_intake
    
    line_intake = line_intake.strip()
    
    line_intake = re.sub(r"(?=\d)(\d{1})[_\s](\d{2})\s*(?=[A-Z])", r" \0 \1.\2 ", line_intake)
    
#     if len(line_intake) >  70:
        
#         a = re.split(r'([A-Za-z]+[\s-][A-Za-z]+)', line_intake)
        
#         for line_intake in a:
            
#             print (clean_more(remove_sludge(line_intake)))
            
#     else:
        
#         return clean_more(remove_sludge(line_intake))
    return clean_more(remove_sludge(line_intake))

def filter_junk(line_intake):

    def remove_sludge(line_intake):
        
        line_intake = re.sub(r"rpt.*Timecard\s?for\s?Pay\s?Period\s*:\s*\d{6}", r"", line_intake)
        
        line_intake = re.sub(r"Day.*OT", r"", line_intake)
                             
        return line_intake
    
    def clean_more(line_intake):
        
        line_intake = re.sub(r"M\w{2}-", r"Mon-", line_intake)
        line_intake = re.sub(r"Tu\w{1}-", r"Tue-", line_intake)
        line_intake = re.sub(r"W\w{2}-", r"Wed-", line_intake)
        line_intake = re.sub(r"Th\w{1}-", r"Thu-", line_intake)
        line_intake = re.sub(r"F\w{2}-", r"Fri-", line_intake)
        line_intake = re.sub(r"Sa\w{1}-", r"Sat-", line_intake)
        line_intake = re.sub(r"Su\w{1}-", r"Sun-", line_intake)

        line_intake = re.sub(r"San.*Hospital", r"", line_intake)
        line_intake = re.sub(r"Pay.*\d{6}[\s-]+\d{6}", r"", line_intake)
        line_intake = re.sub(r"Dates.*\/20\d{2}", r"", line_intake)

        line_intake = re.sub(r";", r":", line_intake)

        return line_intake
    
    line_intake = line_intake.strip()
    
    line_intake = re.sub(r"(?=\d)(\d{1})[_\s](\d{2})\s*(?=[A-Z])", r" \0 \1.\2 ", line_intake)

    return clean_more(remove_sludge(line_intake))


def filter_junk_old(line_intake):

    line_intake = re.sub(r"M\w{2}-", r"Mon-", line_intake)
    line_intake = re.sub(r"Tu\w{1}-", r"Tue-", line_intake)
    line_intake = re.sub(r"W\w{2}-", r"Wed-", line_intake)
    line_intake = re.sub(r"Th\w{1}-", r"Thu-", line_intake)
    line_intake = re.sub(r"F\w{2}-", r"Fri-", line_intake)
    line_intake = re.sub(r"Sa\w{1}-", r"Sat-", line_intake)
    line_intake = re.sub(r"Su\w{1}-", r"Sun-", line_intake)
        
    line_intake = re.sub(r"San.*Hospital", r"", line_intake)
    line_intake = re.sub(r"Pay.*\d{6}[\s-]+\d{6}", r"", line_intake)
    line_intake = re.sub(r"Dates.*\/20\d{2}", r"", line_intake)
    
    line_intake = re.sub(r"[,;!]", r":", line_intake)

    return line_intake

def token2regex(token, timecard, day_digits, month_digits, day, day_num, month_num):
    day_numeric_, month_numeric_ = day_digits, month_digits
    
    # logger.info(f'ERRORING LINE: token-->{token}, timecard-->{timecard}, day digits --> {day_numeric}, month digits --> {month_numeric_}, day-->\
    # {day}, daynum-->{day_num}, desc--> {description}'
    #            )
    
    tt = 'a3434 23442. Mon-14 Sent Home Early 4234244 Preceptor Pay 24432234 Paid Leave On-Call 20 Call Back 45 Missed Break 45 Missed Lunch 3244242342 Shift Leader CA Sick Paid Leave HRO/Benefit Non-Productive'
    response =  re.findall(r"([A-Za-z]{2,9}[\/\s-]*[A-Za-z]{3,}(\s*\d{2})?\s*([A-Za-z]{4}\s[A-Za-z]{5})?)", tt)
    capnames = ["".join(re.findall('[A-Z]+',text[0]))[:2] for text in response]
    capnames = list(filter(lambda x: len(x) == 2, capnames))
    t2regex_dict = dict(zip(capnames,np.full(len(capnames), {}))) # INITIALIZE OUTPUT DICTIONARY
    t2regex_dict['Standard'] = {}
    
    '''
    Here we disentangle the timecard into static data to avoid regex issues that have arisen regarding
    1 or 2 digit months or days that appear without spacing
    '''

    '''
    t2regex_dict has this format
    {'PP': {}, 'PL': {}, 'OC': {}, 'CB': {}, 'MB': {}, 'ML': {}, 'SL': {}, 'CA': {}, 'HR': {}, 'NP': {},  
    'SH':{}, Standard': {}}

    '''
         
                    
    if day_numeric_ == 1 and month_numeric_ == 1:

        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {

            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {
            'day':'(?P<Day>[A-Za-z]{3}-\d{1})',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day': '(?P<Day>[A-Za-z]{3}-\d{1})',
            'in_time_date':'(?P<In_Time_Date>\d{1}\/\d{1})',
            'in_time_hour': '(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date': '(?P<Out_Time_Date>\d{1}\/\d{1})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description': '(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }
       
                        
    elif day_numeric_ == 1 and month_numeric_ == 2:

        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day': '(?P<Day>[A-Za-z]{3}-\d{1})',
            'in_time_date':'(?P<In_Time_Date>\d{2}\/\d{1})',
            'in_time_hour': '(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date': '(?P<Out_Time_Date>\d{2}\/\d{1})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description': '(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }
            
    elif day_numeric_ == 2 and month_numeric_ == 1:

        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {

            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day':'(?P<Day>[A-Za-z]{3}-\d{2})',
            'in_time_date':'(?P<In_Time_Date>\d{1}\/\d{2})',
            'in_time_hour':'(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date':'(?P<Out_Time_Date>\d{1}\/\d{2})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1,2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',

        }
        
    elif day_numeric_ == 2 and month_numeric_ == 2:

        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {

            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {

            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day':'(?P<Day>[A-Za-z]{3}-\d{2})',
            'in_time_date':'(?P<In_Time_Date>\d{2}\/\d{2})',
            'in_time_hour':'(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date':'(?P<Out_Time_Date>\d{2}\/\d{2})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>\s*'+description+'\s*)',
            'dept':'(?P<Department>75\d{2})',

        }
        
    else:
        print ('Parsing Error - Improper Formatting of Input')
        
    
    return t2regex_dict

    # DATE: DEC 28
# THIS FUNCTION IS ONLY FOR LINES CONTAINING A TEXT DESCRIPTION
# SOME LINES WILL H

def token2regex_jobcode_5(token, timecard,  day_digits, month_digits, day, day_num, month_num):
    
    day_numeric_, month_numeric_ = day_digits, month_digits
    
    # job_code = str(job_code)
    
    print("WE ARE SPECIAL JOBCODE 5 TOKEN2REGEX")
    
    # logger.info(f'ERRORING LINE: token-->{token}, timecard-->{timecard}, day digits --> {day_numeric}, month digits --> {month_numeric_}, day-->\
    # {day}, daynum-->{day_num}, desc--> {description}'
    #            )
    
    tt = 'a3434 23442. Mon-14 Sent Home Early 4234244 Preceptor Pay 24432234 Paid Leave On-Call 20 Call Back 45 Missed Break 45 Missed Lunch 3244242342 Shift Leader CA Sick Paid Leave HRO/Benefit Non-Productive'
    response =  re.findall(r"([A-Za-z]{2,9}[\/\s-]*[A-Za-z]{3,}(\s*\d{2})?\s*([A-Za-z]{4}\s[A-Za-z]{5})?)", tt)
    capnames = ["".join(re.findall('[A-Z]+',text[0]))[:2] for text in response]
    capnames = list(filter(lambda x: len(x) == 2, capnames))
    t2regex_dict = dict(zip(capnames,np.full(len(capnames), {}))) # INITIALIZE OUTPUT DICTIONARY
    t2regex_dict['Standard'] = {}
    
    '''
    Here we disentangle the timecard into static data to avoid regex issues that have arisen regarding
    1 or 2 digit months or days that appear without spacing
    '''

    '''
    t2regex_dict has this format
    {'PP': {}, 'PL': {}, 'OC': {}, 'CB': {}, 'MB': {}, 'ML': {}, 'SL': {}, 'CA': {}, 'HR': {}, 'NP': {},  
    'SH':{}, Standard': {}}

    '''
                    

    #     description = 'Shift Leader'
    #     day = '(?P<Day>.*[A-Za-z]{3}-\d{1})'
    #     in_time_date = '(?P<In_Time_Date>\d{1,2}\/\d{1})'
    #     in_time_hour = '(?P<In_Time_Hour>\d{2}:\d{2})'
    #     out_time_date = '(?P<Out_Time_Date>\d{1,2}\/\d{1})'
    #     out_time_hour = '(?P<Out_Time_Hour>\d{2}:\d{2})'
    #     amount = '(?P<Amount>\d{1,2}.\d{2})'
    #     description  = '(?P<Description>'+description+')'
    #     dept = '(?P<Department>\d{4})'
    #     code = '(?P<Job_Code>\d{5})

    if day_numeric_ == 1 and month_numeric_ == 1:

        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {

            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{1})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',

            }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {

            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day': '(?P<Day>[A-Za-z]{3}-\d{1})',
            'in_time_date':'(?P<In_Time_Date>\d{1}\/\d{1})',
            'in_time_hour': '(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date': '(?P<Out_Time_Date>\d{1}\/\d{1})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1,2}[_\s\.;,]\d{2})',
            # 'description': '(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
        }

       
                        
    elif day_numeric_ == 1 and month_numeric_ == 2:

        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
            }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{1}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

                'day': '(?P<Day>[A-Za-z]{3}-\d{1})',
                'in_time_date':'(?P<In_Time_Date>\d{2}\/\d{1})',
                'in_time_hour': '(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
                'out_time_date': '(?P<Out_Time_Date>\d{2}\/\d{1})',
                'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
                'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
                # 'description': '(?P<Description>'+description+')',
                'dept':'(?P<Department>75\d{2})',
            }
            
    elif day_numeric_ == 2 and month_numeric_ == 1:
            
        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
            }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
        }
        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day':'(?P<Day>[A-Za-z]{3}-\d{2})',
            'in_time_date':'(?P<In_Time_Date>\d{1}\/\d{2})',
            'in_time_hour':'(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date':'(?P<Out_Time_Date>\d{1}\/\d{2})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1,2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',

        }
        
    elif day_numeric_ == 2 and month_numeric_ == 2:
            
        t2regex_dict['PP'] = t2regex_dict['ML'] = t2regex_dict['MB'] = t2regex_dict['PL'] = t2regex_dict['HR'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{1}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
            }

        t2regex_dict['OC'] = t2regex_dict['CA'] = {
            'day':'(?P<Day>\s*[A-Za-z]{3}-\d{2}\s*)',
            'in_time_date':'(?P<In_Time_Date>)',
            'in_time_hour':'(?P<In_Time_Hour>)',
            'out_time_date':'(?P<Out_Time_Date>)',
            'out_time_hour':'(?P<Out_Time_Hour>)',
            'amount':'(?P<Amount>\d{2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',
        }

        t2regex_dict['SH'] = t2regex_dict['SL'] = t2regex_dict['CB'] = t2regex_dict['NP'] = t2regex_dict['Standard'] = {

            'day':'(?P<Day>[A-Za-z]{3}-\d{2})',
            'in_time_date':'(?P<In_Time_Date>\d{2}\/\d{2})',
            'in_time_hour':'(?P<In_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'out_time_date':'(?P<Out_Time_Date>\d{2}\/\d{2})',
            'out_time_hour':'(?P<Out_Time_Hour>\d{2}[\.\;\!\:]?\d{2})',
            'amount':'(?P<Amount>\d{1,2}[_\s\.;,]\d{2})',
            # 'description':'(?P<Description>'+description+')',
            'dept':'(?P<Department>75\d{2})',

        }
        
    else:
        print ('Parsing Error - Improper Formatting of Input')
        
    
    return t2regex_dict