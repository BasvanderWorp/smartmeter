# DSMR P1 uitlezen
# (c) 10-2012 - GJ - gratis te kopieren en te plakken
versie = "1.0"
import sys
import serial

##############################################################################
# Main program
##############################################################################
print ("DSMR P1 uitlezen",  versie)
print ("Control-C om te stoppen")
print ("Pas eventueel de waarde ser.port aan in het python script")

# Set COM port config
ser = serial.Serial("/dev/ttyUSB0")
ser.baudrate = 115200
ser.bytesize=serial.SEVENBITS
# ser.parity=serial.PARITY_EVEN
# ser.stopbits=serial.STOPBITS_ONE
# ser.xonxoff=0
# ser.rtscts=0
# ser.timeout=1
ser.port="/dev/ttyUSB0"

# Open COM port
import ipdb; ipdb.set_trace()
try:
    ser.open()
    print('Seriele poort geopend!')
except serial.serialutil.SerialException as err1:
    if err1.args[0] == 'Port is already open.':
        pass
    else:
        sys.exit ("Fout bij het openen van %s. Aaaaarch."  % ser.name)


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
