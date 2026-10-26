Target = HZaTutorial
all: $(Target)

ROOTFLAGS = $(shell root-config --cflags) -g
ROOTLIBS  = $(shell root-config --glibs)

# Defaults for `make run` â€” override on the command line, e.g.
#   make run FILELIST=../configs/filelists/signal_mA2p0GeV.txt NEVENTS=1000
FILELIST ?= signal_mA1p0GeV.txt
# FILELIST ?= signal_mA1p0GeV_laptop.txt
OUTPUT   ?= tutorial_output.root
NEVENTS  ?= -1
NFILES   ?= -1

$(Target): $(Target).cxx
	g++ -O2 -Wall -o $@ $< $(ROOTFLAGS) $(ROOTLIBS)

run: $(Target)
	./$(Target) -f $(FILELIST) -o $(OUTPUT) -n $(NEVENTS) -m $(NFILES)

clean:
	rm -f $(Target) *.o

.PHONY: all run clean
