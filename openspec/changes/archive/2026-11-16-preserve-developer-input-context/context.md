# Developer input context preservation

Adapted from Soju06/codex-lb PR #2569, source commit
`778e10f4ab7111c7ab5539b448df2763fabc1987`, addressing upstream issue #2563.
The developer message belongs to the Responses input history; moving it to
request-local instructions makes later previous_response_id continuations lose
that information. For example, a session developer message supplied on the first
model call must remain part of that response's input when the next call supplies
only tool outputs. Only system messages continue to be hoisted. Responses Lite
and the default Chat Completions mapping retain their existing contracts.

This fork verifies serialization and product route behavior with local upstream
stubs. It does not claim a production or live OpenAI replay test. No new settings,
database changes, or account routing changes are introduced.
