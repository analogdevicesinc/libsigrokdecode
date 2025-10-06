##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2025 Analog Devices Inc.
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

import sigrokdecode as srd
from common.srdhelper import SrdIntEnum
from .lists import *

Ann = SrdIntEnum.from_str('Ann', 'REG_ADDRESS REG_DATA WARNING')

St = SrdIntEnum.from_str('St', 'IDLE GET_SLAVE_ADDR GET_REG_ADDR WAIT_RESTART_OR_DATA READ_DATA')

class Decoder(srd.Decoder):
    api_version = 3
    id = 'adxl355'
    name = 'ADXL355'
    longname = 'Analog Devices ADXL355'
    desc = 'Analog Devices ADXL355 3-axis accelerometer.'
    license = 'gplv2+'
    inputs = ['i2c']
    outputs = []
    tags = ['IC', 'Sensor']
    options = (
        {'id': 'address', 'desc': 'I2C slave address', 'default': 0x1D,
         'values': (0x1D, 0x53)},
        {'id': 'scale_factor', 'desc': 'Acceleration scale factor', 'default': '±2g',
         'values': ('±2g', '±4g', '±8g')},
    )
    annotations = (
        ('reg-address', 'Register address'),
        ('reg-data', 'Register data'),
        ('warning', 'Warning'),
    )
    annotation_rows = (
        ('regs', 'Registers', (Ann.REG_ADDRESS,)),
        ('data', 'Data', (Ann.REG_DATA, Ann.WARNING)),
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = St.IDLE
        self.reg = 0
        self.pending_reg = None
        self.read_count = 0
        self.read_data = []
        self.ss, self.es = -1, -1
        self.data_start_sample = None
        self.block_start_sample = None
        self.data = -1  # For multi-byte values
        self.start_index = None

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.address = self.options['address']
        # Set scale factor based on user option
        scale_option = self.options['scale_factor']
        if scale_option == '±2g':
            self.scale_factor = SCALE_FACTOR_2G
        elif scale_option == '±4g':
            self.scale_factor = SCALE_FACTOR_4G
        elif scale_option == '±8g':
            self.scale_factor = SCALE_FACTOR_8G
        else:
            self.scale_factor = SCALE_FACTOR_2G  # Default

    def putx(self, data):
        self.put(self.ss, self.es, self.out_ann, data)
        
    def handle_acceleration(self, data3, data2, data1, axis):
        # Combine bytes (20-bit value from 3 bytes)
        # data3 is MSB, data1 is LSB
        raw = (data3 << 12) | (data2 << 4) | (data1 >> 4)

        # Convert to signed 20-bit value
        if raw >= 0x80000:
            raw -= 0x100000

        # Convert to acceleration (assuming typical scale factor)
        # This would need to be adjusted based on your sensor's specifications
        acceleration_g = raw / self.scale_factor  # Sscale factor

        self.put(self.start_index, self.es, self.out_ann,
             [Ann.REG_DATA, ['%s-axis: %.3fg' % (axis, acceleration_g), '%.3fg' % acceleration_g]])
        
    def handle_temperature(self, temp2, temp1):
        # Combine bytes (12-bit value, left-justified)
        raw = ((temp2 & 0x0F) << 8) | temp1

        # Convert to Celsius
        celsius = ((raw - TEMP_BIAS) / TEMP_SLOPE) + 25.0
        self.put(self.start_index, self.es, self.out_ann,
                 [Ann.REG_DATA, ['Temperature: %.2f°C' % celsius, '%.2f°C' % celsius]])

    def handle_reg_0x00(self, data):
        # DEVID_AD
        if data == 0xAD:
            self.putx([Ann.REG_DATA, ['Device ID AD: 0xAD', 'ID: 0xAD']])
        else:
            self.putx([Ann.WARNING, ['Device ID AD: 0x%02X (expected 0xAD!)' % data]])

    def handle_reg_0x01(self, data):
        # DEVID_MST
        if data == 0x1D:
            self.putx([Ann.REG_DATA, ['Device ID MST: 0x1D', 'ID: 0x1D']])
        else:
            self.putx([Ann.WARNING, ['Device ID MST: 0x%02X (expected 0x1D!)' % data]])

    def handle_reg_0x02(self, data):
        # PARTID
        if data == 0xED:
            self.putx([Ann.REG_DATA, ['Part ID: 0xED (ADXL355)', 'Part: 0xED']])
        else:
            self.putx([Ann.REG_DATA, ['Part ID: 0x%02X' % data, 'Part: 0x%02X' % data]])

    def handle_reg_0x03(self, data):
        # REVID
        self.putx([Ann.REG_DATA, ['Revision ID: 0x%02X' % data, 'Rev: 0x%02X' % data]])

    def handle_reg_0x04(self, data):
        # STATUS
        status = []
        if data & STATUS_NVM_BUSY: status.append('NVM_BUSY')
        if data & STATUS_ACTIVITY: status.append('Activity')
        if data & STATUS_FIFO_OVR: status.append('FIFO_OVR')
        if data & STATUS_FIFO_FULL: status.append('FIFO_FULL')
        if data & STATUS_DATA_RDY: status.append('DATA_RDY')
        status_str = ' | '.join(status) if status else 'None'
        self.putx([Ann.REG_DATA, ['Status: %s' % status_str, status_str]])

    def handle_reg_0x05(self, data):
        # FIFO_ENTRIES
        self.putx([Ann.REG_DATA, ['FIFO Entries: %d' % data, 'FIFO: %d' % data]])

    def handle_reg_0x06(self, data):
        # TEMP2
        if self.data == -1:
            self.data = data
            self.start_index = self.ss
            self.putx([Ann.REG_DATA, [str(data)]])
        else:
            self.putx([Ann.WARNING, ['Unexpected TEMP2 data']])

    def handle_reg_0x07(self, data):
        # TEMP1
        if self.data != -1:
            self.handle_temperature(self.data, data)
            self.data = -1
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x08(self, data):
        # XDATA3
        self.x_data3 = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x09(self, data):
        # XDATA2
        self.x_data2 = data
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x0a(self, data):
        # XDATA1
        if hasattr(self, 'x_data3') and hasattr(self, 'x_data2'):
            self.handle_acceleration(self.x_data3, self.x_data2, data, 'X')
            # Clear the stored values
            delattr(self, 'x_data3')
            delattr(self, 'x_data2')
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x0b(self, data):
        # YDATA3
        self.y_data3 = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x0c(self, data):
        # YDATA2
        self.y_data2 = data
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x0d(self, data):
        # YDATA1
        if hasattr(self, 'y_data3') and hasattr(self, 'y_data2'):
            self.handle_acceleration(self.y_data3, self.y_data2, data, 'Y')
            # Clear the stored values
            delattr(self, 'y_data3')
            delattr(self, 'y_data2')
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x0e(self, data):
        # ZDATA3
        self.z_data3 = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x0f(self, data):
        # ZDATA2
        self.z_data2 = data
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x10(self, data):
        # ZDATA1
        if hasattr(self, 'z_data3') and hasattr(self, 'z_data2'):
            self.handle_acceleration(self.z_data3, self.z_data2, data, 'Z')
            # Clear the stored values
            delattr(self, 'z_data3')
            delattr(self, 'z_data2')
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x11(self, data):
        # FIFO_DATA - special handling for FIFO reads
        # From datasheet: 96 21-bit FIFO locations, each location is one axis measurement (3 bytes)
        # Each location: 20-bit data + 2 virtual bits (0b00) + empty bit + x-axis marker bit
        if not hasattr(self, 'fifo_byte_count'):
            self.fifo_byte_count = 0
            self.fifo_start_sample = self.ss
            self.fifo_data = []
            self.fifo_location_count = 0
        
        self.fifo_data.append(data)
        self.fifo_byte_count += 1
        
        # Determine position within 3-byte FIFO location
        byte_in_location = (self.fifo_byte_count - 1) % 3
        
        if byte_in_location == 0:
            # First byte of FIFO location (MSB) - store but don't annotate yet
            self.fifo_start_sample = self.ss
        elif byte_in_location == 1:
            # Second byte of FIFO location - store but don't annotate yet
            pass
        elif byte_in_location == 2:
            # Third byte of FIFO location (LSB) - complete the location and annotate
            data3 = self.fifo_data[-3]  # MSB
            data2 = self.fifo_data[-2]  # MID
            data1 = data                # LSB
            
            # Check status bits in LSB
            empty_bit = (data1 >> 1) & 1
            x_marker_bit = data1 & 1
            
            if empty_bit:
                self.put(self.fifo_start_sample, self.es, self.out_ann,
                        [Ann.WARNING, ['FIFO Empty - Invalid Data', 'FIFO Empty']])
            else:
                # Extract 20-bit acceleration value
                # Data format: [MSB][MID][LSB with 2 virtual bits + empty + marker]
                # 20-bit data is in upper 20 bits: (data3 << 12) | (data2 << 4) | (data1 >> 4)
                raw = (data3 << 12) | (data2 << 4) | (data1 >> 4)
                
                # Convert to signed 20-bit value
                if raw >= 0x80000:
                    raw -= 0x100000
                
                # Convert to acceleration using configured scale factor
                acceleration_g = raw / self.scale_factor
                
                # Determine axis based on marker bit and sequence tracking
                if x_marker_bit:
                    # This is X-axis data - reset sequence tracking
                    axis_name = 'X'
                    self.fifo_axis_sequence = 0  # Reset to X
                else:
                    # This is Y or Z axis data - determine based on sequence
                    if not hasattr(self, 'fifo_axis_sequence'):
                        self.fifo_axis_sequence = 0  # Initialize if missing
                    
                    # Increment sequence (X=0, Y=1, Z=2, then repeat)
                    self.fifo_axis_sequence = (self.fifo_axis_sequence + 1) % 3
                    
                    if self.fifo_axis_sequence == 1:
                        axis_name = 'Y'
                    elif self.fifo_axis_sequence == 2:
                        axis_name = 'Z'
                    else:
                        # Fallback - should not happen if X marker is working correctly
                        axis_name = 'Unknown'
                
                self.put(self.fifo_start_sample, self.es, self.out_ann,
                        [Ann.REG_DATA, ['FIFO %s: %.3fg (0x%05X) [Empty:%d, X-Mark:%d]' % 
                                       (axis_name, acceleration_g, raw & 0xFFFFF, empty_bit, x_marker_bit), 
                                       '%s: %.3fg' % (axis_name, acceleration_g)]])
            
            self.fifo_location_count += 1

    def handle_reg_0x1e(self, data):
        # OFFSET_X_H
        self.data = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x1f(self, data):
        # OFFSET_X_L
        if self.data != -1:
            offset = (self.data << 8) | data
            if offset & 0x8000:
                offset = offset - 0x10000
            self.put(self.start_index, self.es, self.out_ann,
                     [Ann.REG_DATA, ['X Offset: %d' % offset, 'X Off: %d' % offset]])
            self.data = -1
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x20(self, data):
        # OFFSET_Y_H
        self.data = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x21(self, data):
        # OFFSET_Y_L
        if self.data != -1:
            offset = (self.data << 8) | data
            if offset & 0x8000:
                offset = offset - 0x10000
            self.put(self.start_index, self.es, self.out_ann,
                     [Ann.REG_DATA, ['Y Offset: %d' % offset, 'Y Off: %d' % offset]])
            self.data = -1
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x22(self, data):
        # OFFSET_Z_H
        self.data = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x23(self, data):
        # OFFSET_Z_L
        if self.data != -1:
            offset = (self.data << 8) | data
            if offset & 0x8000:
                offset = offset - 0x10000
            self.put(self.start_index, self.es, self.out_ann,
                     [Ann.REG_DATA, ['Z Offset: %d' % offset, 'Z Off: %d' % offset]])
            self.data = -1
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x24(self, data):
        # ACT_EN
        acts = []
        if data & 0x01: acts.append('ACT_X')
        if data & 0x02: acts.append('ACT_Y')  
        if data & 0x04: acts.append('ACT_Z')
        act_str = ' | '.join(acts) if acts else 'None'
        self.putx([Ann.REG_DATA, ['Activity Enable: %s' % act_str, 'Act: %s' % act_str]])

    def handle_reg_0x25(self, data):
        # ACT_THRESH_H
        self.data = data
        self.start_index = self.ss
        self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x26(self, data):
        # ACT_THRESH_L
        if self.data != -1:
            threshold = (self.data << 8) | data
            mg = threshold * 3.9  # 3.9mg/LSB
            self.put(self.start_index, self.es, self.out_ann,
                     [Ann.REG_DATA, ['Activity Threshold: %.1f mg' % mg, 'Act Thr: %.1f mg' % mg]])
            self.data = -1
        else:
            self.putx([Ann.REG_DATA, [str(data)]])

    def handle_reg_0x27(self, data):
        # ACT_COUNT
        self.putx([Ann.REG_DATA, ['Activity Count: %d' % data, 'Act Cnt: %d' % data]])

    def handle_reg_0x28(self, data):
        # FILTER
        hpf = (data >> 4) & 0x07
        odr = data & 0x0F
        
        hpf_str = FILTER_HPF_CORNER.get(hpf << 4, 'Unknown')
        odr_str = FILTER_ODR.get(odr, 'Unknown')
        
        self.putx([Ann.REG_DATA, ['Filter - HPF: %s, ODR: %s' % (hpf_str, odr_str), 
                                  'HPF: %s, ODR: %s' % (hpf_str, odr_str)]])

    def handle_reg_0x29(self, data):
        # FIFO_SAMPLES
        self.putx([Ann.REG_DATA, ['FIFO Samples: %d' % data, 'FIFO: %d' % data]])

    def handle_reg_0x2a(self, data):
        # INT_MAP
        ints = []
        if data & 0x01: ints.append('DATA_RDY')
        if data & 0x02: ints.append('FIFO_FULL')
        if data & 0x04: ints.append('FIFO_OVR')
        if data & 0x08: ints.append('Activity')
        int_str = ' | '.join(ints) if ints else 'None'
        self.putx([Ann.REG_DATA, ['INT Map: %s' % int_str, int_str]])

    def handle_reg_0x2b(self, data):
        # SYNC
        sync_mode = (data >> 2) & 0x03
        sync_str = {0: 'Internal', 1: 'External', 2: 'Ext w/ INT', 3: 'Reserved'}.get(sync_mode)
        self.putx([Ann.REG_DATA, ['Sync: %s' % sync_str, sync_str]])

    def handle_reg_0x2c(self, data):
        # RANGE
        range_val = data & 0x03
        range_str = {RANGE_2G: '±2g', RANGE_4G: '±4g', RANGE_8G: '±8g'}.get(range_val, 'Reserved')
        self.putx([Ann.REG_DATA, ['Range: %s' % range_str, range_str]])

    def handle_reg_0x2d(self, data):
        # POWER_CTL
        mode = 'Measurement' if (data & POWER_CTL_MEASUREMENT) == 0 else 'Standby'
        temp = 'OFF' if data & POWER_CTL_TEMP_OFF else 'ON'
        drdy = 'OFF' if data & POWER_CTL_DRDY_OFF else 'ON'
        self.putx([Ann.REG_DATA, ['Power: %s, Temp: %s, DRDY: %s' % (mode, temp, drdy),
                                  '%s, T:%s, D:%s' % (mode, temp, drdy)]])

    def handle_reg_0x2e(self, data):
        # SELF_TEST
        if data & 0x01:
            self.putx([Ann.REG_DATA, ['Self Test: Enabled', 'ST: On']])
        else:
            self.putx([Ann.REG_DATA, ['Self Test: Disabled', 'ST: Off']])

    def handle_reg_0x2f(self, data):
        # RESET
        if data == 0x52:
            self.putx([Ann.REG_DATA, ['Reset command', 'Reset']])
        else:
            self.putx([Ann.REG_DATA, ['Reset: 0x%02X' % data, '0x%02X' % data]])

    def decode(self, ss, es, data):
        cmd, databyte = data
        self.es = es

        # State machine
        if self.state == St.IDLE:
            if cmd in ['START', 'START REPEAT']:
                self.ss = ss
                self.block_start_sample = ss
                self.state = St.GET_SLAVE_ADDR
                
        elif self.state == St.GET_SLAVE_ADDR:
            if cmd == 'ADDRESS WRITE':
                if databyte == self.address:
                    self.state = St.GET_REG_ADDR
                else:
                    self.state = St.IDLE
            elif cmd == 'ADDRESS READ':
                if databyte == self.address:
                    self.state = St.READ_DATA
                    self.read_count = 0
                    self.read_data = []
                    self.data_start_sample = ss
                else:
                    self.state = St.IDLE
                    
        elif self.state == St.GET_REG_ADDR:
            if cmd == 'DATA WRITE':
                self.reg = databyte
                self.pending_reg = databyte
                self.ss = ss
                self.put(ss, es, self.out_ann, [Ann.REG_ADDRESS, register_names.get(self.reg, ['0x%02X' % self.reg])])
                self.state = St.WAIT_RESTART_OR_DATA
                
        elif self.state == St.WAIT_RESTART_OR_DATA:
            if cmd == 'DATA WRITE':
                # This is a write operation
                self.ss = ss
                self.put(ss, es, self.out_ann, [Ann.REG_ADDRESS, register_names.get(self.reg, ['0x%02X' % self.reg])])
                
                if self.reg < 0x00 or self.reg > 0x2F:
                    self.putx([Ann.REG_DATA, [str(databyte)]])
                elif self.reg >= 0x12 and self.reg <= 0x1D:
                    # These registers don't exist per ADXL355 datasheet
                    self.putx([Ann.WARNING, ['Invalid register 0x%02X (undefined)' % self.reg, 
                                            'Invalid: 0x%02X' % self.reg]])
                else:
                    handle_reg = getattr(self, 'handle_reg_0x%02x' % self.reg, None)
                    if handle_reg:
                        handle_reg(databyte)
                    else:
                        self.putx([Ann.REG_DATA, ['0x%02X' % databyte, str(databyte)]])
                
                self.reg = (self.reg + 1) & 0xFF
            elif cmd in ['START REPEAT', 'STOP']:
                if cmd == 'STOP':
                    self.state = St.IDLE
                else:
                    self.state = St.GET_SLAVE_ADDR
                    
        elif self.state == St.READ_DATA:
            if cmd == 'DATA READ':
                self.read_data.append(databyte)
                self.read_count += 1
                
                # Special handling for FIFO_DATA register - it doesn't auto-increment
                if self.pending_reg == 0x11:
                    current_reg = 0x11  # FIFO_DATA stays at 0x11
                else:
                    current_reg = ((self.pending_reg or 0) + self.read_count - 1) & 0xFF
                
                self.ss = ss
                self.put(ss, es, self.out_ann, [Ann.REG_ADDRESS, register_names.get(current_reg, ['0x%02X' % current_reg])])
                
                # Handle other registers
                if current_reg < 0x00 or current_reg > 0x2F:
                    self.putx([Ann.REG_DATA, [str(databyte)]])
                elif current_reg >= 0x12 and current_reg <= 0x1D:
                    # These registers don't exist per ADXL355 datasheet
                    self.putx([Ann.WARNING, ['Invalid register 0x%02X (undefined)' % current_reg, 
                                            'Invalid: 0x%02X' % current_reg]])
                else:
                    handle_reg = getattr(self, 'handle_reg_0x%02x' % current_reg, None)
                    if handle_reg:
                        handle_reg(databyte)
                    else:
                        self.putx([Ann.REG_DATA, ['0x%02X' % databyte, str(databyte)]])
                    
            elif cmd == 'STOP':
                self.state = St.IDLE
                self.pending_reg = None