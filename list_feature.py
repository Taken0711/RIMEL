#!/usr/bin/env python3

import re

regex = r"CONTENT_EXPORT\s+extern\s+const\s+base::Feature\s+(\w+)\s*;"

with open('content_feature.h', 'r') as content_file:
    content = content_file.read()
    features = re.findall(regex, content)
    print(features)


