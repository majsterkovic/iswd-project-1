Zadaniem projektu jest stworzenie rankingu różnych scenariuszy zarządzania odpadami radioaktywnymi z wykorzystaniem odpornej regresji porządkowej. Będziemy bazować na zbiorze danych opisanym w pracy "Nuclear waste management: an application of the multicriteria PROMETHEE methods".

## Zadanie (3)

### Opis preferencji
Grupa 2
* W skutek wyczerpywania się złóż materiałów radioaktywnych, elektrownie mogą
zacząć korzystać z bardziej ubogich złóż, co przełoży się na zwiększenie ilości odpadów radioak-
tywnych.

Grupa 4
* Grupa zawiera ostrożnego inwestora, który nie chce ryzykować.

### Wybrane pary
TODO: Uzupełnić
| Wariant 1 | Wariant 2|
|---|---|
|0|4|
|X|Y|
|A|B|
|C|D|

### Opis wariantów

* S1: Zakłada 10-letnie przechowywanie ILW i 30-letnie przechowywanie HLW.
* S2: Oba typy odpadów, ILW i HLW, są przechowywane przez 30 lat.
* S3: Przedłuża czas przechowywania do 50 lat zarówno dla ILW, jak i HLW

* F1 (metoda opłaty kWh): Opiera się na opłatach za każdy wyprodukowany kWh energii jądrowej, zbieranych w ciągu pierwszych 30 lat. Środki te mogą być akumulowane w funduszu powierniczym, generując odsetki na przyszłe wydatki.
* F2 (metoda prorata): Zakłada nieograniczoną odpowiedzialność producenta odpadów, który pokrywa wszystkie koszty związane z kondycjonowaniem, przechowywaniem i składowaniem odpadów, zgodnie z ich występowaniem.
* F3 (metoda opłaty za odpady): Opłaty są naliczane od producenta odpadów za każdą jednostkę dostarczanego do geologicznego składowiska odpadu. Koszty poniesione przed budową składowiska, transport i przechowywanie są finansowane bezpośrednio, a budowa składowiska jest finansowana z kredytu, który jest spłacany z wpływów z opłat.
* R1, R2, R3: możliwe lokalizacje przechowywania odpadów.

### Opis kryteriów
* C1 - całkowity koszt
* C2 - koszty aktualnych konsumentów
* C3 - koszty przyszłych konsumentów
* C4 - ryzyko dodatkowych kosztów

|Oznaczenie| Wariant | Time scenario | Site | Financing | C1 $\downarrow$ | C2 $\downarrow$ | C3 $\downarrow$ | C4 $\downarrow$ |
|---|---|---|---|---|---|---|---|---|
|A|0 (1)| S1 | R1 | F1 | 0.60 | 0.93 | 0.00 | 0.73 |
|B|4 (5)| S1 | R2 | F2 | 0.62 | 0.40 | 0.56 | 0.50 |
|C|10 (11)| S2 | R1 | F2 | 0.45 | 0.86 | 0.00 | 0.73 |
|D|23 (24)| S3 | R2 | F3 | 0.59 | 0.24 | 0.70 | 0.63 |

### Zapis informacji preferencyjnej - todo
$$
\begin{flalign*}
    U(b) &\ge U(a) + \epsilon \\
    U(c) &= U(d) \\
    U(e) &\ge U(f) + \epsilon \\
    U(g) &\ge U(h) + \epsilon \\
    U(i) &= U(j)
\end{flalign*}
$$

### Normalizacja
$$
\sum_{i=1}^{n} u_i(\beta_i) = 1
$$
