import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class PhishingTools:
    """Tools for autonomous drafting and sending spear-phishing emails using Swarm's LLM context."""
    
    @staticmethod
    def send_email(smtp_server, smtp_port, username, password, from_addr, to_addr, subject, body):
        """Send an email using SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = from_addr
            msg['To'] = to_addr
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            return f"[Success] Email sent to {to_addr}."
        except Exception as e:
            return f"[Error] Failed to send email: {str(e)}"

    @staticmethod
    def draft_phishing_email(llm_backend, target_info, sender_context):
        """
        Takes notes on a target (e.g., from LinkedIn/theHarvester) and drafts an email layout.
        Uses the passed `llm_backend` from the Agent.
        """
        if not llm_backend:
            return "[Error] No LLM backend provided to draft the email."

        prompt = f"""
        You are a red team social engineering expert.
        Draft a highly convincing spear-phishing email based on the following target info:
        {target_info}
        
        The pretext is: {sender_context}
        
        Return ONLY the HTML body of the email. Do not include subject lines or explanations.
        Make it professional, urgent but realistic, and include a placeholder [LINK_HERE] for a payload.
        """
        
        try:
            draft = llm_backend.generate(prompt=prompt, system="You are an expert red team developer.", temperature=0.7)
            return draft if draft else "[Error] LLM failed to generate draft."
        except Exception as e:
            return f"[Error] LLM Exception: {str(e)}"
