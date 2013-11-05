--==============================
-- Script for showing the previous keynote slide 
--==============================

-- Make sure a presentation is opened in Keynote. If not, notify the user and stop.
tell application "Keynote"
	if (front slideshow exists) = false then
		display alert "Unable to proceed." message "Please open a presentation in Keynote."
		return
	end if
		
	show previous

	slide number of current slide of front slideshow

end tell
