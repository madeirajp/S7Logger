# this is fine #
# for taglists.txt: show all columns, select all (CTRL+A) and paste to notepad
# columns should be in following order: Name, Tag table, Data type, Address

# If there is need to debug, enable this
#logging.basicConfig(level=logging.DEBUG)

# IP-address for PLC
ipaddress = "169.254.0.101"

# import some stuff
import snap7.client as c
from snap7.util import *
from snap7.snap7types import *

# time library for sleep function and for logging local time
import time

# sys library for nice console output
import sys

# create dict to store IO objects
names = {}

# because OOP is the way to go
class IOObject:

    # counter for how many IOs we are logging
    IOCount = 0

    # constructor
    def __init__(self, name, dtype, ioType, byte, bit):
        self.name = name
        self.dtype = dtype
        self.ioType = ioType
        self.byte = byte
        self.bit = bit
        self.reading = 0
        IOObject.IOCount += 1

    # display the count
    def displayCount(self):
        print IOObject.IOCount

    # display something else
    def returnName(self):
        return self.name

    def returnType(self):
    	return self.dtype

    def returnIoType(self):
    	return self.ioType

    def returnByte(self):
    	return self.Byte

    def returnBit(self):
    	return self.Bit

    # flag for edge detection
    def setEdgeFlag(self):
        self.edgeFlag = True

    # flag for resetting
    def resetEdgeFlag(self):
        self.edgeFlag = False

    def readIO(self):
	    result = plc.read_area(areas['PA'],0,int(self.byte),S7WLBit)
	    #print "IO read"
	    return get_bool(result,0,int(self.bit))

    # for printing human-readable things about our objects
    def __str__(self):
        return "%s %s %s %s %s" % (self.name, self.dtype, self.ioType, self.byte, self.bit)

# areas['PE'] = Process Inputs
# byte is the first number and bit is the second
# i.e. ReadInput(plc,1,0,S7WLBit) will read Bool from %I1.1
# datatype is usually S7WLBit
def ReadInput(plc,byte,bit,datatype):
    result = plc.read_area(areas['PE'],0,byte,datatype)
    return get_bool(result,0,bit)

# PA = Process outpus
#def ReadIO(plc,byte,bit,datatype):
 #   result = plc.read_area(areas['PA'],0,byte,datatype)
 #   return get_bool(result,0,bit)


# this function will read the text file and save the IOs to dict
def readTags():

    # okay, lets open this file
    taglist = open('taglist.txt', 'r')

    # then loop through all of the lines
    for line in taglist:

        # and split them by line break
        splitline = line.split('\n')

        # how to not name variables.. 
        name = splitline[0].strip().split('\t')

        # ignore files starting with hashtag
        if not name[0] == "#":

			address = list(name[3])
			dtype = name[2]

			# separate address to type, byte, bit and exclude timers etc
			if len(address) == 5:
				ioType = address[1]
				byte = address[2]
				bit = address[4]
				print ioType + byte + bit

				# call the constructor
				names[name[0]] = IOObject(name[0], dtype, ioType, byte, bit)

			else:
				print "Timers etc not supported"			

def logToFile():

    for oPut in names:

    	value = names[oPut].readIO()
    	#print oPut
    	#print names[oPut]
    	#print nimi
        print "\n" + names[oPut].returnName() + " " + str(value)

        # time formatting
        datestamp = time.strftime('%Y-%m-%d')
        timestamp = time.strftime('%H:%M:%S')

        # Edges
        #edge = thisIO+"Edge"

        # Logging for mag solenoid
        if value == True:

            # write to file
            f.write('\n' + names[oPut].returnName())
            f.write("," + datestamp + "," + timestamp + '\n')
            print("event logged")
            # Edge flag to false
            #edge = False

        # From falling edge "reset" the edge flags to True
        #if key == False:
           # key = True


# MAIN LOOP
if __name__=="__main__":

    # Create client
    plc = c.Client()
    # Connect to Distribution station IP, rack 0, slot 2
    plc.connect(ipaddress,0,2)

    # read the tags
    readTags()

    # print all the IO objects to console just to make sure 
    print "\n" + "These " + str(IOObject.IOCount) + " IOs will be logged: "
    print "#######################"
    for x in names:
        print names[x]
    print "#######################" + "\n"

    # Scanning loop
    while True:
        
        timestamp = time.strftime('%H:%M:%S')

        # Let the user know that scanning is active
        sys.stdout.write('\r Scanning PLC IOs on ' + timestamp)  
        #sys.stdout.flush()

        # Open the file where we log the data
        f = open('workfile.txt', 'a')

        # calling logging function
        logToFile()

        # Close the workfile
        f.close()

        # Wait for five seconds
        time.sleep(1)

    # Disconnect from plc
    plc.disconnect()