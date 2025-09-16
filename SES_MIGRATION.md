# AWS SES Migration Guide

This document outlines the migration from SendGrid to AWS SES for email functionality.

## Changes Made

### 1. Dependencies
- Added `boto3` to requirements.txt (already present)
- No additional packages needed for AWS SES

### 2. New Files Created
- `practice_journal/journal_core/utils/ses.py` - AWS SES utility module

### 3. Files Modified
- `practice_journal/settings.py` - Updated email configuration
- `practice_journal/journal_core/utils/user.py` - Updated import
- `practice_journal/journal_core/utils/email_utils.py` - Updated to use SES
- `practice_journal/journal_core/signals.py` - Updated password reset emails

## Environment Variables

### Required Environment Variables
Add these to your environment configuration:

```bash
# AWS SES SMTP Configuration (for Django's built-in email backend)
AWS_SES_SMTP_USERNAME=your-ses-smtp-username
AWS_SES_SMTP_PASSWORD=your-ses-smtp-password

# Existing AWS Configuration (already present)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_REGION_NAME=us-east-1

# Email Configuration
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Removed Environment Variables
You can now remove:
```bash
SENDGRID_API_KEY=your-sendgrid-api-key
```

## AWS SES Setup

### 1. Verify Your Domain
1. Go to AWS SES Console
2. Navigate to "Verified identities"
3. Add and verify your domain
4. Configure DKIM, SPF, and DMARC records

### 2. Create SMTP Credentials
1. Go to AWS SES Console
2. Navigate to "SMTP settings"
3. Create SMTP credentials
4. Use these credentials for `AWS_SES_SMTP_USERNAME` and `AWS_SES_SMTP_PASSWORD`

### 3. Move Out of Sandbox (Production)
- By default, SES is in sandbox mode
- Request production access to send emails to any address
- Or verify individual email addresses for testing

## Testing

### Test Email Functionality
1. Ensure all environment variables are set
2. Test user registration (email confirmation)
3. Test password reset functionality
4. Test email address change confirmation

### Monitoring
- Check AWS SES console for delivery statistics
- Monitor bounce and complaint rates
- Set up CloudWatch alarms for failed sends

## Rollback Plan

If you need to rollback to SendGrid:
1. Revert the changes in the modified files
2. Restore the original `SENDGRID_API_KEY` environment variable
3. Remove the new `ses.py` file
4. Update imports back to SendGrid

## Benefits of Migration

1. **Cost Savings**: AWS SES is typically more cost-effective than SendGrid
2. **AWS Integration**: Better integration with existing AWS infrastructure
3. **Scalability**: SES scales automatically with your needs
4. **Unified Infrastructure**: All services under one AWS account
