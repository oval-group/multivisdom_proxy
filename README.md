# Multi-visdom proxy

Objective: set up and use a proxy server that allows access to multiple `visdom` visualization instances through a single gate server. This is done through a `nginx` web server that redirects paths to running `visdom` instances. The `nginx` configuration is kept separate for each user of the server machine to avoid any conflict.

The `multivisdom_setup.py` script provides an interactive interface to add credentials as well to list, add or remove paths to `visdom` instances.

# Setting up the proxy

We will call proxy server the server used as proxy, it needs to be accessible from the client browser.
We will call visdom server the server that will be running `visdom`, it does not need to be accessible from the client browser.

### Requirements

The proxy server needs to have [`nginx`](https://www.nginx.com/) installed (it should be available from your package manager).
To protect all pages with a password, we will need to have `htpasswd` installed. It is available in the `apache2-utils` package on Ubuntu for example.
In this tutorial, we assume that the address of the proxy server is `proxyserver:1234`.

#### Configuration

You will need a user with write access to the nginx folder (sudoer in general, or normal user if you have a non-global nginx install).
* To initialize the nginx configuration: run `sudo python multivisdom_setup.py` (needs sudoer).
* To allow unprivileged users to reload `nginx` after they make changes, do the following steps:
    * Run `sudo visudo`
    * Go to last line and add: `ALL ALL=NOPASSWD: /usr/sbin/service nginx reload` and a comment `# Allow all users to reload nginx`. All users (even not sudoers) can now run `sudo /usr/sbin/service nginx reload`.

# Usage of the proxy server

### Requirements

You need to have [`visdom`](https://github.com/facebookresearch/visdom) installed on the visdom server(s).
In this tutorial, we assume that you have two visdom servers running on two different servers at `visdomserv1:9087` and `visdomserv2:9087`.

### Using the proxy

Run the `multivisdom_setup.py` script when logged in with your user name on the proxy machine.

Available actions:
* List all links for the current user.
* Add a link for the current user. You need to provide:
    * The path to access visdom on the proxy server. If you enter `foo`, you can access it at `proxyserver:1234/username/foo`
    * The hostname/ip of the server running visdom. In our example, that would be `visdomserv1` or `visdomserv2`.
    * The port used for visdom. In our example, that would be `9087`.
* Delete a link for the current user.
* Add a new login/password to connect to all links of the current user. You will need to use these to access all the pages corresponding to your user.
