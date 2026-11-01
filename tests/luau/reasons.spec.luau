-- Refusal codes reach players as words (src/shared/UI/ReasonText.luau): every
-- code a server service or shared rule returns (scanned from the source by
-- run.py into __SERVER_REFUSAL_CODES) has a line, and an unknown code reads
-- as the generic fallback, never as the raw code.

local ReasonText = require(game:GetService("ReplicatedStorage").Shared.UI.ReasonText)

test("the scan found the server's refusal codes", function()
	expect(type(__SERVER_REFUSAL_CODES) == "table", "run.py passes the scanned codes")
	expect(#__SERVER_REFUSAL_CODES >= 50, ("found %d codes"):format(#__SERVER_REFUSAL_CODES))
	expect(table.find(__SERVER_REFUSAL_CODES, "TooFar") ~= nil, "TooFar is among them")
end)

test("every code the server returns has player-facing text", function()
	local missing = {}
	for _, code in __SERVER_REFUSAL_CODES do
		if not ReasonText.Has(code) then
			table.insert(missing, code)
		end
	end
	expect(#missing == 0, "codes without text: " .. table.concat(missing, ", "))
end)

test("lines are short clauses in characters Merriweather has", function()
	for code, text in ReasonText.TEXT do
		expect(#text > 0 and #text <= 90, code .. " has a short line")
		expect(not string.find(text, "%.$"), code .. " ends without a full stop (screens add their own)")
		expect(not string.find(text, "★") and not string.find(text, "→"), code .. " uses no ★ or →")
		expect(text ~= code, code .. " is not just the code")
	end
end)

test("an unknown code reads as the generic fallback, never the raw code", function()
	expectEq(ReasonText.Text("SomethingNew"), "that didn't work", "unknown code")
	expectEq(ReasonText.Text(nil), "that didn't work", "no code")
	expectEq(ReasonText.Text(42), "that didn't work", "not a string")
	expectEq(ReasonText.Text("TooFar"), "you're too far away", "a known code")
	expectEq(ReasonText.Sentence("SomethingNew"), "That didn't work.", "as a sentence")
	expectEq(ReasonText.Sentence("TooFar"), "You're too far away.", "a known code as a sentence")
end)
