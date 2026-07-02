# Interaktives Website-Template
Dieses Repository dient als technische Grundlage für die Erstellung Ihrer Webseite. 
Die Vorlage integriert Quarto zur Dokumenterstellung, Python für computergestützte Analysen 
sowie beispielhaft Babylon.js für die Einbindung interaktiver 3D-Visualisierungen.

## Inhalt & Struktur unserer Website (Gruppe 9-2 — vSLAM)
Die Hauptseite [index.qmd](index.qmd) ist eine interaktive Ein-Seiten-Präsentation zum Thema **vSLAM (Visual Simultaneous Localization and Mapping)**. Der Aufbau folgt der eigentlichen Algorithmus-Pipeline und ist in nummerierte Kapitel gegliedert:

- **1.1 Feature Extraction** – ORB-Detektor, Deskriptoren, Matching
- **1.2 Visuelle Odometrie** – Essential Matrix, Pose-Schätzung, Trajektorie
- **2.1 Lokales Mapping** – Triangulation (DLT), Perspective-n-Point (PnP)
- **2.2 Lokale Optimierung** – Bundle Adjustment
- **3.1 Loop Closure** – Bag-of-Visual-Words, geometrische Verifikation
- **3.2 Globale Optimierung** – Pose-Graph-Optimierung

Jedes Kapitel nutzt einen selbstgebauten Slider-Mechanismus (`.vslam-slider`, HTML/CSS/JS am Dateianfang von `index.qmd`), der den Inhalt in einzelne, per „Zurück"/„Weiter"-Buttons navigierbare Folien aufteilt, statt alles als langen Fließtext darzustellen.

Ergänzend enthält die Seite:
- eine live ausgeführte `{python}`-Codezelle (Plotly), die zu Beginn eine 3D-Punktwolkenvorschau aus den Rohdaten in `data/` (Kamera-Keyframes, Referenzposen, Feature-Punkte) erzeugt,
- am Ende ausklappbare Codeblöcke (`<details>`) mit den vollständigen (nicht ausgeführten, rein illustrativen) Python-Implementierungen der einzelnen Pipeline-Schritte,
- statische Abbildungen, GIFs und Videos aus `images/`, die per relativem Pfad eingebunden werden.

Die Dateien [13_loop_closure.qmd](13_loop_closure.qmd) und [14_globale_optimierung.qmd](14_globale_optimierung.qmd) sind eigenständige, **vollständig ausgeführte** Quarto-Dokumente zu den Kapiteln 3.1 und 3.2 (die Basis der in `index.qmd` gezeigten Code-Auszüge). Sie werden beim Rendern als eigene Seiten der Website mitgebaut und erzeugen u. a. `loop_constraints.json` sowie einen Teil der Abbildungen in `images/`.

### Technische Voraussetzungen, damit alle Inhalte korrekt laden
- **Assets müssen im Repo vorhanden bleiben:** `images/`, `data/` und `loop_constraints.json` werden von `index.qmd`, `13_loop_closure.qmd` und `14_globale_optimierung.qmd` über relative Pfade referenziert. Fehlen sie (z. B. durch `.gitignore`-Regeln oder unvollständige Forks), bleiben Bilder, Videos oder Plots leer bzw. der Build schlägt fehl.
- **Python-Pakete für ausführbare Codezellen:** Aktuell werden `numpy`, `plotly`, `matplotlib` und `scipy` benötigt (siehe `.github/workflows/publish.yml`). Die GitHub Action installiert diese automatisch bei jedem Push; für ein lokales `quarto render`/`quarto preview` müssen sie manuell installiert sein.
- **Neue Bibliotheken in echten `{python}`-Zellen** (nicht in den rein angezeigten `` ```python ``-Codeblöcken) müssen zusätzlich in `.github/workflows/publish.yml` unter „Install dependencies" ergänzt werden – sonst schlägt das automatische Deployment fehl.
- **JavaScript im Browser aktiviert:** Der Slide-Mechanismus je Kapitel läuft rein clientseitig; ohne JavaScript ist nur die erste Folie jedes Kapitels sichtbar.
- **Aktueller Browser mit Video-/LaTeX-Unterstützung:** Für eingebettete `<video>`-Elemente sowie die per KaTeX gerenderten Formeln wird eine halbwegs aktuelle Browserversion vorausgesetzt.

## Konfigurationsschritte (Setup)
Um eine eigene Arbeitsumgebung auf Basis dieser Vorlage zu erstellen, führen Sie bitte die folgenden Schritte strikt in der angegebenen Reihenfolge aus:

- **Repository forken**
Betätigen Sie die Schaltfläche "Fork" in der oberen rechten Ecke der GitHub-Oberfläche. Hierdurch wird eine identische Kopie des Projekts in Ihren persönlichen GitHub-Account übertragen.

- **Konfiguration der Workflow-Berechtigungen**
Standardmäßig sind Schreibzugriffe für automatisierte Prozesse in Forks deaktiviert. Zur Aktivierung der Website-Erstellung müssen Sie folgende Anpassungen vornehmen:

  - Navigieren Sie zu Settings > Actions > General.
    
  - Suchen Sie den Abschnitt Workflow permissions.

  - Aktivieren Sie die Option "Read and write permissions" und bestätigen Sie mit Save.

  - Wechseln Sie zum Reiter Actions und bestätigen Sie die Aktivierung der Workflows durch Klick auf "I understand my workflows, go ahead and enable them".

- **Aktivierung von GitHub Pages**
- 
  - Navigieren Sie zu Settings > Pages.

  - Wählen Sie unter dem Punkt "Build and deployment" bei Branch den Branch gh-pages aus.

  - Bestätigen Sie die Auswahl mit Save.
(Hinweis: Der Branch gh-pages wird erst nach dem ersten erfolgreichen Durchlauf der GitHub Action generiert, oder muss manuell erstellt werden).

## Workflow für Bearbeitung und Deployment
Sämtliche Änderungen an der Datei index.qmd führen nach einem Push zum Repository automatisch zur Ausführung der CI/CD-Pipeline:

- Python-Umgebung: Quarto führt enthaltene Code-Segmente aus und generiert die entsprechenden Abbildungen.

- Rendering: Die Markdown-Inhalte werden in ein statisches HTML-Dokument transformiert.

- Deployment: Die aktualisierte Website wird unter folgendem URL-Schema bereitgestellt: https://<ihr-username>.github.io/<repo-name>/

## Richtlinien zur Quarto-Syntax:
- Mathematische Formeln: Verwenden Sie die LaTeX-Notation, z. B. $E = mc^2$.

- Python-Berechnungen: Code-Blöcke müssen zwingend mit ```{python} eingeleitet werden.

- HTML/3D-Inhalte: Die Integration von Babylon.js-Skripten erfolgt innerhalb von ```{=html} Blöcken.

## Fehleranalyse (Troubleshooting)
- Fehlende Python-Grafiken: Überprüfen Sie das Protokoll unter dem Reiter "Actions" auf etwaige Installationsfehler der Bibliotheken matplotlib oder numpy.

- Inaktiver 3D-Canvas: Sollte die 3D-Umgebung nicht geladen werden, untersuchen Sie die Browser-Konsole (Taste F12) auf einen 404 (Not Found) Fehler. Dies deutet zumeist auf eine fehlerhafte Syntax im Verweis auf das Babylon.js-Framework hin.

