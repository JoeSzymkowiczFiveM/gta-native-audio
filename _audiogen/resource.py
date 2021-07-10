import os, shutil,ntpath
import templates

def CreateOutline(ouputDirectory, cacheDirectory, name):
    if not os.path.isabs(ouputDirectory):
        ouputDirectory = os.path.join(os.getcwd(), ouputDirectory)


    if os.path.exists(ouputDirectory):
        shutil.rmtree(ouputDirectory)

    paths = {
        "root": ouputDirectory,
        "data": os.path.join(ouputDirectory, "data"),
        "dlc": os.path.join(ouputDirectory,  f"dlc_{name}"),
        "src": os.path.join(ouputDirectory, "src"),
        "audio": os.path.join(ouputDirectory, f"src/{name}")
    }


    for _, value in paths.items():
        os.mkdir(value)

    return paths

def CopyFromCache(cache, paths):
    output = paths["audio"]
    for soundFile in os.listdir(cache):
        shutil.move(
            os.path.join(cache, soundFile), 
            os.path.join(output, soundFile)
        )

def WriteSourceFiles(name, paths):
    manifestFile = open(os.path.join(paths["root"], "fxmanifest.lua"), "w")
    manifestFile.write(templates.GetManifestTemplate(name))
    manifestFile.close()

    soundFiles = []
    for soundFile in os.listdir(paths["audio"]):
        spl = os.path.splitext(soundFile)

        if len(spl) != 2:
            print("Found file without name, skipping " + soundFile)
            continue

        soundFiles.append([soundFile, spl[0]])

    oacFile = open(os.path.join(paths["src"], f"{name}.oac"), "w")
    oacFile.write(templates.GetOacTemplate(name, soundFiles))
    oacFile.close()

    relFile = open(os.path.join(paths["src"], f"dlc{name}_sounds.dat54.rel.xml"), "w")
    relFile.write(templates.GetRelDat54Template(name, soundFiles))
    relFile.close()

    exampleScript = open(os.path.join(paths["root"], "sounds.lua"), "w")
    exampleScript.write(templates.GetScriptExampleTemplate(name, soundFiles))
    exampleScript.close()

    return