# 🎉👋 HELAO 
Hierarchical Experiment Laboratory Orchestration.

# Meaning
Phonetically similar to "Helau" the german word said during Carnival meaning something like "the joy of having fun". This software makes autonomous orchestration a joyful experience. 

# Paradigm
Devices are abstracted as servers and utilize async operation. This allows orchestrating one or multiple instruments spread across the globe. We call this helau_world


# Hierarchy
The hierarchical design of the code achieves:
. instrument-specific configurations, i.e. for a particular piece of hardware
. sharing low level drivers across different instruments, i.e. a particular type of hardware
. defining "actions", i.e. combinations of driver routines, that are meaningful and safe for a given instrument
. orchestrating execution of these actions, e.g. via a user interface


# Orchestrator 
Software that determines what and when actions are executed. Non-safety related decisions on synchronous vs asynchronous execution are made here.
Actions: Single or multi-task routines that are analogous to individual lab actions like "move a motor" or "rinse the cell". Safety/compatibility decisions on synchronous vs. asynchronously execution of tasks
=There is a layer of abstraction between Actions and Server enabling them to be written in different programming languages
Server: Set of functions that translate the available instrument routines to function and argument names that are meaningful for the type of experiment being automated. Some decisions about asynchronous functions are made here. \
Driver: Communicates directly to the hardware. Should be written to be universal across different experimental uses of the hardware.


# Heirarchy relationships
A Config is many-to-many with Drivers, where the Config for a given instrument will include settings related to multiple Drivers, and each Driver will have a different Config for each instrument
A Driver is 1-to-many with Servers, where different servers may translate hardware communications into functions meaningful for the particular type of experiment
A Server is many to many with Action Libraries, where any given action library will combine actions across different pieces of hardware, and a given server can be used in any number of Action Libraries
An Action Library is 1-to-many with Orchestrators, an Action Library dictates the scope of actions available to the Orchestrator, so an Orchestrator is based on a single Actions library, although multiple Orchestrators can be written for a given Actions.

# Kernels
The (Orchestrator, Action Library) runs in 1 kernel. Each (Server,Driver) runs on its own kernel. Cross-kernel communication is via FastAPI.

# git ignore
The config folder in the repository will contain examples of how to specify the settings for each type of hardware, but each instrument-specific config file is relevant only the specific hardware and is thus the config folder is in git ignore.
