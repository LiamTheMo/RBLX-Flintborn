-- Player-facing receipts (GDD §25.2). Each kind keeps only its newest entries so
-- profiles stay bounded; the operation journal still guards exactly-once commits.

local Receipts = {}

return Receipts
