// ============================================================================
// HZaTutorial.cxx — minimal event loop for H → Z(ℓℓ) a(→ hadrons)
//
// Build & run:   make && make run
// ============================================================================

#include <TChain.h>
#include <TFile.h>
#include <TH1D.h>
#include <TLorentzVector.h>
#include <TTreeReader.h>
#include <TTreeReaderArray.h>
#include <TTreeReaderValue.h>
#include <TVector2.h>

#include <cmath>
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// ----------------------------------------------------------------------------
// Configuration (RunIII2024Summer24 MC)
// ----------------------------------------------------------------------------
// Lowest unprescaled single-lepton triggers in 2024
const char* kMuonTrigger     = "HLT_IsoMu24";
const char* kElectronTrigger = "HLT_Ele30_WPTight_Gsf";

const std::string kDefaultFilelist = "signal_mA1p0GeV.txt";
const std::string kDefaultOutput   = "tutorial_output.root";

// ----------------------------------------------------------------------------
// Small helper functions
// ----------------------------------------------------------------------------
float DeltaPhi(float phi1, float phi2) {
  return TVector2::Phi_mpi_pi(phi1 - phi2);
}

float DeltaR(float eta1, float phi1, float eta2, float phi2) {
  float deta = eta1 - eta2;
  float dphi = DeltaPhi(phi1, phi2);
  return std::sqrt(deta * deta + dphi * dphi);
}

// Jet ID "tightLepVeto" for Run 3 (NanoAODv15 no longer stores Jet_jetId).
// Ref: https://twiki.cern.ch/twiki/bin/view/CMS/JetID13p6TeV  (valid for |eta| < 2.6)
bool PassJetIdTightLepVeto(float eta, float chHEF, float neHEF, float chEmEF, float neEmEF,
                           float muEF, int nConstituents, int chMultiplicity) {
  if (std::abs(eta) > 2.6f) return false;
  return neHEF < 0.99f && neEmEF < 0.9f && nConstituents > 1 && chHEF > 0.01f &&
         chMultiplicity > 0 && muEF < 0.8f && chEmEF < 0.8f;
}

// Read a filelist (one ROOT file per line, '#' starts a comment)
std::vector<std::string> ReadFilelist(const std::string& path, int maxFiles) {
  std::ifstream fin(path);
  if (!fin.is_open()) throw std::runtime_error("Cannot open filelist: " + path);
  std::vector<std::string> files;
  std::string line;
  while (std::getline(fin, line)) {
    if (line.empty() || line[0] == '#') continue;
    files.push_back(line);
    if (maxFiles > 0 && (int)files.size() >= maxFiles) break;
  }
  return files;
}

void PrintUsage(const char* prog) {
  std::cout << "Usage: " << prog << " [options]\n"
            << "  -f <filelist>   text file with input ROOT files (default: " << kDefaultFilelist << ")\n"
            << "  -o <output>     output ROOT file               (default: " << kDefaultOutput << ")\n"
            << "  -n <N>          process at most N events       (default: all)\n"
            << "  -m <M>          use at most M files            (default: all)\n";
}

// ============================================================================
int main(int argc, char** argv) {
  std::string filelist   = kDefaultFilelist;
  std::string outputPath = kDefaultOutput;
  Long64_t maxEvents = -1;
  int maxFiles = -1;

  for (int i = 1; i < argc; ++i) {
    std::string arg = argv[i];
    if (arg == "-h" || arg == "--help") { PrintUsage(argv[0]); return 0; }
    if (i + 1 >= argc) { PrintUsage(argv[0]); return 1; }
    if      (arg == "-f") filelist   = argv[++i];
    else if (arg == "-o") outputPath = argv[++i];
    else if (arg == "-n") maxEvents  = std::stoll(argv[++i]);
    else if (arg == "-m") maxFiles   = std::stoi(argv[++i]);
    else { PrintUsage(argv[0]); return 1; }
  }

  // --------------------------------------------------------------------------
  // Input: chain all files of the sample
  // --------------------------------------------------------------------------
  TChain chain("Events");
  for (auto& f : ReadFilelist(filelist, maxFiles)) chain.Add(f.c_str());
  std::cout << "Chained " << chain.GetNtrees() << " files from " << filelist << std::endl;
  if (chain.GetNtrees() == 0) return 1;

  // Data has no generator weight → use that to tell data from simulation
  const bool isMC = chain.GetBranch("genWeight") != nullptr;
  std::cout << "Sample type: " << (isMC ? "simulation" : "data") << std::endl;

  // --------------------------------------------------------------------------
  // Branches. Add more here if you need them
  // Browse a file with:  root -l <file>  →  Events->Print("Muon_*")
  // --------------------------------------------------------------------------
  TTreeReader reader(&chain);

  TTreeReaderValue<UInt_t>    run(reader, "run");
  TTreeReaderValue<UInt_t>    lumi(reader, "luminosityBlock");
  TTreeReaderValue<ULong64_t> event(reader, "event");
  std::unique_ptr<TTreeReaderValue<Float_t>> genWeight;
  if (isMC) genWeight = std::make_unique<TTreeReaderValue<Float_t>>(reader, "genWeight");

  TTreeReaderValue<Bool_t> trigMuon(reader, kMuonTrigger);
  TTreeReaderValue<Bool_t> trigElectron(reader, kElectronTrigger);

  // Muons
  TTreeReaderArray<Float_t> Muon_pt(reader, "Muon_pt");
  TTreeReaderArray<Float_t> Muon_eta(reader, "Muon_eta");
  TTreeReaderArray<Float_t> Muon_phi(reader, "Muon_phi");
  TTreeReaderArray<Float_t> Muon_mass(reader, "Muon_mass");
  TTreeReaderArray<Int_t>   Muon_charge(reader, "Muon_charge");
  TTreeReaderArray<Bool_t>  Muon_mediumId(reader, "Muon_mediumId");
  TTreeReaderArray<Bool_t>  Muon_tightId(reader, "Muon_tightId");
  TTreeReaderArray<Float_t> Muon_pfRelIso04_all(reader, "Muon_pfRelIso04_all");
  TTreeReaderArray<Float_t> Muon_dxy(reader,"Muon_dxy");
  TTreeReaderArray<Float_t> Muon_dz(reader,"Muon_dz");

  // Electrons (cutBased: 0 fail, 1 veto, 2 loose, 3 medium, 4 tight)
  TTreeReaderArray<Float_t> Electron_pt(reader, "Electron_pt");
  TTreeReaderArray<Float_t> Electron_eta(reader, "Electron_eta");
  TTreeReaderArray<Float_t> Electron_phi(reader, "Electron_phi");
  TTreeReaderArray<Float_t> Electron_mass(reader, "Electron_mass");
  TTreeReaderArray<Int_t>   Electron_charge(reader, "Electron_charge");
  TTreeReaderArray<UChar_t> Electron_cutBased(reader, "Electron_cutBased");
  TTreeReaderArray<Float_t> Electron_pfRelIso03_all(reader, "Electron_pfRelIso03_all");
  TTreeReaderArray<Float_t> Electron_dxy(reader,"Electron_dxy");
  TTreeReaderArray<Float_t> Electron_dz(reader,"Electron_dz");

  // Jets (AK4, PUPPI) + the inputs for the jet ID
  TTreeReaderArray<Float_t> Jet_pt(reader, "Jet_pt");
  TTreeReaderArray<Float_t> Jet_eta(reader, "Jet_eta");
  TTreeReaderArray<Float_t> Jet_phi(reader, "Jet_phi");
  TTreeReaderArray<Float_t> Jet_mass(reader, "Jet_mass");
  TTreeReaderArray<Float_t> Jet_btagUParTAK4B(reader, "Jet_btagUParTAK4B");
  TTreeReaderArray<Float_t> Jet_chHEF(reader, "Jet_chHEF");
  TTreeReaderArray<Float_t> Jet_neHEF(reader, "Jet_neHEF");
  TTreeReaderArray<Float_t> Jet_chEmEF(reader, "Jet_chEmEF");
  TTreeReaderArray<Float_t> Jet_neEmEF(reader, "Jet_neEmEF");
  TTreeReaderArray<Float_t> Jet_muEF(reader, "Jet_muEF");
  TTreeReaderArray<UChar_t> Jet_nConstituents(reader, "Jet_nConstituents");
  TTreeReaderArray<UChar_t> Jet_chMultiplicity(reader, "Jet_chMultiplicity");

  // --------------------------------------------------------------------------
  // Output histograms
  // --------------------------------------------------------------------------
  TH1::SetDefaultSumw2();
  TFile outFile(outputPath.c_str(), "RECREATE");
  if (outFile.IsZombie()) return 1;

  const std::vector<std::string> cutNames = {"All", "Trigger", "Z reco", "a reco", "H reco"};
  TH1D h_cutflow("cutflow", "Cutflow;;Events", cutNames.size(), 0, cutNames.size());
  for (size_t i = 0; i < cutNames.size(); ++i) h_cutflow.GetXaxis()->SetBinLabel(i + 1, cutNames[i].c_str());

  // Object-level control histograms (already filled below)
  TH1D h_nMuon("nMuon", ";Number of muons;Events", 10, 0, 10);
  TH1D h_nElectron("nElectron", ";Number of electrons;Events", 10, 0, 10);
  TH1D h_nJet("nJet", ";Number of jets;Events", 20, 0, 20);

  TH1D h_muon_pt("muon_pt", ";Muon p_{T} [GeV];Muons", 50, 0, 200);
  TH1D h_muon_pt1("muon_pt1",";Leading Muon p_{T} [GeV];Muons", 50, 0, 200);
  TH1D h_muon_pt2("muon_pt2",";Sub-Leading Muon p_{T} [GeV];Muons", 50, 0, 200);

  TH1D h_muon_eta("muon_eta", ";Muon #eta;Muons", 50, -2.5, 2.5);
  TH1D h_muon_eta1("muon_eta1",";Leading Muon #eta;Muons", 50, -2.5, 2.5);
  TH1D h_muon_eta2("muon_eta2",";Sub-Leading Muon #eta;Muons", 50, -2.5, 2.5);

  TH1D h_muon_phi("muon_phi",";Muon #phi,Muons",400,-3,3);
  TH1D h_muon_phi1("muon_phi",";Leading Muon #phi",400,-3,3);
  TH1D h_muon_phi2("muon_phi2",";Sub-Leading Muon #phi",400,-3,3);

  TH1D h_muon_dxy("muon_dxy",";Muon tranverse IP, ",601,-0.3,0.3);
  TH1D h_muon_dz("muon_dz",";Muon longitudinal IP, ",601,-0.3,0.3);
  TH1D h_muon_dxy1("muon1_dxy",";Leading Muon tranverse IP, ",601,-0.3,0.3);
  TH1D h_muon_dz1("muon1_dz",";Leadig Muon longitudinal IP, ",601,-0.3,0.3);
  TH1D h_muon_dxy2("muon2_dxy",";Sub_Leading Muon tranverse IP, ",601,-0.3,0.3);
  TH1D h_muon_dz2("muon2_dz",";Sub_Leading Muon longitudinal IP, ",601,-0.3,0.3);
  
  TH1D h_electron_pt("electron_pt", ";Electron p_{T} [GeV];Electrons", 50, 0, 200);
  TH1D h_electron_pt1("electron_pt1",";Leading Electron p_{T} [GeV]; Electrons",50, 0,200);
  TH1D h_electron_pt2("electron_pt2",";Sub-Leading Electron p_{T} [GeV]; Electrons",50, 0,200);

  TH1D h_electron_eta("electron_eta", ";Electron #eta;Electrons", 50, -2.5, 2.5);
  TH1D h_electron_eta1("electron_eta1", ";Leading Electron #eta;Electrons", 50, -2.5, 2.5);
  TH1D h_electron_eta2("electron_eta2", ";Sub-leading Electron #eta;Electrons", 50, -2.5, 2.5);

  TH1D h_electron_phi("electron_phi",";Electron #phi,Electrons",400,-3,3);
  TH1D h_electron_phi1("electron_phi1",";Leading Electron #phi,Electrons",400,-3,3);
  TH1D h_electron_phi2("electron_phi2",";Sub_leading Electron #phi,Electrons",400,-3,3);

  TH1D h_electron_dxy("electron_dxy",";Electron transverse IP,",601,-0.3,0.3);
  TH1D h_electron_dz("electron_dz",";Electron longitudinal IP",601,-0.3,0.3);
  TH1D h_electron_dxy1("electron1_dxy",";Leading Electron transverse IP,",601,-0.3,0.3);
  TH1D h_electron_dz1("electron1_dz",";Leading Electron longitudinal IP",601,-0.3,0.3);
  TH1D h_electron_dxy2("electron2_dxy",";Sub_Leading Electron transverse IP,",601,-0.3,0.3);
  TH1D h_electron_dz2("electron2_dz",";Sub_Leading Electron longitudinal IP",601,-0.3,0.3);
  
  TH1D h_jet_pt("jet_pt", ";Jet p_{T} [GeV];Jets", 50, 0, 300);
  TH1D h_jet_pt1("jet_pt1", ";Leading Jet p_{T} [GeV];Jets", 50, 0, 300);
  TH1D h_jet_pt2("jet_pt2", ";Sub-Leading Jet p_{T} [GeV];Jets", 50, 0, 300);
  
  TH1D h_jet_eta("jet_eta", ";Jet #eta;Jets", 50, -5, 5);
  TH1D h_jet_eta1("jet_eta1", ";Leading Jet #eta;Jets", 50, -5, 5);
  TH1D h_jet_eta2("jet_eta2", ";Sub-Leading Jet #eta;Jets", 50, -5, 5);
  
  TH1D h_jet_mass("jet_mass", ";Jet mass [GeV];Jets", 50, 0, 50);
  TH1D h_jet_mass1("jet_mass", ";Leading Jet mass [GeV];Jets", 50, 0, 50);
  TH1D h_jet_mass2("jet_mass2", ";Subleading Jet mass [GeV];Jets", 50, 0, 50);

  // Reconstructed bosons (filled once you implement the reconstruction)
  TH1D h_Z_mass("Z_mass", ";m_{ll} [GeV];Events", 60, 60, 120);
  TH1D h_Z_pt("Z_pt", ";p_{T}^{ll} [GeV];Events", 50, 0, 200);
  TH1D h_a_mass("a_mass", ";m_{a} [GeV];Events", 50, 0, 20);
  TH1D h_a_pt("a_pt", ";p_{T}^{a} [GeV];Events", 50, 0, 200);
  TH1D h_H_mass("H_mass", ";m_{lla} [GeV];Events", 60, 80, 200);
  TH1D h_H_pt("H_pt", ";p_{T}^{lla} [GeV];Events", 50, 0, 200);

  // --------------------------------------------------------------------------
  // Event loop
  // --------------------------------------------------------------------------
  const Long64_t nTotal = chain.GetEntries();
  const Long64_t nToProcess = (maxEvents > 0 && maxEvents < nTotal) ? maxEvents : nTotal;
  std::cout << "Processing " << nToProcess << " of " << nTotal << " events" << std::endl;

  Long64_t iEvent = 0;
  while (reader.Next() && iEvent < nToProcess) {
    if (iEvent % 10000 == 0) std::cout << "  event " << iEvent << " / " << nToProcess << std::endl;
    ++iEvent;

    // Event weight: in simulation the generator weight (can be negative!), in data 1.
    // Normalisation to cross section x luminosity is done later, not here.
    const double w = isMC ? **genWeight : 1.0;

    h_cutflow.Fill(0.5, w);

    // ── Trigger: single muon OR single electron ──────────────────────────
    // Note for data: an event can be in both the Muon and EGamma datasets.
    // To avoid double counting, require (!muon trigger && electron trigger)
    // when running on EGamma.
    const bool passMuTrig = *trigMuon;
    const bool passElTrig = *trigElectron;
    if (!passMuTrig && !passElTrig) continue;
    h_cutflow.Fill(1.5, w);

    // ── Object information (raw collections, no selection applied yet) ──
    h_nMuon.Fill(Muon_pt.GetSize(), w);
    h_nElectron.Fill(Electron_pt.GetSize(), w);
    h_nJet.Fill(Jet_pt.GetSize(), w);

    for (size_t i = 0; i < Muon_pt.GetSize(); ++i) {
      h_muon_pt.Fill(Muon_pt[i], w);
      h_muon_eta.Fill(Muon_eta[i], w);
      h_muon_phi.Fill(Muon_phi[i],w);
      h_muon_dxy.Fill(Muon_dxy[i],w);
      h_muon_dz.Fill(Muon_dz[i],w);

      if (i==0) {
        h_muon_pt1.Fill(Muon_pt[i], w);
        h_muon_eta1.Fill(Muon_eta[i], w);
        h_muon_phi1.Fill(Muon_phi[i],w);
        h_muon_dxy1.Fill(Muon_dxy[i],w);
        h_muon_dz1.Fill(Muon_dz[i],w);
      }
      else if (i==1) {
        h_muon_pt2.Fill(Muon_pt[i],w);
        h_muon_eta2.Fill(Muon_eta[i], w);
        h_muon_phi2.Fill(Muon_phi[i],w);
        h_muon_dxy2.Fill(Muon_dxy[i],w);
        h_muon_dz2.Fill(Muon_dz[i],w);
      }
    }
    
    for (size_t i = 0; i < Electron_pt.GetSize(); ++i) {
      h_electron_pt.Fill(Electron_pt[i], w);
      h_electron_eta.Fill(Electron_eta[i], w);
      h_electron_phi.Fill(Electron_phi[i],w);
      h_electron_dxy.Fill(Electron_dxy[i],w);
      h_electron_dz.Fill(Electron_dz[i],w);

      if(i==0) {
        h_electron_pt1.Fill(Muon_pt[i], w);
        h_electron_eta1.Fill(Muon_eta[i], w);
        h_electron_phi1.Fill(Electron_phi[i],w);
        h_electron_dxy1.Fill(Electron_dxy[i],w);
        h_electron_dz1.Fill(Electron_dz[i],w);
      }
      else if (i==1) {
        h_electron_pt2.Fill(Muon_pt[i],w);
        h_electron_eta2.Fill(Muon_eta[i], w);
        h_electron_phi2.Fill(Electron_phi[i],w);
        h_electron_dxy2.Fill(Electron_dxy[i],w);
        h_electron_dz2.Fill(Electron_dz[i],w);
      }
    }
    for (size_t i = 0; i < Jet_pt.GetSize(); ++i) {
      h_jet_pt.Fill(Jet_pt[i], w);
      h_jet_eta.Fill(Jet_eta[i], w);
      h_jet_mass.Fill(Jet_mass[i], w);

      if (i==0) {
        h_jet_pt1.Fill(Muon_pt[i], w);
        h_jet_eta1.Fill(Muon_eta[i], w);
        h_jet_mass1.Fill(Jet_mass[i], w);
      }

      else if (i==1) {
        h_jet_pt2.Fill(Muon_pt[i],w);
        h_jet_eta2.Fill(Muon_eta[i], w);
        h_jet_mass2.Fill(Jet_mass[i], w);
      }
    }
    // Example: build a four-vector of a muon
    //   TLorentzVector mu;
    //   mu.SetPtEtaPhiM(Muon_pt[i], Muon_eta[i], Muon_phi[i], Muon_mass[i]);

    // ====================================================================
    // TODO 1: Select good leptons
    //   e.g. muons:     pT > 10 GeV, |eta| < 2.4, Muon_mediumId, Muon_pfRelIso04_all < 0.15
    //        electrons: pT > 15 GeV, |eta| < 2.5, Electron_cutBased >= 3 (medium)
    //   The leading lepton must be above the trigger threshold
    //   (muon: ~26 GeV, electron: ~35 GeV).
    //
    // TODO 2: Reconstruct the Z boson
    //   Find a same-flavour, opposite-charge lepton pair (mu+mu- or e+e-),
    //   e.g. the one with invariant mass closest to 91.19 GeV.
    //
    // TODO 3: Reconstruct the a boson
    //   Select jets (pT, |eta|, PassJetIdTightLepVeto(...)), remove jets that
    //   overlap with the Z leptons (DeltaR < 0.4), and choose the a candidate,
    //   e.g. the leading remaining jet.
    //
    // TODO 4: Reconstruct the Higgs boson from Z + a.
    // ====================================================================
    //TLorentzVector Z_ee, H_ee;
    //TLorentzVector Z_mumu, H_mumu;
    //TLorentzVector a;
    bool hasZ = false, hasA = false;



    // ... your code here ...

    // if (!hasZ) continue;
    // h_cutflow.Fill(2.5, w);
    // h_Z_mass.Fill(Z.M(), w);
    // h_Z_pt.Fill(Z.Pt(), w);

    // if (!hasA) continue;
    // h_cutflow.Fill(3.5, w);
    // h_a_mass.Fill(a.M(), w);
    // h_a_pt.Fill(a.Pt(), w);

    // H = Z + a;
    // h_cutflow.Fill(4.5, w);
    // h_H_mass.Fill(H.M(), w);
    // h_H_pt.Fill(H.Pt(), w);
  }

  // --------------------------------------------------------------------------
  // Write output
  // --------------------------------------------------------------------------
  outFile.Write();
  outFile.Close();

  std::cout << "\nCutflow (weighted):" << std::endl;
  for (size_t i = 0; i < cutNames.size(); ++i)
    std::cout << "  " << cutNames[i] << ": " << h_cutflow.GetBinContent(i + 1) << std::endl;
  std::cout << "Output written to " << outputPath << std::endl;
  return 0;
}
