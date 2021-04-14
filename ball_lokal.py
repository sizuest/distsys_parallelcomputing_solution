# MONTE CARLO SIMULATION EINES BALLWURFS, LOKAL
#
import argparse
import time
import numpy
from progressbar import print_progress

# Konstanten

g = 9.81  # Gravitationskonstante [m/s^2]
cw = 0.2  # Strömungswiderstandskoeffizient [-]
rho = 1.2  # Luftdichte [kg/m^3]
d = 0.068  # Balldurchmesser [m]
m = 0.057  # Ballmassen [kg]
dt = 0.1  # Schrittweite [s]


def trajectory(v_init, a_init, h_init, v_air):
    import random, math

    # Füge Unsicherheit hinzu
    v_init += (random.random() - .5) * 5.0
    a_init += (random.random() - .5) * 4.0
    h_init += (random.random() - .5) * 2.0
    v_air += (random.random() - .5) * 2.0
    rho_l = rho * (1 + (random.random() - .5) * 0.2)

    # Luftwiderstand (Wert und Richtung)
    def air_drag(v_x, v_y, v_air, rho_l):
        import math
        f_a = 0.5 * rho_l * (math.pow(v_x + v_air, 2) + math.pow(v_y, 2)) * math.pow(d, 2) * math.pi / 4
        a_a = math.atan2(v_y, v_x + v_air)
        return f_a, a_a

    # Initialisierung
    r_x = 0
    r_y = h_init
    v_x = v_init * math.cos(a_init * math.pi / 180.0)
    v_y = v_init * math.sin(a_init * math.pi / 180.0)

    # Indikator ob der Ball die Nulllinie von unten noch nicht geschnitten hat
    h_low = 0 > r_y

    # Euler-vorwärts-Integration
    # ... solange bis der Ball die Nullinie von oben schneidet
    while h_low or 0 < r_y:
        (f_a, b_a) = air_drag(v_x, v_y, v_air, rho_l)

        a_x = -f_a * math.cos(b_a)
        a_y = -m * g - f_a * math.sin(b_a)

        r_x += v_x * dt
        r_y += v_y * dt
        v_x += a_x * dt
        v_y += a_y * dt

        if h_low:
            h_low = 0 >= r_y

    return r_x


def count_distances(d):
    d = numpy.around(d)
    b = numpy.linspace(min(d), max(d), 15)
    hist = {}
    for i in d:
        idx = find_nearest(b, i)
        hist[idx] = hist.get(idx, 0) + 1
    return hist


def find_nearest(array, value):
    array = numpy.asarray(array)
    idx = (numpy.abs(array - value)).argmin()
    return array[idx]


def histogram(d) -> None:
    c = count_distances(d)
    dist_count = len(d)

    for k in sorted(c):
        print('\t{0:5.0f} m | {1}'.format(k, '+' * int(c[k] * 500 / dist_count)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("v_init", type=int, help="Initiale Geschwindigkeit [m/s]")
    parser.add_argument("a_init", type=int, help="Abwurfwinkel [°]")
    parser.add_argument("h_init", type=int, help="Abwurfhöhe [m]")
    parser.add_argument("v_air", type=int, help="Windgeschwindigkeit [m/s]")
    parser.add_argument("n_runs", type=int, help="Läufe [-]")

    args = parser.parse_args()

    v_init = args.v_init
    a_init = args.a_init
    h_init = args.h_init
    v_air = args.v_air
    n_runs = args.n_runs

    print(('Schätze die Wurfdistanz eines Balls (Total %s Läufe):' % n_runs))
    print('  Initiale Geschwindigkeit: %s m/s' % v_init)
    print('  Abwurfwinkel:             %s°' % a_init)
    print('  Abwurfhöhe:               %s m' % h_init)
    print('  Windgeschwindigkeit:      %s m/s' % v_air)
    total_inside = 0
    print_progress(0, 1, prefix='Fortschritt:', suffix='komplett', length=50)

    i = 0

    distance = list()

    start = time.time()
    while i < n_runs:
        i += 1

        # Berechne eine Zeile
        distance.append(trajectory(v_init, a_init, h_init, v_air))

        if i % 1000 == 0:
            print_progress(i, n_runs, prefix='Fortschritt:', suffix='komplett', length=50)

    end = time.time()

    # Berechnet die Schätzung für pi
    print(('Simulation der Wurfdistanz mit %s Läufen:' % n_runs))
    histogram(distance)
    print(('Mittelwert: %5.2f m' % (numpy.mean(distance))))
    print(('Laufzeit: %s s' % (end - start)))
