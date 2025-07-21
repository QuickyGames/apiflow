import os
import asyncio
import time
from datetime import datetime
from backend.lib.db import db, create_tables, Job, Workflow
from backend.lib.workflow import WorkflowExecutor

class Worker:
    def __init__(self, poll_interval=5):
        self.poll_interval = poll_interval
        self.running = False
        
    async def process_job(self, job: Job):
        """Process a single job"""
        print(f"Processing job {job.id}: {job.name}")
        
        try:
            # Get the workflow
            workflow = job.workflow
            
            # Create executor
            executor = WorkflowExecutor(workflow, job)
            
            # Execute the workflow
            await executor.execute(job.input)
            
            print(f"Job {job.id} completed successfully")
            
        except Exception as e:
            print(f"Job {job.id} failed: {str(e)}")
            # The executor already updates the job status
    
    async def run(self):
        """Main worker loop"""
        self.running = True
        print("Worker started, polling for jobs...")
        
        while self.running:
            try:
                # Get pending jobs
                with db.atomic():
                    pending_jobs = list(
                        Job.select()
                        .where(Job.status == 'pending')
                        .order_by(Job.created_at)
                        .limit(5)  # Process up to 5 jobs at a time
                    )
                
                if pending_jobs:
                    print(f"Found {len(pending_jobs)} pending jobs")
                    
                    # Process jobs concurrently
                    tasks = []
                    for job in pending_jobs:
                        task = asyncio.create_task(self.process_job(job))
                        tasks.append(task)
                    
                    # Wait for all jobs to complete
                    await asyncio.gather(*tasks, return_exceptions=True)
                
                # Wait before next poll
                await asyncio.sleep(self.poll_interval)
                
            except KeyboardInterrupt:
                print("Worker interrupted by user")
                self.running = False
                break
            except Exception as e:
                print(f"Worker error: {str(e)}")
                await asyncio.sleep(self.poll_interval)
    
    def stop(self):
        """Stop the worker"""
        self.running = False
        print("Worker stopping...")


async def main():
    """Main entry point"""
    # Create tables if needed
    create_tables()
    
    # Create and run worker
    worker = Worker(poll_interval=5)
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        worker.stop()
    finally:
        print("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
