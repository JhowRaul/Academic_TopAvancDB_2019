import redis
from gxredis import (
    RedisDao, RedisString, RedisList, RedisHash, RedisSet, RedisSortedSet,
)

class UsuarioDao(RedisDao):
    item_set = RedisSet(key="usuario")
    item_hash = RedisHash(key="usuario:{apelido}")