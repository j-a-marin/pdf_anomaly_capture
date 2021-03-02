import subprocess as sp
import os, glob, re

def main():

    logfilelast = sorted([f for f in glob.glob('*') if re.search(r"\d{2}.log", f) ], 
        key=lambda x: re.search(r"\d{2}:\d{2}",x)[0], reverse=True)

    print (logfilelast)

    print (f'READING MOST RECENT LOG FILE {logfilelast[0]}')

    args = ["awk", '{print $4}', os.path.abspath(logfilelast[0])]

    p = sp.Popen(args, stdin = sp.PIPE, stdout = sp.PIPE, stderr = sp.PIPE )

    print([e.decode().strip() for e in p.stdout.readlines()])

if __name__ == '__main__':

    main()