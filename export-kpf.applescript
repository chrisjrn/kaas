--==============================
-- Exports the frontmost keynote file to a kpf 
--==============================

-- Make sure a presentation is opened in Keynote. If not, notify the user and stop.
on run argv
	tell application "Keynote"
		if (front slideshow exists) = false then
			display alert "Unable to proceed." message "Please open a presentation in Keynote."
			return 1
		end if
		
		export front slideshow to (item 1 of argv) as KPF_RAW
		return 0
		
	end tell
end run