import subprocess, os, shutil, re

def __RunProcess(commandArray):
    try:
        proc = subprocess.Popen(commandArray, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, header = proc.communicate()

        return str(output), str(header) #For some reason ffmpeg and ffprobe dumps their header into the error stream...
    except:
        return "", ""


def __BuildProcessOptions(base, **kwargs):
    cmdArray = [ base ]

    for key, val in kwargs.items():
        if type(val) is list:
            if key == "map": #resolve the file mapping, which is a list of [map_name, output_file].
                for mapObj in val:
                    cmdArray.append("-map")
                    cmdArray.append(mapObj[0])
                    cmdArray.append(mapObj[1])

        elif type(val) is str:
            if key == "output":
                cmdArray.append(val)
            else:
                cmdArray.append("-" + key)
                if val: cmdArray.append(val)

    return cmdArray

def __RunFfprobe(**kwargs):
    cmdArray = __BuildProcessOptions("ffprobe", **kwargs)
    return __RunProcess(cmdArray)

def __RunFfmpeg(**kwargs):
    cmdArray = __BuildProcessOptions("ffmpeg", **kwargs)
    return __RunProcess(cmdArray)

def CheckPrerequisites():
    try:
        ffmpegArray = __BuildProcessOptions("ffmpeg")
        _, ffmpegHeader =__RunProcess(ffmpegArray)

        if not "ffmpeg version" in ffmpegHeader:
            return False

        ffprobeArray = __BuildProcessOptions("ffprobe")
        _, ffprobeHeader = __RunProcess(ffprobeArray)

        if not "ffprobe version" in ffprobeHeader:
            return False

        return True
    except:
        return False

def GetExtensionsSupported():
    eligibleFormats = []

    codecsOuput, _ = __RunFfmpeg(hide_banner="",formats="")
    codecLineList = re.sub(" +", " ", codecsOuput).split("\\r\\n")[4::]

    for line in codecLineList:
        lineSplit = line.strip().split(" ")

        if len(lineSplit) < 2:
            continue

        capability = lineSplit[0]
        extensions = lineSplit[1].split(",")

        if all(x in capability for x in [ "D" ]): # Match all the capabillity string where D, E and A are present.
            eligibleFormats.extend(extensions)

    print("Found " + str(len(eligibleFormats)) + " eligible audio formats")
    return eligibleFormats

def __AudioMetadata(file):
    output, _ = __RunFfprobe(i=file, show_streams="")

    metadataRaw = str(output).split("\\r\\n")

    codec = "unknown"
    channels = 0
    layout = "unknown"

    for entry in metadataRaw:
        kvp = entry.split("=")

        if(kvp[0] == "codec_name"):
            codec = kvp[1]
        elif(kvp[0] == "channels"):
            channels = kvp[1]
        elif(kvp[0] == "channel_layout"):
            layout = kvp[1]

    return {
        "codec": codec,
        "channels": channels,
        "layout": layout #for most files this seems to be "unknown", kinda of useless tracking this.
    }

def __ToPCM(srcFile, name, dstDir):
    
    outputDirectory = os.path.join(dstDir, name + ".wav")

    __RunFfmpeg(
        i=srcFile,
        acodec="pcm_s16le",
        #ar="22050",
        ac="1",
        output=outputDirectory
    )

def __SplitStereo(srcFile, name, dstDir):
    leftOutput = os.path.join(dstDir, name + "_left.conv.wav")
    rightOutput = os.path.join(dstDir, name + "_right.conv.wav")

    __RunFfmpeg(
        i=srcFile, 
        filter_complex="channelsplit=channel_layout=stereo[l][r]", 
        map=[["[l]", leftOutput], ["[r]", rightOutput]]
    )

    return leftOutput, rightOutput


def __Duplicate(srcFile, name, dstDir):
    leftFile = os.path.join(dstDir, name + "_left.conv.wav")
    rightFile = os.path.join(dstDir, name + "_right.conv.wav")
    shutil.copy(srcFile, leftFile)
    shutil.copy(srcFile, rightFile)

    return leftFile, rightFile


def TryAndConvertToSuitableFormat(i, imax, srcFile, name, cacheDir):
    meta = __AudioMetadata(srcFile)

    ops = 0
    status = lambda op, opCount : (
        print(f"[{i}/{imax}] <{opCount}> {op.ljust(13)} {'->'.ljust(3)} {name}")
    )

    leftFile = ""
    rightFile = ""

    if int(meta["channels"]) >= 2:
        ops += 1; status("Split", ops)
        leftFile, rightFile = __SplitStereo(srcFile, name, cacheDir)
    else:
        ops += 1; status("Duplicate", ops)
        leftFile, rightFile = __Duplicate(srcFile, name, cacheDir)


    if leftFile:
        leftMeta = __AudioMetadata(leftFile)

        if leftMeta["codec"] != "pcm_s16le" or leftMeta["layout"] != "unknown":
            ops += 1; status("Convert Left", ops)
            __ToPCM(leftFile, f"{name}_left", cacheDir)
            os.remove(leftFile)
        else:
            shutil.move(leftFile, os.path.join(cacheDir, f"{name}_left.wav"))

    if rightFile:
        rightMeta = __AudioMetadata(rightFile)

        if rightMeta["codec"] != "pcm_s16le" or rightMeta["layout"] != "unknown":
            ops += 1; status("Convert Right", ops)
            __ToPCM(rightFile, f"{name}_right", cacheDir)
            os.remove(rightFile)
        else: 
            shutil.move(rightFile, os.path.join(cacheDir, f"{name}_right.wav"))