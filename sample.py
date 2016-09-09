# encode: utf-8

from amarak.connections.rest import RestConnection

REST_URL = 'http://127.0.0.1:8000/'


def main():
    conn = RestConnection(REST_URL)
    scheme = conn.schemes.get('http://free-node.ru/schemes/dg5#')
    print scheme.uri

if __name__ == '__main__':
    main()
