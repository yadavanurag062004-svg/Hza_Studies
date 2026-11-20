import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

# --------------------------------------------------
# CMS STYLE
# --------------------------------------------------

CMS.setCMSStyle()
CMS.SetEnergy(13.6)
CMS.SetExtraText("Simulation")

# --------------------------------------------------
# OPEN ROOT FILE
# --------------------------------------------------

f = ROOT.TFile.Open("tutorial_output.root")

if not f or f.IsZombie():
    raise RuntimeError("Cannot open ROOT file!")

# --------------------------------------------------
# HISTOGRAMS
# --------------------------------------------------

histograms = [
    ("good_muon_pt", "Good muon p_{T}", "p_{T} [GeV]"),
    ("good_muon_eta", "Good muon #eta", "#eta"),
    ("good_muon_dxy", "Good muon d_{xy}", "d_{xy} [cm]"),
    ("good_muon_dz", "Good muon d_{z}", "d_{z} [cm]")
]

# --------------------------------------------------
# GAUSSIAN FITS
# --------------------------------------------------

for hist_name, title, x_title in histograms:

    h = f.Get(hist_name)

    if not h:
        print(f"WARNING: {hist_name} not found!")
        continue

    # Create canvas
    c = ROOT.TCanvas(hist_name, title, 800, 800)

    h.SetLineColor(ROOT.kBlack)
    h.SetLineWidth(2)
    h.SetStats(0)

    h.SetTitle(title)
    h.GetXaxis().SetTitle(x_title)
    h.GetYaxis().SetTitle("Events")

    # --------------------------------------------------
    # FIT RANGE
    # --------------------------------------------------

    xmin = h.GetXaxis().GetXmin()
    xmax = h.GetXaxis().GetXmax()

    if hist_name == "good_muon_pt":
        fit_min = 25
        fit_max = h.GetMean() + 2*h.GetStdDev()

    elif hist_name == "good_muon_eta":
        fit_min = -2.5
        fit_max = 2.5

    elif hist_name == "good_muon_dxy":
        fit_min = -0.2
        fit_max = 0.2

    elif hist_name == "good_muon_dz":
        fit_min = -0.5
        fit_max = 0.5

    # Keep fit range inside histogram range
    fit_min = max(fit_min, xmin)
    fit_max = min(fit_max, xmax)

    # --------------------------------------------------
    # GAUSSIAN FUNCTION
    # --------------------------------------------------

    fit = ROOT.TF1(
        "gaus_" + hist_name,
        "gaus",
        fit_min,
        fit_max
    )

    # Initial parameters
    fit.SetParameters(
        h.GetMaximum(),
        h.GetMean(),
        h.GetStdDev()
    )

    fit.SetLineColor(ROOT.kRed)
    fit.SetLineWidth(2)

    # Perform fit
    result = h.Fit(fit, "R S")

    # Extract parameters
    mean = fit.GetParameter(1)
    sigma = abs(fit.GetParameter(2))

    mean_err = fit.GetParError(1)
    sigma_err = fit.GetParError(2)

    # --------------------------------------------------
    # DRAW HISTOGRAM AND FIT
    # --------------------------------------------------

    h.Draw("HIST")
    fit.Draw("SAME")

    # --------------------------------------------------
    # LEGEND
    # --------------------------------------------------

    legend = ROOT.TLegend(0.60, 0.68, 0.88, 0.88)

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.030)

    legend.AddEntry(h, "Good muons", "l")

    legend.AddEntry(
        fit,
        f"Gaussian fit; #sigma = {sigma:.4f}",
        "l"
    )

    legend.AddEntry(
        0,
        f"#mu = {mean:.4f} #pm {mean_err:.4f}",
        ""
    )

    legend.Draw()

    # CMS label
    CMS.CMS_lumi(c, 11)

    c.Update()

    # Save
    c.SaveAs(f"{hist_name}_gaussian.png")
    c.SaveAs(f"{hist_name}_gaussian.pdf")

    print("--------------------------------")
    print(hist_name)
    print(f"Mean  = {mean:.5f} +/- {mean_err:.5f}")
    print(f"Sigma = {sigma:.5f} +/- {sigma_err:.5f}")
    print("--------------------------------")

    c.Close()

f.Close()

print("All Gaussian fits completed!")
