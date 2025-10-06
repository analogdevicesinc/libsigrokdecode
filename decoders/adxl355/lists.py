##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2024 Your Name <your.email@example.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
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

# Register names dictionary
register_names = {
    0x00: ['DEVID_AD', 'DEV_AD'],
    0x01: ['DEVID_MST', 'DEV_MST'],
    0x02: ['PARTID', 'PART'],
    0x03: ['REVID', 'REV'],
    0x04: ['STATUS', 'STAT'],
    0x05: ['FIFO_ENTRIES', 'FIFO_E'],
    0x06: ['TEMP2', 'T2'],
    0x07: ['TEMP1', 'T1'],
    0x08: ['XDATA3', 'X3'],
    0x09: ['XDATA2', 'X2'],
    0x0A: ['XDATA1', 'X1'],
    0x0B: ['YDATA3', 'Y3'],
    0x0C: ['YDATA2', 'Y2'],
    0x0D: ['YDATA1', 'Y1'],
    0x0E: ['ZDATA3', 'Z3'],
    0x0F: ['ZDATA2', 'Z2'],
    0x10: ['ZDATA1', 'Z1'],
    0x11: ['FIFO_DATA', 'FIFO'],
    0x1E: ['OFFSET_X_H', 'OX_H'],
    0x1F: ['OFFSET_X_L', 'OX_L'],
    0x20: ['OFFSET_Y_H', 'OY_H'],
    0x21: ['OFFSET_Y_L', 'OY_L'],
    0x22: ['OFFSET_Z_H', 'OZ_H'],
    0x23: ['OFFSET_Z_L', 'OZ_L'],
    0x24: ['ACT_EN', 'ACT_E'],
    0x25: ['ACT_THRESH_H', 'ATH_H'],
    0x26: ['ACT_THRESH_L', 'ATH_L'],
    0x27: ['ACT_COUNT', 'ACT_C'],
    0x28: ['FILTER', 'FILT'],
    0x29: ['FIFO_SAMPLES', 'FIFO_S'],
    0x2A: ['INT_MAP', 'INT_M'],
    0x2B: ['SYNC', 'SYNC'],
    0x2C: ['RANGE', 'RNG'],
    0x2D: ['POWER_CTL', 'PWR'],
    0x2E: ['SELF_TEST', 'ST'],
    0x2F: ['RESET', 'RST'],
}

# Status register bits
STATUS_NVM_BUSY = (1 << 4)
STATUS_ACTIVITY = (1 << 3)
STATUS_FIFO_OVR = (1 << 2)
STATUS_FIFO_FULL = (1 << 1)
STATUS_DATA_RDY = (1 << 0)

# Power control register bits
POWER_CTL_STANDBY = 0x01
POWER_CTL_MEASUREMENT = 0x00
POWER_CTL_TEMP_OFF = (1 << 1)
POWER_CTL_DRDY_OFF = (1 << 2)

# Range register values
RANGE_2G = 0x01
RANGE_4G = 0x02
RANGE_8G = 0x03

# Filter register - High pass filter corner frequency
FILTER_HPF_CORNER = {
    0x00: 'No high pass filter',
    0x10: '247 × 10^−3 Hz',
    0x20: '62.084 × 10^−3 Hz',
    0x30: '15.545 × 10^−3 Hz',
    0x40: '3.862 × 10^−3 Hz',
    0x50: '0.954 × 10^−3 Hz',
    0x60: '0.238 × 10^−3 Hz',
}

# Filter register - Output data rate
FILTER_ODR = {
    0x00: '4000 Hz',
    0x01: '2000 Hz',
    0x02: '1000 Hz',
    0x03: '500 Hz',
    0x04: '250 Hz',
    0x05: '125 Hz',
    0x06: '62.5 Hz',
    0x07: '31.25 Hz',
    0x08: '15.625 Hz',
    0x09: '7.813 Hz',
    0x0A: '3.906 Hz',
}

# Scale factors for different ranges (LSB/g)
SCALE_FACTOR_2G = 256000.0
SCALE_FACTOR_4G = 128000.0
SCALE_FACTOR_8G = 64000.0

# Temperature calibration constants (from ADXL355 datasheet/driver)
TEMP_BIAS = 1852  # LSB at 25°C
TEMP_SLOPE = -9.05  # LSB/°C

# Error messages
error_messages = {
    'interrupt': ['Interrupts disabled', 'INT disabled'],
    'dis_single_double': ['Single/Double Tap disabled', 'S/D Tap disabled'],
    'dis_double': ['Double Tap disabled', 'D Tap disabled'],
    'undesirable': ['Undesirable behavior', 'Undesired'],
}