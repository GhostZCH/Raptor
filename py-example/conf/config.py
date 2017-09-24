CONF = {
    "servers": {
        "localhost": {
            "listen": ("127.0.0.1", 8000),
            "helpers": 'Index',
            "base-dir": 'html/',
            "https": False,
        },
        "www.baidu.com": {
            "listen": ("127.0.0.1", 8000),
            "upstream": ("www.baidu.com", 80),
            "helpers": 'Upstream',
            "https": False,
        },
        "www.sina.com": {
            "listen": ("127.0.0.1", 8000),
            "https": True,
            "upstream": ("www.sina.com", 80),
            "helpers": 'Upstream',
        }
    }
}
