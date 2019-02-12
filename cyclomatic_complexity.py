import subprocess
import re
import os
from git import Repo
import result_api
from enum import Enum
import sys

class Mode(Enum):
    FUNCTIONS = 1
    FILES = 2
    GLOBAL = 3

NB_OF_THREADS = 4
PATH = sys.argv[1]

FUNCTION_PATTERN = re.compile(r"\s*(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+)\s+([^@]+)@(\d+)-(\d+)@([^\s]+)")
FILE_HEADER_PATTERN = re.compile(r"NLOC\s+Avg\.NLOC\s+AvgCCN\s+Avg\.token\s+function_cnt\s+file")
FILE_PATTERN = re.compile(r"\s*(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+)\s+([^\s]+)")
GLOBAL_HEADER_PATTERN = re.compile(r"Total nloc\s+Avg\.NLOC\s+AvgCCN\s+Avg\.token\s+Fun Cnt\s+Warning cnt\s+Fun Rt\s+nloc Rt")
GLOBAL_PATTERN = re.compile(r"\s*(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+\.?\d*)\s+(\d+)\s+(\d+)\s+(\d+\.?\d*)\s+(\d+\.?\d*)")


def append_in_dict(d, key, value):
    if key not in d:
        d[key] = []
    d[key].append(value)


def is_test(location, function):
    fn = function.split("::")[-1]
    if fn == "TEST" or fn == "TEST_F":
        return True
    if "test" in location.split(os.sep) or "unittest" in os.path.basename(location):
        return True
    return False

res = {"functions": {}, "files": {}, "global": {}}
repo = Repo(PATH)

print("Analyzing project...")
proc = subprocess.Popen(['lizard', PATH, '-t', '4', '-l', 'cpp','--csv','-w','./whitelist.txt'], stdout=subprocess.PIPE)

mode = Mode.FUNCTIONS

while True:
    line = proc.stdout.readline().decode("utf-8")
    if line:
        if FILE_HEADER_PATTERN.match(line):
            mode = Mode.FILES
            continue
        elif GLOBAL_HEADER_PATTERN.match(line):
            mode = Mode.GLOBAL
            continue
        
        if mode == Mode.FUNCTIONS:
            matcher = FUNCTION_PATTERN.match(line)
            if matcher:
                #   NLOC    CCN   token  PARAM  length  location
                nloc, ccn, tokens, params, length, function, _, _, location = matcher.groups()
                if not is_test(location, function):
                    append_in_dict(res["functions"], function, {"nloc": nloc, "ccn": ccn})
        elif mode == Mode.FILES:
            matcher = FILE_PATTERN.match(line)
            if matcher:
                #   NLOC    AvgNLOC    AvgCCN      Avg token   function_cnt    file
                nloc, avgnloc, avgccn, avgtoken, avgfunction, location = matcher.groups()
                if not is_test(location, ""):
                    append_in_dict(res["files"], location, {"nloc": nloc, "avgnloc": avgnloc, "avgccn": avgccn})
        elif mode == Mode.GLOBAL:
            matcher = GLOBAL_PATTERN.match(line)
            if matcher:
                #   Total nloc  AvgNLOC    AvgCCN    Avgtoken   FunCnt    Warning cnt     Fun Rt    nloc Rt
                nloc, avgnloc, avgccn, avgtoken, fctcnt, warning, _, _ = matcher.groups()
                if not is_test(location, ""):
                    append_in_dict(res["global"], location, {"nloc": nloc, "avgnloc": avgnloc, "avgccn": avgccn, "fctcnt": fctcnt, "warning": warning})
    else:
        break


result_api.add_result(repo.head.object.hexsha, res)

