
#default universal (non-instrument specific) config parameters can be placed here but need to override with the specific config
gala_setupd=None
galil_simulate=True

from config_edep import * #this is the only place where the instrument-specif config is specified
#TODO: figure out how to pass the namespace of config_edp to all the py that import config.py


#specify here if there is file from simulate folder that will be used by drivers to customize the simulated experiment