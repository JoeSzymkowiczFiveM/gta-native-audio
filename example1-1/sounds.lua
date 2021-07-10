local i = 1
local sounds = {
	'example2_borgir',
	'example2_bruh',
	'example2_da_way',
	'example2_doesnt_know_tda_way',
	'example2_fuckoff',
	'example2_ja_pierdole_kurwa',
}

Citizen.CreateThread(function() 
    while true do
        if IsControlJustPressed(0, 51) then --e
            PlaySoundFrontend(-1, sounds[i], "dlc_example2_sounds", 1)
            print(sounds[i])
            i = i + 1

            if i > #sounds then 
                i = 1
            end
        end
        
        Citizen.Wait(0)
    end
end)

RequestScriptAudioBank('dlc_example2/example2', 0)
