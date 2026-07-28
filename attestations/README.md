# Release verification

Version tags are SSH-signed with the repository release key in
`release-signing-key.pub`.

Key fingerprint:

```text
SHA256:Syg1Gl7BG9c8cb1psQjmwBs/iC9082a3WvxJ6EMPpos
```

Verify a tag from a trusted checkout:

```bash
printf 'ahronzombi@gmail.com %s\n' \
  "$(cat attestations/release-signing-key.pub)" > /tmp/opk-allowed-signers
git -c gpg.ssh.allowedSignersFile=/tmp/opk-allowed-signers verify-tag v0.1.0
```

The release workflow additionally creates GitHub build-provenance attestations
for distributed artifacts. A valid signature proves which key signed the tag;
it does not prove the truth of a knowledge claim.
