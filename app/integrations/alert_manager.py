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
