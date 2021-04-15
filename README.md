# VoCcaller
Classifies each sample in table as VoC or not (or QC fail). Adds Columns to output of mergeQCresults_plusMissing (VariantYesNo, VariantType columns added). For use on server/in unix environment. 

You can run this on a PC (windows etc) with python3 (e.g. Anaconda Navigator and Spyder IDE) as well, if you change the directory paths for reading in files and the output file as needed.

<b>This script will take the output csv table of mergeQCresults_plusMissing.py or mergeQCresults_plusMissing_v3.py as input, and:</b>

Create 4 new columns at the end: 

    VariantYesNo	VariantType	LibraryNum	RunNum


<b>Example output:</b>
![image](https://user-images.githubusercontent.com/72042148/114810083-382fa580-9d60-11eb-8c71-48d71242fb68.png)


<b>VariantYesNo:</b>

Populate the <b>VariantYesNo column</b> with either Yes, No, Failed, Failed (Excess_Ambiguity), Possible, Warning.

    Populates column with <b>Failed (Excess Ambiguity)</b>, if: the ['qc_pass_x'] column contains "EXCESS_AMBIGUITY" flag     {these may be mixed sequences, so this flag allows you to manually inspect these, and fail/repeat them, etc as needed}

    Populates column with <b>Yes</b>, if: lineage matches those listed in the Positive_values variable (line 52) (['B.1.1.7', 'B.1.351', 'P.1', 'B.1.525'])     {you can add more lineages to the Positive_values variable}

    Populates column with <b>Possible</b>, if: ['lineage_x'] column value is 'none' AND ['num_observed_mutations'] column value > 4     {you can change this value as you monitor trends in your data}   {essentially, if no lineage is assigned, but VoC mutations were detected, then it should be manually inspected to confirm it is/isn't a VoC}

    Populates column with <b>Warning</b>, if: ['lineage_x'] column value is NOT 'none' AND is NOT null AND ['lineage_x'] is NOT in Positive_values variable AND ['num_observed_mutations'] column value > 4     {essentially, if the lineage is a non-VoC lineage, but has VoC mutations detected}

    Populates column with <b>Failed</b>, if: (['lineage_x'] column value is 'none' AND ['pct_covered_bases'] column value < 85.00) OR (['lineage_x'] column value is null AND ['pct_covered_bases'] column value is null)     {the 2nd means it has no data for either column, meaning it was one of the "missing" samples that didn't have enough data to make a consensus file - thus it fails WGS QC}

    Populates column with <b>No</b>, if: ['lineage_x'] column value is NOT 'none'    {at this point, all the other criteria would have been evaluated, so anything left is a non-VoC}


<b>VariantType:</b>

Populate the <b>VariantType column</b> with: 

    (if VariantYesNo = Yes): Brazil (P.1), UK (B.1.1.7), SA (B.1.351), Nigerian (B.1.525)  
    
                  {note that you can add/remove VoCs and VoIs that you monitor for this - modify the Positive_values variable (line 52), and the conditions for Variant Type in the script (---ADD VARIANT COLUMNS to QC Summary Table---- section)}

    (if VariantYesNo = No): Not a VoC

    (if VariantYesNo = Failed): Failed WGS QC

    (if VariantYesNo = Failed (Excess_Ambiguity)): Failed WGS QC  
    
                    {these may be mixed sequences, so this flag allows you to manually inspect these, and fail/repeat them, etc as needed}

    (if VariantYesNo = Warning): Possible Contamination with ['lineage_x'] and ['watchlist_id'] (e.g. Possible Contamination with B.1.1 and P.1)  
    
                    {This will flag anything that has a non-VoC lineage but has 5+ VoC mutations, and NO Excess_Ambiguity flag, so you can manually inspect these as well for mixed samples, or issues with pangolin lineage calls, etc} 

    (if VariantYesNo = Possible): Possible P.1, Possible B.1.1.7, Possible B.1.351, Possible B.1.525  
    
                    {you can specify extra lineages in the script (---ADD VARIANT COLUMNS to QC Summary Table---- section, conditions2 and choices2 variables)}


<b>LibraryNum: (See Sample Naming examples below) </b>

LibraryNum column will be populated with only the Library Plate # for each sample


<b>RunNum: (See Sample Naming examples below) </b>

RunNum column will be populated with the lowest LibraryPlate# to the highest for a WGS run (if multiple per run) (e.g. if one sequencer run has libraries 200, 201, 202, 203 - then RunNum column will be 200-203 for <b>all</b> samples)


# Assumptions:

## Pipelines used: (artic v1.3 and ncov-tools v1.5)
We use the following pipelines to produce results used below: BCCDC-PHL/ncov2019-artic-nf (forked from connor-lab/ncov2019-artic-nf) and BCCDC-PHL/ncov-tools (forked from jts/ncov-tools)

You should have the same <b>directory structure</b> set up on your server/PC as specified for mergeQCresults_plusMissing.py (https://github.com/Kim-Macdonald/mergeQCresults_plusMissing#assumed-directory-structure ) (or change the paths in script to reflect where your input files are, and where you want output files saved):


## Sample Naming:
Our samples/fastq files have names such as (artificial/example fastq IDs shown below):

    NEG20210403-nCoVWGS-221-A

    POS20210403-nCoVWGS-221-A

    A1234567890-221-A-D05

    A1234567891-221-A-F02

(For samples (the bottom 2 fastqIDs), the first part is the sampleID, 2nd is the library plate #, 3rd part is barcode/index set used, 4th is the library plate well location)

(For controls (the top 2 fastqIDs), the first part is the control/sampleID (includes date of library prep), 2nd is standardized text, 3rd is the library plate #, 4th part is barcode/index set used)

The script treats these differently. Only pulls out the sampleID for samples (to populate sample column only). Controls are left as-is. FastqIDs are left as-is in sample_name column. 

If this doesn't fit your needs, you can comment out the ----Replace SAMPLE column string with CID only or full pos/neg cntrl name--- section in the script (near end). This will keep the fastqID in both sample and sample_name columns. 


## Library Plate and Run Numbers: 

If your samples don't have Library Plate # in the name (as illustrated in Sample Naming above), then you can also comment out the -------LIB NUM & RUN NUM COLUMN:-------- section for adding LibraryNum and RunNum columns in the script. 

These columns won't be added to the end of the table (<b>it will just have the 2 VariantYesNo and VariantType columns added at the end</b>). 

<b>Otherwise: </b>

LibraryNum column will be populated with only the Library Plate # for each sample

RunNum column will be populated with the lowest LibraryPlate# to the highest for a run (if multiple per run) (e.g. if a run has libraries 200, 201, 202, 203 - then RunNum column will be 200-203 for <b>all</b> samples)


# Usage:

Save the mergeQCresults_plusMissing.py (or _v3.py script) and addVoCcalls_RunNum.py scripts somewhere on your server or unix PC. 

Run mergeQCresults_plusMissing.py on the server, as per mergeQCresults_plusMissing.py instructions (https://github.com/Kim-Macdonald/mergeQCresults_plusMissing )

Then run VoCcaller script (Both are combined in command below)

(replace [MiSeqRunID] with your MiSeqRunID/RunName or Directory for the sequencing run of interest):

    cd sequence/analysis/run/directory/[MiSeqRunID]; conda activate pandas; python3 path/to/mergeQCresults_plusMissing.py; python3 path/to/addVoCcalls_RunNum.py; conda deactivate
    
    
    OR for artic v1.3 and ncov-tools v1.5:
    
    cd sequence/analysis/run/directory/[MiSeqRunID]; conda activate pandas; python3 path/to/mergeQCresults_plusMissing_v3.py; python3 path/to/addVoCcalls_RunNum.py; conda deactivate
    

Transfer the output file ([MiSeqRunID]_MissingPlus_QC_lineage_VoC_OrderedFinal_PlusVoCcalls.csv) to your PC, if desired, and merge with patient metadata, or VoC PCR data (to identify PCR negatives as possible conflicting results with WGS VoC results (or PCR positives with non-VoC lineages) and manually inspect), etc to report out/count/summarize VoC data along with WGS QC metrics and lineages. 

