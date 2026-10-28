# llm-prompt-version-guard

Prompts are code that changes behaviour without a compiler to notice. This
guard keeps a lockfile of each prompt's content hash and version, and fails
when the text changed but the version did not. A prompt edit then always
shows up as a version bump in review.

Runs offline with the standard library only.

## Layout

```
prompts/summarize.prompt   header (name, version), a --- line, then the body
prompts.lock.json          approved version and sha256 per prompt
```

## Usage

```
python3 -m versionguard check    # compare prompts with the lockfile
python3 -m versionguard lock     # record the current prompts
python3 -m unittest discover -s tests
```

## Workflow

1. Edit a prompt body.
2. `check` fails: `text changed but version is still 1.0.0; bump it`.
3. Bump `version` in the header. `check` now asks you to run `lock`.
4. Run `lock` and commit the prompt and `prompts.lock.json` together.

`check` also fails for a version that went backwards, a prompt missing from
the lockfile, and a locked prompt whose file was deleted. Each message names
the prompt and the step to take.

## Notes

- Only the body is hashed. Line endings and trailing whitespace are
  normalised first, so a CRLF checkout does not look like an edit.
- The version is not derived from the change: choosing major, minor or
  patch stays a human call. The guard only enforces that the call is made.
- Versions must be `MAJOR.MINOR.PATCH`; the comparison is numeric, so
  `1.10.0` is newer than `1.9.0`.
- `make validate` runs the unit tests and `check` on the example prompts;
  CI does the same.
