CONF = {
    "servers": {
        "localhost": {
            "listen": ("127.0.0.1", 8000),
            "helpers": 'IndexHelper',
            "base-dir": 'html/',
            "https": False,
            "protocol": "http"
        },
        # "www.baidu.com": {
        #     "listen": ("127.0.0.1", 8000),
        #     "upstream": ("www.baidu.com", 80),
        #     "helpers": 'IndexHelper',
        #     "https": False,
        #     "protocol": "http"
        # },
        # "www.sina.com": {
        #     "listen": ("127.0.0.1", 8000),
        #     "https": True,
        #     "upstream": ("www.sina.com", 80),
        #     "helpers": 'IndexHelper',
        #     "protocol": "http"
        # }
    }
}
