# -*- coding: UTF8 -*-
import optparse
import pymssql
import sys
 
def main():
 
    #Connect
    try:
        con = pymssql.connect(host=host, user=user, password=password, database=database)
        cur = con.cursor()
    except TypeError:
        print 
        print "Could not connect to SQL Server"
        print 
        sys.exit(1)
 
    # if db mirror -> exec q
    query="""SELECT d.name, m.mirroring_role_desc, m.mirroring_state_desc
             FROM sys.database_mirroring m
             JOIN sys.databases d ON m.database_id = d.database_id
             WHERE mirroring_state_desc IS NOT NULL AND name = """ + "'" + database + "'"
 
    cur.execute(query)
 
    results = cur.fetchall()
 
    for row in results:
        name  = row[0]
        role  = row[1]
        state = row[2]
 
    exit_val = 2
 
    if cur.rowcount > 0:
        if (role == "PRINCIPAL") and (state == "SYNCHRONIZED"):
            exit_val = 0
 
    if exit_val == 0:
        print "OK", "-", name, "-", role, "-", state
    else:
        print "Break mirror DB!"
 
    con.close()
 
 
if __name__ == "__main__":
 
    # Параметры cmd  
    parser = optparse.OptionParser()
 
    parser.add_option("-H", "--host",     dest="host",     metavar="HOST", help="IP or hostname with the mirrored database")
    parser.add_option("-d", "--database", dest="database", metavar="DB",   help="Name of the mirrored database")
    parser.add_option("-u", "--user",     dest="user",     metavar="USER", help="User to login")
    parser.add_option("-p", "--password", dest="password", metavar="PW",   help="Password of the user")
 
    if (len(sys.argv) < 2):
        args=["-h"]
        (options, args) = parser.parse_args(args)
 
    (options, args) = parser.parse_args()
 
    host     = options.host
    user     = options.user
    password = options.password
    database = options.database
 

    main()