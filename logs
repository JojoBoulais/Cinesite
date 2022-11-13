import re

class Num():
    """Contains time, mem, info from a .log file's line"""
    def __init__(self, time, mem="", info="", warning=False):
        self.time = time
        self.mem = mem
        self.info = info
        self.warning = warning

class Error():
    """Contains error's info from a .log file's line"""
    def __init__(self, errorInfo):
        self.info = errorInfo


class Warning():
    """Contains warning's info from a .log file's line"""
    def __init__(self, warningInfo):
        self.info = warningInfo


def readLogFile(logFile):
    """Read line from a .log file

    :param logFile: .log file  -str
    :return: str
    """
    with open(logFile, "r") as logF:
        lines = logF.readlines()
        logF.close()
    return lines


def getTimeUsageErrors(lines):
    """Will return lists of Num, Error, Warning objects.

    :param lines: lines from a .log file
    :return: nums, errors, warnings -list, list, list
    """
    nums = []
    errors = []
    warnings = []

    for line in lines:

        # Render times/Mem usage
        if re.search("^..:..:..", line):

            time = line[0:8]

            mem = ""
            memSplit = re.split(" +", line)
            if len(memSplit) > 1:
                mem = memSplit[1]

            info = line[re.search("\|", line).start()+1:]

            if "WARNING" in line:
                newLog.warning = True

            newLog = Num(time, mem, info)
            nums.append(newLog)

        # Error
        elif re.search("^ERROR", line):
            errorInfo = line[re.search("\|", line).start()+1:]
            newError = Error(errorInfo)
            errors.append(newError)

        # Warning
        elif re.search("^WARNING", line):
            warningInfo = ""
            warningSplitA = re.search("^WARNING.*\| +", line)
            warningSplitB = re.search("^WARNING.*:", line)

            if warningSplitA:
                warningInfo = line[re.search("\|", line).start()+1:]
            elif warningSplitB is not None and warningInfo == "":
                warningInfo = line[re.search(":", line).start()+1:]

            newWarning = Warning(warningInfo)
            warnings.append(newWarning)

    return nums, errors, warnings
