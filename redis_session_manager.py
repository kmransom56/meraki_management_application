#!/usr/bin/env python3
"""
Redis Session Manager for FortiManager Platform
Provides persistent session storage and FortiManager session token management
"""
import redis
import json
import time
import uuid
import hashlib
import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RedisSessionManager:
    """Redis-based session manager for FortiManager platform"""
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0, 
                 redis_password=None, session_timeout=3600):
        """
        Initialize Redis session manager
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
            redis_password: Redis password (if required)
            session_timeout: Session timeout in seconds (default: 1 hour)
        """
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_password = redis_password
        self.session_timeout = session_timeout
        
        # Initialize Redis connection
        try:
            self.redis_client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis session manager connected to {redis_host}:{redis_port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            # Fallback to in-memory storage
            self.redis_client = None
            self._memory_sessions = {}
            logger.warning("Using in-memory session storage as fallback")
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        return str(uuid.uuid4())
    
    def create_session(self, user_data: Dict[str, Any] = None) -> str:
        """
        Create a new session
        
        Args:
            user_data: Optional user data to store in session
            
        Returns:
            Session ID
        """
        session_id = self.generate_session_id()
        
        session_data = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'user_data': user_data or {}
        }
        
        self._store_session(session_id, session_data)
        logger.info(f"Created new session: {session_id}")
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session data
        
        Args:
            session_id: Session ID
            
        Returns:
            Session data or None if not found
        """
        if not session_id:
            return None
            
        session_data = self._get_session(session_id)
        
        if session_data:
            # Update last accessed time
            session_data['last_accessed'] = datetime.now().isoformat()
            self._store_session(session_id, session_data)
            
        return session_data
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> bool:
        """
        Update session data
        
        Args:
            session_id: Session ID
            data: Data to update
            
        Returns:
            True if successful, False otherwise
        """
        session_data = self._get_session(session_id)
        
        if not session_data:
            return False
        
        # Merge new data
        session_data['user_data'].update(data)
        session_data['last_accessed'] = datetime.now().isoformat()
        
        self._store_session(session_id, session_data)
        logger.debug(f"Updated session: {session_id}")
        
        return True
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.redis_client:
                result = self.redis_client.delete(f"session:{session_id}")
                logger.info(f"Deleted session: {session_id}")
                return result > 0
            else:
                if session_id in self._memory_sessions:
                    del self._memory_sessions[session_id]
                    logger.info(f"Deleted session from memory: {session_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {str(e)}")
            return False
    
    def _store_session(self, session_id: str, session_data: Dict[str, Any]):
        """Store session data in Redis or memory"""
        try:
            if self.redis_client:
                self.redis_client.setex(
                    f"session:{session_id}",
                    self.session_timeout,
                    json.dumps(session_data)
                )
            else:
                # Store in memory with expiration
                self._memory_sessions[session_id] = {
                    'data': session_data,
                    'expires_at': time.time() + self.session_timeout
                }
                
        except Exception as e:
            logger.error(f"Error storing session {session_id}: {str(e)}")
    
    def _get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from Redis or memory"""
        try:
            if self.redis_client:
                session_json = self.redis_client.get(f"session:{session_id}")
                if session_json:
                    return json.loads(session_json)
            else:
                # Check memory storage
                if session_id in self._memory_sessions:
                    session_info = self._memory_sessions[session_id]
                    
                    # Check expiration
                    if time.time() < session_info['expires_at']:
                        return session_info['data']
                    else:
                        # Expired, remove it
                        del self._memory_sessions[session_id]
                        
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
    
    def cleanup_expired_sessions(self):
        """Clean up expired sessions (for memory storage)"""
        if not self.redis_client:
            current_time = time.time()
            expired_sessions = [
                session_id for session_id, session_info in self._memory_sessions.items()
                if current_time >= session_info['expires_at']
            ]
            
            for session_id in expired_sessions:
                del self._memory_sessions[session_id]
                logger.debug(f"Cleaned up expired session: {session_id}")
    
    def get_session_count(self) -> int:
        """Get total number of active sessions"""
        try:
            if self.redis_client:
                return len(self.redis_client.keys("session:*"))
            else:
                self.cleanup_expired_sessions()
                return len(self._memory_sessions)
        except Exception as e:
            logger.error(f"Error getting session count: {str(e)}")
            return 0


class FortiManagerSessionManager:
    """Manages FortiManager API session tokens with Redis persistence"""
    
    def __init__(self, redis_session_manager: RedisSessionManager):
        """
        Initialize FortiManager session manager
        
        Args:
            redis_session_manager: Redis session manager instance
        """
        self.session_manager = redis_session_manager
        self.fortimanager_sessions = {}  # In-memory cache for active FM sessions
        
    def get_fortimanager_session(self, site: str, host: str, username: str) -> Optional[str]:
        """
        Get cached FortiManager session token
        
        Args:
            site: Site name (arbys, bww, sonic)
            host: FortiManager host
            username: Username
            
        Returns:
            Session token or None if not found/expired
        """
        session_key = self._generate_fm_session_key(site, host, username)
        
        try:
            if self.session_manager.redis_client:
                session_data = self.session_manager.redis_client.get(f"fm_session:{session_key}")
                if session_data:
                    session_info = json.loads(session_data)
                    
                    # Check if session is still valid (FortiManager sessions typically last 30 minutes)
                    created_time = datetime.fromisoformat(session_info['created_at'])
                    if datetime.now() - created_time < timedelta(minutes=25):  # Refresh before expiry
                        logger.debug(f"Using cached FortiManager session for {site}")
                        return session_info['session_token']
                    else:
                        # Session expired, remove it
                        self.session_manager.redis_client.delete(f"fm_session:{session_key}")
                        logger.debug(f"FortiManager session expired for {site}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving FortiManager session for {site}: {str(e)}")
            return None
    
    def store_fortimanager_session(self, site: str, host: str, username: str, session_token: str):
        """
        Store FortiManager session token
        
        Args:
            site: Site name
            host: FortiManager host
            username: Username
            session_token: FortiManager session token
        """
        session_key = self._generate_fm_session_key(site, host, username)
        
        session_data = {
            'site': site,
            'host': host,
            'username': username,
            'session_token': session_token,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            if self.session_manager.redis_client:
                # Store with 25-minute expiration (FortiManager sessions last ~30 minutes)
                self.session_manager.redis_client.setex(
                    f"fm_session:{session_key}",
                    1500,  # 25 minutes
                    json.dumps(session_data)
                )
                logger.info(f"Stored FortiManager session for {site}")
            else:
                # Store in memory cache
                self.fortimanager_sessions[session_key] = {
                    'data': session_data,
                    'expires_at': time.time() + 1500
                }
                logger.info(f"Stored FortiManager session in memory for {site}")
                
        except Exception as e:
            logger.error(f"Error storing FortiManager session for {site}: {str(e)}")
    
    def invalidate_fortimanager_session(self, site: str, host: str, username: str):
        """
        Invalidate FortiManager session token
        
        Args:
            site: Site name
            host: FortiManager host
            username: Username
        """
        session_key = self._generate_fm_session_key(site, host, username)
        
        try:
            if self.session_manager.redis_client:
                self.session_manager.redis_client.delete(f"fm_session:{session_key}")
            else:
                if session_key in self.fortimanager_sessions:
                    del self.fortimanager_sessions[session_key]
                    
            logger.info(f"Invalidated FortiManager session for {site}")
            
        except Exception as e:
            logger.error(f"Error invalidating FortiManager session for {site}: {str(e)}")
    
    def _generate_fm_session_key(self, site: str, host: str, username: str) -> str:
        """Generate unique key for FortiManager session"""
        key_string = f"{site}:{host}:{username}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_all_fortimanager_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active FortiManager sessions"""
        sessions = {}
        
        try:
            if self.session_manager.redis_client:
                keys = self.session_manager.redis_client.keys("fm_session:*")
                for key in keys:
                    session_data = self.session_manager.redis_client.get(key)
                    if session_data:
                        session_info = json.loads(session_data)
                        sessions[session_info['site']] = session_info
            else:
                current_time = time.time()
                for session_key, session_info in self.fortimanager_sessions.items():
                    if current_time < session_info['expires_at']:
                        sessions[session_info['data']['site']] = session_info['data']
                        
        except Exception as e:
            logger.error(f"Error retrieving all FortiManager sessions: {str(e)}")
        
        return sessions


# Global session managers (initialized in main application)
redis_session_manager = None
fortimanager_session_manager = None

def initialize_session_managers(redis_host='localhost', redis_port=6379, redis_password=None):
    """Initialize global session managers"""
    global redis_session_manager, fortimanager_session_manager
    
    redis_session_manager = RedisSessionManager(
        redis_host=redis_host,
        redis_port=redis_port,
        redis_password=redis_password
    )
    
    fortimanager_session_manager = FortiManagerSessionManager(redis_session_manager)
    
    logger.info("Session managers initialized successfully")
    
    return redis_session_manager, fortimanager_session_manager

def get_session_managers():
    """Get global session managers"""
    return redis_session_manager, fortimanager_session_manager
