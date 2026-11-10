""" import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

# CMS style
CMS.setCMSStyle()
CMS.SetEnergy(13.6)
CMS.SetLumi(108, "fb", "Run 3")
CMS.SetExtraText("Simulation")

# Open ROOT file and get histogram
f = ROOT.TFile.Open("tutorial_output.root") 
h = f.Get("Gen_Z_mass")  # Replace with his histogram name

# Create canvas
c = ROOT.TCanvas("c", "c", 800, 800)

h.SetLineColor(ROOT.kBlue)
h.SetLineWidth(2)
h.GetXaxis().SetTitle("Mass [GeV]")
h.GetYaxis().SetTitle("Events")

h.Draw("HIST")

# CMS label
CMS.CMS_lumi(c, 11)

c.SaveAs("my_CMS_plot.pdf") """

import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

# ==========================
# 1. CMS Style
# ==========================
CMS.setCMSStyle()
CMS.SetEnergy(13.6)
#CMS.SetLumi(108, "fb", "Run 3")
CMS.SetExtraText("Simulation")

# ==========================
# 2. Open ROOT file
# ==========================
f = ROOT.TFile.Open("tutorial_output.root")

# Get histograms
#h1 = f.Get("Gen_Z_mass;1")
h2 = f.Get("Z_mass_Gen_ee_good;1")
h3 = f.Get("Z_mass_ee_sfos;1")

# Clone histograms to avoid modifying original objects
#h1 = h1.Clone("h1")
h2 = h2.Clone("h2")
h3 = h3.Clone("h3")

# ==========================
# 3. Set histogram colors
# ==========================
#h1.SetLineColor(ROOT.kBlue + 2)

h2.SetLineColor(ROOT.kRed + 2)

h3.SetLineColor(ROOT.kGreen + 2)

# Line width
#h1.SetLineWidth(1)
h2.SetLineWidth(1)
h3.SetLineWidth(1)

# ==========================
# 4. Create stack
# ==========================
stack = ROOT.THStack("stack", "")

#stack.Add(h1)
stack.Add(h2)
stack.Add(h3)

# ==========================
# 5. Create canvas
# ==========================
c = ROOT.TCanvas("c", "CMS Stacked Plot", 800, 800)

# Draw stack
stack.Draw("HIST")

# Axis titles
stack.GetXaxis().SetTitle("Mass [GeV]")
stack.GetYaxis().SetTitle("Events")

# ==========================
# 6. Legend
# ==========================
legend = ROOT.TLegend(0.65, 0.70, 0.88, 0.88)

legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.035)

#legend.AddEntry(h1, "Gen Z", "f")
legend.AddEntry(h2, "Gen Reco Z", "f")
legend.AddEntry(h3, "Reco Z", "f")

legend.Draw()

# ==========================
# 7. CMS label
# ==========================
CMS.CMS_lumi(c, 11)

# ==========================
# 8. Save plot
# ==========================
c.SaveAs("CMS_stacked_plot.pdf")
c.SaveAs("CMS_stacked_plot.png")
""" 
from cmsstyle.src import cmsstyle
import cmsstyle as CMS
CMS.SetExtraText("Simulation Preliminary")
CMS.SetLumi(None, run = "")
canv = CMS.cmsCanvas('', 0, 1, 0, 1, '', '', square = True, extraSpace=0.01, iPos=0)
 """
