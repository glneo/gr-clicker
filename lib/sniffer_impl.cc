/* -*- c++ -*- */
/*
 * Copyright 2013 Andrew F. Davis
 * Copyright 2009 Jordan Riggs
 * Copyright 2005, 2006 Free Software Foundation, Inc.
 * 
 * This file is part of gr-clicker
 * 
 * gr-clicker is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 * 
 * gr-clicker is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with gr-clicker; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "sniffer_impl.h"

#include <stdio.h>

namespace gr
{
	namespace clicker
	{

		sniffer::sptr sniffer::make()
		{
			return gnuradio::get_initial_sptr(new sniffer_impl());
 		}

		/*
		* The private constructor
		*/
		sniffer_impl::sniffer_impl() : gr::sync_block("sniffer",
			gr::io_signature::make(1, 1, sizeof(char)),
			gr::io_signature::make(0, 0, 0))
    		{
			set_history(43);
		}

		int sniffer_impl::work(int noutput_items,
		                       gr_vector_const_void_star &input_items,
		                       gr_vector_void_star &output_items)
		{
			char* in = (char*) input_items[0];

			if (in[0] & (char)0x02)
			{
				d_id = 0;
				char code = (in[31]<<3) + (in[32]<<2) + (in[33]<<1) + (in[34]);
				switch (code)
				{
					case 0x01: d_response_code = 'A'; break;
					case 0x05: d_response_code = 'B'; break;
					case 0x0D: d_response_code = 'C'; break;
					case 0x0E: d_response_code = 'D'; break;
					case 0x0A: d_response_code = 'E'; break;
				}
				for (int i = 0; i < 31; i++)
				{
					d_id += (in[i]<<(30-i));
				}
	
				printf("Clicker Packet: ID: %08x Response: %c\n", d_id, d_response_code);

				return 43;
			}
			return 1;
		}

	} /* namespace clicker */
} /* namespace gr */

