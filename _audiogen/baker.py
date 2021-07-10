#!/usr/bin/python
import os, sys, getopt, shutil, ntpath
import audio, resource

def CreateResourceFiles(params):
    output = params["output"]
    cache = params["cache"]
    name = params["name"]

    paths = resource.CreateOutline(output, cache, name)
    resource.CopyFromCache(cache, paths)
    resource.WriteSourceFiles(name, paths)

    return params


def ProcessFileByFfmpeg(params):
    cache = params["cache"]
    files = params["files"]

    filesMax = len(files)
    filesCurrent = 1

    for file in files:
        #if filesCurrent > 3: break
        fileName = os.path.splitext(ntpath.basename(file))[0]

        audio.TryAndConvertToSuitableFormat(
            filesCurrent, filesMax,
            file, fileName, cache,
        )

        filesCurrent = filesCurrent + 1

    return params

def EnumerateInputDirectoryFiles(params):
    inputDir = params["input"]
    extensions = params["extensions"]

    soundFiles = []
    for item in os.listdir(inputDir):
        itemPath = os.path.join(inputDir, item)
        itemExt = os.path.splitext(item)[1].replace(".", "")

        if not itemExt in extensions:
            print("Ineligible file found: " + item)
            continue

        if os.path.isfile(itemPath):
            soundFiles.append(itemPath)


    if len(soundFiles) == 0:
        CrashAndBurn(4, "Given directory doesn't have any suitable files to use.")

    print("Found " + str(len(soundFiles)) + " sound files")
    params["files"] = soundFiles
    return params


def CreateCacheFolder(params):
    cacheDir = os.path.join(os.getcwd(), "cache")

    if os.path.exists(cacheDir):
        shutil.rmtree(cacheDir)
    
    os.mkdir(cacheDir)

    params["cache"] = cacheDir

    print("Cache directory is " + cacheDir)

    return params

def NotifyIncorrectUsage(reason):
    print("baker.py [--in, -i] <input directory> [--out, -o] <output directory> [--name, -n] <name>")
    print("Fail reason: " + reason)
    sys.exit(1)

def CrashAndBurn(code, reason):
    print("baker.py encountered an issue while executing.")
    print("Fail reason: " + reason)
    sys.exit(code)

def main(argv):
    params = {
        "input": "",
        "output": "",
        "name": "",
        "cache": "",
        "files": "",
        "extensions": audio.GetExtensionsSupported()
    }

    try:
        opts, _ = getopt.getopt(argv, "i:n:o:", [ "in=", "name=", "out=" ])
    except getopt.GetoptError:
        NotifyIncorrectUsage("error during parsing of arguments.")

    argCount = 0

    for opt, arg in opts:
        if opt in ("-i", "--in"):
            params["input"] = arg
            argCount += 1
        elif opt in ("-n", "--name"):
            params["name"] = arg
            argCount += 1
        elif opt in ("-o", "--out"):
            params["output"] = arg 
            argCount += 1
    
    if argCount < 3:
        NotifyIncorrectUsage("Missing required arguments.")
    
    if os.path.exists(params["input"]) == False:
        CrashAndBurn(5, "Input folder does not exist.")

    print("Parameters are OK")

    params = CreateCacheFolder(params)
    params = EnumerateInputDirectoryFiles(params)
    params = ProcessFileByFfmpeg(params)
    params = CreateResourceFiles(params)
    
if __name__ == "__main__":
    didFindReqs = audio.CheckPrerequisites();

    if not didFindReqs:
        CrashAndBurn(2, "No ffmpeg or ffprobe installation found. Please install ffmpeg suite and add it to your PATH varible.\n\tTo sanity check, open up a command line and enter 'ffmpeg' and 'ffprobe' to see if it are valid commands.")

    main(sys.argv[1::])
