#! ./env/bin/python

from etmMV.__version__ import version
from etmMV.view import check_output

gb = "".join( chr(x) for x in check_output("git branch"))
print('branch:')
print(gb)
gs = "".join( chr(x) for x in check_output("git status -s"))
print('status:')
print(gs)

possible_extensions = ['a', 'b', 'rc', 'post', 'dev']
pre = post = version
ext = 'a'
ext_num = 1
for poss in possible_extensions:
    if poss in version:
        ext = poss
        pre, post = version.split(ext)
        ext_num = int(post) + 1
        break

# print(version, pre, post, ext)

new_ext = f"{pre}{ext}{ext_num}"
# print(pre)
parts = pre.split('.')
# print(parts)
parts[-1] = str(int(parts[-1]) + 1)
new_patch = ".".join(parts)

import os
version_file = os.path.join(os.getcwd(), 'etmMV', '__version__.py')
# print('version_file', version_file)

print(f"""\
The current version is {version}.
  p: The patch level can be incremented to give version: {new_patch}
  e: The {ext} extension level can be incrmented to give: {new_ext}\
""")
res = input(f"increment patch, p, or extension, e? [pe]: ")

new_version = ''
if res and res.lower() == 'e':
    new_version = new_ext
elif res and res.lower() == 'p':
    new_version = new_patch

if new_version:
    with open(version_file, 'w') as fo:
        fo.write(f"version = '{new_version}'")
    print(f"new version: {new_version}")
else:
    print(f"retained version: {version}")

