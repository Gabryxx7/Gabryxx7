---
title: How to set up your own cloud-based code editor
excerpt_separator: <!--more-->
image: 
  path: /assets/gabryxx7/img/code-server-img.png
  class: "wide-img"
---

I like my website to be lightweight and static, which is one of the reasons I stuck with Jekyll!
One of the pros is being able to write articles in Markdown which I find less distracting and cluttered thn Google Docs, Word or LaTeX.

When self-hosting your website, adding new posts or even making small changes to your website can be rather time consuming. This is especially true when working from different machines.

The way I "fixed" this issue myself is by getting a dedicated server through a cheap hosting service and my own domain.


<!--more-->

- Table of Contents
{:toc .large-only}

## Getting your dedicated server up and running
### Self hosting
After some research I ended up going with [Vultr](https://www.vultr.com/products/cloud-compute/#pricing) as a hosting provider.
Being mine a static, lightweight website, I do not really need a powerful server with lots of space.


| Geekbench Score    	| Storage   	| CPU   	| Memory 	| Bandwidth   	| Monthly Price * 	| Hourly Price *  	|
|--------------------	|-----------	|-------	|--------	|-------------	|-----------------	|-----------------	|
| N/A                	| 10 GB SSD 	| 1 CPU 	| 0.5 GB 	| 0.50 TBIPv6 	| $2.50           	| $0.00           	|
| N/A                	| 10 GB SSD 	| 1 CPU 	| 0.5 GB 	| 0.50 TB     	| $3.50           	| $0.01           	|
| 2413               	| 25 GB SSD 	| 1 CPU 	| 1 GB   	| 1 TB        	| $5.00           	| $0.01           	|
| ...               	| ...   	| ...   	| ...     	| ...        	| ...           	| ...           	|

I opted for the last option with 25gb SSD and 1GB of RAM which is fairly cheap at AU$ 5 per month.

### Domain
In order to make your website secure and trusted you need to set up SSL and HTTPS, and this can only be done with a domain and not with pure IP addresses.

I chose Google Domains in this case as it is fairly cheap and managing DNS records is easy.

Once you set up your domain you can also set up your subdomain for whatever services you might need. This is what my DNS records table look like:

|       Host name      	|  Type 	| TTL    	| Data              	|
|:--------------------:	|:-----:	|--------	|-------------------	|
| gmarini.com          	| A     	| 1 hour 	| 45.76.124.120     	|
| *.code.gmarini.com   	| A     	| 1 hour 	| 45.76.124.120     	|
| code.gmarini.com     	| A     	| 1 hour 	| 45.76.124.120     	|
| www.gmarini.com      	| CNAME 	| 1 hour 	| @.                	|
| www.code.gmarini.com 	| A     	| 1 hour 	| 45.76.124.120     	|

DNSSEC is disabled and I am using Google Domains servers.

## Setting up your server
Now it's time to set up your server and environment. The first thing you want to do is to set up SSH.

### Setting up SSH access


**HEADS UP**: **NEVER** share your SSH public and/or private keys on the internet! The keys down here have been generated for the purpose of this tutorial and promptly discarded!
{:.message}

This will differ depending on your provider. On Vultr you can go to [https://my.vultr.com/settings/#settingssshkeys](https://my.vultr.com/settings/#settingssshkeys), click on the "+" button and then "Add SSH Key".
Give it a name to remind you what is the key for, something like `vultr-server-blog`.

Now you need to create your SSH key, I found this guide fairly simple and straight to the point [Create an SSH Key with OpenSSH](https://www.vultr.com/docs/how-do-i-generate-ssh-keys/).

In short:
- Open `PowerShell`
- Type in `ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
- Confirm the file location
- Enter a passphrase for your key
- Enter the same passphrase again

```powershell
PS C:\Users\Giaga> ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
Generating public/private rsa key pair.
Enter file in which to save the key (C:\Users\Giaga/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in C:\Users\Giaga/.ssh/id_rsa
Your public key has been saved in C:\Users\Giaga/.ssh/id_rsa.pub
The key fingerprint is:
SHA256:gn18jblysbS0XESUadoWM/2pEFJzSYSCEq1lvstPWJQ your_email@example.com
The key's randomart image is:
+---[RSA 4096]----+
|     .o . .+*B.  |
|     . = o.+X..  |
|      *  Eo+o+ ..|
|     + o. .*o  ..|
|    . o S.B.+ .  |
|       +o= B .   |
|      ..o.B      |
|       o.o       |
|        ..       |
+----[SHA256]-----+
```

Now it's usually a good idea to make a backup of the private key as they cannot be recovered if lost!
Copy the file somewhere safe, possibly NOT on the cloud!

You can now get your public key from the PowerShell by typing:

```powershell
(base) PS C:\Users\Giaga> type $env:USERPROFILE\.ssh\id_rsa.pub
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCsQ/tUy8BcGpoWAMCjHHrucZKJLCuOJpFGFxTxhPDy5xet6khpxpfci/cLgyIUm4DEZSGQpCMszl3MXGJ7QuFDoSBue+MebKH9ZC1sK27+DFaFJXvDdD3OhFyTgqwrEIGZ7FKr7GNdMpER+fItUsAKx3ylwBLU4/dh13jsKE968RtApRkluch8M/L3MfzFBaDWJUPO0E+boQv8nOhpZqPU+WL2mzM4j/QA5BGssCGxWOm3zV4m4FTJGlJetN++5P67qTkMyu3U/UW4Y1ItStwnU8Wz/QvRGppOChJgYoAtWfR6MLIXd2iJ1G6IVwtLokVuFnJZFRnOo4BrdabPmqIPD+t3DtBfrsRhXF75IshMrR14r3EYFZKOsX3iJGEWfe3hBmvkoAOmtrV0n70cERcRQdnb8kdgjP4jT60gkt9GMz9UMmAMsMGfhRl3JSMv1bbLoe849xS5T9j/SCMSxQeb6XI6V3mBpFkmIaINs6VwV4/AJGZ9JA/tA175nDrCLsyyo5cGtShNNCYnHSGcFkCc4AWipTTPLdbak3jHetPyK6xn1ExRHKnJd/n65AUFdHNkNj2qj1fSFaWGxOJ706Am6nDWppUVSgWys1J+reXvAt7CFO8lPNhkcWxfJsAfcPpHkvF6fBnPScL8HXa9DwMzbfDNkN7aMkF35sY1z/c34w== your_email@example.com
```

Copy everything from `ssh-rsa` to your email included and paste it onto the textbox from the previous point.


That's it! You can now test your SSH on your PowerShell with

```powershell
(base) PS C:\Users\Giaga> ssh -i C:\Users\Giaga/.ssh/id_rsa username@123.45.678.910
username@123.45.678.910's password:
[...]
username@vultr-server:~$
```

## Setting up NGINX and code-server
nginx conf
```
server {
    listen 80;
    listen [::]:80;
    server_name code.gmarini.com www.code.gmarini.com;

        location / {
                proxy_pass http://127.0.0.1:9443/;
                proxy_set_header Host $host;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection upgrade;
                proxy_set_header Accept-Encoding gzip;
        }
}
```

enable nginx config
```bash
sudo ln -s ../sites-available/code-server /etc/nginx/sites-enabled/code-server.conf
```

Let's encrypt
```bash
sudo certbot --non-interactive --redirect --agree-tos --nginx -d code.gmarini.com -m giaga7@gmail.com
```

Start code-server
```bash
sudo systemctl restart code-server@$USER

```

<!--more-->
- Table of Contents
{:toc .large-only}
