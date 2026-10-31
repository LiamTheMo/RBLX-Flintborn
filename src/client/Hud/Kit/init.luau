-- The UI kit every screen is built from (docs/ui/KIT.md, ARCHITECTURE §2):
-- tokens, role-to-art mapping, the shared interaction state machine, motion,
-- sound, scaling, the one-window modal registry and the components.
--
--   local Kit = require(Hud.Kit)
--   local screen = Kit.Screen.new("FlintbornForge", { size = { 1102, 679 } })
--   local window = Kit.Window.new(screen, { title = "Ancestral Forge", icon = "anvil", smallCaps = true })
--   Kit.Button.new(window:Body(), { rect = { 640, 480, 256, 62 }, label = "Forge", onPress = forge })

local Kit = {}

Kit.Tokens = require(script.Tokens)
Kit.Art = require(script.Art)
Kit.Core = require(script.Core)
Kit.Interact = require(script.Interact)
Kit.Input = require(script.Input)
Kit.Motion = require(script.Motion)
Kit.Sound = require(script.Sound)
Kit.Scale = require(script.Scale)
Kit.Modal = require(script.Modal)
Kit.Debug = require(script.Debug)

Kit.Screen = require(script.Screen)
Kit.Window = require(script.Window)
Kit.Panel = require(script.Panel)
Kit.SectionHeader = require(script.SectionHeader)
Kit.Button = require(script.Button)
Kit.IconButton = require(script.IconButton)
Kit.Tab = require(script.Tab)
Kit.TabGroup = Kit.Tab.Group
Kit.Slot = require(script.Slot)
Kit.Bar = require(script.Bar)
Kit.Ring = require(script.Ring)
Kit.Checkbox = require(script.Checkbox)
Kit.Toggle = require(script.Toggle)
Kit.Slider = require(script.Slider)
Kit.Dropdown = require(script.Dropdown)
Kit.SearchBox = require(script.SearchBox)
Kit.TextField = require(script.TextField)
Kit.Stepper = require(script.Stepper)
Kit.KeyCap = require(script.KeyCap)
Kit.Divider = require(script.Divider)
Kit.ListRow = require(script.ListRow)
Kit.PlayerRow = require(script.PlayerRow)
Kit.Badge = require(script.Badge)
Kit.CurrencyPill = require(script.CurrencyPill)
Kit.Portrait = require(script.Portrait)
Kit.Picture = require(script.Picture)
Kit.Icon = require(script.Icon)
Kit.ItemIcon = require(script.ItemIcon)
Kit.Text = require(script.Text)
Kit.Scroll = require(script.Scroll)
Kit.Toast = require(script.Toast)
Kit.ConfirmDialog = require(script.ConfirmDialog)
Kit.Tooltip = require(script.Tooltip)

return Kit
