-- Camera bounds (GDD §36.5, Q58). Third person with adjustable zoom inside fixed
-- bounds, so nobody gets a corner-peeking advantage from extreme distances.

local CameraRules = {}

CameraRules.MIN_ZOOM = 8
CameraRules.MAX_ZOOM = 40
CameraRules.DEFAULT_ZOOM = 16

-- A saved preference clamped to the bounds (or the default when missing/invalid).
function CameraRules.Clamp(zoom: any): number
	if type(zoom) ~= "number" or zoom ~= zoom then
		return CameraRules.DEFAULT_ZOOM
	end
	return math.clamp(math.round(zoom), CameraRules.MIN_ZOOM, CameraRules.MAX_ZOOM)
end

return CameraRules
