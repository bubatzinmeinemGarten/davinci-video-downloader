# Video Downloader: URL -> yt-dlp -> Media Pool Bin "Downloader"
# Ablegen unter: .../Fusion/Scripts/Utility/  (Workspace > Scripts > Video Downloader)
import os, sys, subprocess
from pathlib import Path

DL = Path.home() / ("Movies" if sys.platform == "darwin" else "Videos") / "DaVinci Downloads"
YTDLP = DL / "yt-dlp"  # Einzeldatei: github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp
LOG = DL / "yt-dlp.log"
BIN = "Downloader"

# yt-dlp läuft im Subprozess mit Resolves eigenem Python (ab 21.1): Python-Threads bekommen neben der
# UI-Schleife (RunLoop) kaum Rechenzeit, ein Download im Thread würde praktisch stehen.
PY = next((p for p in ["/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolvePython",
                       r"C:\Program Files\Blackmagic Design\DaVinci Resolve\ResolvePython\ResolvePython.exe",
                       "/opt/resolve/bin/ResolvePython"] if os.path.exists(p)), "python3")

# ffmpeg, ffprobe, deno: aus "bin" neben yt-dlp; Resolve aus dem Finder/Dock kennt den Homebrew-PATH nicht
os.environ["PATH"] += os.pathsep + os.pathsep.join([str(DL / "bin"), "/opt/homebrew/bin", "/usr/local/bin"])

def video(h):  # H.264 + AAC bevorzugen (Resolve-kompatibel); "res" = kürzere Seite, klappt auch bei Hochkant
    return ["-f", "bv*+ba/b", "-S", f"vcodec:h264,res:{h},acodec:aac", "--merge-output-format", "mp4"]

def audio(codec):
    return ["-f", "ba/b", "-x", "--audio-format", codec]

FORMATS = {"MP4 1080p": video(1080), "MP4 720p": video(720),
           "Nur Audio (WAV)": audio("wav"), "Nur Audio (MP3)": audio("mp3")}

job = {}  # laufender yt-dlp-Prozess + Fortschritt

def num(s):
    try:
        return float(s)
    except ValueError:  # yt-dlp schreibt "NA" für unbekannte Werte
        return None

def import_media(paths):
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return "Download fertig, aber kein Projekt offen: " + paths[0]
    mp = project.GetMediaPool()
    root = mp.GetRootFolder()
    folder = next((f for f in root.GetSubFolderList() if f.GetName() == BIN), None) or mp.AddSubFolder(root, BIN)
    mp.SetCurrentFolder(folder)
    if mp.ImportMedia(paths):
        return f"Fertig: {len(paths)} Datei(en) im Bin „{BIN}“."
    return "Download fertig, Import fehlgeschlagen: " + paths[0]

ui = fusion.UIManager
disp = bmd.UIDispatcher(ui)
win = disp.AddWindow({"ID": "Dl", "WindowTitle": "Video Downloader", "Geometry": [300, 300, 520, 200]}, ui.VGroup([
    ui.LineEdit({"ID": "Url", "PlaceholderText": "YouTube- / Instagram- / TikTok-Link einfügen"}),
    ui.ComboBox({"ID": "Fmt"}),
    ui.Button({"ID": "Go", "Text": "Download && Import"}),  # "&&" = ein sichtbares "&" (Qt-Shortcut-Zeichen)
    ui.Slider({"ID": "Bar", "Minimum": 0, "Maximum": 100, "Value": 0, "Enabled": False, "Orientation": "Horizontal",  # Slider als Ladebalken
               "StyleSheet": "QSlider::groove:horizontal{height:10px;background:#3a3a3a;border-radius:5px;}"
                             "QSlider::sub-page:horizontal{background:#4a9df8;border-radius:5px;}"
                             "QSlider::handle:horizontal{width:0px;margin:0px;}"}),
    ui.Label({"ID": "Status", "Text": "Bereit.", "WordWrap": True}),
]))
itm = win.GetItems()
for name in FORMATS:
    itm["Fmt"].AddItem(name)

def go(ev):
    url = itm["Url"].Text.strip()
    if not url:
        return
    DL.mkdir(parents=True, exist_ok=True)
    if not YTDLP.exists():
        itm["Status"].Text = f'yt-dlp fehlt. Terminal: curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o "{YTDLP}"'
        return
    fmt = itm["Fmt"].CurrentText  # steht im Dateinamen, sonst meldet yt-dlp bei anderer Auflösung "schon geladen"
    cmd = [PY, str(YTDLP), *FORMATS[fmt], "--no-playlist", "--no-color", "--newline", "--progress",  # --print schaltet sonst alle Fortschrittszeilen ab
           "-o", str(DL / f"%(title).80B [%(id)s] {fmt}.%(ext)s"),
           "--progress-template", "download:PROG %(progress.downloaded_bytes)s %(progress.total_bytes)s %(progress.total_bytes_estimate)s",
           "--progress-template", "postprocess:POST %(progress.postprocessor)s",
           "--print", "before_dl:TOTAL %(filesize,filesize_approx)s", "--print", "after_move:FILE %(filepath)s", url]
    try:
        with LOG.open("w") as log:
            job.update(done=0.0, prev=0.0, st=0.0)  # Bytes fertiger Ströme (Video, dann Ton), letzter Stand, Größe des letzten Stroms
            job["p"] = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUTF8": "1"},
                                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except OSError as e:
        itm["Status"].Text = f"Fehler: Python für yt-dlp nicht startbar ({e})"
        return
    itm["Go"].Enabled = False
    itm["Bar"].Value = 0
    itm["Status"].Text = "Starte…"

def tick(ev):  # alle 300 ms im Hauptthread: Fortschritt lesen, am Ende importieren
    p = job.get("p")
    if not p:
        return
    done = p.poll() is not None
    lines = LOG.read_text(encoding="utf-8", errors="replace").splitlines()  # Resolves GUI-Prozess hat oft kein UTF-8 als Standard
    if not done:
        if any(l.startswith("POST ") for l in lines):  # ffmpeg-Nachbearbeitung (Zusammenführen, Audio umwandeln)
            itm["Bar"].Value, itm["Status"].Text = 100, "Verarbeite (ffmpeg)…"
            return
        total = next((num(l[6:]) for l in lines if l.startswith("TOTAL ")), None)  # Video + Ton, bei Instagram unbekannt
        prog = next((l.split()[1:] for l in reversed(lines) if l.startswith("PROG ")), None)
        if prog and num(prog[0]) is not None:
            cur, size = num(prog[0]), num(prog[1]) or num(prog[2])
            if cur < job["prev"]:  # neuer Strom hat begonnen: den fertigen verbuchen
                job["done"] += job["st"]
            job["prev"], job["st"] = cur, size or cur
            frac = (job["done"] + cur) / total if total else (cur / size if size else 0)
            itm["Bar"].Value = min(int(frac * 100), 99)
            itm["Status"].Text = f"Download läuft… {itm['Bar'].Value}%"
        return
    job.clear()
    paths = [f for f in (l[5:] for l in lines if l.startswith("FILE ")) if os.path.exists(f)]  # ohne ffmpeg wird nie zusammengeführt
    if p.returncode == 0 and paths:
        itm["Bar"].Value = 100
        itm["Status"].Text = import_media(paths)
    elif any("ffmpeg" in l for l in lines):
        itm["Status"].Text = f"Fehler: ffmpeg/ffprobe fehlt. Datei(en) nach {DL / 'bin'} legen oder per brew installieren."
    else:
        itm["Status"].Text = "Fehler: " + next((l for l in reversed(lines) if l.startswith("ERROR")), "siehe yt-dlp.log")[:250]
    itm["Go"].Enabled = True

def close(ev):
    if job.get("p"):
        job["p"].terminate()
    disp.ExitLoop()

disp.On.Timeout = tick
timer = ui.Timer({"ID": "Poll", "Interval": 300, "Events": {"Timeout": True}})
timer.Start()
win.On.Go.Clicked = go
win.On.Dl.Close = close
win.Show()
disp.RunLoop()
win.Hide()
