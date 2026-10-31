-- A plain text field (codes, names, amounts): the small paper value box with a
-- TextBox, placeholder and an optional clear ✕. Same API as Kit.SearchBox.
--
--   Kit.TextField.new(page, { rect = { 0, 40, 260, 41 }, placeholder = "Enter a code", maxLength = 20,
--       clearButton = false, onSubmit = redeem })

local SearchBox = require(script.Parent.SearchBox)

local TextField = {}

-- props: as Kit.SearchBox (placeholder, text, debounce, onChanged, onSubmit,
-- maxLength, textSize, clearButton).
function TextField.new(parent: Instance, props)
	local options = table.clone(props)
	options.plain = true
	return SearchBox.new(parent, options)
end

return TextField
