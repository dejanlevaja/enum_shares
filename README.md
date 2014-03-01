enum_shares
===========

Shared folders enumeration tool


Enum_Shares  enumerates shared folders across the network and under a custom user account. It can check if the shared folder is writable for the current user.  It can save you a lot of time when you need to discover directories allowing "write" to everyone or some specific user (group member).


Syntax is as follows:

./share_enum.py -t 10.10.10.0/24 -u mydomain\\myuser -p Password -w -o logfile.txt

or

./share_enum.py -t 10.10.10.222 -u someuser -p somepass -n threads (default:100)

or any combination of  [-t|-u|-p|-w|-o|-n]
