#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Usage -

Similar to the Linux 'column' command but our command only handles csv-formatted data.
But it can handle embedded commas in the csv input.
You can call this script as a command or a module:

Command:
    %(scriptName)s csv_file_name
    cat csv_file_name | %(scriptName)s
    %(scriptName)s < csv_file_name

    Read from stdin or csv_file_name.

    Blank lines will be printed out and not ignored.

    Fields with embedded commas must be double-quoted, not single-quoted:
    echo test1,"test2,200",test3 | %(scriptName)s

    But for strings from stdin, you must escape the quotes to shield them from the shell:
    echo test1,\\\"test2,200\\\",test3 | %(scriptName)s
    Or surround the double-quotes items with single quotes:
    echo \\\'test1,"test2,200",test3\\\' | %(scriptName)s

Module usage:
    The columnize_output() function can process a Python list of csv strings.
    The columnize_output() function can also process a Python list of lists of basic data types, e.g., string, int.
    The columnize_output() function returns a Python list of columnized strings.
    You can pass an optional filename to columnize_output() in the save_filename param and columnize_output() will create a text file of the output in addition to returning a Python list of the output.

justify_cols:
    The columnize_output() justify_cols param specifies how the columns will be formatted for output:
    
    L = left-justify
    R = right-justify
    '   ' = 3 blank spaces between columns.
    
    The default is to have one space between columns.
    
    The max column width of each column is set to the longest string in the column.
    
    Example:
    
    "L,R,R,L,   ,R" =
    
              col1         col2    col3 col4          col5   col6
              test1       test2   test3 test4        test5  test6
              test123 test45678 test789 test0123   test456 test78
    Spacing:  777777719999999991777777718888888833377777771666666
    
    If you have more columns than the justify_cols specifies, the rightmost justify will be carried forward and used for the extra columns.  In the above example, there are 5 L's or R's but there are 6 columns.  So the R for col5 is carried forward and used for col6.  Most output will use "L,R" because most tables use this format.

    If a row contains one string or a row contains one list containing one string, the string will be output as is and not be aligned.  This will allow you to interleave aligned-columned rows with plain text rows.


Debugging this script:
    %(scriptName)s --debug ...
    Output debug trace messages.

Testing this script:
    %(scriptName)s --test file csv_test_file
    Test file input method.

    %(scriptName)s --test llt csv_test_file
    Test list_of_list input method.

    %(scriptName)s --test lcs csv_test_file
    Test list_of_csv_strings input method.

Test the following:
    columns.py  --test file columns.py_list_of_csv_strings_test
    cat columns.py_list_of_csv_strings_test | columns.py  --test file
    columns.py  --test lcs columns.py_list_of_csv_strings_test
    columns.py  --test llt columns.py_list_of_csv_strings_test

"""

import sys
import os
import re
import csv
import string
import getopt
from logging_wrappers import debug_run_status, debug_option, reportError, reportWarning
import select
import types


scriptName = os.path.basename(os.path.realpath(__file__))
scriptDir = os.path.dirname(os.path.realpath(__file__))

#=========================================================

# input_data can be either:
# list of csv strings
# list of lists of non-csv strings

def save_input_data_to_csv_file(input_data=[], csv_filename=''):
    if csv_filename == '':
        csv_filename = scriptName + '.csv'

    if not re.search('\.csv$', csv_filename):
        csv_filename += '.csv'

    if 'list' not in str(type(input_data)):
        print(("ERROR: input_data must be a list but is not. Type = ", str(type(input_data))))
        sys.exit(1)

    list_of_csv_strings = []
    if 'str' in str(type(input_data[0])):
        list_of_csv_strings = input_data
    elif 'list' in str(type(input_data[0])):
        for row in input_data:
            list_of_csv_strings.append(','.join(map(str,row)))
    else:
        print(("ERROR: input_data is a list but is not a list of string or a list of list but is a list of type = ", str(type(input_data[0]))))
        sys.exit(1)

    with open(csv_filename, 'w') as fd:
        for row in list_of_csv_strings:
            fd.write(row + '\n')

#=========================================================

debug = False
test_mode = ''

# Handles uneven rows, e.g., 3 columns in one row and 6 columns in another row.

# Non-string elements will be converted to strings before columnizing.

# Returns a list of strings, each string row contains well-spaced columnize_outputd fields.

# input_data can be either:
# list of csv strings
# list of lists of non-csv strings

def columnize_output(input_data=[], justify_cols='L,R', save_filename=''):
    global debug

    # print debug_run_status("columnize_output")

    debug = debug_option()

    rc = 0

    list_of_lists_of_strings = []
    columnized_output_list = []

    if debug: print("Entering columnize_output")
    if debug: print(("input_data = " , input_data))

    # print(152, input_data)
    # print(153, type(input_data))

    if 'list' in str(type(input_data)):
        if 'str' in str(type(input_data[0])):
            for row in input_data:
                for entry in csv.reader([row], skipinitialspace=True):
                    list_of_lists_of_strings.append(entry)
        if 'list' in str(type(input_data[0])):
            list_of_lists_of_strings = input_data

    else:
        if input_data == sys.stdin:
            reader = csv.reader(input_data)
            for entry in reader:
                if debug: print(('49', entry))
                list_of_lists_of_strings.append(entry)

        elif os.path.exists(input_data):
            csvfile = open( input_data, 'rb')
            reader = csv.reader( csvfile )
            for entry in reader:
                if debug: print(('49', entry))
                list_of_lists_of_strings.append(entry)
            csvfile.close()

        else:
            usage()

    if test_mode != '' or debug == True:
        print("All input should be in list_of_lists format at this point:")
        print(("input_data = ", input_data))
        # print list_of_lists_of_strings
        for row in list_of_lists_of_strings:
            print(row)

    if len(list_of_lists_of_strings) == 0:
        msg = "len(list_of_lists_of_strings) == 0"
        reportError(msg, mode='return_msg_only')
        return 1, "line 195"

    if save_filename != '':
        save_input_data_to_csv_file(input_data=list_of_lists_of_strings, csv_filename=save_filename)

    justify_cols_list = justify_cols.split(',')
    columnized_output_list_of_strings = []
    curr_max_num_cols = 0
    row_num = 0
    # Loop through all rows and if they don't all have the same list length, find out the max number of columns needed.
    for index in range(len(list_of_lists_of_strings)):
        row = list_of_lists_of_strings[index]
        # print(201, row)

        if 'list' in str(type(row)):
            if len(row) == 1:
                continue
        elif 'str' in str(type(row)):
            continue

        for column_index in range(len(list_of_lists_of_strings[index])):
            if list_of_lists_of_strings[index][column_index] == None:
                list_of_lists_of_strings[index][column_index] = ''
        if debug: print(("68", row))
        if 'list' not in str(type(row)):
            reportError("Outer list row is not a list--  Row type: " + str(type(row)) + ".  Row num: " + str(row_num) + ".  Row: " + str(row))
            return 1, "line 221"

        row_num += 1
        if curr_max_num_cols == 0:
            curr_max_num_cols = len(row)
            continue
        if len(row) == curr_max_num_cols:
            continue
        # print "debug: " , len(row) , curr_max_num_cols
        if len(row) == curr_max_num_cols:
            continue
        if len(row) > curr_max_num_cols:
            rc = 2
            reportWarning("Detected in columnize_output(), row " + str(row_num) + " contains an extra column: " + str(len(row)) + " instead of " + str(curr_max_num_cols) + ".  Row: " + str(row) + ".  Pad all previous rows and continue.")
            curr_max_num_cols = len(row)
        else:
            rc = 2
            reportWarning("Detected in columnize_output(), row " + str(row_num) + " is missing a column: " + str(len(row)) + " instead of " + str(curr_max_num_cols) + ".  Row: " + str(row) + ".  Will pad the row and continue.")
        for index2 in range(len(list_of_lists_of_strings)):
            # print "len: " + str(len(list_of_lists_of_strings[index2]))
            # print "len: " + str(list_of_lists_of_strings[index2])
            while len(list_of_lists_of_strings[index2]) < curr_max_num_cols:
                list_of_lists_of_strings[index2].append('')

    # Pad our justify list if padding was done.
    while len(justify_cols_list) < curr_max_num_cols:
        justify_cols_list.append(justify_cols_list[-1])

    # Determine the max num of characters for each column.
    max_col_widths = []
    for row in list_of_lists_of_strings:
        if len(row) == 1:
            continue
        for index in range(curr_max_num_cols):
            # print index
            # print len(row)
            # print row
            # print curr_max_num_cols
            if type(row[index]) is not string:
                row[index] = str(row[index])
            if len(max_col_widths) < len(row):
                max_col_widths.append(len(row[index]))
            else:
                if max_col_widths[index] < len(row[index]):
                    max_col_widths[index] = len(row[index])

    # for col in max_col_widths: print col
    # print 'end of list'

    # Create/format the table.
    columnized_output_list_of_strings = []
    for row in list_of_lists_of_strings:
        # If a row only has one string in it or the row contains one list with one string in it, output the string as is and don't align it.  Treat it like a comment or title row.
        if 'list' in str(type(row)):
            if len(row) == 1:
                columnized_output_list_of_strings.append(row[0])
                continue
        elif 'str' in str(type(row)):
            columnized_output_list_of_strings.append(row)
            continue

        line = ''
        justify_col_curr = -1
        curr_col = -1
        while True:
            curr_col += 1
            if curr_col >= len(max_col_widths):
               break
            if line != '':
               line += ' '
            if justify_col_curr < (len(justify_cols_list)-1):
               justify_col_curr += 1
            if justify_cols_list[justify_col_curr] == 'L':
                line += "".join(row[curr_col]).ljust(max_col_widths[curr_col]+1)
            elif justify_cols_list[justify_col_curr] == 'R':
                line += "".join(row[curr_col]).rjust(max_col_widths[curr_col]+1)
            else:
                found = re.search('^( +)$', justify_cols_list[justify_col_curr])
                if found:
                    line += found.group(1)
                    curr_col -= 1
                else:
                    print("ERROR: Unrecognized justify param = ", justify_cols_list[justify_col_curr])
                    sys.exit(1)


        # print "139", line
        columnized_output_list_of_strings.append(line)


    if debug: print(("142", len(columnized_output_list_of_strings)))

    if save_filename != '':
        if not re.search('\.txt$', save_filename):
            save_filename += '.txt'

        with open(save_filename, 'w') as fd:
            for row in columnized_output_list_of_strings:
                fd.write(row + '\n')

    return rc,columnized_output_list_of_strings


#========================================================

def usage():
    print((__doc__ % {'scriptName' : scriptName,}))
    sys.exit(1)

#========================================================

if __name__ == '__main__':

    debug = debug_option()

    if len(sys.argv) <= 1 and not select.select([sys.stdin,],[],[],0.0)[0]:
        usage()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["test=", "debug"])
    except getopt.GetoptError as err:
        usage()

    input_data = ''
    list_of_lists_test_input_file = ''
    list_of_lists_of_strings = []
    list_of_csv_strings_test_input_file = ''
    list_of_csv_strings = []
    test_mode = ''
    arg = ''
    opt = ''
    for opt, arg in opts:
        # print "arg = " + arg
        if opt == '--test':
            test_mode = arg
            if arg == 'llt':
                list_of_lists_test_input_file = args[0]
            if arg == 'lcs':
                list_of_csv_strings_test_input_file = args[0]
            if arg == 'file':
                pass
            continue
        if opt == '--debug':
            debug = True
            continue

    if debug: print(("len(sys.argv) = " + str(len(sys.argv))))
    if debug:
        print(('args', args))
        if len(args) > 0: print(("args last index = " + str(sys.argv.index(args[0]))))

    if test_mode != '':
        if list_of_lists_test_input_file != '':
            for line in open(list_of_lists_test_input_file, 'r').read().splitlines():
                if debug: print(("242", line))
                for entry in csv.reader([line], skipinitialspace=True):
                    if debug: print(("244", entry))
                list_of_lists_of_strings.append(entry)
            input_data = list_of_lists_of_strings

        elif list_of_csv_strings_test_input_file != '':
            list_of_csv_strings = open(list_of_csv_strings_test_input_file, 'r').read().splitlines()
            input_data = list_of_csv_strings
        else:
            print("ERROR: Undefined test mode.")
            sys.exit(1)

    else:

        if len(args) > 0 and (sys.argv.index(args[0]) + 1 <= len(sys.argv)):
            input_data = sys.argv[-1]

        elif select.select([sys.stdin,],[],[],0.0)[0]:
            input_data = sys.stdin

        else:
            input_data = sys.stdin

    if debug: print(("opt = " , opt))
    if debug: print(("sys.argv[-1] = " , sys.argv[-1]))
    if debug: print(("input_data = " , input_data))

    if test_mode != '' or debug == True:
        print(("list_of_csv_strings = ", list_of_csv_strings))
        print(("list_of_lists_of_strings = ", list_of_lists_of_strings))

    rc, results = columnize_output(input_data=input_data)
    if rc != 0:  print("ERROR: In columnize_output():")
    for row in results:
        print(row)



