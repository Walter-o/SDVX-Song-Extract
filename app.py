import os
import time
import shutil
import subprocess
from bs4 import BeautifulSoup

relativeSongFolderPath = "data/music"
relativeMusicDbPath = "data/others/music_db.xml"

# Directory to save converted music to
outputDir = "SDVX Music"

audioFormats = {
    "mp3": "MP3 V0       (verly gud bang for your disk space buck)",
    "wav": "WAV 1411kbps (only choose this if you hate .ASF format)",
    "asf": "ASF VBR      (Original, lol .s3v is just .asf but renamed)"
    }

# Credits to giltay @ stackoverflow 120656
def listdirFP(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

# Friendly interface to use the program
def CLI():
    print("Welcome to Walter's SDVX song extractor")
    # Fetch game folder path
    while True:
        gameFolder = input("Insert path to SDVX folder > ")
        if os.path.exists(gameFolder):
            #check if user entered parent folder instead
            if "contents" in os.listdir(gameFolder):
                gameFolder = os.path.join(gameFolder, "contents")

            #prioritise modules folder
            checkPath = os.path.join(gameFolder, "modules") if ("modules" in os.listdir(gameFolder)) else gameFolder
            
            if "soundvoltex.dll" in (os.listdir(checkPath)):
                print("OK, that path looks legit, yesssss")
                break
            else:
                print("I can't see any soundvoltex.dll here :C")
        else:
            print(f"Invalid folder entered:  \"{gameFolder}\"", end="\n\n")
    # Fetch audio format choice
    while True:
        print("Choose your format!\n", "-"*30)
        for i, audioFormat in audioFormats.items():
            print("%s = %s}" % (i, audioFormat))
        format = input("> ")
        if format in audioFormats.keys():
            print("OK starting...")
            break
        else:
            print("no")
    return gameFolder, format

# Gets list of all full relative paths to wanted .s3v files
def getSongPaths(gameFolder):
    songPaths = []
    songsFolder = os.path.join(gameFolder, relativeSongFolderPath)
    for songFolder in listdirFP(songsFolder):
        if os.path.isdir(songFolder):
            for filename in listdirFP(songFolder):
                if filename.endswith(".s3v") and not filename.endswith("_pre.s3v"):
                    songPaths.append(filename)
    return songPaths

# Convert and-or copy songs and place them in music directory
def extractSongs(songPaths, format, metadatas):
    outputFolder = os.path.join(outputDir, format)
    if not os.path.exists(outputFolder):
        os.makedirs(outputFolder)
    cmd = {
        "wav": '''ffmpeg.exe -i "%s" -id3v2_version 3 -metadata title="%s" -metadata author="%s" -metadata genre="%s" "%s"''',
        "mp3": '''ffmpeg.exe -i "%s" -id3v2_version 3 -metadata title="%s" -metadata artist="%s" -metadata genre="%s" -q:a 0 "%s"''',
        "asf": False
        }[format]
    for songPath in songPaths:
        filename = os.path.basename(songPath)
        outputFile = os.path.join(outputFolder, filename[:-3] + format)
        if not os.path.exists(outputFile):
            songId = filename.split("_")[0]
            metadata = metadatas[int(songId)]
            subprocess.call(cmd % (
                songPath, 
                metadata["title"], metadata["author"], metadata["genre"],
                outputFile,
                ), shell=True) \
            if cmd else shutil.copy2(songPath, outputFile)


def extractSongsMetadata(songPaths, gameFolder):
    metadatas={}
    songIds = [int(os.path.basename(filename).split("_")[0]) for filename in songPaths]

    with open(os.path.join(gameFolder, relativeMusicDbPath), "r", encoding="Shift-JIS", errors="ignore") as xmlFile:
        soup = BeautifulSoup(xmlFile.read(), "lxml")

    metas = soup.find_all("music")
    for meta in metas:
        metadatas[int(meta["id"])] = {
            "title": meta.find("title_name").text,
            "author": meta.find("artist_name").text,
            "genre": meta.find("genre").text
            }
    return metadatas

def main():
    gameFolder, format = CLI()
    songPaths = getSongPaths(gameFolder)
    metadatas = extractSongsMetadata(songPaths, gameFolder)
    extractSongs(songPaths, format, metadatas)

main()
