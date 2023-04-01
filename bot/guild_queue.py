from music_queue import MusicQueue


class GuildQueueManager:
    music_queues = {}

    @staticmethod
    def get_guild_queue(guild_id):
        if guild_id not in GuildQueueManager.music_queues:
            GuildQueueManager.music_queues[guild_id] = MusicQueue()
        return GuildQueueManager.music_queues[guild_id]
