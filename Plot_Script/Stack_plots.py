""" 
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

f = ROOT.TFile.Open("bkg_tutorial_output.root")

if not f or f.IsZombie():
    raise RuntimeError("Cannot open ROOT file!")

# --------------------------------------------------
# GET HISTOGRAMS
# --------------------------------------------------

h_all = f.Get("Z_mass_ee_all")
h_good = f.Get("Z_mass_ee_good")
h_iso = f.Get("Z_mass_ee_isolated")
h_sfos = f.Get("Z_mass_ee_sfos")

histograms = [h_all, h_good, h_iso, h_sfos]

for h in histograms:
    if not h:
        raise RuntimeError("One or more histograms were not found!")

# --------------------------------------------------
# CANVAS
# --------------------------------------------------

c = ROOT.TCanvas("c", "Z Mass Selection", 800, 800)

# --------------------------------------------------
# HISTOGRAM STYLE
# --------------------------------------------------

h_all.SetLineColor(ROOT.kBlack)
h_good.SetLineColor(ROOT.kBlue)
h_iso.SetLineColor(ROOT.kGreen + 2)
h_sfos.SetLineColor(ROOT.kRed)

for h in histograms:
    h.SetLineWidth(2)
    h.SetStats(0)
    h.GetXaxis().SetTitle("m_{ll} [GeV]")
    h.GetYaxis().SetTitle("Events")

# --------------------------------------------------
# DRAW HISTOGRAMS
# --------------------------------------------------

h_all.SetTitle("Z boson reconstruction")

maximum = max(h.GetMaximum() for h in histograms)
h_all.SetMaximum(maximum * 1.25)

h_all.Draw("HIST")
h_good.Draw("HIST SAME")
h_iso.Draw("HIST SAME")
h_sfos.Draw("HIST SAME")

# --------------------------------------------------
# LEGEND
# --------------------------------------------------

legend = ROOT.TLegend(0.70, 0.68, 0.90, 0.88)


legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.035)

legend.AddEntry(h_all, "All events", "l")
legend.AddEntry(h_good, "Good leptons", "l")
legend.AddEntry(h_iso, "Isolated leptons", "l")
legend.AddEntry(h_sfos, "SFOS leptons", "l")

legend.Draw()

# --------------------------------------------------
# CMS LABEL
# --------------------------------------------------

CMS.CMS_lumi(c, 11)

c.Update()

# --------------------------------------------------
# SAVE
# --------------------------------------------------

c.SaveAs("Z_mass_ee_bkg.png")

f.Close()

print("Z mass comparison plots saved!")  """






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
# OPEN ROOT FILES
# --------------------------------------------------

f_signal = ROOT.TFile.Open("tutorial_output.root")
f_bkg = ROOT.TFile.Open("bkg_tutorial_output.root")

if not f_signal or f_signal.IsZombie():
    raise RuntimeError("Cannot open signal ROOT file!")

if not f_bkg or f_bkg.IsZombie():
    raise RuntimeError("Cannot open background ROOT file!")

# --------------------------------------------------
# GET HISTOGRAMS
# --------------------------------------------------

h_signal = f_signal.Get("Z_mass_ee_sfos")
h_bkg = f_bkg.Get("Z_mass_ee_sfos")

if not h_signal or not h_bkg:
    raise RuntimeError("Histogram not found!")

h_signal.SetDirectory(0)
h_bkg.SetDirectory(0)

# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

if h_signal.Integral() > 0:
    h_signal.Scale(1.0 / h_signal.Integral())

if h_bkg.Integral() > 0:
    h_bkg.Scale(1.0 / h_bkg.Integral())

# --------------------------------------------------
# CANVAS
# --------------------------------------------------

c = ROOT.TCanvas("c", "Signal vs Background", 800, 800)

# --------------------------------------------------
# HISTOGRAM STYLE
# --------------------------------------------------

h_signal.SetLineColor(ROOT.kBlue)
h_signal.SetLineWidth(2)

h_bkg.SetLineColor(ROOT.kRed)
h_bkg.SetLineWidth(2)

h_signal.SetStats(0)
h_bkg.SetStats(0)

h_signal.SetTitle("Z boson invariant mass")
h_signal.GetXaxis().SetTitle("m_{ll} [GeV]")
h_signal.GetYaxis().SetTitle("Normalized events")

# --------------------------------------------------
# GAUSSIAN FITS
# --------------------------------------------------

# Signal fit range
signal_min = 60
signal_max = 120

# Background fit range
bkg_min = 60
bkg_max = 120

# Signal Gaussian
fit_signal = ROOT.TF1(
    "fit_signal", "gaus", signal_min, signal_max
)

fit_signal.SetParameters(
    h_signal.GetMaximum(),
    h_signal.GetMean(),
    h_signal.GetStdDev()
)

fit_signal.SetLineColor(ROOT.kBlue)
fit_signal.SetLineStyle(2)
fit_signal.SetLineWidth(2)

# Background Gaussian
fit_bkg = ROOT.TF1(
    "fit_bkg", "gaus", bkg_min, bkg_max
)

fit_bkg.SetParameters(
    h_bkg.GetMaximum(),
    h_bkg.GetMean(),
    h_bkg.GetStdDev()
)

fit_bkg.SetLineColor(ROOT.kRed)
fit_bkg.SetLineStyle(2)
fit_bkg.SetLineWidth(2)

# Perform fits
result_signal = h_signal.Fit(fit_signal, "R S")
result_bkg = h_bkg.Fit(fit_bkg, "R S")

# Extract parameters
mean_signal = fit_signal.GetParameter(1)
sigma_signal = abs(fit_signal.GetParameter(2))

mean_bkg = fit_bkg.GetParameter(1)
sigma_bkg = abs(fit_bkg.GetParameter(2))

# --------------------------------------------------
# DRAW HISTOGRAMS AND FITS
# --------------------------------------------------

maximum = max(
    h_signal.GetMaximum(),
    h_bkg.GetMaximum()
)

h_signal.SetMaximum(maximum * 1.4)

h_signal.Draw("HIST")
h_bkg.Draw("HIST SAME")

fit_signal.Draw("SAME")
fit_bkg.Draw("SAME")

# --------------------------------------------------
# LEGEND
# --------------------------------------------------

legend = ROOT.TLegend(0.55, 0.63, 0.88, 0.88)

legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetTextSize(0.030)

legend.AddEntry(h_signal, "Signal", "l")
legend.AddEntry(fit_signal, "Signal Gaussian fit", "l")

legend.AddEntry(
    0,
    f"Signal #mu = {mean_signal:.2f}, #sigma = {sigma_signal:.2f}",
    ""
)

legend.AddEntry(h_bkg, "Background", "l")
legend.AddEntry(fit_bkg, "Background Gaussian fit", "l")

legend.AddEntry(
    0,
    f"Background #mu = {mean_bkg:.2f}, #sigma = {sigma_bkg:.2f}",
    ""
)

legend.Draw()

# --------------------------------------------------
# CMS LABEL
# --------------------------------------------------

CMS.CMS_lumi(c, 11)

c.Update()

# --------------------------------------------------
# SAVE
# --------------------------------------------------

c.SaveAs("Z_mass_signal_background_gaussian.png")

# --------------------------------------------------
# PRINT RESULTS
# --------------------------------------------------

print("\n========== GAUSSIAN FIT RESULTS ==========")

print("SIGNAL:")
print(f"Mean  = {mean_signal:.4f}")
print(f"Sigma = {sigma_signal:.4f}")

print("\nBACKGROUND:")
print(f"Mean  = {mean_bkg:.4f}")
print(f"Sigma = {sigma_bkg:.4f}")

print("==========================================")

f_signal.Close()
f_bkg.Close()

print("Plot saved successfully!")
