###################################################
# ATE STDF Data Reader Python Edition             #
# Flask Web App Version                           #
# Web Version: Alpha 0.1                          #
#                                                 #
# March 14, 2018                                  #
# Thomas Kaunzinger                               #
# LTX-Credence / XCerra Corp.                     #
#                                                 #
# References:                                     #
# PySTDF Library                                  #
# Flask                                           #
# numpy                                           #
# matplotlib                                      #
# countrymarmot (cp + cpk)                        #
# PyPDF2                                          #
# My crying soul because there's no documentation #
###################################################

########################################################################################################################
# The purpose of 'ATE_Flask.py' is to take what I've made so far in 'ATE Data Reader.py' and create a user-friendly    #
# web-browser-based interface built on Flask for a user to more easily interact with, upload, and select what tests    #
# they may wish to run in processing. Ultimately, this is the end result imagined from the conception of this project; #
# a simple free program anybody can use to process these cursed files. Please excuse any archaic artifacts from the    #
# local program. Those will be removed in due time.                                                                    #
########################################################################################################################


# ~~~~~ PREVIOUS COMMENTS BELOW. SOME ARE STILL RELEVANT I'LL LOOK THROUGH THEM LATER ~~~~~ #

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

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

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

import tkinter
import tkinter.filedialog

gzPattern = re.compile('\.g?z', re.I)
bz2Pattern = re.compile('\.bz2', re.I)

###################################################

app = Flask(__name__)
@app.route('/<nice>')
def index(nice):
    return render_template('index.html', nice=nice)




###################################################

#############
# EXECUTION #
#############

# Starts the application. Weow!!!
# If you made it this far, sorry for my passive-aggressive commenting and thanks for sticking through it all.
if __name__ == "__main__":
    app.run(debug=True)
