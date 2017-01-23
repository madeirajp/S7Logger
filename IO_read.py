import snap7.client as c
from snap7.util import *
from snap7.snap7types import *

# time is needed for sleep function and for logging local time
import time
import sys

# If there is need to debug, enable this
#logging.basicConfig(level=logging.DEBUG)

# IP-address for PLC
ipaddress = "123.123.123.123"

# areas['PE'] = Process Inputs
# byte is the first number and bit is the second
# i.e. ReadInput(plc,1,0,S7WLBit) will read Bool from %I1.1
def ReadInput(plc,byte,bit,datatype):
    result = plc.read_area(areas['PE'],0,byte,datatype)
    return get_bool(result,0,bit)

# PA = Process Outputs
def ReadOutput(plc,byte,bit,datatype):
    result = plc.read_area(areas['PA'],0,byte,datatype)
    return get_bool(result,0,bit)

if __name__=="__main__":

    # Create client
    plc = c.Client()

    # Connect to Distribution station IP, rack 0, slot 2
    plc.connect(ipaddress,0,2)

    # Initialize edge flags
    magSolenoidEdge = True
    vacuumOnEdge = True
    armRightEdge = True

    # Scanning loop
    while True:
        
        # time formatting
        datestamp = time.strftime('%Y-%m-%d')
        timestamp = time.strftime('%H:%M:%S')
        
        # Let the user know that scanning is active
        sys.stdout.write('\r Scanning PLC IOs on ' + timestamp)  
        sys.stdout.flush()

        # Open the file where we log the data
        f = open('workfile.txt', 'a') 

        # save the output values
        magSolenoid = ReadOutput(plc,0,0,S7WLBit)
        vacuumOn = ReadOutput(plc,0,1,S7WLBit)
        armRight = ReadOutput(plc,0,4,S7WLBit)

        # Logging for mag solenoid
        if magSolenoid and magSolenoidEdge:
            # write to file
            f.write("magSolenoid," + str(magSolenoid))
            f.write("," + datestamp + "," + timestamp + '\n')
            # Edge flag to false
            magSolenoidEdge = False

        # Logging for vacuum
        if vacuumOn and vacuumOnEdge:
            f.write("vacuumOn," + str(vacuumOn))
            f.write("," + datestamp + "," + timestamp + '\n')
            vacuumOnEdge = False

        # Logging for arm right movement
        if armRight and armRightEdge:
            f.write("armRight," + str(armRight))
            f.write("," + datestamp + "," + timestamp + '\n')
            armRightEdge = False

         # From falling edge "reset" the edge flags to True
        if magSolenoid == False:
            magSolenoidEdge = True
        if vacuumOn == False:
            vacuumOnEdge = True
        if armRight == False:
            armRightEdge = True

        # Close the workfile
        f.close()

        # Wait for five seconds
        time.sleep(0.1)

    # Disconnect from plc
    plc.disconnect()
        