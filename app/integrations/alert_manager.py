"""
Alert Manager for Email and Slack Notifications
Sends alerts when high-value development opportunities are found
"""

import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Optional
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AlertManager:
    """
    Manages email and Slack notifications for development opportunities
    Triggers on high-value properties (score >= threshold)
    """
    
    def __init__(self, email_enabled: bool = True, slack_enabled: bool = True):
        """
        Initialize Alert Manager
        
        Args:
            email_enabled: Send email alerts (requires SMTP config)
            slack_enabled: Send Slack alerts (requires SLACK_WEBHOOK_URL)
        """
        self.logger = logging.getLogger('alert_manager')
        self.email_enabled = email_enabled
        self.slack_enabled = slack_enabled
        
        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        
        # Slack configuration
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        
        # Alert threshold
        self.score_threshold = 70.0
        
        # Validate configuration
        if self.email_enabled and not (self.sender_email and self.sender_password):
            self.logger.warning("Email enabled but SENDER_EMAIL/SENDER_PASSWORD not configured")
            self.email_enabled = False
        
        if self.slack_enabled and not self.slack_webhook:
            self.logger.warning("Slack enabled but SLACK_WEBHOOK_URL not configured")
            self.slack_enabled = False
    
    def notify_scan_started(
        self,
        run_type: str = "manual",
        recipient_email: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Send notification that scan has started (small notification)
        
        Args:
            run_type: "daily", "weekly", or "manual"
            recipient_email: Email to send to (uses SENDER_EMAIL if not provided)
        
        Returns:
            Dictionary with success status for each channel
        """
        results = {}
        
        if self.email_enabled:
            recipient = recipient_email or self.sender_email
            results['email'] = self._send_scan_started_email(recipient, run_type)
        else:
            results['email'] = False
        
        if self.slack_enabled:
            results['slack'] = self._send_scan_started_slack(run_type)
        else:
            results['slack'] = False
        
        return results
    
    def notify_scan_completed(
        self,
        total_found: int = 0,
        opportunities_found: int = 0,
        high_value_found: int = 0,
        run_type: str = "manual",
        recipient_email: Optional[str] = None
    ) -> Dict[str, bool]:
        """
        Send notification that scan completed with summary (no new values found notification)
        
        Args:
            total_found: Total properties found in scan
            opportunities_found: Development opportunities found
            high_value_found: High-value opportunities (score >= 70)
            run_type: "daily", "weekly", or "manual"
            recipient_email: Email to send to (uses SENDER_EMAIL if not provided)
        
        Returns:
            Dictionary with success status for each channel
        """
        results = {}
        
        if self.email_enabled:
            recipient = recipient_email or self.sender_email
            results['email'] = self._send_scan_completed_email(
                total_found, opportunities_found, high_value_found, recipient, run_type
            )
        else:
            results['email'] = False
        
        if self.slack_enabled:
            results['slack'] = self._send_scan_completed_slack(
                total_found, opportunities_found, high_value_found, run_type
            )
        else:
            results['slack'] = False
        
        return results
    
    def alert_on_opportunities(
        self,
        opportunities: List[Dict],
        recipient_email: Optional[str] = None,
        run_type: str = "manual"
    ) -> Dict[str, bool]:
        """
        Send alerts for high-value opportunities
        
        Args:
            opportunities: List of opportunity dictionaries with development_score
            recipient_email: Email to send to (uses SENDER_EMAIL if not provided)
            run_type: "daily", "weekly", or "manual" for context
        
        Returns:
            Dictionary with success status for each channel
        """
        if not opportunities:
            self.logger.info("No opportunities to alert on")
            return {'email': False, 'slack': False}
        
        # Filter high-value opportunities
        high_value = [o for o in opportunities if float(o.get('development_score', 0)) >= self.score_threshold]
        
        if not high_value:
            self.logger.info(f"No opportunities with score >= {self.score_threshold}")
            return {'email': False, 'slack': False}
        
        results = {}
        
        # Send email alert
        if self.email_enabled:
            recipient = recipient_email or self.sender_email
            results['email'] = self._send_email_alert(high_value, recipient, run_type)
        else:
            results['email'] = False
        
        # Send Slack alert
        if self.slack_enabled:
            results['slack'] = self._send_slack_alert(high_value, run_type)
        else:
            results['slack'] = False
        
        return results
    
    def _send_email_alert(
        self,
        opportunities: List[Dict],
        recipient_email: str,
        run_type: str
    ) -> bool:
        """
        Send email notification with HTML formatting
        
        Args:
            opportunities: High-value opportunities to include
            recipient_email: Recipient email address
            run_type: Type of run (daily, weekly, manual)
        
        Returns:
            Success status
        """
        try:
            # Create email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🏠 {len(opportunities)} New Development Opportunities Found!"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Create HTML content
            html = self._generate_email_html(opportunities, run_type)
            
            # Attach HTML
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"✓ Email alert sent to {recipient_email} ({len(opportunities)} opportunities)")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send email: {e}")
            return False
    
    def _send_slack_alert(
        self,
        opportunities: List[Dict],
        run_type: str
    ) -> bool:
        """
        Send Slack message with opportunity preview
        
        Args:
            opportunities: High-value opportunities to include
            run_type: Type of run (daily, weekly, manual)
        
        Returns:
            Success status
        """
        try:
            # Create Slack message blocks
            blocks = self._generate_slack_blocks(opportunities, run_type)
            
            payload = {
                'blocks': blocks,
                'text': f"🏠 {len(opportunities)} Development Opportunities"
            }
            
            # Send to Slack
            response = requests.post(self.slack_webhook, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"✓ Slack alert sent ({len(opportunities)} opportunities)")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send Slack message: {e}")
            return False
    
    def _generate_email_html(self, opportunities: List[Dict], run_type: str) -> str:
        """Generate HTML email content"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_type_display = run_type.replace('_', ' ').title()
        
        opportunities_html = ""
        for i, opp in enumerate(opportunities[:10], 1):  # Show top 10
            score = float(opp.get('development_score', 0))
            address = opp.get('address', 'N/A')
            explanation = opp.get('explanation', '')[:150]
            price = opp.get('price', 'N/A')
            label = opp.get('label', 'N/A')
            
            opportunities_html += f"""
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <strong style="font-size: 16px; color: #1a5f7a;">{i}. {address}</strong>
                    <br/>
                    <small style="color: #666;">Score: <strong>{score:.1f}/100</strong> | Label: <strong>{label}</strong></small>
                    <br/>
                    <small style="color: #888;">{explanation}...</small>
                    <br/>
                    <small style="color: #999;">Price: ${price if price else 'N/A'}</small>
                </td>
            </tr>
            """
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    color: #333;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 800px;
                    margin: 20px auto;
                    background-color: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 14px;
                }}
                .content {{
                    padding: 30px;
                }}
                .summary {{
                    background-color: #f0f8ff;
                    border-left: 4px solid #667eea;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-radius: 4px;
                }}
                .summary p {{
                    margin: 5px 0;
                    color: #333;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .score-high {{
                    background-color: #d4edda;
                    color: #155724;
                }}
                .score-med {{
                    background-color: #fff3cd;
                    color: #856404;
                }}
                .footer {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #666;
                    border-top: 1px solid #eee;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #667eea;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🏠 New Development Opportunities</h1>
                    <p>{run_type_display} Scan - {timestamp}</p>
                </div>
                
                <div class="content">
                    <div class="summary">
                        <p><strong>📊 Summary:</strong> Found <strong>{len(opportunities)}</strong> high-value properties (Score ≥ {self.score_threshold})</p>
                        <p><strong>🎯 Top Score:</strong> {max(float(o.get('development_score', 0)) for o in opportunities):.1f}/100</p>
                        <p><strong>📍 Location:</strong> Newton, MA Area</p>
                    </div>
                    
                    <h2 style="color: #1a5f7a; margin-bottom: 15px;">Top Opportunities</h2>
                    <table>
                        {opportunities_html}
                    </table>
                    
                    <div style="text-align: center; margin-top: 20px;">
                        <a href="https://docs.google.com/spreadsheets" class="button">View Full List in Google Sheets →</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>🤖 Automated alert from Development Leads Finder</p>
                    <p>Next scan: Daily at 9:00 AM | <a href="mailto:{self.sender_email}" style="color: #667eea; text-decoration: none;">Manage Preferences</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_slack_blocks(self, opportunities: List[Dict], run_type: str) -> List[Dict]:
        """Generate Slack message blocks"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        run_type_display = run_type.replace('_', ' ').title()
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🏠 New Development Opportunities Found!",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{run_type_display} Scan Results* — {timestamp}\n*{len(opportunities)} high-value properties* with score ≥ {self.score_threshold}"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add top 5 opportunities
        for i, opp in enumerate(opportunities[:5], 1):
            score = float(opp.get('development_score', 0))
            address = opp.get('address', 'N/A')
            label = opp.get('label', 'N/A')
            explanation = opp.get('explanation', '')[:80]
            
            # Color code by score
            if score >= 80:
                emoji = "🔴"  # Excellent
            elif score >= 70:
                emoji = "🟠"  # Good
            else:
                emoji = "🟡"  # Fair
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{emoji} *{i}. {address}*\nScore: *{score:.1f}/100* | Label: _{label}_\n_{explanation}_"
                }
            })
        
        # Add action buttons
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 View in Google Sheets",
                            "emoji": True
                        },
                        "url": "https://docs.google.com/spreadsheets",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "📧 Email Details",
                            "emoji": True
                        },
                        "url": f"mailto:?subject=Development Leads - {run_type_display}",
                        "style": "primary"
                    }
                ]
            }
        ])
        
        return blocks
    
    def _send_scan_started_email(
        self,
        recipient_email: str,
        run_type: str
    ) -> bool:
        """
        Send small notification that scan has started
        
        Args:
            recipient_email: Email recipient
            run_type: "daily", "weekly", or "manual"
        
        Returns:
            Success status
        """
        try:
            run_type_display = run_type.replace('_', ' ').title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🔄 {run_type_display} Scan Started"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Create simple HTML
            html = f"""
            <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #333;">
                <div style="max-width: 500px; margin: 20px auto; padding: 20px; background: #f0f7ff; border-radius: 8px; border-left: 4px solid #0066cc;">
                    <h2 style="color: #0066cc; margin-top: 0;">🔄 Scan Started</h2>
                    <p style="font-size: 16px; color: #555;">
                        <strong>{run_type_display}</strong> scan has been initiated.
                    </p>
                    <p style="font-size: 14px; color: #888;">
                        Time: {timestamp}<br/>
                        Type: {run_type_display} Scan<br/>
                        Status: ⏳ In Progress
                    </p>
                    <p style="font-size: 12px; color: #999; border-top: 1px solid #ddd; padding-top: 10px; margin-top: 15px;">
                        You'll receive a follow-up email when the scan completes with results.
                    </p>
                </div>
            </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"✓ Scan started notification sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send scan started email: {e}")
            return False
    
    def _send_scan_started_slack(self, run_type: str) -> bool:
        """Send Slack notification that scan started"""
        try:
            run_type_display = run_type.replace('_', ' ').title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🔄 *{run_type_display} Scan Started*\n_{timestamp}_"
                    }
                }
            ]
            
            payload = {'blocks': blocks, 'text': f"{run_type_display} scan started"}
            requests.post(self.slack_webhook, json=payload, timeout=10)
            self.logger.info(f"✓ Scan started notification sent to Slack")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send Slack scan started: {e}")
            return False
    
    def _send_scan_completed_email(
        self,
        total_found: int,
        opportunities_found: int,
        high_value_found: int,
        recipient_email: str,
        run_type: str
    ) -> bool:
        """
        Send notification that scan completed with summary
        
        Args:
            total_found: Total properties found
            opportunities_found: Development opportunities found
            high_value_found: High-value properties (score >= 70)
            recipient_email: Email recipient
            run_type: "daily", "weekly", or "manual"
        
        Returns:
            Success status
        """
        try:
            run_type_display = run_type.replace('_', ' ').title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine status icon
            if high_value_found > 0:
                status_icon = "✅"
                status_text = "High-value opportunities found!"
            elif opportunities_found > 0:
                status_icon = "✅"
                status_text = "Opportunities found"
            else:
                status_icon = "ℹ️"
                status_text = "No new high-value properties found"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"{status_icon} {run_type_display} Scan Complete"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email
            
            # Create HTML
            html = f"""
            <html>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; color: #333;">
                <div style="max-width: 600px; margin: 20px auto; padding: 20px; background: #f9fafb; border-radius: 8px; border-left: 4px solid #10b981;">
                    <h2 style="color: #10b981; margin-top: 0;">{status_icon} Scan Complete</h2>
                    
                    <p style="font-size: 16px; color: #555; margin-bottom: 20px;">
                        {status_text}
                    </p>
                    
                    <div style="background: white; padding: 15px; border-radius: 6px; border: 1px solid #e5e7eb;">
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr>
                                <td style="padding: 8px; color: #666;"><strong>Total Properties Found:</strong></td>
                                <td style="padding: 8px; text-align: right; color: #111;"><strong>{total_found}</strong></td>
                            </tr>
                            <tr style="background: #f3f4f6;">
                                <td style="padding: 8px; color: #666;"><strong>Development Opportunities:</strong></td>
                                <td style="padding: 8px; text-align: right; color: #111;"><strong>{opportunities_found}</strong></td>
                            </tr>
                            <tr>
                                <td style="padding: 8px; color: #666;"><strong>High-Value (Score ≥ 70):</strong></td>
                                <td style="padding: 8px; text-align: right; color: #059669;"><strong>{high_value_found}</strong></td>
                            </tr>
                        </table>
                    </div>
                    
                    <p style="font-size: 13px; color: #999; border-top: 1px solid #e5e7eb; padding-top: 15px; margin-top: 15px;">
                        <strong>Scan Details:</strong><br/>
                        Time: {timestamp}<br/>
                        Type: {run_type_display} Scan
                    </p>
                    
                    {f'<p style="padding: 10px; background: #fef3c7; border-radius: 4px; color: #92400e; font-size: 13px; margin-top: 10px;">⭐ High-value opportunities found! Check your Google Sheets for detailed listings.</p>' if high_value_found > 0 else ''}
                </div>
            </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            self.logger.info(f"✓ Scan completed notification sent to {recipient_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send scan completed email: {e}")
            return False
    
    def _send_scan_completed_slack(
        self,
        total_found: int,
        opportunities_found: int,
        high_value_found: int,
        run_type: str
    ) -> bool:
        """Send Slack notification that scan completed"""
        try:
            run_type_display = run_type.replace('_', ' ').title()
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Determine color and status
            if high_value_found > 0:
                color = "#10b981"
                status = "🟢 High-Value Found!"
            elif opportunities_found > 0:
                color = "#3b82f6"
                status = "🟡 Opportunities Found"
            else:
                color = "#6b7280"
                status = "⚪ No New High-Value Found"
            
            blocks = [
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{status}\n*{run_type_display} Scan Complete*"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Total Found*\n{total_found}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Opportunities*\n{opportunities_found}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*High-Value (≥70)*\n{high_value_found}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Time*\n{timestamp}"
                        }
                    ]
                }
            ]
            
            payload = {'blocks': blocks, 'text': f"{run_type_display} scan completed"}
            requests.post(self.slack_webhook, json=payload, timeout=10)
            self.logger.info(f"✓ Scan completed notification sent to Slack")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send Slack scan completed: {e}")
            return False
    
    def send_pipeline_summary(
        self,
        total_collected: int,
        total_classified: int,
        opportunities_found: int,
        duration_seconds: float,
        recipient_email: Optional[str] = None,
        run_type: str = "manual"
    ) -> Dict[str, bool]:
        """
        Send pipeline execution summary
        
        Args:
            total_collected: Total listings collected
            total_classified: Total listings classified
            opportunities_found: Count of high-value opportunities
            duration_seconds: Pipeline execution time
            recipient_email: Email recipient
            run_type: Type of run
        
        Returns:
            Success status for each channel
        """
        try:
            summary = {
                'total_collected': total_collected,
                'total_classified': total_classified,
                'opportunities_found': opportunities_found,
                'duration': f"{duration_seconds:.1f}s"
            }
            
            # Send Slack summary
            if self.slack_enabled:
                self._send_slack_summary(summary, run_type)
            
            self.logger.info(f"✓ Pipeline summary alert sent")
            return {'email': True, 'slack': self.slack_enabled}
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send summary: {e}")
            return {'email': False, 'slack': False}
    
    def _send_slack_summary(self, summary: Dict, run_type: str) -> bool:
        """Send Slack pipeline summary"""
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "✅ Pipeline Execution Summary",
                        "emoji": True
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": f"*Run Type*\n{run_type.title()}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Duration*\n{summary['duration']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Listings Collected*\n{summary['total_collected']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Listings Classified*\n{summary['total_classified']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*High-Value Found*\n{summary['opportunities_found']}"
                        },
                        {
                            "type": "mrkdwn",
                            "text": f"*Status*\n✅ Success"
                        }
                    ]
                }
            ]
            
            payload = {'blocks': blocks}
            requests.post(self.slack_webhook, json=payload, timeout=10)
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Slack summary failed: {e}")
            return False
