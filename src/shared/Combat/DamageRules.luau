-- Pure combat checks shared by the server and specs (GDD §5.1, §5.5, §21.1, §31.2,
-- Q160b). The server resolves every hit with these; clients never declare hits.

local DamageRules = {}

-- Extra reach allowed for latency between client and server positions.
DamageRules.REACH_ALLOWANCE = 2

-- True when `toTarget` lies within `arcDegrees` (full cone) of `facing`.
function DamageRules.WithinArc(facing, toTarget, arcDegrees: number): boolean
	local length = toTarget.Magnitude
	if length < 1e-6 then
		return true
	end
	local cosine = facing:Dot(toTarget / length) / math.max(facing.Magnitude, 1e-6)
	return cosine >= math.cos(math.rad(arcDegrees / 2))
end

return DamageRules
