from util import variability, location
from strings import quadrantNames
from currentquadrant import CurrentQuadrant


# Quadrants of the galaxy
class Quadrant:

    def __init__(self, qx, qy):
        self.name = ""
        self.klingons = 0
        self.stars = 0
        self.starbase = False
        self.scanned = False
        self.loc_x = qx
        self.loc_y = qy



    def quadrant_location(self):
        return self.loc_x, self.loc_y


# All quadrants
class Galaxy:

    quadrants = [[Quadrant(0, 0) for _ in range(8)] for _ in range(8)]

    def __init__(self):

        self.build_quadrants()

        self.place_elements()

        self.current_quadrant = CurrentQuadrant(self, 0, 0)

    def restart(self):

        self.build_quadrants()

        self.place_elements()

    def build_quadrants(self):
        names = quadrantNames.copy()
        for i in range(8):
            for j in range(8):
                quadrant = Quadrant(i, j)
                index = variability(len(names) - 1)
                quadrant.name = names[index]
                del names[index]
                quadrant.stars = 1 + variability(7)
                self.quadrants[i][j] = quadrant

    def place_elements(self):
        klingon_count = 15 + variability(5)
        starbase_count = 2 + variability(2)
        while klingon_count > 0 or starbase_count > 0:
            i, j = location()
            quadrant = self.quadrants[i][j]
            if starbase_count > 0 and not quadrant.starbase:
                quadrant.starbase = True
                starbase_count -= 1
            if quadrant.klingons < 3:
                quadrant.klingons += 1
                klingon_count -= 1

    def set_current_quadrant(self, qx, qy, sx, sy):
        quadrant = self.quadrants[qx][qy]
        starbase = quadrant.starbase
        stars = quadrant.stars
        klingons = quadrant.klingons
        self.current_quadrant.clear()
        self.current_quadrant.quadrant_x = qx
        self.current_quadrant.quadrant_y = qy
        self.current_quadrant.set_enterprise_sector(sx, sy)
        while starbase or stars > 0 or klingons > 0:
            i, j = location()
            if self.current_quadrant.sector_region_is_empty(i, j):
                if starbase:
                    self.current_quadrant.set_starbase_sector(i, j)
                    starbase = False
                elif stars > 0:
                    self.current_quadrant.set_star_sector(i, j)
                    stars -= 1
                elif klingons > 0:
                    self.current_quadrant.set_klingon_sector(i, j)
                    klingons -= 1

    # current quadrant klingons

    def galaxy_klingon_count(self):
        count = 0
        for i in range(8):
            for j in range(8):
                count += self.quadrants[i][j].klingons
        return count

    def quadrant_klingon_count(self, qx, qy):
        return self.quadrants[qx][qy].klingons

    def quadrant_has_klingons(self, x, y):
        return self.quadrants[x][y].klingons > 0

    def current_quadrant_klingon_count(self):
        return self.quadrant_klingon_count(self.current_quadrant.quadrant_x, self.current_quadrant.quadrant_y)

    def current_quadrant_has_klingons(self):
        return self.current_quadrant.quadrant_has_klingons()

    def current_quadrant_klingon_ships(self):
        return self.current_quadrant.klingon_ships

    def destroy_klingon(self, ship):
        self.current_quadrant.destroy_klingon(ship)

    # current quadrant starbase

    def galaxy_starbase_count(self):
        count = 0
        for i in range(8):
            for j in range(8):
                if self.quadrants[i][j].starbase:
                    count += 1
        return count

    def quadrant_has_starbase(self, x, y):
        return self.quadrants[x][y].starbase

    def current_quadrant_has_starbase(self):
        return self.quadrants[self.current_quadrant.quadrant_x][self.current_quadrant.quadrant_y].starbase

    def current_quadrant_sector_has_starbase(self, sx, sy):
        return self.current_quadrant.sector_has_starbase(sx, sy)

    def starbase_destroyed(self):
        self.current_quadrant.destroy_starbase()

    # current quadrant stars

    def current_quadrant_sector_has_star(self, sx, sy):
        return self.current_quadrant.sector_has_star(sx, sy)

    # current quadrant general

    def clear_current_quadrant_sector(self, sx, sy):
        self.current_quadrant.clear_sector(sx, sy)

    def sector_is_empty(self, sx, sy):
        return self.current_quadrant.sector_is_empty(sx, sy)

    def set_enterprise_sector(self, sx, sy):
        self.current_quadrant.set_enterprise_sector(sx, sy)

    def is_docking_location(self, sx, sy):
        return self.current_quadrant.is_docking_location(sx, sy)

    # records

    def quadrant_scanned(self, x, y):
        self.quadrants[x][y].scanned = True

    def galactic_record(self):
        status = [["    " for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                quadrant = self.quadrants[i][j]
                adj = "*" if i == self.current_quadrant.quadrant_x and j == self.current_quadrant.quadrant_y else " "
                if quadrant.scanned:
                    status[i][j] = "{0}{1}{2}{3}".format(quadrant.klingons, 1 if quadrant.starbase else 0, quadrant.stars, adj)
        return status

    def print_quadrant_neighborhood(self, x, y):
        sb = ""
        print("Long range scan for quadrant {0}-{1}:".format(x + 1, y + 1))
        print("-------------------")
        for j in range(y - 1, y + 2):   # inclusive
            for i in range(x - 1, x + 2):   # inclusive
                sb += "| "
                if 0 <= i < 8 and 0 <= j < 8:
                    quadrant = self.quadrants[i][j]
                    quadrant.scanned = True
                    sb = sb + "{0}{1}{2} ".format(quadrant.klingons, 1 if quadrant.starbase else 0, quadrant.stars)
                else:
                    sb = sb + "    "
            sb += "| "
            print(sb)
            sb = ""
            print("-------------------")
        print()
