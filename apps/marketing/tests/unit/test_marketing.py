"""Unit tests for marketing use cases."""

from __future__ import annotations

import uuid

import pytest

from apps.marketing.domain.exceptions import CampaignAlreadySentError, CampaignNotFoundError
from apps.marketing.tests.unit.fakes import (
    FakeAudienceSegmentRepository,
    FakeCampaignRepository,
    make_campaign,
)


def test_list_campaigns_empty():
    """Returns empty list when no campaigns exist."""
    from apps.marketing.application.use_cases.list_campaigns import ListCampaignsUseCase

    result = ListCampaignsUseCase(FakeCampaignRepository()).execute()
    assert result == []


def test_create_campaign_success():
    """Creating a campaign returns a CampaignEntity in draft status."""
    from apps.marketing.application.use_cases.create_campaign import CreateCampaignUseCase

    repo = FakeCampaignRepository()
    result = CreateCampaignUseCase(repo).execute(
        created_by=uuid.uuid4(),
        name="Newsletter",
        subject="Hello",
        body="<p>Hi</p>",
    )
    assert result.status == "draft"
    assert result.name == "Newsletter"


def test_send_campaign_marks_sent():
    """SendCampaignUseCase transitions status to sent and records sent_at."""
    from apps.marketing.application.use_cases.send_campaign import SendCampaignUseCase

    campaign = make_campaign(status="draft")
    repo = FakeCampaignRepository([campaign])
    result = SendCampaignUseCase(repo).execute(campaign_id=campaign.id)
    assert result.status == "sent"
    assert result.sent_at is not None


def test_send_already_sent_raises():
    """Raises CampaignAlreadySentError when campaign is already sent."""
    from apps.marketing.application.use_cases.send_campaign import SendCampaignUseCase

    campaign = make_campaign(status="sent")
    repo = FakeCampaignRepository([campaign])
    with pytest.raises(CampaignAlreadySentError):
        SendCampaignUseCase(repo).execute(campaign_id=campaign.id)


def test_send_missing_campaign_raises():
    """Raises CampaignNotFoundError when campaign does not exist."""
    from apps.marketing.application.use_cases.send_campaign import SendCampaignUseCase

    with pytest.raises(CampaignNotFoundError):
        SendCampaignUseCase(FakeCampaignRepository()).execute(campaign_id=uuid.uuid4())


def test_create_segment_success():
    """Creating a segment returns an AudienceSegmentEntity."""
    from apps.marketing.application.use_cases.create_segment import CreateSegmentUseCase

    repo = FakeAudienceSegmentRepository()
    result = CreateSegmentUseCase(repo).execute(
        created_by=uuid.uuid4(),
        name="VIP Users",
        filters={"verified": True},
    )
    assert result.name == "VIP Users"
    assert result.filters == {"verified": True}


def test_list_segments_returns_created():
    """List segments returns the one we created."""
    from apps.marketing.application.use_cases.create_segment import CreateSegmentUseCase
    from apps.marketing.application.use_cases.list_segments import ListSegmentsUseCase

    repo = FakeAudienceSegmentRepository()
    CreateSegmentUseCase(repo).execute(created_by=uuid.uuid4(), name="All", filters={})
    result = ListSegmentsUseCase(repo).execute()
    assert len(result) == 1
