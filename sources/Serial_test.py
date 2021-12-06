from ctypes.wintypes import CHAR
import serial
from serial.serialutil import PARITY_EVEN, Timeout
import serial.tools.list_ports, serial.tools.list_ports_common, serial.tools.list_ports_windows

all_ser_ports = serial.tools.list_ports.comports()
for singel_port in all_ser_ports :
    print(singel_port.device, ": ", singel_port.description, ":", singel_port.hwid)
chargePort = serial.Serial("COM4", 38400, 8, PARITY_EVEN, 1, 3)
chargeInstr = bytearray([2,116,3])
chargePort.write(chargeInstr)

temp_ser_read = chargePort.read(9)

temp_main_int = temp_ser_read[6] * 256 + temp_ser_read[7]
temp_main_float = float(temp_main_int / 100)

print(temp_ser_read)

print(temp_main_int," ",temp_main_float)

chargePort.close()

#from serial.tools import list_ports
#print(
#    "\n".join(
#        [
#            port.device + ': ' + port.description
#            for port in list_ports.comports()
#        ]
#    )
#)
