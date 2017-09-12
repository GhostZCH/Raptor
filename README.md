
# Raptor
A HTTP proxy engine written in c++

## Requirement
+ run only on linux
+ run only with epoll
+ should only depand on std and common linux libs
+ with admin apis(to send commond and get runing report)
+ 60%-80% performance of nginx
+ use little easy-understand code
+ use c++ to reduce code
+ do unit tests on windows and linux
+ load domain configures from a db(or something can be updated from time to time) rather then fixed text files
+ a tiny core and lots of system independent handlers(may be in lua) which can be tested by unit tests
