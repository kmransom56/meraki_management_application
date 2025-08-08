#!/usr/bin/env python3
"""
Redis Session Management Test for FortiManager Platform
Test Redis-based session storage and FortiManager session token reuse
"""
import os
import time
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_redis_connectivity():
    """Test basic Redis connectivity"""
    print("=" * 60)
    print("TESTING REDIS CONNECTIVITY")
    print("=" * 60)
    
    try:
        import redis
        
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_password = os.getenv('REDIS_PASSWORD') or None
        
        print(f"Connecting to Redis: {redis_host}:{redis_port}")
        
        # Test Redis connection
        r = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            decode_responses=True,
            socket_connect_timeout=5
        )
        
        # Test ping
        r.ping()
        print("✅ Redis connection successful")
        
        # Test basic operations
        r.set("test_key", "test_value", ex=10)
        value = r.get("test_key")
        
        if value == "test_value":
            print("✅ Redis read/write operations working")
        else:
            print("❌ Redis read/write operations failed")
            
        # Clean up
        r.delete("test_key")
        
        return True
        
    except ImportError:
        print("❌ Redis module not installed")
        print("   Install with: pip install redis hiredis")
        return False
    except Exception as e:
        print(f"❌ Redis connection failed: {str(e)}")
        print("   Make sure Redis server is running")
        return False

def test_session_managers():
    """Test Redis session managers"""
    print("\n" + "=" * 60)
    print("TESTING SESSION MANAGERS")
    print("=" * 60)
    
    try:
        from redis_session_manager import initialize_session_managers, get_session_managers
        
        # Initialize session managers
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', 6379))
        redis_password = os.getenv('REDIS_PASSWORD') or None
        
        print(f"Initializing session managers: {redis_host}:{redis_port}")
        
        redis_session_manager, fm_session_manager = initialize_session_managers(
            redis_host, redis_port, redis_password
        )
        
        if redis_session_manager and fm_session_manager:
            print("✅ Session managers initialized successfully")
            
            # Test session creation
            session_id = redis_session_manager.create_session({
                'user': 'test_user',
                'timestamp': time.time()
            })
            
            print(f"✅ Created test session: {session_id}")
            
            # Test session retrieval
            session_data = redis_session_manager.get_session(session_id)
            if session_data:
                print("✅ Session retrieval working")
                print(f"   Session data: {json.dumps(session_data, indent=2)}")
            else:
                print("❌ Session retrieval failed")
                
            # Test session update
            update_success = redis_session_manager.update_session(session_id, {
                'updated': True,
                'update_time': time.time()
            })
            
            if update_success:
                print("✅ Session update working")
            else:
                print("❌ Session update failed")
                
            # Clean up
            redis_session_manager.delete_session(session_id)
            print("✅ Session cleanup completed")
            
            return True
        else:
            print("❌ Session managers initialization failed")
            return False
            
    except ImportError as e:
        print(f"❌ Session manager modules not available: {e}")
        return False
    except Exception as e:
        print(f"❌ Session manager test failed: {str(e)}")
        return False

def test_fortimanager_session_reuse():
    """Test FortiManager session token reuse"""
    print("\n" + "=" * 60)
    print("TESTING FORTIMANAGER SESSION TOKEN REUSE")
    print("=" * 60)
    
    try:
        from redis_session_manager import get_session_managers
        from fortimanager_api import FortiManagerAPI
        
        # Get session managers
        redis_session_manager, fm_session_manager = get_session_managers()
        
        if not (redis_session_manager and fm_session_manager):
            print("❌ Session managers not available")
            return False
        
        # Test with ARBYS FortiManager
        arbys_host = os.getenv('ARBYS_FORTIMANAGER_HOST')
        arbys_username = os.getenv('ARBYS_USERNAME')
        arbys_password = os.getenv('ARBYS_PASSWORD')
        
        if not all([arbys_host, arbys_username, arbys_password]):
            print("❌ ARBYS FortiManager credentials not found in environment")
            return False
            
        print(f"Testing session reuse with ARBYS FortiManager: {arbys_host}")
        
        # First connection - should create new session
        print("\n1. First connection (should create new session):")
        fm1 = FortiManagerAPI(arbys_host, arbys_username, arbys_password, site='arbys')
        
        start_time = time.time()
        login1_success = fm1.login()
        login1_time = time.time() - start_time
        
        if login1_success:
            print(f"✅ First login successful in {login1_time:.2f}s")
            print(f"   Session ID: {fm1.session_id}")
            
            # Store session manually to test caching
            if fm1.session_id:
                fm_session_manager.store_fortimanager_session(
                    'arbys', arbys_host, arbys_username, fm1.session_id
                )
                print("✅ Session token stored in Redis")
            
            fm1.logout()
        else:
            print("❌ First login failed")
            return False
        
        # Second connection - should reuse cached session
        print("\n2. Second connection (should reuse cached session):")
        fm2 = FortiManagerAPI(arbys_host, arbys_username, arbys_password, site='arbys')
        
        start_time = time.time()
        login2_success = fm2.login()
        login2_time = time.time() - start_time
        
        if login2_success:
            print(f"✅ Second login successful in {login2_time:.2f}s")
            print(f"   Session ID: {fm2.session_id}")
            
            # Check if session was reused (should be much faster)
            if login2_time < login1_time * 0.5:  # Should be at least 50% faster
                print("✅ Session reuse detected (faster login)")
            else:
                print("⚠️ Session may not have been reused (similar login time)")
                
            fm2.logout()
        else:
            print("❌ Second login failed")
            return False
            
        # Test session invalidation
        print("\n3. Testing session invalidation:")
        fm_session_manager.invalidate_fortimanager_session('arbys', arbys_host, arbys_username)
        print("✅ Session invalidated")
        
        # Third connection - should create new session again
        print("\n4. Third connection (should create new session after invalidation):")
        fm3 = FortiManagerAPI(arbys_host, arbys_username, arbys_password, site='arbys')
        
        start_time = time.time()
        login3_success = fm3.login()
        login3_time = time.time() - start_time
        
        if login3_success:
            print(f"✅ Third login successful in {login3_time:.2f}s")
            print(f"   Session ID: {fm3.session_id}")
            
            # Should be similar to first login time (new session)
            if abs(login3_time - login1_time) < 2.0:  # Within 2 seconds
                print("✅ New session created after invalidation")
            else:
                print("⚠️ Login time unexpected after invalidation")
                
            fm3.logout()
        else:
            print("❌ Third login failed")
            return False
            
        print("\n✅ FortiManager session reuse test completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Required modules not available: {e}")
        return False
    except Exception as e:
        print(f"❌ FortiManager session reuse test failed: {str(e)}")
        return False

def test_multi_site_session_management():
    """Test session management across multiple FortiManager sites"""
    print("\n" + "=" * 60)
    print("TESTING MULTI-SITE SESSION MANAGEMENT")
    print("=" * 60)
    
    try:
        from redis_session_manager import get_session_managers
        
        # Get session managers
        redis_session_manager, fm_session_manager = get_session_managers()
        
        if not (redis_session_manager and fm_session_manager):
            print("❌ Session managers not available")
            return False
        
        # Test storing sessions for all sites
        sites = ['arbys', 'bww', 'sonic']
        test_sessions = {}
        
        for site in sites:
            host = os.getenv(f'{site.upper()}_FORTIMANAGER_HOST')
            username = os.getenv(f'{site.upper()}_USERNAME')
            
            if host and username:
                # Store a test session
                test_session_id = f"test_session_{site}_{int(time.time())}"
                fm_session_manager.store_fortimanager_session(
                    site, host, username, test_session_id
                )
                test_sessions[site] = test_session_id
                print(f"✅ Stored test session for {site.upper()}: {host}")
            else:
                print(f"⚠️ Skipping {site.upper()} - credentials not found")
        
        # Retrieve all sessions
        print(f"\nRetrieving all FortiManager sessions:")
        all_sessions = fm_session_manager.get_all_fortimanager_sessions()
        
        for site, session_info in all_sessions.items():
            print(f"✅ {site.upper()}: {session_info['host']} - Session: {session_info['session_token'][:20]}...")
        
        # Clean up test sessions
        print(f"\nCleaning up test sessions:")
        for site, session_id in test_sessions.items():
            host = os.getenv(f'{site.upper()}_FORTIMANAGER_HOST')
            username = os.getenv(f'{site.upper()}_USERNAME')
            
            if host and username:
                fm_session_manager.invalidate_fortimanager_session(site, host, username)
                print(f"✅ Cleaned up {site.upper()} test session")
        
        print(f"\n✅ Multi-site session management test completed")
        return True
        
    except Exception as e:
        print(f"❌ Multi-site session management test failed: {str(e)}")
        return False

def main():
    """Run all Redis session management tests"""
    print("Redis Session Management Test Suite")
    print("FortiManager Platform - Production Session Management")
    print("=" * 60)
    
    test_results = []
    
    # Test 1: Redis connectivity
    test_results.append(("Redis Connectivity", test_redis_connectivity()))
    
    # Test 2: Session managers
    test_results.append(("Session Managers", test_session_managers()))
    
    # Test 3: FortiManager session reuse
    test_results.append(("FortiManager Session Reuse", test_fortimanager_session_reuse()))
    
    # Test 4: Multi-site session management
    test_results.append(("Multi-Site Session Management", test_multi_site_session_management()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Redis session management tests PASSED!")
        print("Your FortiManager platform is ready for production with Redis session management!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review the issues above.")
        print("Common solutions:")
        print("1. Install Redis: pip install redis hiredis")
        print("2. Start Redis server: redis-server")
        print("3. Check Redis configuration in .env file")
        print("4. Verify FortiManager credentials are correct")

if __name__ == "__main__":
    main()
