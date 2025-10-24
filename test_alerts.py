#!/usr/bin/env python3
"""
Test script for Email and Slack alerts
Run this to verify your alert configuration before production use
"""

import os
import sys
from app.integrations.alert_manager import AlertManager

# Sample high-value opportunities for testing
TEST_OPPORTUNITIES = [
    {
        'address': '42 Lindbergh Ave, Newton, MA 02465',
        'development_score': '92.5',
        'label': 'development',
        'explanation': 'Prime opportunity for those seeking a teardown project with excellent potential.',
        'price': '500000'
    },
    {
        'address': '371 Cherry St, Newton, MA 02465',
        'development_score': '78.0',
        'label': 'potential',
        'explanation': 'Good development potential with large lot in desirable area.',
        'price': '450000'
    },
    {
        'address': '253 Nahanton St, Newton, MA 02459',
        'development_score': '71.5',
        'label': 'development',
        'explanation': 'Solid development opportunity with reasonable acquisition costs.',
        'price': '520000'
    }
]

def test_email():
    """Test email alert"""
    print("\n" + "="*60)
    print("Testing EMAIL Alert")
    print("="*60)
    
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not sender_email or not sender_password:
        print("❌ SENDER_EMAIL or SENDER_PASSWORD not configured in .env")
        return False
    
    print(f"📧 Sending test email to: {sender_email}")
    
    try:
        alert = AlertManager(email_enabled=True, slack_enabled=False)
        results = alert.alert_on_opportunities(
            opportunities=TEST_OPPORTUNITIES,
            recipient_email=sender_email,
            run_type='test'
        )
        
        if results.get('email'):
            print("✅ Email sent successfully!")
            return True
        else:
            print("❌ Email failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_slack():
    """Test Slack alert"""
    print("\n" + "="*60)
    print("Testing SLACK Alert")
    print("="*60)
    
    slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("❌ SLACK_WEBHOOK_URL not configured in .env")
        return False
    
    print(f"💬 Sending test Slack message...")
    
    try:
        alert = AlertManager(email_enabled=False, slack_enabled=True)
        results = alert.alert_on_opportunities(
            opportunities=TEST_OPPORTUNITIES,
            run_type='test'
        )
        
        if results.get('slack'):
            print("✅ Slack message sent successfully!")
            return True
        else:
            print("❌ Slack message failed to send")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_both():
    """Test both email and Slack"""
    print("\n" + "="*60)
    print("Testing BOTH Email & Slack Alerts")
    print("="*60)
    
    try:
        alert = AlertManager(email_enabled=True, slack_enabled=True)
        results = alert.alert_on_opportunities(
            opportunities=TEST_OPPORTUNITIES,
            run_type='test'
        )
        
        if results.get('email'):
            print("✅ Email sent successfully!")
        else:
            print("❌ Email failed")
        
        if results.get('slack'):
            print("✅ Slack message sent successfully!")
        else:
            print("❌ Slack failed")
        
        return results.get('email') or results.get('slack')
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_pipeline_summary():
    """Test pipeline summary alert"""
    print("\n" + "="*60)
    print("Testing PIPELINE SUMMARY Alert")
    print("="*60)
    
    try:
        alert = AlertManager(email_enabled=False, slack_enabled=True)
        results = alert.send_pipeline_summary(
            total_collected=30,
            total_classified=30,
            opportunities_found=3,
            duration_seconds=87.5,
            run_type='test'
        )
        
        if results.get('slack'):
            print("✅ Pipeline summary sent to Slack!")
            return True
        else:
            print("❌ Pipeline summary failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "🚀 Alert System Test Suite" + " "*17 + "║")
    print("╚" + "="*58 + "╝")
    
    # Check environment
    print("\n📋 Checking environment variables...")
    
    has_email = os.getenv('SENDER_EMAIL') and os.getenv('SENDER_PASSWORD')
    has_slack = os.getenv('SLACK_WEBHOOK_URL')
    
    print(f"  Email config: {'✅' if has_email else '❌'}")
    print(f"  Slack config: {'✅' if has_slack else '❌'}")
    
    if not has_email and not has_slack:
        print("\n❌ No alerts configured! Set SENDER_EMAIL/PASSWORD or SLACK_WEBHOOK_URL in .env")
        return 1
    
    # Run tests
    results = []
    
    if has_email:
        results.append(('Email', test_email()))
    
    if has_slack:
        results.append(('Slack', test_slack()))
    
    # Pipeline summary test
    if has_slack:
        results.append(('Pipeline Summary', test_pipeline_summary()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:.<40} {status}")
    
    all_passed = all(passed for _, passed in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests passed! Alerts are ready to use.")
        print("\nRun: python -m app.dev_pipeline")
        print("to trigger alerts in your next pipeline run.")
        return 0
    else:
        print("❌ Some tests failed. Check configuration and try again.")
        print("\nNeed help? See TASK2_EMAIL_SLACK_SETUP.md")
        return 1

if __name__ == '__main__':
    sys.exit(main())
