# CRIME Attack Demo  

Noemi Glaeser  
CMSC 818O: Security (Fall 2019)  
Presented: 26 Sep 2019  

## Dependencies

* nginx with SSL compression: for example nginx 1.0.6 [or 1.1.6?]
* a vulnerable browser: Chrome v 15.0.0875.0 on a virtual machine running Ubuntu 14.04.

## Set Up

### 1. Ubuntu Virtual Machine

1. [Install VirtualBox](https://www.virtualbox.org/wiki/Downloads) or VMWare, depending on your host system. *(Note: On MacOS 10.14, I had to jump through some hoops to get VirtualBox installed; see [this thread](https://forums.virtualbox.org/viewtopic.php?f=8&t=84092))*

2. Create an Ubuntu VM and load an Ubuntu 14.04 ISO into it, as described in [this article](https://www.cs.unm.edu/~bradykey/ubuntuVMInstallGuide.html), for example. Other versions of Ubuntu may work too, but this is the one I used. Files are available in the `binaries` folder. 
* Be sure to set the Network Adapter to NAT (Settings > Network > Attached to: NAT).
* Set enough memory, provided your host machine can afford it, so the VM won't lag painfully. I set it at 4096 MB. 
* Once the machine is running, repeat step 1.1 with the VM's `/etc/hosts`.

3. Install the vulnerable browser on your VM. It seems only Chrome (/Chromium) was every truly vulnerable to CRIME, so in this demo I used [Chrome (Chromium) v 15.0.875.0](https://www.googleapis.com/download/storage/v1/b/chromium-browser-snapshots/o/Linux_x64%2F100002%2Fchrome-linux.zip?generation=1&alt=media).
* Download the ZIP file
* Extract its contents
* run `./chrome-wrapper` in the terminal

4. Install OpenSSL with zlib support as described [here](https://securitygrind.com/building-openssl-with-zlib-support/). Summary below:
```
# uninstall any existing OpenSSL
apt-get remove openssl
apt-get purge openssl

cd Downloads
wget https://www.openssl.org/source/openssl-1.0.2t.tar.gz
# wget https://www.openssl.org/source/old/1.0.0/openssl-1.0.0.tar.gz # try an even older version
# wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.8zh.tar.gz # try this with nginx 1.0.6, has DZLIB flag - doesn't work??
# same with nginx 1.1.6 instead
# this also doesn't have the DZLIB flag??

# wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.8.tar.gz # won't compile properly
# wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.8x.tar.gz # won't compile properly
# wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.7.tar.gz # doesn't have DZLIB flag in vrsion -f
# wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.8n.tar.gz # also won't compile properly
# wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.8za.tar.gz # also won't compile properly
wget https://www.openssl.org/source/old/0.9.x/openssl-0.9.8zb.tar.gz
apt-get install zlib1g-dev
tar xvf openssl-1.0.2t.tar.gz
cd openssl-1.0.2t
./config zlib # no-md5 # for openssl 0.9.8
make
sudo make install

# I had to do this additional step:
# mv ~/Downloads/openssl-1.0.2t/apps/openssl /usr/bin/openssl
# mv ~/Downloads/openssl-1.0.2t/ssl /usr/lib/ssl

# double check that openssl has zlib capabilities
~/Downloads/openssl-1.0.2t/apps/openssl version -f | grep DZLIB

~/Downloads/openssl-1.0.2t/apps/openssl version -a
```

Output from last command:
```
OpenSSL 0.9.8zb 6 Aug 2014
built on: Fri Sep 27 01:59:42 EDT 2019
platform: linux-x86_64
options:  bn(64,64) md2(int) rc4(1x,char) des(idx,cisc,16,int) idea(int) blowfish(idx) 
compiler: gcc -DZLIB -DOPENSSL_THREADS -D_REENTRANT -DDSO_DLFCN -DHAVE_DLFCN_H -Wa,--noexecstack -m64 -DL_ENDIAN -DTERMIO -O3 -Wall -DMD32_REG_T=int -DOPENSSL_BN_ASM_MONT -DSHA1_ASM -DSHA256_ASM -DSHA512_ASM -DMD5_ASM -DAES_ASM
OPENSSLDIR: "/usr/local/ssl"
```

5. Install an nginx version that supports SSL compression, such as [nginx 1.0.6](http://nginx.org/download/). 

[ Now trying 1.1.6 and looking for SSL\_OP\_NO\_COMPRESSION in source ]

* See [this article](https://www.thegeekstuff.com/2011/07/install-nginx-from-source/) about installing nginx from source. Here are the commands and options I used (use `sudo` as necessary):  
```
#./configure --with-http_ssl_module --without-http_rewrite_module --with-openssl=~/Downloads/openssl-0.9.8zh # could it be that passing the openssl flag makes it recompile ssl with the wrong flags? yes, apparently
#ln -s /home/noemi/Downloads/openssl-0.9.8zb/apps/openssl /usr/bin/openssl
#./configure --with-http_ssl_module --without-http_rewrite_module --with-cc-opt="-DZLIB" --with-openssl=~/Downloads/openssl-0.9.8zb # set --with-cc-opt to pass DZLIB option to the openssl compiler so it doesn't get removed # this doesn't work either
#sudo ./configure --with-http_ssl_module --without-http_rewrite_module --with-ld-opt="-L/usr/local/ssl/lib" # try to set link to source and libraries instead of to source (which would cause a fresh re-compile) # also doesn't work, still complains it can't find openssl
#ln -s /usr/local/ssl/lib /usr/local/lib/openssl
#sudo ./configure --with-http_ssl_module --without-http_rewrite_module
sudo ./configure --with-http_ssl_module --without-http_rewrite_module --with-ld-opt="-L /home/noemi/Downloads/openssl-0.9.8zb -lssl -lcrypto -lz -ldl -static-libgcc" # this compiles nginx properly! and openssl version -a still has the DZLIB flag! But the Server Hello packet still has no compression methods
sudo make
sudo make install

# I had to make an alias for the binary
alias nginx=/usr/local/nginx/sbin/nginx

# Make a backup of the original config file; we will modify it in the next section
cp /usr/local/nginx/conf/nginx.conf /usr/local/nginx/conf/nginx.conf-bak
```

[ will add the following to a binaries folder: Ubuntu ISO, Chrome ZIP, nginx-1.\*.6.tar.gz, openssl-0.9.\*.tar.gz ]

[ Right now, I see two avenues:  
- run the nginx `./configure` with `--with-openssl` and find a way to pass the `-DZLIB` flag into the openssl configuration/make  
- find a way to specify the path to the openssl library to the nginx `./configure` <- check :)
- try with nginx 1.1.6 instead, or newer ]

### 2. Setting up the sites

On the VM, serve the contents of the faceb00k and cookies sites as follows.

1. Add the following localhost aliases to `/etc/hosts` (you may need to `sudo` edit):

```
127.0.0.1   localhost
127.0.0.1   faceb00k.com
127.0.0.1   www.faceb00k.com
127.0.0.1   cookies.com
127.0.0.1   www.cookies.com
```

2. Generate a self-signed certificate for the HTTPS website faceb00k.com (this is self-signed for demo purposes, in a real scenario this would be a legitimate HTTPS site):

```
openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout faceb00k1.key -out faceb00k1.crt
```

and answer the prompts.

2. Add the servers to your `nginx.conf` (mine was located in `/usr/local/nginx/conf/nginx.conf`), or wherever else you put your servers. A sample `nginx.conf` can be found in this repo.


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

### 3. Simulate the attack and observe traffic

[ Troubleshooting here now. Status: can't capture packets from VM, and don't want to install Wireshark on the VM. ]

1. [Download Wireshark](https://www.wireshark.org/download.html) and open it.
* On the first page that pops up, pick "Loopback: lo0" as your interface. Now you're capturing!
* For readability, apply `ssl` as the display filter by entering it into the text box at the top.

2. In Chromium in the VM, access https://www.faceb00k.com.
* If the page doesn't load, make sure you've run `nginx` on your host.
* In Wireshark, you should see a "Client Hello" packet. In the TLS header, you should see DEFLATE listed as a compression method:  
[!Compression Methods](compressionheader.png)

3. Now navigate to www.cookies.com.

### 4. Proof of concept of incremental cookie discovery

I made some slight edits to this script to improve demo-ability, namely adding colors and pauses. Run with  
```
python crime.py
```

...  


Wireshark display filter: `tcp.dstport == 443 and ssl`  
Another useful filter for unencrypted (HTTP) faceb00k server debugging: `http contains GET` (won't be compressed though)

## New try

### Apache

See [this article](https://geekflare.com/apache-setup-ssl-certificate/). Configure Apache with  

```
./configure --enable-ssl –-enable-so --with-ssl=/path/to/openssl
```
