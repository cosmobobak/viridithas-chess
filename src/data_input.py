def get_engine_parameters():
    out = dict()
    
    out["human"] = False 
    if input("Is there a human opponent? (Y/N) ").upper() == "Y":
        out["human"] = True

    if input("Would you like to set a position from FEN? (y/n) ").upper() == "Y":
        out["fen"] = input("FEN: ")
        out["pgn"] = ""
    elif input("Would you like to set a position from PGN? (y/n) ").upper() == "Y":
        out["fen"] = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        out["pgn"] = input("PGN: ")
    else:
        out["pgn"] = ""

    out["timeLimit"] = 10000000000
    out["advancedTC"] = [0, 0]

    controlType = input("Advanced, Simple, or Infinite time control? \n[a/s/i]: ").upper()
    while controlType not in ["A", "S", "I"]:
        controlType = input("[a/s/i]: ").upper()

    if controlType == 'S':
        out["timeLimit"] = int(input("Enter time limit in seconds: "))

    elif controlType == 'A':
        out["advancedTC"][0] = int(input("Enter minutes: "))
        out["advancedTC"][1] = int(input("Enter increment: "))

    out["book"] = False
    out["fun"] = False
    if input("Would you like to use an opening book? (y/n) ").upper() == 'Y':
        out["book"] = True
        if input("Would you like to pick varied openings? (y/n) ").upper() == 'Y':
            out["fun"] = True 

    out["contempt"] = int(input("Enter contempt in millipawns: "))

    return out
