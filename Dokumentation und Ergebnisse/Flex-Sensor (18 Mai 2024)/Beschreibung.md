Dieses Video zeigt den ersten Fortschritt, der in direktem Zusammenhang mit dieser Arbeit steht. Nach dem ersten Treffen mit der Betreuungsperson (18.3.2024) wurde mit recherchierung angefangen.

Mithilfe eines Arduino wird der grundlegende Aufbau eines Stromkreises und der Einsatz eines Flex-Sensors anschaulich demonstriert. Zur Ansteuerung des Arduino kommt die Bibliothek PyFirmata zum Einsatz, die Python-Befehle in C++-Code für den Arduino übersetzt.

Das Programm umfasst zwei Schaltkreise:
Spannungsteiler – Hier wird die Spannung des Flex-Sensors gemessen und ausgewertet.
LED-Schaltkreis – Der ausgelesene Wert steuert die Helligkeit der LED, sodass diese gedimmt werden kann.

Ein auftretendes Problem besteht darin, dass bei zu starker Biegung des Flex-Sensors die LED ihre maximale Leuchtstärke erreicht und nicht mehr weiter abgedunkelt werden kann. Sobald das passiert, leuchtet die Lampe wieder auf. Dieses Problem wurde in der Arbeit bei der Motorwerteskala behoben.
