import redis
from gxredis import (
    RedisDao, RedisString, RedisList, RedisHash, RedisSet, RedisSortedSet,
)

class UsuarioDao(RedisDao):
    item_set = RedisSet(key="usuario")
    item_hash = RedisHash(key="usuario:{apelido}")

class MensagemDao(RedisDao):
    item = RedisString(key="{id}")
    item_set = RedisSet(key="recebidas:{apelido}")
    item_set_env = RedisSet(key="enviadas:{apelido}")
    item_zset = RedisSortedSet(key="res:{id}")
