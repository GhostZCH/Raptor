
# Raptor
A HTTP proxy engine written in c++

## Requirement
+ use c++
+ run only on linux
+ run only with epoll
+ should only depend on std and common linux libs
+ with admin APIs(to send command and get running report)
+ 60%-80% performance of nginx
+ 10-20k lines of code (while nginx has abort 100k lines)
+ load configures from a db(or something can be updated from time to time) rather then fixed text files
+ a lots of system independent handlers(may be in lua) which can be tested with unit tests tools
