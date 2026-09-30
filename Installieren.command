#!/bin/bash
# Installiert den Video Downloader für DaVinci Resolve (macOS).
# Lädt yt-dlp, ffmpeg, ffprobe und deno direkt von den Originalquellen.
set -e
cd "$(dirname "$0")"
SCRIPTS="$HOME/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Scripts/Utility"
DL="$HOME/Movies/DaVinci Downloads"
ARCH="${ARCH:-$(uname -m)}"
mkdir -p "$SCRIPTS" "$DL/bin"

echo "1/4 Skript installieren"
cp "Video Downloader.py" "$SCRIPTS/"

echo "2/4 yt-dlp laden"
curl -fL# -o "$DL/yt-dlp" https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp

if [ "$ARCH" = "arm64" ]; then
  DENO=https://github.com/denoland/deno/releases/latest/download/deno-aarch64-apple-darwin.zip
  FFMPEG=https://www.osxexperts.net/ffmpeg80arm.zip
  FFPROBE=https://www.osxexperts.net/ffprobe80arm.zip
else
  DENO=https://github.com/denoland/deno/releases/latest/download/deno-x86_64-apple-darwin.zip
  FFMPEG=https://evermeet.cx/ffmpeg/getrelease/ffmpeg/zip
  FFPROBE=https://evermeet.cx/ffmpeg/getrelease/ffprobe/zip
fi

fetch() {  # Name URL
  echo "$3 $1 laden"
  curl -fL# -o "$DL/bin/$1.zip" "$2"
  unzip -o -q "$DL/bin/$1.zip" "$1" -d "$DL/bin"
  rm "$DL/bin/$1.zip"
  chmod +x "$DL/bin/$1"
}
fetch deno "$DENO" "3/4"
fetch ffmpeg "$FFMPEG" "4/4"
fetch ffprobe "$FFPROBE" "4/4"

echo
"$DL/bin/deno" --version | head -1
"$DL/bin/ffmpeg" -version | head -1
echo
echo "Fertig. DaVinci Resolve neu starten, dann: Workspace > Scripts > Video Downloader"
echo "Heruntergeladene Videos liegen in: $DL"
read -n 1 -s -r -p "Beliebige Taste zum Schließen…"
