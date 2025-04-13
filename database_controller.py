import pymongo

class DBController:
    def __init__(
            self,
            host: str,
            port: int,
            db_name: str,
            collection_name: str,
    ):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client.get_database(db_name)
        self.collection = self.db.get_collection(collection_name)

    def add_user(self, user_id: str) -> dict:
        doc = {'user_id': user_id,
               'settings': {},
               'playlists': []
               }
        if not self.collection.find_one({"user_id": user_id}):
            self.collection.insert_one(doc)
            return {"status": "success"}

        return {"status": "error", "message": "user already exists."}


    def add_playlist(self, user_id: str, playlist_id: str, track_ids: list) -> dict:
        doc = self.collection.find_one({"user_id": user_id})
        
        if not doc:
            return {"status": "error", "message": "user doesn't exist."}

        if playlist_id in doc['playlists']:
            return {"status": "error", "message": "playlist already exists."}    

        playlist = {"id": playlist_id,
                    "track_ids": track_ids
                    }
        doc["playlists"].append(playlist)
        
        self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"playlists": doc["playlists"]}}
        )

        return {"status": "success"}
            

    def update_playlist(self, user_id: str, playlist_id: str, track_ids: list) _> dict: 
        doc = self.collection.find_one({"user_id": user_id})
        
        if not doc:
            return {"status": "error", "message": "user doesn't exist."}
        
        playlists = doc['playlists']
        playlist_index = next((i for i, pl in enumerate(playlists) if pl['id'] == playlist_id), None)

        if not playlist_index:
            return {"status": "error", "message": "playlist doesn't exist."}

        playlists[playlist_index][track_ids] = track_ids

        self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"playlists": playlists}
        )

        return {"status": "success"}


    def delete_playlist(self, user_id: str, playlist_id: str):
        pass

    def read_playlist(self, user_id: str, playlist_id: str):
        pass

    def get_playlists(self, user_id: str):
        pass

