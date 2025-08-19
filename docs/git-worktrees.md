# Git Worktrees – Einsteigerfreundliche Erklärung + Übungen

Git-Worktrees erlauben dir, mehrere Arbeitsverzeichnisse derselben Repository-Historie parallel zu nutzen – ohne die Repo mehrfach zu klonen. Jeder Worktree kann eine andere Branch gleichzeitig ausgecheckt haben. Ideal für paralleles Arbeiten (z. B. PR-Merge-Tests), ohne ständig zu staschen oder zu switchen.

## Was ist ein Worktree?
- Ein zusätzlicher Arbeitsordner, der dieselbe `.git`-Objektdatenbank nutzt.
- Jeder Worktree hat seine eigene ausgecheckte Branch/HEAD.
- Du sparst Speicher und Zeit gegenüber mehreren vollständigen Clones.

Analogie: Stell dir die Git-Historie als „gemeinsames Lager“ vor. Worktrees sind mehrere „Werkbänke“, die alle auf dasselbe Lager zugreifen, aber an unterschiedlichen Baustücken (Branches) gleichzeitig arbeiten.

## Wofür ist das gut?
- Parallele Branches gleichzeitig bearbeiten (z. B. Hotfix in einem Worktree, Feature im anderen).
- Konfliktauflösung/Merge-Tests isoliert ausprobieren, ohne den Haupt-Arbeitsbaum zu „verschmutzen“.
- Reproduktionen/CI-Experimente in separatem Ordner.
- Große Refactors inkrementell testen, während ein anderer Worktree lauffähig bleibt.

## Worktrees vs. Branches (normaler Checkout)
- Normal: Eine Arbeitskopie; Branch-Wechsel = Kontextwechsel, ggf. Stash nötig.
- Worktrees: Mehrere Arbeitskopien gleichzeitig; jede mit eigener Branch. Kein ständiges Hin- und Herspringen nötig.

## Kernbefehle
- Worktrees auflisten:
```bash
git worktree list
```
- Neuen Worktree für bestehende Branch anlegen (Pfad anpassen):
```bash
git worktree add ../wt-merge-test main
```
- Neuen Worktree mit neuer Branch auf Basis von `origin/main`:
```bash
git worktree add -b feature/x ../wt-feature-x origin/main
```
- Worktree entfernen (sauber):
```bash
git worktree remove ../wt-feature-x
```
- Verwaiste Einträge aufräumen (falls Ordner manuell gelöscht wurde):
```bash
git worktree prune
```

Hinweis: Git verwaltet Worktree-Metadaten unter `.git/worktrees/...` (intern). Ein Ordner auf Repositoriumsebene namens `.worktrees/` ist hingegen nur ein normaler Ordner, den jemand angelegt hat – nicht Git-intern. Du kannst ihn gefahrlos löschen oder in `.gitignore` aufnehmen.

## Typische Workflows
- „Sicheren“ Merge in separatem Worktree testen.
- Hotfix während laufender Entwicklung: Ein Worktree hält die App am Laufen, im anderen wird fix entwickelt.
- Langläufer-Refactor trennen, ohne den Alltag zu blockieren.

## Häufige Stolpersteine
- Dieselbe Branch kann nicht gleichzeitig in zwei Worktrees ausgecheckt werden. Lösung: zweite Branch anlegen oder detached HEAD verwenden.
- Manuelles Löschen eines Worktree-Ordners hinterlässt Metadaten → `git worktree prune` ausführen.
- Tools, die hart `.git/` erwarten, müssen ggf. den Worktree-Pfad unterstützen (in Worktrees liegt oft eine `.git`-Datei, die auf das gemeinsame Repo verweist).

---

# Übungen für Umschüler:innen (Hands-on)

Voraussetzungen: Git installiert, ein bestehendes Repo mit `main` und ein Remote `origin`.

## Übung 1: Ersten Worktree anlegen und committen
1) Liste vorhandene Worktrees:
```bash
git worktree list
```
2) Lege einen Worktree für `main` an:
```bash
git worktree add ../wt-demo-a main
```
3) Wechsle in den neuen Ordner und erstelle eine Datei:
```bash
cd ../wt-demo-a
echo "Hello Worktrees" > WORKTREES_DEMO.txt
git add WORKTREES_DEMO.txt
git commit -m "chore: add demo file for worktrees"
```
4) Optional: Pushen
```bash
git push
```

## Übung 2: Feature-Branch in eigenem Worktree
1) Neuen Worktree mit neuer Branch erstellen:
```bash
cd /pfad/zum/hauptrepo
git worktree add -b feature/worktrees-intro ../wt-feature origin/main
```
2) Datei ändern und committen:
```bash
cd ../wt-feature
echo "Feature in eigenem Worktree" >> WORKTREES_DEMO.txt
git add WORKTREES_DEMO.txt
git commit -m "feat: extend demo in separate worktree"
git push --set-upstream origin feature/worktrees-intro
```

## Übung 3: Merge-Tests isoliert
1) Erstelle Worktree für die Zielbranch (z. B. `main`):
```bash
cd /pfad/zum/hauptrepo
git worktree add ../wt-merge main
```
2) Im Worktree `../wt-merge` eine Test-Branch vom aktuellen `main` erstellen und Feature reinmergen:
```bash
cd ../wt-merge
git checkout -b test/merge-feature
git merge origin/feature/worktrees-intro
# Konflikte (falls vorhanden) lösen, testen, committen.
```
3) Dein „Haupt“-Worktree bleibt unberührt.

## Übung 4: Aufräumen
1) Entferne nicht mehr benötigte Worktrees:
```bash
cd /pfad/zum/hauptrepo
git worktree remove ../wt-feature
git worktree remove ../wt-merge
```
2) Falls du Ordner manuell gelöscht hast, Metadaten bereinigen:
```bash
git worktree prune
```

## Übung 5: Detached HEAD Worktree (Tag/Commit testen)
1) Worktree auf bestimmtem Commit/Tag (z. B. `v1.2.3`) anlegen:
```bash
git worktree add ../wt-tag v1.2.3
```
2) Nur lesen/testen, nicht zwingend committen. Danach entfernen:
```bash
git worktree remove ../wt-tag
```

## Übung 6: „Same branch already checked out“-Fehler nachvollziehen
1) Checke `main` in einem Worktree aus.
2) Versuche, `main` in einem zweiten Worktree zu verwenden (ohne neue Branch) → Fehler erscheint.
3) Lösung: Neue Branch anlegen (`-b`) oder in detached HEAD arbeiten.

---

## FAQ
- Unterschied zu neuem Clone? Worktrees teilen sich die Git-Objekte → schneller und platzsparend.
- Löscht `git worktree remove` meine Commits? Nein. Es entfernt nur den Arbeitsordner und den Worktree-Verweis. Commits/Branches bleiben im Repo.
- Wo „liegt“ die Verwaltung? In `.git/worktrees/...` (intern). Ein Repo-Ordner `.worktrees/` ist kein Git-internes Verzeichnis – nur ein normaler Ordner.

## Empfehlung für dieses Repo
- Wenn ein Top-Level-Ordner `.worktrees/` existiert, nimm ihn in `.gitignore` auf oder lösche ihn, da er nur lokale Hilfsdateien enthält.
