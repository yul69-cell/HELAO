# For reference:
# need to install the sdk and point to the dll
# a measurement is the sequence of Connecting -> Uploading Firmware -> Selecting Procedure -> Measuring Procedure -> Releasing The Potentiostat and maybe disconnecting if needed
# A Procedure has commands -> command lists -> parameters I believe it is better to set these in the .nox files as most measurements will
# be done in a similar way for the different chemistries. Live plotting is not really possibile as ironpython has no matplotlib
# so we have to append the data to a textfile and maybe have an external thrid program run the live plotting if needed

import os, sys
import clr  # this is the .NET interface
from copy import copy
import pickle
from time import sleep
import json

class Autolab:
    def __init__(self):
        # Set the paths correctly and point to the standart procedurs
        self.basep = r'C:\Program Files\Metrohm Autolab\Autolab SDK 1.11'
        self.procp = r'C:\Users\Operator\Documents\git\auro-master\conf\echemprocedures'
        self.hwsetupf = r'C:\ProgramData\Metrohm Autolab\12.0\HardwareSetup.AUT88078.xml'
        self.micsetupf = os.path.join(self.basep, r'Hardware Setup Files\Adk.bin')
        # Before adding a procedure check if it compatible with NOVA 1.11 not all procedures
        # from NOVA 2.X are compatible
        self.proceduresd = {'cp': os.path.join(self.procp, 'CP_v1.nox'),
                            'ca': os.path.join(self.procp, 'CA_v1.nox'), 
                            'cv': os.path.join(self.procp, 'CV_v1.nox'),
                            'eis': os.path.join(self.procp, 'EISP_v1.nox'),
                            'ocp': os.path.join(self.procp, 'OCP_v1.nox')}
        sys.path.append(self.basep)
        # This is the magic of ironpython. Could check if this works with pythonnet
        # The error that I seem to get is that an assembly cannot be loaded. Typically EcoChemie
        clr.AddReference('EcoChemie.Autolab.Sdk')
        from EcoChemie.Autolab import Sdk as sdk
        self.inst = sdk.Instrument()
        self.connect()
        
    def connect(self):
        # this connects to the PGSTAT302N with the FRA32M module
        self.inst.HardwareSetupFile = self.hwsetupf
        self.inst.AutolabConnection.EmbeddedExeFileToStart = self.micsetupf
        # now we can connect
        self.inst.Connect()
        
    def disconnect(self):
        try:
            self.proc.Abort()
        except:
            print('Procedure abort failed. Disconnecting anyhow.')
        self.inst.Disconnect()
        
    def ismeasuring(self):
        try:
            return self.proc.IsMeasuring
        except:
            # likely no procedure set
            return False
    '''
    def cellon(self): #this stangely does not do anything
        return self.inst.Ei.CellOnOff.On
    
    def celloff(self):
        return self.inst.Ei.CellOnOff.Off
    '''
    def potential(self):
        # just gives the currently applied raw potential vs. ref
        return float(self.inst.Ei.Potential)
    
    def current(self):
        # just gives the currently applied raw potential
        return float(self.inst.Ei.Current)
    
    def appliedpotential(self):
        return float(self.inst.Ei.PotentialApplied)
    
    def abort(self):
        try:
            self.proc.Abort()
        except:
            print('Likely nothing to abort')
            
    def parsenox(self,path,comm,params):
        self.finished_proc = self.inst.LoadProcedure(path)
        names = [str(n) for n in self.finished_proc.Commands[comm].Signals.Names]
        self.data = {n:[float(f) for f in self.finished_proc.Commands[comm].Signals[n].Value] for n in names}
        self.data['params'] = params
        with open(path.replace('nox','json'),'w') as f:
            json.dump(self.data, f)
            
    def EIS(self, safepath, fname,procedure=None):
        if procedure == None:
            self.proc = self.inst.LoadProcedure(self.proceduresd['eis'])
        else:
            self.proc = self.inst.LoadProcedure(procedure)
        self.fra = self.proc.FraCommands['FIAScan']
        eis_signals = ['Time', 'Frequency', 'H_Real', 'H_Imaginary', 'H_Modulus', 'H_Phase','RawTime', 'RawChannelX', 'RawADCResolutionX', 'RawChannelY', 'RawADCResolutionY','ChannelXDC', 'ChannelYDC']
        # modus = self.inst.Ei.Mode
        self.proc.Measure()
        sleep(0.1)
        self.data = {s: {} for s in eis_signals}
        i = 0
        while self.proc.IsMeasuring:
            for eis_signal in eis_signals:
                try:
                    val = copy(self.fra.Signals[eis_signal].Value)
                    val = [v for v in val]
                    if not len(val) == 0:
                        if len(val) == 1:
                            self.data[eis_signal][i].append(val[0])
                        else:
                            self.data[eis_signal][i].append(val)
                except:
                    print('Exception...')
            i += 1
            sleep(0.5)
        with open(os.path.join(safepath, fname + '.pck'), 'wb') as f:
            pickle.dump(self.data,f)
        self.proc.SaveAs(os.path.join(safepath, fname + '.nox'))
        
    def CA(self, safepath, fname,procedure=None,potential=0.0,duration=10,live=0):
        #a.CA(r'C:\Users\Operator\Documents\git\auro-master\temp','ca_new')
        self.proc = self.inst.LoadProcedure(self.proceduresd['ca'])
        self.proc.Commands['applypotential'].CommandParameters['Setpoint value'].Value = potential
        self.proc.Commands['recordsignal'].CommandParameters['Duration'].Value = duration
        self.proc.Measure()
        #setup a dict for live viewing
        self.data = {s: {} for s in ['Potential','Current']}
        i = 0
        while self.proc.IsMeasuring:
            #this is only for live viewing
            if life:
                print('_Potential:{}_Current: {}'.format(self.potential(),self.current()))
            sleep(0.1)
        self.proc.SaveAs(os.path.join(safepath, fname + '.nox'))
        params = {'potential':potential, 'duration':duration,'procedure':self.proceduresd['ca']}
        self.parsenox(os.path.join(safepath, fname + '.nox'),comm='recordsignal',params=params)
        
    def CP(self,safepath, fname, current=0,duration=5,live=0):
        #a.CA(r'C:\Users\Operator\Documents\git\auro-master\temp','ca_new')
        self.proc = self.inst.LoadProcedure(self.proceduresd['cp'])
        self.proc.Commands['applycurrent'].CommandParameters['Setpoint value'].Value = current
        self.proc.Commands['recordsignal'].CommandParameters['Duration'].Value = duration
        self.proc.Measure()
        #setup a dict for live viewing
        self.data = {s: {} for s in ['Potential','Current']}
        i = 0
        sleep(1)
        while self.proc.IsMeasuring:
            #this is only for live viewing
            if life:
                print('_Potential:{}_Current: {}'.format(self.potential(),self.current()))
            sleep(0.1)
        self.proc.SaveAs(os.path.join(safepath, fname + '.nox'))
        params = {'current':current, 'duration':duration,'procedure':self.proceduresd['ca']}
        self.parsenox(os.path.join(safepath, fname + '.nox'),comm='recordsignal',params=params)
        
    def CV(self,safepath, fname, v0=0,uv=0.5,lv=-0.5,cycles=2,speed=1,live=0):
        #a.CA(r'C:\Users\Operator\Documents\git\auro-master\temp','ca_new')
        self.proc = self.inst.LoadProcedure(self.proceduresd['cv'])
        self.proc.Commands['cvlinear'].CommandParameters['Start potential (V)'].Value = v0
        self.proc.Commands['cvlinear'].CommandParameters['Upper vertex potential (V)'].Value = uv
        self.proc.Commands['cvlinear'].CommandParameters['Lower vertex potential (V)'].Value = lv
        self.proc.Commands['cvlinear'].CommandParameters['Number of start or vertex potential crossings'].Value = cycles
        self.proc.Commands['cvlinear'].CommandParameters['Scan rate (V/s)'].Value = speed
        self.proc.Measure()
        #setup a dict for live viewing
        self.data = {s: {} for s in ['Potential','Current']}
        i = 0
        sleep(1)
        while self.proc.IsMeasuring:
            #this is only for live viewing
            if live:
                print('_Potential:{}_Current: {}'.format(self.potential(),self.current()))
            sleep(0.1)
        self.proc.SaveAs(os.path.join(safepath, fname + '.nox'))
        params = {'v0':v0, 'uv':uv,'lv':lv,'cycles':cycles,'speed':speed,'procedure':self.proceduresd['cv']}
        self.parsenox(os.path.join(safepath, fname + '.nox'),comm='cvlinear',params=params)
    def ocp(self,safepath):
        pass

#a = Autolab()
#a.CA(r'C:\Users\Operator\Documents\git\auro-master\temp','ca_new') #ok
#a.CP(r'C:\Users\Operator\Documents\git\auro-master\temp','cp_new') #ok
#a.EIS(r'C:\Users\Operator\Documents\git\auro-master\temp','eis_new') #half
#a.CV(r'C:\Users\Operator\Documents\git\auro-master\temp','cv_new',speed=1.0) #ok
#a.OCP(r'C:\Users\Operator\Documents\git\auro-master\temp','ocp_new') #TODO
#a.Cylce(r'C:\Users\Operator\Documents\git\auro-master\temp','cycle_new') #TODO
#a.CycleEIS(r'C:\Users\Operator\Documents\git\auro-master\temp','cycle_EIS_new') #TODO
