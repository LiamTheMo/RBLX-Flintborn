import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib"))
import flintkit as fk
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
fk.reset_file()

a = fk.Asset("PalisadePanelA", "Fences")
n, r, h = 6, 0.62, 9.0
for i in range(n):
    x = (i - (n - 1) / 2) * r * 2.0
    a.stake(r, h + a.rng.uniform(-0.35, 0.35), tip=1.9, loc=(x, 0, 0))
xs = [(i - (n - 1) / 2) * r * 2.0 for i in range(n)]
a.rope_band(xs, r, 1.0, count=2, thickness=0.16)
a.rope_band(xs, r, 5.3, count=2, thickness=0.16)
p = a.finish()

b = fk.Asset("LowBoulder", "Rocks")
b.rock((7, 5, 3.6), subdiv=2, rough=0.1, facets=10)
q = b.finish()

t = fk.Asset("BroadleafStout", "Trees")
t.cyl(1.9, 1.3, 8, 7, mat="bark", jitter=0.12)
for (x, y, z, s) in [(0,0,11,4.5),(-3,0.5,9.5,3.3),(3,-0.3,9.6,3.4),(1.2,2,12,3),(-1.5,-1.8,10.6,3.1),(0.5,0.5,13.5,3)]:
    t.leaf_blob(s, (x, y, z), mat="leaf", subdiv=1, rough=0.1)
u = t.finish()

fk.layout_row([p, q, u])
fk.render_sheet([p, q, u], os.path.join(ROOT, "renders", "_kit_test.png"), cols=3)
print("TRIS", p["tris"], q["tris"], u["tris"])
import collections
cnt = collections.Counter()
for poly in p.data.polygons:
    cnt[p.data.materials[poly.material_index].name] += len(poly.vertices) - 2
print("BYMAT", dict(cnt), len(p.data.vertices))
