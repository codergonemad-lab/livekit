from livekit import api
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class LiveKitService:
    def __init__(self):
        self.api_key = os.getenv("LIVEKIT_API_KEY")
        self.api_secret = os.getenv("LIVEKIT_API_SECRET")
        self.livekit_url = os.getenv("LIVEKIT_URL")
        
        if not all([self.api_key, self.api_secret, self.livekit_url]):
            raise ValueError("LiveKit configuration is incomplete. Please check your environment variables.")
    
    def create_access_token(
        self, 
        room_name: str, 
        participant_identity: str, 
        participant_name: Optional[str] = None,
        metadata: Optional[str] = None
    ) -> str:
        """
        Create a LiveKit access token for a participant to join a room.
        
        Args:
            room_name: Name of the room
            participant_identity: Unique identity for the participant
            participant_name: Display name for the participant
            metadata: Optional metadata for the participant
        
        Returns:
            JWT token string
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_identity)
        
        if participant_name:
            token.with_name(participant_name)
        
        if metadata:
            token.with_metadata(metadata)
        
        # Grant permissions
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True
        ))
        
        return token.to_jwt()
    
    def create_room_admin_token(self, participant_identity: str) -> str:
        """
        Create a token with room admin permissions.
        
        Args:
            participant_identity: Unique identity for the admin
        
        Returns:
            JWT token string with admin permissions
        """
        token = api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(participant_identity)
        
        # Grant admin permissions
        token.with_grants(api.VideoGrants(
            room_create=True,
            room_list=True,
            room_admin=True
        ))
        
        return token.to_jwt()
    
    async def get_room_info(self, room_name: str):
        """
        Get information about a room including participants.
        
        Args:
            room_name: Name of the room
        
        Returns:
            Room information and participants
        """
        try:
            room_client = api.RoomService(
                http_uri=self.livekit_url.replace('wss://', 'https://').replace('ws://', 'http://'),
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            room_info = await room_client.get_room(api.GetRoomRequest(name=room_name))
            participants = await room_client.list_participants(
                api.ListParticipantsRequest(room=room_name)
            )
            
            return {
                "room": room_info,
                "participants": participants.participants
            }
        except Exception as e:
            print(f"Error getting room info: {e}")
            return None
    
    async def create_room(self, room_name: str, max_participants: int = 50):
        """
        Create a new room on LiveKit server.
        
        Args:
            room_name: Name of the room to create
            max_participants: Maximum number of participants allowed
        
        Returns:
            Created room information
        """
        try:
            room_client = api.RoomService(
                http_uri=self.livekit_url.replace('wss://', 'https://').replace('ws://', 'http://'),
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            room = await room_client.create_room(api.CreateRoomRequest(
                name=room_name,
                max_participants=max_participants
            ))
            
            return room
        except Exception as e:
            print(f"Error creating room: {e}")
            return None
    
    async def delete_room(self, room_name: str):
        """
        Delete a room from LiveKit server.
        
        Args:
            room_name: Name of the room to delete
        
        Returns:
            Success status
        """
        try:
            room_client = api.RoomService(
                http_uri=self.livekit_url.replace('wss://', 'https://').replace('ws://', 'http://'),
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            await room_client.delete_room(api.DeleteRoomRequest(room=room_name))
            return True
        except Exception as e:
            print(f"Error deleting room: {e}")
            return False

# Global instance
livekit_service = LiveKitService()
