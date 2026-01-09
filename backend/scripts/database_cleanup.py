"""
Database Cleanup & Deduplication Script
Removes duplicate documents, invalid batches, and orphaned records
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.database import get_db, close_db, Batch, File, Block, ComplianceFlag, ApprovalClassification, ApprovalRequiredDocument
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def remove_duplicate_documents():
    """Remove duplicate documents based on hash."""
    db = get_db()
    try:
        # Find duplicate hashes
        from sqlalchemy import func
        
        duplicate_hashes = db.query(
            File.document_hash,
            func.count(File.id).label('count')
        ).filter(
            File.document_hash.isnot(None)
        ).group_by(
            File.document_hash
        ).having(
            func.count(File.id) > 1
        ).all()
        
        removed_count = 0
        
        for hash_val, count in duplicate_hashes:
            # Get all files with this hash, keep the oldest one
            files = db.query(File).filter(
                File.document_hash == hash_val
            ).order_by(File.uploaded_at).all()
            
            # Keep first, remove rest
            for file in files[1:]:
                logger.info(f"Removing duplicate file: {file.filename} (hash: {hash_val[:16]}...)")
                # Delete physical file
                try:
                    from pathlib import Path
                    if Path(file.filepath).exists():
                        Path(file.filepath).unlink()
                except Exception as e:
                    logger.warning(f"Could not delete file {file.filepath}: {e}")
                
                # Delete associated blocks
                db.query(Block).filter(Block.source_doc == file.filename).delete()
                
                # Delete file record
                db.delete(file)
                removed_count += 1
        
        db.commit()
        logger.info(f"✅ Removed {removed_count} duplicate documents")
        return removed_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing duplicates: {e}")
        return 0
    finally:
        close_db(db)


def remove_invalid_batches():
    """Remove batches marked as invalid."""
    db = get_db()
    try:
        invalid_batches = db.query(Batch).filter(Batch.is_invalid == 1).all()
        removed_count = 0
        
        for batch in invalid_batches:
            logger.info(f"Removing invalid batch: {batch.id}")
            
            # Delete associated data
            db.query(Block).filter(Block.batch_id == batch.id).delete()
            db.query(File).filter(File.batch_id == batch.id).delete()
            db.query(ComplianceFlag).filter(ComplianceFlag.batch_id == batch.id).delete()
            db.query(ApprovalClassification).filter(ApprovalClassification.batch_id == batch.id).delete()
            db.query(ApprovalRequiredDocument).filter(ApprovalRequiredDocument.batch_id == batch.id).delete()
            
            # Delete batch
            db.delete(batch)
            removed_count += 1
        
        db.commit()
        logger.info(f"✅ Removed {removed_count} invalid batches")
        return removed_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing invalid batches: {e}")
        return 0
    finally:
        close_db(db)


def remove_orphaned_files():
    """Remove files without associated batches."""
    db = get_db()
    try:
        # Get all batch IDs
        batch_ids = {b.id for b in db.query(Batch.id).all()}
        
        # Find files without batches
        orphaned_files = db.query(File).filter(~File.batch_id.in_(batch_ids)).all()
        removed_count = 0
        
        for file in orphaned_files:
            logger.info(f"Removing orphaned file: {file.filename}")
            
            # Delete physical file
            try:
                from pathlib import Path
                if Path(file.filepath).exists():
                    Path(file.filepath).unlink()
            except Exception as e:
                logger.warning(f"Could not delete file {file.filepath}: {e}")
            
            # Delete associated blocks
            db.query(Block).filter(Block.source_doc == file.filename).delete()
            
            # Delete file record
            db.delete(file)
            removed_count += 1
        
        db.commit()
        logger.info(f"✅ Removed {removed_count} orphaned files")
        return removed_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing orphaned files: {e}")
        return 0
    finally:
        close_db(db)


def remove_orphaned_blocks():
    """Remove blocks without associated batches."""
    db = get_db()
    try:
        # Get all batch IDs
        batch_ids = {b.id for b in db.query(Batch.id).all()}
        
        # Find blocks without batches
        orphaned_blocks = db.query(Block).filter(~Block.batch_id.in_(batch_ids)).all()
        removed_count = len(orphaned_blocks)
        
        for block in orphaned_blocks:
            db.delete(block)
        
        db.commit()
        logger.info(f"✅ Removed {removed_count} orphaned blocks")
        return removed_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error removing orphaned blocks: {e}")
        return 0
    finally:
        close_db(db)


def enforce_uniqueness_constraints():
    """Enforce uniqueness: institution + department + year."""
    db = get_db()
    try:
        # Find batches with same institution + department + year
        from sqlalchemy import func
        
        duplicates = db.query(
            Batch.institution_name,
            Batch.department_name,
            Batch.academic_year,
            func.count(Batch.id).label('count')
        ).filter(
            Batch.institution_name.isnot(None),
            Batch.department_name.isnot(None),
            Batch.academic_year.isnot(None)
        ).group_by(
            Batch.institution_name,
            Batch.department_name,
            Batch.academic_year
        ).having(
            func.count(Batch.id) > 1
        ).all()
        
        removed_count = 0
        
        for inst, dept, year, count in duplicates:
            # Get all batches with this combination, keep the most recent
            batches = db.query(Batch).filter(
                Batch.institution_name == inst,
                Batch.department_name == dept,
                Batch.academic_year == year
            ).order_by(Batch.created_at.desc()).all()
            
            # Keep first (most recent), mark others for review
            for batch in batches[1:]:
                logger.info(f"Found duplicate: {inst}/{dept}/{year} - batch {batch.id} (keeping most recent)")
                # Mark as invalid instead of deleting (data might be needed)
                batch.is_invalid = 1
                removed_count += 1
        
        db.commit()
        logger.info(f"✅ Marked {removed_count} duplicate institution/department/year combinations as invalid")
        return removed_count
    except Exception as e:
        db.rollback()
        logger.error(f"Error enforcing uniqueness: {e}")
        return 0
    finally:
        close_db(db)


def cleanup_all():
    """Run all cleanup operations."""
    logger.info("🧹 Starting database cleanup...")
    
    results = {
        "duplicate_documents": remove_duplicate_documents(),
        "invalid_batches": remove_invalid_batches(),
        "orphaned_files": remove_orphaned_files(),
        "orphaned_blocks": remove_orphaned_blocks(),
        "duplicate_combinations": enforce_uniqueness_constraints()
    }
    
    total_removed = sum(results.values())
    logger.info(f"✅ Cleanup complete. Total items removed/marked: {total_removed}")
    
    return results


if __name__ == "__main__":
    cleanup_all()

