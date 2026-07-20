# Build 0039 Recovery Utility Safety Standard

**Package correction:** v1.3.2

The recovery utility may remove only files and directories recorded in the current transaction journal. A created file is deleted only when its current SHA-256 still matches the applied package hash. A directory is removed only when it was created by the transaction and is proven empty immediately before a non-recursive `rmdir` call.

`shutil.rmtree`, recursive deletion, wildcard directory deletion and removal of a pre-existing canonical directory are prohibited.

Regression coverage must preserve:

- a pre-existing sibling file;
- a pre-existing sibling folder;
- nested content in that sibling folder;
- a non-empty transaction-created folder containing unexpected content;
- a transaction-created file modified after import.
