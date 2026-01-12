## PR Title Format

> **Required:** PR titles must follow Conventional Commits format:
> `type(scope): description`
>
> **Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
>
> **Examples:**
> - `feat(tools): add bulk message sending tool`
> - `fix(api): resolve connection timeout issue`
> - `docs: update installation instructions`

---

## Summary

<!-- Brief description of what this PR does -->

## Changes

<!-- List the main changes in this PR -->
-

## Related Issues

<!-- Link any related issues using "Fixes #123" or "Relates to #123" -->

## Testing

<!-- Describe how you tested these changes -->
- [ ] Unit tests pass (`uv run pytest tests/ --ignore=tests/integration/`)
- [ ] Pre-commit checks pass (`uv run pre-commit run --all-files`)
- [ ] Integration tests pass (if applicable)

## Checklist

- [ ] PR title follows Conventional Commits format
- [ ] Code follows project style guidelines
- [ ] Tests added/updated as needed
- [ ] Documentation updated as needed
