exfiltools
==========

--Inspired by --> https://raw.githubusercontent.com/todb/junkdrawer/master/exfiltrate-data.rb

Python ICMP Exfil compatible with metasploit

This utility will send out files via ICMP to an listening metasploit auxiliary server.  

It also has the option to compress the file.

Checks for nping from nmap as well in x86/x64

ICMP exfiltration utility for Metasploit icmp_exfil.

optional arguments:
  -h, --help            show this help message and exit
  
  -i IPAddress, --ipaddress / The destination IP Address.

  -f, --file / The file to exfiltrate.
  
  -s, --size / size of data packet.

  -c, --compress / Enable zlib compression. To retrieve "cat file | xxd -r -ps | openssl zlib -d | tee >(md5sum) > out"
  
  --version             show program's version number and exit
  

