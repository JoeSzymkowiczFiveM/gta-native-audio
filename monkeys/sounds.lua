local i = 1
local sounds = {
	'piggybank_oinkoink',
}

Citizen.CreateThread(function() 
    while not RequestScriptAudioBank('dlc_piggybank/piggybank', 0) do
        print("Still requesting script bank...." .. tostring(RequestScriptAudioBank('dlc_piggybank/piggybank', 1)))
        Citizen.Wait(10)
    end
    
    while true do
        if IsControlJustPressed(0, 51) then --e
            PlaySoundFrontend(-1, sounds[i], "dlc_piggybank_sounds", 1)
            print(sounds[i])
            i = i + 1

            if i > #sounds then 
                i = 1
            end
        end
        
        Citizen.Wait(0)
    end
end)
