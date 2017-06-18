# ModelMMORPG

ModelMMORPG is a scientific project sponsored by the Croatian Science Foundation. Massively multi-player on-line role playing games (MMORPGs) give us the opportunity to study two important aspects of computing: (1) large-scale virtual social interaction of people (players) and (2) the design, development and coordination of large-scale distributed artificial inteligence (AI). 

A common denominator for both aspects are the methods used to study them: social interaction can be descibed and simulated using agent-based models (ABM social science perspective) whilst distributed AI is commonly modelled in terms of multi-agent systems (MAS computer science perspective).

The important question to ask in both perspectives is how do agents organize in order to perform their tasks and reach their objectives? Project ModelMMORPG (Large-Scale Multi-Agent Modelling of Massively On-Line Role-Playing Games) will employ a combined empirical and theoretical approach towards finding the answer to this question.

From the empirical side, we shall study the human behaviour on a number of venues across various gaming servers in order to find most suitable structures, cultures, processes, strategies and dynamics employed by most successful player communities.

From the theoretical side, we shall test a multitude of organizational architectures from organization theory in various MMORPG settings, and compare them with methods found in empirical research.

Our research is therefore aimed towards enriching the organizational design methods for the development of MMORPG to foster the development of self-organizing and adaptable networks of large-scale multi-agent systems.

## Main Goals:

1) To identify and formalize adequate organizational design methods for developing LSMAS in MMORPGs.

2) To couple them with real-life and future scenarios from industry.

3) To provide open and accessible tools, which will allow for design, development, implementation, control, simulation and maintenance of LSMAS in MMORPGs.

The quest for the dragon egg is a quest specially designed for the Mana World MMORPG that shall allow us to study the organizational behaviour of players on-line.

The provided repository deals with the implementation of an end-point plug-in for a large-scale multi-agent system's modelling tool developed by ModelMMORPG.


## Testing

In order to test the current implementation of the agent you need to have an active account on a ManaWorld server. *Beware, most active servers prohibit the use of automated bots and players!* Thus, firstly make sure the server you are using allows usage of bots or setup an own dedicated server for yourself. After cloning the repository add a file testconf.py with the following data:

```
SERVER = 'your server or ip' 
PORT = 6901 # make sure this is right
USERNAME = 'your username'
PASSWORD = 'your password'
CHARACTER = 0 # the index of your registered character - 1
KBFOLDER = '/path/to/kbs' # Path were you want to store your agents' knowledge bases
```

To test the low-level interface run

```
./llinterface.py
```

The program will run the low-level interface and provide you with an options menu. In order to see what the bot is actually doing when using the various actions, use an additional account and the ManaPlus client to connect to the server with another character.

To test the high level interface run

```
./hlinterface.py
```

The interface will start and try to solve quests by it self. This part is highly experimental and not fully functional. The script hass the following syntax:

```
usage: hlinterface.py [-h] [--name NAME] [--num NUM] [--interval INTERVAL]
                      [--clear]

Create a TMW agent player (mali_agent[num])

optional arguments:
  -h, --help           show this help message and exit
  --name NAME          Create a TMW agent "mali_agent[num]" agents
  --num NUM            Create [num] TMW agents from [name] to [name+num]
                       "mali_agent[i]" agents
  --interval INTERVAL  Interval between agent instances in seconds
  --clear              Clear existing knowledge bases (DANGEROUS: Deletes all
                       .pl files from KBFOLDER)
```
