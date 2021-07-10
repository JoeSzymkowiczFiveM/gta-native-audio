import os
import hash

def __FormatTemplate(template, **kwargs):
    formattedTemplate = template
    for key, val in kwargs.items():
        formattedTemplate = formattedTemplate.replace(f"$${key}$$", val)
    
    return formattedTemplate

def GetManifestTemplate(name):
    manifestTemplate = """
fx_version 'cerulean'
games { 'gta5' }

files {
    "data/dlc$$name$$_sounds.dat54.rel",
    "dlc_$$name$$/$$name$$.awc"
}

client_scripts {
    'sounds.lua'
}

data_file 'AUDIO_WAVEPACK' 'dlc_$$name$$'
data_file 'AUDIO_SOUNDDATA' 'data/dlc$$name$$_sounds.dat'
    """

    return __FormatTemplate(manifestTemplate, name=name)

def GetOacTemplate(name, files):
    oacOutline = """Version 1 11
{
\tIsStream False
\tDescriptorsInOrder False	
\tEntries
\t{\t\t$$entries$$
\t}
}
    """

    oacEntry = """
\t\tWaveTrack $$soundname$$
\t\t{
\t\t\tCompression PCM
\t\t\tHeadroom 161
\t\t\tLoopPoint -1
\t\t\tLoopBegin 0
\t\t\tLoopEnd 0
\t\t\tPlayBegin 0
\t\t\tPlayEnd 0
\t\t\tWave $$dirname$$\$$file$$
\t\t\tAnimClip null
\t\t\tEvents null
\t\t\tUNKNOWN_23097A2B null
\t\t\tUNKNOWN_E787895A null
\t\t\tUNKNOWN_252C20D9 null
\t\t}"""

    entriesContent = ""

    for soundFullName, soundActualName in files:
        entry = __FormatTemplate(
            oacEntry, 
            soundname=soundActualName.upper(), 
            dirname=name,
            file=soundFullName
        )

        entriesContent = entriesContent + entry

    oac = __FormatTemplate(oacOutline, entries=entriesContent)
    return oac

def GetRelDat54Template(name, files):
    relOutline = """<?xml version="1.0" encoding="UTF-8"?>
<Dat54>
 <Version value="7314721" />
 <NameTable>
  <Item>dlc_$$name$$\$$name$$</Item>
 </NameTable>
 <Items>$$leftsounds$$$$rightsounds$$$$soundset$$$$multitracks$$
 </Items>
</Dat54>
    """

    relLeftSound = """
  <Item type="SimpleSound">
   <Name>dlc_$$name$$_$$soundleftname$$</Name>
   <Header>
    <Flags value="0x00000040" />
    <Unk06 value="270" />
   </Header>
   <ContainerName>dlc_$$name$$/$$name$$</ContainerName>
   <FileName>$$soundleft$$</FileName>
   <WaveSlotNum value="0" />
  </Item>"""

    relRightSound = """
  <Item type="SimpleSound">
   <Name>dlc_$$name$$_$$soundrightname$$</Name>
   <Header>
    <Flags value="0x00000040" />
    <Unk06 value="90" />
   </Header>
   <ContainerName>dlc_$$name$$/$$name$$</ContainerName>
   <FileName>$$soundright$$</FileName>
   <WaveSlotNum value="0" />
  </Item>"""

    relSoundSet = """
  <Item type="SoundSet">
   <Name>dlc_$$name$$_sounds</Name>
   <Header>
    <Flags value="0xAAAAAAAA" />
   </Header>
   <Items>$$soundsetitems$$
   </Items>
  </Item>"""

    relSoundSetItem = """
    <Item>
     <ScriptName>$$fullscriptname$$</ScriptName>
     <SoundName>dlc_$$fullscriptname$$_mt</SoundName>
    </Item>"""

    relMultiTrack = """
  <Item type="MultitrackSound">
   <Name>dlc_$$name$$_$$scriptname$$_mt</Name>
   <Header>
    <Flags value="0x00008005" />
    <Flags2 value="0xAAA0AAAA" />
    <Unk02 value="65236" />
    <Category>hash_02C7B342</Category>
   </Header>
   <AudioTracks>
    <Item>dlc_$$name$$_$$soundrightname$$</Item>
    <Item>dlc_$$name$$_$$soundleftname$$</Item>
   </AudioTracks>
  </Item>"""

    leftSoundsItems = ""
    rightSoundsItems = ""
    soundSet = ""
    soundSetList = []
    soundSetItems = ""
    multiTrackItems = ""
    
    dedupedSoundFiles = []

    for  _, soundActualName in files:
        soundleftname = soundActualName.replace("_left", "_l")
        soundrightname = soundActualName.replace("_right", "_r")
        thename = soundActualName.replace("_right", "").replace("_left", "")

        if not thename in dedupedSoundFiles:
            dedupedSoundFiles.append(thename)

        if "left" in soundActualName:
            leftSoundsItems += __FormatTemplate(relLeftSound, 
                name=name, 
                soundleft=soundActualName,
                soundleftname=soundleftname
            )
        elif "right" in soundActualName:
            rightSoundsItems += __FormatTemplate(relRightSound, 
                name=name, 
                soundright=soundActualName,
                soundrightname=soundrightname
            )

    for soundName in dedupedSoundFiles:
        fullName = f"{name}_{soundName}"
        soundSetList.append(fullName)

        multiTrackItems += __FormatTemplate(relMultiTrack,
            name=name,
            soundleftname=f"{soundName}_l",
            soundrightname=f"{soundName}_r",
            scriptname=soundName
        )

    soundSetList.sort(key=lambda x: hash.joaat_hash_hex_fill(x, 32))

    for soundSetItem in soundSetList:
        print(soundSetItem, hash.joaat_hash_hex_fill(soundSetItem, 12))

        soundSetItems += __FormatTemplate(relSoundSetItem,
            name=name,
            fullscriptname=soundSetItem,
        )

    soundSet = __FormatTemplate(relSoundSet, 
        name=name,
        soundsetitems=soundSetItems
    )

    return __FormatTemplate(relOutline,
        name=name,
        leftsounds=leftSoundsItems,
        rightsounds=rightSoundsItems,
        soundset=soundSet,
        multitracks=multiTrackItems
    )

def GetScriptExampleTemplate(name, soundFiles):
    scriptTemplate = """local i = 1
local sounds = {
$$soundnames$$}

Citizen.CreateThread(function() 
    while true do
        if IsControlJustPressed(0, 51) then --e
            PlaySoundFrontend(-1, sounds[i], "$$soundset$$", 1)
            print(sounds[i])
            i = i + 1

            if i > #sounds then 
                i = 1
            end
        end
        
        Citizen.Wait(0)
    end
end)

RequestScriptAudioBank('dlc_$$name$$/$$name$$', 0)
"""


    soundNames = ""
    dedupeList = []

    for  _, soundActualName in soundFiles:
        scriptName = soundActualName.replace("_right", "").replace("_left", "")
        
        if not scriptName in dedupeList:
            dedupeList.append(scriptName)
        else:
            soundNames += f"\t'{name}_{scriptName}',\n"

    return __FormatTemplate(scriptTemplate, 
        name=name,
        soundset=f"dlc_{name}_sounds",
        soundnames=soundNames,
    )