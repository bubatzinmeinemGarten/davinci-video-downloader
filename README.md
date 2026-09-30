# Video Downloader für DaVinci Resolve

Link von **YouTube, Instagram oder TikTok** einfügen, Format wählen, „Download & Import“ klicken.
Das Video wird geladen und landet im Bin **„Downloader“** deines Media Pools. Mit Fortschrittsbalken,
DaVinci Resolve bleibt dabei bedienbar. Läuft als Fenster direkt in Resolve (Fusion UI Manager).

**Formate:** MP4 1080p, MP4 720p (H.264, direkt schnittfähig), Nur Audio (WAV oder MP3)

## Download

➡️ **[Neueste Version als ZIP (6 KB)](../../releases/latest)** – Skript, Installer und Anleitung.
Die großen Programme (yt-dlp, ffmpeg, deno) sind nicht enthalten, der Installer lädt sie von den Originalquellen.

## Voraussetzung

- DaVinci Resolve **21.1 oder neuer** (bringt ein eigenes Python mit)
- Getestet: Resolve Studio 21.1 auf macOS (Apple Silicon); Installer auch für Intel-Macs getestet
- Windows/Linux: vorbereitet, aber **nicht getestet**

## Installation (macOS)

1. ZIP entpacken
2. `Installieren.command` per **Rechtsklick › Öffnen** starten (Doppelklick meldet einen Sicherheitshinweis,
   weil die Datei aus dem Internet kommt). Alternativ im Terminal: `bash Installieren.command`
3. DaVinci Resolve neu starten
4. **Workspace › Scripts › Video Downloader**

Der Installer legt ab:

- das Skript in `~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility/`
- yt-dlp, ffmpeg, ffprobe und deno (ca. 200 MB) in `~/Movies/DaVinci Downloads/` – dort landen auch die Videos

Die Programme kommen direkt von den Originalquellen: GitHub (yt-dlp, deno), osxexperts.net bzw. evermeet.cx (ffmpeg, ffprobe).

## Manuell (z. B. Windows, ungetestet)

- `Video Downloader.py` nach `%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility`
- [yt-dlp](https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp) als Einzeldatei (ohne Endung) nach `%USERPROFILE%\Videos\DaVinci Downloads\yt-dlp`
- ffmpeg, ffprobe und deno in den Unterordner `bin` daneben legen oder im PATH haben
- deno braucht YouTube für Auflösungen über 240p, ffmpeg zum Zusammenführen von Video und Ton und für „Nur Audio“

## Wenn Downloads nicht mehr gehen

YouTube und Instagram ändern regelmäßig etwas. Dann yt-dlp aktualisieren (macOS):

```bash
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/Movies/"DaVinci Downloads"/yt-dlp
```

Details zu Fehlern stehen in `~/Movies/DaVinci Downloads/yt-dlp.log`.

## Rechtliches

Nur Inhalte laden, für die du die Rechte hast oder deren Download erlaubt ist, und die Nutzungsbedingungen
der Plattformen beachten. Nutzung auf eigene Verantwortung, ohne Gewähr.
