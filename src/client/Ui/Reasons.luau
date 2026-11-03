-- Player-facing text for server refusal codes (shared/UI/ReasonText: a short
-- lower-case clause for every code the server returns). A code without a line
-- reads as the generic "that didn't work", never as the raw code.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ReasonText = require(ReplicatedStorage.Shared.UI.ReasonText)

local Reasons = {}

-- True when `code` has its own line (screens with their own wording for some
-- codes ask before falling back to the generic one).
function Reasons.Has(code: any): boolean
	return ReasonText.Has(code)
end

-- The clause for `code` ("you're too far away").
function Reasons.Text(code: any): string
	return ReasonText.Text(code)
end

-- The clause as a sentence ("You're too far away.").
function Reasons.Sentence(code: any): string
	return ReasonText.Sentence(code)
end

return Reasons
