from ctypes.wintypes import CHAR
import serial
from serial.serialutil import PARITY_EVEN, Timeout
import serial.tools.list_ports, serial.tools.list_ports_common, serial.tools.list_ports_windows
import time
#import locale
#locale.setlocale(locale.LC_ALL, 'de_DE')

def transAccuNumToStr(accuNumber):
    accuTypsStr = ["NiCd","NiMH","Li-Ion","LiPo","Pb","LiFePO","N/A"]
    if accuNumber < 6:
        return(accuTypsStr[accuNumber])
    else:
        return(accuTypsStr[6])

def transEscByArToClearByAr(RawArray : bytearray):
    laenge = RawArray.__len__()

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
   
    def setVerSerNum(self, serNumRaw : bytearray):
        longAlcTyp = ["Start"]
        longAlcTyp[98] = "ALC 8500 Firmware < 2.00"
        longAlcTyp[99] = "ALC 8000 Firmware < 2.00"
        longAlcTyp[100] = "ALC 8500-2 Firmware < 2.00"
        longAlcTyp[101] = "ALC 8000 PLUS Firmware < 2.00"
        longAlcTyp[102] = "ALC 5000 mobile Firmware < 2.00"
        longAlcTyp[103] = "ALC 3000 PC Firmware > 2.00"
        longAlcTyp[104] = "ALC 8500-2 Firmware > 2.00"
        longAlcTyp[105] = "ALC 8000 Firmware > 2.00"
        longAlcTyp[106] = "ALC 5000 mobil Firmware > 2.00"

        shortAlcTyp = ["Start"]
        shortAlcTyp[98] = "ALC8500"
        shortAlcTyp[99] = "ALC8000"
        shortAlcTyp[100] = "ALC8500-2"
        shortAlcTyp[101] = "ALC8000PLUS"
        shortAlcTyp[102] = "ALC5000mobile"
        shortAlcTyp[103] = "ALC3000PC"
        shortAlcTyp[104] = "ALC8500-2"
        shortAlcTyp[105] = "ALC8000"
        shortAlcTyp[106] = "ALC5000mobil"

        temp_string = serNumRaw[7:11]
        self.__SwVersion = temp_string.decode()
        self.__TypeLong = longAlcTyp[serNumRaw[2]]
        self.__TypeShort = shortAlcTyp[serNumRaw[2]]

        temp_string = serNumRaw[13:23]
        self.__SerialNumber = temp_string.decode()

    def setTemperatures(self,temperaturesRaw:bytearray):

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

    def __init__(self, chargePort, channelNumber):

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
        #if self.__accuType == 0:
        #    self.__accuTypeDescription = "NiCd"
        #elif self.__accuType == 1:
        #    self.__accuTypeDescription = "NiMH"
        #elif self.__accuType == 2:
        #     self.__accuTypeDescription = "Li-Ion"
        # elif self.__accuType == 3:
        #     self.__accuTypeDescription = "LiPo"
        # elif self.__accuType == 4:
        #     self.__accuTypeDescription = "Pb"
        # elif self.__accuType == 5:
        #     self.__accuTypeDescription = "LiFePO"
        # elif self.__accuType == 0xff:
        #     self.__accuTypeDescription = "N/A"
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
    
    def __init__(self,chargePort,dbEntryNumber):
        
        self.__chargePort = chargePort
        self.__dbEntryNumber = dbEntryNumber

    def pulldbEntry(self):
        temp_ByteArray : bytearray
        print(self.__dbEntryNumber)
        channelInstr = bytearray([0x02, 0x64])
        self.__chargePort.write(channelInstr)
        if (self.__dbEntryNumber == 0x02 or self.__dbEntryNumber == 0x03 or self.__dbEntryNumber == 0x05):
            channelInstr = bytearray([0x05, 0x10 + channelInstr])
        else:
            channelInstr = bytearray([self.__dbEntryNumber])
        self.__chargePort.write(channelInstr)
        channelInstr = bytearray([0x03])
        self.__chargePort.write(channelInstr)

        if (self.__dbEntryNumber == 0x02 or self.__dbEntryNumber == 0x03 or self.__dbEntryNumber == 0x05):
            temp_ByteArray   = self.__chargePort.read(29)
            print(temp_ByteArray)
            if self.__dbEntryNumber == 0x02:
                temp_ByteArray[2] = 0x02
            elif self.__dbEntryNumber == 0x03:
                temp_ByteArray[2] = 0x03
            elif self.__dbEntryNumber == 0x05:
                temp_ByteArray[2] = 0x05
            for i in range(4,28):
                temp_ByteArray[i-1] = temp_ByteArray[i]
        else:
            temp_ByteArray          = self.__chargePort.read(28)

        self.__accuName         = temp_ByteArray[3:12].decode()
        self.__dbRereadEntryNumber = temp_ByteArray[2]
        self.__accuType         = temp_ByteArray[12]
        self.__accuCellCount    = temp_ByteArray[13]
        self.__accuCapacity     = float((temp_ByteArray[14] * 0x1000000 + temp_ByteArray[15] * 0x10000 + temp_ByteArray[16] * 0x100 + temp_ByteArray[17]) / 10000)
        self.__rechargeCurrent  = float((temp_ByteArray[18] * 256 + temp_ByteArray[19]) / 10)
        self.__chargeCurrent    = float((temp_ByteArray[20] * 256 + temp_ByteArray[21]) / 10)
        self.__restPeriod       = temp_ByteArray[22] * 256 + temp_ByteArray[23]
        self.__chargeFlags      = temp_ByteArray[24]
        self.__functionsFlags   = temp_ByteArray[25]

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

chargeDevice = ChargeDevicesAlcGeneric("COM4")
chargeDevice.setVerSerNum(chargeDevice.pullVerSerNum())
chargeDevice.setTemperatures(chargeDevice.pullTemperatures())

chargeCannel = ChargeDeviceALCChannel(chargeDevice.getChargePort(),0)
chargeCannel.pullCurrentCannelData()
chargeCannel.pullCurrentMeasuredValues()

chargeDBentry = ChargeDeviceAccuDbEntry(chargeDevice.getChargePort(),0x02)
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