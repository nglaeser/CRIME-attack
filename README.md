# CRIME Attack Demo  

Noemi Glaeser  
CMSC 818O: Security (Fall 2019)  
Presented: 26 Sep 2019  

## Dependencies

* nginx
* a vulnerable browser: Chrome v xx on a virtual machine running Ubuntu 14.04.

## Set Up

### 1. Setting up the sites

Serve the contents of the faceb00k and cookies sites as follows.

1. Add the following localhost aliases to `/etc/hosts` (you may need to `sudo` edit):

```
127.0.0.1   localhost
127.0.0.1   faceb00k.com
127.0.0.1   cookies.com
```

2. Generate a self-signed certificate for the HTTPS website faceb00k.com (this is self-signed for demo purposes, in a real scenario this would be a legitimate HTTPS site):

```
openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout faceb00k1.key -out faceb00k1.crt
```

2. Add the servers to your `nginx.conf` (mine was located in `/usr/local/etc/nginx/nginx.conf`), or wherever else you put your servers:


```
http {
# ...

    # faceb00k server - HTTPS
    server {
        listen       443 ssl;
        server_name  faceb00k.com www.faceb00k.com;
        ssl_certificate path/to/faceb00k1.crt;
        ssl_certificate_key path/to/faceb00k1.key;
        ssl_protocols SSLv2 SSLv3 TLSv1 TLSv1.1 TLSv1.2; # up to and including TLSv1.2 is vulnerable to CRIME 

        gzip         on; # enable server-side TLS/SSL compression - this is the attack vector, so it's crucial

        location / { 
            root   path/to/faceb00k; # folder containing files to serve
            index  index.html index.htm;
        } 

    # cookies server
    server {
        listen       80; # this port can be whatever you want, 80 is default for HTTP
        server_name  cookies.com www.cookies.com;

        location / {
            root   path/to/cookies; # folder containing files to serve
            index  index.html index.htm;
        }
    }
# ...
}
```

3. Start/restart nginx (you have to do this anytime you change your `nginx.conf` file):

```
# start
nginx

# restart
sudo nginx -s reload
```

4. Serve the sites on localhost, e.g. with

```
python -m SimpleHTTPServer 80
```

Actually, it seems like you don't need to do [4] at all.

### 2. Access through a vulnerable browser

Now we just need to get the user (of a vulnerable browser, i.e. one that has SSL compression enabled) to be logged into faceb00k.com *and* access our evil site cookies.com. Then we can steal their faceb00k cookies!

1. [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads) or VMWare, depending on your host system. *(Note: On MacOS 10.14, I had to jump through some hoops to get VirtualBox installed; see [this thread](https://forums.virtualbox.org/viewtopic.php?f=8&t=84092))*

2. Create an Ubuntu VM and load an Ubuntu 14.04 ISO into it, as described in [this article](https://www.cs.unm.edu/~bradykey/ubuntuVMInstallGuide.html), for example. Other versions of Ubuntu may work too, but this is the one I used. Files are available in the `binaries` folder. 
* Be sure to set the Network Adapter to NAT (Settings > Network > Attached to: NAT).
* Set enough memory, provided your host machine can afford it, so the VM won't lag painfully. I set it at 4096 MB. 
* Once the machine is running, repeat step 1.1 with the VM's `/etc/hosts`.

3. Install the vulnerable browser on your VM. It seems only Chrome was every truly vulnerable to CRIME, so in this demo I used [Chrome v xx](https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F100002%2Fchrome-linux.zip?generation=1&alt=media).
* Download the ZIP file
* Extract its contents
* run `./chrome-wrapper` in the terminal

[ will add the following to a binaries folder: Ubuntu ISO, Chrome ZIP]

### 3. Simulate the attack and observe traffic

### 4. Proof of concept of incremental cookie discovery

I made some slight edits to this script to improve demo-ability, namely adding colors and pauses. Run with  
```
python crime.py
```

...  


Wireshark display filter: `tcp.dstport == 443 and ssl`
Another useful filter for unencrypted (HTTP) faceb00k server debugging: `http contains GET` (won't be compressed though)
