def test_classification():
    from app.services.classifier_service import classify_email

    assert classify_email("Invoice Amazon", "") == "finance"
    assert classify_email("Job interview", "") == "career"
    assert classify_email("Hello friend", "") == "other"