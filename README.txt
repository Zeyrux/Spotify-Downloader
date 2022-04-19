changes in Interpreter/Lib/site-packages/pytube/cipher.py:

line 288 to:
nfunc=re.escape(function_match.group(1))),

change in function get_throttling_function_name function_patterns to:
r'a\.[a-zA-Z]\s*&&\s*\([a-z]\s*=\s*a\.get\("n"\)\)\s*&&\s*'
r'\([a-z]\s*=\s*([a-zA-Z0-9$]{2,3})(\[\d+\])?\([a-z]\)'