import json
import os
import glob
import sys
import time
import serial
import logging
import random
import math
import datetime
import copy

from pyhaptic import HapticInterface
from test_pyhaptic import find_comm_port


def log_data(*args):
	strings = [str(a) for a in args]
	puts = "".join(strings)
	print(puts)
	#with open('logs.txt', 'a+') as logfile:
	#	logfile.write(puts)


def fix_vibrations(vibrations):
	vibs = []
	vibrations = sorted(vibrations, key=lambda x: x['beat'])
	for v in vibrations:
		motors = v['motors']
		while v['beat'] >= len(vibs):
			vibs.append([])
		randoms = []
		for m in motors:
			if m < 0:
				if m == -100:
					n = random.randint(0, 47)
					while n in randoms:
						n = random.randint(0, 47)
					motors.remove(m)
					motors.append(n)
					randoms.append(n)
				else:
					x = (math.fabs(m) - 1) * 8
					n = random.randint(x, x + 7)
					while n in randoms:
						n = random.randint(x, x + 7)
					motors.remove(m)
					motors.append(n)
					randoms.append(n)

		vibs[v['beat']].extend(motors)

	return vibs

def create_pattern(interface, pattern, duration, saltation=False):
	pulse = float(duration['pulse']) / 1000.0
	gap = float(duration['gap']) / 1000.0
	vibrations = fix_vibrations(pattern['vibrations'])

	def exec_pattern():
		log_data("\nRunning Pattern: ", pattern["name"])
		log_data("\nGap: ", gap)
		log_data("\nPulse: ", pulse)
		log_data("\nTime: ", datetime.datetime.now())
		if saltation:
			log_data("\nSaltation Enabled")
		else:
			log_data("\nSaltation Disabled")
		log_data("\n")

		time.sleep(gap)

		for v in vibrations:
			for m in v:
				interface.vibrate(m, 3, 0, 7)

			time.sleep(pulse)

			for m in v:
				interface.vibrate(m, 3, 0, 0)

			time.sleep(gap)

		return pattern['name'] + " -- " + str(pulse) + ":" + str(gap)

	return exec_pattern


def main():
	data = json.loads(open('patterns.json').read())
	durations = data['durations']
	patterns = data['patterns']

	pattern_list = []

	interface = None
	port = find_comm_port()
	print(port)
	interface = HapticInterface(port)
	try:
		interface.connect()
	except:
		print("Failed to connect on ...")
		#sys.exit(1)

	print("Connected to chair.")

	for p in patterns:
		for d in durations:
			x = create_pattern(interface, p, d)
			x.p_name = p["name"]
			x.p_image = p.get('image')
			pattern_list.append(x)

	print("Generated patterns.")

	# random.shuffle(pattern_list)

	print("Randomized patterns.")

	"""
	log_data("Starting Experiment.\n\n")
	for fn in pattern_list:
		fn()
		time.sleep(5.0)
		i = raw_input("\nNext pattern?\n")
		if i in ['q', 'Q', 'n', 'N', 'x', 'X']:
			break

	log_data("\n\nCompleted Experiment!")
	"""

	return pattern_list, interface, data
