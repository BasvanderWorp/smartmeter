# Dutch Smart Meter Reader (P1)
versie = "1.0"
import sys
import serial

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
DMSR_PORT = CONFIG['DMSR_PORT']
DMSR_PORT = "/dev/ttyUSB0"
DMSR_BAUDRATE = CONFIG['DMSR_BAUDRATE']
DMSR_BAUDRATE = 115200
DMSR_BYTESIZE = CONFIG['DMSR_BYTESIZE']
DMSR_BYTESIZE =serial.SEVENBITS
DMSR_PARITY = CONFIG['DMSR_PARITY']
DMSR_PARITY = serial.PARITY_EVEN

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
    logger.info('Start program    : ' + PROGRAM_NAME)
    logger.info('Version          : ' + PROGRAM_VERSION)
    logger.info('Version date     : ' + PROGRAM_VERSION_DATE)
    logger.info('Host             : ' + socket.gethostname())
    logger.info('parameters       : ')
    logger.info('parameters       : ')

print ("Digital Smart Meter Reader (P1), version ",  PROGRAM_VERSION)
print ("Press Control-C to stop")

# Set COM port config
ser = serial.Serial()
ser.port = DMSR_PORT
ser.baudrate = DMSR_BAUDRATE
ser.bytesize = DMSR_BYTESIZE
ser.parity = DMSR_PARITY

# Open COM port
import ipdb; ipdb.set_trace()
try:
    ser.open()
    print('Seriele poort geopend!')
except serial.serialutil.SerialException as err1:
    if err1.args[0] == 'Port is already open.':
        logger.warning(err1)
        pass
    else:
        msg = f'Error opening port {ser.name}, error: {err1}'
        logger.warning(msg)
        print (msg, ' program terminated')

# Initialize
# p1_teller is mijn tellertje voor van 0 tot 20 te tellen
p1_teller=0

while p1_teller < 20:
    print(f'p1_teller: {p1_teller}')
    p1_line=''
# Read 1 line van de seriele poort
    try:
        print('Start lezen van de regel')
        p1_raw = ser.readline()
        print('Regel gelezen')
    except:
        sys.exit ("Seriele poort %s kan niet gelezen worden. Aaaaaaaaarch." % ser.name )
    print(f'p1_raw: {p1_raw}')
    p1_str=str(p1_raw)
    print(f'p1_str: {p1_str}')
    p1_line=p1_str.strip()
# als je alles wil zien moet je de volgende line uncommenten
    # print (p1_line)
    p1_teller = p1_teller +1

# Close port and show status
try:
    ser.close()
except:
    sys.exit ("Oops %s. Programma afgebroken. Kon de seriele poort niet sluiten." % ser.name )
