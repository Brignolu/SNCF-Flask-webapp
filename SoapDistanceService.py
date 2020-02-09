from ladon.ladonizer import ladonize
import math


class Distance(object):
    @ladonize(float, float, float, float, rtype=float)
    def calcul_distance(self, latA, latB, longA, longB):
        latA = math.radians(latA)
        latB = math.radians(latB)
        longA = math.radians(longA)
        longB = math.radians(longB)
        delta = longB - longA
        sinlatA = math.sin(latA)
        sinlatB = math.sin(latB)
        coslatA = math.cos(latA)
        coslatB = math.cos(latB)
        cosdelta = math.cos(delta)
        rayonTerre = 6378137
        return rayonTerre * math.acos(sinlatA * sinlatB + coslatA * coslatB * cosdelta)
