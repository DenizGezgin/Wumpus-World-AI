import sys
sys.path.append('.')
sys.path.append('..')

import os
import time
import math
from wumpus.World import World


def main():

    args = sys.argv

    if len(args) == 2: #Fix me back to 1
        # Run on a random world and exit
        startTime = round(time.time() * 1000)
        world = World()
        score = world.run()
        elapsedTime = round(time.time() * 1000) - startTime
        print ("Your agent scored: " + str(score))
        print ("Time in msec: " + str(elapsedTime))
        return

    # Important Variables
    search     = True
    debug      = False
    verbose    = False
    randomAI   = False
    manualAI   = False
    folder     = False
    worldFile  = ""
    outputFile = ""

    firstToken = args[1]

    # If there are options
    if firstToken[0] == '-':
        # Parse Options
        for char in firstToken[1:]:
            if char == '-':
                continue
            elif char == 'f' or char == 'F':
                folder = True
            elif char == 'v' or char == 'V':
                verbose = True
            elif char == 'r' or char == 'R':
                randomAI = True
            elif char == 'm' or char == 'M':
                manualAI = True
            elif char == 'd' or char == 'D':
                debug = True
            else:
                print ( "Wumpus_World [Options] [InputFile] [OutputFile]" )
                print ( )
                print ( "Options:" )
                print ( "\t-d Debug mode, which displays the game board" )
                print ( "\t   after every mode." )
                print ( "\t-h Displays help menu and quits." )
                print ( "\t-f treats the InputFile as a folder containing" )
                print ( "\t   worlds. This will trigger the program to" )
                print ( "\t   display the average score and standard" )
                print ( "\t   deviation instead of a single score. InputFile" )
                print ( "\t   must be entered with this option." )
                print ( )
                print ( "InputFile: A path to a valid Wumpus World File, or" )
                print ( "           folder with -f. This is optional unless" )
                print ( "           used with -f." )
                print ( )
                print ( "OutputFile: A path to a file where the results will" )
                print ( "            be written. This is optional." )
                print ( )
                return

        if randomAI and manualAI:
            # If both AI's on, turn one off and let the user know.
            manualAI = False
            print("[WARNING] Manual AI and Random AI both on; Manual AI was turned off.")

        if len(args) >= 3:
            worldFile = args[2]
        if len(args) >= 4:
            outputFile = args[3]
    else:
        if len(args) >= 2:
            worldFile = args[1]
        if len(args) >= 3:
            outputFile = args[2]

    if worldFile == "":
        if folder:
            print ( "[WARNING] No folder specified; running on a random world." )
        startTime = round(time.time() * 1000)
        world = World ( debug, randomAI, manualAI, search )
        score = world.run()
        elapsedTime = round(time.time() * 1000) - startTime
        print ( "The agent scored: " + str(score) )
        print ( "Time in msec: " + str(elapsedTime) )
        return

    if folder:
        listOfWorlds = None

        try:
            listOfWorlds = os.listdir ( worldFile )
        except:
            print ( "[ERROR] Failed to open directory." )
            return

        numOfScores = 0
        sumOfScores = 0
        sumOfScoresSquared = 0
        startTime = 0
        totalTime = 0
        elapsedTime = 0

        for file in listOfWorlds:
            if verbose:
                print ( "Running world: " + str(file) )

            score = None
            try:
                newLineDelim = "\n"
                if "\r\n".encode() in open(worldFile + "/" + file,"rb").read():
                    newLineDelim = "\r\n"
                startTime = round(time.time() * 1000)
                world = World ( debug, randomAI, manualAI, search, open ( worldFile + "/" + file, 'r', newline=newLineDelim ) )
                score = world.run()
                elapsedTime = round(time.time() * 1000) - startTime

            except Exception:
                numOfScores = 0
                sumOfScores = 0
                sumOfScoresSquared = 0
                break;

            numOfScores += 1
            sumOfScores += score
            sumOfScoresSquared += score*score
            totalTime += elapsedTime

        avg = None
        std_dev = None

        if numOfScores != 0:
            avg = sumOfScores / numOfScores
            std_dev = math.sqrt ( (sumOfScoresSquared - ((sumOfScores*sumOfScores) / numOfScores) ) / numOfScores)
        else:
            avg = float('nan')
            std_dev = float('nan')

        if outputFile == "":
            print ( "The agent's average score: " + str(avg) )
            print ( "The agent's standard deviation: " + str(std_dev) )
            print ( "Total time in msec: " + str(totalTime) )
        else:
            try:
                outFile = open ( outputFile, 'w' )
                outFile.write ( "SCORE: " + str(avg) + '\n' )
                outFile.write ( "STDEV: " + str(std_dev) )
                outFile.write ( "TIME: " + str(totalTime) )
                outFile.close ( )
            except Exception:
                print( "[ERROR] Failure to write to output file." )

        return

    try:
        if verbose:
            print ( "Running world: " + worldFile )

        newLineDelim = "\n"
        if "\r\n".encode() in open(worldFile,"rb").read():
            newLineDelim = "\r\n"
        startTime = round(time.time() * 1000)
        world = World ( debug, randomAI, manualAI, search, open ( worldFile, 'rt', newline=newLineDelim ) )
        score = world.run()
        elapsedTime = round(time.time() * 1000) - startTime

        if outputFile == "":
            print ( "The agent scored: " + str(score) )
            print ( "Time in msec: " + str(elapsedTime) )
        else:
            try:
                outFile = open ( outputFile, 'w' )
                outFile.write ( "SCORE: " + str(score) )
                outFile.write ( "TIME: " + str(elapsedTime) )
                outFile.close ( )
            except:
                print ( "[ERROR] Failure to write to output file." )
    except Exception:
        print ( "[ERROR] Failure to open file." )

main()