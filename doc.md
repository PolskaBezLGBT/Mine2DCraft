

---

## 1. OPIS GRY

### Survival Game: The Nether Update to dwuwymiarowa gra survivalowa stworzona w bibliotece pygame. Gracz steruje postacią poruszającą się po otwartym świecie, walczącą z przeciwnikami, zdobywającą doświadczenie oraz ulepszenia. Gra zawiera dwa światy: Overworld oraz Nether.

---

## 2. CEL GRY

### Celem gry jest przetrwanie jak najdłużej poprzez:

- eliminowanie przeciwników
- zdobywanie doświadczenia i poziomów
- zbieranie przedmiotów
- przejście do świata Nether

---

## 3. STEROWANIE

W – ruch w górę
S – ruch w dół
A – ruch w lewo
D – ruch w prawo
R – restart gry po śmierci

---

## 4. MECHANIKA GRY

### 4.1 Gracz

- porusza się w czterech kierunkach
- automatycznie atakuje najbliższego przeciwnika
- zdobywa doświadczenie za pokonanych wrogów

### 4.2 Zdrowie i pancerz

- HP określa ilość życia gracza
- pancerz redukuje obrażenia
- po wyczerpaniu pancerza obrażenia trafiają bezpośrednio w HP

### 4.3 Doświadczenie i poziomy

* przeciwnicy dają punkty doświadczenia
* po zdobyciu odpowiedniej ilości EXP gracz awansuje
* każdy poziom zwiększa maksymalne HP
* po awansie aktywowany jest obracający się miecz na określony czas

---

## 5. PRZECIWNICY

### 5.1 Overworld

* skeleton – strzela pociskami
* slow – wolny, ale wytrzymały
* fast – szybki, mało wytrzymały

### 5.2 Nether

* ghast – strzela fireballami
* blaze – szybki przeciwnik dystansowy
* pigman – przeciwnik o średnich statystykach
* nether_skeleton – bardzo szybki, posiada dodatkowy atak

---

## 6. SYSTEM WALKI

* gracz automatycznie oddaje strzały co określony czas
* możliwy jest tryb pojedynczego lub potrójnego strzału
* przeciwnicy mogą atakować wręcz lub dystansowo

## Rodzaje pocisków:

* arrow – szybki, standardowy
* fireball – wolniejszy, zadaje większe obrażenia

---

## 7. ŚWIAT GRY

* świat podzielony jest na segmenty (chunki) o rozmiarze 600x600
* generowane są dynamicznie wokół gracza
* mogą zawierać przeszkody

## 7.1 Overworld

* zielone tło
* podstawowe przeszkody

## 7.2 Nether

* zmienione tekstury
* inny wygląd otoczenia

---

## 8. PORTAL

pojawia się losowo po pokonaniu przeciwnika w Overworld
umożliwia przejście do Nether
po użyciu:

- reset przeciwników
- reset mapy
- regeneracja zdrowia



---

## 9. PRZEDMIOTY

* apteczka – przywraca zdrowie
* power-up – aktywuje potrójny strzał na określony czas
* pancerz – zwiększa poziom ochrony

---

## 10. SZTUCZNA INTELIGENCJA

* przeciwnicy poruszają się w stronę gracza
* niektórzy posiadają zdolność strzelania
* część posiada specjalne ataki

---

## 11. ŚMIERĆ

* gdy HP spadnie do zera gra się kończy
* wyświetlana jest animacja śmierci
* możliwy restart klawiszem R

---

## 12. TECHNOLOGIE

* Python
* pygame
* Pillow (PIL)

---

## 13. GŁÓWNE FUNKCJE


```reset_game()
Resetuje stan gry

spawn_enemy()
Tworzy przeciwników

take_damage(amount)
Obsługuje obrażenia

generate_chunk(cx, cy)
Generuje fragment mapy

normalize_vector(dx, dy)
Normalizuje wektor ruchu

```

## 14. MOŻLIWE ROZSZERZENIA

* dodanie bossów
* system ekwipunku
* nowe światy
* zapis gry
* tryb multiplayer
