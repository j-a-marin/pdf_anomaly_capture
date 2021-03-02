'''
This program runs the others..
'''
import os, glob, re, pickle
import numpy as np
import pandas as pd

import argparse

from datetime import datetime
from collections import defaultdict
overview_dict = defaultdict(list)

from tqdm import tqdm

from lib.parse_helpers import parse_timecard_line_v2
from lib.process_csv import process_csv, extract_text_multipage_v5, process_alt_df_special, timecard2dict_reporting, fix210
from setlog import setup_log
logger = setup_log()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog='Document to Excel and Overview Processer', 
        description='''Takes Processed Document and Creates Excel Tables by Integrating
        Source(s) of Content related to a PDF
        The Doc Processor can also be triggered using the --run flag
        ''')
    #We use the optional switch -- otherwise it is mandatory
    parser.add_argument('--run', '-r', action='store_true', help='Run Doc Processor')

    # NOTE - NO FLAG INCLUDED MEANS FALSE 
    #Run the argument parser
    args = parser.parse_args()
    # print (args.run)

    if args.run:

        # os.system("rm alternate*")
        os.system("python Doc_Processer.py -b 101 -e 106")

    Alt_Dict_Last = sorted([f for f in glob.glob('*') if re.search(r"alternate_key_page.*\d{2}:\d{2}\.pkl", f) ], 
        key=lambda x: re.search(r"\d{2}:\d{2}",x)[0], reverse=True)

    Alt_Dict_Last = Alt_Dict_Last[0]

    print (Alt_Dict_Last)

    pkl_file = open(Alt_Dict_Last, 'rb')
    alternate_key_df = pickle.load(pkl_file)

        '''
    ONLY RUN THIS AFTER THE LATEST PICKLED ALTERNATE DATA DICT HAS BEEN LOADED 
    LOOP HAS TWO PURPOSES 
    1) CREATE CONCATENATED FINAL PRODUCT EXCEL SHEET
    2) CREATE STATUS OVERVIEW TABLE WITH ENTRIES PAGE,STATUS,TIMECARD,DATES,NO.ENTRIES,SPECIAL HANDLING

    THE VERSION BELOW WORKED ON TEST DRAFT 

    NEW VERSION UNDERNEATH

    '''

    output = []
    overdict = defaultdict(dict)

    csv_aws_file_locus = '../ON_CALL_CASE/processed/*'

    for f in tqdm(glob.glob(csv_aws_file_locus)[:5]): 
        
        doc_id = re.findall(r'.*bling_(\d{3})_.*', os.path.splitext(os.path.basename(f))[0])[0]

        if alternate_key_df[doc_id]:

            print ('the alt df', alternate_key_df[doc_id])

            ADDITION TO HANDLE 210 EXCEPTIONALLY

            if doc_id == '210':

                alt_df_page = fix210

                output.append(alt_df_page)
         
                overdict[doc_id]['page'] = int(doc_id)
                overdict[doc_id]['timecard'] = alternate_key_df[doc_id]['timecard']
                overdict[doc_id]['status'] = alternate_key_df[doc_id]['status']
                overdict[doc_id]['dates'] = timecard2dict_reporting(alternate_key_df[doc_id]['timecard'])
                overdict[doc_id]['no. entries'] = len(fix210)
                overdict[doc_id]['special handling'] = 'Special Handling'
                continue 


            if alternate_key_df[doc_id]['status'] == "HR Table":

                pass
        
                overdict[doc_id]['page'] =  int(doc_id)
                overdict[doc_id]['timecard'] = alternate_key_df[doc_id]['timecard']
                overdict[doc_id]['status'] = alternate_key_df[doc_id]['status']
                overdict[doc_id]['dates'] = timecard2dict_reporting(alternate_key_df[doc_id]['timecard'])
                overdict[doc_id]['no. entries'] = np.nan
                overdict[doc_id]['special handling'] = np.nan

            try:

                # Here we concede to the quality of AWS - they have the full lines of the csv
                if not alternate_key_df[doc_id]['refdate'].empty:

                    overdict[doc_id]['cat'] = 'try zone'

                    if doc_id == '210':

                        dfx = fix210

                        columnTitles = ['Time_Card_Year', 'Time_Card_Period', 'Day', 'In_Time_Date', 'In_Time_Hour', 'Out_Time_Date', 
                    'Out_Time_Hour', 'Amount', 'Description', 'Department', 'Job_Code']

                        dfx = dfx.reindex(columns=columnTitles)
                        dfx.reset_index(inplace=True)
                        dfx.drop(['index'], axis=1, inplace=True)

                        output.append(dfx)
            
                        overdict[doc_id]['page'] = int(doc_id)
                        overdict[doc_id]['timecard'] = alternate_key_df[doc_id]['timecard']
                        overdict[doc_id]['status'] = alternate_key_df[doc_id]['status']
                        overdict[doc_id]['dates'] = timecard2dict_reporting(alternate_key_df[doc_id]['timecard'])
                        overdict[doc_id]['no. entries'] = len(dfx)
                        overdict[doc_id]['special handling'] = 'Special Handling'

                    else:

                    output.append(process_csv(f, alternate_key_df[doc_id]['timecard']))

                    overdict[doc_id]['page'] = int(doc_id)
                    overdict[doc_id]['timecard'] = alternate_key_df[doc_id]['timecard']
                    overdict[doc_id]['status'] = alternate_key_df[doc_id]['status']
                    overdict[doc_id]['dates'] = timecard2dict_reporting(alternate_key_df[doc_id]['timecard'])
                    overdict[doc_id]['no. entries'] = len(alternate_key_df[doc_id]['refdate'])
                    overdict[doc_id]['special handling'] = np.nan 
                    
            except Exception as e:

                overdict[doc_id]['cat'] = 'except zone'

                
                if not alternate_key_df[doc_id]['refdate'].empty:
                
                    logger.error(f'{doc_id} AWS errored here but we have a timecard thusly accessed the alternate dict {e}')
                    alt_df_page = process_alt_df_special(alternate_key_df[str(doc_id)]['refdate'], alternate_key_df[str(doc_id)]['timecard'])

                    output.append(alt_df_page)
             
                    overdict[doc_id]['page'] = int(doc_id)
                    overdict[doc_id]['timecard'] = alternate_key_df[doc_id]['timecard']
                    overdict[doc_id]['status'] = alternate_key_df[doc_id]['status']
                    overdict[doc_id]['dates'] = timecard2dict_reporting(alternate_key_df[doc_id]['timecard'])
                    overdict[doc_id]['no. entries'] = len(alternate_key_df[doc_id]['refdate'])
                    overdict[doc_id]['special handling'] = 'Special Handling'

                else:
                    
                    logger.error(f'{doc_id} neither AWS nor alt dict available {e}')

                    pass

    ramirez_full_excel = pd.concat(output, sort=False)


    dfs = {'XYZ Full Records': XYZ_full_excel}

    filename = f'./XYZ_{datetime.now().date()}.xlsx'

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=False)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
            
    writer.save()


    '''
    SAVE OVERVIEW DOCUMENT
    '''
    overdict_df = pd.DataFrame(overdict).T
    overdict_df = overdict_df.set_index('page')
    columnTitles = ['timecard', 'status', 'special handling', 'no. entries', 'dates']
    overdict_df = overdict_df.reindex(columns=columnTitles)

    dfs = {'Summary Document': overdict_df}

    filename = f'./data_overview_{datetime.now().date()}.xlsx'

    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=True)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
                )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width

    writer.save()

    assert len(glob.glob(csv_aws_file_locus)) == len(glob.glob(r'../ON_CALL_CASE/*bling*'))\
    , 'assertion failure: number of csv files and pdf files do not match'

    if len(glob.glob(csv_aws_file_locus)) != overdict_df.shape[0]:
        missing_values = set(list(range(101,251))).difference(overdict_df.index.values)

    print (" ALERT ********** PROCESSING COMPLETE WITH MISSING VALUES: ", missing_values)



