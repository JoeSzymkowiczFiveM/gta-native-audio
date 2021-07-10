local i = 1
local sounds = {
	'example3_bananaphone',
}

Citizen.CreateThread(function() 
    while true do
        if IsControlJustPressed(0, 51) then --e
            PlaySoundFrontend(-1, sounds[i], "dlc_example3_sounds", 1)
            print(sounds[i])
            i = i + 1

            if i > #sounds then 
                i = 1
            end
        end
        
        Citizen.Wait(0)
    end
end)

while not RequestScriptAudioBank('dlc_example3/example3', 0) do
    print("Audio bank not loaded.")
    Citizen.Wait(10)
end
