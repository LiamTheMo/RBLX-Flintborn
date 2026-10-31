-- Hooks for scenes and verifiers: walk the kit components under a root and
-- force their drawn state through the DebugState attribute.
--
--   Kit.Debug.Force(button.root, "pressed")
--   Kit.Debug.Each(window.root, function(root) print(root:GetAttribute("KitRole")) end)

local Debug = {}

-- Calls fn(root) for every descendant of `root` (and root itself) carrying the
-- KitComponent attribute.
function Debug.Each(root: Instance, fn: (Instance) -> ())
	if root:GetAttribute("KitComponent") then
		fn(root)
	end
	for _, item in root:GetDescendants() do
		if item:GetAttribute("KitComponent") then
			fn(item)
		end
	end
end

-- Forces `state` on a component root ("" or nil returns it to live input).
function Debug.Force(root: Instance, state: string?)
	root:SetAttribute("DebugState", state)
end

-- Every component root under `root` whose KitRole is `role`.
function Debug.Find(root: Instance, role: string): { Instance }
	local found = {}
	Debug.Each(root, function(item)
		if item:GetAttribute("KitRole") == role then
			table.insert(found, item)
		end
	end)
	return found
end

return Debug
