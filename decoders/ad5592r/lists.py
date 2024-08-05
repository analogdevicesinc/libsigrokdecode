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

def disabled_enabled(v):
    return 'Disabled' if v == 0 else 'Enabled'


def dac_ch(v):
    return 'DAC{0}'.format(v)


def adc_chn(v):
    return 'ADC{v}'.format(v=v)


def empty_str(v):
    return ''


def dec_to_hex(v):
    '''Convert a number to a string with hexadecimal representation.'''
    return '0x{0:02X}'.format(v)


def bit_indices(num):
    '''Return bit indices of a number as a string where bits are set to 1.'''
    res = []
    i = 0
    while num:
        if num & 1:
            res.append(str(i))
        num >>= 1
        i += 1
    return ','.join(res)


#   CTRL_REGISTERS: dict
#       Opcode (key):  a control register
#       Value:  tuple
#          0:  register name : str    
#          1:  Field Configuration (Tuple)
#               0:  start bit   : int
#               1:  width      : int
#               2:  field name  : int
#               3:  parsing filed custom function
#                   display filed value if missing
#       
#   Special keys: 'ADDR_IDX', 'MSB_IDX' -> provide global description (fields common to all registers)
CTRL_REGISTERS = {
    0b0000: (
        'NOP',
        (
            (11, 4, 'REG_ADDR', dec_to_hex),
        ),
    ),
    0b0001: (
        'DAC_RD',
        (
            (0, 3, 'DAC_CH_SEL', dac_ch),
            (3, 2, 'DAC_RD_EN', disabled_enabled),
            (5, 6, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        ),
    ),
    0b0010: (
        'ADC_SEQ',
        (
            (0, 8, 'ADC Channels', bit_indices),
            # When enabled temp also sent to MISO
            (8, 1, 'Temp Indicator', disabled_enabled),
            (9, 1, 'Repeat', disabled_enabled),
            (10, 1, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0011: (
        'GEN_CTRL_REG',
        (
            (0,  4, 'RESERVED', empty_str),
            (4,  1, 'DAC_RANGE', lambda v: '0V to {text}'.format(
                text=['Vref', '2xVref'][v])),
            (5,  1, 'ADC_RANGE', lambda v: '0V to {text}'.format(
                text=['Vref', '2xVref'][v])),
            (6,  1, 'ALL_DAC', disabled_enabled),
            (7,  1, 'IO_LOCK', disabled_enabled),
            (8,  1, 'ADC_BUF_EN', disabled_enabled),
            (9,  1, 'ADC_BUF_PRECH', disabled_enabled),
            (10, 1, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0100: (
        'ADC_CONFIG',
        (
            (0, 8, 'ADC input pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0101: (
        'DAC_CONFIG',
        (
            (0, 8, 'DAC output pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0110: (
        'PULLDWN_CONFIG',
        (
            (0, 8, 'Weak-pulldown output pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b0111: (
        'CONFIG_READ_AND_LDAC',
        (
            (0, 2, 'LDAC_MODE', empty_str),
            (2, 4, 'Read back register', dec_to_hex),
            (6, 1, 'REG_RD_EN', disabled_enabled),
            (7, 4, 'REG_RD_EN', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1000: (
        'GPIO_CONFIG',
        (
            (0, 8, 'GPIO output pins', bit_indices),
            (8, 1, 'EN_BUSY', disabled_enabled),
            (9, 2, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1001: (
        'GPIO_OUTPUT', 
        (
            (0, 8, 'Logic "1" pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1010: (
        'GPIO_INPUT',
        (
            (0, 8, 'GPIO input pins', bit_indices),
            (9, 2, 'RESERVED', empty_str),
            (10, 1, 'GPIO_RD_EN', disabled_enabled),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1011: (
        'PD_REF_CTRL',
        (
            (0, 8, 'DAC power-down pins', bit_indices),
            (8, 1, 'RESERVED', empty_str),
            (9, 1, 'Internal reference', disabled_enabled),
            (10, 1, 'Power down all', disabled_enabled),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1100: (
        'GPIO_OPENDRAIN_CONFIG',
        (
            (0, 8, 'GPIO open-drain pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1101: (
        'IO_TS_CONFIG',
        (
            (0, 8, 'Three-state output pins', bit_indices),
            (8, 3, 'RESERVED', empty_str),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    0b1111: (
        'SW_RESET',
        (
            (0, 8, 'Reset command', dec_to_hex),
            (11, 4, 'REG_ADDR', dec_to_hex),
        )
    ),
    'ADDR_IDX': (11, 4),
    'MSB_IDX': (15, 1),
}

DAC_CHANNELS = {
    # any DAC addr write [0 to 7] has the same register structure
    0: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    1: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    2: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    3: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    4: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    5: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    6: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    7: (
        'DAC_WR',
        (
            (0, 12, 'DAC data'),
            (12, 3, 'DAC addr')
        )
    ),
    'ADDR_IDX': (12, 3),
    'MSB_IDX': (15, 1),
}

#   0:  Field Configuration (Tuple)
#       0:  start bit   : int
#       1:  width      : int
#       2:  field name  : int
#       3 (optional):  parsing filed custom function
#                      display filed value if missing
MISO_READING = {
    'ADC_RESULT': (
        (0, 12, 'ADC data'),
        (12, 3, 'ADC_ADDR', adc_chn),
    ),
    'TMP_SENSE_RESULT': (
        (0, 12, 'Temperature data'),
        (12, 4, 'TEMPSENSE_ADDR', empty_str),
    ),
    'DAC_DATA_RD': (
        (0, 12, 'DAC data'),
        (12, 3, 'DAC addr'),
    ),
    'REG_READ': (
        
    ),
}
