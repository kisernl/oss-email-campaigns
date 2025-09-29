"""
Cloud Tasks service for managing email sending tasks.

Provides functionality to create and manage Cloud Tasks for individual email
sending, enabling scalable and resilient email campaign processing.
"""

import os
import json
import random
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from google.cloud import tasks_v2
from google.cloud.tasks_v2 import Task
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class CloudTasksService:
    """
    Service for managing Cloud Tasks for email campaigns.
    
    Handles creating individual email sending tasks with proper scheduling
    and delay management for email campaigns.
    """
    
    def __init__(self):
        """Initialize the Cloud Tasks service."""
        self.client = tasks_v2.CloudTasksClient()
        
        # Get configuration from environment
        self.project_id = os.getenv('PROJECT_ID', 'oss-email-campaigns')
        self.location = os.getenv('QUEUE_LOCATION', 'us-east1')
        self.queue_name = os.getenv('QUEUE_NAME', 'email-campaign-queue')
        self.service_url = os.getenv('CLOUD_RUN_SERVICE_URL', 'https://oss-email-campaigns-backend-891093788849.us-east1.run.app')
        
        # Construct queue path
        self.queue_path = self.client.queue_path(
            self.project_id, 
            self.location, 
            self.queue_name
        )
        
        print(f"🔧 Cloud Tasks initialized - Queue: {self.queue_path}")
    
    def create_email_task(
        self, 
        email_send_id: int, 
        delay_minutes: int = 0,
        task_name: Optional[str] = None
    ) -> Task:
        """
        Create a Cloud Task to send a single email.
        
        Args:
            email_send_id: ID of the EmailSend record to process
            delay_minutes: Minutes to delay before executing the task
            task_name: Optional custom task name
            
        Returns:
            Created Task object
        """
        try:
            # Task payload
            payload = {
                'email_send_id': email_send_id,
                'timestamp': datetime.utcnow().isoformat(),
                'created_by': 'campaign_service'
            }
            
            # Create HTTP request for the task
            http_request = {
                'http_method': tasks_v2.HttpMethod.POST,
                'url': f'{self.service_url}/api/tasks/send-email',
                'headers': {
                    'Content-Type': 'application/json',
                    'User-Agent': 'CloudTasks-EmailCampaign/1.0'
                },
                'body': json.dumps(payload).encode('utf-8')
            }
            
            # Create task structure
            task_config = {
                'http_request': http_request
            }
            
            # Add custom task name if provided
            if task_name:
                task_config['name'] = self.client.task_path(
                    self.project_id,
                    self.location,
                    self.queue_name,
                    task_name
                )
            
            # Add delay if specified
            if delay_minutes > 0:
                schedule_time = datetime.utcnow() + timedelta(minutes=delay_minutes)
                # Convert to protobuf Timestamp
                task_config['schedule_time'] = {
                    'seconds': int(schedule_time.timestamp())
                }
                print(f"📅 Task scheduled for {delay_minutes} minutes from now ({schedule_time.strftime('%H:%M:%S')})")
            
            # Create the task
            task = self.client.create_task(
                parent=self.queue_path, 
                task=task_config
            )
            
            print(f"✅ Created task for email_send_id {email_send_id}: {task.name}")
            return task
            
        except Exception as e:
            print(f"❌ Error creating Cloud Task for email_send_id {email_send_id}: {e}")
            raise
    
    def create_campaign_tasks(
        self, 
        email_send_ids: list[int], 
        delay_min_minutes: int = 4,
        delay_max_minutes: int = 7
    ) -> list[Task]:
        """
        Create multiple email tasks for a campaign with staggered delays.
        
        Args:
            email_send_ids: List of EmailSend IDs to create tasks for
            delay_min_minutes: Minimum delay between emails
            delay_max_minutes: Maximum delay between emails
            
        Returns:
            List of created Task objects
        """
        tasks = []
        cumulative_delay = 0
        
        print(f"🚀 Creating {len(email_send_ids)} email tasks with {delay_min_minutes}-{delay_max_minutes} minute delays")
        
        for i, email_send_id in enumerate(email_send_ids):
            # Calculate delay for this email
            if i == 0:
                # First email sends immediately
                delay_minutes = 0
            else:
                # Subsequent emails have random delays
                email_delay = random.randint(delay_min_minutes, delay_max_minutes)
                cumulative_delay += email_delay
                delay_minutes = cumulative_delay
            
            # Create task name to ensure uniqueness
            task_name = f"email-{email_send_id}-{int(datetime.utcnow().timestamp())}"
            
            try:
                task = self.create_email_task(
                    email_send_id=email_send_id,
                    delay_minutes=delay_minutes,
                    task_name=task_name
                )
                tasks.append(task)
                
                if i % 10 == 0 and i > 0:
                    print(f"📊 Created {i}/{len(email_send_ids)} tasks...")
                    
            except Exception as e:
                print(f"❌ Failed to create task for email_send_id {email_send_id}: {e}")
                # Continue creating other tasks
                continue
        
        print(f"✅ Successfully created {len(tasks)}/{len(email_send_ids)} email tasks")
        return tasks
    
    def delete_task(self, task_name: str) -> bool:
        """
        Delete a specific task.
        
        Args:
            task_name: Full name of the task to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_task(name=task_name)
            print(f"🗑️ Deleted task: {task_name}")
            return True
        except Exception as e:
            print(f"❌ Error deleting task {task_name}: {e}")
            return False
    
    def get_queue_info(self) -> Dict[str, Any]:
        """
        Get information about the task queue.
        
        Returns:
            Dictionary with queue statistics
        """
        try:
            queue = self.client.get_queue(name=self.queue_path)
            return {
                'name': queue.name,
                'state': queue.state.name,
                'purge_time': queue.purge_time,
                'retry_config': {
                    'max_attempts': queue.retry_config.max_attempts,
                    'max_retry_duration': queue.retry_config.max_retry_duration.seconds
                } if queue.retry_config else None
            }
        except Exception as e:
            print(f"❌ Error getting queue info: {e}")
            return {'error': str(e)}
    
    def purge_queue(self) -> bool:
        """
        Purge all tasks from the queue.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.purge_queue(name=self.queue_path)
            print(f"🧹 Purged all tasks from queue: {self.queue_name}")
            return True
        except Exception as e:
            print(f"❌ Error purging queue: {e}")
            return False


# Global instance
tasks_service: Optional[CloudTasksService] = None


def get_tasks_service() -> CloudTasksService:
    """Get or create the global Cloud Tasks service instance."""
    global tasks_service
    if tasks_service is None:
        tasks_service = CloudTasksService()
    return tasks_service