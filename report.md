Zadaniem projektu jest stworzenie rankingu różnych scenariuszy zarządzania odpadami radioaktywnymi z wykorzystaniem odpornej regresji porządkowej. Będziemy bazować na zbiorze danych opisanym w pracy "Nuclear waste management: an application of the multicriteria PROMETHEE methods".

## Zadanie (3)

### Opis preferencji
Grupa 2
* W skutek wyczerpywania się złóż materiałów radioaktywnych, elektrownie mogą zacząć korzystać z bardziej ubogich złóż, co przełoży się na zwiększenie ilości odpadów radioaktywnych.

Grupa 4
* Grupa zawiera ostrożnego inwestora, który nie chce ryzykować.

### Wybrane pary wariantów referencyjncyh
|Lp. | Wariant 1 | Wariant 2|
|-|---|---|
|1.|0|4|
|2.|10|23|
|3.|2|6|
|4.|13|26|
|5.|21|22|


### Opis wariantów

* S1: Zakłada 10-letnie przechowywanie ILW i 30-letnie przechowywanie HLW.
* S2: Oba typy odpadów, ILW i HLW, są przechowywane przez 30 lat.
* S3: Przedłuża czas przechowywania do 50 lat zarówno dla ILW, jak i HLW

* F1 (metoda opłaty kWh): Opiera się na opłatach za każdy wyprodukowany kWh energii jądrowej, zbieranych w ciągu pierwszych 30 lat. Środki te mogą być akumulowane w funduszu powierniczym, generując odsetki na przyszłe wydatki.
* F2 (metoda prorata): Zakłada nieograniczoną odpowiedzialność producenta odpadów, który pokrywa wszystkie koszty związane z kondycjonowaniem, przechowywaniem i składowaniem odpadów, zgodnie z ich występowaniem.
* F3 (metoda opłaty za odpady): Opłaty są naliczane od producenta odpadów za każdą jednostkę dostarczanego do geologicznego składowiska odpadu. Koszty poniesione przed budową składowiska, transport i przechowywanie są finansowane bezpośrednio, a budowa składowiska jest finansowana z kredytu, który jest spłacany z wpływów z opłat.
* R1, R2, R3: możliwe lokalizacje przechowywania odpadów.

* C1 - całkowity koszt
* C2 - koszty aktualnych konsumentów
* C3 - koszty przyszłych konsumentów
* C4 - ryzyko dodatkowych kosztów

|Oznaczenie| Wariant | Time scenario | Site | Financing | C1 $\downarrow$ | C2 $\downarrow$ | C3 $\downarrow$ | C4 $\downarrow$ |
|-|----------|----|----|----|------|------|------|------|
|A| 0 (1)    | S1 | R1 | F1 | 0.60 | 0.93 | 0.00 | 0.73 |
|B| 4 (5)    | S1 | R2 | F2 | 0.62 | 0.40 | 0.56 | 0.50 |
|C| 10 (11)  | S2 | R1 | F2 | 0.45 | 0.86 | 0.00 | 0.73 |
|D| 23 (24)  | S3 | R2 | F3 | 0.59 | 0.24 | 0.70 | 0.63 |
|E| 2 (3)    | S1 | R1 | F3 | 1.00 | 0.45 | 0.57 | 0.50 |
|F| 6 (7)    | S1 | R3 | F1 | 0.40 | 0.90 | 0.00 | 0.82 |
|G| 13 (14)  | S2 | R2 | F2 | 0.69 | 0.49 | 0.56 | 0.61 |
|H| 26 (27)  | S3 | R3 | F3 | 0.80 | 0.06 | 1.00 | 0.67 |
|I| 21 (22)  | S3 | R2 | F1 | 0.32 | 0.83 | 0.00 | 0.94 |
|J| 22 (23)  | S3 | R2 | F2 | 0.59 | 0.24 | 0.70 | 0.63 |

### Wstępna strategia:
* Grupa 2: Zwiększenie ilości odpadów w przyszłości może zwiększyć przyszłe koszty, z tego względu najważniejsze wydaje się kryterium C3, warto również wyróżnić S1 minimalizujące długość przechowywania odpadów a także F2.

* Grupa 4: Inwestorowi zależy na stałych dochodach, bezpieczeństwie i stabilności, w tym celu szczególną uwagę trzeba poświęcić na kryterium C4, niezależnym od niego finansowaniu F2 oraz bezpiecznym czasie przechowywania S3.


### Zapis informacji preferencyjnej
$$
U(b) \ge U(a) + \epsilon \\
U(c) \ge U(d) + \epsilon \\
U(e) = U(f) \\
U(g) \ge U(h) + \epsilon \\
U(i) = U(j)
$$