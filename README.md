# Charge-ALC
alternative software for controlling the ELV-ALC series. It is implemented in Python.

Projektstatus:  :construction_worker:<p>
Lesen von Geräteparameter: 80%

# Beschreibung der CLI-Programm-Version

folgende Optionen können genutzt werde:

+ -h, --help: Hilfehinweise ausgeben<p>
+ -s, --search: Sucht nach Geräte von ELV und gib die Liste aus<p>
+ -d x, --device x: Steuert das Gerät mit der Nummer x, typische bei einem Gerät
 ist die "1"<p>
+ -l, --list: Gibt die Parameter des genannten Gerätes aus<p>
+ -c x, --channel x Gibt die Paramerter des entsprechenden Kanals aus<p>
+ -a, --accudb: Liste mit den Akkuprofilen<p>
+ -b x, --dbentry: Der komplette Profil- Datensatz<p>
+ -m, --measurement: Gibt die Messwerte des entsprechenden Kanals aus<p>
+ -q, --continuous: Gibt die Messwerte alle 5s Sekunden aus. Das Programm wird mit "q" beendet.<p>

