"""Programm zu steuern eines ELV-ALCs.

folgende Optionen können genutzt werde:

-h, --help: Hilfehinweise ausgeben
-s, --search: Sucht nach Geräte von ELV und gib die Liste aus
-d x, --device x: Steuert das Gerät mit der Nummer x, typische bei einem Gerät
 ist die "1"
-l, --list: Gibt die Parameter des genannten Gerätes aus
-c x, --channel x Gibt die Paramerter des entsprechenden Kanals aus
-a, --accudb: Liste mit den Akkuprofilen
-b x, --dbentry: Der komplette Profil- Datensatz
*-j, --json: Ausgabe der Daten im JSON-Format
"""
# TODO: Implementierung der JSON-Ausgabe
import argparse

from simple_help_func import is_found_dev_a_alc, search_elv_device
from charge_alc_bib import charge_devices_alc_generic
from charge_alc_bib import ChargeDeviceALC3000
from charge_alc_bib import ChargeDeviceAccuDbEntry

if __name__ == "__main__":

    device_number = 1
    charge_db_entry = []
    temp_flag_name = [None] * 2
    temp_flag_status = [None] * 2
    device_list = search_elv_device()
#    print(device_list)
#    if device_list is not None:
#        print("COM-Port: ", device_list[0][0], "; Beschreibung: ",
#              device_list[1][0], ";")
#    else:
#        print("Kein ELV-Device gefunden!")

    parse_instance = argparse.ArgumentParser(
        description="Steuert ELV-Ladegeräte")
    parse_instance.add_argument("-s", "--search", action='store_true',
                                help="Sucht Ladegeräte und gibt erste Werte")
    parse_instance.add_argument("-d", "--device", type=int,
                                help="""Das zu steuernde Gerät.
                                 Siehe Such-Liste""")
    parse_instance.add_argument("-l", "--list", action='store_true',
                                help="Wesendliche Parameter, des Gerätes")
    parse_instance.add_argument("-c", "--channel", type=int,
                                help="""Gibt die Parameter des entsprechenden
                                 Kanals""")
    parse_instance.add_argument("-a", "--accudb", action='store_true',
                                help="""Gibt die Datenbank mit den Akuprofilen
                                 aus""") 
    parse_instance.add_argument("-b", "--dbentry", type=int,
                                help="""Gibt die Parameter des entsprechenden
                                 AkkuDB-Eintrages aus""")
    parse_args = parse_instance.parse_args()
    print(parse_args)

    if parse_args.search is True:
        if device_list is not None:
            for i in range(0, device_list[0].__len__()):
                print(f'{i+1}. Port: {device_list[0][i]}; ',
                      f'Portname: {device_list[1][i]}')
        else:
            print("No ELV device found.")
    elif parse_args.device:
        device_number = parse_args.device
        print(device_number)
    elif parse_args.list:
        if device_list is not None:
            if is_found_dev_a_alc(device_list[0][device_number-1]):
                charge_device = charge_devices_alc_generic(device_list[0]
                                                           [device_number-1])
                charge_device.pull_ver_ser_num()
                charge_device.pull_temperatures()
                temp_dev_typ = charge_device.get_device_type_long()
                temp_sn = charge_device.get_ser_num()
                temp_cooler_temp = charge_device.get_main_temperature()
                temp_cooler_temp = str(temp_cooler_temp)+"°C"
                temp_power_temp = charge_device.get_power_sup_temperature()
                if temp_power_temp is not None:
                    temp_power_temp = str(temp_cooler_temp)+"°C"
                else:
                    temp_power_temp = "N/A"
                temp_accu_temp = charge_device.get_accu_temperature()
                if temp_accu_temp is not None:
                    temp_accu_temp = str(temp_cooler_temp)+"°C"
                else:
                    temp_accu_temp = "N/A"
                print("{:<30} {:<14} {:<8} {:<8} {:<8}".format("Typ", "Seriennummer", "Temp. 1", "Temp.2", "Temp. Akku"))
                print("{:<30} {:<14} {:<8} {:<8} {:<8}".format(temp_dev_typ, temp_sn, temp_cooler_temp, temp_power_temp, temp_accu_temp))
            else:
                print("Das Gerät ist kein Lagegerät oder ist nicht angeschaltet.")
        else:
            print("No ELV device found.")
    elif parse_args.channel:
        if device_list is not None:
            if is_found_dev_a_alc(device_list[0][device_number-1]):
                charge_device = charge_devices_alc_generic(device_list[0]
                                                           [device_number-1])
                charge_device.pull_ver_ser_num()
                if charge_device.get_device_type_int() == 103:
                    del charge_device
                    charge_device_3000 = ChargeDeviceALC3000(device_list[0]
                                                             [device_number-1])
                    print("Parameter des Kanals: ", parse_args.channel)
                    print(20*"####")
                    print("{:<16} {:<13} {:<14} {:<10}".format("Programmnummer: ", 
                          charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_program_number(),
                          "Programmname: ",
                          charge_device_3000.charge_db_entry[charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_program_number()].get_accu_type_description()))
                    print("{:<16} {:<13} {:<14} {:<10}".format("Akkutyp: ",
                          charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_accu_type_description(),
                          "Zellenanzahl: ",
                          charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_cell_count()))
                    print("{:<16} {:<13}".format("Akkukapazität: ", str(
                          charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_accu_capacity())+" mA/h"))
                    print("{:<16} {:<13} {:<14} {:<10}".format("Entladestrom: ", str(
                          charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_charge_current())+" mA",
                          "Ladestrom: ", str(
                          charge_device_3000.charge_cannel_ins[parse_args.channel-1].get_recharge_current())+" mA"))
            else:
                print("Das Gerät ist kein Lagegerät oder ist nicht angeschaltet.")
        else:
            print("No ELV device found.")
    elif parse_args.accudb:
        if device_list is not None:
            if is_found_dev_a_alc(device_list[0][device_number-1]):
                charge_device = charge_devices_alc_generic(device_list[0]
                                                           [device_number-1])
                for i in range(charge_device.accu_db_items):
                    charge_db_entry.append(ChargeDeviceAccuDbEntry(
                        charge_device.get_charge_port(), i))
                    charge_db_entry[i].pull_db_entry()
                print(charge_db_entry[0].get_accu_name())
                print("{:<3} {:<11} {:<7} {:<6} {:<10} {:<10} {:<13} {:<8}".format(
                      "DB#", "Name", "Anzahl", "Typ", "Kapazität",
                      "Ladestrom", "Entladestrom", "Pause"))
                print(20*"####")
                for j in charge_db_entry:
                    if j.get_is_db_entry_blank():
                        print(j.get_db_reread_entry_number(), " N/A.")
                    else:
                        print("{:<3} {:<11} {:<7} {:<6} {:<10} {:<10} {:<13} {:<8}".format(
                              j.get_db_reread_entry_number()+1,
                              j.get_accu_name(), j.get_accu_cell_count(),
                              j.get_accu_type_description(),
                              str("{:.0f}".format(j.get_accu_capacity()))+" mA/h",
                              str("{:.0f}".format(j.get_charge_current()))+" mA",
                              str("{:.0f}".format(j.get_recharge_current()))+" mA",
                              str(j.get_rest_period())+" s"
                              ))
            else:
                print("Das Gerät ist kein Lagegerät oder ist nicht angeschaltet.")
        else:
            print("No ELV device found.")
    elif parse_args.dbentry:
        if device_list is not None:
            if is_found_dev_a_alc(device_list[0][device_number-1]):
                charge_device = charge_devices_alc_generic(device_list[0]
                                                           [device_number-1])
                accu_db_entry = ChargeDeviceAccuDbEntry(charge_device.get_charge_port(), parse_args.dbentry-1)
                accu_db_entry.pull_db_entry()
                if accu_db_entry.get_charge_factor():
                    temp_charge_factor = str(accu_db_entry.get_charge_factor())+" %"
                else:
                    temp_charge_factor = "N/A"
                print("Parameter des Akku-DB-Eintrages: ", parse_args.dbentry)
                print(20*"####")
                print("{:<14} {:<13} {:<12} {:<10}".format("Akkuname: ",
                      accu_db_entry.get_accu_name(),
                        "Typ: ",
                        accu_db_entry.get_accu_type_description()))
                print("{:<14} {:<13} {:<12} {:<10}".format("Zellenanzahl: ",
                      str(accu_db_entry.get_accu_cell_count()),
                      "Kapazität: ",
                      str(accu_db_entry.get_accu_capacity())+" mA/h"))
                print("{:<14} {:<13} {:<12} {:<10}".format("Laden: ", str(
                      accu_db_entry.get_charge_current())+" mA",
                      "Entladen: ",
                      str(accu_db_entry.get_recharge_current())+" mA"))
                print("{:<14} {:<13} {:<14} {:<10}".format("Pause: ",
                      str(accu_db_entry.get_rest_period())+" s",
                        "Temp. erforderlich: ", "nein"))
                print("{:<14} {:<13}".format("Ladefaktor: ", temp_charge_factor))
                print("\nFreigegebene Funktionen")
                print(20*"----")
                print(accu_db_entry.get_func_flags_dict()[1])
                i = 0
                temp_flags_dict = accu_db_entry.get_func_flags_dict()[1]
                for flag_entry in temp_flags_dict:
                    temp_flag_name[i] = flag_entry
                    temp_flag_status[i] = temp_flags_dict[flag_entry]
                    i += 1
                    if i >= 2:
                        print("{:<18} {:<7} {:<16} {:<5}".format(
                              temp_flag_name[0]+" :", temp_flag_status[0],
                              temp_flag_name[1]+" :", temp_flag_status[1]))
                        i = 0
            else:
                print("Das Gerät ist kein Lagegerät oder ist nicht angeschaltet.")
        else:
            print("No ELV device found.")

#    charge_device = charge_devices_alc_generic(device_list[0][0])
#    charge_device.pull_ver_ser_num()

#    print(charge_device.get_ser_num())
