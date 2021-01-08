#!/bin/bash

# SGE Options
#$ -S /bin/bash
# Shell environment forwarding
#$ -V
# Job Name
#$ -N test_stommel
# Notifications
#$ -M c.m.pierard@uu.nl
# When notified (b : begin, e : end, s : error)
#$ -m es
# Set memory limit (important when you a lot of field- or particle data(
#  Guideline: try with 20G - if you get a mail with subject "Job <some_number_here> (<EXPERIMENT_NAME>) Aborted",
#  then check the output line "Max vmem". If that is bigger that what you typed in here, your experiment ran
#  out of memory. In that case, raise this number a bit.
#  (1) 'h_vmem' cannot be >256G (hard limit); (2) Do not start with with 200G or more - remember that you
#  share this computer with your next-door-neighbour and colleague.
#$ -l h_vmem=20G
# Set runtime limit
#$ -l h_rt=24:00:00
# run the job on the queue for long-running processes: $ -q long.q

echo 'Running Stommel example ...'
cd ${HOME}/parcels/parcels/examples
python3 example_stommel.py
echo 'Finished computation.'
