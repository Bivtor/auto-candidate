import os

path = "/Users/victorrinaldi/Downloads/" + \
    os.popen("ls -t /Users/victorrinaldi/Downloads/ | head -n1").read()

print(path.strip())
