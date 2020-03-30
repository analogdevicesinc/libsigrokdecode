##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2020 Analog Devices Inc.
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##


import sigrokdecode as srd


class Decoder(srd.Decoder):
    api_version = 3
    id = 'ad5626'
    name = 'AD5626'
    longname = 'AD5626'
    desc = 'AD5626 12-bit nanoDAC'
    license = 'gplv2+'
    inputs = ['spi']
    outputs = []
    tags = ['Display']
    annotations = (
        ('data', 'Data'),
    )
    annotation_rows = (
        ('data', 'Data', (0,)),
    )

    def __init__(self,):
        self.reset()

    def reset(self):
        self.data = 0
        self.start_sample = 0

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def put_data(self, pos, data):
        self.put(pos[0], pos[1], self.out_ann, [0, [str(data) + 'V']])


    def decode(self, ss, es, data):
        ptype = data[0]

        if ptype == 'CS-CHANGE':
            cs_old, cs_new = data[1:]
            if cs_old is not None and cs_old == 0 and cs_new == 1:
                self.data >>= 1
                self.data /= 1000
                self.put_data([self.start_sample, es], self.data)

                self.data = 0
            elif cs_old is not None and cs_old == 1 and cs_new == 0:
                self.start_sample = ss

        elif ptype == 'BITS':
            mosi = data[1]

            for bit in reversed(mosi):
                self.data = self.data | bit[0]

                self.data <<= 1
