# Opgave: Flat File DB system

Screenshot af testresultat

PS C:\Users\Mathias\Documents\ITSECWorspace\IT_sikkerhed_1_2> python -m unittest discover tests -v
test_add_duplicate_user (test_flat_file_db.TestFlatFileDB.test_add_duplicate_user) ... ok
test_add_user (test_flat_file_db.TestFlatFileDB.test_add_user) ... ok
test_delete_user (test_flat_file_db.TestFlatFileDB.test_delete_user) ... ok
test_get_nonexistent_user (test_flat_file_db.TestFlatFileDB.test_get_nonexistent_user) ... ok
test_missing_fields (test_flat_file_db.TestFlatFileDB.test_missing_fields) ... ok
test_update_user (test_flat_file_db.TestFlatFileDB.test_update_user) ... ok

----------------------------------------------------------------------
Ran 6 tests in 0.009s

OK

Dette projekt implementerer en simpel brugerdatabase, der gemmer data i en JSON-fil (flat file database). Systemet er skrevet i Python og inkluderer omfattende unit tests.

## Hvorfor er det smart at bruge en flat_file_db?

At bruge en "flat file database" (som f.eks. en JSON-fil) har flere fordele i bestemte situationer:

1.  **Simpelhed:** Det er utroligt nemt at sætte op og kræver ingen separat database-server (som MySQL eller PostgreSQL).
2.  **Portabilitet:** Hele databasen er blot en fil, som nemt kan flyttes, kopieres eller sendes sammen med koden.
3.  **Læsbarhed:** Data gemmes ofte i tekstformat (som JSON eller CSV), hvilket gør det nemt for mennesker at læse og debugge direkte i filen.
4.  **Lav overhead:** Det kræver meget få ressourcer at køre, hvilket er ideelt til små applikationer, prototyper eller konfigurationsfiler.

*Bemærk: Til store systemer med mange samtidige brugere eller enorme datamængder vil en rigtig SQL-database være bedre, men til mindre opgaver er en flat file løsning ofte perfekt.*

## Unit Tests

Projektet indeholder unit tests designet med **Given-When-Then** metoden for at sikre, at alle krav er opfyldt.


### Test Design og Risici

Hver test i `tests/test_flat_file_db.py` indeholder kommentarer, der beskriver:
-   **Risiko:** Hvad er risikoen, hvis denne funktion fejler? (F.eks. tab af data eller sikkerhedsbrist).
-   **Given:** Starttilstanden før testen.
-   **When:** Den handling, der udføres.
-   **Then:** Det forventede resultat.




OPGAVER 03-02-2025

Dette er et skole projekt på Zealand Næstved


Nye unit test
<img width="322" height="368" alt="image" src="https://github.com/user-attachments/assets/00f458b2-8265-4427-bb79-b8499ea81aa5" />

Test af de nye unit tests
<img width="1301" height="338" alt="image" src="https://github.com/user-attachments/assets/a4d9bd3d-46a4-457b-b3de-a3108f766349" />

<img width="1302" height="470" alt="image" src="https://github.com/user-attachments/assets/d5afdb75-41f5-43eb-b1a3-01836ea19b81" />

<img width="1288" height="510" alt="image" src="https://github.com/user-attachments/assets/32a10808-034f-4391-b8b0-6220712edd01" />


<img width="1285" height="756" alt="image" src="https://github.com/user-attachments/assets/9881c1c4-3f47-41fa-9a51-0d16092b9ceb" />


OPGAVER 05-02-2025

Grænseværditest
Jeg har valgt et klassisk adgangskode kontrol-system for at lave opgaverne

For en adgangskode hvor kravet er 8 tegn, så kan man opdele dem således:


Gyldige adgangskoder: Alle koder mellem 8 tegn og over burde accepteres

For korte adgangskoder: Alle koder med 0-7 tegn systemet bør afvise dem alle

Her er mit kode eksempel: 
<img width="408" height="368" alt="image" src="https://github.com/user-attachments/assets/ff36d37f-fe78-4712-9dad-5c61bc3da2bb" />

Her er resultat fra test
<img width="1246" height="89" alt="image" src="https://github.com/user-attachments/assets/3a9c8a62-862d-48f6-9fac-6fc96f40aace" />

CRUD OPGAVE

 (Create): Kan man oprette en ny bruger med et password korrekt i systemet? 

 (Read): Kan systemet hente og verificere brugerens data, når de forsøger at logge ind? 

 (Update): Kan en eksisterende bruger ændre sit password uden fejl? 

 (Delete): Kan en brugerprofil slettes sikkert og fuldstændigt fra databasen? 

 (List): Kan en administrator trække en form for oversigt/liste over alle registrerede brugere?


CYCLE PROCESS TEST OPGAVE

Cycle Process Test fokuserer på at teste om systemet kan håndtere den samme handling mange gange over længere tid uden at fejle.

For loginkontrol kan jeg eksempelvis teste dette:

Gentagelse: Kan en bruger logge ind, udføre en handling og logge ud igen 100+ gange i træk uden at systemet bliver langsomt eller går ned

Ressourcer: Sikrer man at systemet rydder op i de ældre sessioner og data hver gang, så hukommelsen ikke bliver fyldt op. Der kan evt komme memory leaks

Stabilitet: Bliver log-filer fyldt op, eller stopper systemet med at validere login korrekt efter mange forsøg?.


TEST PYRAMIDEN OPGAVE

 Bottom Up med fokus på hastigheden ved testing
 
Denne model fokuserer på at have flest unit tests i bunden, fordi de er hurtigere at køre

I toppen har man få End-to-end tests, da de tager meget lang tid at udføre. og kan ende med at tage xxxxxx timer

For mit loginkontrol betyder det, at jeg ville teste selve koden bag login mange gange, men kun tester hele skærmbilledet få gange.

 Top Down (Fokus på brugeren)
Her kigger man først på brugerrejser for at få det bedste overblik over, om login virker for brugeren

Ulempen er, at man "ikke kan se skoven for bare træer". 

Det betyder at man kan se, at login fejler, men det er svært at gennemskue præcis hvor i koden fejlen ligger.

OPGAVE DECISION TABLE TEST

Eksempel for et loginsystem


(Jeg kunne ikke få MARKDOWN Tabel til at virke...)

(REGEL) (GYLDIGT-LOGIN) (MFA-KORREKT) (RESULTAT)
R1        NEJ              NEJ             Adgang bliver nægtet og vi logger det
R2        JA               NEJ            Adgang vil blive nægtet (eller måske bed om MFA, afhænger af hvordan systemet er bygget, kan også være man får en påmindelse om at sætte det op eller noget i den dur)
R3        JA               JA             Adgang givet - logget ind




Data dreven unit-test med PyTest
