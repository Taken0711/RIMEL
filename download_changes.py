import sys
import requests
import subprocess
import os
import re
import result_api



RAW_PATTERN = re.compile(r"(.*\/chromium\/[^\/]+\/[^\/]+)(\/.*)")
DEBUG_LOG_ENABLE = True



if len(sys.argv) < 2:
    print("Usage : " + sys.argv[0] + " PATH_TO_COMMIT_LIST.txt")
    exit 
def log(data):
    if DEBUG_LOG_ENABLE:
        print(data)
    

# Only for poc
def run_lizard(path): 
    proc = subprocess.Popen(['lizard', path, '-t', '4', '-l', 'cpp','--csv'], stdout=subprocess.PIPE)
    totalComplexity = 0
    while True:
        line = proc.stdout.readline().decode("utf-8")
        if line:
            elements = line.split(",")
            totalComplexity = totalComplexity + int(elements[1])
        else:
            break
    return totalComplexity

def is_valid_file(filename):
    return filename.endswith(".cc") or filename.endswith(".h")

def get_file_content(file):
    return requests.get(file).text

def write_file(filename, content):
    path = os.path.dirname(filename)
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True) 
        
    fileOnDisk = open(filename,"w+")
    fileOnDisk.write(content)
    fileOnDisk.close()

def process_commit(commit_sha1):
    
    log("Process commit "+ commit_sha1)
    result = requests.get('https://api.github.com/repos/chromium/chromium/commits/'+commit_sha1)
    files = list_modified_files(result)
    for f in files:
        filename = f["filename"]
        if is_valid_file(filename):
            log("Process file "+ filename)

            file_path = commit_sha1 + "/AFTER/" + filename

            fileContent = get_file_content(f["url"])
            write_file(file_path, fileContent)

            matcher = RAW_PATTERN.match(f["url"])
            if matcher:
                start, end = matcher.groups()
                oldFile = start + "~" + end
                log(oldFile)
                fileContent = get_file_content(oldFile)
                filename = commit_sha1 + "/BEFORE/" + filename
                write_file(filename, fileContent)
            else:
                log("DOESNT MATCH "+ f["url"] )
    return {"old": commit_sha1 + "/BEFORE/", "new": commit_sha1 + "/AFTER/"}




def list_modified_files(results):
    files = []
    for file in results.json()["files"]:
        files.append({"filename":file["filename"], "url":file["raw_url"]})

    return files



with open(sys.argv[1]) as f:
    for line in f:
        commit=line[:-1]
        if not result_api.already_computed(commit):
            paths = process_commit(commit)    
            totalbefore = run_lizard(paths["old"])
            totalAfter = run_lizard(paths["new"])
            result_api.add_result(commit, {"before":totalbefore, "after": totalAfter, "diff": (totalAfter- totalbefore)})
        else:
            print("Commit "+ commit + " already processed")  
