# Tutorial: a minimal H → Z a event loop

This folder contains a deliberately simple analysis skeleton to get started with
the CMS NanoAOD ntuples before moving on to the full analysis
(`../HZaRecoAnalysis.cxx`).

It is a single C++ file, `HZaTutorial.cxx`, with a plain event loop
(`TChain` + `TTreeReader`) that

1. chains all NanoAOD files of **one sample** (by default the signal point
   m(a) = 1 GeV, listed in `signal_mA1p0GeV.txt` in this folder),
2. applies the **lowest unprescaled single-lepton triggers** of 2024,
   `HLT_IsoMu24` OR `HLT_Ele30_WPTight_Gsf`,
3. gives you access to the **muon, electron and jet** collections of each event,
4. writes **histograms** to an output ROOT file.

The reconstruction of the Z boson, the a boson and the Higgs boson is **not
implemented**. That part is up to you; look for the `TODO` block in the
event loop.

## Setup, build and run

On a DESY NAF node:

```bash
# setup root (this works on DESY NAF or other system with cvmfs access)
source /cvmfs/sft.cern.ch/lcg/app/releases/ROOT/6.38.00/x86_64-almalinux9.7-gcc115-opt/bin/thisroot.sh
root-config --version

# compile and run
make                    # compiles HZaTutorial.cxx → ./HZaTutorial
make run                # runs on the default signal sample
```

`make run` takes these optional settings:

```bash
make run NEVENTS=10000                                        # only the first 10k events
make run NFILES=5                                             # only the first 5 files
make run FILELIST=../configs/filelists/signal_mA2p0GeV.txt \
         OUTPUT=signal_mA2p0GeV.root                          # another signal point
```

You can also call the program directly:

```bash
./HZaTutorial -f <filelist> -o <output.root> [-n maxEvents] [-m maxFiles]
./HZaTutorial -h
```

A filelist is a text file with one ROOT file per line (lines starting with `#`
are ignored).

## Output

The output file (default `tutorial_output.root`) contains:

| Histogram | Content |
|---|---|
| `cutflow` | Weighted number of events after each step |
| `nMuon`, `nElectron`, `nJet` | Object multiplicities (no selection) |
| `muon_pt`, `muon_eta`, `electron_pt`, `electron_eta` | Lepton kinematics (no selection) |
| `jet_pt`, `jet_eta`, `jet_mass` | Jet kinematics (no selection) |
| `Z_mass`, `Z_pt` | Reconstructed Z boson: **empty until you implement it** |
| `a_mass`, `a_pt` | Reconstructed a boson: **empty until you implement it** |
| `H_mass`, `H_pt` | Reconstructed Higgs boson: **empty until you implement it** |

Look at them with

```bash
root -l tutorial_output.root
root [1] new TBrowser
```

Simulated events are weighted with the generator weight `genWeight`, which can be
negative. Histograms are **not** yet normalised to cross section × luminosity.

## Your task

Inside the event loop, fill in the `TODO` block:

1. **Lepton selection.** Select good muons (e.g. pT > 10 GeV, |η| < 2.4,
   `Muon_mediumId`, `Muon_pfRelIso04_all < 0.15`) and electrons (e.g.
   pT > 15 GeV, |η| < 2.5, `Electron_cutBased >= 3`). The leading lepton must
   be above the trigger threshold.
2. **Z boson.** Build a same-flavour, opposite-charge lepton pair and pick
   the best Z candidate. Set `Z` and `hasZ = true`.
3. **a boson.** Select jets (pT, |η|, jet ID via the helper
   `PassJetIdTightLepVeto(...)`), remove jets close to the Z leptons
   (`DeltaR(...) < 0.4`), and pick the a candidate. Set `a` and `hasA = true`.
4. **Higgs boson.** H = Z + a is already computed for you.

Helpers available in the file: `DeltaR`, `DeltaPhi`, `PassJetIdTightLepVeto`.
Build four-vectors with `TLorentzVector::SetPtEtaPhiM(pt, eta, phi, mass)`.

## Tips

- **Need another branch?** List what is available with
  `root -l <file.root>` and then `Events->Print("Jet_*")`. Add a
  `TTreeReaderArray<Float_t>` (or the matching type) next to the existing ones.
  The type must match the branch exactly (`Float_t`, `Int_t`, `UChar_t`,
  `Bool_t`, ...), or the reader will complain at runtime.
- **Running on data.** An event can be in both the `Muon` and the `EGamma`
  dataset. To avoid counting it twice, require only `HLT_IsoMu24` on `Muon`
  and `!HLT_IsoMu24 && HLT_Ele30_WPTight_Gsf` on `EGamma`.
- **Start small.** Use `make run NEVENTS=1000` while developing.
