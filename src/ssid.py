import subprocess


def start(code):
    """
    This function starts the program
    """
    r = subprocess.run(
        ["nmcli", "-f", "SSID", "dev", "wifi"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    grep = r.split("\n")

    s = subprocess.run(
        ["nmcli", "-f", "SECURITY", "dev", "wifi"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    grep_s = s.split("\n")

    networks = [
        k.strip()
        for k in grep
        if (k.strip() != "SSID") and (k.strip() != "--") and (k.strip() != "")
    ]
    net_type = [
        k.strip() for k in grep_s if (k.strip() != "SECURITY") and (k.strip() != "")
    ]

    ssid = []
    security = []

    for i in enumerate(networks):
        if i[1] not in ssid:
            ssid.append(i[1])
            security.append(net_type[i[0]])

    if code == 0:
        print(ssid)
        print(security)
    else:
        return [ssid, security]


if __name__ == "__main__":
    start(0)
