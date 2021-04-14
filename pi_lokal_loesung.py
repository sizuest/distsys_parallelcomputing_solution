# BERECHNUNG VON PI MITTELS CLUSTER
#
# Adaptiert von raspberrypilearning/octapi-setup

import argparse
import decimal
import time

import numpy

from progressbar import print_progress


# 'compute' berechnet für eine Zeile die Anzahl Punkte innerhalb des Einheitskreises
def compute(y, n_x):
    inside = 0

    # für alle x-koordinaten in der Zeile:
    for x in numpy.linspace(0, 1, n_x):
        # Berechne den Radius
        r = x * x + y * y
        # Ermittle, ob der Punkt im Einheitskreis liegt
        if r <= 1.0:
            inside = inside + 1

    return inside


# main
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("no_of_lines", type=int, help="Anzahl Zeilen / Spalten im Quadranten")
    args = parser.parse_args()

    no_of_lines = args.no_of_lines

    print(('Schätze pi mit %s Zeilen / Spalten im 1. Quadranten (Total %s Punkte)' % (
        no_of_lines, no_of_lines * 100000)))
    total_inside = 0
    print_progress(0, no_of_lines, prefix='Fortschritt:', suffix='komplett', length=50)

    y = numpy.linspace(0, 1, no_of_lines)
    i = 0

    start = time.time()
    while i < no_of_lines:
        i += 1

        # Berechne eine Zeile
        inside = compute(y[i - 1], 100000)
        # Summiere Ergebniss
        total_inside += inside

        if i % 10 == 0:
            print_progress(i, no_of_lines, prefix='Fortschritt:', suffix='komplett', length=50)

    end = time.time()

    # Berechnet die Schätzung für pi
    total_no_of_points = no_of_lines * 100000
    decimal.getcontext().prec = 100  # override standard precision
    Pi = decimal.Decimal(4 * total_inside / total_no_of_points)
    print(('Schätzung für Pi mit %s Zeilen / Spalten: %s' % (total_no_of_points, +Pi)))
    print(('Laufzeit: %s s' % (end - start)))
