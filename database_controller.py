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
               'playlists': []
               }
        if not self.collection.find_one({"user_id": user_id}):
            self.collection.insert_one(doc)
            return {"status": "success"}

        return {"status": "error", "message": "user already exists."}


    def get_user(self, user_id: str) -> dict:
        doc = self.collection.find_one({"user_id": user_id})
        
        if not doc:
            return {"status": "error", "message": "user doesn't exist."}

        return doc

    def get_playlist_index(self, playlist_id: str, playlists: list) -> dict:
        playlist_index = next((i for i, pl in enumerate(playlists) if pl['id'] == playlist_id), None)
        
        if playlist_index is None:
            return {"status": "error", "message": "playlist doesn't exist."}

        return playlist_index


    def add_playlist(self, user_id: str, playlist_id: str, track_ids: list, auto_check: bool=False) -> dict:
        # geting user
        doc = self.get_user(user_id)
        if type(doc) == dict and doc.get('status') and doc.get('status') == 'error':
            return doc
        
        # checking if playlist exists
        if playlist_id in [pl['id'] for pl in doc['playlists']]:
            return {"status": "error", "message": "playlist already exists."}    

        # appending playlist
        playlist = {"id": playlist_id,
                    "auto_check": auto_check,
                    "track_ids": track_ids
                    }
        doc["playlists"].append(playlist)
        
        # adding user to the collection
        self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"playlists": doc["playlists"]}}
        )

        return {"status": "success"}
            

    def update_playlist_tracks(self, user_id: str, playlist_id: str, track_ids: list) -> dict: 
        # getting user
        doc = self.get_user(user_id)
        if type(doc) == dict and doc.get('status') and doc.get('status') == 'error':
            return doc

        # getting playlist
        playlist_index = self.get_playlist_index(playlist_id, doc['playlists'])
        if type(playlist_index) == dict and playlist_index.get('status') and playlist_index.get('status') == 'error':
            return playlist_index
        
        # updating track ids
        doc['playlists'][playlist_index]['track_ids'] = track_ids

        # updating playlists
        self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"playlists": doc['playlists']}}
        )

        return {"status": "success"}

    
    def update_playlist_auto_check(self, user_id: str, playlist_id: str, auto_check: bool) -> dict:
        # getting user
        doc = self.get_user(user_id)
        if type(doc) == dict and doc.get('status') and doc.get('status') == 'error':
            return doc
        
        # getting playlist
        playlist_index = self.get_playlist_index(playlist_id, doc['playlists'])
        if type(playlist_index) == dict and playlist_index.get('status') and playlist_index.get('status') == 'error':
            return playlist_index

        # updating the auto check
        doc['playlists'][playlist_index]['auto_check'] = auto_check

        self.collection.update_one(
                {"user_id": user_id},
                {"$set": {"playlists": doc['playlists']}}
        )

        return {"status": "success"}


    def delete_playlist(self, user_id: str, playlist_id: str) -> dict:
        # getting user
        doc = self.get_user(user_id)
        if type(doc) == dict and doc.get('status') and doc.get('status') == 'error':
            return doc
        
        # getting playlists
        playlist_index = self.get_playlist_index(playlist_id, doc['playlists'])
        if type(playlist_index) == dict and playlist_index.get('status') and playlist_index.get('status') == 'error':
            return playlist_index

        
        # deleting playlist and setting and updating user
        doc['playlists'].pop(playlist_index)

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"playlists": doc['playlists']}}
        )

        return {"status": "success"}


    def get_playlist_track_ids(self, user_id: str, playlist_id: str) -> dict | list:
        # getting user
        doc = self.get_user(user_id)
        if type(doc) == dict and doc.get('status') and doc.get('status') == 'error':
            return doc
        
        # getting playlist index
        playlist_index = self.get_playlist_index(playlist_id, doc['playlists'])
        if type(playlist_index) == dict and playlist_index.get('status') and playlist_index.get('status') == 'error':
            return playlist_index
        
        return doc['playlists'][playlist_index]['track_ids']       


    def get_playlist_ids(self, user_id: str) -> dict | list: 
        # getting user
        doc = self.get_user(user_id)
        if type(doc) == dict and doc.get('status') and doc.get('status') == 'error':
            return doc

        return [pl['id'] for pl in doc['playlists']]



