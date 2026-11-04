-- Server half of Shared.Combat.WeaponCatalog: what only the server uses. Everything in
-- ReplicatedStorage is downloaded to every player, so the shared module keeps
-- only what clients need; this one clones it and adds the rest, and server code
-- requires this module.

local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SharedWeaponCatalog = require(ReplicatedStorage.Shared.Combat.WeaponCatalog)

local WeaponCatalog = table.clone(SharedWeaponCatalog)

WeaponCatalog.ARROW = "FlintArrow"

WeaponCatalog.MIN_ARROW_SPEED = 60
WeaponCatalog.MAX_ARROW_SPEED = 120
WeaponCatalog.ARROW_GRAVITY_SCALE = 0.35
WeaponCatalog.ARROW_LIFETIME = 5

return WeaponCatalog
