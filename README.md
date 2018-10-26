# MetaPAD
Meta Pattern-driven Attribute Discovery from Massive Text Corpora

## Datasets 
### NYT News Dataset 
`zip/data-metapad.zip`
  typed news corpus
  
You can check your output with `zip/output-metapad.zip`
  meta patterns after segmentation (top or bottom)
  matching tables with meta patterns of appropriate granularity (top-down or bottom-up)
  results of information extraction using meta patterns (attribute)
  


### Newsbank Dataset 
Entity linked done by matching to Freebase (thus possible typing errors).

Data is in the `input/` folder. 

## Requirements 
This version should be compatible with Python3. 
C++ code requires OpenMP library to run.

## How to run
Execute `run.sh`

## Code 
- Encryption: `metapad.py` 
- pattern segmentation and classification : C++
- synonymous pattern grouping: Python `metapad.py` 
- type level adjustment: Python `metapad.py` 


