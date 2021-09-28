Delta õppehoonele loodud ingliskeelse juturoboti lähtekood.

Rasa dokumentatsioon on leitav [siit](https://rasa.com/docs/rasa/).

Systemd teenuste dokumentatsioon on leitav [siit](http://manpages.ubuntu.com/manpages/cosmic/man5/systemd.service.5.html).

PostgreSQLi dokumentatsioon on leitav [siit](https://www.postgresql.org/docs/).

## **Paigaldusjuhis**

Eeldused:
* LINUX-tüüpi operatsioonisüsteem (arendatud Ubuntu 18.04 kasutades)
* Python 3.7.10 virtuaalkeskkond (näiteks paketi _virtualenv_ abil)

### **Juturoboti kiirkäivitus**

Juturobotiga käsureal vestlemiseks läbi järgnevad sammud:

1. Liigu lähtekoodi juurkausta _Delta/_.
2. Käivita vajalike pakettide installimine käsuga "pip install -r requirements.txt".
3. Loo andmebaasi koopia _auxiliary/delta_backup.sql_ abil PostgreSQL andmebaas ja muuda vajadusel _actions.actions.py_
alguses asuvaid andmebaasiligipääsu parameetreid.
4. Loo juturoboti andmetabelid ja uuenda andmebaasi seis kaustas _auxiliary/crons/_ asuvate skriptide käivitamisega,
parandades vajadusel skriptide alguses olevaid parameetreid andmebaasiligipääsu ja vaatlusaja osas.
5. Naase projekti juurkausta _Delta/_ ja treeni juturoboti mudel käsuga "rasa train"
6. Käivita Rasa Action Server käsuga "rasa run actions".
7. Käivita juturobot käsureal käsuga "rasa shell".

Käsureavestlusest väljumiseks kasuta klahvikombinatsiooni Ctrl+C.

### **Juturoboti täielik käivitus**

Juturoboti alaliselt veebile avamiseks läbi järgnevad sammud: 

1. Soorita kiirkäivituse sammud 1-5.
2. Sea üles Nginx server, kasutades konfiguratsiooni _auxiliary/rasa.conf_. Vajadusel paranda konfiguratsioonifailis
muutuja _root_ väärtus selliseks, et see osutaks faili _front.html_ asukohale.
3. Paiguta kaustas _auxiliary/services/_ olevad failid kausta _/etc/systemd/system/_, parandades vajadusel
nendes kirjeldatud kaustade asukohad.
4. Käivita süsteemiteenused järgnevate käskudega:
    1. "service rasa-actions start"
    2. "service rasa-core start"
    3. "service rasa-logger start"

Süsteemiteenuste sulgemiseks kasuta käsku "service rasa-* stop"
