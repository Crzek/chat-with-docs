"""
Bascic Configuration for Database
Contains the following attributes:
- nameDatabase: str
- user: str
- password: str
- host: str
- port: str 
    
"""


class DatabaseConfig:
    def __init__(self, nameDatabase, user, password, host, port) -> None:
        self. nameDatabase = nameDatabase
        self.user = user
        self.password = password
        self.host = host
        self.port = port
