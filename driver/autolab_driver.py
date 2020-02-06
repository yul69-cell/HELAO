#this is a test version that only runs in ironpython!

# AURO-POTI
# Script to run the Mtrohm-Autolab Potentiostat through python
# this has been tested in ironpython and pythonnet might not work
# (c) 2020 Dr.-Ing. Helge S. Stein

import sys, os
import clr
from time import sleep

basepath = r'C:\Program Files\Metrohm Autolab\Autolab SDK 1.11'
hwsetupf = os.path.join(basepath,r'Hardware Setup Files\PGSTAT302N\HardwareSetup.FRA32M.xml')
micsetupf = os.path.join(basepath,r'Hardware Setup Files\Adk.bin')
procp = os.path.join(basepath,r'Standard Nova Procedures')
proceduresd = {'ca_F':os.path.join(procp,'Chrono amperometry fast.nox'),
                'ca':os.path.join(procp,'Chrono amperometry.nox'),
                'cv_BA':os.path.join(procp,'Cyclic voltammetry with BA.nox'),
                'cv_ECD':os.path.join(procp,'Cyclic voltammetry with ECD.nox'),
                'cv':os.path.join(procp,'Cyclic voltammetry.nox'),
                'eis':os.path.join(procp,'FRA impedance potentiostatic.nox')}
'''
commandsd = {'CV staircase': 'FHCyclicVoltammetry2',
                'LSV staircase': 'FHLinearSweep',
                'CV linear scan': 'CVLinearScanAdc164',
                'CV linear scan high speed': 'CVLinearScanAdcHs',
                'CV staircase galvanostatic': 'FHCyclicVoltammetryGalvanostatic',
                'LSV staircase galvanostatic': 'FHLinearSweepGalvanostatic',
                'Record signals (> 1 ms)': 'FHLevel',
                'Chrono methods': 'RecordLevelsContainer',
                'Chrono methods high speed': 'HighSpeedLevelsContainer',
                'Chrono methods high speed galvanostatic': 'HighSpeedLevelsContainer',
                'FRA frequency scan potentiostatic': 'FIAScan',
                'FRA frequency scan galvanostatic': 'FIAScan',
                'FRA frequency scan external': 'FIAScan',
                'Corrosion rate, fit': 'CorrosionRateFitCommand',
                'Corrosion rate, Tafel slope': 'CorrosionRateTafelSlopeCommand',
                'SG smooth': 'MathSmoothSavitzkyGolay',
                'Peak search': 'PeakSearchCommand',
                'Nested procedure': 'ExecCommandSequence',
                'Calculate signal': 'MathParser',
                'Windower': 'SignalWindowerCommand',
                'Scan selector': 'SignalWindowerCommand'}
'''
sys.path.append(basepath)
clr.AddReference('EcoChemie.Autolab.Sdk.dll')
from EcoChemie.Autolab import Sdk as sdk

#Let us instanciate a instrument.
inst = sdk.Instrument()
#We need to load the hardware setup file i.e. HardwareSetup.FRA32M.xml
#and upload the firmware to the potentiostat
inst.HardwareSetupFile = hwsetupf
inst.AutolabConnection.EmbeddedExeFileToStart = micsetupf
#now we can connect
inst.Connect()

proc = inst.LoadProcedure(proceduresd['eis'])
#If we want to select a parameter the structure is:
#Procedure -> Command -> CommandParameter -> Parameter
#A Procedure can have multiple commands

#apparently one way to get the data:
comm = proc.Commands['FHCyclicVoltammetry2']
potential = comm.Signals['Potential'].Value

#other way for live viewing
potential = inst.EI.Sampler.GetSignal('WE(1).Potential')


inst.Disconnect()
