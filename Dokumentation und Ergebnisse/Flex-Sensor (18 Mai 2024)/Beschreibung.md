Dieses Video zeigt den ersten Fortschritt, der in direktem Zusammenhang mit dieser Arbeit steht. Nach dem ersten Treffen mit der Betreuungsperson am 18.03.2024 begann die Recherche mit dem Thema.

Mithilfe eines Arduino wurde der grundlegende Aufbau eines Stromkreises und der Einsatz eines Flex-Sensors anschaulich demonstriert. Zur Ansteuerung des Arduino kommt die Bibliothek PyFirmata zum Einsatz, die Python-Befehle in C++-Code für den Arduino übersetzt.

Das Programm umfasst zwei Schaltkreise:

Spannungsteiler – Hier wird die Spannung des Flex-Sensors gemessen und ausgewertet.
LED-Schaltkreis – Der ausgelesene Wert steuert die Helligkeit der LED, sodass diese gedimmt werden kann.

Ein Problem tritt auf, wenn der Flex-Sensor zu stark gebogen wird: Die LED erreicht ihre maximale Leuchtstärke und kann dann nicht weiter abgedunkelt werden. Sobald dies geschieht, leuchtet die Lampe erneut auf. Dieses Problem wurde in der Arbeit bei der Entwicklung der Motorwerteskala behoben.
