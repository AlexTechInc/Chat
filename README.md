# Description
Project allow to create chat-room with unlimited count of users using pure python.

Libs used:
 - tkinter
 - socket
 - threading
 - sys
 - time

# Usage
## Screenshot
![Server and Client](/blob/usage.png)

## How to run
###	Running server:
```python server.py```

Server username is always set to 'server'

If window creation for server is no needed, command line argument ```--no--window``` can be specified.

### Running client:
```python client.py```

Client default username is always set to 'client'

Client username can be passed as command line argument, for ex. :
```python client.py AlexTechInc```

# Transfer details
### Restrictions
 - Max username length is set to 16
 - Max message length is set to 256
 - Max packet size is username + message + len bytes + magic open/close byets = 16 + 256 + 2 + 6 = 280

### Packet format

```
    0                  3             4                u         u+1           t                  t+3
    +------------------+-------------+------ /// -----+----------+---- /// ---+-------------------+
    | Magic bytes open | Usename len | Username value | Text len | Text value | Magic bytes close |
    +------------------+-------------+------ /// -----+----------+---- /// ---+-------------------+
```

Fields description:
 - Magic bytes open - 3 bytes - '$%\_' used to validate message start 
 - Username len - one byte that equals to length of Username value field length
 - Username value - field, that contains username
 - Text len - one byte that equals to length of Text value field length
 - Text value - field, that contains message
 - Magic bytes close - 3 bytes '\_%$' used to validate message end