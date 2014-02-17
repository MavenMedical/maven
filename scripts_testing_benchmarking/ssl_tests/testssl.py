import pycurl


class Response(object):
    """ utility class to collect the response """
    def __init__(self):
        self.chunks = []
    def callback(self, chunk):
        self.chunks.append(str(chunk))
    def content(self):
        return ''.join(self.chunks)

res = Response()

curl = pycurl.Curl()
curl.setopt(curl.URL, "https://app.mavenmedical.net/loop")
curl.setopt(curl.WRITEFUNCTION, res.callback)
curl.setopt(curl.CAINFO, "/etc/nginx/conf.d/server.crt")
curl.setopt(curl.SSLKEY, "/home/devel/maven/scripts_testing_benchmarking/ssl_tests/ssl_setup/client_key.pem")
curl.setopt(curl.SSLCERT, "/home/devel/maven/scripts_testing_benchmarking/ssl_tests/ssl_setup/client.pem")
curl.perform()

print(res.content())

