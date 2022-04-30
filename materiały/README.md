# Serwis BragerConnect

Serwis BragerConnect znajduje się pod adresem https://cloud.bragerconnect.com

# Komunikacja z serwisem BragerConnect

Komunikacja z serwisem BragerConnect realizowana jest za pomocą protokołu WebSocket.

Po połączeniu z adresem wss://cloud.bragerconnect.com serwis celem potwierdzenia połączenia wysyła:

{"wrkfnc":true,"type":10,"name":null,"args":null}

Należy odpowiedzieć (wysłać) dokładnie ten sam komunikat.
Następnie trzeba się zakogować do serwisu.

## Struktura poleceń

Znaczenie składowych poleceń:

"wrkfnc": true
- jest to potwierdzenie, że wysyłany (odbierany) komunikat należy przetwarzać, każdy komunikat zawiera tę pozycję
"type": num
- jest to typ polecenia, typ może mieć wartość:
* 1: żądanie wykonania procedury (nic nie zwraca)
* 2: żądanie wykonania funkcji
ten typ polecenia zawiera rónież
* * "nr" -- numer żądania wysyłany przy komunikacie, odpowiedź zawiera ten sam numer
* * "name" -- nazwa funkcji
* * "args" -- argumenty funkcji
* 10: sygnał gotowości
* * zawiera argumanty "name" i "resp" o wartości null
* 12: wynik działania funkcji
* * "nr" -- wynik funkcji dla rządania o tym samym numerze
* * "resp" -- odpowidż funkcji
* 20: wyjątek (błąd)
* * resp 2 -- niepoprawny login lub hasło
* 21: message port?? -- nie wiem co to jest

## Logowanie

Aby zalogować się, należy wysłać komunikat o treści:

{"wrkfnc":true,"type":2,"name":"s_login","nr":0,"args":["<login>","<hasło>",null,null,"bc_web"]}

podając:

<login> - nazwę użytkownika

<hasło> - hasło

# Komponent do Hone Assistant
