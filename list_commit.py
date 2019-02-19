#!/usr/bin/env python3
import urllib.request
import sys
from bs4 import BeautifulSoup
BASE_URL = "https://chromium.googlesource.com/chromium/src.git/+log/master/"
file = "content/public/common/content_features.cc"
if len(sys.argv) < 2:
    print ("Usage: "+ str(sys.argv[0])+" FILE")
    print("Using "+file) 
else:
    file = sys.argv[1]

page = urllib.request.urlopen(BASE_URL + file);
soup = BeautifulSoup(page)
commitsLinks = soup.find_all('a', class_='u-sha1 u-monospace CommitLog-sha1')
commitsLinks[0].get("")
print(commits)
