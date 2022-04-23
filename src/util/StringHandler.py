import re 

class StringHandler:

    bracketRemove = "\(.*\)|\s-\s.*" 
    bracketExtraction = re.compile(r"\(([^)]+)", re.S)
