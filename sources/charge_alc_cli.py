"""Programm zu steuern eines ELV-ALCs.

folgende Optionen können genutzt werde:

-h, --help: Hilfehinweise ausgeben
-s, --search: Sucht nach Geräte von ELV und gib die Liste aus
-d x, --device x: Steuert das Gerät mit der Nummer x, typische bei einem Gerät
 ist die "1"
-l, --list: Gibt die Parameter des genannten Gerätes aus
"""
import argparse

from simple_help_func import is_found_dev_a_alc, search_elv_device
from charge_alc_bib import charge_devices_alc_generic

if __name__ == "__main__":

    device_number = 1

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
                print("{:<30} {:<14}".format("Typ", "Seriennummer"))
                print("{:<30} {:<14}".format(temp_dev_typ, temp_sn))
            else:
                print("Das Gerät ist kein Lagegerät oder ist nicht angeschaltet.")
        else:
            print("No ELV device found.")

"""
    print(sys.argv[1:])
    opts, args = getopt.getopt(sys.argv[1:], ":hsd=v", ["help", "search",
     "device="])
    print("Optionen:", opts, ":", args)
    for prog_opt, opt_para in opts:
        print("Optionen2:", prog_opt, ":", opt_para)
        if (prog_opt == "-h") or (prog_opt == "--help"):
            pass
        elif (prog_opt == "-s") or (prog_opt == "--search"):
            device_list = search_elv_device()
            if device_list is not None:
                for i in range(0, device_list[0].__len__()):
                    print(i+1, ". Port", device_list[0][i], "Portname: ",
                        device_list[1][i])
            else:
                print("No ELV device found.")
"""
#    charge_device = charge_devices_alc_generic(device_list[0][0])
#    charge_device.pull_ver_ser_num()

#    print(charge_device.get_ser_num())
