# -*- coding: CP1251 -*-

import os, sys, socket, struct, select, time, pyodbc, threading
ICMP_ECHO_REQUEST = 8 
DRIVER = u"{SQL Server}"
DATABASE = u""
LOGIN = u""
PASSWORD = u""
status = 0
count_serv =0
sumserver = 0

LOCK = threading.RLock()
def checksum(source_string):
    sum = 0
    countTo = (len(source_string) / 2) * 2
    count = 0
    while count < countTo:
        thisVal = ord(source_string[count + 1]) * 256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2
    if countTo < len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer


def receive_one_ping(my_socket, ID, timeout):
    timeLeft = timeout
    while True:
        startedSelect = time.clock()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (time.clock() - startedSelect)
        if whatReady[0] == []: # Timeout
            return

        timeReceived = time.clock()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return


def send_one_ping(my_socket, dest_addr, ID):
    dest_addr = socket.gethostbyname(dest_addr)
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.clock()) + data
    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1)) # Don't know about the 1


def do_one(dest_addr, timeout):
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error, (errno, msg):
        if errno == 1:
            msg = msg + (
                " - Note that ICMP messages can only be sent from processes"
                " running as root."
            )
            raise socket.error(msg)
        raise

    my_ID = os.getpid() & 0xFFFF

    send_one_ping(my_socket, dest_addr, my_ID)
    delay = receive_one_ping(my_socket, my_ID, timeout)

    my_socket.close()
    return delay

def checkstatus(SERVER):
    global sumserver
    try:
        cnxn = pyodbc.connect("DRIVER=%s;SERVER=%s;DATABASE=%s;UID=%s;PWD=%s"
                              % (DRIVER, SERVER, DATABASE, LOGIN, PASSWORD))
    except:
        cnxn = None
        print "Cann't connect to server MSSQL on : ", SERVER 
    if cnxn:
        filename = r"D:\\Users_Crystall\%s.txt" %(SERVER)
        fs = open(filename,"w")
        cursor = cnxn.cursor()
        query = """SELECT Users.SubjectName, Modes.ModeName, UserPermissions.ActionDisabled, UserPermissions.InsertDisabled, UserPermissions.UpdateDisabled, UserPermissions.DeleteDisabled, UserPermissions.LoadDisabled, UserPermissions.UnloadDisabled FROM Users INNER JOIN UserPermissions ON Users.Id = UserPermissions.SubjectId INNER JOIN Modes ON UserPermissions.ModeId = Modes.Id Order by SubjectName"""
        cursor.execute(query.encode('CP1251'))
        rows = cursor.fetchall() 
        retr = server_last = ()
        if rows:
            rowq = "Список пользователей на сервере с ip адресом:  "+SERVER+" \n"
            fs.write(str(rowq))
            for row in rows:
                rowq = row.SubjectName+", "+row.ModeName+", Права :  Выполнение = "+str(row.ActionDisabled)+"  Добавление = "+str(row.InsertDisabled)+"  Изменение = "+str(row.UpdateDisabled)+"  Удаление = "+str(row.DeleteDisabled)+"  Загрузка = "+str(row.LoadDisabled)+"  Выгрузка = "+str(row.UnloadDisabled)
                fs.write(str(rowq+"\n"))

        
        fs.close()
        return status
    

def verbose_ping(dest_addr, timeout=2, count=1):
    
    for i in xrange(count):
        
        try:
            delay = do_one(dest_addr, timeout)
        except socket.gaierror, e:
        
            break

        if delay == None:
            continue
        
        else:
            delay = delay * 1000
            status = checkstatus(SERVER)

verbose_ping(SERVER)

