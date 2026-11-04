-- Server half of Shared.Crafting.ForgeRecipes: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedForgeRecipes = require(ReplicatedStorage.Shared.Crafting.ForgeRecipes)

local ForgeRecipes = table.clone(SharedForgeRecipes)

function ForgeRecipes.Get(recipeId: any)
	return type(recipeId) == "string" and ForgeRecipes.ById[recipeId] or nil
end

return ForgeRecipes
