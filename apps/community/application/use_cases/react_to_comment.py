"""Use case: react to a comment (upsert -- one reaction per user per comment)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from apps.community.domain.entities import CommentReactionEntity
from apps.community.domain.repositories import ICommentReactionRepository, IPostCommentRepository


class ReactToCommentUseCase:
    """Add or replace a user's reaction on a comment."""

    def __init__(
        self,
        comment_repo: IPostCommentRepository,
        reaction_repo: ICommentReactionRepository,
    ) -> None:
        self._comments = comment_repo
        self._reactions = reaction_repo

    def execute(
        self,
        *,
        comment_id: uuid.UUID,
        user_id: uuid.UUID,
        reaction_type: str,
    ) -> CommentReactionEntity:
        """Verify the comment exists, then upsert the reaction."""
        self._comments.get_by_id(comment_id)
        reaction = CommentReactionEntity(
            id=uuid.uuid4(),
            comment_id=comment_id,
            user_id=user_id,
            reaction_type=reaction_type,
            created_at=datetime.now(timezone.utc),
        )
        return self._reactions.upsert(reaction)
