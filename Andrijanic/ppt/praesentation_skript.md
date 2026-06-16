# Sprech-Skript — passend zu vSLAM_1.1_1.2_FINAL.pptx (21 Folien)

**Ziel ~8:45–10:00.** `[Folie N]` = umblättern. Zeitmarke = Ende des Abschnitts. Reihenfolge 1:1 zum Deck.

---

### [Folie 1 — Titel]
*(kurz stehen lassen, kein Text — direkt mit Folie 2 beginnen)*

### [Folie 2 — Problem]  ·  [0:35]
Wenn wir Menschen durch einen Raum gehen, wissen wir automatisch, wo wir sind und wie der Raum aussieht — allein mit den Augen. Ein Roboter hat dieses Gefühl nicht. Er bekommt nur einen Strom von Bildern und muss daraus zwei Dinge gleichzeitig herausfinden: erstens, wie er sich bewegt hat, und zweitens, wie die Umgebung aufgebaut ist — in Echtzeit. Genau das löst visuelles SLAM.

### [Folie 3 — Use-Cases & Motivation]  ·  [1:25]
Mein Hauptbeispiel ist eine Drohne in einem Gebäude oder Tunnel. Dort gibt es kein GPS-Signal — trotzdem muss sie wissen, wo sie ist. Mit Kamera und vSLAM bestimmt sie ihre Position allein aus den Bildern. Warum nicht GPS oder LiDAR? GPS funktioniert drinnen nicht. LiDAR — ein Laser-Scanner — funktioniert, ist aber teuer und schwer. Eine Kamera ist billig und leicht, funktioniert ohne GPS und liefert nicht nur die Position, sondern gleichzeitig eine Karte. Dasselbe steckt in smarten Staubsauger-Robotern oder hilft beim autonomen Fahren, wenn das GPS kurz ausfällt.

### [Folie 4 — Überblick]  ·  [2:20]
Der Workflow hat fünf Phasen. In 1.1, Feature Extraction, suchen wir markante Punkte — vor allem Ecken, also Stellen, wo sich die Helligkeit in mehrere Richtungen stark ändert; solche Punkte kann man zuverlässig wiedererkennen. In 1.2, Visueller Odometrie, verfolgen wir sie und schätzen die Kamerabewegung. In 2.1, dem lokalen Mapping, werden die bisher nur 2D-Punkte zu echten 3D-Punkten — weil wir denselben Punkt aus mehreren Positionen sehen und seine Tiefe berechnen können. In 2.2 werden Karte und Bewegung mit Bundle Adjustment gemeinsam verfeinert. Und in 3.1 und 3.2 erkennt das System bekannte Orte wieder und korrigiert den Drift. Ich übernehme die ersten beiden Phasen.

---

### [Folie 5 — Graustufen & Gauß]  ·  [2:55]
Zuerst die Vorverarbeitung. Das Farbbild wird in Graustufen umgewandelt — mit der Formel Y = 0,299·R + 0,587·G + 0,114·B; Grün zählt am meisten, weil unser Auge dafür am empfindlichsten ist. Warum Graustufen statt Farbe? Für Ecken zählt nur die Helligkeit — ein Kanal statt drei, also schneller. Danach glättet der Gauß-Filter das Rauschen, indem jeder Pixel mit seinen Nachbarn gemittelt wird; rechts sieht man, wie der helle Ausreißer 250 abgeschwächt wird. Den Gauß-Filter haben wir in Vorlesung 2 verwendet.

### [Folie 6 — FAST-Detektor]  ·  [3:30]
Der FAST-Detektor prüft für jeden Pixel p einen Kreis aus 16 Nachbarn. Ein Ringpixel zählt als heller, wenn er über p plus Schwelle t liegt, als dunkler unter p minus t — dazwischen ist er ähnlich. Die Schwelle ist wichtig: ohne sie würde schon Rauschen als Unterschied zählen. Ein Pixel ist eine Ecke, wenn mindestens 9 zusammenhängende Ringpixel heller oder dunkler sind. Links: 10 zusammenhängende heller → Ecke. Rechts: hellere Pixel verstreut, längster Bogen nur 5 → keine Ecke.

### [Folie 7 — Bildpyramide: Beispiel]  ·  [4:00]
Dieselbe Ecke sieht je nach Entfernung anders aus; ist ein Objekt zu groß, ist die Ecke verschmiert und der FAST-Kreis zu klein. Lösung: die Bildpyramide. Hier dieselbe Stelle — auf Stufe 0 keine Ecke, Bogen 5; auf der kleineren Stufe 6 wird sie erkannt, Bogen 13.

### [Folie 8 — Bildpyramide: Rückrechnung]  ·  [4:20]
Wir erzeugen 8 Stufen, jede um Faktor 1,2 kleiner. Finden wir eine Ecke auf einer kleinen Stufe, rechnen wir ihre Position zurück aufs Original: Position im Original = Position auf Stufe k mal 1,2 hoch k. Beispiel: Stufe 6, (120, 80); 1,2 hoch 6 ist 2,99 — also Original (358, 239).

### [Folie 9 — Harris: Gradient → Matrix M]  ·  [5:05]
Wie misst Harris, ob eine Stelle eine Ecke ist? Über die Gradienten — wie stark sich die Helligkeit ändert. Iₓ ist die Änderung in x-Richtung, I_y in y-Richtung; an einer Kante 200→50 ergibt das −75. Dann bilden wir drei Summen über das Fenster: Sₓₓ ist die Summe von Iₓ², S_yy von I_y², und Sₓy von Iₓ mal I_y. Diese drei Zahlen bilden die Struktur-Matrix M. Sind beide Diagonalwerte groß, ändert sich die Helligkeit in beiden Richtungen — ein Zeichen für eine Ecke.

### [Folie 10 — Harris: Response R]  ·  [5:35]
Aus M berechnen wir die Harris-Response: R gleich Determinante von M minus k mal Spur von M zum Quadrat, mit k etwa 0,04. Man muss sich nur das Ergebnis merken: ist R groß und positiv, ändert sich die Helligkeit in beiden Richtungen — eine starke Ecke. Ist R klein oder negativ, haben wir nur eine Kante. Ist R nahe null, ist die Region flach. Je größer R, desto stärker die Ecke — wir behalten nur Stellen mit großem R.

### [Folie 11 — Quadtree]  ·  [6:00]
FAST liefert zu viele Ecken, die an Kanten clustern — hier 275. Der Quadtree legt ein Gitter über das Bild und behält pro Zelle nur die nach Harris stärkste Ecke. So sind die Punkte gleichmäßig verteilt und stark. Reihenfolge: FAST findet Kandidaten, Harris bewertet, der Quadtree wählt verteilt aus.

### [Folie 12 — Zusammenfassung 1.1]  ·  [6:20]
Zusammengefasst ist 1.1 ein Trichter: aus etwa 787 FAST-Ecken werden durch den Quadtree 73, und Harris behält die Top 40. Die Menge sinkt, die Qualität steigt.

---

### [Folie 13 — Orientierung θ]  ·  [6:55]
Jetzt 1.2. Jeder Ecke geben wir eine Orientierung θ über einen Patch von 31×31 Pixeln. Wir berechnen den Helligkeits-Schwerpunkt über die Momente: m-null-null ist die Summe aller Helligkeiten, m-eins-null die Summe aus x mal Helligkeit, m-null-eins aus y mal Helligkeit. Im Beispiel liegen die hellen Pixel rechts: m-eins-null wird plus 160, m-null-eins plus 80, also θ = atan2(80,160) ≈ 27 Grad — der Pfeil zeigt zum Hellen. So bekommt dieselbe Ecke immer dasselbe θ — rotationsinvariant.

### [Folie 14 — Deskriptor: Prinzip]  ·  [7:20]
Jetzt der binäre Deskriptor — ein Fingerabdruck aus Nullen und Einsen. Wir legen feste Pixelpaare in den Patch — hier 10, in echt 256. Für jedes Paar vergleichen wir die Helligkeit: ist Punkt A heller als B, schreiben wir eine 1, sonst eine 0. So entsteht ein Bit-String.

### [Folie 15 — Deskriptor: Rotation]  ·  [7:40]
Damit das auch bei gedrehter Kamera klappt, drehen wir die Paare. Links die Paare ohne Rotation, rechts dieselben Paare um den Winkel θ gedreht — das hervorgehobene Paar macht die Drehung sichtbar. So liest dieselbe Ecke immer dieselben Stellen ab und ergibt denselben Bit-String. Das nennt man steered BRIEF.

### [Folie 16 — Matching: Hamming]  ·  [8:00]
Um dieselbe Ecke in zwei Bildern wiederzufinden, vergleichen wir die 256-Bit-Deskriptoren über die Hamming-Distanz — wie viele Bits sich unterscheiden, per XOR. Gleiche Ecke: nur wenige, hier 8 von 256. Andere Ecke: viele, hier 107. Wenig Unterschiede heißt: dieselbe Ecke.

### [Folie 17 — Ratio-Test]  ·  [8:20]
Problem: ähnliche Stellen wie gleiche Fenster passen mehrfach. Deshalb der Lowe-Ratio-Test: wir nehmen die zwei besten Treffer; ist der beste deutlich besser — geteilt durch den zweitbesten unter 0,75 — behalten wir ihn, sonst verwerfen. 12 zu 80 ist 0,15, behalten; 40 zu 45 ist 0,89, verwerfen. Übrig bleiben die grünen Matches.

### [Folie 18 — Pose: Pipeline]  ·  [8:50]
Aus den Punktpaaren berechnen wir die Kamerabewegung. Für jedes Paar gilt x'ᵀ·E·x = 0 — die Epipolar-Bedingung, die sagt, ob ein Paar zur Bewegung passt. E ist die Essential-Matrix; sie entsteht aus t und R — E = [t]ₓ·R — und versteckt so Rotation und Translation in einer 3×3-Matrix. findEssentialMat mit RANSAC berechnet E aus mindestens fünf Paaren und markiert Ausreißer. Dann zerlegt recoverPose E per SVD in R und t: R ist die Drehung, t nur die Richtung — die echte Strecke bleibt bei einer Mono-Kamera unbekannt.

### [Folie 19 — Pose: Inlier / Outlier]  ·  [9:15]
Ein einfaches Zahlenbeispiel bei reiner Seitwärtsbewegung: die Bedingung verlangt, dass die y-Koordinate in beiden Frames gleich bleibt. Für x = (3,2,1) und x' = (1,2,1) ergibt x'ᵀ·E·x null — ein Inlier. Wäre x' = (1,5,1), käme minus drei heraus — ein Outlier, den RANSAC verwirft. Rechts das echte Ergebnis aus meinen Frames: grün die Inlier, rot die Outlier, die Translation zeigt nach vorne, die Rotation ist fast reines Gieren.

### [Folie 20 — Trajektorie]  ·  [9:40]
Schritt 11 gibt nur die Bewegung zwischen zwei Frames. Die Trajektorie entsteht durch Aufsummieren. Wir starten bei Position null und Orientierung Identität. Dann für jedes Frame-Paar: die neue Position ist die alte plus R_global mal t — das lokale „vorne" wird über R_global erst in die Weltrichtung gedreht; danach kombinieren wir die Drehungen mit R_global = R_global mal R. Am Ende haben wir die Liste aller Positionen — die Trajektorie. Im Beispiel ist t immer (1,0), aber durch R_global wird der Weltschritt mal (1,0), mal (0,1), mal (−1,0) — der Pfad dreht sich.

### [Folie 21 — Abschluss]  ·  [10:00]
Ein Problem bleibt: kleine Fehler summieren sich, die Trajektorie driftet, und die Punkte sind nur 2D. Wie man daraus eine 3D-Karte baut und den Drift korrigiert, zeigen jetzt meine Kollegen. Danke!

---

### Übungs-Tipps
- ~10 min komplett; wenn du auf 8,5 musst, kürze zuerst Folie 9 (Gradient-Detail) und Folie 19 (Zahlenbeispiel).
- Pro Folie eine Idee. Zahlen/Matrizen sind Backup für Fragen, nicht zum Vorlesen.
- Die Bilder tragen viel — ruhig sprechen, auf das Bild zeigen.
