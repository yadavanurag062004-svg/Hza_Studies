import ROOT

import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

# --------------------------------------------------
# CMS STYLE
# --------------------------------------------------

CMS.setCMSStyle()
CMS.SetEnergy(13.6)
CMS.SetLumi(-1, "","Run 3 (2024)")
CMS.SetExtraText("Simulation")

# --------------------------------------------------
# OPEN ROOT FILE
# --------------------------------------------------

f = ROOT.TFile.Open("Output.root")

if not f or f.IsZombie():
    raise RuntimeError("Cannot open ROOT file!")

# --------------------------------------------------
# DEFINE SIX HISTOGRAMS
# --------------------------------------------------

histograms = [
    ("Muon_Acceptance", "-1", "p_{T} [GeV]"),
    ("Muon_Efficiency", "-1", "p_{T} [GeV]"),
    ("Muon_Acc*Eff", "-1", "p_{T} [GeV]"),
    ("Electron_Acceptance", "-1", "p_{T} [GeV]"),
    ("Electron_Efficiency", "-1", "p_{T} [GeV]"),
    ("Electron_Acc*Eff", "-1", "p_{T} [GeV]"),
    ("Muon_Acceptance_eta", "-1", "{eta}"),
    ("Muon_Efficiency_eta", "-1", "{eta}"),
    ("Muon_Acc*Eff_eta", "-1", "{eta}"),
    ("Electron_Acceptance_eta", "-1", "{eta}"),
    ("Electron_Efficiency_eta", "-1", "{eta}"),
    ("Electron_Acc*Eff_eta", "-1", "{eta}"),
]

# --------------------------------------------------
# CREATE AND SAVE INDIVIDUAL PLOTS
# --------------------------------------------------
for hist_name, title, x_title in histograms:

    h = f.Get(hist_name)

    if not h:
        print(f"WARNING: {hist_name} not found!")
        continue

    # Create individual canvas
    c = ROOT.TCanvas(hist_name, title, 800, 800)

    h.SetLineColor(ROOT.kBlue)
    h.SetLineWidth(2)

    h.SetTitle(title)
    h.GetXaxis().SetTitle(x_title)
    h.GetYaxis().SetTitle("P_{T}")

    # Logarithmic y-axis only for phi
    if hist_name == "muon_phi1" or hist_name == "muon_phi2":
        c.SetLogy(1)
        #h.SetMinimum(0.1)

    h.Draw("HIST")

    # CMS label
    CMS.CMS_lumi(c, 11)

    c.Update()

    # Save individual plots
    c.SaveAs(f"{hist_name}.png")

    print(f"Saved:{hist_name}.png")

    c.Close()

f.Close()

print("All plots generated successfully!") 
 

