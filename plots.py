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

f = ROOT.TFile.Open("tutorial_output.root")

if not f or f.IsZombie():
    raise RuntimeError("Cannot open ROOT file!")

# --------------------------------------------------
# DEFINE SIX HISTOGRAMS
# --------------------------------------------------

histograms = [
    ("No_cut_ele_pt", "Electron p_{T}", "p_{T} [GeV]"),
    ("Reco_ele_pt", "Electron p_{T}", "p_{T} [GeV]"),
    ("Gen_ele_pt", "Electron p_{T}", "p_{T} [GeV]"),
    #("good_muon_pt", "Good Muon p_{T}", "p_{T} [GeV]"),
    #("good_muon_eta", "Good Muon pseudorapidity", "#eta"),
    #("good_muon_dxy", "Good Muon transverse IP", "d_{xy} [cm]"),
    #("good_muon_dz", "Good Muon longitudinal IP", "d_{z} [cm]"),
    #("muon_phi1", "Leading Muon azimuthal angle", "#phi"),
    #("muon_phi2", "Subleading Muon azimuthal angle", "#phi")
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
    h.GetYaxis().SetTitle("Events")

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

    print(f"Saved: {hist_name}.pdf and {hist_name}.png")

    c.Close()

f.Close()

print("All plots generated successfully!") 
 

