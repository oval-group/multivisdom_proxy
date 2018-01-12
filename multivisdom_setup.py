# For python 2 and 3 compatibility
from __future__ import print_function
import sys
if sys.version_info[0] < 3:
    input = raw_input


import argparse
import os
import stat
import shutil
import getpass

CONF_EXTENSION = ".multivisdom"

ACTION_STOP = 0
ACTION_LIST = 1
ACTION_ADD  = 2
ACTION_DEL  = 3
ACTION_PASS = 4
ACTION_INIT = 5
ACTION_CLEAN= 6
NUM_ACTIONS = 7

ALL_CONF_TEMPLATE = """
map $http_upgrade $connection_upgrade {{
        default upgrade;
        '' close;
}}

server {{
    listen {port};

    # Deny anything else than what we specify
    location / {{ deny all; }}

    include {nginx_path}/sites-available/multivisdom/*.conf;
}}
"""

USER_CONF_HTML_TEMPLATE = """
location /{user}/ {{
    rewrite (.*) /{user};
}}

location = /{user} {{
    auth_basic "Protected access";
    auth_basic_user_file {cred_file};
    default_type "text/html";
    alias {html_file};
}}
"""

USER_CONF_TEMPLATE = """
{header}
location {path}/ {{
    auth_basic "Protected access";
    auth_basic_user_file {cred_file};
    proxy_pass {server};
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $http_host{path};
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}}
"""

USER_HTML_HEADER = """
<title>Boards for {user}</title>
<body>
<h2>Boards for {user}</h2>
<hr>
<ul>
"""

USER_HTML_CONTENT = """
<li><a href="{path}">{path}</a> {descr}
"""

USER_HTML_FOOTER = """
</ul>
<hr>
</body>
</html>
"""

SPECIAL_COMMENT_MARK = "###"
SPECIAL_COMMENT_SEPARATOR = "||"

def get_shared_conf(args):
    all_conf_file_path = os.path.join(args.nginx_path, "sites-available", "multi_visdom_all.conf")
    all_conf_link_path = os.path.join(args.nginx_path, "sites-enabled", "multi_visdom")
    all_conf_folder = os.path.join(args.nginx_path, "sites-available", "multivisdom")
    return all_conf_file_path, all_conf_link_path, all_conf_folder

def get_user_files(args):
    user_conf_file = os.path.join(args.nginx_path, "sites-available", "multivisdom", args.user+".conf")
    user_cred_file = os.path.join(args.nginx_path, "sites-available", "multivisdom", args.user+".htpasswd")
    user_html_file = os.path.join(args.nginx_path, "sites-available", "multivisdom", args.user+".html")
    return user_conf_file, user_cred_file, user_html_file


def ask_what_to_do():
    print("")
    print("")
    print("This tool will help you configure a multivisdom proxy with nginx.")
    print("Possible actions:")
    print("{}: Quit.".format(ACTION_STOP))
    print("{}: List all links for your user.".format(ACTION_LIST))
    print("{}: Add a link for your user.".format(ACTION_ADD))
    print("{}: Delete a link for your user.".format(ACTION_DEL))
    print("{}: Add access credential for your user's links.".format(ACTION_PASS))
    print("")
    print("Options that should be used by privileged users only:")
    print("{}: Initialize configuration of nginx (done once by main user).".format(ACTION_INIT))
    print("{}: Nuke all files from the nginx configuration created by this script.".format(ACTION_CLEAN))
    while True:
        answer = input("\nAction number: ")
        try:
            answer = int(answer)
            if answer >= 0 and answer < NUM_ACTIONS:
                return answer
        except:
            pass
        print("Your answer should be just a number below {}.".format(NUM_ACTIONS))

def get_perm(path):
    return stat.S_IMODE(os.lstat(path)[stat.ST_MODE])

def make_writeable(path):
    os.chmod(path, get_perm(path) | stat.S_IWOTH)

def init_nginx(args):
    if (not os.path.isdir(os.path.join(args.nginx_path, "sites-available"))) or \
       (not os.path.isdir(os.path.join(args.nginx_path, "sites-enabled"))):
        raise RuntimeError("Provided nginx path is not correct, 'sites-available' or 'sites-enabled' not existing.")

    all_conf_file_path, all_conf_link_path, all_conf_folder = get_shared_conf(args)

    if os.path.exists(all_conf_file_path) or os.path.exists(all_conf_folder):
        print("Some multivisdom configuration already exists, you need to clean you nginx config first.")
        while True:
            answer = input("Clean and continue (c) or quit (q)? ")
            if answer == "q":
                return
            elif answer == "c":
                nuke_nginx(args)
                break

    try:
        os.mkdir(all_conf_folder)
    except:
        raise RuntimeError("You do not have write access into the nginx folder, ask a user which have access to do it.")
    make_writeable(all_conf_folder)

    # Assume that we can write in the nginx config folders from now on.
    with open(all_conf_file_path, "w") as f:
        f.write(ALL_CONF_TEMPLATE.format(port=args.port, nginx_path=args.nginx_path))

    os.symlink(all_conf_file_path, all_conf_link_path)

    print("Trying to reload nginx so that changes are taken into account...")
    os.system("sudo /usr/sbin/service nginx reload")

    print("Init completed.")

def try_del(path):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except:
        print("could not remove {} either it does not exist or you are not allowed to.".format(path))

def nuke_nginx(args):
    if (not os.path.isdir(os.path.join(args.nginx_path, "sites-available"))) or \
       (not os.path.isdir(os.path.join(args.nginx_path, "sites-enabled"))):
        raise RuntimeError("Provided nginx path is not correct, 'sites-available' or 'sites-enabled' not existing.")

    all_conf_file_path, all_conf_link_path, all_conf_folder = get_shared_conf(args)

    try_del(all_conf_link_path)
    try_del(all_conf_file_path)
    try_del(all_conf_folder)

    print("Trying to reload nginx so that changes are taken into account...")
    os.system("sudo /usr/sbin/service nginx reload")

    print("Nuke completed.")

def get_available_entries(args):
    user_file, _, _ = get_user_files(args)
    entries = []
    if os.path.isfile(user_file):
        with open(user_file, "r") as f:
            for l in f:
                if l.startswith(SPECIAL_COMMENT_MARK):
                    l = l.strip().replace(SPECIAL_COMMENT_MARK, '')
                    entries.append(l.split(SPECIAL_COMMENT_SEPARATOR))
    return entries

def write_entries(args, entries):
    user_file, user_cred_file, user_html_file = get_user_files(args)
    with open(user_file, "w") as output_f:
        for path, server, descr in entries:
            header = SPECIAL_COMMENT_MARK+path+SPECIAL_COMMENT_SEPARATOR+server+SPECIAL_COMMENT_SEPARATOR+descr
            output_f.write(USER_CONF_TEMPLATE.format(header=header, path=path, server=server, cred_file=user_cred_file))
            output_f.write("\n\n")

        # Add html page to it
        output_f.write(USER_CONF_HTML_TEMPLATE.format(user=args.user, cred_file=user_cred_file, html_file=user_html_file))
        output_f.write("\n\n")

    with open(user_html_file, "w") as output_f:
        output_f.write(USER_HTML_HEADER.format(user=args.user))
        for path, _, descr in entries:
            output_f.write(USER_HTML_CONTENT.format(path=path, descr=descr))
        output_f.write(USER_HTML_FOOTER)

    print("Trying to reload nginx so that changes are taken into account...")
    os.system("sudo /usr/sbin/service nginx reload")

def list_available(args):
    entries = get_available_entries(args)
    print("Available links for {}:".format(args.user))
    for path, server, descr in entries:
        print("{} => {} ({})".format(path, server, descr))

def add_entry(args):
    entries = get_available_entries(args)
    path = input("Link name on proxy server: ")
    serv_addr = input("Server address: ")
    serv_port = input("Server port: ")
    descr = input("One-line description: ")

    if path.startswith('/'):
        path = path[1:]
    path = "/{}/{}".format(args.user, path)
    server = "http://{}:{}/".format(serv_addr, serv_port)

    already_exists = False
    for p, _, _ in entries:
        if p == path:
            already_exists = True
            break
    if already_exists:
        print("The path {} is already used, please choose a different one.".format(path))
        return

    print("You are about to create the mapping: {} => {}".format(path, server))
    while True:
        answer = input("Are you sure? (y/n) ")
        if answer == "y":
            break
        elif answer == "n":
            return

    entries.append((path, server, descr))
    write_entries(args, entries)

    _, user_cred_file, _ = get_user_files(args)
    if not os.path.exists(user_cred_file):
        while True:
            answer = input("No credentials exist for your user, do you want to add one (y/n)? ")
            if answer == "y":
                add_cred(args)
                break
            elif answer == "n":
                break


def delete_entry(args):
    entries = get_available_entries(args)
    print("Available links for {}:".format(args.user))
    for idx, (path, server, descr) in enumerate(entries):
        print("{}: {} => {} ({})".format(idx, path, server, descr))
    while True:
        answer = input("Id of link to delete: ")
        try:
            to_del = int(answer)
            if to_del < 0 or to_del >= len(entries):
                print("Enter one of the ids above.")
            else:
                break
        except:
            print("Enter a single number.")

    entry_to_del = entries[to_del]
    print("You are going to delete {} => {} ({})".format(*entry_to_del))
    while True:
        answer = input("Are you sure (y/n)? ")
        if answer == "y":
            break
        elif answer == "n":
            return

    del entries[to_del]
    write_entries(args, entries)

def add_cred(args):
    _, user_cred_file, _ = get_user_files(args)
    username = input("What is the username for the credentials? ")
    # create password file if it does not exist yet
    opt = '-c' if not os.path.exists(user_cred_file) else ''
    os.system("htpasswd {} {} {}".format(opt, user_cred_file, username))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Configure nginx for multivisdom proxy.')
    parser.add_argument("--nginx_path", type=str, default="/etc/nginx",
                        help="path to the nginx's install folder.")
    parser.add_argument("--port", type=int, default=1234,
                        help="Port on which the server will be available (used for init only).")
    args = parser.parse_args()

    args.user = getpass.getuser()
    print("Username detected automatically: {}".format(args.user))

    while True:
        todo = ask_what_to_do()

        if todo == ACTION_STOP:
            break
        elif todo == ACTION_INIT:
            init_nginx(args)
        elif todo == ACTION_CLEAN:
            nuke_nginx(args)
        elif todo == ACTION_LIST:
            list_available(args)
        elif todo == ACTION_ADD:
            add_entry(args)
        elif todo == ACTION_DEL:
            delete_entry(args)
        elif todo == ACTION_PASS:
            add_cred(args)
        else:
            print("Wrong choice.")



