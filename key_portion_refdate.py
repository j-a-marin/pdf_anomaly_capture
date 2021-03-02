#key_portion_refdate.py

    if not refdates:
        key_page[page_num]['status'] = 'HR Table'
        return key_page
        
    namz = ['Day','In_Time','Out_Time','Amount','Description','Department','Job_Code','OT']
    parsed_date_list = []

    if refdates:

        refdate_split = re.split(r'(?!^)(?=\w{3}-\d{1,2})', refdates[0])

        for line in refdate_split:

            print ('refdate parsing', line.strip())

#             assert type(line) == str, 'line entering parse from page processing is not a string'
#             assert type(timecard) == str, 'timecard entering parse from page processing is not a string'
#             assert type(job_code) == str, 'job_code entering parse from page processing is not a string'

            parsed_date_list.append(parse_timecard_line_v2(line, timecard, job_code)) 

    print ('parsed date list -->', parsed_date_list)
    
    temp_df = pd.concat(parsed_date_list, ignore_index=True, sort=False)

            remodelled = []

        for line in refdate_split_filter1:

            remodelled.append(list(reform_produce(line.strip(), timecard)))

        print (remodelled)

        for line in remodelled:

            print ("****", line)

            if isinstance(line, dict):

                for buff_line in handle_buffer_entries(line):

                    parsed_date_list.append(parse_timecard_line_v2(buff_line, timecard, job_code))
#     
            elif isinstance(line, str):

                parsed_date_list.append(parse_timecard_line_v2(line, timecard, job_code)) 

            else:

            	raise ValueError("Improper String Object processed as PDF line")

