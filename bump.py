#! ./env/bin/python

from etm.__version__ import version
from etm.view import check_output
import pendulum
import sys

def byte2str(b):
    return "".join( chr(x) for x in b )


gb = byte2str(check_output("git branch"))
print('branch:')
print(gb)
gs = byte2str(check_output("git status -s"))
if gs:
    print('status:')
    print(gs)
    print("There are uncommitted changes.")
    ans = input("Cancel? [Yn] ")
    if not (ans and ans.lower() == "n"):
        sys.exit()

# PEP 440 extensions
# possible_extensions = ['a', 'b', 'rc', '.post', '.dev']
# For etm only the following will be used 
possible_extensions = ['a', 'b', 'rc']

pre = post = version
ext = 'a'
ext_num = 1
for poss in possible_extensions:
    if poss in version:
        ext = poss
        pre, post = version.split(ext)
        ext_num = int(post) + 1
        break

extension_options = {
        'a': {'a': f'a{ext_num}', 'b': 'b0', 'r': 'rc0'},
        'b': {'b': f'b{ext_num}', 'r': 'rc0'},
        'rc': {'r': f'rc{ext_num}'},
        }


# print(version, pre, post, ext)

new_ext = f"{pre}{ext}{ext_num}"
# print(pre)
parts = pre.split('.')
# print(parts)
parts[-1] = str(int(parts[-1]) + 1)
new_patch = ".".join(parts)

opts = [f'The current version is {version}']
if ext and ext in extension_options:
    i = 0
    for k, v in extension_options[ext].items():
        opts.append(f"  {k}: {pre}{v}")
    opts.append(f"  p: {new_patch}")

import os
version_file = os.path.join(os.getcwd(), 'etm', '__version__.py')
# print('version_file', version_file)

# print(f"""\
# The current version is {version}.
#   e: The {ext} extension level can be incrmented to give: {new_ext}\
#   p: The patch level can be incremented to give version: {new_patch}
# """)
# res = input(f"increment patch, p, or extension, e? [pe]: ")

print("\n".join(opts))
res = input(f"Which new version? ")

new_version = ''
res = res.lower()
if res in extension_options[ext]:
    new_version = f"{pre}{extension_options[ext][res]}"
elif res == 'p':
    new_version = new_patch

print(f"new version: {new_version}")

sys.exit()

if new_version:
    with open(version_file, 'w') as fo:
        fo.write(f"version = '{new_version}'")
    print(f"new version: {new_version}")
    tmsg = f"Tagged version {new_version}."
    check_output(f"git commit -a -m '{tmsg}'")
    version_info = byte2str(check_output("git log --pretty=format:'%ai' -n 1"))
    check_output(f"git tag -a -f '{new_version}' -m '{version_info}'")

    count = 100
    check_output(f"echo 'Recent changes as of {pendulum.now()}:' > CHANGES.txt")
    check_output(f"git log --pretty=format:'- %ar%d %an%n    %h %ai%n%w(70,4,4)%B' --max-count={count} >> CHANGES.txt")
    check_output(f"git commit -a --amend -m '{tmsg}'")

else:
    print(f"retained version: {version}")

