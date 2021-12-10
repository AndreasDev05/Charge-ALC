from ctypes.wintypes import CHAR
import serial
from serial.serialutil import PARITY_EVEN, Timeout
import serial.tools.list_ports, serial.tools.list_ports_common, serial.tools.list_ports_windows
import time

from simpleHelpFunc import transByArToEscByAr, transEscByArToClearByAr

#import locale
#locale.setlocale(locale.LC_ALL, 'de_DE')

def transAccuNumToStr(accuNumber):
    accuTypsStr = ["NiCd","NiMH","Li-Ion","LiPo","Pb","LiFePO","N/A"]
    if accuNumber < 6:
        return(accuTypsStr[accuNumber])
    else:
        return(accuTypsStr[6])

class ChargeDevicesAlcGeneric():

    ChargeChannels = 0
    AccuDbItems = 0x27

    def __init__(self, ser_port):
        self.__chargePort = serial.Serial(ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        #TODO: Expliziete Übergabe der Schnittstellenparameter, für eine unverselle Funktion
    #    print(type(self.__chargePort))

    def pullVerSerNum(self):
        temp_ByteArray : bytearray
        chargeInstr = bytearray([2,0x75,3])
        
        self.__chargePort.write(chargeInstr)

        temp_ByteArray = self.__chargePort.read(24)
    #    self.__chargePort.close()
    #    print(temp_ByteArray)
        return(temp_ByteArray)

    def pullTemperatures(self):
        temp_ByteArray : bytearray
        chargeInstr = bytearray([0x02,0x74,0x03])
        
        self.__chargePort.write(chargeInstr)

        temp_ByteArray = self.__chargePort.read(9)
        return(temp_ByteArray)
   
    def setVerSerNum(self, serNumRaw: bytearray):
        longAlcTyp = {98: "ALC 8500 Firmware < 2.00", 99: "ALC 8000 Firmware < 2.00",
                      100: "ALC 8500-2 Firmware < 2.00", 101: "ALC 8000 PLUS Firmware < 2.00", 102: "ALC 5000 mobile Firmware < 2.00",
                      103: "ALC 3000 PC Firmware > 2.00", 104: "ALC 8500-2 Firmware > 2.00", 105: "ALC 8000 Firmware > 2.00",
                      106: "ALC 5000 mobil Firmware > 2.00"}
        '''
        longAlcTyp = ["Start"]
        longAlcTyp.insert(98,"ALC 8500 Firmware < 2.00")
        longAlcTyp.insert(99,"ALC 8000 Firmware < 2.00")
        longAlcTyp.insert(100,"ALC 8500-2 Firmware < 2.00")
        longAlcTyp.insert(101,"ALC 8000 PLUS Firmware < 2.00")
        longAlcTyp.insert(102,"ALC 5000 mobile Firmware < 2.00")
        longAlcTyp.insert(103,"ALC 3000 PC Firmware > 2.00")
        longAlcTyp.insert(104,"ALC 8500-2 Firmware > 2.00")
        longAlcTyp.insert(105,"ALC 8000 Firmware > 2.00")
        longAlcTyp.insert(106,"ALC 5000 mobil Firmware > 2.00")
        '''
        shortAlcTyp = {98: "ALC8500", 99: "ALC8000", 100: "ALC8500-2", 101: "ALC8000PLUS",
                       102: "ALC5000mobile", 103: "ALC3000PC", 104: "ALC8500-2", 105: "ALC8000", 106: "ALC5000mobil"}
        '''
        shortAlcTyp = ["Start"]
        shortAlcTyp.insert(98, "ALC8500")
        shortAlcTyp.insert(99, "ALC8000")
        shortAlcTyp.insert(100, "ALC8500-2")
        shortAlcTyp.insert(101, "ALC8000PLUS")
        shortAlcTyp.insert(102, "ALC5000mobile")
        shortAlcTyp.insert(103, "ALC3000PC")
        shortAlcTyp.insert(104, "ALC8500-2")
        shortAlcTyp.insert(105, "ALC8000")
        shortAlcTyp.insert(106, "ALC5000mobil")
        '''
        temp_string = serNumRaw[7:11]
        self.__SwVersion = temp_string.decode()
        # print(longAlcTyp.index("ALC 8000 Firmware > 2.00"))
        self.__TypeLong = longAlcTyp[serNumRaw[2]]
        self.__TypeShort = shortAlcTyp[serNumRaw[2]]

        temp_string = serNumRaw[13:23]
        self.__SerialNumber = temp_string.decode()

    def setTemperatures(self, temperaturesRaw: bytearray):

        temp_temp_int = temperaturesRaw[2] * 256 + temperaturesRaw[3]
        if temp_temp_int == 0xABE0:
            self.__tempAccuFloat = None
        else:
            self.__tempAccuFloat = float(temp_temp_int / 100)
        #TODO: Negative Temperaturen berechnen

        temp_temp_int = temperaturesRaw[4] * 256 + temperaturesRaw[5]
        if temp_temp_int == 0xABE0:
            self.__tempPowerSupFloat = None
        else:
            self.__tempPowerSupFloat = float(temp_temp_int / 100)
        #TODO: Negative Temperaturen berechnen

        temp_temp_int = temperaturesRaw[6] * 256 + temperaturesRaw[7]
        self.__tempMainFloat = float(temp_temp_int / 100)

    def getSerNum(self):
        return(self.__SerialNumber)

    def getDeviceTypeLong(self):
        return(self.__TypeLong)

    def getDeviceTypeShort(self):
        return(self.__TypeShort)

    def getDeviceSwVersion(self):
        return(self.__SwVersion)

    def getChargePort(self):
        return(self.__chargePort)

    def getMainTemperature(self):
        return(self.__tempMainFloat)

    def getAccuTemperature(self):
        '''  Temperatur des Akkus

        Gibt die Temperatur des Akkus in °C als float zurück.
        Wenn kein Sensor angeschlossen ist gibt die Funktion "None" zurück.
        '''
        return(self.__tempAccuFloat)

class ChargeDeviceALC3000(ChargeDevicesAlcGeneric):

    chargeCannel = 1

    def __init__(self, ser_port):
        ChargeDevicesAlcGeneric.__init__(self, ser_port)
        
        for i in range(1,self.chargeCannel):
            self.chargeCannelIns[i] = ChargeDeviceALCChannel(self.__chargePort,i-1)
            self.chargeCannelIns[i].pullCurrentCannelData()
            self.chargeCannelIns[i].pullCurrentMeasuredValues()

        for i in range(self.AccuDbItems):
            self.chargeDbEntry[i] = ChargeDeviceAccuDbEntry(self.__chargePort,i)
            self.chargeDbEntry[i].pulldbEntry

class ChargeDeviceALCChannel():

    def __init__(self, chargePort:serial.Serial, channelNumber):

        self.ser_port = chargePort
        self.__chargePort = chargePort
        self.__channelNumber = channelNumber

    def pullCurrentCannelData(self):
        temp_ByteArray : bytearray
        #self.__chargePort = serial.Serial(self.ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        channelInstr = bytearray([2,0x70,self.__channelNumber,3])
        self.__chargePort.write(channelInstr)

        temp_ByteArray = self.__chargePort.read(24)
        self.__accuNumber   = temp_ByteArray[3]
        self.__accuType     = temp_ByteArray[4]
        self.__accuTypeDescription = transAccuNumToStr(self.__accuType)
        self.__cellCount    = temp_ByteArray[5]
        self.__rechargeCurrent = float((temp_ByteArray[6] * 256 + temp_ByteArray[7]) / 10)
        self.__chargeCurrent = float((temp_ByteArray[8] * 256 + temp_ByteArray[9]) / 10)
        self.__accuCapacity = float((temp_ByteArray[10] * 0x1000000 + temp_ByteArray[11] * 0x10000 + temp_ByteArray[12] * 0x100 + temp_ByteArray[13]) / 10000)
        self.__programNumber = temp_ByteArray[14]
        self.__formattingCurrent = float((temp_ByteArray[15] * 256 + temp_ByteArray[16]) / 10)
        self.__restPeriod   = temp_ByteArray[17] * 256 + temp_ByteArray[18]
        self.__chargeFlags  = temp_ByteArray[19]
        self.__pointerDataRecord = temp_ByteArray[20] * 256 + temp_ByteArray[21]
        self.__accuCapacityFactor = temp_ByteArray[22]
        
        print("Akkunummer: ",self.__accuNumber)
        print("Ladestrom: ",self.__chargeCurrent)
        print("Entladestrom: ",self.__rechargeCurrent)
        print("Akkutype: ",self.__accuTypeDescription)
        print("Akkukapazität: ",self.__accuCapacity)

    def pullCurrentMeasuredValues(self):
        temp_ByteArray : bytearray
        isDataSetOK = False
        attemptCount = 0
        channelInstr = bytearray([2,0x6D,self.__channelNumber,3])

        while True:
            self.__chargePort.write(channelInstr)

            temp_ByteArray = self.__chargePort.read(12)
            self.__chargePort.reset_input_buffer()
            self.__chargePort.reset_output_buffer()
            # time.sleep(0.5)
            if temp_ByteArray[11] == 0x03:
                if (temp_ByteArray[3] * 256 + temp_ByteArray[4]) != 0xFFFF:
                    self.__topicalVoltage = float((temp_ByteArray[3] * 256 + temp_ByteArray[4]) / 1000)
                if (temp_ByteArray[5] * 256 + temp_ByteArray[6]) != 0xFFFF:
                    self.__topicalCurrent = float((temp_ByteArray[5] * 256 + temp_ByteArray[6]) / 10)
                self.__topicalAccuCapacity = float((temp_ByteArray[7] * 0x1000000 + temp_ByteArray[8] * 0x10000 + temp_ByteArray[9] * 0x100 + temp_ByteArray[10]) / 10000)
                attemptCount = attemptCount + 1
                isDataSetOK = True
            if isDataSetOK or attemptCount > 5:
                if isDataSetOK == False:
                    self.__topicalVoltage = None
                    self.__topicalCurrent = None
                    self.__topicalAccuCapacity = None
                break

        print(self.__topicalVoltage,"V ;",temp_ByteArray[3],"; ",temp_ByteArray[4])
        print(self.__topicalCurrent,"mA")
        print(self.__topicalAccuCapacity,"mA/h")

    def getTopicalVoltage(self):
        return(self.__topicalVoltage)

    def getTopicalCurrent(self):
        return(self.__topicalCurrent)

    def getTopicalAccuCapacity(self):
        return(self.__topicalAccuCapacity)

    def getAccuNumber(self):
        return(self.__accuNumber)

    def getChargeCurrent(self):
        return(self.__chargeCurrent)

    def getRechargeCurrent(self):
        return(self.__rechargeCurrent)

    def getAccuTypeDescription(self):
        return(self.__accuTypeDescription)

    def getCellCount(self):
        return(self.__cellCount)

    def getProgramNumber(self):
        return(self.__programNumber)

    def getFormatingCurrent(self):
        return(self.__formattingCurrent)

    def getRestPeriod(self):
        return(self.__restPeriod)

    def getChargeFlags(self):
        # TODO: Flags seperat auswerten
        return(self.__chargeFlags)

    def getPointerDataRecord(self):
        return(self.__pointerDataRecord)

    def getAccuCapacityFactor(self):
        return(self.__accuCapacityFactor)

class ChargeDeviceAccuDbEntry():
    
    def __init__(self,chargePort:serial.Serial,dbEntryNumber):
        
        self.__chargePort = chargePort
        self.__dbEntryNumber = dbEntryNumber

    def pulldbEntry(self):
        temp_ByteArray : bytearray
        channelInstr = bytearray([0x64,self.__dbEntryNumber])
        temp_ByteArray = transByArToEscByAr(channelInstr)
        '''
        for i in range(0,temp_ByteArray.__len__()):
            self.__chargePort.write(temp_ByteArray[i])
            time.sleep(0.01)
            print(i," ",temp_ByteArray[i])
        '''
        self.__chargePort.write(transByArToEscByAr(channelInstr))
        print(transByArToEscByAr(channelInstr))
        temp_ByteArray          = self.__chargePort.read_until(b'\x03',50)
        print(temp_ByteArray)
        temp_ByteArray          = transEscByArToClearByAr(temp_ByteArray)
        print(temp_ByteArray)
        self.__accuName         = temp_ByteArray[2:11].decode()
        self.__dbRereadEntryNumber = temp_ByteArray[1]
        self.__accuType         = temp_ByteArray[11]
        self.__accuCellCount    = temp_ByteArray[12]
        self.__accuCapacity     = float((temp_ByteArray[13] * 0x1000000 + temp_ByteArray[14] * 0x10000 + temp_ByteArray[15] * 0x100 + temp_ByteArray[16]) / 10000)
        self.__rechargeCurrent  = float((temp_ByteArray[17] * 256 + temp_ByteArray[18]) / 10)
        self.__chargeCurrent    = float((temp_ByteArray[19] * 256 + temp_ByteArray[20]) / 10)
        self.__restPeriod       = temp_ByteArray[21] * 256 + temp_ByteArray[22]
        self.__chargeFlags      = temp_ByteArray[23]
        self.__functionsFlags   = temp_ByteArray[24]

        print(temp_ByteArray)
        #print(self.__accuName)

    def getAccuName(self):
        return(self.__accuName)

    def getAccuTyp(self):
        return(self.__accuType)

    def getAccuCellCount(self):
        return(self.__accuCellCount)

    def getAccuCapacity(self):
        return(self.__accuCapacity)

    def getRechargeCurrent(self):
        return(self.__rechargeCurrent)

    def getChargeCurrent(self):
        return(self.__chargeCurrent)

    def getRestPeriod(self):
        return(self.__restPeriod)

    def getChargeFlags(self):
        return(self.__chargeFlags)

    def getFunctionsFlags(self):
        return(self.__functionsFlags)

if __name__ == "__main__":

    chargeDevice = ChargeDevicesAlcGeneric("COM4")
    chargeDevice.setVerSerNum(chargeDevice.pullVerSerNum())
    chargeDevice.setTemperatures(chargeDevice.pullTemperatures())

    chargeCannel = ChargeDeviceALCChannel(chargeDevice.getChargePort(),0)
    chargeCannel.pullCurrentCannelData()
    chargeCannel.pullCurrentMeasuredValues()
    time.sleep(1)
    chargeDBentry = ChargeDeviceAccuDbEntry(chargeDevice.getChargePort(),0x05)
    chargeDBentry.pulldbEntry()

    print(chargeDevice.getSerNum())
    print(chargeDevice.getDeviceTypeLong())
    print(chargeDevice.getDeviceTypeShort())
    print(chargeDevice.getDeviceSwVersion())
    print(chargeDevice.getMainTemperature(),"°C")

    print(chargeDBentry.getAccuName())
    print(chargeDBentry.getAccuTyp())
    print(chargeDBentry.getAccuCellCount())
    print(chargeDBentry.getChargeCurrent())