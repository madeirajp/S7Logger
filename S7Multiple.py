# Only Bool-type of memory values supported!

# for taglists.txt: show all columns, select all (CTRL+A) and paste to notepad
# columns should be in following order: Name, Tag table, Data type, Address
# tags export to xlsx is not supported

# If there is need to debug, enable this
# logging.basicConfig(level=logging.DEBUG)

# If you destroy/wipe the log file, append manually Memory,Type,Date,Time, to the first row!

# IP-address for PLC, this is for the Distributing Station
ipaddress1 = "169.254.0.101"
ipaddress2 = "169.254.0.102"

# Scan time in seconds
scantime = 0.1

# import some stuff
import snap7.client as c
from snap7.util import *
from snap7.snap7types import *
import time
import sys
import threading
import SimpleHTTPServer
import SocketServer
import random

# create dict to store IO objects
names = {}
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
        self.edgeFlag = False
        IOObject.IOCount += 1

    # display the count
    def displayCount(self):
        print IOObject.IOCount

    def returnName(self):
        return self.name

    def returnType(self):
        return self.dtype

    def returnIoType(self):
        return self.ioType

    def returnByte(self):
        return self.byte

    def returnBit(self):
        return self.bit

    # flag for edge detection
    def setEdgeFlag(self):
        self.edgeFlag = True

    # flag for resetting
    def resetEdgeFlag(self):
        self.edgeFlag = False

    def returnEdgeFlag(self):
        return self.edgeFlag

    def readIO(self, station):

        if self.dtype != "Bool":
            print "Only Boolean memory types are supported!"
            return

        # areas:
        # PA = Process outputs, PE = Process inputs, MK = Merkers
        if self.ioType == "Q":
            result = station.read_area(areas['PA'], 0, int(self.byte), S7WLBit)
        if self.ioType == "I":
            result = station.read_area(areas['PE'], 0, int(self.byte), S7WLBit)
        if self.ioType == "M":
            result = station.read_area(areas['MK'], 0, int(self.byte), S7WLBit)

            # return the value
        return get_bool(result, 0, int(self.bit))

    # for printing human-readable things about our objects
    def __str__(self):
        return "%s %s %s %s %s" % (self.name, self.dtype, self.ioType, self.byte, self.bit)

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

        # print list(name[0])

        # ignore files starting with hashtag
        if not list(name[0])[0] == "#":

            # sorry about this mess, memory addresses were tough for me
            address = name[3].split(".")
            # print address
            dtype = name[2]
            addresslist = list(address[0])
            ioType = addresslist[1]
            byte = ''.join(addresslist[2:])

            # Memory types without byte,bit type of address are not supported
            if len(address) > 1:
                # prevent indexerror
                bit = address[1]
                # call the constructor
                names[name[0]] = IOObject(name[0], dtype, ioType, byte, bit)
            # let the user know if there is any unsupported type of tags
            else:
                # instructions for user
                print "\nNOTICE: " + name[2] + " is not supported!"

# actual logging
def logToFile():

    # Inputs, Outputs or Memory objects
    for IOM in names:

        # renaming
        thisIO = names[IOM]

        # read the certain IO
        value1 = thisIO.readIO(plc1)
        value2 = thisIO.readIO(plc2)

        # time formatting
        datestamp = time.strftime('%Y-%m-%d')
        timestamp = time.strftime('%H:%M:%S')

        # Logging only if this IO is True and edge flag is on
        if value1 == True or value2 == True and thisIO.returnEdgeFlag():
            # write to file the name and type
            f.write(thisIO.returnName() + "," + thisIO.returnIoType())

            # and of cource date- and timestamp, duh
            f.write("," + datestamp + "," + timestamp + '\n')

            # also print something to console
            #print('\n' + thisIO.returnName() + " event logged")

            # reset the edge flag
            thisIO.resetEdgeFlag()

        # From falling edge set the edge flag
        if value1 == False or value2 == False:
            thisIO.setEdgeFlag()


# MAIN LOOP
if __name__ == "__main__":

    # Create client
    plc1 = c.Client()
    plc2 = c.Client()

    # read the tags and create objects
    readTags()

    # ONLINE: lets connect
    if True:
        # arguments are for rack 0, slot 2
        plc1.connect(ipaddress1, 0, 2)
        plc2.connect(ipaddress2, 0, 2)
        # print all the IO objects to console just to make sure
        print "These " + str(IOObject.IOCount) + " memory addresses will be logged: "
        for x in names:
            print "  " + str(names[x])
        print "Online mode activated"

    # just a little fun to console.. sorry I was tired
    print "Initializing",
    for x in range(0, IOObject.IOCount):
        print ".",
        time.sleep(scantime)

    try:
        # Scanning loop
        while True:
            # time formatting
            timestamp = time.strftime('%H:%M:%S')
            # Open the file where we log the data
            f = open('logmultiple.csv', 'a')
            # if we are online, lets log
            if True:
                # Let the user know that scanning is active
                sys.stdout.write(
                    '\r Scanning PLC memory on ' + timestamp + ' with the scan time of ' + str(scantime) + ' seconds' +
                    ' on http://127.0.0.1:8080/S7PivotVisualizer.html')
                sys.stdout.flush()
                logToFile()

            # Close the workfile so the logged data can be viewed while the script is running
            f.close()

            # Wait for five seconds
            time.sleep(scantime)

    # to break out from loop in console (CTRL+C)
    except KeyboardInterrupt:
        logFile = open('workfile.txt', 'r')
        print "\n \n" + "Thank you for using S7Logger! Here are the contents of the workfile: " + "\n"
        for line in logFile:
            print line

        plc.disconnect()
        logFile.close()
        print "Workfile closed. Bye!"
