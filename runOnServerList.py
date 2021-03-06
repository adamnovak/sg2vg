#!/usr/bin/env python2.7


"""
Given a server list with following format

region	url	trivial	contributor	refOnly
brca1	http://bla.compute.amazonaws.com/trivial-brca1/	yes	null	no
brca2	http://bla.compute.amazonaws.com/trivial-brca2/	yes	null	no
etc.

run sg2vg on each server in the list. quick script designed to check if
sg2vg runs without error on all the latest servers

"""

import argparse, sys, os, os.path, random, subprocess, shutil, itertools
import collections, urllib2, shutil, subprocess, glob, doctest
import urllib2, datetime

def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__, 
        formatter_class=argparse.RawDescriptionHelpFormatter)
    
    parser.add_argument("serverList",
            help="tab-separated server list.  first line is header. url 2nd col"
            " of other lines.  can be url with http:// prefix")
    parser.add_argument("outDir",
                        help="output directory")
    parser.add_argument("--version",
                        help="protocol version",
                        default="v0.6.g")
    parser.add_argument("--page",
                        help="sg2vg pageSize", type=int,
                        default=None)
    parser.add_argument("--vg",
                        help="write vg instead of json (with vg mod -X 100 and vg ids -s)",
                        action="store_true",
                        default=False)
    
    args = args[1:]

    options = parser.parse_args(args)

    return options

def run_server(line, options, errorSummary):
    """
    extract url from line in server file.  run sg2vg on it.
    errorSummary is list of [errorCount, errorLog]
    """
    name, url = parseLine(line)
    vurl = os.path.join(url, options.version)

    # pipe stdout and stderr to files
    if not options.vg:
        outPath = os.path.join(options.outDir, name + ".json")
    else:
        outPath = os.path.join(options.outDir, name + ".vg")
    outFile = open(outPath, "w")
    errPath = os.path.join(options.outDir, name + ".stderr")
    errFile = open(errPath, "w")

    flags = "-u"
    if options.page is not None:
        flags += " -p {}".format(options.page)
    now = datetime.datetime.now()
    command = "sg2vg {} {}".format(vurl, flags)
    if options.vg:
        # hardcode adams options:
        command += " | vg view -Jv - | vg mod -X 100 - | vg ids -s -"
    ret = subprocess.call(command, shell=True, stdout=outFile,
                          stderr=errFile, bufsize=-1)

    # read error back into string and close files
    outFile.close()
    errFile.close()
    errFile = open(errPath, "r")
    errorString = errFile.read()
    errFile.close()

    # keep a log of whats happening in stderr
    sys.stderr.write(now.strftime("%Y-%m-%d %H:%M:%S\n"))
    sys.stderr.write(command)
    sys.stderr.write("\n")
    sys.stderr.write(errorString)
    sys.stderr.write("\n")

    # keep some error summary info in a running string
    if ret != 0:
        errorSummary[0] += 1
        errorSummary[1] += "{}\t{}: {}\n".format(name, url,
                                                mungeError(errorString))
        
def parseLine(line):
    """
    parse a line of server listing, returning name, url
    """
    toks = line.split("\t")
    if len(toks) < 2:
        raise RuntimeError("Invalid Server Line: {}".format(line))
    url = toks[1]
    if not url.startswith("http://"):
        raise RuntimeError("Invalid Server URL: {}".format(url))
    utoks = url.split("/")
    if len(utoks) < 4:
        raise RuntimeError("Invalid Server URL: {}".format(url))
    name = utoks[-1]
    if len(name) == 0:
        name = utoks[-2]
    if len(name) == 0:
        raise RuntimeError("Invalid Server URL: {}".format(url))
    return name, url
    
def mungeError(errorString):
    """
    pluck out body of runtime_error from sg2vg output
    """
    p = errorString.find("runtime_error:")
    if p >= 0:
        return errorString[p + len("runtime_error:"):]
    else:
        return "Error not parsed -- see log\n" 

def main(args):
    
    options = parse_args(args)

    if not os.path.isdir(options.outDir):
        os.makedirs(options.outDir)

    # read url list text file
    if options.serverList.startswith("http://"):
        serverFile = urllib2.urlopen(options.serverList)
    else:
        serverFile = open(options.serverList)
    serverLines = [line for line in serverFile][1:]
    serverFile.close()

    errorSummary = [0, ""]
    
    # do each line
    for line in serverLines:
        if len(line.strip()) > 0:
            run_server(line, options, errorSummary)

    if errorSummary[0] > 0:
        sys.stderr.write("Error Summary\n")
        sys.stderr.write(":\n{}\n".format(errorSummary[1]))
    sys.stderr.write("{} Errors\n\n".format(errorSummary[0]))
                    
if __name__ == "__main__" :
    sys.exit(main(sys.argv))
