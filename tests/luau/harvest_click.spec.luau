local Shared = game:GetService("ReplicatedStorage").Shared
local HarvestRules = require(Shared.Resources.HarvestRules)
local NodeCatalog = require(Shared.Resources.NodeCatalog)

local ORIGIN = Vector3.new(0, 3, 0)
local NORTH = Vector3.new(0, 0, -1)

-- A node standing on the ground (y = 0) at (x, z) with a w × h × d box.
local function node(x: number, z: number, w: number, h: number, d: number, active: boolean?)
	return {
		center = Vector3.new(x, h / 2, z),
		half = Vector3.new(w / 2, h / 2, d / 2),
		active = active,
	}
end

test("reach is measured to the hitbox surface, not its centre", function()
	-- A wide rock whose centre is 9 studs away but whose face is 4 away.
	local rock = node(0, -9, 10, 4, 10)
	expectNear(HarvestRules.SurfaceDistance(ORIGIN, rock.center, rock.half), 4, 1e-9, "face distance")
	local picked = HarvestRules.Pick(ORIGIN, NORTH, HarvestRules.Reach(5), { rock })
	expect(picked == rock, "a hand swing reaches the big rock's face")
	-- The same centre distance with a thin node is out of reach.
	local twig = node(0, -9, 1, 4, 1)
	expect(HarvestRules.Pick(ORIGIN, NORTH, HarvestRules.Reach(5), { twig }) == nil, "the thin node is too far")
	-- Height counts too: the top of a short node below the root is still close.
	local mushrooms = node(0, -2, 2, 2, 2)
	expectNear(HarvestRules.SurfaceDistance(ORIGIN, mushrooms.center, mushrooms.half), math.sqrt(2), 1e-9, "3D")
	expectEq(
		HarvestRules.SurfaceDistance(Vector3.new(0, 1, 0), node(0, 0, 4, 4, 4).center, node(0, 0, 4, 4, 4).half),
		0,
		"inside"
	)
end)

test("reach follows the held item and never passes the harvest range", function()
	expectEq(HarvestRules.Reach(5), 5 + HarvestRules.REACH_ALLOWANCE, "hand reach plus slack")
	expectEq(HarvestRules.Reach(50), NodeCatalog.HARVEST_RANGE, "capped at the harvest range")
end)

test("only nodes inside the arc are hit; a node being touched always is", function()
	local behind = node(0, 5, 2, 2, 2)
	local side = node(5, 0, 2, 2, 2)
	expect(HarvestRules.Pick(ORIGIN, NORTH, 7, { behind }) == nil, "behind is missed")
	expect(HarvestRules.Pick(ORIGIN, NORTH, 7, { side }) == nil, "90 degrees off is outside a 120 degree arc")
	local ahead = node(2, -4, 2, 2, 2)
	expect(HarvestRules.Pick(ORIGIN, NORTH, 7, { ahead }) == ahead, "ahead and a little to the side")
	-- Standing right against a node's side counts whatever the aim.
	local touching = node(0, 1.5, 2, 2, 2)
	expect(HarvestRules.InArc(ORIGIN, NORTH, touching.center, touching.half), "touching")
	-- A long log beside the player: centre out of the arc, its near end inside.
	local log = node(-8, -3, 16, 2, 2)
	expect(HarvestRules.InArc(ORIGIN, NORTH, log.center, log.half), "the near part of a long node counts")
end)

test("the closest node wins and depleted nodes are skipped", function()
	local near = node(0, -3, 2, 2, 2)
	local far = node(1, -6, 2, 2, 2)
	expect(HarvestRules.Pick(ORIGIN, NORTH, 7, { far, near }) == near, "closest wins")
	near.active = false
	expect(HarvestRules.Pick(ORIGIN, NORTH, 7, { far, near }) == far, "a depleted node is skipped")
	far.active = false
	expect(HarvestRules.Pick(ORIGIN, NORTH, 7, { far, near }) == nil, "nothing left")
end)

test("line of sight is asked only of nodes that would win", function()
	local near = node(0, -3, 2, 2, 2)
	local far = node(1, -6, 2, 2, 2)
	local behind = node(0, 5, 2, 2, 2)
	local asked = {}
	local picked = HarvestRules.Pick(ORIGIN, NORTH, 7, { behind, near, far }, function(candidate)
		asked[candidate] = true
		return candidate ~= near
	end)
	expect(picked == far, "a blocked node gives way to the next")
	expect(asked[behind] == nil, "never raycasts to a node outside the arc")
end)

test("hitbox extents follow rotation", function()
	local size = Vector3.new(14, 3, 3)
	-- A trunk lying along X, turned upright (90 degrees about Z).
	local half = HarvestRules.WorldHalf(Vector3.new(0, 1, 0), Vector3.new(-1, 0, 0), Vector3.new(0, 0, -1), size)
	expectNear(half.X, 1.5, 1e-9, "x")
	expectNear(half.Y, 7, 1e-9, "y")
	expectNear(half.Z, 1.5, 1e-9, "z")
	local upright = HarvestRules.WorldHalf(Vector3.new(1, 0, 0), Vector3.new(0, 1, 0), Vector3.new(0, 0, -1), size)
	expectNear(upright.X, 7, 1e-9, "unrotated x")
end)

test("target priority: fights first, then nodes for gear and hands, structures for weapons", function()
	local gathering = HarvestRules.TargetOrder(false, false)
	expectEq(table.concat(gathering, ">"), "Player>Npc>Node>Structure", "tools and hands")
	local weapon = HarvestRules.TargetOrder(true, false)
	expectEq(table.concat(weapon, ">"), "Player>Npc>Structure>Node", "weapons")
	-- Nobody deals damage inside a safe zone; gathering is still allowed.
	expectEq(table.concat(HarvestRules.TargetOrder(true, true), ">"), "Node", "safe zone, weapon")
	expectEq(table.concat(HarvestRules.TargetOrder(false, true), ">"), "Node", "safe zone, hands")
end)

test("harvest cadence and client swing pacing", function()
	expect(HarvestRules.CadenceReady(nil, 0), "first hit")
	expect(not HarvestRules.CadenceReady(10, 10.2), "too soon")
	expect(HarvestRules.CadenceReady(10, 10 + NodeCatalog.HARVEST_INTERVAL), "on the interval")
	expect(HarvestRules.CadenceReady(10, 10 + NodeCatalog.HARVEST_INTERVAL - 0.03), "jitter slack")
	-- Bare hands swing every 0.3 s, but wait for the harvest cadence at a node.
	expectEq(HarvestRules.SwingInterval(0.3, false), 0.3, "fighting pace")
	expectEq(HarvestRules.SwingInterval(0.3, true), NodeCatalog.HARVEST_INTERVAL, "gathering pace")
	expectEq(HarvestRules.SwingInterval(0.9, true), 0.9, "a slow weapon keeps its own pace")
end)

test("hover labels name the action, the node and its pickaxe gate", function()
	expectEq(HarvestRules.Action("Tree"), "Chop", "trees are chopped")
	expectEq(HarvestRules.Action("Rock"), "Mine", "rocks are mined")
	expectEq(HarvestRules.Action("IronDeposit"), "Mine", "ores are mined")
	expectEq(HarvestRules.Action("RedberryBush"), "Gather", "berries are gathered")
	expectEq(HarvestRules.Label("Tree"), "Tree", "no gate")
	expectEq(HarvestRules.Label("RedberryBush"), "Redberry Bush", "spaced name")
	local gate = NodeCatalog.PickaxeName(NodeCatalog.Nodes.IronDeposit.minRank)
	expectEq(HarvestRules.Label("IronDeposit"), "Iron Deposit · " .. gate .. "+", "gate shown")
	expectEq(HarvestRules.GateLabel("FiberPlant"), nil, "plants have no gate")
	for nodeType in NodeCatalog.Nodes do
		expect(#HarvestRules.Label(nodeType) > 0, nodeType .. " has a label")
	end
end)

test("hover plaque height and touch attack icon", function()
	-- A short node: just above its top. A tall tree: at the player's eye level.
	expectEq(HarvestRules.LabelHeight(1, 1, 3), 3, "above a mushroom patch")
	expectEq(HarvestRules.LabelHeight(10, 10, 3), 6, "beside a tall tree")
	expectEq(HarvestRules.AttackIcon("Axe"), "stone_axe", "axe")
	expectEq(HarvestRules.AttackIcon("Pickaxe"), "pickaxe", "pickaxe")
	expectEq(HarvestRules.AttackIcon(nil), "spear", "weapons and hands")
end)
