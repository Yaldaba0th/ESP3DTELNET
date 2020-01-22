#!/usr/bin/env python
# coding: utf-8

import telnetlib
import functools
import time

def readm27(mess):
        if b"Not SD printing" in mess:
            return "notp",0.0
        #elif b"T:" in mess :
        #    return "heat",0.0
        elif b"SD printing" in mess:
            text=mess.decode("utf-8")
            percentext=""
            for l in text:
                if (l>='0' and l<='9') or l=="/":
                    percentext+=l
            temp=percentext.split("/")
            return "print",100*int(temp[0])/int(temp[1])
        else:
            return "else",0.0
            

def checkanswer(mess):
        if b"Resend" in mess:
            return True
        elif b"ok" in mess:
            return False
        elif b"T:" in mess :
            print("Printer is heating, wait a minute please.")
            for n in range(6):
                time.sleep(10)
                print(str((n+1)*10)+" seconds passed...")
            print("Ready")
            return True
        else:
            return True
def showmenu(oplist):
        print("Select option:")
        for opn, opt in enumerate(opciones):
            print(str(opn+1)+". "+opt)
        select=input("Enter option number: ")
        return select
def parseco(command,cs,ln):
        prefix = "N" + str(ln) + " " + command
        cs=functools.reduce(lambda x, y: x ^ y, map(ord, prefix))
        ln=ln+1
        return prefix + "*" + str(cs), cs, ln
def leefile(filename):
        file = open(filename, 'r') 
        sep = ';'
        comandos=[]
        comandos.append("M28 "+filename)
        for line in file:
            rest = (line[:-1]).split(sep, 1)[0]
            if len(rest)>0:
                if rest[-1]==" ":
                    rest=rest[:-1]
                comandos.append(rest)
        comandos.append("M29 "+filename)
        file.close()
        return comandos
    
cs=0
ln=0
host = "192.168.43.101"
port = "8888"
tn = telnetlib.Telnet(host, port)

print("----------Connecting----------")
command,cs,ln = parseco("M110",cs,ln)
send=True
while send:
    print(command)
    tn.write((command+"\n").encode('ascii'))
    mess=tn.read_until(b"ok",timeout=3)
    print(mess)
    send=checkanswer(mess)

print("----------Connected----------")

print("Welcome!")
opciones=["Check SD","Upload to SD","Print","Check Progress","Exit"]
loop=True
#ln+=1
while loop:
    
    sel="none"
    seln=showmenu(opciones)
    print()
    try:
        if (int(seln)<1):
            print("Invalid!")
        else:
            sel=opciones[int(seln)-1]
    except ValueError:
        print("Invalid!")
    
    if sel == "Exit":
        print("Exiting...")
        loop=False
    
    if sel == "Upload to SD":
        print("Uploading...")
        filnam=input("Enter filename: ")
        comandos=leefile(filnam)
        for rawco in comandos:
            command,cs,ln=parseco(rawco,cs,ln)
            send=True
            while send:
                print(command)
                tn.write((command+"\n").encode('ascii'))
                mess=tn.read_until(b"ok",timeout=10)
                print(mess)
                send=checkanswer(mess)
        print("FILE "+filnam+" UPLOADED\n")
        
    if sel == "Print":
        filnam=input("Enter filename to print: ")
        comandos=[("M23 "+filnam),"M24"+filnam]
        for rawco in comandos:
            command,cs,ln=parseco(rawco,cs,ln)
            send=True
            while send:
                print(command)
                tn.write((command+"\n").encode('ascii'))
                mess=tn.read_until(b"ok",timeout=10)
                print(mess)
                send=checkanswer(mess)
        print("Printing\n")
        
    if sel == "Check Progress":
        command,cs,ln=parseco("M27",cs,ln)
        send=True
        while send:
            print(command)
            tn.write((command+"\n").encode('ascii'))
            mess=tn.read_until(b"ok",timeout=10)
            print(mess)
            send=checkanswer(mess)
        est,per=readm27(mess)
        if est == "notp":
            print("Not printing anything\n")
        elif est == "heat":
            print("Printer heating\n")
        elif est == "print":
            print("PRINT PROGRESS: "+str(per)+"%\n")
        else:
            print("Printer preparing to print\n")
           
    if sel == "Check SD":
        command,cs,ln=parseco("M20",cs,ln)
        send=True
        while send:
            print(command)
            tn.write((command+"\n").encode('ascii'))
            mess=tn.read_until(b"ok",timeout=10)
            print(mess)
            send=checkanswer(mess)
        text=mess.decode("utf-8")
        print(text[:-2])
        
        
tn.close()
print("Bye")

