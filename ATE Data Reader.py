###################################################
# ATE STDF Data Reader Python Edition             #
# Version: Beta 0.8                               #
#                                                 #
# March 20, 2018                                  #
# Thomas Kaunzinger                               #
# LTX-Credence / XCerra Corp.                     #
#                                                 #
# References:                                     #
# PySTDF Library                                  #
# numpy                                           #
# matplotlib                                      #
# countrymarmot (cp + cpk)                        #
# PyPDF2                                          #
# My crying soul because there's no documentation #
###################################################

########################################################################################################################
# The purpose of this program is to attempt to make sense of Teradyne's de-facto standard fie format: the              #
# Standard Test Data Format (STDF). This proprietary file format consists of non-trivially parsed and encoded          #
# binary data and is the most commonly used format of data produced by Automatic Test Equipment (ATE), used by         #
# companies like LTX-Credence and Teradyne. This program will be using the obscure but very helpful PySTDF library     #
# to parse and subsequently process the data into sensible, meaningful results.                                        #
#                                                                                                                      #
# This project can be found here: https://github.com/McNibbler/public-projects/tree/master/Python/ATE%20Data%20Reader  #
#   Note: repository contains more projects than just the ATE Reader. Please check them out if you're interested :)    #
#   I may move this project to its own repository at some point after I get a full, functional version of it.          #
#                                                                                                                      #
# The PySTDF library project can be found here: https://github.com/cmars/pystdf                                        #
########################################################################################################################

########################################################################################################################
# This is the part where I apologize for having some likely extremely jank code. For a while, this project used some   #
# horrible combination of numpy and python's normal arrays because I didn't really remember what I was doing, due to   #
# not using python much like this for a long time. That has since been cleaned up, but I know as a fact that there's   #
# still plenty of horrible things in my code and it's probably disgustingly organized, but just bear with me. Maybe if #
# I at all knew what I was supposed to do when I started this, it would have worked out better, but for now we're just #
# gonna roll with it. Have mercy on me :)                                                                              #
########################################################################################################################

########################################################################################################################
# NOTE: Do not run this program on data with the a file of the same name, but with "_parsed.txt" or "_excel.xlsx" or   #
# "_results.pdf" appended to the end; e.g. running this on "data.std" with a file called "data.std_parsed.txt" in the  #
# same folder is a bad idea, as it will be overwritten, due to the fact that this program creates and writes to a text #
# file of that naming convention. But for real, why would you even do that in the first place?                         #
########################################################################################################################

########################################################################################################################
# License: none yet lol. Do what you want with it for now, just credit me, let me know, and buy me food some time :)   #
# Product of LTX-Credence of Xcerra Corporation. Program designed by Thomas Kaunzinger. Please contact for any         #
# questions regarding use.                                                                                             #
########################################################################################################################

###################################################

#######################
# IMPORTING LIBRARIES #
#######################

# Importing a bunch of stuff that I probably won't even need but we'll just roll with it for now. I actually don't even
# know what libraries here I actually am using at the moment so that's fun.

# from __future__ import print_function

import os
import sys

from pystdf.IO import *
from pystdf.Writers import *
import pystdf.V4 as V4
from pystdf.Importer import STDF2DataFrame

import numpy as np
import matplotlib.pyplot as plt
from decimal import Decimal
import pandas as pd

from matplotlib.backends.backend_pdf import PdfPages
from PyPDF2 import PdfFileMerger, PdfFileReader

try:
    import gzip
    have_gzip = True
except ImportError:
    have_gzip = False

try:
    import bz2
    have_bz2 = True
except ImportError:
    have_bz2 = False

from tkinter import *
import tkinter.filedialog

gzPattern = re.compile('\.g?z', re.I)
bz2Pattern = re.compile('\.bz2', re.I)

###################################################

##############################
# PROGRAM EXECUTION BOOLEANS #
##############################

# Selects what form of execution you want for the program
# if gui_input is true, the program will use the GUI I am attempting to build (unfinished)
# if gui_input is false and cmd_input is true, the program will use the command-line interface (stable and functional)
# if both are false, then it defaults to the hard-coded configuration that I just made for testing quickly (bad idea)
cmd_input = True


###################################################

###############
# MAIN METHOD #
###############

# Defining the main method
def main():

    # Command-line interface for file selection
    if cmd_input:

        file_selected = False
        while not file_selected:
            filepath = input('Select file location: ')
            print()

            wd = os.path.dirname(os.path.abspath(__file__))
            filepath = os.path.join(wd, filepath)

            # Checks validity of file selection
            if not filepath.lower().endswith(('.std', '.stdf')):
                print("Please select a file ending in '.std' or '.stdf'")
                print()

            elif not os.path.isfile(filepath):
                print("Please select a filepath that exists")
                print()

            else:
                file_selected = True

        # Asks if you wish to create a new parsed file
        parse_selected = False
        parse_chosen_yet = False
        while not parse_chosen_yet:
            parse_input = input('Create parsed text file now? (do this if you have not before with this STDF) (y/n): ')
            print()
            if parse_input.lower() == 'y' or parse_input.lower() == 'yes':
                parse_selected = True
                parse_chosen_yet = True
            elif parse_input.lower() == 'n' or parse_input.lower() == 'no':
                parse_selected = False
                parse_chosen_yet = True
            else:
                print('Please select yes or no')
                print()

    # Fast hard-coded testing code if both are false
    else:
        # Chose where the STDF file is located. I'll add some pretty-ness to this at some point
        wd = os.path.dirname(os.path.abspath(__file__))

        filepath = os.path.join(wd, "Data\\data.std")

        print('Your filepath is located at: ' + filepath)

        parse_selected = False




    # Parses that big boi into a text file
    if parse_selected:

        # Checks that the file isn't already open and in use
        written = False
        while not written:
            try:
                process_file(filepath)
                print('STDF parsed successfully!')
                print()
                written = True

            except PermissionError:
                print(str('Please close ' + str(filepath + "_parsed.txt") + ' and try again.'))
                input('Press <Enter> to continue...')
                print()

    # This one is way too slow. Use with caution. Very good for visualizing how the parsed text file is organized.
    # toExcel(filepath)

    # Finds and opens the recently created parsed text file
    parsedDataFile = str(filepath + "_parsed.txt")

    # Checks if you actually have parsed data
    if not os.path.isfile(parsedDataFile):
        print("Please try again and select yes to parse data")
        print()
        input("Press <Enter> to close...")
        sys.exit()

    # Reads raw data from parsed text file
    data = open(parsedDataFile).read().splitlines()

    # Separates the different types of data from the text file into their own sets. Here, I am initializing the arrays.
    far_data, mir_data, sdr_data, pmr_data, pgr_data, pir_data, ptr_data, prr_data, tsr_data, hbr_data, sbr_data, pcr_data, mrr_data = [], [], [], [], [], [], [], [], [], [], [], [], []

    # Appends each set of data to their own personal arrays.
    # Python doesn't have proper switch statements because God knows why
    for i in range(0, len(data) - 1):
        if data[i].startswith("FAR"):
            far_data.append(data[i])
        elif data[i].startswith("MIR"):
            mir_data.append(data[i])
        elif data[i].startswith("SDR"):
            sdr_data.append(data[i])
        elif data[i].startswith("PMR"):
            pmr_data.append(data[i])
        elif data[i].startswith("PGR"):
            pgr_data.append(data[i])
        elif data[i].startswith("PIR"):
            pir_data.append(data[i])
        elif data[i].startswith("PTR"):
            ptr_data.append(data[i])
        elif data[i].startswith("PRR"):
            prr_data.append(data[i])
        elif data[i].startswith("TSR"):
            tsr_data.append(data[i])
        elif data[i].startswith("HBR"):
            hbr_data.append(data[i])
        elif data[i].startswith("SBR"):
            sbr_data.append(data[i])
        elif data[i].startswith("PCR"):
            pcr_data.append(data[i])
        elif data[i].startswith("MRR"):
            mrr_data.append(data[i])

    # finds the number of lines per test, one line for each site being tested
    sdr_parse = sdr_data[0].split("|")
    number_of_sites = int(sdr_parse[3])
    print('Number of testing sites per test: ' + str(number_of_sites))
    print()

    # Gathers a list of the test numbers and the tests ran for each site, avoiding repeats from rerun tests
    list_of_test_numbers = []
    for i in range(0, len(ptr_data), number_of_sites):
        if [ptr_data[i].split("|")[1], ptr_data[i].split("|")[7]] in list_of_test_numbers:
            pass
        else:
            list_of_test_numbers.append([ptr_data[i].split("|")[1], ptr_data[i].split("|")[7]])

    selected_test_all = []

    # Juicy user input weow!!!
    if cmd_input:

        selected = False
        selecting = False

        # Select if you want to do every test or just one individually
        while not selected:
            choosing = input('Select test? (otherwise run on all tests) (y/n): ')
            print()
            if choosing.lower() == 'y' or choosing.lower() == 'yes':
                selecting = True
                selected = True
            elif choosing.lower() == 'n' or choosing.lower() == 'no':
                selecting = False
                selected = True
            else:
                print('Please select yes or no')
                print()

        # Select what you would want instead
        if selecting:
            picked = False

            # Creates a list of just the test numbers to check for valid inputs
            list_of_just_numbers = []
            for i in range(0, len(list_of_test_numbers)):
                if list_of_test_numbers[i][0] in list_of_just_numbers:
                    pass
                else:
                    list_of_just_numbers.append(list_of_test_numbers[i][0])

            # Selecting a test to run the script on
            while not picked:
                test_selection = input('Input a test number you wish to observe (type "show" to show options): ')
                print()

                # Displays valid tests
                if test_selection.lower() == 'show':

                    for i in range(0, len(list_of_test_numbers)):
                        print(list_of_test_numbers[i])

                    print()
                    print("Format: ['Test Number', 'Test Description']")
                    print("Note: some test numbers contain multiple relevant tests. Each will have their own page.")
                    print()

                # Checks validity
                elif test_selection not in list_of_just_numbers:
                    print("Please choose a valid test number.")
                    print()

                # Chooses the test
                else:
                    selected_test_all = find_tests_of_number(test_selection, list_of_test_numbers)
                    picked = True

        # All tests (if not selecting any individual test)
        else:
            selected_test_all = list_of_test_numbers


        # Selecting the desired results generated from the test

        # Choose to create results spreadsheet
        chosen = False
        summary = False
        while not chosen:
            spreadsheet_selection = input('Generate spreadsheet summary of all tests? (y/n): ')
            print()

            if spreadsheet_selection.lower() == 'y' or spreadsheet_selection.lower() == 'yes':
                summary = True
                chosen = True
            elif spreadsheet_selection.lower() == 'n' or spreadsheet_selection.lower() == 'no':
                summary = False
                chosen = True
            else:
                print('Please select yes or no')
                print()

        # Choose to render the pdf
        pdf_render = False
        # Extracts the PTR data for the selected test number
        all_ptr_test = []
        for i in range(0, len(selected_test_all)):
            all_ptr_test.append(ptr_extractor(number_of_sites, ptr_data, selected_test_all[i]))

        # Gathers each set of data from all runs for each site in all selected tests
        all_test = []
        for i in range(len(all_ptr_test)):
            all_test.append(single_test_data(number_of_sites, all_ptr_test[i]))
        chosen = False
        while not chosen:
            pdf_selection = input('Render detailed PDF results of all tests (slow if lots of data selected)? (y/n): ')
            print()

            if pdf_selection.lower() == 'y' or pdf_selection.lower() == 'yes':
                pdf_render = True
                chosen = True
            elif pdf_selection.lower() == 'n' or pdf_selection.lower() == 'no':
                pdf_render = False
                chosen = True
            else:
                print('Please select yes or no')
                print()


    # Automatic stuff if there's no user inputs
    else:
        # Selects a test number + name combination for a given index
        test_index = 100  # Totally arbitrary
        selected_test = [ptr_data[number_of_sites * test_index].split("|")[1],
                         ptr_data[number_of_sites * test_index].split("|")[7]]
        print('Selected test: ' + str(selected_test))
        print()

        # Creates a list of tuples that contains the test number and name for all of the tests that have the same
        # number as selected_test
        selected_test_all = find_tests_of_number(selected_test[0], list_of_test_numbers)

        pdf_render = True
        summary = True





    # ~~~~~ Execution of data processing functions ~~~~~ #

    # creates a spreadsheet of the final data results
    if summary:

        table = get_summary_table(all_test, ptr_data, number_of_sites, selected_test_all)

        # In case someone has the file open
        written = False
        while not written:
            try:
                table.to_csv(path_or_buf=str(filepath + "_summary.csv"))
                print('CSV summary written successfully!')
                print()
                written = True

            except PermissionError:
                print(str('Please close ' + str(filepath + "_summary.csv") + ' and try again.'))
                input('Press <Enter> to continue...')
                print()

    # plots all of the tests under the selected test number
    if pdf_render:
        plot_list_of_tests(all_test, ptr_data, number_of_sites, selected_test_all, filepath)

    # ~~~~~ END OF MAIN FUNCTION ~~~~~ #


###################################################

#####################
# BACKEND FUNCTIONS #
#####################


# IMPORTANT DOCUMENTATION I NEED TO FILL OUT TO MAKE SURE PEOPLE KNOW WHAT THE HELL IS GOING ON

# ~~~~~~~~~~ Data definition explanations (in functions) ~~~~~~~~~~ #
# data --> ptr_data                                                 #
#   gathered in main()                                              #
#                                                                   #
# test_tuple --> ['test_number', 'test_name']                       #
#   Structure for associating a test's name with its test number    #
#                                                                   #
# test_list --> List of test_tuple                                  #
#   find_test_of_number() returns this                              #
#   list_of_test_numbers in main() is the complete list of this     #
#                                                                   #
# num_of_sites --> number of testing sites for each test run        #
#   number_of_sites = int(sdr_parse[3]) in main()                   #
#                                                                   #
# test_list_data --> list of sets of site_data                      #
#   (sorted in the same order as corresponding tests in test_list)  #
#                                                                   #
# site_data --> array of float data points number_of_sites long     #
#   raw data for a single corresponding test_tuple                  #
#                                                                   #
# test_list and test_list_data are the same length                  #
#                                                                   #
# minimum, maximum --> floats                                       #
#   lower and upper extremes for a site_data from a corresponding   #
#       test_tuple. These are found in the ptr_data (data), which   #
#       has the values located in one of the columns for the first  #
#       test site in the first data point in a test.                #
#   returned by get_plot_extremes() abstraction                     #
# units --> string                                                  #
#   Gathered virtually identically to minimum and maximum.          #
#       Represents units for plotting and post calculations on      #
#       data sets.                                                  #
#                                                                   #
# ~~~~~~~~~~~~ Parsed text file structure explanation ~~~~~~~~~~~~~ #
# The PySTDF library parses the data really non-intuitively,        #
#   although it can be viewed somewhat more clearly if you use the  #
#   toExcel() function (I recommend doing this for figuring out the #
#   way the file is formatted). Basically, each '|' separates the   #
#   information in columns, and the first column determines the     #
#   "page" you are dealing with. The only ones I found particularly #
#   useful were SDR (for the number of sites) and PTR (where all    #
#   the data is actually contained).                                #
# The way the PTR data is parsed is very non-intuitive still, with  #
#   the data broken into chunks num_of_sites lines long, meaning    #
#   each chunk of num_of_sites lines contain a corresponding        #
#   test_tuple that can be extracted, as well as a data point       #
#   result for each test site. This is then done for every single   #
#   test_tuple combination. After all that is done, the process is  #
#   repeated for every single run of the test, creating a new data  #
#   point for each site in each test tuple for however many numbers #
#   of tests there are.                                             #
# It's very not obvious at first, so I strongly recommend creating  #
#   an excel file first to look at it yourself and reverse-engineer #
#   it like I did if you really want to try and figure out the file #
#   format yourself. I'm sorry the library sucks but I didn't       #
#   design it :/ . Good luck!                                       #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #


# Given a set of data for each test, the full set of ptr data, the number of sites, and the list of names/tests for the
#   set of data needed, expect each item in this set of data to be plotted in a new figure
# test_list_data should be an array of arrays of arrays with the same length as test_list, which is an array of tuples
#   with each tuple representing the test number and name of the test data in that specific trial
def plot_list_of_tests(test_list_data, data, num_of_sites, test_list, directory):
    # Runs through each of the tests in the list and plots it in a new figure
    pp = PdfFileMerger()

    for i in range(0, len(test_list)):

        pdfTemp = PdfPages(str(directory + "_results_temp"))

        plt.figure(figsize=(11, 8.5))
        pdfTemp.savefig(plot_everything_from_one_test(test_list_data[i], data, num_of_sites, test_list[i]))

        pdfTemp.close()

        pp.append(PdfFileReader(str(directory + "_results_temp"), "rb"))

        if i % 10 == 0:
            print(str(i) + "/" + str(len(test_list)) + " test results completed")

        plt.close()

    print(str(len(test_list)) + "/" + str(len(test_list)) + " test results completed")
    print()

    os.remove(str(directory + "_results_temp"))

    # Makes sure that the pdf isn't open and prompts you to close it if it is
    written = False
    while not written:
        try:
            pp.write(str(directory + "_results.pdf"))
            print('PDF written successfully!')
            written = True

        except PermissionError:
            print(str('Please close ' + str(directory + "_results.pdf") + ' and try again.'))
            input('Press <Enter> to continue...')
            print()


# Plots the results of everything from one test
def plot_everything_from_one_test(test_data, data, num_of_sites, test_tuple):

    # Find the limits
    low_lim = get_plot_min(data, test_tuple, num_of_sites)
    hi_lim = get_plot_max(data, test_tuple, num_of_sites)
    units = get_units(data, test_tuple, num_of_sites)

    # Title for everything
    plt.suptitle(str("Test: " + test_tuple[0] + " - " + test_tuple[1] + " - Units: " + units))

    # Plots the table of results, showing a max of 16 sites at once, plus all the collective data
    table = table_of_results(test_data, low_lim, hi_lim, units)
    table = table[0:17]
    plt.subplot(211)
    cell_text = []
    for row in range(len(table)):
        cell_text.append(table.iloc[row])

    plt.table(cellText=cell_text, colLabels=table.columns, loc='center')
    plt.axis('off')


    # Plots the trendline
    plt.subplot(223)
    plot_full_test_trend(test_data, low_lim, hi_lim)
    plt.xlabel("Trials")
    plt.ylabel(units)
    plt.title("Trendline")
    plt.grid(color='0.9', linestyle='--', linewidth=1)

    # Plots the histogram
    plt.subplot(224)
    plot_full_test_hist(test_data, low_lim, hi_lim)
    plt.xlabel(units)
    plt.ylabel("Trials")
    plt.title("Histogram")
    plt.grid(color='0.9', linestyle='--', linewidth=1, axis='y')


# TestNumber (string) + ListOfTests (list of tuples) -> ListOfTests with TestNumber as the 0th index (list of tuples)
# Takes a string representing a test number and returns any test names associated with that test number
#   e.g. one test number may be 1234 and might have 40 tests run on it, but it may be 20 tests under
#   the name "device_test_20kHz" and then another 20 tests under the name "device_test_100kHz", meaning
#   there were two unique tests run under the same test number.
def find_tests_of_number(test_number, test_list):
    tests_of_number = []
    for i in range(0, len(test_list)):
        if test_list[i][0] == test_number:
            tests_of_number.append(test_list[i])

    return tests_of_number


# Returns the lower allowed limit of a set of data
def get_plot_min(data, test_tuple, num_of_sites):
    return get_plot_extremes(data, test_tuple, num_of_sites)[0]

# Returns the upper allowed limit of a set of data
def get_plot_max(data, test_tuple, num_of_sites):
    return get_plot_extremes(data, test_tuple, num_of_sites)[1]

# Returns the units for a set of data
def get_units(data, test_tuple, num_of_sites):
    return get_plot_extremes(data, test_tuple, num_of_sites)[2]

# Abstraction of above 3 functions, returns tuple with min and max
def get_plot_extremes(data, test_tuple, num_of_sites):
    minimum_test = 0
    maximum_test = 1
    units = ''
    temp = 0
    not_found = True
    while not_found:
        if data[temp].split("|")[1] == test_tuple[0]:
            minimum_test = float(data[temp].split("|")[13])
            maximum_test = float(data[temp].split("|")[14])
            units = (data[temp].split("|")[15])
            not_found = False
        temp += num_of_sites
    return [minimum_test, maximum_test, units]


# Plots the results of all sites from one test
def plot_full_test_trend(test_data, minimum, maximum):

    # Plots each site one at a time
    for i in range(0, len(test_data)):
        plot_single_site_trend(test_data[i])

    # Plots the minimum and maximum barriers
    plt.plot(range(0, len(test_data[0])), [minimum] * len(test_data[0]), color="red", linewidth=3.0)
    plt.plot(range(0, len(test_data[0])), [maximum] * len(test_data[0]), color="red", linewidth=3.0)

    # My feeble attempt to get pretty dynamic limits
    expand = max([abs(minimum), abs(maximum)])
    if minimum == maximum:
        plt.ylim(ymin=-0.05)
        plt.ylim(ymax=1.05)
    else:
        plt.ylim(ymin= minimum - abs(0.05 * expand))
        plt.ylim(ymax= maximum + abs(0.05 * expand))


# Supposedly gets the summary results for all sites in each test
def get_summary_table(test_list_data, data, num_of_sites, test_list):
    parameters = ['Units', 'Runs', 'Fails', 'Min', 'Mean', 'Max', 'Range', 'STD', 'Cp', 'Cpl', 'Cpu', 'Cpk']

    summary_results = []

    for i in range(0, len(test_list_data)):

        all_data_array = np.concatenate(test_list_data[i], axis=0)

        units = get_units(data, test_list[i], num_of_sites)
        minimum = get_plot_min(data, test_list[i], num_of_sites)
        maximum = get_plot_max(data, test_list[i], num_of_sites)

        summary_results.append(site_array(all_data_array, minimum, maximum, units, units))

    test_names = []
    for i in range(0, len(test_list)):
        test_names.append(test_list[i][1])

    table = pd.DataFrame(summary_results, columns=parameters, index=test_names)

    return table


# Returns the table of the results of all the tests to visualize the data
def table_of_results(test_data, minimum, maximum, units):
    parameters = ['Site', 'Runs', 'Fails', 'Min', 'Mean', 'Max', 'Range', 'STD', 'Cp', 'Cpl', 'Cpu', 'Cpk']

    # Clarification
    if units.lower() == 'db':
        parameters[7] = 'STD (%)'

    all_data = np.concatenate(test_data, axis=0)

    test_results = [site_array(all_data, minimum, maximum, 'ALL', units)]

    for i in range(0, len(test_data)):
        test_results.append(site_array(test_data[i], minimum, maximum, i + 1, units))

    table = pd.DataFrame(test_results, columns=parameters)

    return table


# Returns an array a site's final test results
def site_array(site_data, minimum, maximum, site_number, units):

    # Big boi initialization
    site_results = []

    # Not actually volts, it's actually % if it's db technically but who cares
    volt_data = []

    # The struggles of logarithmic data
    if units.lower() == 'db':

        for i in range(0, len(site_data)):
            volt_data.append(db2v(site_data[i]))

        mean_result = v2db(np.mean(volt_data))
        standard_deviation = np.std(volt_data)*100  # *100 for converting to %
        std_string = str('%.3E' % (Decimal(standard_deviation)))

        cp_result = str(Decimal(cp(volt_data, db2v(minimum), db2v(maximum))).quantize(Decimal('0.001')))
        cpl_result = str(Decimal(cpl(volt_data, db2v(minimum))).quantize(Decimal('0.001')))
        cpu_result = str(Decimal(cpu(volt_data, db2v(maximum))).quantize(Decimal('0.001')))
        cpk_result = str(Decimal(cpk(volt_data, db2v(minimum), db2v(maximum))).quantize(Decimal('0.001')))

    # Pass/fail data is stupid
    elif minimum == maximum:
        mean_result = np.mean(site_data)
        std_string = str(np.std(site_data))
        cp_result = 'N/A'
        cpl_result = 'N/A'
        cpu_result = 'N/A'
        cpk_result = 'N/A'

    # Yummy linear data instead
    else:
        mean_result = np.mean(site_data)
        std_string = str(Decimal(np.std(site_data)).quantize(Decimal('0.001')))
        cp_result = str(Decimal(cp(site_data, minimum, maximum)).quantize(Decimal('0.001')))
        cpl_result = str(Decimal(cpu(site_data, minimum)).quantize(Decimal('0.001')))
        cpu_result = str(Decimal(cpl(site_data, maximum)).quantize(Decimal('0.001')))
        cpk_result = str(Decimal(cpk(site_data, minimum, maximum)).quantize(Decimal('0.001')))

    # Appending all the important results weow!
    site_results.append(str(site_number))
    site_results.append(str(len(site_data)))
    site_results.append(str(calculate_fails(site_data, minimum, maximum)))
    site_results.append(str(Decimal(min(site_data)).quantize(Decimal('0.001'))))
    site_results.append(str(Decimal(mean_result).quantize(Decimal('0.001'))))
    site_results.append(str(Decimal(max(site_data)).quantize(Decimal('0.001'))))
    site_results.append(str(Decimal(max(site_data) - min(site_data)).quantize(Decimal('0.001'))))
    site_results.append(std_string)
    site_results.append(cp_result)
    site_results.append(cpl_result)
    site_results.append(cpu_result)
    site_results.append(cpk_result)

    return site_results


# Converts to decibels
def v2db(v):
    return 20*np.log10(abs(v))

# Converts from decibels
def db2v(db):
    return 10 ** (db / 20)


# Counts the number of fails in a data set
def calculate_fails(site_data, minimum, maximum):
    fails_count = 0

    # Increase a fails counter for every data point that exceeds an extreme
    for i in range(0, len(site_data)):
        if site_data[i] > maximum or site_data[i] < minimum:
            fails_count += 1

    return fails_count


# Plots the historgram results of all sites from one test
def plot_full_test_hist(test_data, minimum, maximum):

    # Plots each site one at a time
    for i in range(0, len(test_data)):
        plot_single_site_hist(test_data[i], minimum, maximum)

    # My feeble attempt to get pretty dynamic limits
    if minimum == maximum:
        plt.xlim(xmin=0)
        plt.xlim(xmax=1)
    else:
        plt.xlim(xmin=minimum)
        plt.xlim(xmax=maximum)

    plt.ylim(ymin=0)
    plt.ylim(ymax=len(test_data[0]))


# Plots a single site's results
def plot_single_site_trend(site_data):
    plt.plot(range(0, len(site_data)), site_data)


# Plots a single site's results as a histogram
def plot_single_site_hist(site_data, minimum, maximum):
    # At the moment the bins are the same as they are in the previous program's results. Will add fail bin later.

    # Damn pass/fail data exceptions everywhere
    if minimum == maximum:
        binboi = np.linspace(0, 1, 21)

    else:
        binboi = np.linspace(minimum, maximum, 21)

    plt.hist(np.clip(site_data, binboi[0], binboi[-1]), bins=binboi, edgecolor='white', linewidth=0.5)


# Creates an array of arrays that has the raw data for each test site in one particular test
# Given the integer number of sites under test and the Array result from ptr_extractor for a certain test num + name,
#   expect a 2D array with each row being the reran test results for each of the sites in a particular test
def single_test_data(num_of_sites, extracted_ptr):

    # Me being bad at initializing arrays again, hush
    single_test = []

    # Runs through once for each of the sites in the test, incrementing by 1
    for i in range(0, num_of_sites):

        single_site = []

        # Runs through once for each of the loops of the test, incrementing by the number of test sites until all test
        # loops are covered for the individual testing site. The incremented i offsets it so that it moves on to the
        # next testing site
        for j in range(i, len(extracted_ptr), num_of_sites):

            single_site.append(float(extracted_ptr[j][6]))

        single_test.append(single_site)

    return single_test


# Integer (Number_of_sites), Parsed List of Strings (ptr_data specifically), tuple ([test_number, test_name])
#   Returns -> array with just the relevant test data parsed along '|'
# It grabs the data for a certain test in the PTR data and turns that specific test into an array of arrays
def ptr_extractor(num_of_sites, data, test_number):

    # Initializes an array of the data from one of the tests for all test sites
    ptr_array_test = []

    # Finds where in the data to start looking for the test in question
    starting_index = 0
    for i in range(0, len(data), num_of_sites):
        if (data[i].split("|")[1] == test_number[0]) and (data[i].split("|")[7] == test_number[1]):
            starting_index = i
            for j in range(starting_index, (starting_index + num_of_sites)):
                ptr_array_test.append(data[j].split("|"))

    # Returns the array weow!
    return ptr_array_test


# For the four following functions, site_data is a list of raw floating point data, minimum is the lower limit and
# maximum is the upper limit

# CP AND CPK FUNCTIONS
# Credit to: countrymarmot on github gist:  https://gist.github.com/countrymarmot/8413981
def cp(site_data, minimum, maximum):
    sigma = np.std(site_data)
    cp_value = float(maximum - minimum) / (6*sigma)
    return cp_value

def cpk(site_data, minimum, maximum):
    sigma = np.std(site_data)
    m = np.mean(site_data)
    cpu_value = float(maximum - m) / (3*sigma)
    cpl_value = float(m - minimum) / (3*sigma)
    cpk_value = np.min([cpu_value, cpl_value])
    return cpk_value


# One sided calculations (cpl/cpu)
def cpl(site_data, minimum):
    sigma = np.std(site_data)
    m = np.mean(site_data)
    cpl_value = float(m - minimum) / (3*sigma)
    return cpl_value

def cpu(site_data, maximum):
    sigma = np.std(site_data)
    m = np.mean(site_data)
    cpu_value = float(maximum - m) / (3 * sigma)
    return cpu_value


###################################################

############################
# FILE READING AND PARSING #
############################

# lmfao i just took this from the stdf2text script and im trying to change it so it works but there's no documentation
# im crying inside and out send help. I'll attempt to document it myself, but I'm so sorry for all the garbo.

# Currently, this function takes the stdf file and parses it to a text file with the name of the file, followed by a
# "_parsed.txt", which can be open and analyzed later. Parsing is delimited with pipes, "|"
def process_file(filename):

    # Lets you know what's goin' on
    print('Parsing data...')
    print()

    # Not sure what this actually does but it was in the script so lets roll with it
    reopen_fn = None

    # Checks if gzip is installed and opens file with it if possible
    if gzPattern.search(filename):
        if not have_gzip:
            print("gzip is not supported on this system", file=sys.stderr)
            sys.exit(1)
        reopen_fn = lambda: gzip.open(filename, 'rb')
        f = reopen_fn()

    # Checks if bz2 is installed in the event that gzip isn't installed
    elif bz2Pattern.search(filename):
        if not have_bz2:
            print("bz2 is not supported on this system", file=sys.stderr)
            sys.exit(1)
        reopen_fn = lambda: bz2.BZ2File(filename, 'rb')
        f = reopen_fn()

    # Opens it the boring way otherwise (i don't actually know what makes this different, probably speed idk)
    else:
        f = open(filename, 'rb')

    # The name of the new file, preserving the directory of the previous
    newFile = filename + "_parsed.txt"

    # I guess I'm making a parsing object here, but again I didn't write this part
    p = Parser(inp=f, reopen_fn=reopen_fn)

    # Writing to a text file instead of vomiting it to the console
    with open(newFile, 'w') as fout:
        p.addSink(TextWriter(stream=fout))      # fout writes it to the opened text file
        p.parse()

    # We don't need to keep that file open
    f.close()


# Similar to the previous function, takes an STDF file and creates an xlsx document with "_excel.xlsx" added to the file
# name. This function is hella slow, so I recommend not using it if you don't need to, but we'll see if I actually end
# up using it in this script or not.
def toExcel(filename):
    # Converts the stdf to a data frame... somehow (i do not ever intend on looking how he managed to parse this gross
    # file format)
    tables = STDF2DataFrame(filename)

    # The name of the new file, preserving the directory of the previous
    fname = filename + "_excel.xlsx"

    # Writing object to work with excel documents
    writer = pd.ExcelWriter(fname, engine='xlsxwriter')

    # Not mine and I don't really know what's going on here, but it works, so I won't question him. It actually writes
    # the data frame as an excel document
    for k, v in tables.items():
        # Make sure the order of columns complies the specs
        record = [r for r in V4.records if r.__class__.__name__.upper() == k]
        if len(record) == 0:
            print("Ignore exporting table %s: No such record type exists." % k)
        else:
            columns = [field[0] for field in record[0].fieldMap]
            v.to_excel(writer, sheet_name=k, columns=columns, index=False, na_rep="N/A")

    writer.save()


###################################################

#############
# EXECUTION #
#############

# Execute main method. Weow!!!
# If you made it this far, sorry for my passive-aggressive commenting and thanks for sticking through it all.
if __name__ == "__main__":
    main()
    print()
    input("Press <Enter> to close...")
