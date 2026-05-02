# Initial User Test

This pass is meant to answer one question first: does the studio already feel understandable and worth exploring before the full inspector and export systems land?

## Recommended launch commands

Showcase run:

```bash
python -m pyqt6_stylizer --preset showcase-playground
```

Reload the same showcase if you want a clean baseline between participants.

## Moderator checklist

1. Ask the tester what they think the app is for within the first 30 seconds.
2. Ask them to pan across the canvas and point out which examples feel simplest versus densest.
3. Ask them to open at least one flyout and one dialog without being told where those triggers live.
4. Ask them to duplicate one example, move it, change at least two values in Properties, then edit one obvious field in the structured block pane and click `Apply Block`.
5. Ask whether the current examples and editing loop feel broad enough to suggest a personal product style or application direction.

## Signals to capture

- Where the tester expected the primary controls to live.
- Whether the example names read as useful or abstract.
- Whether the difference between scene cards and embedded widget cards feels meaningful.
- Which parts of the giant canvas felt most promising and which felt too busy.
- Which missing property editors were immediately noticeable.

## Likely next follow-up after the first test

- Descriptor-driven property editing in the inspector.
- Export bundle generation for AI handoff.
- Richer dummy interaction controls tied directly to `StudioDocument.interactions`.