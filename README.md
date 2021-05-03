Delta õppehoonele loodud ingliskeelse juturoboti lähtekood.

Rasa dokumentatsioon on leitav [siit](https://rasa.com/docs/rasa/).

Systemd teenuste dokumentatsioon on leitav [siit](http://manpages.ubuntu.com/manpages/cosmic/man5/systemd.service.5.html).

## **Paigaldusjuhis**

Eeldused:
* UNIX-tüüpi operatsioonisüsteem (arendatud Ubuntu 18.04 kasutades)
* Python 3.7.10 virtuaalkeskkond (näiteks paketi _virtualenv_ abil)

### **Juturoboti kiirkäivitus**

Juturobotiga käsureal vestlemiseks läbi järgnevad sammud:

1. Liigu lähtekoodi asukohta (kaust Delta/).
2. Käivita vajalike pakettide installimine käsuga "pip install -r requirements.txt".
3. Loo _auxiliary/delta_backup.sql_ abil PostgreSQL andmebaas ja muuda vajadusel _actions.actions.py_ alguses asuvaid
andmebaasiligipääsu parameetreid.
4. Käivita Rasa Action Server käsuga "rasa run actions".
5. Käivita juturobot käsureal käsuga "rasa shell".

Käsureavestlusest väljumiseks kasuta klahvikombinatsiooni Ctrl+C.

### **Juturoboti täielik käivitus**

Juturoboti alaliselt veebile avamiseks läbi järgnevad sammud: 

1. Soorita kiirkäivituse sammud 1-3.
2. VALIKULINE: uuenda andmebaasi seis kaustas _auxiliary/crons/_ asuvate skriptide käivitamisega, parandades vajadusel 
skriptide alguses olevaid parameetreid andmebaasiligipääsu ja vaatlusaja osas.
3. Sea üles Nginx server, kasutades konfiguratsiooni _auxiliary/rasa.conf_. Vajadusel paranda konfiguratsioonifailis
muutuja _root_ väärtus selliseks, et see osutaks faili _front.html_ asukohale.
4. Paiguta kaustas _auxiliary/services/_ olevad failid kausta _/etc/systemd/service/_, parandades vajadusel
nendes kirjeldatud kaustade asukohad.
5. Käivita süsteemiteenused järgnevate käskudega:
    1. _service rasa-actions start_
    2. _service rasa-core start_
    3. _service rasa-logger start_

Süsteemiteenuste sulgemiseks kasuta käsku _service rasa-* stop_.