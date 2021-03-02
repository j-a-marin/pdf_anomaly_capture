# process_csv.py

# MON DEC 28

import pandas as pd
import numpy as np
import datetime
from dateutil.parser import parse
import sys, os, glob, re, io

from collections import defaultdict

from collections import Counter
from collections import OrderedDict
import bs4 as bs
import requests
import unicodedata
import lxml

supp210 = {'Day': ['Sun-22', 'Sun-22', 'Sun-22', 'Mon-23', 'Mon-23', 'Mon-23', 'Tue-24', 'Tue-24', 'Mon-30',
                  'Mon-30', 'Mon-30', 'Tue-31', 'Tue-31', 'Tue-31', 'Wed-31', 'Wed-31', 'Wed-31'],
           'In_Time_Date': ['5/22', '5/22', np.nan, '5/23', '5/23', np.nan, '5/24', np.nan, '5/30', '5/30', np.nan,
                            '5/31', '5/31', np.nan, '6/1', '6/1', np.nan],
           'In_Time_Hour': ['06:31', '14:00', np.nan, '06:30', '13:00', np.nan, '06:23', np.nan, '06:15', '13:00', np.nan,
                            '06:17', '13:00', np.nan, '06:20', '13:30', np.nan],
           'Out_Time_Date': ['5/22', '5/22', np.nan, '5/23', '5/23', np.nan, '5/24', np.nan, '5/30', '5/30', np.nan,
                            '5/31', '5/31', np.nan, '6/1', '6/1', np.nan],
           'Out_Time_Hour': ['13:30', '17:57',  np.nan, '12:30', '19:00', np.nan, '10:25', np.nan, '12:30', '18:46', np.nan,
                             '12:30','18:59', np.nan, '13:00', '18:51', np.nan],
           'Amount':['7.00', '3.90', '12.00', '6.00', '6.00', '12.00', '4.00', '8.00', 
                     '6.30', '5.70', '12.00', '6.20', '6.00', '12.00', '6.70', '5.30', '12.00'],
           'Description': ['Shift Leader', 'Shift Leader', 'On-Call', 'Shift Leader', 'Shift Leader', 'On-Call',
                          'Shift Leader', 'Paid Leave',  'Shift Leader', 'Shift Leader', 'On-Call',
                           'Shift Leader', 'Shift Leader', 'On-Call', 'Shift Leader', 'Shift Leader', 'On-Call'],
           'Department': np.repeat('7560',17), 
           'Job_Code': np.repeat('147',17),
           'Time_Card_Year': np.repeat('2016',17),
           'Time_Card_Period':np.repeat('12',17)
          }

fix210 = pd.concat( [pd.DataFrame(supp210)], sort=False)

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

def timecard2dict_reporting(timecard):

    if isinstance(timecard,list):
        timecard=timecard[0]

    if timecard:
        timecard_year = int(timecard[:-2])
        timecard_number = int(timecard[-2:])
        timecard_number_adjusted = timecard_number * 2
    
    end_timecard_window = weekly_mapping(timecard_year)['Week ' + f'{timecard_number_adjusted:02}'][0]
    # print (end_timecard_window)
    end_date = parse(end_timecard_window)
    no_of_days = datetime.timedelta(days=15) if timecard_number_adjusted !=2 else datetime.timedelta(days=22)
    begin = (end_date - no_of_days)


    return (begin.strftime('%B %d, %Y'), end_date.strftime('%B %d, %Y'))

def process_alt_df_special(special_df, timecard):
    
    df_alt = special_df
    df_alt['Time_Card_Year'] = timecard[:4]
    df_alt['Time_Card_Period'] = timecard[-2:]
    
    columnTitles = ['Time_Card_Year', 'Time_Card_Period', 'Day', 'In_Time_Date', 'In_Time_Hour', 'Out_Time_Date', 
                'Out_Time_Hour', 'Amount', 'Description', 'Department', 'Job_Code']

    df_alt = df_alt.reindex(columns=columnTitles)
    df_alt.reset_index(inplace=True)
    df_alt.drop(['index'], axis=1, inplace=True)
    return df_alt


def extract_text_multipage_v5(pdf_path, output_dict):
    timecard_dates_dict = output_dict
    numbering_adjustment = int(os.path.splitext(pdf_path)[0][-3:])
    for ix, page in enumerate(extract_text_by_page(pdf_path)):    
        timecard_dates_dict[ix + numbering_adjustment]['timecard'] = re.findall(r"Timecard\s+for\s+Pay\s+Period.*?(\d{6})",page)
        timecard_dates_dict[ix + numbering_adjustment]['refdate'] = re.findall(r"\w{3}-\s*\d{1,2}\s*\d+/\d{1,2}\s*\d{2}:\d{2}",page)

    return timecard_dates_dict
    

def process_csv(path, timecard):

    namz = ['Day','In_Time','Out_Time','Amount','Description','Department','Job_Code','OT']

    def trim_all_columns(df):
        """
        Trim whitespace from ends of each value across all series in dataframe
        """
        trim_strings = lambda x: x.strip("!_:;~`*-") if isinstance(x, str) else x
        return df.applymap(trim_strings)

    dfx = pd.read_csv(path,  names=namz, header=None)[2:]
    dfx = trim_all_columns(dfx)
    
    patternKeep = r"^[A-Za-z]{3}-.*"
    filter = dfx.Day.str.contains(patternKeep, regex=True, na=False)
    # filter
    try:
        dfx = dfx.loc[filter & dfx.isnull()]
    except:
        pass

    dfx=dfx[filter]
    
    patternKeep = r".*[a-zA-Z]{3}-\s*\d{1,3}.*"
    filter = dfx.Day.str.contains(patternKeep, regex=True)
    try:
        dfx = dfx[filter]
    except:
        logger.info('ERROR THAT MISSES LARGE PAGES')
        pass
    
#     for i in range(1,3):
#         dfx.iloc[:,1] = dfx.iloc[:,1].astype(str).str.replace(";",":",regex=False)

#     for ix, c in dfx.iterrows():
#         if "." not in str(c.Amount):
#             c.Amount = str(c.Amount) + "." + str(c.Description)
#             c.Description = ''
#             c.Description = np.NaN
#         if c.Department is np.NaN:
#             c.Department = c.Job_Code
#             c.Job_Code = c.OT
#             c.OT = np.NaN
#         if 'Call' in c.Amount:
#             c.Amount = c.Amount.replace('Call','')
#             c.Description = 'Call' + ' ' + c.Description
        
#         if 'Paid' in c.Amount:
#             c.Amount = c.Amount.replace('Paid','')
#             c.Description = 'Paid' + ' ' + c.Description
            
    
    def defect_Amount_Description(dfx):
        
        pattern_amount_defect = r"\."
        filter_temp = dfx.Amount.str.contains(pattern_amount_defect, regex=True)
        for ix, row in dfx[~filter_temp].iterrows():
            dfx.loc[ix,'Amount'] = ".".join([row.Amount.strip(), row.Description.strip()])
            # this should sub to preserve rather than destroy
            dfx.loc[ix,'Description'] = dfx.loc[ix,'Department']
            # here I attempt to incorporate one of the missing department scenarios in this compound defect
            dfx.loc[ix,'Department'] = dfx.loc[ix,'Job_Code']
            dfx.loc[ix,'Job_Code'] = dfx.loc[ix,'OT'] 
            dfx.loc[ix,'OT'] = np.nan

#         pattern_amount_defect = r"\d{1,2}\.\d{2}\s*[\w\s-]+"
#         filter_temp = dfx.Amount.str.contains(pattern_amount_defect, regex=True)
#         for ix, row in dfx[filter_temp].iterrows():
# #             dfx.loc[ix,'Amount'] = re.search(r"(\d{1,2}\.\d{2})\s*([\w\s-]+)", row.Amount).group(1)
#             print ('focus',re.search(r"(\d{1,2}\.\d{2})\s*([\w\s-]+)", row.Amount))
    
        pattern_amount_defect = r"\d{1,2}\.\d{2}\s*\w+"
        filter_temp = dfx.Amount.str.contains(pattern_amount_defect, regex=True)
        for ix, row in dfx[filter_temp].iterrows():
            dfx.loc[ix,'Amount'] = re.search(r"(\d{1,2}\.\d{2})\s*([\w\s-]+)", row.Amount).group(1)
            dfx.loc[ix,'Description'] = re.search(r"(\d{1,2}\.\d{2})\s*([\w\s-]+)", row.Amount).group(2)+\
            " " + re.search(r"\s*(\w+)\s*", row.Description).group(1)   
#             if re.search(r"(\d{1,2}\.\d{2})\s*([\w\s-]+)", row.Amount).group(2) is not '':
#                 dfx.loc[ix,'Description'] = re.search(r"(\d{1,2}\.\d{2})\s*([\w\s-]+)", row.Amount).group(2)
#             else:
#                 dfx.loc[ix,'Description'] = np.nan

        return dfx

    def defect_Missing_Department(dfx_):

        pattern_department_wander = r"\d{4}"

        filter_dept = dfx_.Department.str.contains(pattern_department_wander, na=False, regex=True)
        filter_desc= dfx_.Description.str.contains(pattern_department_wander, na=False, regex=True)

        for ix, row in dfx_[~filter_dept & filter_desc].iterrows():
            dfx_.loc[ix, 'Job_Code'] = re.search(r"\d{3}", row.Department)[0]
            dfx_.loc[ix, 'Department'] = re.search(r"\d{4}", row.Description)[0]
            dfx_.loc[ix, 'Description'] = re.sub(r"\d{4}", r"", row.Description)
            
            if len(dfx_.loc[ix, 'Job_Code']) > len(dfx_.loc[ix, 'Department']):
                dfx_.loc[ix, 'Job_Code'], dfx_.loc[ix, 'Department'] = \
                dfx_.loc[ix, 'Department'], dfx_.loc[ix, 'Job_Code']
        
        return dfx_

#     def defect_Missing_Department(dfx):
                
#         missing_dept_defect = r".*\d{4}.*"
        
#         filter_temp = dfx.Department.str.contains(missing_dept_defect, na=False, regex=True)
#         for ix, row in dfx[~filter_temp].iterrows():
#             dfx.loc[ix,'Amount'] = ".".join([row.Amount.strip(), row.Description.strip()])
#             dfx.loc[ix,'Description'] = np.nan
#             dfx.loc[ix,'Department'] = dfx.loc[ix,'Department']
#             dfx.loc[ix,'Job_Code'] = int(147) 
#             dfx.loc[ix,'OT'] = np.nan
            
#         return dfx
    
    def defect_Date_Time_Separate(dfx):
    
        pattern_date_defect = r".*\d{1,2}\/\d{1,2}\s+\d{2}:\d{2}.*"

        filter_temp = dfx.In_Time.str.contains(pattern_date_defect, na=False, regex=True)

        for ix, row in dfx[~dfx.In_Time.isnull() & ~filter_temp].iterrows():
            dfx.loc[ix,'In_Time']= re.sub(r".*(\d{1,2}\/\d{1,2}).*(\d{2}:\d{2}).*", r"\1 \2", row.In_Time)

        filter_temp = dfx.Out_Time.str.contains(pattern_date_defect, na=False, regex=True)

        for ix, row in dfx[~dfx.Out_Time.isnull() & ~filter_temp].iterrows():
            dfx.loc[ix,'Out_Time']= re.sub(r".*(\d{1,2}\/\d{1,2}).*(\d{2}:\d{2}).*", r"\1 \2", row.Out_Time)

        return dfx
    
    def createNA(dfx):
        dfx = dfx.replace(['',' '], np.nan) 
        return dfx

#         for ix, c in dfx.iloc[np.where(dfx.Amount.apply(lambda x: re.search(r'[A-Z]',x)))[0]].iterrows():

            
#         try:
#             dfx[~filter_2]['Amount']  = dfx[~filter_2].Amount.str.extract(r'.*(\d{1}).*')
#             dfx[~filter_2]['Description'] = dfx[~filter_2].Description.str.extract(r'.*(\d{2}).*')
# #             dfx[~filter_2] = tempAmt_1 + tempAmt_2
#         except:
#             pass
#         return dfx

    dfx = createNA(defect_Missing_Department(defect_Date_Time_Separate(defect_Amount_Description(dfx))))
    
#     return (dfx)
    
    
    dfx[['In_Time_Date','In_Time_Hour']] = dfx.In_Time.str.split(expand=True)
    dfx[['Out_Time_Date','Out_Time_Hour']] = dfx.Out_Time.str.split(expand=True)

    dfx.drop(['OT','In_Time',"Out_Time"], axis=1, inplace=True)
    

#     doc_id = int(re.findall(r'.*bling_(\d{2,3})_.*', os.path.splitext(os.path.basename(path))[0])[0])

#     def timecard_column(doc_id):
        
#         dfx['Time_Card_Year'] = timecard_dates_dict[doc_id]['timecard'][0][:4]
        
#         dfx['Time_Card_Period'] = timecard_dates_dict[doc_id]['timecard'][0][-2:]

#         return dfx
    
#     timecard_extant = [k for k,v in timecard_dates_dict.items() if len(v['timecard']) > 0]
    
# #     timecard_derivative = [k for k,v in timecard_dates_dict.items() if len(v['timecard']) == 0 and len(v['refdate']) > 0]
    
#     if doc_id in timecard_extant:
#         dfx = timecard_column(doc_id)

    def timecard_columns(timecard):
        
        dfx['Time_Card_Year'] = timecard[:4]
        
        dfx['Time_Card_Period'] = timecard[-2:]

        return dfx
    
    dfx = timecard_columns(timecard)
        
    columnTitles = ['Time_Card_Year', 'Time_Card_Period', 'Day', 'In_Time_Date', 'In_Time_Hour', 'Out_Time_Date', 
                    'Out_Time_Hour', 'Amount', 'Description', 'Department', 'Job_Code']

    dfx = dfx.reindex(columns=columnTitles)
    dfx.reset_index(inplace=True)
    dfx.drop(['index'], axis=1, inplace=True)

    return dfx


if __name__ == '__main__':

    from collections import defaultdict

    timecard_dates_dict_v2 = defaultdict(dict)

    for f in glob.glob(r'./*bling*'): 

        extract_text_multipage_v5(f, timecard_dates_dict_v2)