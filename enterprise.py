import strings
from util import print_strings, input_double, direction, distance, print_line, variability, \
    calculate_vector, calculate_approx_vector, location, calculate_delivered_energy
from abc import abstractmethod


class Actor:

    def __init__(self):
        self.name = "Actor"
        self.damage = 0

    @abstractmethod
    def act(self):
        pass

    def repair(self):
        if self.damage > 0:
            self.damage -= 1
            if self.damage == 0:
                if self.name.endswith("s"):
                    print("{0} have been repaired.".format(self.name))
                else:
                    print("{0} has been repaired.".format(self.name))
            print()
            return True
        return False

    def take_damage(self, val):
        self.damage = val
        if self.name.endswith("s"):
            print("{0} are malfunctioning".format(self.name))
        else:
            print("{0} is malfunctioning".format(self.name))


class Navigation(Actor):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "warp engines"

    def act(self):
        galaxy = self.parent.galaxy
        max_warp_factor = 8.0
        if self.damage > 0:
            max_warp_factor = 0.2 + variability(8) / 10.0
            print_line("Warp engines damaged. Maximum warp factor: {0}".format(max_warp_factor), 0, 1)

        dirct = input_double("Enter course (1.0--8.9): ")
        if not dirct or dirct < 1.0 or dirct > 9.0:
            print_line("Invalid course.", 0, 1)
            return

        dist = input_double("Enter warp factor (0.1--{0}): ".format(max_warp_factor))
        if not dist or dist < 0.1 or dist > max_warp_factor:
            print_line("Invalid warp factor.", 0, 1)
            return

        print()

        dist *= 8
        energy_required = int(dist)
        if energy_required >= self.parent.energy:
            print_line("Unable to comply. Insufficient energy to travel that speed.", 0, 1)
            return
        else:
            print_line("Warp engines engaged.", 0, 1)
            self.parent.energy -= energy_required

        last_quad_x = self.parent.quadrant_x
        last_quad_y = self.parent.quadrant_y
        last_sect_x = self.parent.sector_x
        last_sect_y = self.parent.sector_y
        x = self.parent.quadrant_x * 8 + self.parent.sector_x
        y = self.parent.quadrant_y * 8 + self.parent.sector_y
        vx, vy = calculate_vector(dirct, dist)
        dx = vx / 1000
        dy = vy / 1000

        galaxy.clear_current_quadrant_sector(self.parent.sector_x, self.parent.sector_y)

        obstacle = False
        for i in range(999):
            x += dx
            y += dy
            quad_x = int(int(round(x)) / 8)
            quad_y = int(int(round(y)) / 8)
            if quad_x == self.parent.quadrant_x and quad_y == self.parent.quadrant_y:
                sect_x = int(round(x)) % 8
                sect_y = int(round(y)) % 8
                if not galaxy.sector_is_empty(sect_x, sect_y):
                    self.parent.sector_x = last_sect_x
                    self.parent.sector_y = last_sect_y
                    galaxy.set_enterprise_sector(self.parent.sector_x, self.parent.sector_y)
                    print_line("Encountered obstacle within quadrant.", 0, 1)
                    obstacle = True
                    break
                last_sect_x = sect_x
                last_sect_y = sect_y

        if not obstacle:    # Not stopped inside the sector
            if x < 0:
                x = 0
            elif x > 63:
                x = 63
            if y < 0:
                y = 0
            elif y > 63:
                y = 63
            quad_x = int(int(round(x)) / 8)
            quad_y = int(int(round(y)) / 8)
            self.parent.sector_x = int(round(x)) % 8
            self.parent.sector_y = int(round(y)) % 8
            if quad_x != self.parent.quadrant_x or quad_y != self.parent.quadrant_y:
                self.parent.increment_date()
                self.parent.quadrant_x = quad_x
                self.parent.quadrant_y = quad_y
                self.parent.galaxy.set_current_quadrant(self.parent.quadrant_x, self.parent.quadrant_y,
                                                        self.parent.sector_x, self.parent.sector_y)
            else:
                galaxy.set_enterprise_sector(self.parent.sector_x, self.parent.sector_y)

        if galaxy.is_docking_location(self.parent.sector_x, self.parent.sector_y):
            self.parent.energy = 3000
            self.parent.torpedoes.torpedoes = 10
            self.parent.navigation.damage = 0
            self.parent.short_range_sensors.damage = 0
            self.parent.long_range_sensors.damage = 0
            self.parent.shields.damage = 0
            self.parent.computers.damage = 0
            self.parent.torpedoes.damage = 0
            self.parent.phasers.damage = 0
            self.parent.shields.level = 0
            self.parent.docked = True
        else:
            self.parent.docked = False

        self.parent.short_range_sensors.act()

        if self.parent.docked:
            print("Lowering shields as part of docking sequence...")
            print_line("Enterprise successfully docked with starbase.", 0, 1)
        else:
            if galaxy.current_quadrant_has_klingons() \
                    and last_quad_x == self.parent.quadrant_x and last_quad_y == self.parent.quadrant_y:
                self.parent.klingon_attack()
                print()
            elif not self.parent.repair_damage():
                self.parent.take_damage(-1)


class Shields(Actor):

    def __init__(self, parent):
        super().__init__()
        self.level = 0
        self.parent = parent
        self.name = "shields"

    def act(self):
        print("--- Shield Controls ----------------")
        print("Shields at {0}.".format(self.parent.shields.level))
        print("add = Add energy to shields.")
        print("sub = Subtract energy from shields.")
        print()
        command = input("Enter shield control command: ").strip().lower()
        print()
        if command == "add":
            adding = True
            max_transfer = self.parent.energy
        elif command == "sub":
            adding = False
            max_transfer = self.level
        else:
            print_line("Invalid command.", 0, 1)
            return
        transfer = input_double(
            "Enter amount of energy (1--{0}): ".format(max_transfer))
        if not transfer or transfer < 1 or transfer > max_transfer:
            print_line("Invalid amount of energy.", 0, 1)
            return
        print()
        if adding:
            self.parent.energy -= int(transfer)
            self.level += int(transfer)
        else:
            self.parent.energy += int(transfer)
            self.level -= int(transfer)
        print_line("Shield strength is now {0}. Energy level is now {1}.".format(self.level, self.parent.energy), 0, 1)


class ShortRangeSensors(Actor):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "short range sensors"

    def act(self):
        if self.damage > 0:
            print_line("Short range scanner is damaged. Repairs are underway.", 1)
            return
        self.parent.galaxy.quadrant_scanned(self.parent.quadrant_x, self.parent.quadrant_y)
        self.display_quadrant()
        print()

    def display_quadrant(self):
        galaxy = self.parent.galaxy
        quadrant_status = galaxy.current_quadrant.status()
        quadrant = galaxy.current_quadrant.quadrant()
        condition = "GREEN"
        if galaxy.current_quadrant_klingon_count() > 0:
            condition = "RED"
        elif self.parent.energy < 300:
            condition = "YELLOW"

        print("-=--=--=--=--=--=--=--=-          Region: {0}".format(quadrant.name))
        print(self.quadrant_status_row(0, quadrant_status), "           Quadrant: [{0},{1}]".format(quadrant.loc_x + 1,
                                                                                                    quadrant.loc_y + 1))
        print(self.quadrant_status_row(1, quadrant_status), "             Sector: [{0},{1}]"
              .format(self.parent.sector_x + 1, self.parent.sector_y + 1))
        print(self.quadrant_status_row(2, quadrant_status), "           Stardate: {0}".format(self.parent.star_date))
        print(self.quadrant_status_row(3, quadrant_status), "     Time remaining: {0}"
              .format(self.parent.time_remaining))
        print(self.quadrant_status_row(4, quadrant_status), "          Condition: {0}".format(condition))
        print(self.quadrant_status_row(5, quadrant_status), "             Energy: {0}".format(self.parent.energy))
        print(self.quadrant_status_row(6, quadrant_status), "            Shields: {0}"
              .format(self.parent.shields.level))
        print(self.quadrant_status_row(7, quadrant_status), "   Photon Torpedoes: {0}"
              .format(self.parent.torpedoes.torpedoes))
        print("-=--=--=--=--=--=--=--=-             Docked: {0}".format(self.parent.docked))

        if galaxy.current_quadrant_klingon_count() > 0:
            print_line("Condition RED: Klingon ship{0} detected."
                       .format("" if galaxy.current_quadrant_klingon_count() == 1 else "s"), 1, 0)
            if self.parent.shields.level == 0 and not self.parent.docked:
                print("Warning: Shields are down.")
        elif self.parent.energy < 300:
            print_line("Condition YELLOW: Low energy level.", 1, 0)

    def quadrant_status_row(self, y, status):
        sb = ""
        for x in range(8):
            sb += status[x][y]
        return sb


class LongRangeSensors(Actor):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "long range sensors"

    def act(self):
        if self.damage > 0:
            print_line("Long range scanner is damaged. Repairs are underway.", 0, 1)
            return
        self.parent.galaxy.print_quadrant_neighborhood(self.parent.quadrant_x, self.parent.quadrant_y)


class Computers(Actor):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "main computer"

    def act(self):
        commands = {"rec": self.display_galactic_record, "sta": self.display_status,
                    "tor": self.photon_torpedo_calculator,
                    "bas": self.starbase_calculator, "nav": self.navigation_calculator}

        if self.damage > 0:
            print_line("The main computer is damaged. Repairs are underway.", 0, 1)
            return
        print_strings(strings.computerStrings)
        command = input("Enter computer command: ").strip().lower()
        cmd = commands.get(command)
        if cmd is not None:
            cmd()
        else:
            print_line("Invalid computer command.", 1, 1)
        self.parent.take_damage(4)

    def display_galactic_record(self):
        status = self.parent.galaxy.galactic_record()
        print("Current quadrant: {0}-{1}.".format(self.parent.quadrant_x + 1, self.parent.quadrant_y + 1))
        print_line("-------------------------------------------------", 1, 0)
        sb = ""
        for j in range(8):
            for i in range(8):
                sb += "| "
                sb += status[i][j]
            sb += "| "
            print(sb)
            sb = ""
            print("-------------------------------------------------")
        print()

    def navigation_calculator(self):
        print_line("Enterprise located in quadrant [%s,%s]."
                   % (self.parent.quadrant_x + 1, self.parent.quadrant_y + 1), 1, 1)
        quad_x = input_double("Enter destination quadrant X (1--8): ")
        if quad_x is False or quad_x < 1 or quad_x > 8:
            print("Invalid X coordinate.")
            print()
            return
        quad_y = input_double("Enter destination quadrant Y (1--8): ")
        if quad_y is False or quad_y < 1 or quad_y > 8:
            print("Invalid Y coordinate.")
            print()
            return

        print()
        qx = int(quad_x) - 1
        qy = int(quad_y) - 1
        if qx == self.parent.quadrant_x and qy == self.parent.quadrant_y:
            print_line("That is the current location of the Enterprise.", 0, 1)
            return
        print("Direction: {0:1.2f}".format(direction(self.parent.quadrant_x, self.parent.quadrant_y, qx, qy)))
        print_line("Distance:  {0:2.2f}".format(distance(self.parent.quadrant_x, self.parent.quadrant_y, qx, qy)), 0, 1)

    def photon_torpedo_calculator(self):
        print()
        galaxy = self.parent.galaxy
        if not galaxy.current_quadrant_has_klingons():
            print_line("There are no Klingon ships in this quadrant.", 0, 1)
            return

        for ship in galaxy.current_quadrant_klingon_ships():
            text = "Direction {2:1.2f}: Klingon ship in sector [{0},{1}]."
            print(text.format(
                ship.sector_x + 1, ship.sector_y + 1,
                direction(self.parent.sector_x, self.parent.sector_y, ship.sector_x, ship.sector_y)))
        print()

    def starbase_calculator(self):
        print()
        if self.parent.galaxy.quadrant_has_starbase(self.parent.quadrant_x, self.parent.quadrant_y):
            sx, sy = self.parent.galaxy.current_quadrant.starbase_loc()
            print("Starbase in sector [%s,%s]." % (sx + 1, sy + 1))
            print("Direction: {0:1.2f}".format(
                direction(self.parent.sector_x, self.parent.sector_y, sx, sy)
            ))
            print("Distance:  {0:2.2f}".format(distance(self.parent.sector_x, self.parent.sector_y, sx, sy) / 8))
        else:
            print("There are no starbases in this quadrant.")
        print()

    def display_status(self):
        print()
        print("               Time Remaining: {0}".format(self.parent.time_remaining))
        print("      Klingon Ships Remaining: {0}".format(self.parent.galaxy.galaxy_klingon_count()))
        print("                    Starbases: {0}".format(self.parent.galaxy.galaxy_starbase_count()))
        print("           Warp Engine Damage: {0}".format(self.parent.navigation.damage))
        print("   Short Range Scanner Damage: {0}".format(self.parent.short_range_sensors.damage))
        print("    Long Range Scanner Damage: {0}".format(self.parent.long_range_sensors.damage))
        print("       Shield Controls Damage: {0}".format(self.parent.shields.damage))
        print("         Main Computer Damage: {0}".format(self.parent.computers.damage))
        print("Photon Torpedo Control Damage: {0}".format(self.parent.torpedoes.damage))
        print("                Phaser Damage: {0}".format(self.parent.phasers.damage))
        print()


class TorpedoControl(Actor):

    def __init__(self, parent):
        super().__init__()
        self.torpedoes = 10
        self.parent = parent
        self.name = "torpedo control"

    def act(self):
        if self.damage > 0:
            print_line("Photon torpedo control is damaged. Repairs are underway.", 0, 1)
            return
        if self.parent.torpedoes.torpedoes == 0:
            print_line("Photon torpedoes exhausted.", 0, 1)
            return
        if not self.parent.galaxy.current_quadrant_has_klingons():
            print_line("There are no Klingon ships in this quadrant.", 0, 1)
            return
        dirct = input_double("Enter firing direction (1.0--9.0): ")
        if not dirct or dirct < 1.0 or dirct > 9.0:
            print_line("Invalid direction.", 0, 1)
            return
        print_line("Photon torpedo fired...", 1, 0)
        self.torpedoes -= 1
        vx, vy = calculate_approx_vector(dirct)
        dx = vx / 20
        dy = vy / 20
        x = self.parent.sector_x
        y = self.parent.sector_y
        last_x = last_y = -1
        hit = False
        while x >= 0 and y >= 0 and round(x) < 8 and round(y) < 8:
            new_x = int(round(x))
            new_y = int(round(y))
            if last_x != new_x or last_y != new_y:
                print("  [{0},{1}]".format(new_x + 1, new_y + 1))
                last_x = new_x
                last_y = new_y
            for ship in self.parent.galaxy.current_quadrant_klingon_ships():
                if ship.sector_x == new_x and ship.sector_y == new_y:
                    print("Klingon ship destroyed at sector [{0},{1}].".format(ship.sector_x + 1, ship.sector_y + 1))
                    self.parent.galaxy.destroy_klingon(ship)
                    hit = True
                    break  # break out of the for loop
            if hit:
                break  # break out of the while loop
            if self.parent.galaxy.current_quadrant_sector_has_starbase(new_x, new_y):
                self.parent.galaxy.starbase_destroyed()
                print("The Enterprise destroyed a Federation starbase at sector [{0},{1}]!"
                      .format(new_x + 1, new_y + 1))
                hit = True
                break
            elif self.parent.galaxy.current_quadrant_sector_has_star(new_x, new_y):
                print("The torpedo was captured by a star's gravitational field at sector [{0},{1}].".format(
                    new_x + 1, new_y + 1
                ))
                hit = True
                break
            x += dx
            y += dy
        if not hit:
            print("Photon torpedo failed to hit anything.")
        if self.parent.galaxy.current_quadrant_has_klingons():
            print()
            self.parent.klingon_attack()
        print()


class PhaserControl(Actor):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.name = "phaser control"

    def act(self):
        if self.damage > 0:
            print_line("Phasers are damaged. Repairs are underway.", 0, 1)
            return
        galaxy = self.parent.galaxy
        if not galaxy.current_quadrant_has_klingons():
            print_line("There are no Klingon ships in this quadrant.", 0, 1)
            return
        print("Phasers locked on target.")
        phaser_energy = input_double("Enter phaser energy (1--{0}): ".format(self.parent.energy))
        if not phaser_energy or phaser_energy < 1 or phaser_energy > self.parent.energy:
            print_line("Invalid energy level.", 0, 1)
            return
        print_line("Firing phasers...", 1, 0)
        destroyed_ships = []
        for ship in galaxy.current_quadrant_klingon_ships():
            self.parent.energy -= int(phaser_energy)
            if self.parent.energy < 0:
                self.parent.energy = 0
                break
            dist = distance(self.parent.sector_x, self.parent.sector_y, ship.sector_x, ship.sector_y)
            delivered_energy = phaser_energy * (1.0 - dist / 11.3)
            ship.shield_level -= int(delivered_energy)
            if ship.shield_level <= 0:
                print("Klingon ship destroyed at sector [{0},{1}].".format(ship.sector_x + 1, ship.sector_y + 1))
                destroyed_ships.append(ship)
            else:
                print("Hit ship at sector [{0},{1}]. Klingon shield strength dropped to {2}.".format(
                    ship.sector_x + 1, ship.sector_y + 1, ship.shield_level
                ))
        for ship in destroyed_ships:
            galaxy.destroy_klingon(ship)
        if galaxy.current_quadrant_has_klingons():
            print()
            self.parent.klingon_attack()
        print()


class Enterprise:

    def __init__(self, galaxy):
        self.navigation = Navigation(self)
        self.shields = Shields(self)
        self.short_range_sensors = ShortRangeSensors(self)
        self.long_range_sensors = LongRangeSensors(self)
        self.computers = Computers(self)
        self.torpedoes = TorpedoControl(self)
        self.phasers = PhaserControl(self)

        # Global info
        self.star_date = 2250 + variability(50)
        self.time_remaining = 40 + variability(9)

        # initial location
        self.galaxy = galaxy
        self.quadrant_x, self.quadrant_y = location()
        self.sector_x, self.sector_y = location()
        self.galaxy.set_current_quadrant(self.quadrant_x, self.quadrant_y, self.sector_x, self.sector_y)

        # status
        self.docked = False
        self.destroyed = False
        self.energy = 3000

    def set_globals(self):
        self.star_date = 2250 + variability(50)
        self.time_remaining = 40 + variability(9)

    def set_location(self):
        self.quadrant_x, self.quadrant_y = location()
        self.sector_x, self.sector_y = location()
        self.galaxy.set_current_quadrant(self.quadrant_x, self.quadrant_y, self.sector_x, self.sector_y)

    def set_status(self):
        self.docked = False
        self.destroyed = False
        self.energy = 3000

    def restart(self):
        self.set_globals()
        self.set_location()
        self.set_status()

    def command_prompt(self):

        commands = {"nav": self.navigation, "srs": self.short_range_sensors, "lrs": self.long_range_sensors,
                    "pha": self.phasers, "tor": self.torpedoes, "she": self.shields,
                    "com": self.computers, "quit": exit, "exit": exit}

        command = input("Enter command: ").strip().lower()
        print()
        cmd = commands.get(command)
        if cmd == exit:
            exit()
        if cmd is not None:
            cmd.act()
        else:
            print_strings(strings.commandStrings)

    def repair_damage(self):
        if self.navigation.repair():
            return True
        if self.short_range_sensors.repair():
            return True
        if self.long_range_sensors.repair():
            return True
        if self.shields.repair():
            return True
        if self.computers.repair():
            return True
        if self.torpedoes.repair():
            return True
        if self.phasers.repair():
            return True
        return False

    def take_damage(self, item):
        if variability(6) > 0:
            return
        damage = 1 + variability(4)
        if item < 0:
            item = variability(6)
            match item:
                case 0:
                    self.navigation.take_damage(damage)
                case 1:
                    self.short_range_sensors.take_damage(damage)
                case 2:
                    self.long_range_sensors.take_damage(damage)
                case 3:
                    self.shields.take_damage(damage)
                case 4:
                    self.computers.take_damage(damage)
                case 5:
                    self.torpedoes.take_damage(damage)
                case 6:
                    self.phasers.take_damage(damage)
        print()

    def klingon_attack(self):
        galaxy = self.galaxy
        if galaxy.current_quadrant_has_klingons():
            for ship in galaxy.current_quadrant_klingon_ships():
                if self.docked:
                    print("Enterprise hit by ship at sector [{0},{1}]. No damage due to starbase shields.".format(
                        ship.sector_x + 1, ship.sector_y + 1
                    ))
                else:
                    dist = distance(
                        self.sector_x, self.sector_y, ship.sector_x, ship.sector_y)
                    delivered_energy = calculate_delivered_energy(dist)
                    self.shields.level -= int(delivered_energy)
                    if self.shields.level < 0:
                        self.shields.level = 0
                        self.destroyed = True
                    print("Enterprise hit by ship at sector [{0},{1}]. Shields dropped to {2}.".format(
                        ship.sector_x + 1, ship.sector_y + 1, self.shields.level
                    ))
                    if self.shields.level == 0:
                        return True
            return True
        return False

    def update_enterprise_quadrant(self, qx, qy, sx, sy):
        quadrant = self.galaxy.quadrants[qx][qy]
        self.galaxy.current_quadrant.set_current_quadrant(quadrant, sx, sy)

    def increment_date(self):
        self.time_remaining -= 1
        self.star_date += 1

    def display_mission(self):
        print_line("Mission: Destroy {0} Klingon ships in {1} stardates with {2} starbases.".format(
            self.galaxy.galaxy_klingon_count(), self.time_remaining, self.galaxy.galaxy_starbase_count()), 1)

    def display_status(self):
        if self.destroyed:
            print_line("MISSION FAILED: ENTERPRISE DESTROYED!!!", 0, 3)
        elif self.energy == 0:
            print_line("MISSION FAILED: ENTERPRISE RAN OUT OF ENERGY.", 0, 3)
        elif self.galaxy.galaxy_klingon_count() == 0:
            print_line("MISSION ACCOMPLISHED: ALL KLINGON SHIPS DESTROYED. WELL DONE!!!", 0, 3)
        elif self.time_remaining == 0:
            print_line("MISSION FAILED: ENTERPRISE RAN OUT OF TIME.", 0, 3)

    def quadrant(self):
        return self.galaxy.quadrants[self.quadrant_x][self.quadrant_y]
