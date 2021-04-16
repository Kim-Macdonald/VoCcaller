# -*- coding: utf-8 -*-
"""
Created on Mon Apr 12 10:57:50 2021

@author: KimMacdonald
"""

#created & tested on PC using:
# pandas v1.1.3
# python v3.8.5
#and on laptop with:
# pandas v1.0.5
# python v3.8.3
#Server has pandas v1.2.3 and python v3.8.8
    
#import packages I need
import os
import subprocess
import fnmatch
import pandas as pd
import numpy as np


# Store current date in a variable: (can use for file naming if desired. Not used here)
from datetime import datetime
Today = datetime.today().strftime('%Y-%m-%d')   # output is like '2021-01-26'  


#save the current working directory (cwd) to a variable to use in everything below. 
#For us, this would be the MiSeqRunID directory for each run - it changes each time we analyze a run, 
#so i want to pull this from where ever I am, 
#so I don't have to enter it each time:
cwdPath = os.getcwd()


#Define variable using last part of directory/path
#This will be used to name your files uniquely:
MiSeqRunID = os.path.basename(os.path.normpath(cwdPath))
#print(MiSeqRunID)  #works


# Read in QC summary table ( [MiSeqRunID]_MissingPlus_QC_lineage_VoC_OrderedFinal.csv ) csv file:
for dir_path, dir_names, file_names in os.walk(cwdPath):
    for f in file_names:
        if fnmatch.fnmatch(f, '*_MissingPlus_QC_lineage_VoC_OrderedFinal.csv'):
            #print(f)  # worked
            file5 = os.path.join(cwdPath, f)
            df_QCsummary = pd.read_csv(file5)


# Make variable to store values for positives (lineages of concern): (YOU CAN ADD TO THIS LIST, or remove from it)
Positive_values = ['B.1.1.7', 'B.1.351', 'P.1', 'B.1.427', 'B.1.429', 'B.1.617']
VoI_Values = ['B.1.525', 'B.1.526', 'B.1.1.318', 'P.2', 'P.3', 'A.23.1', 'A.27']
# df_VoCpos0 = df_QCsummary.loc[df_QCsummary['lineage_x'].isin(Positive_values)]
# print(df_VoCpos0) 



#-----------ADD VARIANT COLUMNS to QC Summary Table------------------
# Create 2 columns for VariantYesNo and VariantType:
df_QCsummary.insert(31, "VariantYesNo", "")
df_QCsummary.insert(32, "VariantType", "")
#print(df_QCsummary) # correct

df_VariantReqMatch0 = df_QCsummary
#df_VariantReqMatch0 = df_QCsummary.iloc[:, 1:33]
#print(df_VariantReqMatch0) #correct



# Fill VariantYesNo Column with Yes/No/Failed/Possible values based on criteria:
conditions = [
    (df_VariantReqMatch0['qc_pass_x'].astype(str).str.contains('EXCESS_AMBIGUITY')),
    (df_VariantReqMatch0['lineage_x'].isin(Positive_values)),
    (df_VariantReqMatch0['lineage_x'].isin(VoI_Values)),
    (df_VariantReqMatch0['lineage_x'].eq('none')) & (df_VariantReqMatch0['num_observed_mutations'] > 4),
    #Include Warning flag for samples with a non-VoC lineage AND num_observed_mutations > 4 (may be mixed sample):
    (~df_VariantReqMatch0['lineage_x'].eq('none')) & (pd.notnull(df_VariantReqMatch0['lineage_x'])) & (~df_VariantReqMatch0['lineage_x'].isin(Positive_values)) & (df_VariantReqMatch0['num_observed_mutations'] > 4),  
    #(df_VariantReqMatch0['lineage_x'].eq('none')) & (df_ncovtoolsSummary_plusMissing['pct_covered_bases'] < 85.00),
    #updated to capture anything with blank values (removed from pipeline b/c not enough data) as Failed as well (otherwise are erroneously assigned as Not a Voc)
    (df_VariantReqMatch0['lineage_x'].eq('none')) & (df_VariantReqMatch0['pct_covered_bases'] < 85.00),
    (pd.isnull(df_VariantReqMatch0['lineage_x'])) & (pd.isnull(df_VariantReqMatch0['pct_covered_bases'])),
    (df_VariantReqMatch0['lineage_x'] != 'none')
]

choices = ['Failed (Excess Ambiguity)','Yes','Yes (VoI)','Possible','Warning','Failed','Failed','No']

df_VariantReqMatch0['VariantYesNo'] = np.select(conditions, choices, default='No')
#print(df_VariantReqMatch0)  #correct


# YOU CAN ADD VoC LINEAGES TO THIS LIST (Conditions2 and Choices2), or remove from it, AS WELL:
conditions2 = [
    (df_VariantReqMatch0['VariantYesNo'].eq('Failed (Excess Ambiguity)')),
    (df_VariantReqMatch0['lineage_x'] == "B.1.1.7"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.351"),
    (df_VariantReqMatch0['lineage_x'] == "P.1"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.525"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.427"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.429"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.617"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.526"),
    (df_VariantReqMatch0['lineage_x'] == "P.2"),
    (df_VariantReqMatch0['lineage_x'] == "P.3"),
    (df_VariantReqMatch0['lineage_x'] == "B.1.1.318"),
    (df_VariantReqMatch0['lineage_x'] == "A.23.1"),
    (df_VariantReqMatch0['lineage_x'] == "A.27"),
    (df_VariantReqMatch0['VariantYesNo'].eq('Failed')),
    (df_VariantReqMatch0['VariantYesNo'].eq('Possible')),
    (df_VariantReqMatch0['VariantYesNo'].eq('Warning')),
    (df_VariantReqMatch0['VariantYesNo'].eq('No'))
]

choices2 = ['Failed WGS QC','UK (B.1.1.7)','SA (B.1.351)','Brazil (P.1)','Nigerian (B.1.525)','California (B.1.427)','California (B.1.429)','India (B.1.617)','New York (B.1.526)','P.2','P.3','B.1.1.318','A.23.1','A.27','Failed WGS QC',('Possible ' + df_VariantReqMatch0['watchlist_id']),('Possible Contamination with ' + df_VariantReqMatch0['lineage_x'] + ' and ' + df_VariantReqMatch0['watchlist_id']),'Not a VoC']

df_VariantReqMatch0['VariantType'] = np.select(conditions2, choices2, default='Not a VoC')
#print(df_VariantReqMatch0)  #correct




#sort df:
df_VariantReqMatch1 = df_VariantReqMatch0.sort_values(by=['VariantYesNo', 'sample'])  
#print(df_VariantReqMatch1)




#--------LIB NUM & RUN NUM COLUMN:-------- (You Can Comment Out from this part, down to (but not including) the SAVE FILE section if you don't need LibraryNum & RunNum columns, or sampleID changed)

#----LibraryNum & RunNum:
    
# Create 1 column for LibraryNum (library plate #) at end:
df_VariantReqMatch1.insert(33, "LibraryNum", "")

# split sample column text by "-" 
LibNum_split = df_VariantReqMatch1['sample'].str.split("-")
#print(LibNum_split)
# store the 2nd value between -'s as a variable (this is for samples that start with E or R (named like R1234567890-201-D-E03)):
LibNum0 = df_VariantReqMatch1['sample'].str.split("-").str[1]
#print(LibNum0)
# store the 3rd value btwn -'s as a variable (this is for pos/neg cntrls (named like: NEG20210331-nCoVWGS-201-D)):
LibNum1 = df_VariantReqMatch1['sample'].str.split("-").str[2]
#print(LibNum1)
# store the 1st value (before 1st -) - the sampleID, as a variable:
SampleID = df_VariantReqMatch1['sample'].str.split("-").str[0]
#print(SampleID)
#store the LibNum0 length in a variable:
SampleLength = LibNum0.str.len()
#print(SampleLength)
#print(SampleLength.loc[1])



# Fill LibraryNum Column with Lib# values, based on criteria:
# IF SampleLength (the 2nd value btwn -'s) is <5 characters long (the Library number), then use LibNum0 to fill in it's LibraryNum:
# IF sampleID is >5 characters long (not the Lib#), then use LibNum1 to fill in it's LibraryNum, b/c it's a pos/neg cntrl:

conditions = [
    (SampleLength < 5),    
    (SampleLength > 5)
]

choices = [LibNum0, LibNum1]

df_VariantReqMatch1['LibraryNum'] = np.select(conditions, choices, default='')
#print(df_VariantReqMatch1['LibraryNum'])  #correct

#------------------------

#------------RunNum------------

# Create 1 column for RunNum (Sequencer Run#) (combines all library#s per sequencer run)
df_VariantReqMatch1.insert(34, "RunNum", "")


df_RunNum0 = df_VariantReqMatch1.sort_values(by=['LibraryNum', 'sample'])
#print(df_RunNum0)
             

df_RunNum7 = df_RunNum0['LibraryNum'].iloc[0]
df_RunNum8 = df_RunNum0['LibraryNum'].iloc[-1]
#print(df_RunNum7) #works
#print(df_RunNum8)

df_RunNum5 = df_RunNum7 + '-' + df_RunNum8
#print(df_RunNum5)

df_VariantReqMatch1[['RunNum']] = df_RunNum5
#print(df_VariantReqMatch1['RunNum'])  #correct
#print(df_VariantReqMatch1)
#print(df_VariantReqMatch1['VariantType'])  #correct


#---------------------------------------------------



#--------Replace SAMPLE column string with CID/sampleID only or full pos/neg cntrl name-----------
#REPLACE SAMPLE string in sample column with SampleID variable (just the CID):
#Controls are left as-is (e.g. NEG20210403-nCoVWGS-221-A) b/c the 2nd item after the dash split (nCoVWGS) is >5 characters long.
#Samples are changed (e.g. A1234567890-221-A-D05 to A1234567890) b/c the 2nd item after the dash split (the library plate #) is <5 characters long

conditions = [
    (SampleLength < 5),    
    (SampleLength > 5)
]

choices = [SampleID, df_VariantReqMatch1['sample']]

df_VariantReqMatch1['sample'] = np.select(conditions, choices, default='')
#print(df_VariantReqMatch1['sample'])  #correct

#--------------------------------------------



#-------------------------------------
#QC checks on new/altered columns (only used for testing):
#print(df_VariantReqMatch1['sample']) #works
#print(df_VariantReqMatch1['LibraryNum']) #works 
#print(df_VariantReqMatch1['RunNum']) #works

#print(df_VariantReqMatch1)
  
# Remove extra index column from table: 
df_QCsummary3 = df_VariantReqMatch1.iloc[:, 1:35]    
#df_QCsummary3 = df_VariantReqMatch1.iloc[:, 2:35].reset_index()          
# print(df_QCsummary3['sample']) 
# print(df_QCsummary3['VariantType'])

#if you want to check what versions of pandas and python (respectively) you're using:
# print(pd.__version__)
# print(sys.version)

#to check datatypes of columns that may cause issues/conflicts:
# print(df_QCsummary3['num_observed_mutations'].dtypes)
# print(df_QCsummary3['pct_covered_bases'].dtypes)

#print(df_QCsummary3)

#----------------------------------------------


#-------------Not Used Currently------------
#Store RunNum as variable in case you need it for file naming. I don't use it here):
# remove duplicates - only keep one line of Run#, and only want last column (the Run# column):
RunNum5 = df_VariantReqMatch1.drop_duplicates(subset=['RunNum'], keep='first').iloc[:, 34:35] 
#print(RunNum5.iloc[:, -1].to_string(index=False)) #worked (just prints the run # for each table)
# remove Headers and index to store just the Run# in the RunNum6 variable:
RunNum6 = RunNum5.iloc[:, -1].to_string(index=False)
#print(RunNum6) #works

#------------------------------------------



#-------------SAVE FILE---------------------

# Remove Extra Index Column
df_VariantReqMatch2 = df_VariantReqMatch1.iloc[:, 1:35]
# print(df_QCsummary3)       # has 1 index row and all columns (34)
# print(df_VariantReqMatch1) # has extra index row and 34 columns (35 total)
# print(df_VariantReqMatch2) # has 1 index row and all 34 columns


# Save output to file:
df_VariantReqMatch2.to_csv(MiSeqRunID + '_' + 'MissingPlus_QC_lineage_VoC_OrderedFinal_PlusVoCcalls.csv')  #Alternative file save if you don't want to use run# here (e.g. if multiple run numbers are in the VoC request sheet)
    
