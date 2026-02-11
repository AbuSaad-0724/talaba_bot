"""
File Cleanup Utility
Automatically removes old temporary files
"""

import os
import time
import logging
from config import TEMP_DIR

logger = logging.getLogger(__name__)

def cleanup_old_files(max_age_hours=24):
    """
    Remove files older than max_age_hours from temp directory
    
    Args:
        max_age_hours: Maximum age of files in hours (default: 24)
    """
    if not os.path.exists(TEMP_DIR):
        logger.info(f"Temp directory does not exist: {TEMP_DIR}")
        return
    
    now = time.time()
    max_age_seconds = max_age_hours * 3600
    
    deleted_count = 0
    total_size = 0
    
    try:
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            
            # Skip if not a file
            if not os.path.isfile(filepath):
                continue
            
            try:
                # Get file age
                file_age = now - os.path.getmtime(filepath)
                file_size = os.path.getsize(filepath)
                
                # Delete if too old
                if file_age > max_age_seconds:
                    os.remove(filepath)
                    deleted_count += 1
                    total_size += file_size
                    logger.info(f"Deleted old file: {filename} ({file_size} bytes, {file_age/3600:.1f} hours old)")
                    
            except Exception as e:
                logger.error(f"Error processing file {filename}: {e}")
                
    except Exception as e:
        logger.error(f"Error accessing temp directory: {e}")
    
    if deleted_count > 0:
        logger.info(f"Cleanup completed: {deleted_count} files deleted, {total_size/1024:.2f} KB freed")
    else:
        logger.debug("No old files to delete")
    
    return deleted_count, total_size


def get_temp_stats():
    """Get statistics about temp directory"""
    if not os.path.exists(TEMP_DIR):
        return {'exists': False}
    
    file_count = 0
    total_size = 0
    oldest_file = None
    oldest_age = 0
    
    now = time.time()
    
    try:
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            
            if os.path.isfile(filepath):
                file_count += 1
                file_size = os.path.getsize(filepath)
                total_size += file_size
                
                file_age = now - os.path.getmtime(filepath)
                if file_age > oldest_age:
                    oldest_age = file_age
                    oldest_file = filename
                    
    except Exception as e:
        logger.error(f"Error getting temp stats: {e}")
    
    return {
        'exists': True,
        'file_count': file_count,
        'total_size': total_size,
        'total_size_mb': total_size / (1024 * 1024),
        'oldest_file': oldest_file,
        'oldest_age_hours': oldest_age / 3600
    }


def cleanup_all_temp_files():
    """Remove ALL files from temp directory (use with caution!)"""
    if not os.path.exists(TEMP_DIR):
        return 0
    
    deleted_count = 0
    
    try:
        for filename in os.listdir(TEMP_DIR):
            filepath = os.path.join(TEMP_DIR, filename)
            
            if os.path.isfile(filepath):
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting {filename}: {e}")
                    
    except Exception as e:
        logger.error(f"Error cleaning temp directory: {e}")
    
    logger.info(f"Cleaned all temp files: {deleted_count} files deleted")
    return deleted_count


if __name__ == "__main__":
    # Test cleanup
    logging.basicConfig(level=logging.INFO)
    
    print("📊 Temp Directory Stats:")
    stats = get_temp_stats()
    
    if stats['exists']:
        print(f"   Files: {stats['file_count']}")
        print(f"   Size: {stats['total_size_mb']:.2f} MB")
        if stats['oldest_file']:
            print(f"   Oldest: {stats['oldest_file']} ({stats['oldest_age_hours']:.1f} hours)")
    else:
        print("   Directory does not exist")
    
    print("\n🧹 Running cleanup...")
    deleted, size = cleanup_old_files(max_age_hours=24)
    print(f"   Deleted: {deleted} files ({size/1024:.2f} KB)")
