from util import print_strings
import strings

from galaxy import Galaxy
from enterprise import Enterprise

galaxy = Galaxy()
enterprise = Enterprise(galaxy)


def run():
    print_strings(strings.titleStrings)
    while True:
        enterprise.display_mission()
        print_strings(strings.commandStrings)
        while enterprise.energy > 0 and not enterprise.destroyed and galaxy.galaxy_klingon_count() > 0 \
                and enterprise.time_remaining > 0:
            enterprise.command_prompt()
            enterprise.display_status()
        restart()


def restart():
    if enterprise.energy <= 0:
        print("***** Enterprise has been recovered for a new mission. *****")
    elif enterprise.destroyed:
        print("***** Enterprise has been salvaged for a new mission. *****")
    elif galaxy.galaxy_klingon_count() <= 0:
        print("***** Enterprise has been refitted for a new mission. *****")
    elif enterprise.time_remaining <= 0:
        print("***** Enterprise has been retasked for a new mission. *****")

    galaxy.restart()
    enterprise.restart()


if __name__ == '__main__':
    run()
