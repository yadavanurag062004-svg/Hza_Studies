import ROOT
import cmsstyle as CMS

ROOT.gROOT.SetBatch(True)

CMS.setCMSStyle()
CMS.SetEnergy(13.6)
CMS.SetLumi(-1,"","Run 3", "")
CMS.SetExtraText("Simulation")

# --------------------------------------------------
# OPEN ROOT FILE
# --------------------------------------------------

f = ROOT.TFile.Open("tutorial_output.root")


# -------------------------------------------------
# Z MASS FIT
# --------------------------------------------------

def fit_z_mass(hist_name, title):

    h = f.Get(hist_name)

    if not h:
        print(f"WARNING: {hist_name} not found!")
        return

    c = ROOT.TCanvas(hist_name, title, 1000, 1000)

    h.SetLineColor(ROOT.kBlack)
    h.SetLineWidth(2)
    h.SetStats(0)

    h.SetTitle(title)
    h.GetXaxis().SetTitle("m_{ll} [GeV]")
    h.GetYaxis().SetTitle("Events")

    # --------------------------------------------------
    # FIT RANGE
    # --------------------------------------------------

    fit_min = 70
    fit_max = 110

    # --------------------------------------------------
    # AUTOMATIC INITIAL ESTIMATES FROM HISTOGRAM
    # --------------------------------------------------

    peak_bin = h.GetMaximumBin()
    peak = h.GetBinCenter(peak_bin)

    # Estimate width from bins around the peak
    rms = h.GetRMS()

    # Estimate Gaussian resolution
    sigma_initial = max(h.GetBinWidth(peak_bin), min(rms, 3.0))

    # Estimate normalization
    amplitude_initial = h.GetMaximum()

    # --------------------------------------------------
    # VOIGTIAN FIT
    # --------------------------------------------------

    fit = ROOT.TF1(
        "voigt_" + hist_name,
        "[0]*TMath::Voigt(x-[1],[2],[3])",
        fit_min,
        fit_max
    )

    # All starting values estimated from histogram
    fit.SetParameters(
        amplitude_initial,
        peak,
        sigma_initial,
        2.4952
    )

    # Allow parameters to vary
    fit.SetParLimits(0, 0, amplitude_initial * 100)
    fit.SetParLimits(1, fit_min, fit_max)
    fit.SetParLimits(2, 0.01, 10)
    fit.SetParLimits(3, 0.1, 10)

    fit.SetLineColor(ROOT.kRed)
    fit.SetLineWidth(3)

    # --------------------------------------------------
    # FIT
    # --------------------------------------------------

    result = h.Fit(fit, "RLS")

    # --------------------------------------------------
    # RESULTS
    # --------------------------------------------------

    mass = fit.GetParameter(1)
    mass_err = fit.GetParError(1)

    resolution = fit.GetParameter(2)
    resolution_err = fit.GetParError(2)

    width = fit.GetParameter(3)
    width_err = fit.GetParError(3)

    chi2 = fit.GetChisquare()
    ndf = fit.GetNDF()

    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------

    h.Draw("HIST")
    fit.Draw("SAME")

    legend = ROOT.TLegend(0.65, 0.72, 0.88, 0.88)

    legend.SetBorderSize(0)
    legend.SetFillStyle(0)
    legend.SetTextSize(0.025)


    legend.AddEntry(h, "Reconstructed Z", "l")
    legend.AddEntry(fit, "Fit", "l")

    legend.AddEntry(
        0,
        f"M_{{Z}} = {mass:.3f} #pm {mass_err:.3f} GeV",
        ""
    )

    legend.AddEntry(
        0,
        f"#sigma = {resolution:.3f} #pm {resolution_err:.3f} GeV",
        ""
    )

    legend.AddEntry(
        0,
        f"#Gamma = {width:.3f} #pm {width_err:.3f} GeV",
        ""
    ) 

   

    legend.Draw()

    CMS.CMS_lumi(c, 11)

    c.Update()

    c.SaveAs(hist_name + "_Fit.png")

    # --------------------------------------------------
    # PRINT RESULTS
    # --------------------------------------------------

    print("------------------------------------")
    print(hist_name)
    print(f"Mass       = {mass:.5f} +/- {mass_err:.5f} GeV")
    print(f"Resolution = {resolution:.5f} +/- {resolution_err:.5f} GeV")
    print(f"Width      = {width:.5f} +/- {width_err:.5f} GeV")
    print(f"Chi2/NDF   = {chi2:.2f}/{ndf}")
    print(f"Fit status = {int(result)}")
    print("------------------------------------")

    c.Close()


# --------------------------------------------------
# FIT BOTH CHANNELS
# --------------------------------------------------

fit_z_mass("Z_mumu", "Z #rightarrow #mu^{+}#mu^{-}")

f.Close()

print("All Z mass fits completed!")
