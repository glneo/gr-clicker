#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2013 Andrew F. Davis
# Copyright 2009 Jordan Riggs

from gnuradio import gr, eng_notation, uhd, analog, digital, blocks

from clicker import *
from gnuradio.eng_option import eng_option
from optparse import OptionParser

AC = "101100001011000010110000"

class gr_clicker_block(gr.top_block):

	def __init__(self, options, filename):
		gr.top_block.__init__(self)

		inf_str = None
		symbol_rate = 152.34e3
		sample_rate = 1e6
		
		#if len(options) != 0:
		#	inf_str = args[0]

		squelch = analog.pwr_squelch_cc(float(options.squelch), 0.1, 0, True)
		demod = analog.quadrature_demod_cf(1.0)
		cr = digital.clock_recovery_mm_ff(sample_rate/symbol_rate, 0.00765625, 0, 0.175, 0.005)
		slicer = digital.binary_slicer_fb()
		corr = digital.correlate_access_code_bb(AC, 3)
		sink = sniffer()

		if False:
			print "Reading from: " + inf_str
			src = blocks.file_source(gr.sizeof_gr_complex, inf_str, False)
		
		else:
			freqs = {
				'AA':917.0e6, 'AB':913.0e6, 'AC':914.0e6, 'AD':915.0e6,
				'BA':916.0e6, 'BB':919.0e6, 'BC':920.0e6, 'BD':921.0e6,
				'CA':922.0e6, 'CB':923.0e6, 'CC':907.0e6, 'CD':908.0e6,
				'DA':905.5e6, 'DB':909.0e6, 'DC':911.0e6, 'DD':910.0e6}

			frequency = freqs[options.channel]
			print "Channel: " + options.channel + " (" + str(frequency/1e6) + "MHz)"

			# Create a UHD device source
			src = uhd.usrp_source(device_addr=options.args, stream_args=uhd.stream_args('fc32', "sc16", args=""))

			# Set the subdevice spec
			if(options.spec):
				src.set_subdev_spec(options.spec, 0)

			# Set the antenna
			if(options.antenna):
				src.set_antenna(options.antenna, 0)

			# Set receiver sample rate
			src.set_samp_rate(options.samp_rate)

			# Set receive daughterboard gain
			if options.gain is None:
				g = src.get_gain_range()
				options.gain = float(g.start()+g.stop())/2
				print "Using mid-point gain of", options.gain, "(", g.start(), "-", g.stop(), ")"
				src.set_gain(options.gain)

			# Set frequency (tune request takes lo_offset)
			treq = uhd.tune_request(frequency)
			tr = src.set_center_freq(treq)
			if tr == None:
				sys.stderr.write('Failed to set center frequency\n')
				raise SystemExit, 1

		self.connect(src, squelch, demod, cr, slicer, corr, sink)

def get_options():
	usage="%prog: [options] [input file]"
	parser = OptionParser(option_class=eng_option, usage=usage)
	parser.add_option("-a", "--args", type="string", default="",
	                    help="UHD device address args , [default=%default]")
	parser.add_option("", "--spec", type="string", default=None,
	                    help="Subdevice of UHD device where appropriate")
	parser.add_option("-A", "--antenna", type="string", default=None,
	                    help="select Rx Antenna where appropriate")
	parser.add_option("", "--samp-rate", type="eng_float", default=1e6,
	                    help="set sample rate (bandwidth) [default=%default]")
	parser.add_option("-g", "--gain", type="eng_float", default=None,
	                    help="set gain in dB (default is midpoint)")
	parser.add_option("", "--lo-offset", type="eng_float", default=None,
	                    help="set daughterboard LO offset to OFFSET [default=hw default]")
	parser.add_option("", "--stream-args", type="string", default="",
	                    help="set stream arguments [default=%default]")
	parser.add_option("", "--show-async-msg", action="store_true", default=False,
	                    help="Show asynchronous message notifications from UHD [default=%default]")
	parser.add_option("-c", "--channel", type="string", default='AA',
	                    help="two-letter channel code (default: AA)")
	parser.add_option("-t", "--transmit", action="store_true", default=False,
	                    help="automatically determine and transmit reponse")
	parser.add_option("-R", "--rx-subdev-spec", type="subdev", default=(0, 0),
	                   help="select USRP Rx side A or B (default=A)")
	parser.add_option("-s", "--squelch", type="eng_float", default=20,
	                   help="set squelch in dB")

	(options, args) = parser.parse_args ()
	if len(args) != 1:
		parser.print_help()
		raise SystemExit, 1

	return (options, args[0])

if __name__ == '__main__':
	(options, filename) = get_options()
	tb = gr_clicker_block(options, filename)

	try:
		tb.run()
	except KeyboardInterrupt:
		pass

