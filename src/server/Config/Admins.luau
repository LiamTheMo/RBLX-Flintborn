-- Server-held administrator list (GDD §30.3). Admin rights never come from a
-- client flag. The experience owner (or, for a group-owned experience, group
-- ranks at or above MIN_GROUP_RANK) is always an admin; add other trusted user IDs
-- here.

return {
	UserIds = {},
	MIN_GROUP_RANK = 254,
}
