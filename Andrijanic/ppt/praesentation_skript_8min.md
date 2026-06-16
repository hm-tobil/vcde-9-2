# Sprech-Skript KURZ (~8 min) — passend zu vSLAM_1.1_1.2_kurz.pptx

`[Folie N]` = umblättern. Gekürzte Fassung (Detail-Digressionen entfernt).

---

### [Folie 1 — Titel]
Titel — kurz stehen lassen.

### [Folie 2 — Problem]
Menschen wissen beim Gehen automatisch, wo sie sind und wie der Raum aussieht. Ein Roboter bekommt nur Bilder und muss zwei Dinge gleichzeitig finden: wie er sich bewegt und wie die Umgebung aussieht — in Echtzeit. Das löst visuelles SLAM.

### [Folie 3 — Use-Cases & Motivation]
Beispiel: Drohne im Tunnel — kein GPS. Mit Kamera und vSLAM bestimmt sie ihre Position allein aus den Bildern. Kamera ist billig, leicht, ohne GPS — und liefert Position UND Karte. Auch in Staubsauger-Robotern und beim autonomen Fahren.

### [Folie 4 — Überblick]
Fünf Phasen: 1.1 markante Punkte, vor allem Ecken, finden; 1.2 sie verfolgen und die Bewegung schätzen. 2.1 baut eine 3D-Karte, 2.2 verfeinert sie, 3.1 und 3.2 erkennen bekannte Orte und korrigieren den Drift. Ich mache 1.1 und 1.2.

### [Folie 5 — Graustufen & Gauß]
Farbbild → Graustufen mit Y = 0,299·R + 0,587·G + 0,114·B; für Ecken zählt nur die Helligkeit, ein Kanal statt drei. Der Gauß-Filter glättet das Rauschen, damit FAST keine zufälligen Ecken findet.

### [Folie 6 — FAST-Detektor]
FAST prüft für jeden Pixel einen Kreis aus 16 Nachbarn: heller über p plus t, dunkler unter p minus t. Die Schwelle t hält Rauschen draußen. Ecke, wenn mindestens 9 zusammenhängend heller oder dunkler. Links 10 zusammenhängend → Ecke; rechts verstreut → keine Ecke.

### [Folie 7 — Bildpyramide: Beispiel]
Dieselbe Ecke sieht je nach Entfernung anders aus. Mit der Bildpyramide verkleinern wir das Bild: auf Stufe 0 keine Ecke, auf der kleineren Stufe 6 wird sie erkannt.

### [Folie 8 — Bildpyramide: Rückrechnung]
8 Stufen, Faktor 1,2. Eine Ecke auf einer kleinen Stufe wird zurückgerechnet: Original = Position mal 1,2 hoch k. Z.B. Stufe 6 → mal 2,99.

### [Folie 9 — Harris: Gradient → M]
Harris nutzt die Gradienten in x und y. Drei Summen bilden die Matrix M. Sind beide Diagonalwerte groß, ändert sich die Helligkeit in beiden Richtungen — das ist eine Ecke.

### [Folie 10 — Harris: Response R]
R = det(M) − k mal Spur² . R groß positiv → starke Ecke; klein oder negativ → nur Kante; nahe null → flach. Je größer R, desto stärker — wir behalten nur große R.

### [Folie 11 — Quadtree]
FAST liefert zu viele Ecken, die an Kanten clustern — 275. Der Quadtree behält pro Zelle die nach Harris stärkste Ecke → gleichmäßig verteilt und stark.

### [Folie 12 — Zusammenfassung 1.1]
1.1 ist ein Trichter: aus ~787 FAST-Ecken werden 73 durch den Quadtree, Harris behält die Top 40. Menge sinkt, Qualität steigt.

### [Folie 13 — Orientierung θ]
Jetzt 1.2. Jede Ecke bekommt eine Orientierung θ über einen 31×31-Patch — die Richtung zum Helligkeits-Schwerpunkt. Dadurch wird das Feature rotationsinvariant.

### [Folie 14 — Deskriptor: Prinzip]
Der binäre Deskriptor: feste Pixelpaare, hier 10, in echt 256. Pro Paar: ist A heller als B, eine 1, sonst 0. So entsteht ein Bit-String.

### [Folie 15 — Deskriptor: Rotation]
Damit es bei gedrehter Kamera klappt, drehen wir die Paare um θ — links ohne, rechts mit Rotation. So ergibt dieselbe Ecke denselben Bit-String (steered BRIEF).

### [Folie 16 — Matching: Hamming]
Wiederfinden über die Hamming-Distanz: wie viele Bits sich unterscheiden. Gleiche Ecke wenige (8 von 256), andere viele (107). Wenig Unterschiede = dieselbe Ecke.

### [Folie 17 — Ratio-Test]
Ähnliche Stellen passen mehrfach. Lowe-Ratio-Test: bester geteilt durch zweitbesten unter 0,75 → behalten, sonst verwerfen. Übrig bleiben die grünen Matches.

### [Folie 18 — Pose: Pipeline]
Aus den Paaren die Bewegung. Es gilt x'ᵀ·E·x = 0. E = [t]ₓ·R versteckt Rotation und Translation. findEssentialMat mit RANSAC berechnet E, recoverPose zerlegt es per SVD in R und t — t nur Richtung, Skala bei Mono unbekannt.

### [Folie 19 — Pose: Inlier/Outlier]
Die Epipolar-Bedingung prüft, ob ein Paar zur Bewegung passt: ist x'ᵀEx ungefähr null, ein Inlier, sonst ein Outlier, den RANSAC verwirft. Rechts: grün Inlier, rot Outlier, Translation vorwärts, Rotation fast nur Gieren.

### [Folie 20 — Trajektorie]
Trajektorie = Aufsummieren. Start bei null, Orientierung Identität. Für jedes Paar: neue Position = alte + R_global·t (lokales vorne in die Weltrichtung gedreht), dann R_global = R_global·R. So entsteht der Pfad — t bleibt (1,0), aber R_global dreht ihn.

### [Folie 21 — Abschluss]
Kleine Fehler summieren sich, die Trajektorie driftet, und die Punkte sind nur 2D. Wie man daraus eine 3D-Karte baut und den Drift korrigiert, zeigen jetzt meine Kollegen. Danke!

---

**Gekürzt ggü. Langfassung:** Folie 9 (Gradient-Detail −75/Summen), Folie 13 (Momenten-Zahlen), Folie 19 (Zahlenbeispiel), Folie 4 (2.1/2.2 knapper), Folie 5 (Grün-Aside), Folie 3 (LiDAR/Extras knapper).
