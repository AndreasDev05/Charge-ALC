# import time

import serial
import serial.tools.list_ports
import serial.tools.list_ports_common
import serial.tools.list_ports_windows
from serial.serialutil import PARITY_EVEN, Timeout

from simple_help_func import (trans_by_ar_to_esc_by_ar,
                              trans_esc_by_ar_to_clear_by_ar,
                              trans_accu_num_to_str)

# import locale
# locale.setlocale(locale.LC_ALL, 'de_DE')


class charge_devices_alc_generic():

    charge_channels = 0
    accu_db_items = 0x27

    def __init__(self, ser_port):
        self.__sw_version: str = str()
        self.__type_long: str = str()
        self.__type_short: str = str()
        self.__serial_number: str = str()

        self.__temp_main_float: float = float()
        self.__temp_accu_float: float = float()
        self.__temp_power_sup_float: float = float()
        self.__charge_port = serial.Serial(
            ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        # TODO: Expliziete Übergabe der Schnittstellenparameter,
        # für eine unverselle Funktion
    #    print(type(self.__chargePort))

    def pull_ver_ser_num(self):
        """Liest die Identität des Ladesgerätes aus.

        Läd die statischen Parameter und speichert sie in die Objektvariablen.
        Wandelt auch die numerische Typennummern in Strings um.
        """
        LONG_ALC_TYP = {98: "ALC 8500 Firmware < 2.00",
                        99: "ALC 8000 Firmware < 2.00",
                        100: "ALC 8500-2 Firmware < 2.00",
                        101: "ALC 8000 PLUS Firmware < 2.00",
                        102: "ALC 5000 mobile Firmware < 2.00",
                        103: "ALC 3000 PC Firmware > 2.00",
                        104: "ALC 8500-2 Firmware > 2.00",
                        105: "ALC 8000 Firmware > 2.00",
                        106: "ALC 5000 mobil Firmware > 2.00"}

        SHORT_ALC_TYP = {98: "ALC8500", 99: "ALC8000", 100: "ALC8500-2",
                         101: "ALC8000PLUS", 102: "ALC5000mobile",
                         103: "ALC3000PC", 104: "ALC8500-2",
                         105: "ALC8000", 106: "ALC5000mobil"}
        temp_byte_array: bytearray
        charge_instr = bytearray([0x75])

        self.__charge_port.write(trans_by_ar_to_esc_by_ar(charge_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)

        temp_string = temp_byte_array[6:10]
        self.__sw_version = temp_string.decode()
        self.__type_long = LONG_ALC_TYP[temp_byte_array[1]]
        self.__type_short = SHORT_ALC_TYP[temp_byte_array[1]]

        temp_string = temp_byte_array[12:22]
        self.__serial_number = temp_string.decode()

    def pull_temperatures(self):
        """Läd die Temperaturwerte des Ladegerätes aus.

        Läd die dynamischen Temperaturwerte und speichert sie in die
        Objektvariablen. Die Werte werden in °C umgerechnet und als
        Fließkommawerte abgespeichert
        """
        temp_byte_array: bytearray
        charge_instr = bytearray([0x74])

        self.__charge_port.write(trans_by_ar_to_esc_by_ar(charge_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)

        temp_temp_int = temp_byte_array[1] * 256 + temp_byte_array[2]

        if temp_temp_int == 0xABE0:
            self.__temp_accu_float = None
        else:
            self.__temp_accu_float = float(temp_temp_int / 100)
        # TODO: Negative Temperaturen berechnen

        temp_temp_int = temp_byte_array[3] * 256 + temp_byte_array[4]
        if temp_temp_int == 0xABE0:
            self.__temp_power_sup_float = None
        else:
            self.__temp_power_sup_float = float(temp_temp_int / 100)
        # TODO: Negative Temperaturen berechnen

        temp_temp_int = temp_byte_array[5] * 256 + temp_byte_array[6]
        self.__temp_main_float = float(temp_temp_int / 100)

    def get_is_alc_ready(self):
        """Diese Funktion kontrolliert Erreichbarkeit des Gerätes.

        Die Funktion fragt das Gerät ab. Ist das Gerät erreichbar und gibt die
        richtige Seriennummer zurück, erhält man ein TRUE, anderenfalls FALSE.
        """
        temp_byte_array: bytearray
        charge_instr = bytearray([0x75])
        try:
            self.__charge_port.write(trans_by_ar_to_esc_by_ar(charge_instr))
            temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        except FileNotFoundError:
            temp_return = False
            return temp_return

        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)

        temp_string = temp_byte_array[12:22]
        temp_serial_number = temp_string.decode()

        if temp_serial_number == self.__serial_number:
            temp_return = True
        else:
            temp_return = False

        return temp_return

    def get_ser_num(self):
        return self.__serial_number

    def get_device_type_long(self):
        return self.__type_long

    def get_device_type_short(self):
        return self.__type_short

    def get_device_sw_version(self):
        return self.__sw_version

    def get_charge_port(self):
        return self.__charge_port

    def get_main_temperature(self):
        """Temperatur des Sytems.

        Gibt die Temperatur des Systems /Kühlkörper in °C als float zurück.
        """
        return self.__temp_main_float

    def get_accu_temperature(self):
        """Temperatur des Akkus.

        Gibt die Temperatur des Akkus in °C als float zurück.
        Wenn kein Sensor angeschlossen ist gibt die Funktion "None" zurück.
        """
        return self.__temp_accu_float

    def get_power_sup_temperature(self):
        """Temperatur des Netzteils.

        Gibt die Temperatur des Netzteils in °C als float zurück.
        Wenn kein Sensor angeschlossen ist gibt die Funktion "None" zurück.
        """
        return self.__temp_power_sup_float


class ChargeDeviceALC3000(charge_devices_alc_generic):

    charge_cannel = 1

    def __init__(self, ser_port):
        charge_devices_alc_generic.__init__(self, ser_port)

        self.charge_cannel_ins: list = list()
        self.charge_db_entry: list = list()
        for i in range(1, self.charge_cannel):
            self.charge_cannel_ins[i] = ChargeDeviceAlcChannel(
                self.__charge_port, i-1)
            self.charge_cannel_ins[i].pullCurrentCannelData()
            self.charge_cannel_ins[i].pullCurrentMeasuredValues()

        for i in range(self.accu_db_items):
            self.charge_db_entry[i] = ChargeDeviceAccuDbEntry(
                self.__charge_port, i)
            self.charge_db_entry[i].pulldbEntry()


class ChargeDeviceAlcChannel():

    def __init__(self, charge_port: serial.Serial, channel_number):

        self.__accu_number: bytes = bytes()
        self.__accu_type: bytes = bytes()
        self.__accu_type_description: str = str()
        self.__cell_count: bytes = bytes()
        self.__recharge_current: float = float()
        self.__charge_current: float = float()
        self.__accu_capacity: float = float()
        self.__program_number: bytes = bytes()
        self.__formatting_current: float = float()
        self.__rest_period: int = int()
        self.__charge_flags: bytes = bytes()
        self.__pointer_data_record: int = int()
        self.__accu_capacity_factor: bytes = bytes()
        self.__topical_voltage: float = float()
        self.__topical_current: float = float()
        self.__topical_accu_capacity: float = float()
        self.__charge_function_str: str = str()
        self.__charge_function: bytes = bytes()

        self.ser_port = charge_port
        self.__charge_port = charge_port
        self.__channel_number = channel_number

    def pull_current_cannel_data(self):
        """Läd die Parameter des übergebenen Ladekanals.

        Läd die statischen Parameter und speichert sie in die Objektvariablen
        Der Ladekanal wird bei der Erzeugung der Instanz übergeben
        """
        temp_byte_array: bytearray
        # self.__chargePort = serial.Serial(self.ser_port, 38400, 8, PARITY_EVEN, 1, 3)
        channel_instr = bytearray([0x70, self.__channel_number])
        self.__charge_port.write(trans_by_ar_to_esc_by_ar(channel_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)
        self.__accu_number = temp_byte_array[2]
        self.__accu_type = temp_byte_array[3]
        self.__accu_type_description = trans_accu_num_to_str(self.__accu_type)
        self.__cell_count = temp_byte_array[4]
        self.__recharge_current = float(
            (temp_byte_array[5] * 256 + temp_byte_array[6]) / 10)
        self.__charge_current = float(
            (temp_byte_array[7] * 256 + temp_byte_array[8]) / 10)
        self.__accu_capacity = float(
            (temp_byte_array[9] * 0x1000000 + temp_byte_array[10] * 0x10000 +
             temp_byte_array[11] * 0x100 + temp_byte_array[12]) / 10000)
        self.__program_number = temp_byte_array[13]
        self.__formatting_current = float(
            (temp_byte_array[14] * 256 + temp_byte_array[15]) / 10)
        self.__rest_period = temp_byte_array[16] * 256 + temp_byte_array[17]
        self.__charge_flags = temp_byte_array[18]
        self.__pointer_data_record = temp_byte_array[19] * \
            256 + temp_byte_array[20]
        self.__accu_capacity_factor = temp_byte_array[21]

    def pull_current_measured_values(self):
        """Läd die Parameter des übergebenen Ladekanals.

        Läd die dynamischen Parameter und speichert sie in die Objektvariablen
        Es werden Spannung, Strom und Kapazität gelesen.
        Der Ladekanal wird bei der Erzeugung der Instanz übergeben
        """
        temp_byte_array: bytearray
        attempt_count = 0
        channel_instr = bytearray([0x6D, self.__channel_number])

        self.__charge_port.write(trans_by_ar_to_esc_by_ar(channel_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        self.__charge_port.reset_input_buffer()
        self.__charge_port.reset_output_buffer()
        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)
        if (temp_byte_array[2] * 256 + temp_byte_array[2]) != 0xFFFF:
            self.__topical_voltage = float(
                (temp_byte_array[2] * 256 + temp_byte_array[3]) / 1000)
        else:
            self.__topical_voltage = None
        if (temp_byte_array[4] * 256 + temp_byte_array[5]) != 0xFFFF:
            self.__topical_current = float(
                (temp_byte_array[4] * 256 + temp_byte_array[5]) / 10)
        else:
            self.__topical_current = None
        self.__topical_accu_capacity = float(
            (temp_byte_array[6] * 0x1000000 + temp_byte_array[7] * 0x10000 +
             temp_byte_array[8] * 0x100 + temp_byte_array[9]) / 10000)
        attempt_count = attempt_count + 1

    def pull_charge_function(self):
        """Läd die Parameter des übergebenen Ladekanals.

        List den Status des Kanals und speichert sie in die Objektvariablen.
        Der Ladekanal wird bei der Erzeugung der Instanz übergeben
        """
        temp_byte_array: bytearray
        charge_function_str_de = {0: "DE", 1: "Leerlauf", 2: "Pause / Warten",
                                  3: "Entladen", 4: "Erhaltungsladung",
                                  5: "Entladen beendet", 6: "Notabschaltung"}
        charge_function_str_en = {0: "EN", 1: "idel state", 2: "pause / wait",
                                  3: "discharge", 4: "maintenance charging",
                                  5: "discharge end", 6: "emergency cutout"}
        charge_function_str = [charge_function_str_en, charge_function_str_de]
        channel_instr = bytearray([0x61, self.__channel_number])

        self.__charge_port.write(trans_by_ar_to_esc_by_ar(channel_instr))

        temp_byte_array = self.__charge_port.read_until(b'\x03', 20)
        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)

        self.__charge_function = temp_byte_array[1]

        if self.__charge_function >= 0x00 and self.__charge_function <= 0x0A:
            self.__charge_function_str = charge_function_str[1][1]
        elif self.__charge_function >= 0x0B and self.__charge_function <= 0x2D:
            self.__charge_function_str = charge_function_str[1][2]
        elif self.__charge_function >= 0x2E and self.__charge_function <= 0x37:
            self.__charge_function_str = charge_function_str[1][3]
        elif self.__charge_function >= 0x38 and self.__charge_function <= 0x6E:
            self.__charge_function_str = charge_function_str[1][4]
        elif self.__charge_function >= 0x6F and self.__charge_function <= 0xA0:
            self.__charge_function_str = charge_function_str[1][5]
        elif self.__charge_function >= 0xA1 and self.__charge_function <= 0xFF:
            self.__charge_function_str = charge_function_str[1][6]

    def get_topical_voltage(self):
        return self.__topical_voltage

    def get_topical_current(self):
        return self.__topical_current

    def get_topical_accu_capacity(self):
        return self.__topical_accu_capacity

    def get_accu_number(self):
        return self.__accu_number

    def get_charge_current(self):
        return self.__charge_current

    def get_recharge_current(self):
        return self.__recharge_current

    def get_accu_type_description(self):
        return self.__accu_type_description

    def get_cell_count(self):
        return self.__cell_count

    def get_program_number(self):
        return self.__program_number

    def get_formating_current(self):
        return self.__formatting_current

    def get_rest_period(self):
        return self.__rest_period

    def get_charge_flags(self):
        # TODO: Flags seperat auswerten
        return self.__charge_flags

    def get_pointer_data_record(self):
        return self.__pointer_data_record

    def get_accu_capacity_factor(self):
        return self.__accu_capacity_factor

    def get_charge_function(self):
        return self.__charge_function

    def get_charge_function_str(self):
        return self.__charge_function_str


class ChargeDeviceAccuDbEntry():

    def __init__(self, charge_port: serial.Serial, db_entry_number):

        self.__charge_port = charge_port
        self.__db_entry_number = db_entry_number

        self.__blank_db_entry: bool = bool()
        self.__accu_name: str = str()
        self.__db_reread_entry_number: bytes = bytes()
        self.__accu_type: bytes = bytes()
        self.__accu_type_description: str = str()
        self.__accu_cell_count: bytes = bytes()
        self.__accu_capacity: float = float()
        self.__recharge_current: float = float()
        self.__charge_current: float = float()
        self.__rest_period: int = int()
        self.__charge_flags: bytes = bytes()
        self.__functions_flags: bytes = bytes()

    def pull_db_entry(self):
        """Liest einen Akku-Parameter-Datensatz.

        Liest einen Akku-Parameter-Datensatz und scheibt ihn in die
        entsprechenden privaten Variablen
        """
        temp_byte_array: bytearray
        channel_instr = bytearray([0x64, self.__db_entry_number])
        temp_byte_array = trans_by_ar_to_esc_by_ar(channel_instr)
        self.__charge_port.write(trans_by_ar_to_esc_by_ar(channel_instr))
        temp_byte_array = self.__charge_port.read_until(b'\x03', 50)
        temp_byte_array = trans_esc_by_ar_to_clear_by_ar(temp_byte_array)

        self.__accu_name = temp_byte_array[2:11].decode()
        self.__db_reread_entry_number = temp_byte_array[1]
        self.__accu_type = temp_byte_array[11]
        self.__accu_type_description = trans_accu_num_to_str(self.__accu_type)
        if self.__accu_type == 0xFF:
            self.__blank_db_entry = True
        else:
            self.__blank_db_entry = False
        self.__accu_cell_count = temp_byte_array[12]
        self.__accu_capacity = float(
            (temp_byte_array[13] * 0x1000000 + temp_byte_array[14] * 0x10000 +
             temp_byte_array[15] * 0x100 + temp_byte_array[16]) / 10000)
        self.__recharge_current = float(
            (temp_byte_array[17] * 256 + temp_byte_array[18]) / 10)
        self.__charge_current = float(
            (temp_byte_array[19] * 256 + temp_byte_array[20]) / 10)
        self.__rest_period = temp_byte_array[21] * 256 + temp_byte_array[22]
        self.__charge_flags = temp_byte_array[23]
        self.__functions_flags = temp_byte_array[24]

    def get_is_db_entry_blank(self):
        return self.__blank_db_entry

    def get_accu_name(self):
        return self.__accu_name

    def get_accu_typ(self):
        return self.__accu_type

    def get_accu_type_description(self):
        return self.__accu_type_description

    def get_accu_cell_count(self):
        return self.__accu_cell_count

    def get_accu_capacity(self):
        return self.__accu_capacity

    def get_recharge_current(self):
        return self.__recharge_current

    def get_charge_current(self):
        return self.__charge_current

    def get_rest_period(self):
        return self.__rest_period

    def get_charge_flags(self):
        return self.__charge_flags

    def get_functions_flags(self):
        return self.__functions_flags


if __name__ == "__main__":

    charge_device = charge_devices_alc_generic("COM4")
    charge_device.set_ver_ser_num(charge_device.pull_ver_ser_num())
    charge_device.pull_temperatures()

    charge_cannel = ChargeDeviceAlcChannel(charge_device.get_charge_port(), 0)
    charge_cannel.pull_current_cannel_data()
    charge_cannel.pull_current_measured_values()
    charge_cannel.pull_charge_function()
    charge_db_entry = ChargeDeviceAccuDbEntry(
        charge_device.get_charge_port(), 0x05)
    charge_db_entry.pull_db_entry()

    print(charge_device.get_ser_num())
    print(charge_device.get_device_type_long())
    print(charge_device.get_device_type_short())
    print(charge_device.get_device_sw_version())
    print(charge_cannel.get_charge_function_str())
    print(charge_device.get_main_temperature(), "°C")

    print(charge_db_entry.get_accu_name())
    print(charge_db_entry.get_accu_typ())
    print(charge_db_entry.get_accu_cell_count())
    print(charge_db_entry.get_charge_current())
