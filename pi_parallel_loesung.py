# BERECHNUNG VON PI MITTELS CLUSTER
#
# Adaptiert von raspberrypilearning/octapi-setup

import time
import argparse
import decimal
import dispy
import logging
import numpy
import socket
import threading

from progressbar import print_progress


def compute(y, n_x):
    import numpy
    inside = 0

    # für alle x-koordinaten in der Zeile:
    for x in numpy.linspace(0, 1, n_x):
        # Berechne den Radius
        r = x * x + y * y
        # Ermittle, ob der Punkt im Einheitskreis liegt
        if r <= 1.0:
            inside = inside + 1

    return inside


def job_callback(job):  # executed at the client
    global pending_jobs, jobs_cond, no_of_jobs, no_of_jobs_finished
    global total_inside

    if (job.status == dispy.DispyJob.Finished  # most usual case
            or job.status in (dispy.DispyJob.Terminated, dispy.DispyJob.Cancelled,
                              dispy.DispyJob.Abandoned)):
        # 'pending_jobs' is shared between two threads, so access it with
        # 'jobs_cond' (see below)
        jobs_cond.acquire()
        no_of_jobs_finished = no_of_jobs_finished + 1
        if job.id:  # job may have finished before 'main' assigned id
            pending_jobs.pop(job.id)

            if no_of_jobs_finished % 1 == 0:
                print_progress(no_of_jobs_finished, no_of_jobs, prefix='Fortschritt:', suffix='komplett', length=50)

            # extract the results for each job as it happens
            inside = job.result
            total_inside += inside
            
        if len(pending_jobs) <= lower_bound:
            jobs_cond.notify()

        jobs_cond.release()


# main
if __name__ == '__main__':

    # set lower and upper bounds as appropriate
    # lower_bound is at least num of cpus and upper_bound is roughly 3x lower_bound
    lower_bound, upper_bound = 13*4, 3*13*4

    parser = argparse.ArgumentParser()
    parser.add_argument("no_of_lines", type=int, help="Anzahl Zeilen / Spalten im Quadranten")
    args = parser.parse_args()

    no_of_lines = args.no_of_lines
    no_of_jobs = no_of_lines

    server_nodes = ["octapi-s2.simple.eee.intern", 
                    "octapi-s3.simple.eee.intern", 
                    "octapi-s4.simple.eee.intern", 
                    "octapi-s5.simple.eee.intern", 
                    "octapi-s6.simple.eee.intern", 
                    "octapi-s7.simple.eee.intern", 
                    "octapi-s8.simple.eee.intern", 
                    "octapi-s9.simple.eee.intern", 
                    "octapi-s10.simple.eee.intern", 
                    "octapi-s11.simple.eee.intern", 
                    "octapi-s12.simple.eee.intern", 
                    "octapi-s13.simple.eee.intern", 
                    "octapi-s14.simple.eee.intern", 
                    "octapi-s15.simple.eee.intern", 
                    "octapi-s16.simple.eee.intern"]
    master_node = 'octapi-s16.simple.eee.intern'

    # use Condition variable to protect access to pending_jobs, as
    # 'job_callback' is executed in another thread
    jobs_cond = threading.Condition()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))  # doesn't matter if 8.8.8.8 can't be reached
    cluster = dispy.SharedJobCluster(compute, nodes=server_nodes, callback=job_callback, host=s.getsockname()[0],
                                     loglevel=logging.INFO, scheduler_host=master_node, exclusive=False)

    pending_jobs = {}
    no_of_jobs_finished = 0

    print(('Schätze pi mit %s Zeilen / Spalten im 1. Quadranten (Total %s Punkte)' % (
        no_of_lines, no_of_lines * 100000)))

    total_inside = 0
    i = 0
    y = numpy.linspace(0, 1, no_of_lines)

    start = time.time()
    while i < no_of_jobs and i<100000000 and (time.time()-start)<=60:
                    
        i += 1

        # schedule execution of 'compute' on a node (running 'dispynode')
        job = cluster.submit(y[i - 1], 100000)
        
        if job is None:
            continue

        jobs_cond.acquire()

        job.id = i  # associate an ID to the job

        # there is a chance the job may have finished and job_callback called by
        # this time, so put it in 'pending_jobs' only if job is pending
        if job.status == dispy.DispyJob.Created or job.status == dispy.DispyJob.Running:
            pending_jobs[i] = job
            
            if len(pending_jobs) >= upper_bound:
                while len(pending_jobs) > lower_bound:
                    jobs_cond.wait()

        jobs_cond.release()

    cluster.wait(timeout=30)

    end = time.time()

    time.sleep(1)

    # Berechnet die Schätzung für pi
    total_no_of_points = no_of_jobs_finished * 100000
    decimal.getcontext().prec = 100  # override standard precision
    Pi = decimal.Decimal(4 * total_inside / total_no_of_points)
    print(('Schätzung für Pi mit %s Zeilen / Spalten: %s' % (no_of_lines, +Pi)))
    print(('Laufzeit: %s s' % (end - start)))

    cluster.print_status()
    cluster.close(timeout=15, terminate=True)
