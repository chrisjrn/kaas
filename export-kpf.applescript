--==============================
-- Send Keynote Presenter Notes to Evernote
-- Version 1.0.0
-- Written By: Ben Waldie <ben@automatedworkflows.com>
-- http://www.automatedworkflows.com
--==============================

-- Make sure a presentation is opened in Keynote. If not, notify the user and stop.
tell application "Keynote"
	if (front slideshow exists) = false then
		display alert "Unable to proceed." message "Please open a presentation in Keynote."
		return
	end if
	
	export front slideshow to "/Users/chrisjrn/Desktop/Keynote Export.KPF" as KPF_RAW
	
end tell
