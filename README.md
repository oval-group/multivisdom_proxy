# Multi-visdom proxy

This repo contains everything you need to use a server a proxy to access multiple visdom on different urls.

# Setup

We will call proxy server the server used as proxy, it needs to be accessible from the client browser.
We will call visdom server the server that will be running visdom, it does not need to be accessible from the client browser.

## Visdom server

You will need to have visdom installed on it and running on it.
In this tutorial, we will assume that you have two visdom servers running on two different servers at `visdomserv1:9087` and `visdomserv2:9087`.

## Proxy server

The proxy server needs to have [`nginx`](https://www.nginx.com/) installed on the server, this should be available from your package manager.
In this tutorial, we will assume that the procy server will be running at `proxyserver:1234`.


