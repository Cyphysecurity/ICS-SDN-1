from minicps.devices import PLC
from utils import *
import random
import time
import logging
import signal
import sys

SENSOR_ADDR = IP['lit101']

LIT101 = ('LIT101', 1)

class Lit101(PLC):
	def sigint_handler(self, sig, frame):
		print "I received a SIGINT!"
		global reader
		reader = 0
		sys.exit(0)

	def pre_loop(self, sleep=0.1):
		signal.signal(signal.SIGINT, self.sigint_handler)
		signal.signal(signal.SIGTERM, self.sigint_handler)

	def main_loop(self):
		#print 'DEBUG: sensor enters main_loop'
		logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO, filename='defense_replay_attack_5/replay_lit101.log')
		count = 0
		gaussian_noise_experiment = 1
		noise_level = 0.03
		attack_lower_limit = 50
		random_duration = random.randint(5,20)
		#random_duration = 10
		attack_upper_limit = attack_lower_limit + random_duration
		attack_upper_window = attack_lower_limit + 60
		attack_active = 0

		while True:

			if count>=attack_lower_limit and count<=attack_upper_limit:
				if count == attack_lower_limit:
					self.level = float(self.get(LIT101))
				attack_active = 1
			else:
				attack_active = 0

			if attack_active==0:
				self.level = float(self.get(LIT101))
				if gaussian_noise_experiment == 1:
					self.level = self.level + random.gauss(0, noise_level)
					if self.level > 1.0:
						self.level = 1.0
					if self.level < 0:
						self.level = 0.0
				self.send(LIT101, self.level, SENSOR_ADDR)
				logging.info('LIT101: %f', self.level)
				logging.info('NORMAL')
				time.sleep(PLC_PERIOD_SEC)
			else:
				self.send(LIT101, self.level, SENSOR_ADDR)
				logging.info('LIT101: %f', self.level)
				logging.info('ATTACK')
				time.sleep(PLC_PERIOD_SEC)

			if (count >= attack_upper_window):
				attack_lower_limit = attack_upper_window
				random_duration = random.randint(5,20)
				attack_upper_limit = attack_lower_limit + random_duration
				attack_upper_window = attack_lower_limit + 60
			count = count+1

if __name__ == '__main__':
	lit101 = Lit101(name='lit101',state=STATE,protocol=LIT101_PROTOCOL,memory=GENERIC_DATA,disk=GENERIC_DATA)

