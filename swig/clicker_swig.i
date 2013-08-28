/* -*- c++ -*- */

#define CLICKER_API

%include "gnuradio.i"			// the common stuff

//load generated python docstrings
%include "clicker_swig_doc.i"

%{
#include "clicker/sniffer.h"
%}

%include "clicker/sniffer.h"
GR_SWIG_BLOCK_MAGIC2(clicker, sniffer);
