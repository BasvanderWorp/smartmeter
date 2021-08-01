# Dutch Smart Meter Reader (P1)
import sys
import serial
from util import read_config
import argparse
import os
import logging
from datetime import datetime
import socket

##############################################################################
# Part 0.1: Set global variables
##############################################################################
PROGRAM_NAME = 'dsmr'
PROGRAM_VERSION = "0.01"
PROGRAM_VERSION_DATE = "11-07-2021"
PROGRAM_AUTHOR = "Bas van der Worp"
CONFIG_STORE = '/dsmr/dsmr_config.json'
CONFIG = read_config(CONFIG_STORE)
LOG_PATH_BASE = CONFIG['LOG_PATH_BASE']
OUTPUT_PATH_BASE = CONFIG['OUTPUT_PATH_BASE']
DSMR_PORT = CONFIG['DSMR_PORT']
DSMR_BAUDRATE = eval(CONFIG['DSMR_BAUDRATE'])
DSMR_BYTESIZE = eval(CONFIG['DSMR_BYTESIZE'])
DSMR_PARITY = eval(CONFIG['DSMR_PARITY'])

##############################################################################
# Main program
##############################################################################
if __name__ == '__main__':
    ##########################################################################
    # === Part 0.2: Commandline parameter initialisation
    ##########################################################################
    parser = argparse.ArgumentParser()
    requiredNamed = parser.add_argument_group('required named arguments')
    requiredNamed.add_argument("-d", "--dummy", help="Dummy")
    args = parser.parse_args()

    if args.dummy:
        dummy = args.dummy
    else:
        dummy = ""

    ##########################################################################
    # Part 0.3: Initialise logging
    ##########################################################################
    # Check whether logfolder exists. If not, write to 'log' folder
    LOG_PATH = f'{LOG_PATH_BASE}{PROGRAM_NAME}/'
    if not os.path.exists(LOG_PATH):
        try:
            os.makedirs(LOG_PATH)
        except OSError as e:
            if e.errno != errno.EEXIST:
                LOG_PATH = ""
                raise

    OS_USER = os.getlogin().lower()
    LOGLEVEL_DEBUG = eval('logging.DEBUG')
    LOGLEVEL_INFO = eval('logging.INFO')

    LOGFILE = os.path.normpath(LOG_PATH + "log"
                               "_" + "{:%Y%m%d}".format(datetime.now()) +
                               ".log")

    logging.basicConfig(
        filename=LOGFILE,
        level='INFO',
        format='%(asctime)s %(levelname)s ' +
               '%(name)s %(funcName)s: %(message)s',
        datefmt='%d-%m-%Y %H:%M:%S')
    logger = logging.getLogger(__name__)

    msg_1 = '='*80
    logger.info(msg_1)
    logger.info(f'Start program    : {PROGRAM_NAME}')
    logger.info(f'Version          : {PROGRAM_VERSION}')
    logger.info(f'Version date     : {PROGRAM_VERSION_DATE}')
    logger.info(f'Host             : {socket.gethostname()}')
    logger.info(f'parameters       : {CONFIG}')

    ##########################################################################
    # Part 0.4: Start logging
    ##########################################################################
    print ("Digital Smart Meter Reader (P1), version ",  PROGRAM_VERSION)
    print ("Press Control-C to stop")

    # Set COM port config
    ser = serial.Serial()
    ser.port = DSMR_PORT
    ser.baudrate = DSMR_BAUDRATE
    ser.bytesize = DSMR_BYTESIZE
    ser.parity = DSMR_PARITY

    # Open COM port
    try:
        ser.open()
        logger.info('Serial port opened!')
    except serial.serialutil.SerialException as err1:
        if err1.args[0] == 'Port is already open.':
            logger.warning(err1)
            pass
        else:
            msg = f'Error opening port {ser.name}, error: {err1}'
            logger.warning(msg)
            print (msg, ' program terminated')
            sys.exit(msg)

    # Initialize
    telegram_counter = 1
    line_counter = 0

    while telegram_counter < 25:
        p1_line = ''
        telegram_start_line_found = False

        # Read lines from serial port, search start of telegram
        while not telegram_start_line_found:
            try:
                p1_raw = ser.readline()
                line_counter += 1
            except:
                sys.exit (f"Seriele port {ser.name} cannot be read.")
            if p1_raw == b'/ISK5\\2M550T-1011\r\n':
                telegram_start_line_found = True
                print(f'{str(line_counter).zfill(4)} telegram {telegram_counter}', end="")
            else:
                # skip line, not a start line
                print(f'{str(line_counter).zfill(4)} SKIPPED: {p1_raw}')

        if telegram_start_line_found:
            # read first line
            p1_raw = ser.readline()
            p1_str = p1_raw.decode('utf-8')
            line_counter += 1
            if p1_str == '!':
                telegram_last_line_found = True
            else: 
                telegram_last_line_found = False
        else:
            msg = 'start line not found'
            logger.error(msg)
            sys.exit(msg)

        # Read all telegram lines
        while not telegram_last_line_found:
            p1_str = p1_raw.decode('utf-8')
            msg = f'{str(line_counter).zfill(4)}: RAW: {p1_raw}, DECODE:{p1_str}'
            # print(msg, end="")
            if p1_str[0] == '!':
                # print(f'{str(line_counter).zfill(4)} LAST LINE FOUND: {p1_raw}')
                telegram_last_line_found = True
                telegram_counter += 1
            else: 
                telegram_last_line_found = False
                if p1_str[-2:] == '\r\n':
                    p1_str = p1_str[:-2]
                else:
                    msg = f'Unexpected end of line in telegram line {p1_raw}'
                    logger.error(msg)
                    sys.exit(msg)
    
                if len(p1_str) > 3:
                    if p1_str[3] == ':':
                        p1_str = p1_str[4:]
                    else:
                        # skip line
                        try:
                            # print(f'{str(line_counter).zfill(4)} SKIPPED2: {p1_raw}')
                            p1_raw = ser.readline()
                            line_counter += 1
                        except:
                            sys.exit (f"Seriele port {ser.name} cannot be read.")
                        continue
                else:
                    # skip line (maybe error)
                    try:
                        # print(f'{str(line_counter).zfill(4)} SKIPPED3: {p1_raw}')
                        p1_raw = ser.readline()
                        line_counter += 1
                    except:
                        sys.exit (f"Seriele port {ser.name} cannot be read.")
                    if p1_raw == b'!5AC3\r\n':
                        telegram_last_line_found = True
                        telegram_counter += 1
                        print(f'{str(line_counter).zfill(4)} LAST LINE FOUND: {p1_raw}')
                    continue

                # print(p1_str)
                measure = ""
                value = ""
                obis_code = p1_str.split('(')[0]
                p1_value = p1_str.split('(')[1][:-1]
                # remove closing bracket
                if obis_code == '1.7.0':
                    measure = "actual_delivery (kW)"
                    value = p1_value[:-1]
                    print(f'---- {measure}:{value}')
                # print(f'{str(line_counter).zfill(4)}: {p1_raw}, {measure}:{value}')

                try:
                    p1_raw = ser.readline()
                    line_counter += 1
                except:
                    sys.exit (f"Seriele port {ser.name} cannot be read.")
    
    # Close port and show status
    try:
        ser.close()
        msg = f"Serial port {ser.name} succesfully closed."
        logger.info(msg)
    except:
        msg = f"Oops {ser.name}. Programma terminated. Could not close serial port"
        logger.error(msg)
        sys.exit (msg)
