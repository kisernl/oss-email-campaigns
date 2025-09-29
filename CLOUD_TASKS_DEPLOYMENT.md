# Cloud Tasks Deployment Guide

This guide explains how to deploy the Cloud Tasks-enabled email campaign system to Google Cloud Run.

## Overview

The email campaign system has been upgraded to use Google Cloud Tasks instead of long-running background processes. This solves the Cloud Run autoscaling issue where campaigns would stop mid-process when instances scaled down.

## Architecture Changes

### Before (Problematic)
```
Campaign Start → Long-Running Process → Send All Emails → Complete
                      ↑
                Cloud Run kills this during delays
```

### After (Cloud Tasks Solution)
```
Campaign Start → Create Individual Tasks → Each Task Sends One Email → Complete
```

## What Changed

1. **New Cloud Tasks Service** (`app/services/task_service.py`)
2. **Individual Email Handler** (`send_single_email_task()` function)
3. **Task Processing Endpoint** (`/api/tasks/send-email`)
4. **Campaign Start Logic** (`start_campaign_with_cloud_tasks()` function)
5. **Updated Send Campaign API** (now uses Cloud Tasks for immediate sending)

## Deployment Steps

### 1. Create Cloud Tasks Queue

```bash
# Create the email campaign queue
gcloud tasks queues create email-campaign-queue \
  --location=us-east1 \
  --max-attempts=3 \
  --max-retry-duration=3600s
```

### 2. Update Environment Variables

Add these to your Cloud Run service:

```bash
GOOGLE_CLOUD_PROJECT=ai-lead-gen-471213
CLOUD_TASKS_LOCATION=us-east1
CLOUD_TASKS_QUEUE=email-campaign-queue
CLOUD_RUN_SERVICE_URL=https://your-service-url.run.app
```

### 3. Deploy Updated Code

```bash
# Build and deploy to Cloud Run
gcloud run deploy oss-email-campaigns-backend \
  --source . \
  --region us-east1 \
  --allow-unauthenticated
```

### 4. Test the New System

1. **Test individual task endpoint**:
   ```bash
   curl -X POST https://your-service-url/api/tasks/health
   ```

2. **Create a test campaign** via your frontend

3. **Monitor Cloud Tasks** in Google Cloud Console

## How It Works

### Campaign Creation Flow
1. User creates campaign and clicks "Send"
2. API calls `start_campaign_with_cloud_tasks()`
3. System reads Google Sheets and creates `EmailSend` records
4. System creates individual Cloud Tasks for each email
5. Tasks are scheduled with random delays (4-7 minutes apart)

### Email Processing Flow
1. Cloud Tasks calls `/api/tasks/send-email` for each email
2. Endpoint calls `send_single_email_task()`
3. Email is sent via SMTP
4. Campaign statistics are updated
5. When all tasks complete, campaign is marked as "completed"

## Benefits

✅ **Survives instance restarts** - Each email is a separate task
✅ **Automatic retries** - Failed emails retry up to 3 times  
✅ **Better scalability** - Can handle thousands of emails
✅ **Cost effective** - Only pay when processing
✅ **Resumable** - Can restart campaigns by creating new tasks

## Monitoring

### Check Queue Status
```bash
gcloud tasks queues describe email-campaign-queue --location=us-east1
```

### View Tasks
```bash
gcloud tasks list --queue=email-campaign-queue --location=us-east1
```

### Purge Queue (if needed)
```bash
gcloud tasks queues purge email-campaign-queue --location=us-east1
```

## Troubleshooting

### Campaign Stuck in "Sending"
- Check Cloud Tasks queue for pending tasks
- Verify task endpoint is responding: `/api/tasks/health`
- Check Cloud Run logs for task processing errors

### Tasks Not Being Created
- Verify Cloud Tasks queue exists
- Check IAM permissions for Cloud Tasks
- Review environment variables

### Emails Not Sending
- Test individual email endpoint with valid `email_send_id`
- Check SMTP configuration
- Verify Google Sheets integration

## Environment Variables Summary

### Required for Cloud Tasks
```env
GOOGLE_CLOUD_PROJECT=ai-lead-gen-471213
CLOUD_TASKS_LOCATION=us-east1
CLOUD_TASKS_QUEUE=email-campaign-queue
CLOUD_RUN_SERVICE_URL=https://your-service-url.run.app
```

### Existing Variables (still needed)
```env
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
GOOGLE_CREDENTIALS_JSON={"type":"service_account"...}
SMTP_HOST=your-smtp-host
SMTP_USERNAME=your-email
SMTP_PASSWORD=your-password
# ... other existing variables
```

## API Changes

### New Endpoints
- `POST /api/tasks/send-email` - Process individual email task
- `GET /api/tasks/health` - Health check for task processing

### Modified Endpoints  
- `POST /api/campaigns/{id}/send` - Now uses Cloud Tasks for immediate sending

### Behavior Changes
- Immediate campaigns now use Cloud Tasks
- Scheduled campaigns still use background tasks (for now)
- Campaign statistics update as individual emails complete
- Campaigns complete automatically when all tasks finish

## Next Steps

1. **Deploy and test** the current implementation
2. **Monitor performance** and adjust retry settings if needed
3. **Consider Cloud Scheduler** for scheduled campaigns
4. **Add batch processing** for very large campaigns (1000+ emails)

This Cloud Tasks implementation resolves the Cloud Run scaling issue and provides a more robust, scalable email campaign system.