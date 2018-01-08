# Multi-visdom proxy

This repository contains everything you need to use a server a proxy to access multiple visdom on different urls.

To do so, the setup script allows you to configure an nginx webserver that is used as a proxy to access all your visdom instances.
The configuration is separate for each user of the server machine so that there are no interaction between different users.

# Setup

We will call proxy server the server used as proxy, it needs to be accessible from the client browser.
We will call visdom server the server that will be running visdom, it does not need to be accessible from the client browser.

### Visdom server

You will need to have visdom installed on it and running on it.
In this tutorial, we will assume that you have two visdom servers running on two different servers at `visdomserv1:9087` and `visdomserv2:9087`.

### Proxy server

The proxy server needs to have [`nginx`](https://www.nginx.com/) installed on the server, this should be available from your package manager.
To protect all pages with a password, we will use need to have `htpasswd` installed. It is available in the `apache2-utils` package on ubuntu for example.
In this tutorial, we will assume that the proxy server will be running at `proxyserver:1234`.

#### Sudoer config

You will need a user with write access to the nginx folder (sudoer in general, or normal user if you have a non-global nginx install).
* The `init` command in the provided script needs to be ran by a sudoer to initialize the nginx configuration.
* To allow unprivileged users to reload nginx after changing the configuration, do the following steps:
    * Run `sudo visudo`
    * Go to last line and add: `ALL ALL=NOPASSWD: /usr/sbin/service nginx reload` and a comment `# Allow all users to reload nginx`. All users (even not sudoers) can now run `sudo /usr/sbin/service nginx reload`.


# Usage

Run the `multivisdom_setup.py` script while being logged in with your username.

Available actions:
* List all links for the current user.
* Add a link for the current user. You need to provide:
    * The url to access visdom on the proxy server. If you set `foo`, you can access it at `proxyserver:1234/username/foo`
    * The hostname/ip of the server running visdom. In our example, that would be `visdomserv1` or `visdomserv2`.
    * The port used for visdom. In our example, that would be `9087`.
* Delete a link for the current user.
* Add a new login/password to connect to all boards of the current user. You will need to use these to access all the pages corresponding to your user.
