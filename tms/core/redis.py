import redis


r = redis.StrictRedis(host='localhost', port=6379, db=15)
r.set('blackdot', 'updated')
r.set('vehicle', 'updated')
