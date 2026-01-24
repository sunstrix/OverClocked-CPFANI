from overclocked_helpdesk.services.email_service import send_email_alert

emails = [
    "ishitabej26@gmail.com",
    "vikash.pan2003@gmail.com"
]

for email in emails:
    ok = send_email_alert(
        to_email=email,
        subject="OverClocked Helpdesk Test",
        body="This is a test email from OverClocked Helpdesk."
    )
    print(email, "Sent" if ok else "Failed")
