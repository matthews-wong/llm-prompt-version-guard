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
