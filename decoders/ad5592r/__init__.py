##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2024 Analog Devices Inc.
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

'''
    The Analog Devices AD5592R is a 12-bit ADC/DAC with 8 channels that
    operates over an SPI interface.
    
    This decoder stacks on top of the 'spi' PD and decodes the AD5592R operations.
    
    Please note that the SPI interface uses clock polarity 1 and 
    clock phase 1 which are not the default settings
    
    Details:
    https://www.analog.com/media/en/technical-documentation/data-sheets/ad5592r.pdf
'''

from .pd import Decoder