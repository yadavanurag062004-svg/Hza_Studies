import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

# --------------------------------------------------
# CMS STYLE
# --------------------------------------------------

CMS.setCMSStyle()
CMS.SetEnergy(13.6)
CMS.SetLumi(-1, "", "Run 3 (2024)")
CMS.SetExtraText("Simulation")

# --------------------------------------------------
# OPEN ROOT FILE
# --------------------------------------------------

f = ROOT.TFile.Open("tutorial_output.root")

if not f or f.IsZombie():
    raise RuntimeError("Cannot open ROOT file!")

# --------------------------------------------------
# GET HISTOGRAMS
# --------------------------------------------------
#h_all = f.Get("Z_mass_mumu_all")
#h_good = f.Get("Z_mass_mumu_good")
h_Z_Reco = f.Get("Z_mass_mumu_good")
h_Gen_Z_Reco = f.Get("Z_mass_Gen_mumu_good")
#h_iso = f.Get("Z_mass_mumu_isolated")

#h_all,h_good,h_iso,
histograms = [h_Z_Reco, h_Gen_Z_Reco]

for h in histograms:
    if not h:
        raise RuntimeError("One or more histograms were not found!")

# --------------------------------------------------
# NORMALIZATION (SAME PEAK HEIGHT)
# --------------------------------------------------

for h in histograms:

    maximum = h.GetMaximum()

    if maximum > 0:
        h.Scale(1.0 / maximum)

    print(
        h.GetName(),
        "Maximum after normalization =", h.GetMaximum()
    )

# --------------------------------------------------
# NORMALIZATION (UNIT AREA)
# --------------------------------------------------

"""for h in histograms:

    integral = h.Integral("width")

    if integral > 0:
        h.Scale(1.0 / integral)

    print(
        h.GetName(),
        "Normalized integral =",
        h.Integral("width")
    )"""

# --------------------------------------------------
# CANVAS
# --------------------------------------------------

c = ROOT.TCanvas("c", "Z Mass", 800, 800)

# --------------------------------------------------
# HISTOGRAM STYLE
# --------------------------------------------------
#h_all.SetLineColor(ROOT.kBlack)
h_Z_Reco.SetLineColor(ROOT.kRed)
h_Gen_Z_Reco.SetLineColor(ROOT.kBlue)
#h_good.SetLineColor(ROOT.kGreen + 2)
#h_iso.SetLineColor(ROOT.kOrange + 7)


for h in histograms:

    h.SetLineWidth(2)
    h.SetStats(0)

    h.GetXaxis().SetTitle("m_{ll} [GeV]")
    h.GetYaxis().SetTitle("Normalized density [GeV^{-1}]")

# --------------------------------------------------
# DRAW HISTOGRAMS
# --------------------------------------------------

h_Z_Reco.SetTitle("Z boson reconstruction")


maximum = max(h.GetMaximum() for h in histograms)

h_Z_Reco.SetMaximum(maximum * 1.25)
h_Z_Reco.SetMinimum(0)

h_Z_Reco.Draw("HIST")
h_Gen_Z_Reco.Draw("HIST SAME")
#h_all.Draw("HIST SAME")
#h_good.Draw("HIST SAME")
#h_iso.Draw("HIST SAME")


# --------------------------------------------------
# LEGEND
# --------------------------------------------------

legend = ROOT.TLegend(0.65, 0.68, 0.90, 0.88)

legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.035)

legend.AddEntry(h_Z_Reco, "Z Reco", "l")
legend.AddEntry(h_Gen_Z_Reco, "Gen_Z_Reco", "l")
#legend.AddEntry(h_all, "All muons", "l")
#legend.AddEntry(h_good, "Good muons", "l")
#legend.AddEntry(h_iso, "Isolated muons", "l")

legend.Draw()

# --------------------------------------------------
# CMS LABEL
# --------------------------------------------------

CMS.CMS_lumi(c, 11)

c.Update()

# --------------------------------------------------
# SAVE
# --------------------------------------------------

c.SaveAs("Z_mass_reco_gen.png")


f.Close()

print("Z mass comparison plots saved!")


