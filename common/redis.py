from aredis import StrictRedis
g_redis = StrictRedis(host='127.0.0.1', port=6379, db=0, max_idle_time=2, idle_check_interval=0.1)