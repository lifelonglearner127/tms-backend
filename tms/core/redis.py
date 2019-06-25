import redis


r = redis.StrictRedis(host='localhost', port=6379, db=15)
r.set('station', 'read')
r.set('vehicle', 'read')
