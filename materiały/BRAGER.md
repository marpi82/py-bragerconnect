# Komunikacja z serwisem BragerConnect

Komunikacja z serwisem BragerConnect realizowana jest za pomocą protokołu WebSocket, wszystkie dane - zarówno te wysyłane, jak i odbierane - sformatowane są w JSON.

Adres serwera WebSocket: wss://cloud.bragerconnect.com

## Składnia poleceń

Każde polecenie zawiera na początku `"wrkfnc": true`, co oznacza, że odebrane/wysłane dane powinny być przetwarzane.

Następnie mogą to być:

- `"type": [numer]`

  Jest to typ polecenia, typ może mieć wartość:
  - 1:  żądanie wykonania procedury (nic nie zwraca)
  - 2:  żądanie wykonania funkcji
  - 10: sygnał gotowości
  - 12: wynik działania funkcji
  - 20: wyjątek (błąd)
  - 21: komunikat - *nie wiem co to jest*

- `"name": [tekst]`

  Jest to nazwa funkcji/procedury do wykonania

- `"nr": [numer]`

  Pojawia się w przypadku żądania wykonania funkcji, tym samym umerem opatrzona jest odpowiedź serwera w odpowiedzi na wysłane żądanie.

- `"args": [lista]`

  Jest to lista argumentów potrzebnych wykonania procedury lub funkcji.

- `resp: [różne typy]`

  Jest to odpowiedź serwera na wysłane żądanie, może być numerem, listą, słownikiem, pustym typem

**Przykłady poleceń:**

```json
{"wrkfnc":true,"type":1,"name":"taskListChanged","args":["FTTCTBSLCE"]}
{"wrkfnc":true,"type":2,"name":"s_login","nr":0,"args":["<login>","<hasło>",null,null,"bc_web"]}
{"wrkfnc":true,"type":10,"name":null,"args":null}
{"wrkfnc":true,"type":12,"nr":736,"resp":0}
{"wrkfnc":true,"type":20,"nr":0,"resp":2}
```

## Rozpoczęcie transmisji

Po połączeniu z WebSocket, serwer wysyła sygnał gotowości `{"wrkfnc":true,"type":10,"name":null,"args":null}`, należy odpowiedzieć tym samym poleceniem. Oznacza to poprawne rozpoczęcie transmisji i potwierdzenie gotowości rozpoczęcia transmisji.

## Logowanie

Aby zalogować się, należy wysłać polecenie o składni:

```json
{"wrkfnc":true,"type":2,"name":"s_login","nr":0,"args":["<login>","<hasło>",null,null,"bc_web"]}`
```

podając:
***nr*** - jest kolejnym numerem, pierwszy komunikat to nr=0,
***login*** - nazwę użytkownika oraz
***hasło***.

Serwer odpowiada:

```jsonc
{"wrkfnc":true,"type":20,"nr":0,"resp":2} // w przypadku błądnego logowania
{"wrkfnc":true,"type":12,"nr":0,"resp":1} // w przypadku poprawnego logowania
```

**Po poprawnym zalogowaniu serwer przyjmuje inne polecenia, oraz w przypadku zmiany jakiegoś parametru (po stronie serwera, również bez naszej ingerencji) - od razu - wysyła komunikat zawierający zmianę.**

## Inne polecenia (skupię się jedynie na "potrzebnych")

### Pobieranie listy dostępnych na koncie użytkownika urządzeń

```jsonc
{"wrkfnc":true,"type":2,"name":"s_getMyDevIdList","nr":6,"args":[]}  // polecenie

{"wrkfnc":true,"type":12,"nr":6,"resp":  // odpowiedź
    [
        {
            "username":"marpi82",  // nazwa zalogowanego użytkownika
            "sharedfrom_name":null,
            "devid":"FTTCTBSLCE",  // identyfikator urządzenia
            "distr_group":"ht",  // dystrybutor urządzenia
            "id_perm_group":1,
            "permissions_enabled":1,
            "permissions_time_start":null,
            "permissions_time_end":null,
            "accepted":1,
            "verified":1,
            "name":"",
            "description":"",
            "producer_permissions":2,
            "producer_code":"67",
            "warranty_void":null,
            "last_activity_time":2,
            "alert":false
        }
    ]
}
```

tu jedno urządzenie, jeśli było by więcej, wtedy dodana zostanie kolejna pozycja listy (założenie, nie miałem jak sprawdzić)

### Ustawienie identyfikatora urządzenia, którego chcemy aby dotyczyły wysyłane przez nas polecenia

```jsonc
{"wrkfnc":true,"type":2,"name":"s_setActiveDevid","nr":15,"args":["FTTCTBSLCE"]} // polecenie

{"wrkfnc":true,"type":12,"nr":15,"resp":true} // odpowiedź
```

### Pobranie identyfikatora urządzenia, którego dotyczyczą wysyłane przez nas polecenia

```jsonc
{"wrkfnc":true,"type":2,"name":"s_getActiveDevid","nr":10,"args":[]} // polecenie

{"wrkfnc":true,"type":12,"nr":10,"resp":"FTTCTBSLCE"} // odpowiedź
```

### Pobieranie "puli parametrów"

```json
{"wrkfnc":true,"type":2,"name":"s_getAllPoolData","nr":7,"args":[]}
```

W odpowiedzi dostajemy słownik zawierający wszystkie parametry pracy urządzenia (kotła C.O.). Tu wersja skrócona, całość parametrów mojego kotła można zobaczyć [tutaj](parametry.json)

```json
{
    "P4": {
        "v0": 65.5, "u0": 1, "s0": 0,
        "v1": 58.5, "u1": 1, "s1": 0,
        "v2": 45.5, "u2": 1, "s2": 0,
        "v3": 31,   "u3": 1, "s3": 6,
        "v4": 0,    "u4": 1, "s4": 0,
        "v5": 51.5, "u5": 1, "s5": 0
    },
    "P5": {
        "s0": 1,
        "s1": 0,
        "s2": 0,
        "s3": 4,
        "s4": 7,
        "s5": 8960
    },
    "P6": {
        "v0": 73, "n0": 60, "x0": 87, "u0": 1, "s0": 64,
        "v1": 55, "n1": 55, "x1": 70, "u1": 1, "s1": 0,
        "v2": 0,  "n2": 0,  "x2": 1,  "u2": 6, "s2": 67,
        "v3": 5,  "n3": 5,  "x3": 20, "u3": 2, "s3": 3
    },
    "P7": {
        "v2": 0,
        "s2": 67,
        "v3": 0,
    },
    "P8": {
        "v0": 0, "s0": 0,
        "v1": 1, "s1": 0,
        "v2": 2, "s2": 0
    },
    "P10": {
        "v2": 333, "n2": 259, "x2": 370, "u2": 49, "s2": 64,
        "v4": 111, "n4": 111, "x4": 185, "u4": 49, "s4": 67
    },
    "P11": {
        "v1": "Z.HT900T v2.5.25 Apr 26 2021", "s1": 0,
        "v4": "DasPell GL 37 V1+",            "s4": 64,
        "v5": "HT Connect V2.08 Sep 24 2020", "s5": 0,
        "v6": "ID ETH: FTTCTBSLCE",           "s6": 0
    },
    "P12": {
        "a4": 0, "b4": 0, "c4": 0, "d4": 0, "e4": 0, "f4": 0, "g4": 0, "h4": 0, "i4": 0, "n4": -10, "x4": 10, "u4": 1, "s4": 3,
        "a5": 0, "b5": 0, "c5": 0, "d5": 0, "e5": 0, "f5": 0, "g5": 0, "h5": 0, "i5": 0, "n5": -10, "x5": 10, "u5": 1, "s5": 3
    }
}
```

#### Co wiem odnośnie puli parametrów

Numery przy literach to numery parametrów, np. v1, s1, u1 dotyczą parametru numer 1

Litery przy numerach parametrów to:

***v*** -- value (wartość parametru)

***u*** -- unit (jednostka miary parametru, wg. danych z [pliku](pl_units.json), niektóre jednostki reprezentowane są jako pola wyboru z listy)
***s*** -- status (status w formie bitowej)

***n*** -- min (minimalna wartość możliwa do ustawienia w polu ***v***)

***x*** -- max (maksymalna wartość możliwa do ustawienia w polu ***v***)

***a, b, c, d, e, f, g, h, i*** -- są używane w termostacie, ale dokładnie musiał bym sprawdzić która litera za co odpowiadała, siedem z nich to najprawdopodobniej dni tygodnia.

- Pula P4 - pula zawiera wartości z czujników kotła
- Pula P5 - pula zawiera statusy pracy urządzeń kotła (pompy, dmuchawy, podajniki) jak i samego kotła
- Pula P6 - pula zawiera głowne parametry pracy kotła (nastawy)
- Pula P7 - pula zawiera, nie wiem co :)
- Pula P8 - pula zawiera jakieś dane odnośnie haseł i logowania w sterowniku kotła
- Pula P10 - pula zawiera parametry (nastawy) pracy palnika pelletu
- Pula P11 - pula zawiera dane odnośnie hardware'u i software'u urządzeń
- Pula P12 - pula zawiera parametry (nastawy) termostatów

Opisy parametrów z puli P6 i P10 znajdują się w [pliku](pl_pools.json)

### Pobranie "listy zadań"

```jsonc
{"wrkfnc":true,"type":2,"name":"s_getTaskQueue","nr":18,"args":[]} // polecenie

{"wrkfnc":true,"type":12,"nr":22,"resp":  // odpowiedź
    [
        {
            "id": 238666,
            "module_id": 4563,
            "type": "A",
            "state": 4,
            "result_sent": 1,
            "user_owner": "marpi82",
            "producerApp": 0,
            "create_timestamp": 1642236055288,
            "start_timestamp": 1642236055643,
            "end_timestamp": 1642236059662,
            "end_cause": 0,
            "nr": "0",
            "value": "74",
            "name": "",
            "started_at": "2022-01-15T08:40:55.643Z",
            "finished_at": "2022-01-15T08:40:59.662Z",
            "created_at": "2022-01-15T08:40:55.288Z",
            "updated_at": "2022-01-15T08:40:59.662Z"
        }, {...}
    ]
}
```

### Pobranie "listy alarmów"

```jsonc
{"wrkfnc":true,"type":2,"name":"s_getAlarmListExtended","nr":22,"args":[]} // polecenie

{"wrkfnc":true,"type":12,"nr":22,"resp":[]} // odpowiedź gdy nie występuje alarm

{"wrkfnc":true,"type":12,"nr":22,"resp":   // lista alarmów gdy występują
    [
        {
            "name": "ERROR_BRAK_PALIWA",
            "value": true,
            "timestamp":1647509573
        }, {...}
    ]
}
```

### Ustawienie parametru w "puli"

```jsonc
// polecenie zmiany w puili 6, parametru 0, na wartość 74
{"wrkfnc":true,"type":2,"name":"s_setPoolParam","nr":736,"args":[6,0,74]}

// najpierw otrzymujemy potwierdzenie wykonania polecenia
{"wrkfnc":true,"type":12,"nr":736,"resp":22} // 22 jest to numer serwerowego tasku

// póżniej przychodzi powiadomienie, że zmienia się lista tasków (zadanie zmiany parametru jest w trakcie)
{"wrkfnc":true,"type":1,"name":"taskListChanged","args":["FTTCTBSLCE"]}
// więc dobrze było by ją pobrać uaktualnioną

// wysyłamy żądanie pobrania listy
{"wrkfnc":true,"type":2,"name":"s_getTaskQueue","nr":739,"args":[]}

// otrzymujemy odpowiedź
{"wrkfnc":true,"type":12,"nr":739,"resp":[{...}]}

// serwer wysyła potwierdzenie wykonania zadania
{"wrkfnc":true,"type":1,"name":"taskSuccessConfirmation","args":[22,"FTTCTBSLCE"]}
// pierwszy argument, czyli numer 22, to numer tasku serwera (czyli powyższego zadania)

// znowu uaktualnia się lista tasków
{"wrkfnc":true,"type":1,"name":"taskListChanged","args":["FTTCTBSLCE"]}

// i znów wypada ją pobrać...
{"wrkfnc":true,"type":2,"name":"s_getTaskQueue","nr":758,"args":[]}

// otrzymujemy odpowiedź
{"wrkfnc":true,"type":12,"nr":758,"resp":[{...}]}
```

### Polecenia (powiadomienia) które wysyła serwer WebSocket

Te komunikaty/polecenia pojawiają się w razie wystąpienia aktualizacji jakichś danych w sterowniku kotła (np. zmiana temperatury kotła, wystąpienie alarmu itp.)

#### Zmiana w "puli"

```json
{"wrkfnc":true,"type":1,"name":"poolDataChanged","args":
    [
        [
            {
                "pool":"P4",
                "field":"v1",
                "value":58
            },
            {
                "pool":"P4",
                "field":"v24",
                "value":231
            }
        ],
        "FTTCTBSLCE"
    ]
}
```

Oznacza to po prostu tyle, że w puli P4 dla urządzenia FTTCTBSLCE zmieniły się parametry v1 i v24 na podaną wartość 'value'

#### Zmiana (wystąpienie) alarmu

```json
TODO
```

#### Gdy nastąpiła zmiana na liście "task'ów"

```json
{"wrkfnc":true,"type":1,"name":"taskListChanged","args":["FTTCTBSLCE"]}
```

#### Potwierdzenie wykonania zadania

Zadanie nr 22 dla urządzenia FTTCTBSLCE zostało wykonane

```json
{"wrkfnc":true,"type":1,"name":"taskSuccessConfirmation","args":[22,"FTTCTBSLCE"]}
```
