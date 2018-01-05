# Multi-visdom proxy

This repository contains everything you need to use a server a proxy to access multiple visdom on different urls.

# Setup

We will call proxy server the server used as proxy, it needs to be accessible from the client browser.
We will call visdom server the server that will be running visdom, it does not need to be accessible from the client browser.

## Visdom server

You will need to have visdom installed on it and running on it.
In this tutorial, we will assume that you have two visdom servers running on two different servers at `visdomserv1:9087` and `visdomserv2:9087`.

## Proxy server

The proxy server needs to have [`nginx`](https://www.nginx.com/) installed on the server, this should be available from your package manager.
To protect all pages with a password, we will use need to have `htpasswd` installed. It is available in the `apache2-utils` package on ubuntu for example.
In this tutorial, we will assume that the proxy server will be running at `proxyserver:1234`.

### Sudoer config

You will need a user with write access to the nginx folder (sudoer in general, or normal user if you have a non-global nginx install).
* The `init` command in the provided script needs to be ran by a sudoer to initialize the nginx configuration.
* To allow unprivileged users to reload nginx after changing the configuration, do the following steps:
    * Run `sudo visudo`
    * Go to last line and add: `ALL ALL=NOPASSWD: /usr/sbin/service nginx reload` and a comment `# Allow all users to reload nginx`. All users (even not sudoers) can now run `sudo /usr/sbin/service nginx reload`.




