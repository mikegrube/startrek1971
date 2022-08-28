from util import variability
from enum import Enum


class SectorType(Enum):

    EMPTY = 0
    STAR = 1
    KLINGON = 2
    ENTERPRISE = 3
    STARBASE = 4


class KlingonShip:

    def __init__(self):
        self.sector_x = 0
        self.sector_y = 0
        self.shield_level = 0


class CurrentQuadrant:

    sector = [[SectorType.EMPTY for _ in range(8)] for _ in range(8)]
    klingon_ships = []
    starbase_x, starbase_y = 0, 0

    def __init__(self, parent, qx, qy):
        super().__init__()
        self.parent = parent
        self.quadrant_x = qx
        self.quadrant_y = qy

    def is_docking_location(self, x, y):
        xs = x - 1 if x > 0 else 0
        xe = x + 1 if x < 7 else 7
        ys = y - 1 if y > 0 else 0
        ye = y + 1 if y < 7 else 7

        for i in range(xs, xe + 1):   # inclusion
            for j in range(ys, ye + 1):   # inclusion
                if self.sector[i][j] == SectorType.STARBASE:
                    return True
        return False

    def sector_region_is_empty(self, x, y):
        xs = x - 1 if x > 0 else 0
        xe = x + 1 if x < 7 else 7
        ys = y - 1 if y > 0 else 0
        ye = y + 1 if y < 7 else 7

        for i in range(xs, xe + 1):   # inclusion
            for j in range(ys, ye + 1):   # inclusion
                if self.sector[i][j] != SectorType.EMPTY:
                    return False
        return True

    def quadrant_has_klingons(self):
        return len(self.klingon_ships) > 0

    def quadrant_klingon_ships(self):
        return self.klingon_ships

    def sector_is_empty(self, x, y):
        return self.sector[x][y] == SectorType.EMPTY

    def sector_has_starbase(self, x, y):
        return self.sector[x][y] == SectorType.STARBASE

    def sector_has_star(self, x, y):
        return self.sector[x][y] == SectorType.STAR

    def sector_has_kingon(self, x, y):
        return self.sector[x][y] == SectorType.KLINGON

    def fill_sector(self, x, y, stype):
        self.sector[x][y] = stype

    def starbase_loc(self):
        for i in range(8):
            for j in range(8):
                if self.sector[i][j] == SectorType.STARBASE:
                    return i, j
        return -1, -1  # shouldn't happen

    def destroy_klingon(self, ship):
        self.sector[ship.sector_x][ship.sector_y] = SectorType.EMPTY
        self.klingon_ships.remove(ship)
        self.parent.quadrants[self.quadrant_x][self.quadrant_y].klingons -= 1

    def destroy_starbase(self):
        self.sector[self.starbase_x][self.starbase_y] = SectorType.EMPTY
        self.quadrant().starbase = False

    def quadrant_location(self):
        return self.quadrant_x, self.quadrant_y

    def sector_at(self, x, y):
        return self.sector[x][y]

    def clear(self):
        for i in range(8):
            for j in range(8):
                self.sector[i][j] = SectorType.EMPTY
        self.klingon_ships = []

    def set_enterprise_sector(self, sx, sy):
        self.sector[sx][sy] = SectorType.ENTERPRISE

    def set_star_sector(self, sx, sy):
        self.sector[sx][sy] = SectorType.STAR

    def set_starbase_sector(self, sx, sy):
        self.sector[sx][sy] = SectorType.STARBASE

    def set_klingon_sector(self, sx, sy):
        self.sector[sx][sy] = SectorType.KLINGON
        klingon_ship = KlingonShip()
        klingon_ship.shield_level = 300 + variability(199)
        klingon_ship.sector_x = sx
        klingon_ship.sector_y = sy
        self.klingon_ships.append(klingon_ship)

    def clear_sector(self, x, y):
        self.sector[x][y] = SectorType.EMPTY

    def status(self):
        status = [["   " for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                s = "   "
                match self.sector[i][j]:
                    case SectorType.EMPTY:
                        s = "   "
                    case SectorType.ENTERPRISE:
                        s = "<E>"
                    case SectorType.KLINGON:
                        s = "+K+"
                    case SectorType.STAR:
                        s = " * "
                    case SectorType.STARBASE:
                        s = ">S<"
                status[i][j] = s
        return status

    def quadrant(self):
        return self.parent.quadrants[self.quadrant_x][self.quadrant_y]
