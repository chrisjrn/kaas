HTTP Server reference
=====================


Authentication
--------------

While we recommend you use the server on a private network, it's still best if
you use authentication to ensure that a random eavesdropper cannot make requests
and take over your presentation.

To that end, you can sign your requests with HMAC-SHA256. 

To do this, you need to provide two HTTP headers with each request.

- X-Kaas-Digest: the hmac-sha256 hex digest of the request
- X-Kass-Nonce: a set of random characters to salt the hash.

A request is authenticated if and only if:
- The precise Digest has not been used to authenticate a request on this 
  server.
- The Digest is equivalent to the HMAC-SHA256 digest of:
    self.command + '\n' + self.path + '\n' + X-Kaas-Nonce
  (each encoded as ASCII)


