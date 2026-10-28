import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt, re, os
plt.rcParams.update({"mathtext.fontset":"cm","svg.fonttype":"path"})
F = {
 "f_direccion": r"$d_c \;=\; \dfrac{1}{5}\sum_{s=1}^{5}\left(h^{\mathrm{hacker}}_{s,c} \,-\, h^{\mathrm{control}}_{s,c}\right)$",
 "f_intervencion": r"$h_c \;\leftarrow\; h_c \,-\, \alpha\, d_c$",
 "f_did": r"$d^{\,\mathrm{did}} \;=\; \left(h^{\mathrm{hacker}}_{\mathrm{con}} - h^{\mathrm{hacker}}_{\mathrm{sin}}\right) \,-\, \left(h^{\mathrm{control}}_{\mathrm{con}} - h^{\mathrm{control}}_{\mathrm{sin}}\right)$",
}
for name, tex in F.items():
    fig = plt.figure(figsize=(0.01,0.01))
    fig.text(0,0,tex,fontsize=28,color="#143A33")
    fig.savefig(f"{name}.svg", bbox_inches="tight", pad_inches=0.02, transparent=True)
    fig.savefig(f"{name}.png", bbox_inches="tight", pad_inches=0.05, dpi=100, facecolor="white")
    plt.close(fig)
    s=open(f"{name}.svg",encoding="utf-8").read()
    print(name, re.search(r'width="([\d.]+)pt" height="([\d.]+)pt"',s).groups(), os.path.getsize(f"{name}.svg"))
