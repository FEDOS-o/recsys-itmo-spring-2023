import random


from .recommender import Recommender
from .contextual import Contextual


class Better(Recommender):

    def __init__(self, tracks_redis, catalog, rec_base_track_pool, rec_base_track):
        self.tracks_redis = tracks_redis
        self.fallback = Contextual(tracks_redis, catalog)
        self.catalog = catalog
        self.rec_base_track_pool = rec_base_track_pool
        self.rec_base_track = rec_base_track

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if user not in self.rec_base_track_pool:
            self.rec_base_track_pool[user] = []
        else:
            self.rec_base_track_pool[user].append((prev_track, prev_track_time))
        if user not in self.rec_base_track:
            self.rec_base_track[user] = prev_track
        if len(self.rec_base_track_pool[user]) > 10:
            self.rec_base_track_pool[user].sort(key=lambda t: -t[1])
            self.rec_base_track[user] = self.rec_base_track_pool[user][0][0]
            self.rec_base_track_pool.pop(user)

        base_track = self.tracks_redis.get(self.rec_base_track[user])
        if base_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        track = self.catalog.from_bytes(base_track)
        recs = track.recommendations
        if not recs:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        shuffled = list(recs)
        random.shuffle(shuffled)
        return shuffled[0]
